#!/usr/bin/env python
# coding: utf-8

import os
import sys

sys.path.append('../../../..')

from zeno_etl_libs.helper.aws.s3 import S3
from zeno_etl_libs.helper.email.email import Email
from zeno_etl_libs.db.db import DB, MySQL
from zeno_etl_libs.config.common import Config
from zeno_etl_libs.logger import get_logger
from zeno_etl_libs.helper import helper
from dateutil.tz import gettz

import json
import datetime

import argparse
import pandas as pd
import numpy as np
import traceback

parser = argparse.ArgumentParser(description="This is ETL script.")
parser.add_argument('-e', '--env', default="dev", type=str, required=False)
parser.add_argument('-et', '--email_to', default="saurav.maskar@zeno.health", type=str, required=False)
parser.add_argument('-sku', '--sku_to_add_daily', default=18, type=int, required=False)
parser.add_argument('-ccf', '--cold_chain_flag', default=0, type=str, required=False)
parser.add_argument('-si', '--stores_to_include_if_blank_all', default="NULL", type=str, required=False)
parser.add_argument('-se', '--stores_to_exclude_if_blank_none', default="NULL", type=str, required=False)
parser.add_argument('-qc', '--quantity_cap', default=70, type=int, required=False)
args, unknown = parser.parse_known_args()
env = args.env
email_to = args.email_to
sku_to_add_daily = args.sku_to_add_daily
# Cold Chain Parameter Logic - If 0 - Don't add cold chain products, IF 2 - Only add cold chain product, If 1 - Don't care if cold chain product is added or not
cold_chain_flag = args.cold_chain_flag
stores_to_include_if_blank_all = args.stores_to_include_if_blank_all
stores_to_exclude_if_blank_none = args.stores_to_exclude_if_blank_none
quantity_cap = args.quantity_cap

quantity_cap = int(quantity_cap)

os.environ['env'] = env

logger = get_logger(level='INFO')

logger.info(f"env: {env}")

rs_db = DB()
rs_db.open_connection()

rs_db_write = DB(read_only=False)
rs_db_write.open_connection()

s3 = S3()
start_time = datetime.datetime.now()
logger.info('Script Manager Initialized')
logger.info("")
logger.info("parameters reading")
logger.info(f"env: {env}")
logger.info("email_to - " + email_to)
logger.info("sku_to_add_daily - " + str(sku_to_add_daily))
logger.info("cold_chain_flag - " + str(cold_chain_flag))
logger.info("stores_to_include_if_blank_all - " + str(stores_to_include_if_blank_all))
logger.info("stores_to_exclude_if_blank_none - " + str(stores_to_exclude_if_blank_none))
logger.info("quantity_cap - " + str(quantity_cap))
logger.info("")

# date parameter
logger.info("code started at {}".format(datetime.datetime.now().strftime(
    '%Y-%m-%d %H:%M:%S')))
logger.info("")

cur_date = datetime.datetime.now(tz=gettz('Asia/Kolkata')).date()

# =============================================================================
# set parameters, to adhere to adhoc request of adding/excluding NPI in mentioned stores only
# =============================================================================

parameter_input1 = False
parameter_input2 = False


# Writng this function so that we can get list of stores irrespective of input format in parameter
def fetch_number(list):
    list2 = []
    for i in list:
        try:
            int(i)
            list2.append(int(i))
        except:
            pass
    return list2


if stores_to_include_if_blank_all == 'NULL' and stores_to_exclude_if_blank_none == 'NULL':
    parameter_input1 = False
    parameter_input2 = False
    logger.info('Missing parameters, Taking all stores')
else:
    if stores_to_include_if_blank_all != 'NULL':
        parameter_input1 = True
        stores_to_include_if_blank_all = stores_to_include_if_blank_all
        stores_to_include_if_blank_all = fetch_number(stores_to_include_if_blank_all.split(','))
        logger.info('read parameters to include stores, taking included stores only - {}'.format(
            stores_to_include_if_blank_all))
    if stores_to_exclude_if_blank_none != 'NULL':
        parameter_input2 = True
        stores_to_exclude_if_blank_none = stores_to_exclude_if_blank_none
        stores_to_exclude_if_blank_none = fetch_number(stores_to_exclude_if_blank_none.split(','))
        logger.info('read parameters to exclude stores, not taking excluded stores - {}'.format(
            stores_to_exclude_if_blank_none))

