"""""
 To provide patient view for franchise billing panel
 author : neha.karekar@zeno.health
"""""

import argparse
import os
import sys
import datetime
import dateutil
from dateutil.tz import gettz
from datetime import datetime as dt
from datetime import date, timedelta
import pandas as pd
import numpy as np

sys.path.append('../../../..')

from zeno_etl_libs.logger import get_logger
from zeno_etl_libs.helper.aws.s3 import S3
from zeno_etl_libs.helper import helper
from zeno_etl_libs.db.db import DB

parser = argparse.ArgumentParser(description="This is ETL script.")
parser.add_argument('-e', '--env', default="dev", type=str, required=False,
                    help="This is env(dev, stage, prod)")
args, unknown = parser.parse_known_args()
env = args.env
os.environ['env'] = env
logger = get_logger()
logger.info(f"info message")

rs_db = DB()
rs_db_write = DB(read_only=False)
rs_db.open_connection()
rs_db_write.open_connection()
s3 = S3()

schema = 'prod2-generico'
table_name = 'franchise-patient-one-view'
table_info = helper.get_table_info(db=rs_db_write, table_name=table_name, schema=schema)

# creating summary data using bills info

pat_store_q = """
    select
        s."patient-id",
        s."store-id" ,
        count(distinct "bill-id") "total-bills-to-store",
        sum(s."revenue-value") "total-value-to-store",
        max(date("created-at")) "last-transacted-at",
        max("bill-id") "last-bill-id"
    from
        "prod2-generico".sales s
    where
        "franchisee-id" != 1
        and "bill-flag" = 'gross'
    group by
        1,
        2
    having
        "last-transacted-at"> DATEADD('month',
        -6,
        DATE_TRUNC('month', CURRENT_DATE))
"""
pat_store = rs_db.get_df(pat_store_q)

# taking refill date
refill_q = f"""
    select
        "patient-id",
        "store-id",
        min("refill-date") as "expected-next-date"
    from
        "prod2-generico"."retention-refill"
    where
        "bill-id" in {tuple(pat_store['last-bill-id'].unique())}
    group by
        1,
        2
        """
refill = rs_db.get_df(refill_q)

pat_store_refill = pd.merge(pat_store, refill, how='left', on=['patient-id', 'store-id'])
pat_store_refill[(pd.isnull(pat_store_refill['expected-next-date']) == True)].head()
pat_store_refill['expected-next-date'] = np.where(pd.isnull(pat_store_refill['expected-next-date']) == True,
                                         pat_store_refill['last-transacted-at'] +
                                         timedelta(days=30), pat_store_refill['expected-next-date'])

#segment category
seg_q = """
    select
        id as "patient-id",
        "patient-category"
    from
        "prod2-generico".patients
    where
        id in {}
""".format(tuple(pat_store_refill['patient-id'].unique()))
seg = rs_db.get_df(seg_q)

pat_store_refill_seg = pd.merge(pat_store_refill, seg, how='left', on=['patient-id'])

#etl
pat_store_refill_seg['created-at'] = datetime.datetime.now(tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
pat_store_refill_seg['updated-at'] = datetime.datetime.now(tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
pat_store_refill_seg['created-by'] = 'etl-automation'
pat_store_refill_seg['updated-by'] = 'etl-automation'

if pat_store_refill_seg.empty:
    print('DataFrame is empty!')
    exit()
if isinstance(table_info, type(None)):
    raise Exception(f"table: {table_name} do not exist, create the table first")
else:
    logger.info(f"Table:{table_name} exists")

truncate_query = f''' DELETE FROM "{schema}"."{table_name}"'''
print(truncate_query)
rs_db_write.execute(truncate_query)
s3.write_df_to_db(df=pat_store_refill_seg[table_info['column_name']], table_name=table_name, db=rs_db_write,
                  schema=schema)
rs_db.close_connection()
rs_db_write.close_connection()

