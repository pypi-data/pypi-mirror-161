import argparse
import sys
import os
import datetime

sys.path.append('../../../..')

from zeno_etl_libs.db.db import DB
from zeno_etl_libs.helper.aws.s3 import S3
from zeno_etl_libs.logger import get_logger

parser = argparse.ArgumentParser(description="This is ETL script.")
parser.add_argument('-e', '--env', default="dev", type=str, required=False,
                    help="This is env(dev, stag, prod)")

args, unknown = parser.parse_known_args()

env = args.env
print(env)
os.environ['env'] = env

logger = get_logger(level="INFO")
logger.info(f"ENV: {env}")
rs_db = DB()
rs_db.open_connection()

s3 = S3(bucket_name=f"{env}-zeno-s3-db")

#########################################################
# Drugs data extraction
########################################################
end_ts = datetime.datetime.now()
start_ts = end_ts + datetime.timedelta(days=-1)
end_ts = end_ts.strftime("%Y-%m-%d 00:00:00")
start_ts = start_ts.strftime("%Y-%m-%d 00:00:00")

drugs_q = f""" SELECT * FROM "prod2-generico"."drugs" 
where "updated-at" >= '{start_ts}' and "updated-at" < '{end_ts}'"""

logger.info(f"query: {drugs_q}")
data_drugs = rs_db.get_df(drugs_q)

logger.info(f"Total drugs with updates: {len(data_drugs)}")
# TODO: Make parquet format live
# f_name = 'drug-master/{}/data.parquet'.format(start_ts[:10].replace("-", "/"))
f_name = 'drug-master/{}/data.csv'.format(start_ts[:10].replace("-", "/"))

# uri = s3.save_df_to_s3_parquet(df=data_drugs, file_name=f_name)
uri = s3.save_df_to_s3(df=data_drugs, file_name=f_name)
print(uri)

# Closing the DB Connection
rs_db.close_connection()
