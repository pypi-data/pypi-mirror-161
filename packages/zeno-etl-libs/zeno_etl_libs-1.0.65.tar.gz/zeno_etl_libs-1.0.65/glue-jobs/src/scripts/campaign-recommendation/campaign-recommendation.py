"""
Author:shubham.gupta@zeno.health
Purpose: Campaign Recommendation
"""

import argparse
import os
import sys
from datetime import datetime as dt
from datetime import timedelta
from warnings import filterwarnings as fw

import numpy as np
import pandas as pd

fw('ignore')

sys.path.append('../../../..')

from zeno_etl_libs.logger import get_logger
from zeno_etl_libs.helper.aws.s3 import S3
from zeno_etl_libs.db.db import DB
from zeno_etl_libs.helper.email.email import Email
from zeno_etl_libs.helper.parameter.job_parameter import parameter

parser = argparse.ArgumentParser(description="This is ETL script.")
parser.add_argument('-e', '--env', default="dev", type=str, required=False)

job_params = parameter.get_params(job_id=131)
args, unknown = parser.parse_known_args()
env = args.env
os.environ['env'] = env
email_to = job_params['email_to']

logger = get_logger()

logger.info(f"env: {env}")

rs_db = DB()
rs_db.open_connection()

s3 = S3()

read_schema = 'prod2-generico'

#################################################################
# ABV Module
#################################################################

# Last Monday :
today = dt.today().date()
last_monday = today - timedelta(days=(today.weekday()))
logger.info(last_monday)

abv_q = f"""
        select
            pm."primary-store-id",
            cv."abv-seg",
            cv."patient-id",
            recency,
            frequency,
            stage,
            p.phone,
            cv."last-bill"
        from
            "{read_schema}"."crm-view" cv
        left join "{read_schema}"."patients-metadata-2" pm 
        on
            cv."patient-id" = pm.id
        left join "{read_schema}".patients p on
            pm.id = p.id
        where
            cv."calculation-date" = '{last_monday}'
            and cv."r-score" >= 4
            and cv."f-score" >= 3;"""

logger.info(f"query for abv module data : {abv_q}")
abv_driver = rs_db.get_df(abv_q)

# Creating identity for clevertap
abv_driver['phone'] = abv_driver['phone'].apply(lambda x: '91' + x)

logger.info(f"Campaign will run for : {abv_driver.stage.unique()}")

logger.info(f"recency min : {abv_driver.recency.min()}")
logger.info(f"recency max : {abv_driver.recency.max()}")

logger.info(f"frequency min : {abv_driver.frequency.min()}")
logger.info(f"frequency max : {abv_driver.frequency.max()}")

abv_dis = pd.crosstab(index=abv_driver['primary-store-id'],
                      columns=abv_driver['abv-seg'],
                      values=abv_driver['patient-id'],
                      aggfunc='nunique',
                      normalize='index') * 100

abv_dis['major_contributor'] = abv_dis.idxmax(axis=1)
abv_dis = abv_dis.reset_index()

store_abv_campaign = abv_dis.groupby('major_contributor')['primary-store-id'].apply(lambda x: list(np.unique(x)))
logger.info(store_abv_campaign)

patient_abv = abv_dis[['primary-store-id', 'major_contributor']]
patient_abv = pd.merge(patient_abv,
                       abv_driver,
                       how='left',
                       left_on=['primary-store-id', 'major_contributor'],
                       right_on=['primary-store-id', 'abv-seg'])

abv_patient_count = patient_abv.groupby('major_contributor')['patient-id'].nunique()
logger.info(f"ABV driver campaign patient count {abv_patient_count}", )

patient_abv = patient_abv[['primary-store-id', 'abv-seg', 'patient-id']]

abv_driver_mail_body = f"""
Hey Team,
For ABV Driver campaign (Targeted) patients list is attached in mail
Campaign will run for patients where NOB is greater than {abv_driver.frequency.min()}
and recency of customer less than {abv_driver.recency.max()} days
Customers will fall in stages : {abv_driver.stage.unique()}

Store-wise campaign : list attached
Please follow targeted customer for their ABV segments ( Neglect if segment size <1000)

Code will be open but sms campaign will run for mentioned patients only.

Test/Control split - 90/10
Code : Open 
Min purchase condition : based on targeted abv segment
Max per patients : 1
Conversion condition : Charged (Next 30 Days) & total-amount > abv-seg(max)

*Marketing team : suggest/create promo-codes
*Pooja : send SMS-draft for campaigns
"""

sac = s3.save_df_to_s3(df=pd.DataFrame(store_abv_campaign),
                       file_name="Store_ABV_Campaigns.csv",
                       index_label='ABV Segment',
                       index=True)
acpl = s3.save_df_to_s3(df=pd.DataFrame(patient_abv), file_name="ABV_Campaign_Patients_list.csv")

# Sending email
subject = 'ABV Driver Campaign'
mail_body = abv_driver_mail_body
email = Email()
files = [sac, acpl]
email.send_email_file(subject=subject, mail_body=mail_body, to_emails=email_to, file_uris=files)

#################################################################
# Lost Customers Module
#################################################################

