import sys
import os

sys.path.append('../../../..')

from zeno_etl_libs.helper.aws.s3 import S3
from zeno_etl_libs.logger import get_logger
from zeno_etl_libs.helper.email.email import Email
from zeno_etl_libs.db.db import DB

import argparse
import datetime

parser = argparse.ArgumentParser(description="This is ETL script.")
parser.add_argument('-e', '--env', default="dev", type=str, required=False)
parser.add_argument('-et', '--email_to', default="sanjay.bohra@zeno.health,rohan.kamble@zeno.health,"
                                                 "renuka.rawal@zeno.health", type=str, required=False)
args, unknown = parser.parse_known_args()
env = args.env
email_to = args.email_to
os.environ['env'] = env
logger = get_logger()

logger.info(f"env: {env}")

rs_db = DB()
rs_db.open_connection()
s3 = S3()

query = '''
        select
            mtd."start-date",
            mtd.composition,
            round(mtd."MTD composition share",2) as "MTD composition share",
            round(y."Yesterdays composition share",2) as "Yesterdays composition share",
            round(mtd."Goodaid Margin",2) as "Goodaid Margin",
            round(mtd."ethical margin",2) as "Ethical Margin",
            mtd."MTD Goodaid Qty",
            mtd."MTD Non GA Generic Qty",
            mtd."MTD Ethical Qty",
            round(mtd."MTD Goodaid Sales", 0) as "MTD Goodaid Sales",
            round(mtd."MTD Non GA Generic Sales",0) as "MTD Non GA Generic Sales",
            round(mtd."MTD Ethical Sales",0) as "MTD Ethical Sales",
            y."Yesterdays Goodaid Qty",
            y."Yesterdays Non GA Generic Qty",
            y."Yesterdays Ethical Qty",
            round(y."Yesterdays Goodaid Sales",0) as "Yesterdays Goodaid Sales",
            round(y."Yesterdays Non GA Generic Sales",0) as "Yesterdays Non GA Generic Sales",
            round(y."Yesterdays Ethical Sales", 0) as "Yesterdays Ethical Sales"
        from 
        (select
            date(g."min-bill-date")  as "start-date",
            s.composition , 
            sum(case when s."type"= 'generic' and s."company-id"= 6984 then (s."net-quantity") else 0 end) as "MTD Goodaid Qty",
            sum(case when s."type"= 'generic' and "company-id" <> 6984  then (s."net-quantity") else 0 end) as "MTD Non GA Generic Qty",
            sum(case when s."type"= 'ethical' then (s."net-quantity") else 0 end) as "MTD Ethical Qty",
            sum(case when s."type"= 'generic' and s."company-id"= 6984 then ("revenue-value") else 0 end) as "MTD Goodaid Sales",
            sum(case when s."type"= 'generic' and s."company-id" <> 6984 then (s."revenue-value") else 0 end) as "MTD Non GA Generic Sales",
            sum(case when s."type"= 'ethical' then (s."revenue-value") else 0 end) as "MTD Ethical Sales",
            (("MTD Goodaid Qty"*1.0)/("MTD Goodaid Qty"*1.0+"MTD Non GA Generic Qty"*1.0+"MTD Ethical Qty"*1.0))*100 as "MTD composition share",
            sum(case when s."type"= 'generic' and s."company-id"= 6984 then (s.quantity*s."purchase-rate") else 0 end) as "MTD Goodaid Cogs",
            sum(case when s."type"= 'ethical' then (s.quantity *s."purchase-rate") else 0 end) as "MTD Ethical Cogs",
            (("MTD Ethical Sales"-"MTD Ethical Cogs")/"MTD Ethical Sales")*100 as "ethical margin",
            (("MTD Goodaid Sales"-"MTD Goodaid Cogs")/"MTD Goodaid Sales")*100 as "Goodaid Margin"
        from 
            "prod2-generico"."prod2-generico".sales s 
        left join "prod2-generico"."prod2-generico"."goodaid-atc-sr" g
            on s.composition  = g.composition  
        where
            s."bill-flag" = 'gross'
            and	s.composition in ('Sitagliptin(100mg)', 'Sitagliptin(50mg)', 'Metformin(1000mg),Sitagliptin(50mg)', 'Metformin(500mg),Sitagliptin(50mg)')
            and (s."created-at") > DATE_TRUNC('day', dateadd(day, -(extract(day from current_date)), current_date))
        group by 1,2) mtd 
        left join 
        (select
            composition , 
            sum(case when "type"= 'generic' and "company-id"= 6984 then ("net-quantity") else 0 end) as "Yesterdays Goodaid Qty",
            sum(case when "type"= 'generic' and "company-id" <> 6984 then ("net-quantity") else 0 end) as "Yesterdays Non GA Generic Qty",
            sum(case when "type"= 'ethical' then ("net-quantity") else 0 end) as "Yesterdays Ethical Qty",
            sum(case when "type"= 'generic' and "company-id"= 6984 then ("revenue-value") else 0 end) as "Yesterdays Goodaid Sales",
            sum(case when "type"= 'generic' and "company-id" <> 6984 then ("revenue-value") else 0 end) as "Yesterdays Non GA Generic Sales",
            sum(case when "type"= 'ethical' then ("revenue-value") else 0 end) as "Yesterdays Ethical Sales",
            (("Yesterdays Goodaid Qty"*1.0)/("Yesterdays Goodaid Qty"*1.0+"Yesterdays Non GA Generic Qty"*1.0+"Yesterdays Ethical Qty"*1.0))*100 as "Yesterdays composition share",
            sum(case when s."type"= 'generic' and s."company-id"= 6984 then (s.quantity*s."purchase-rate") else 0 end) as "Yest Goodaid Cogs",
            sum(case when s."type"= 'ethical' then (s.quantity *s."purchase-rate") else 0 end) as "Yest Ethical Cogs"
        from 
            "prod2-generico"."prod2-generico".sales s
        where
            s."bill-flag" = 'gross' 
            and composition in ('Sitagliptin(100mg)', 'Sitagliptin(50mg)', 'Metformin(1000mg),Sitagliptin(50mg)', 'Metformin(500mg),Sitagliptin(50mg)')
            and date("created-at") = dateadd(day, -1, current_date)
        group by 1) y 
        on mtd.composition = y.composition '''
data = rs_db.get_df(query)
logger.info("data for the 4 composition successfully loaded")

run_date = str(datetime.datetime.now().date())
file_name = 'Goodaid New Diabetes Drug Data-{}.csv'.format(str(run_date))

# Uploading the file to s3
new_drugs = s3.save_df_to_s3(df=data, file_name=file_name)
# Sending email
subject = '''New Diabetes Drug Data '''
mail_body = '''Please find the attached file containing the data till-{} 
        '''.format(run_date)
file_uris = [new_drugs]
email = Email()
email.send_email_file(subject=subject, mail_body=mail_body, to_emails=email_to, file_uris=file_uris)

# deleteing the old files
for uri in file_uris:
    s3.delete_s3_obj(uri=uri)

# Closing the DB Connection
rs_db.close_connection()