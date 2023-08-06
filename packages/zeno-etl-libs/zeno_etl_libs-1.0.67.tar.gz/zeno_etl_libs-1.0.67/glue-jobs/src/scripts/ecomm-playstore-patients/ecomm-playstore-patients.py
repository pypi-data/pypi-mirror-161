"""
Automailer for Playstore Reviews
Fuzzy use to get patient names
author : neha.karekar@zeno.health
"""

import argparse
import sys
import os

sys.path.append('../../../..')

from zeno_etl_libs.logger import get_logger
from zeno_etl_libs.db.db import DB
from zeno_etl_libs.helper.aws.s3 import S3
from zeno_etl_libs.helper import helper
import pandas as pd
import dateutil
import datetime
from dateutil.tz import gettz
from zeno_etl_libs.helper.email.email import Email
import numpy as np
import Levenshtein as lev
from datetime import timedelta

parser = argparse.ArgumentParser(description="This is ETL script.")
parser.add_argument('-e', '--env', default="dev", type=str, required=False,
                    help="This is env(dev, stag, prod)")
parser.add_argument('-d', '--full_run', default=0, type=int, required=False)
parser.add_argument('-et', '--email_to', default="neha.karekar@zeno.health", type=str, required=False)
args, unknown = parser.parse_known_args()
email_to = args.email_to
env = args.env
full_run = args.full_run
os.environ['env'] = env
logger = get_logger()
logger.info(f"full_run: {full_run}")

rs_db = DB()
rs_db_write = DB(read_only=False)
rs_db.open_connection()
rs_db_write.open_connection()

s3 = S3()

schema = 'prod2-generico'
table_name = 'ecomm-playstore-patients'
table_info = helper.get_table_info(db=rs_db_write, table_name=table_name, schema=schema)

# max of data
playstore_q = """
select
            max("review-created-at") max_exp
        from
            "prod2-generico"."ecomm-playstore-reviews" 
        """
max_exp_date = rs_db.get_df(playstore_q)
max_exp_date['max_exp'].fillna(np.nan, inplace=True)
print(max_exp_date.info())
max_exp_date = max_exp_date['max_exp'].to_string(index=False)
print(max_exp_date)

# params
if full_run or max_exp_date == 'NaN':
    start = '2017-05-13'
else:
    start = max_exp_date
start = dateutil.parser.parse(start)
print(start)
startminus7 = start - timedelta(days=7)
startminus14 = start - timedelta(days=14)

q = f"""
    select
        "review-id",
        "review",
        "author-name",
        "review-created-at",
        "star-rating"
    from
        "prod2-generico"."ecomm-playstore-reviews"
    where
        date("review-created-at")> '{startminus7}'
       """
reviews = rs_db.get_df(q)
print(reviews)
reviews.columns = [c.replace('-', '_') for c in reviews.columns]
reviews['review_created_at'] = pd.to_datetime(reviews['review_created_at'])
reviews['review_day_pre7'] = reviews['review_created_at'] - pd.DateOffset(days=7)
zeno_q = f"""
    select
        zo.id as zeno_order_id_before_review ,
        zo."patient-id" ,
        zo."created-at" as order_created_at,
        p.phone,
        p."name" as "matched-name"
    from
        "prod2-generico"."zeno-order" zo
    left join "prod2-generico".patients p on
        zo."patient-id" = p.id
    where
        date(zo."created-at") > '{startminus14}'
        and p."name" is not null
    """
zeno_orders = rs_db.get_df(zeno_q)
reviews['i'] = 1
zeno_orders['i'] = 1
merged_df = pd.merge(reviews, zeno_orders, how='outer', on='i')
merged_df['author_name'] = merged_df['author_name'].str.lower()
merged_df['matched-name'] = merged_df['matched-name'].str.lower()
merged_df['lev_ratio'] = merged_df.apply(lambda row: lev.ratio(row['author_name'], row['matched-name']), 1)
merged_df['rank_order'] = merged_df.sort_values(['zeno_order_id_before_review'], ascending=[False]) \
                              .groupby(['review_id', 'matched-name']) \
                              .cumcount() + 1
latest_order = merged_df[(merged_df['rank_order'] == 1)]
latest_order.columns
latest_order['top_3_matches'] = latest_order.sort_values(['lev_ratio'], ascending=[False]).groupby(['review_id']) \
                                    .cumcount() + 1
latest_order = latest_order[(latest_order['top_3_matches'] <= 3)]
latest_order = latest_order.sort_values(['star_rating', 'review_id', 'top_3_matches']
                                        , ascending=[True, True, True])
latest_order.columns = [c.replace('_', '-') for c in latest_order.columns]
latest_order_data = latest_order[['review-id', 'review', 'star-rating', 'review-created-at', 'author-name',
                                  'matched-name', 'zeno-order-id-before-review', 'patient-id'
    , 'order-created-at', 'phone', 'lev-ratio']]
latest_order_mail = latest_order[['review-id', 'review', 'star-rating', 'review-created-at', 'author-name',
                                  'matched-name', 'zeno-order-id-before-review', 'patient-id'
    , 'order-created-at']]
# etl
latest_order_data['created-at'] = datetime.datetime.now(tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
latest_order_data['updated-at'] = datetime.datetime.now(tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
latest_order_data['created-by'] = 'etl-automation'
latest_order_data['updated-by'] = 'etl-automation'
latest_order_data=latest_order_data[(pd.to_datetime(latest_order_data['review-created-at']) > start)]
latest_order_mail=latest_order_mail[(pd.to_datetime(latest_order_mail['review-created-at']) > start)]
if latest_order_mail.empty:
    print('DataFrame is empty!')
    exit()
if isinstance(table_info, type(None)):
    raise Exception(f"table: {table_name} do not exist, create the table first")
else:
    logger.info(f"Table:{table_name} exists")
print(start)
truncate_query = f''' DELETE FROM "{schema}"."{table_name}" where DATE("review-created-at") >'{start}' '''
print(truncate_query)
rs_db_write.execute(truncate_query)
s3.write_df_to_db(df=latest_order_data[table_info['column_name']], table_name=table_name, db=rs_db_write,
                  schema=schema)
file_name = 'Zeno_playstore.xlsx'
file_path = s3.write_df_to_excel(data={'Zeno Playstore': latest_order_mail}, file_name=file_name)

email = Email()
# file_path ='/Users/Lenovo/Downloads/utter.csv'
email.send_email_file(subject="Zeno Playstore",
                      mail_body='Zeno Playstore',
                      to_emails=email_to, file_uris=[], file_paths=[file_path])
# Closing the DB Connection
rs_db.close_connection()