# =============================================================================
# NPI Removal Script
# =============================================================================

# Getting prod drug detail
prod_drugs_query = '''
    select
        id as "drug-id",
        "drug-name",
        type,
        "pack-form",
        "cold-chain" 
    from
        "prod2-generico"."drugs"
        '''
prod_drugs = rs_db.get_df(prod_drugs_query)

# getting my sql store_drug list
store_drug_prod_query = '''
    select
        "store-id" ,
        "drug-id",
        1 as "dummy"
    from
        "prod2-generico"."npi-drugs" nd
    where
        status in ('saved', 'in-progress')
        or (status = 'completed'
            and date(nd."created-at") > date(dateadd(d,-45,current_date)))
        '''
store_drug_prod = rs_db.get_df(store_drug_prod_query)

# getting store_id list

# connection = current_config.data_science_postgresql_conn()
# store_list_query = '''
#          select distinct store_id
#             from dead_stock_inventory dsi
#             where inventory_type = 'Rotate'
#     '''
# store_list = pd.read_sql_query(store_list_query, connection)
# connection.close()

store_list_query = '''
    select
        distinct "store-id"
    from
        "prod2-generico"."npi-inventory-at-store" nias
    where
        "inventory-type" = 'Rotate'
        and nias."clust-sold-flag" = 0
        and nias."shelf-life-more-than-6-months-flag" = 1
        '''
store_list = rs_db.get_df(store_list_query)

if parameter_input1:
    store_list = pd.DataFrame(stores_to_include_if_blank_all)
    store_list.rename(columns={0: 'store-id'}, inplace=True)

if parameter_input2:
    store_list[~store_list['store-id'].isin(stores_to_exclude_if_blank_none)]

# getting last day store status

store_completed = pd.DataFrame()
store_last_status_query = """
    select
        *
    from
        (
        select
            row_number() over (partition by nd."store-id"
        order by
            nd."created-at" desc
              ) as "row",
            nd."store-id",
            nd.status ,
            nd."created-at"
        from
            "prod2-generico"."npi-drugs" nd) nd
    where
        nd."row" = 1
"""
store_last_status = rs_db.get_df(store_last_status_query)

store_completed = store_last_status[store_last_status['status']=='completed']['store-id']
store_completed  = pd.DataFrame(store_completed,columns=['store-id'])

# Checking If any new store is added
nd_stores = store_last_status['store-id'].unique()
new_stores = pd.DataFrame()
for store in store_list['store-id']:
    if store not in nd_stores:
        #print(store)
        store_new = pd.DataFrame([store], columns=['store-id'])
        new_stores = new_stores.append(store_new)

store_completed = pd.concat([store_completed,new_stores])
#
# for store in store_list['store-id']:
#     store_completed_query = '''
#             select
#                 distinct "store-id"
#             from
#                 "prod2-generico"."npi-drugs"
#             where
#                 date("created-at") =
#                         (
#                 select
#                     Max(date("created-at"))
#                 from
#                     "prod2-generico"."npi-drugs"
#                 where
#                     "store-id"= {store})
#                 and status = 'completed'
#                 and "store-id"= {store}
#             '''.format(store=store)
#     store_completed_1 = rs_db.get_df(store_completed_query)
#
#     if len(store_completed_1)== 0:
#         new_store = """
#         SELECT
#             DISTINCT nd."store-id"
#         FROM
#             "prod2-generico"."npi-drugs" nd
#         WHERE
#             nd."store-id" = {store}
#         """.format(store=store)
#         new_store = rs_db.get_df(new_store)
#
#         if len(new_store)== 0:
#             store_completed_1 = pd.DataFrame([store],columns=['store-id'])
#
#     store_completed = store_completed_1.append(store_completed)

# getting PG drug list

