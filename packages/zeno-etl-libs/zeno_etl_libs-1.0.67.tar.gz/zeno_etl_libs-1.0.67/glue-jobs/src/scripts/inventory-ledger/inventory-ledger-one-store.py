import argparse
import datetime
import sys
import os

sys.path.append('../../../..')

from zeno_etl_libs.logger import get_logger
from zeno_etl_libs.db.db import DB
from zeno_etl_libs.utils.inventory.inventory import Data
from zeno_etl_libs.helper.aws.s3 import S3

parser = argparse.ArgumentParser(description="This is ETL script.")
parser.add_argument('-e', '--env', default="dev", type=str, required=False,
                    help="This is env(dev, stage, prod)")
parser.add_argument('-sd', '--start_date', default="2022-06-01", type=str, required=False, help="Start date in IST")
parser.add_argument('-ed', '--end_date', default="2022-06-26", type=str, required=False, help="End date in IST")
parser.add_argument('-si', '--store_id', default="215", type=int, required=False,
                    help="")
parser.add_argument('-lfp', '--local_file_path', default="/Users/kuldeep/Downloads", type=str, required=False, help="")

args, unknown = parser.parse_known_args()
env = args.env
start_date = args.start_date
end_date = args.end_date
store_id = args.store_id
local_file_path = args.local_file_path

os.environ['env'] = env
logger = get_logger()

""" read connection """
db = DB()
db.open_connection()

s3 = S3(bucket_name=f"{env}-zeno-s3-db")

if not (start_date and end_date) or start_date == "NA" or end_date == "NA":
    """ if no dates given, then run for yesterday """
    end_date = datetime.datetime.now().strftime("%Y-%m-%d")
    start_date = datetime.datetime.now() + datetime.timedelta(days=-1)
    start_date = start_date.strftime("%Y-%m-%d")

"""
Instructions to use(README):
    0. Make sure tables for both the dates (start and end) are present in public schema (eg: bills-1-mis-2022-06-11)
    1. set the start date and end date
    2. Set the store id 
    3. Data is uploaded to s3(ie. prod-zeno-s3-db) inside "inventory/ledger/" folder (eg: s3://prod-zeno-s3-db/inventory/ledger/adhoc/2022/06/11/240.csv)
    4. S3 Data can be queried using AWS Athena

Tables Required:
    inventory-1,invoice-items-1,invoices-1,customer-return-items-1,customer-returns-1,stock-transfer-items-1,
    stock-transfers-1,bill-items-1,bills-1,return-items-1,returns-to-dc-1,deleted-invoices,deleted-invoices-1,
    inventory-changes-1 
"""

""" this column order will be maintained across all csv files """
column_order = ["id", "barcode", "ptr", "o", "cr", "xin", "xout", "sold", "ret", "ar", "rr", "del", "c", "e",
                'start-time', 'end-time', 'purchase-rate', 'drug-name']

""" calculating the data """
data = Data(db=db, csv_store_ids=f"{store_id}", start_date=start_date, end_date=end_date)
recon_df = data.concat()

recon_df['start-time'] = data.start_ts
recon_df['end-time'] = data.end_ts

""" add other meta data """
meta_df = data.get_meta_data()

df = recon_df.merge(meta_df, how='left', on=['id'])


""" for testing the s3 part """
# recon_df = pd.DataFrame(data=[[1,2,3,4,5,6,7,8,9,0,1,2,3,4]], columns=column_order)
file_name = f"store-{store_id}-{start_date}-{end_date}.csv"
uri = s3.save_df_to_s3(df=df[column_order], file_name=f"inventory/ledger/adhoc/{file_name}", index=False)

if local_file_path:
    local_file_path = f"{local_file_path}/{file_name}"
    df.to_csv(path_or_buf=local_file_path)

logger.info(f"Uploaded successfully @ {uri}")
