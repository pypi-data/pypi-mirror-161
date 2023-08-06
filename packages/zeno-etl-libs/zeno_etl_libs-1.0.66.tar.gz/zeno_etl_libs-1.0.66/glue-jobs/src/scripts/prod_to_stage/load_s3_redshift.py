import argparse
import sys
import os

sys.path.append('../../../..')

from zeno_etl_libs.logger import get_logger
from zeno_etl_libs.db.db import DB
from zeno_etl_libs.helper.aws.s3 import S3

parser = argparse.ArgumentParser(description="This is ETL script.")
parser.add_argument('-e', '--env', default="dev", type=str, required=False,
                    help="This is env(dev, stag, prod)")

args, unknown = parser.parse_known_args()

env = args.env
os.environ['env'] = env
logger = get_logger()

rs_db = DB(read_only=False)
rs_db.open_connection()

s3 = S3()

schema = 'prod2-generico'

if env not in ['stage', 'dev']:
    raise Exception("Use Stage job for loading data into redshift")

response = s3.s3_client.list_objects_v2(Bucket=s3.bucket_name, Prefix="unload/")
files_in_folder = response["Contents"]
tablename_list = []
for f in files_in_folder:
    tablename_list.append(f["Key"].split('/')[1])
tablename_list = list(set(tablename_list))

for i in tablename_list:
    query = f''' DELETE FROM "{schema}"."{i}"; '''
    rs_db.execute(query)
    s3.write_to_db_from_s3_csv(i, 's3://aws-glue-temporary-921939243643-ap-south-1/unload/'+i+'/', rs_db, schema, delete_folder=True)



