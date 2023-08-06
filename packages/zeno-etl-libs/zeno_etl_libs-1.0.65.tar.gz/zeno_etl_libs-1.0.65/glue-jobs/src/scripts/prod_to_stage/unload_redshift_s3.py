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
parser.add_argument('-d', '--table_name', default="", type=str, required=False)

args, unknown = parser.parse_known_args()

env = args.env
table_name = args.table_name
os.environ['env'] = env
logger = get_logger()
logger.info(f"table_name: {table_name}")

rs_db = DB()
rs_db.open_connection()

s3 = S3()

schema = 'prod2-generico'

if table_name.__contains__(','):
    list_tables = table_name.split(',')
    for i in list_tables:
        s3.unload_redshift_s3(i, 's3://aws-glue-temporary-921939243643-ap-south-1/unload/'+i+'/', rs_db, schema)
else:
    s3.unload_redshift_s3(table_name, 's3://aws-glue-temporary-921939243643-ap-south-1/unload/'+table_name+'/', rs_db, schema)