lost_q = f"""
        select
            pm."primary-store-id",
            cv."patient-id",
            recency,
            frequency,
            stage,
            p.phone,
            "last-bill"
        from
            "{read_schema}"."crm-view" cv
        left join "{read_schema}"."patients-metadata-2" pm 
        on
            cv."patient-id" = pm.id
        left join "{read_schema}".patients p on
            pm.id = p.id
        where
            cv."calculation-date" = '{last_monday}'
            and stage in ('Hibernating', 'At Risk', 'Can\\\'t Lose them');"""

logger.info(f"query for lost customer module data : {lost_q}")
lost_customers = rs_db.get_df(lost_q)

store_wise_segment = pd.pivot_table(data=lost_customers,
                                    index='primary-store-id',
                                    columns='stage',
                                    values='patient-id',
                                    aggfunc='nunique').reset_index()

segment_properties = pd.pivot_table(data=lost_customers,
                                    index='stage',
                                    values=['recency', 'frequency', 'last-bill'],
                                    aggfunc=['min', 'max']).reset_index()

segment_size = pd.pivot_table(data=lost_customers,
                              index='stage',
                              values='patient-id',
                              aggfunc=['nunique']).reset_index()

lost_customers_data = lost_customers[['primary-store-id', 'stage', 'patient-id']].drop_duplicates()

lost_customer_mail_body = """
Hey Team,

Properties for lost customer segments is attached,
Please create campaign using those properties
Can't lose them : High priority
At risk : Medium priority
Hibernating : low priority 
Suggest promo-codes accordingly 
Segment size is also attached for reference

Test/Control split - 90/10
Code : Restricted
Min purchase condition : 1
Max per patients : 1
Discount : based on priority
Conversion condition : Charged (Next 30 Days)

*Marketing team : suggest/create promo-codes
*Pooja : send SMS-draft for campaigns

Thanks & Regards
"""

sws = s3.save_df_to_s3(df=store_wise_segment,
                       file_name="Store_Lost_Customers.csv")

lcsp = s3.save_df_to_s3(df=segment_properties,
                        file_name="Lost_Customer_Segment_Properties.csv")

ss = s3.save_df_to_s3(df=segment_size,
                      file_name="Lost_Customer_Segment_Size.csv")

lsd = s3.save_df_to_s3(df=lost_customers_data,
                       file_name="Lost_Customer_Data.csv")

# Sending email
subject = 'Lost Customer Campaign'
mail_body = lost_customer_mail_body
email = Email()
files = [sws, lcsp, ss, lsd]
email.send_email_file(subject=subject, mail_body=mail_body, to_emails=email_to, file_uris=files)

#################################################################
# Retention Module
#################################################################

retention_q = f"""
        select
            pm."primary-store-id",
            cv."patient-id",
            recency,
            frequency,
            stage,
            p.phone,
            "last-bill"
        from
            "{read_schema}"."crm-view" cv
        left join "{read_schema}"."patients-metadata-2" pm 
        on
            cv."patient-id" = pm.id
        left join "{read_schema}".patients p on
            pm.id = p.id
        where
            cv."calculation-date" = '{last_monday}'
            and stage in ('Promising')
            and "m-score" >= 4;"""

logger.info(f"query for retention module data : {retention_q}")
retention = rs_db.get_df(retention_q)

retention_data = retention[['primary-store-id', 'stage', 'patient-id']].drop_duplicates()

store_wise_segment = pd.pivot_table(data=retention,
                                    index='primary-store-id',
                                    columns='stage',
                                    values='patient-id',
                                    aggfunc='nunique').reset_index()

segment_properties = pd.pivot_table(data=retention,
                                    index='stage',
                                    values=['recency', 'frequency', 'last-bill'],
                                    aggfunc=['min', 'max']).reset_index()

segment_size = pd.pivot_table(data=retention,
                              index='stage',
                              values='patient-id',
                              aggfunc=['nunique']).reset_index()

retention_mail_body = """
Hey Team,

Properties for retention campaign is attached,
Focus is to increase quarter on quarter retention
Please create campaign using those properties

Suggest promo-codes accordingly 
Segment size is also attached for reference
Code will be open but sms campaign will run for mentioned patients only.

Test/Control split - 90/10
Code : Open
Min purchase condition : minimum monetary value of segment
Max per patients : 4 (NOB2-4)
NOB : 2-4
Conversion condition : Charged (Next 30 Days)

*Marketing team : suggest/create promo-codes
*Pooja : send SMS-draft for campaigns

Thanks & Regards
"""

sws = s3.save_df_to_s3(df=store_wise_segment,
                       file_name="Store_Retention.csv")

lcsp = s3.save_df_to_s3(df=segment_properties,
                        file_name="Retention_Segment_Properties.csv")

ss = s3.save_df_to_s3(df=segment_size,
                      file_name="Retention_Segment_Size.csv")

rd = s3.save_df_to_s3(df=retention_data,
                       file_name="Retention_Customer_Data.csv")

# Sending email
subject = 'Retention Campaign'
mail_body = retention_mail_body
email = Email()
files = [sws, lcsp, ss, rd]
email.send_email_file(subject=subject, mail_body=mail_body, to_emails=email_to, file_uris=files)

# closing the connection
rs_db.close_connection()
