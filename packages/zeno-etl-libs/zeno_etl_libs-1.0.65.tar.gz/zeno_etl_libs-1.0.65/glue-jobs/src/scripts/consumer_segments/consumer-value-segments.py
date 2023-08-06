"""
# Author - shubham.jangir@zeno.health shubham.gupta@zeno.health
# Purpose - script with DSS write action for customer value segments
# Pyliny Score - 7.98
"""

import argparse
import os
import sys
from datetime import datetime as dt

import numpy as np
from dateutil.tz import gettz

from zeno_etl_libs.helper.email.email import Email
from zeno_etl_libs.helper.parameter.job_parameter import parameter

sys.path.append('../../../..')

from zeno_etl_libs.helper.aws.s3 import S3
from zeno_etl_libs.db.db import DB
from zeno_etl_libs.helper import helper
from zeno_etl_libs.logger import get_logger

parser = argparse.ArgumentParser(description="This is ETL script.")
parser.add_argument('-e', '--env', default="dev", type=str, required=False)

args, unknown = parser.parse_known_args()
env = args.env
job_params = parameter.get_params(job_id=42)
email_to = job_params['email_to']
os.environ['env'] = env

logger = get_logger()

# params
# Segment calculation date should be 1st of every month

try:
    period_end_d_plus1 = job_params['period_end_d_plus1']
    period_end_d_plus1 = str(dt.strptime(period_end_d_plus1, "%Y-%m-%d").date())
    period_end_d_plus1 = period_end_d_plus1[:-3] + '-01'
except ValueError:
    period_end_d_plus1 = dt.today().strftime('%Y-%m') + '-01'

logger.info(f"segment calculation date : {period_end_d_plus1}")

read_schema = 'prod2-generico'
table_name = 'customer-value-segment'

rs_db = DB()
rs_db.open_connection()

s3 = S3()

table_info = helper.get_table_info(db=rs_db, table_name=table_name, schema=read_schema)
logger.info(table_info)
if isinstance(table_info, type(None)):
    logger.info(f"table: {table_name} do not exist")

s = f"""
    SELECT
        "patient-id",
        COUNT(DISTINCT "id") AS "total-bills",
        SUM("net-payable") AS "total-spend"
    FROM "{read_schema}"."bills-1"
    WHERE DATEDIFF('days', '{period_end_d_plus1}', date("created-at")) between -90 and -1
    GROUP BY "patient-id"
    """
logger.info(f"data query : {s}")
data = rs_db.get_df(query=s)

logger.info(data.head())

data['total-spend'] = data['total-spend'].astype(float)
data['abv'] = np.round(data['total-spend'] / data['total-bills'], 2)
data = data.sort_values(['total-spend'], ascending=False)
data['rank'] = data['total-spend'].rank(method='dense', ascending=False)
data['rank'] = data['rank'].astype(int)
data['cumm-sales'] = data.sort_values(['total-spend'], ascending=False)['total-spend'].cumsum()

len_data = len(data)
logger.info(len_data)


def assign_value_segment(row):
    """
    :param row:
    :return: value-segment
    """
    if row['rank'] <= 0.05 * len_data:
        return 'platinum'
    if (row['rank'] > 0.05 * len_data) & (row['rank'] <= 0.1 * len_data):
        return 'gold'
    if (row['rank'] > 0.1 * len_data) & (row['rank'] <= 0.2 * len_data):
        return 'silver'
    return 'others'


data['value-segment'] = data.apply(assign_value_segment, axis=1)

platinum_length = len(data[data['value-segment'] == 'platinum'])
gold_length = len(data[data['value-segment'] == 'gold'])
silver_length = len(data[data['value-segment'] == 'silver'])
others_length = len(data[data['value-segment'] == 'others'])

platinum_data = data[data['value-segment'] == 'platinum']

# Write to csv
s3.save_df_to_s3(df=platinum_data,
                 file_name='Shubham_G/value_segment/value_segment_data_platinum.csv')

logger.info(f'Length of Platinum segment is {platinum_length}')
logger.info(f'Length of Gold segment is {gold_length}')
logger.info(f'Length of Silver segment is {silver_length}')
logger.info(f'Length of Others segment is {others_length}')

q2 = f"""
    SELECT
        "patient-id",
        "store-id",
        COUNT(DISTINCT "id") AS "store-bills",
        SUM("net-payable") AS "store-spend"
    FROM "{read_schema}"."bills-1"
    WHERE DATEDIFF('days', '{period_end_d_plus1}', date("created-at")) between -90 and -1
    GROUP BY "patient-id","store-id" 
    """
logger.info(q2)
data_store = rs_db.get_df(query=q2)
logger.info(f"data_store {data_store.head()}")
data_store['rank'] = data_store.sort_values(['store-bills',
                                             'store-spend'],
                                            ascending=[False, False]). \
                         groupby(['patient-id']).cumcount() + 1

patient_store = data_store[data_store['rank'] == 1][['patient-id', 'store-id']]

q3 = f"""
    SELECT
        "id" AS "store-id",
        "name" AS "store-name"
    FROM "{read_schema}"."stores"
    """
logger.info(q3)
stores = rs_db.get_df(q3)
logger.info(f"stores {stores}")
patient_store = patient_store.merge(stores, how='inner', on=['store-id', 'store-id'])
data = data.merge(patient_store, how='inner', left_on=['patient-id'], right_on=['patient-id'])

runtime_month = dt.today().strftime('%Y-%m')

runtime_date = dt.today().strftime('%Y-%m-%d')

data['segment-calculation-date'] = period_end_d_plus1
data['base-list-identifier'] = runtime_month
data['upload-date'] = runtime_date

# etl
data['created-at'] = dt.now(tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
data['created-by'] = 'etl-automation'
data['updated-at'] = dt.now(tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
data['updated-by'] = 'etl-automation'

logger.info(f"data write : \n {data.head()}")

# truncate data if current month data already exist

if isinstance(table_info, type(None)):
    logger.info(f"table: {table_name} do not exist")
else:
    truncate_query = f"""
            DELETE
            FROM
                "{read_schema}"."{table_name}"
            WHERE
                "segment-calculation-date" = '{period_end_d_plus1}';
                """
    logger.info(truncate_query)
    rs_db.execute(truncate_query)

# drop duplicates subset - patient-id
data.drop_duplicates(subset=['patient-id'], inplace=True)

# Write to csv
s3.save_df_to_s3(df=data[table_info['column_name']],
                 file_name='Shubham_G/value_segment/value_segment_data.csv')
s3.write_df_to_db(df=data[table_info['column_name']], table_name=table_name,
                  db=rs_db, schema=read_schema)

logger.info("Script ran successfully")

# email after job ran successfully
email = Email()

subject = "Task Status behaviour segment calculation"
mail_body = f"Value segments upload succeeded for segment calculation date {period_end_d_plus1} " \
            f"with data shape {data.shape}"

email.send_email_file(subject=subject,
                      mail_body=mail_body,
                      to_emails=email_to, file_uris=[], file_paths=[])

# closing connection
rs_db.close_connection()