# connection = current_config.data_science_postgresql_conn()
# npi_drug_list = """
#         select store_id, drug_id,
#         sum(locked_quantity + quantity) as "total_quantity",
#         sum(locked_value + value) as "total_value"
#         from dead_stock_inventory dsi
#         where inventory_type = 'Rotate'
#         group by store_id, drug_id
#     """
# npi_drug_list = pd.read_sql_query(npi_drug_list, connection)
# connection.close()

npi_drug_list = """
        select
            "store-id",
            "drug-id",
            sum("locked-quantity" + "quantity") as "total-quantity",
            sum("locked-value" + "value") as "total-value"
        from
            "prod2-generico"."npi-inventory-at-store" nias
        where
            "inventory-type" = 'Rotate'
            and nias."clust-sold-flag" = 0
            and nias."shelf-life-more-than-6-months-flag" = 1
        group by
            "store-id",
            "drug-id"
       """
npi_drug_list = rs_db.get_df(npi_drug_list)

# merging  npi list with drugs table for packform
npi_drug_list = npi_drug_list.merge(prod_drugs, how='inner', on='drug-id')

# =============================================================================
# Adding Quantity Sold at System level
# =============================================================================

drgs = tuple(map(int,npi_drug_list['drug-id'].unique()))

s1 = """
    select
        "drug-id",
        sum("net-quantity") as "system-sales-qty-last-90-days"
    from
        "prod2-generico"."sales" sh
    where
        date("created-at") >= date(current_date - 90)
        and date("created-at") <= date(current_date)
        and "drug-id" in {drgs}
    group by
        "drug-id"
""".format( drgs=drgs)

quantity_sold = rs_db.get_df(s1)
npi_drug_list = npi_drug_list.merge(quantity_sold,on = 'drug-id', how ='left')
npi_drug_list['system-sales-qty-last-90-days'] = npi_drug_list['system-sales-qty-last-90-days'].fillna(0)

# =============================================================================
# System Searched quantity last 90 days
# =============================================================================
s2 = """
    select
        "drug-id",
        sum("search-count-clean") as "system-searched-qty-last-90-days"
    from
        "prod2-generico"."cfr-searches-v2" csv2
    where
        date("search-date")  >= date(current_date - 90)
        and date("search-date")  <= date(current_date)
        and "drug-id" in {drgs}
    group by
        "drug-id"
""".format( drgs=drgs)

drugs_searched = rs_db.get_df(s2)
npi_drug_list = npi_drug_list.merge(drugs_searched,on = 'drug-id', how ='left')

npi_drug_list['system-searched-qty-last-90-days'] = npi_drug_list['system-searched-qty-last-90-days'].fillna(0)

npi_drug_list['liquidation-index'] = npi_drug_list['system-sales-qty-last-90-days']*0.8+npi_drug_list['system-searched-qty-last-90-days']*0.2

if int(cold_chain_flag) == 0:
    npi_drug_list = npi_drug_list[npi_drug_list['cold-chain']==0]
    logger.info('removing cold chain products')
elif int(cold_chain_flag) == 2:
    npi_drug_list = npi_drug_list[npi_drug_list['cold-chain'] == 1]
    logger.info('considering only cold chain products')
else:
    logger.info('Not caring whether cold chain items are added or not')

# merging prod and DSS to avoid duplicate entries
npi_drug_list = npi_drug_list.merge(store_drug_prod, how='left', on=['store-id', 'drug-id'])

# merging with completed stores
npi_drug_list = npi_drug_list.merge(store_completed, how='inner', on=['store-id'])

# replaceing null with 0 and extracting 35 rows
npi_drug_list = npi_drug_list.replace(np.nan, 0)

npi_drug_list = npi_drug_list[npi_drug_list.dummy == 0]

npi_drug_list=npi_drug_list[~npi_drug_list['type'].isin(['discontinued-products','banned'])]

choice = [npi_drug_list['type'] == 'high-value-ethical',
          npi_drug_list['type'] == 'ethical',
          npi_drug_list['type'] == 'generic',
          npi_drug_list['type'] == 'ayurvedic',
          npi_drug_list['type'] == 'surgical',
          npi_drug_list['type'] == 'category-4',
          npi_drug_list['type'] == 'otc',
          npi_drug_list['type'] == 'general',
          npi_drug_list['type'] == 'baby-food',
          npi_drug_list['type'] == 'baby-product',
          npi_drug_list['type'] == 'glucose-test-kit',
          npi_drug_list['type'] == 'discontinued-products',
          npi_drug_list['type'] == 'banned']

select = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]

npi_drug_list['sort-type'] = np.select(choice, select, default=999)

npi_drug_list.sort_values(['store-id', 'liquidation-index',  'sort-type', 'pack-form', 'drug-name'],
                          ascending=[True, False, True, True, True], inplace=True)

# Adding decided SKU (18 - parameter - sku_to_add_daily) per day
final_list = npi_drug_list.groupby('store-id').head(sku_to_add_daily).reset_index(drop=True)

# Capping quantity to decided number for outside mumbai(70 - Paramenter - quantity_cap)
final_list['total-quantity'] = final_list['total-quantity'].astype(float)
final_list['cum_sum_quantity_per_store'] =  final_list.groupby(['store-id'])['total-quantity'].cumsum()

# Atleast one sku should be added
final_list['sku_rank'] = final_list.groupby(['store-id']).cumcount()+1

# Adding city ids
# Mumbai citi ids - 1 - Mumbai, 3 - Thane, 2 - Navi Mumbai

store_ids = tuple(map(int,final_list['store-id'].unique()))

additng_city_id_query = """
    select
        s.id as "store-id",
        s."city-id",
        zc."name" as "city-name"
    from
        "prod2-generico".stores s
    left join "prod2-generico"."zeno-city" zc 
    on
        s."city-id" = zc.id 
    where s.id in {store_ids}
""".format(store_ids=store_ids)

additng_city_id = rs_db.get_df(additng_city_id_query)

final_list = final_list.merge(additng_city_id,how = 'left', on = 'store-id')

final_list['city-id'] = final_list['city-id'].astype(int)

conditions = [final_list['city-id'].isin([1,2,3]),final_list['sku_rank']==1,final_list['sku_rank']!=1]
choices = [1,1,final_list['cum_sum_quantity_per_store']]
final_list['quantity_cap_index'] = np.select(conditions, choices, default = 0)

final_list = final_list[final_list['quantity_cap_index']<quantity_cap]

logger.info(f'for outside mumbai cities quantity is capped to {quantity_cap}')

final_list['created-date'] = cur_date
final_list['created-by'] = 'data.science@zeno.health'

final_list_npi = final_list[['store-id', 'drug-id']]

expected_data_length_insert = len(final_list_npi)
logger.info("mySQL - Resulted data length after insert should be is {}".format(expected_data_length_insert))

schema = 'prod2-generico'
table_name = 'npi-removal'
table_info = helper.get_table_info(db=rs_db_write, table_name=table_name, schema=schema)
status1 = False
status2 = False

if isinstance(table_info, type(None)):
    raise Exception(f"table: {table_name} do not exist, create the table first")
else:
    logger.info(f"Table:{table_name} exists")

    s3.write_df_to_db(df=final_list[table_info['column_name']], table_name=table_name, db=rs_db_write,
                      schema=schema)

    logger.info(str(table_name) + ' table uploaded')
    status1 = True

if status1:
    mysql_write = MySQL(read_only=False)
    mysql_write.open_connection()

    # inserting data into prod

    logger.info("mySQL - Insert starting")

    final_list_npi.to_sql(name='npi-drugs', con=mysql_write.engine,
                          if_exists='append', index=False,
                          method='multi', chunksize=500)

    logger.info("mySQL - Insert ended")
    status2 = True

npi_added_uri = s3.save_df_to_s3(df=final_list, file_name='npi_removal_details_{}.csv'.format(cur_date))

if status2 is True:
    status = 'Success'
else:
    status = 'Failed'

end_time = datetime.datetime.now()
difference = end_time - start_time
min_to_complete = round(difference.total_seconds() / 60, 2)
email = Email()

email.send_email_file(subject=f"{env}-{status} : {table_name} table updated",
                      mail_body=f"{table_name} table updated, Time for job completion - {min_to_complete} mins ",
                      to_emails=email_to, file_uris=[npi_added_uri])

rs_db.close_connection()
rs_db_write.close_connection()
mysql_write.close()

