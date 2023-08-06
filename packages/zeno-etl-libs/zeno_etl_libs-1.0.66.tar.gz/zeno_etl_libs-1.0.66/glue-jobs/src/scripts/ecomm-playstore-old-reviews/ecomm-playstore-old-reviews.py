"""""
 To fetch past playstore reviews google to s3 to DB
"""""

import argparse
import os
import sys
from io import StringIO
import datetime
import dateutil
from dateutil.tz import gettz

import pandas as pd

sys.path.append('../../../..')

from zeno_etl_libs.logger import get_logger
from zeno_etl_libs.helper.aws.s3 import S3
from zeno_etl_libs.helper import helper
from zeno_etl_libs.db.db import DB

parser = argparse.ArgumentParser(description="This is ETL script.")
parser.add_argument('-e', '--env', default="dev", type=str, required=False,
                    help="This is env(dev, stage, prod)")
parser.add_argument('-d', '--full_run', default=0, type=int, required=False)
parser.add_argument('-l', '--max_month', default=6, type=int, required=False)
args, unknown = parser.parse_known_args()
env = args.env
full_run = args.full_run
max_month = args.max_month
os.environ['env'] = env
logger = get_logger()
logger.info(f"info message")
logger.info(f"full_run: {full_run}")

rs_db = DB(read_only=False)
rs_db.open_connection()
reviews = pd.DataFrame()
s3 = S3()
logger.info(f"max_month: {max_month}")
if full_run == 1:
    for year in (21, 22):
        for month in range(1, 12):
            if month > max_month and year == 22:
                """ stopping """
                continue
            uri = f"s3://aws-glue-temporary-921939243643-ap-south-1/playstore-reviews/reviews_reviews_com.zenohealth.android_20{year}{str(month).zfill(2)}.csv"
            logger.info(f"uri: {uri}")
            csv_string = s3.get_file_object(uri=uri, encoding="utf-16")
            df = pd.read_csv(StringIO(csv_string))
            df['month'] = str(month).zfill(2)
            df['year'] = str(year)
            reviews = pd.concat([reviews, df], ignore_index=True)

else:
        last_month_date = datetime.datetime.now() - datetime.timedelta(days=30)
        last_year = last_month_date.strftime("%Y")[2:]
        last_month = last_month_date.strftime("%m")
        logger.info(f"last_month_date: {last_month_date} last year : {last_year} last month : {last_month} ")
        uri = f"s3://aws-glue-temporary-921939243643-ap-south-1/playstore-reviews/reviews_reviews_com.zenohealth.android_20" \
              f"{last_year}{str(last_month).zfill(2)}.csv"
        logger.info(f"uri: {uri}")
        csv_string = s3.get_file_object(uri=uri, encoding="utf-16")
        reviews = pd.read_csv(StringIO(csv_string))
        reviews['month'] = str(last_month)
        # reviews['month'] = reviews['month'].astype('str', errors='ignore')[2:]
        reviews['year'] = str(last_year)
        # reviews['year'] = reviews['year'].astype('str', errors='ignore')
columns = [c.replace(" ", "-").lower() for c in reviews.columns]
reviews.columns = columns
for col in ['review-submit-date-and-time', 'review-last-update-date-and-time','developer-reply-date-and-time']:
    reviews[col] = pd.to_datetime(reviews[col], errors='coerce').dt.strftime('%Y-%m-%d %H:%M:%S')
    reviews[col] = reviews[col].replace('NaT', '')

reviews['created-at'] = datetime.datetime.now(tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
reviews['updated-at'] = datetime.datetime.now(tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
reviews['created-by'] = 'etl-automation'
reviews['updated-by'] = 'etl-automation'

# Table info
schema = 'prod2-generico'
table_name = 'ecomm-playstore-old-reviews'
table_info = helper.get_table_info(db=rs_db, table_name=table_name, schema=schema)

if isinstance(table_info, type(None)):
    raise Exception(f"table: {table_name} do not exist, create the table first")

logger.info(f"Table:{table_name} exists and input data has all columns")

if full_run == 1:
    truncate_query = f''' DELETE FROM "{schema}"."{table_name}" '''
else:
    truncate_query = f''' DELETE FROM "{schema}"."{table_name}" where "month">={last_month} and "year">={last_year}'''
rs_db.execute(truncate_query)
s3.write_df_to_db(df=reviews[table_info['column_name']], table_name=table_name, db=rs_db, schema=schema)
logger.info("Pushed reviews successfully")
rs_db.close_connection()
