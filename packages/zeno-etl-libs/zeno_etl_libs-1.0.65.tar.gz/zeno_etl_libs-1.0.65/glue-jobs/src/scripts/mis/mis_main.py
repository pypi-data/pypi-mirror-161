# =============================================================================
# purpose: MIS Automation
# =============================================================================

import os
import sys


sys.path.append('../../../..')

from zeno_etl_libs.helper.aws.s3 import S3
from zeno_etl_libs.helper.email.email import Email
from zeno_etl_libs.db.db import DB
from zeno_etl_libs.logger import get_logger
from zeno_etl_libs.helper import helper
from dateutil.tz import gettz
from zeno_etl_libs.queries.mis.mis_class import Mis
from zeno_etl_libs.queries.mis import mis_queries
import datetime


import json
import argparse
import pandas as pd
import numpy as np
import traceback
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

parser = argparse.ArgumentParser(description="This is ETL script.")
parser.add_argument('-e', '--env', default="dev", type=str, required=False)
parser.add_argument('-et', '--email_to', default="saurav.maskar@zeno.health", type=str, required=False)
parser.add_argument('-met', '--mis_email_to', default="mis.zeno@zeno.health,rupa.sharma@zeno.health,vaibhav.bhawar@zeno.health,saurav.maskar@zeno.health,vijay.pratap@zeno.health", type=str, required=False)
parser.add_argument('-dt', '--mis_db_date', default="NA", type=str, required=False)
parser.add_argument('-sc', '--schema_to_select', default="public", type=str, required=False)
parser.add_argument('-cy', '--choose_year', default="NA", type=str, required=False)
parser.add_argument('-cm', '--choose_month', default="NA", type=str, required=False)
parser.add_argument('-pc', '--power_consumer_value', default=2000, type=int, required=False)
args, unknown = parser.parse_known_args()
env = args.env
email_to = args.email_to
mis_email_to = args.mis_email_to
mis_db_date = args.mis_db_date
schema_to_select = args.schema_to_select
choose_year = args.choose_year
choose_month = args.choose_month
power_consumer_value = args.power_consumer_value
power_consumer_value = int(power_consumer_value)

if choose_month=='NA':
    choose_month = datetime.datetime.now(tz=gettz('Asia/Kolkata')).month
    if choose_month == 1:
        choose_month = 12
    else:
        choose_month = choose_month-1

if choose_year=='NA':
    choose_year = datetime.datetime.now(tz=gettz('Asia/Kolkata')).year
    if choose_month==1:
        choose_year = choose_year-1
    else:
        choose_year = choose_year

analysis_start_time = datetime.datetime(int(choose_year),int(choose_month),1,0,0,0).strftime('%Y-%m-%d %H:%M:%S')

if int(choose_month)== 12:
    analysis_end_time = (datetime.datetime((int(choose_year)+1),1,1,23,59,59)-datetime.timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
else:
    analysis_end_time = (datetime.datetime(int(choose_year), (int(choose_month) + 1), 1, 23, 59, 59) - datetime.timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')

if mis_db_date == 'NA':
    if int(choose_month)==12:
        mis_db_date = (datetime.datetime((int(choose_year)+1),1,1,23,59,59)-datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    else:
        mis_db_date = (datetime.datetime(int(choose_year), (int(choose_month) + 1), 1, 23, 59, 59) - datetime.timedelta(days=1)).strftime('%Y-%m-%d')

suffix_to_table = '-mis-' + str(mis_db_date)

os.environ['env'] = env

logger = get_logger(level='INFO')

rs_db = DB()

rs_db.open_connection()

rs_db_write = DB(read_only=False)
rs_db_write.open_connection()

s3 = S3()
start_time = datetime.datetime.now(tz=gettz('Asia/Kolkata'))
today_date = start_time.strftime('%Y-%m-%d')
logger.info('Script Manager Initialized')
logger.info(f"env: {env}")
logger.info("email_to - " + email_to)
logger.info("mis_email_to - " + mis_email_to)
logger.info("mis_db_date - " + str(mis_db_date))
logger.info("schema_to_select - " + str(schema_to_select))
logger.info("choose_year - " + str(choose_year))
logger.info("choose_month - " + str(choose_month))
logger.info("analysis_start_time - " + str(analysis_start_time))
logger.info("analysis_end_time - " + str(analysis_end_time))
logger.info("suffix_to_table - " + str(suffix_to_table))
logger.info("power_consumer_value - " + str(power_consumer_value))

logger.info("")

# date parameter
logger.info("code started at {}".format(datetime.datetime.now(tz=gettz('Asia/Kolkata')).strftime(
    '%Y-%m-%d %H:%M:%S')))
logger.info("")

mis = Mis(analysis_start_time,analysis_end_time,suffix_to_table,schema_to_select,choose_year,choose_month,rs_db,logger,mis_queries)

# order_source and stores are used in almost all jobs, please run them beforehand

order_source = mis.order_source()
stores = mis.store_list()

# =============================================================================
# MIS - Breakup/Unified
# two versions of MIS are provided to Accounts team, Breakup - Counts Goodaid as seperate entity
# Table name with no suffix will be used for Breakup
# For unified suffix _unified will be added
# =============================================================================

breakup_master = pd.DataFrame()
unified_master = pd.DataFrame()

status = False

try:
    # =============================================================================
    # prerequisite tables
    # =============================================================================

    # sales

    sales = mis.sales()

    sales_unified = sales.copy(deep=True)

    sales['order_source'] = np.where(sales.bill_id.isin(order_source.zeno_bill_id),
                                     "ecomm", "store")

    sales_unified['order_source'] = 'all'

    sales['type1'] = np.vectorize(mis.order_type_tag)(sales['company'],sales['type'],'breakup')

    sales_unified['type1'] = np.vectorize(mis.order_type_tag)(sales_unified['company'],sales_unified['type'],'unified')

    logger.info('fetched sales for selected period')

    # customer returns

    customer_returns = mis.customer_returns()

    customer_returns_unified = customer_returns.copy(deep = True)

    customer_returns['order_source'] = np.where(customer_returns.bill_id.isin(order_source.zeno_bill_id),
                                     "ecomm", "store")

    customer_returns_unified['order_source'] = 'all'

    customer_returns['type1'] = np.vectorize(mis.order_type_tag)(customer_returns['company'],customer_returns['type'],'breakup')

    customer_returns_unified['type1'] = np.vectorize(mis.order_type_tag)(customer_returns_unified['company'],customer_returns_unified['type'],'unified')

    logger.info('fetched customer returns data for selected period')

    # inventory
    inventory = mis.inventory()
    inventory_unified = inventory.copy(deep = True)

    inventory['type1'] = np.vectorize(mis.order_type_tag)(inventory['company'],inventory['type'],'breakup')
    inventory_unified['type1'] = np.vectorize(mis.order_type_tag)(inventory_unified['company'],inventory_unified['type'],'unified')

    logger.info('fetched inventory data')

    # cumulative_consumer_data
    cumulative_consumers_data = mis.cumulative_consumers_data()

    cumulative_consumers_data = pd.merge(left=cumulative_consumers_data, right=stores,
                                         how='left',
                                         on=['store_id'])

    logger.info('fetched cumulative consumers data')

    # all_cons_initial_bill_date

    all_cons_initial_bill_date = mis.cons_initial_bill_date()

    logger.info('fetched customers_initial_bill_date data')

    # home delivery data

    home_delivery_data = mis.home_delivery_data()

    home_delivery_data_unified = home_delivery_data.copy(deep = True)

    logger.info('fetched home delivery data')

    home_delivery_data['order_source'] = np.where(home_delivery_data.bill_id.isin(order_source.zeno_bill_id),
                                                  "ecomm", "store")
    home_delivery_data_unified['order_source'] = 'all'

    delivery_bill_ids = mis.delivery_bill_ids()

    logger.info('fetched delivery bill ids')

    # purchase_from_workcell

    purchase_from_wc_data = mis.purchase_from_wc_data()

    purchase_from_wc_data_unified = purchase_from_wc_data.copy(deep=True)

    purchase_from_wc_data['type1'] = np.vectorize(mis.order_type_tag)(purchase_from_wc_data['company'],purchase_from_wc_data['type'],'breakup')

    purchase_from_wc_data_unified['type1'] = np.vectorize(mis.order_type_tag)(purchase_from_wc_data_unified['company'],purchase_from_wc_data_unified['type'],'unified')

    logger.info('fetched purchase from wc data for selected period')

    # zippin_return_data

    zippin_return_data = mis.zippin_return_data()

    zippin_return_data_unified = zippin_return_data.copy(deep=True)

    zippin_return_data['type1'] = np.vectorize(mis.order_type_tag)(zippin_return_data['company'],zippin_return_data['type'],'breakup')

    zippin_return_data_unified['type1'] = np.vectorize(mis.order_type_tag)(zippin_return_data_unified['company'],zippin_return_data_unified['type'],'unified')

    logger.info('fetched zippin return data for selected period')

    # workcell_return_data

    workcell_return_data = mis.workcell_return_data()

    workcell_return_data_unified = workcell_return_data.copy(deep=True)

    workcell_return_data['type1'] = np.vectorize(mis.order_type_tag)(workcell_return_data['company'],workcell_return_data['type'],'breakup')

    workcell_return_data_unified['type1'] = np.vectorize(mis.order_type_tag)(workcell_return_data_unified['company'],workcell_return_data_unified['type'],'unified')

    logger.info('fetched workcell return data for selected period')

    # local_purchase_data

    local_purchase_data = mis.local_purchase_data()

    local_purchase_data_unified = local_purchase_data.copy(deep=True)

    local_purchase_data['type1'] = np.vectorize(mis.order_type_tag)(local_purchase_data['company'],local_purchase_data['type'],'breakup')

    local_purchase_data_unified['type1'] = np.vectorize(mis.order_type_tag)(local_purchase_data['company'],local_purchase_data['type'],'unified')

    logger.info('fetched local purchase data for selected period')

    # =============================================================================
    # 1. GMV_gross_payment
    # =============================================================================

    # prerequisite = sales

    breakup_gmv_gross_payment = mis.gmv_gross_payment(sales,stores)
    unified_gmv_gross_payment = mis.gmv_gross_payment(sales_unified,stores)

    logger.info('1. - GMV, Gross, Payment ran successfully')

    # =============================================================================
    # 2. netsale_tax_cogs
    # =============================================================================

    # prerequisite = sales, customer_returns

    breakup_netsale_tax_cogs = mis.netsale_tax_cogs(sales,customer_returns,stores)
    unified_netsale_tax_cogs = mis.netsale_tax_cogs(sales_unified,customer_returns_unified,stores)

    logger.info('2. - Net sale, Taxes, COGS ran successfully')

    breakup_master = pd.concat([breakup_gmv_gross_payment,breakup_netsale_tax_cogs],sort=True)
    unified_master = pd.concat([unified_gmv_gross_payment,unified_netsale_tax_cogs], sort=True)

    # =============================================================================
    # 3. inventoryageing_nearexpiry
    # =============================================================================

    # prerequisite = inventory

    near_expiry = mis.near_expiry(inventory,stores,'breakup')
    near_expiry_unified = mis.near_expiry(inventory_unified,stores,'unified')

    inventory_ageing = mis.inventory_ageing(inventory,stores,'breakup')
    inventory_ageing_unified = mis.inventory_ageing(inventory_unified,stores,'unified')

    logger.info('3. - Inventory ageing, Near expiry ran successfully')

    breakup_master = pd.concat([breakup_master, inventory_ageing, near_expiry], sort=True)
    unified_master = pd.concat([unified_master, inventory_ageing_unified, near_expiry_unified], sort=True)

    # =============================================================================
    # 4. Sales by volume
    # =============================================================================

    # prerequisite = sales

    sale_by_volume = mis.sales_by_volume(sales,stores)
    sale_by_volume_unified = mis.sales_by_volume(sales_unified,stores)

    logger.info('4. - Sales by volume ran successfully')

    breakup_master = pd.concat([breakup_master, sale_by_volume], sort=True)
    unified_master = pd.concat([unified_master, sale_by_volume_unified], sort=True)

    # =============================================================================
    # 5. Gross revenue - Chronic and Acute
    # =============================================================================

    # prerequisite = sales, customer_returns

    gross_rev_chronic_sale_vol, gross_rev_acute_sale_vol = mis.gross_rev_chronic_acute(sales,customer_returns,stores)
    gross_rev_chronic_sale_vol_unified, gross_rev_acute_sale_vol_unified = mis.gross_rev_chronic_acute(sales_unified,customer_returns_unified,stores)

    logger.info('5. - Gross revenue - Chronic and Acute ran successfully')

    breakup_master = pd.concat([breakup_master, gross_rev_chronic_sale_vol, gross_rev_acute_sale_vol], sort=True)
    unified_master = pd.concat([unified_master, gross_rev_chronic_sale_vol_unified, gross_rev_acute_sale_vol_unified], sort=True)

    # =============================================================================
    # 6. Cummulative consumers
    # =============================================================================

    # prerequisite = cumulative_consumers_data

    cummulative_cons = mis.cummulative_cons(cumulative_consumers_data,'breakup')
    cummulative_cons_unified = mis.cummulative_cons(cumulative_consumers_data,'unified')

    logger.info('6. - Cummulative consumers ran successfully')

    breakup_master = pd.concat([breakup_master, cummulative_cons], sort=True)
    unified_master = pd.concat([unified_master, cummulative_cons_unified], sort=True)

    # =============================================================================
    # 7. Total customers (in MIS month)
    # =============================================================================

    # prerequisite = sales

    total_cons_mis_month = mis.total_cons_mis_month(sales,stores)
    total_cons_mis_month_unified = mis.total_cons_mis_month(sales_unified,stores)

    logger.info('7. - Total customers (in MIS month) ran successfully')

    breakup_master = pd.concat([breakup_master, total_cons_mis_month], sort=True)
    unified_master = pd.concat([unified_master, total_cons_mis_month_unified], sort=True)

    # =============================================================================
    # 8. Customer type Category Wise Count
    # =============================================================================

    # prerequisite = sales

    category_wise_customer_type_count = mis.category_wise_customer_type_count(sales,stores)
    category_wise_customer_type_count_unified = mis.category_wise_customer_type_count(sales_unified,stores)

    logger.info('8. - Customer type Category Wise Count ran successfully')

    breakup_master = pd.concat([breakup_master, category_wise_customer_type_count], sort=True)
    unified_master = pd.concat([unified_master, category_wise_customer_type_count_unified], sort=True)

    # =============================================================================
    # 9. New customers
    # =============================================================================

    # prerequisite = sales, cons_initial_bill_date

    new_customers = mis.new_customers(sales,all_cons_initial_bill_date,stores)
    new_customers_unified = mis.new_customers(sales_unified,all_cons_initial_bill_date,stores)

    logger.info('9. - New Customers ran successfully')

    breakup_master = pd.concat([breakup_master, new_customers], sort=True)
    unified_master = pd.concat([unified_master, new_customers_unified], sort=True)

    # =============================================================================
    # 10. Total repeat consumers
    # =============================================================================

    # prerequisite = sales, cons_initial_bill_date

    tot_repeat_consumers = mis.tot_repeat_consumers(sales,all_cons_initial_bill_date,stores)
    tot_repeat_consumers_unified = mis.tot_repeat_consumers(sales_unified,all_cons_initial_bill_date,stores)

    logger.info('10. - total repeat customers ran successfully')

    breakup_master = pd.concat([breakup_master, tot_repeat_consumers], sort=True)
    unified_master = pd.concat([unified_master, tot_repeat_consumers_unified], sort=True)

    # =============================================================================
    # 11. New consumers - value and volume
    # =============================================================================

    # prerequisite = sales, cons_initial_bill_date

    new_cons_vol_qty = mis.new_cons_vol_qty(sales,all_cons_initial_bill_date,stores)
    new_cons_vol_qty_unified = mis.new_cons_vol_qty(sales_unified,all_cons_initial_bill_date,stores)

    logger.info('11. - New consumers - value and volume ran successfully')

    breakup_master = pd.concat([breakup_master, new_cons_vol_qty], sort=True)
    unified_master = pd.concat([unified_master, new_cons_vol_qty_unified], sort=True)

    # =============================================================================
    # 12. Total bills - new and repeat
    # =============================================================================

    # prerequisite = sales, cons_initial_bill_date

    total_bills_new_repeat = mis.total_bills_new_repeat(sales,all_cons_initial_bill_date,stores,choose_year,choose_month)
    total_bills_new_repeat_unified = mis.total_bills_new_repeat(sales_unified,all_cons_initial_bill_date,stores,choose_year,choose_month)

    logger.info('12. - Total bills - new and repeat ran successfully')

    breakup_master = pd.concat([breakup_master, total_bills_new_repeat], sort=True)
    unified_master = pd.concat([unified_master, total_bills_new_repeat_unified], sort=True)

    # =============================================================================
    # 13. Total bills - chronic and acute
    # =============================================================================

    # prerequisite = sales, customer_returns

    total_bills_chronic_acute = mis.total_bills_chronic_acute(sales,customer_returns,stores)
    total_bills_chronic_acute_unified = mis.total_bills_chronic_acute(sales_unified,customer_returns_unified,stores)

    logger.info('13. - Total bills - chronic and acute ran successfully')

    breakup_master = pd.concat([breakup_master, total_bills_chronic_acute], sort=True)
    unified_master = pd.concat([unified_master, total_bills_chronic_acute_unified], sort=True)

    # =============================================================================
    # 14. Bills per consumer - new and repeat
    # =============================================================================

    # prerequisite = sales, all_cons_initial_bill_date

    bills_per_cons_new_repeat = mis.bills_per_cons_new_repeat(sales,all_cons_initial_bill_date,stores,choose_year,choose_month)
    bills_per_cons_new_repeat_unified = mis.bills_per_cons_new_repeat(sales_unified,all_cons_initial_bill_date,stores,choose_year,choose_month)

    logger.info('14. - Bills per consumer - new and repeat ran successfully')

    breakup_master = pd.concat([breakup_master, bills_per_cons_new_repeat], sort=True)
    unified_master = pd.concat([unified_master, bills_per_cons_new_repeat_unified], sort=True)

    # =============================================================================
    # 15. ABV - new, repeat and chronic
    # =============================================================================

    # prerequisite = sales, all_cons_initial_bill_date

    abv_new_repeat_chronic = mis.abv_new_repeat_chronic(sales,all_cons_initial_bill_date,stores,choose_year,choose_month)
    abv_new_repeat_chronic_unified = mis.abv_new_repeat_chronic(sales_unified,all_cons_initial_bill_date,stores,choose_year,choose_month)

    logger.info('15. - ABV - new, repeat and chronic - new and repeat ran successfully')

    breakup_master = pd.concat([breakup_master, abv_new_repeat_chronic], sort=True)
    unified_master = pd.concat([unified_master, abv_new_repeat_chronic_unified], sort=True)

    # =============================================================================
    # 16. Items per consumer
    # =============================================================================

    # prerequisite = sales, all_cons_initial_bill_date

    items_per_cons_new_repeat = mis.items_per_cons_new_repeat(sales,all_cons_initial_bill_date,stores,choose_year,choose_month)
    items_per_cons_new_repeat_unified = mis.items_per_cons_new_repeat(sales_unified,all_cons_initial_bill_date,stores,choose_year,choose_month)

    logger.info('16. - Items per consumer - new and repeat ran successfully')

    breakup_master = pd.concat([breakup_master, items_per_cons_new_repeat], sort=True)
    unified_master = pd.concat([unified_master, items_per_cons_new_repeat_unified], sort=True)

    # =============================================================================
    # 17. Total items sold- new and repeat
    # =============================================================================

    # prerequisite = sales, all_cons_initial_bill_date

    tot_items_sold_new_repeat = mis.tot_items_sold_new_repeat(sales,all_cons_initial_bill_date,stores,choose_year,choose_month)
    tot_items_sold_new_repeat_unified = mis.tot_items_sold_new_repeat(sales_unified,all_cons_initial_bill_date,stores,choose_year,choose_month)

    logger.info('17. - Total items sold - new and repeat ran successfully')

    breakup_master = pd.concat([breakup_master, tot_items_sold_new_repeat], sort=True)
    unified_master = pd.concat([unified_master, tot_items_sold_new_repeat_unified], sort=True)

    # =============================================================================
    # 18. Generic customers
    # =============================================================================

    # prerequisite = sales, all_cons_initial_bill_date

    generic_cons_overall_new = mis.generic_cons_overall_new(sales,all_cons_initial_bill_date,stores)
    generic_cons_overall_new_unified = mis.generic_cons_overall_new(sales_unified,all_cons_initial_bill_date,stores)

    logger.info('18. - Generic customers  ran successfully')

    breakup_master = pd.concat([breakup_master, generic_cons_overall_new], sort=True)
    unified_master = pd.concat([unified_master, generic_cons_overall_new_unified], sort=True)

    # =============================================================================
    # 19. Power consumers - Count
    # =============================================================================

    # prerequisite = sales, all_cons_initial_bill_date

    power_cons_overall_new = mis.power_cons_overall_new(sales,all_cons_initial_bill_date,stores,power_consumer_value)
    power_cons_overall_new_unified = mis.power_cons_overall_new(sales_unified,all_cons_initial_bill_date,stores,power_consumer_value)

    logger.info('19. - Power consumers - Count ran successfully')

    breakup_master = pd.concat([breakup_master, power_cons_overall_new], sort=True)
    unified_master = pd.concat([unified_master, power_cons_overall_new_unified], sort=True)

    # =============================================================================
    # 20. Power consumers - Sales ran successfully
    # =============================================================================

    # prerequisite = sales

    power_consumers_sale = mis.power_consumers_sale(sales,stores,power_consumer_value,'breakup')
    power_consumers_sale_unified = mis.power_consumers_sale(sales_unified,stores,power_consumer_value,'unified')

    logger.info('20. - Power consumers - Sales ran successfully')

    breakup_master = pd.concat([breakup_master, power_consumers_sale], sort=True)
    unified_master = pd.concat([unified_master, power_consumers_sale_unified], sort=True)

    # =============================================================================
    # 21. Power consumer - Bills
    # =============================================================================

    # prerequisite = sales

    power_cons_bills = mis.power_cons_bills(sales,stores,power_consumer_value)
    power_cons_bills_unified = mis.power_cons_bills(sales_unified,stores,power_consumer_value)

    logger.info('21. - Power consumers - Bills ran successfully')

    breakup_master = pd.concat([breakup_master, power_cons_bills], sort=True)
    unified_master = pd.concat([unified_master, power_cons_bills_unified], sort=True)

    # =============================================================================
    # 22. Home delivery
    # =============================================================================

    # prerequisite = sales, customer_returns, home_delivery_data

    home_delivery = mis.home_delivery(sales,customer_returns,home_delivery_data,stores,delivery_bill_ids,'breakup')
    home_delivery_unified = mis.home_delivery(sales_unified,customer_returns_unified,home_delivery_data_unified,stores,delivery_bill_ids,'unified')

    logger.info('22. - Home delivery ran successfully')

    breakup_master = pd.concat([breakup_master, home_delivery], sort=True)
    unified_master = pd.concat([unified_master, home_delivery_unified], sort=True)

    # =============================================================================
    # 23. Purchase from Workcell
    # =============================================================================

    # prerequisite = purchase_from_wc_data

    purchase_from_worckell = mis.purchase_from_worckell(purchase_from_wc_data,stores,'breakup')
    purchase_from_worckell_unified = mis.purchase_from_worckell(purchase_from_wc_data_unified,stores,'unified')

    logger.info('23. - Purchase from Workcell ran successfully')

    breakup_master = pd.concat([breakup_master, purchase_from_worckell], sort=True)
    unified_master = pd.concat([unified_master, purchase_from_worckell_unified], sort=True)

    # =============================================================================
    # 24. COGS for Workcell
    # =============================================================================

    # prerequisite = purchase_from_wc_data

    cogs_for_wc = mis.cogs_for_wc(purchase_from_wc_data,stores,'breakup')
    cogs_for_wc_unified = mis.cogs_for_wc(purchase_from_wc_data_unified,stores,'unified')

    logger.info('24. - COGS from Workcell ran successfully')

    breakup_master = pd.concat([breakup_master, cogs_for_wc], sort=True)
    unified_master = pd.concat([unified_master, cogs_for_wc_unified], sort=True)

    # =============================================================================
    # 25. Return from Zippin
    # =============================================================================

    # prerequisite = zippin_return_data

    return_from_zippin = mis.return_from_zippin(zippin_return_data,'breakup')
    return_from_zippin_unified = mis.return_from_zippin(zippin_return_data_unified,'unified')

    logger.info('25. - Return from Zippin ran successfully')

    breakup_master = pd.concat([breakup_master, return_from_zippin], sort=True)
    unified_master = pd.concat([unified_master, return_from_zippin_unified], sort=True)

    # =============================================================================
    # 26. Return from Workcell
    # =============================================================================

    # prerequisite = workcell_return_data

    return_from_workcell = mis.return_from_workcell(workcell_return_data,'breakup')
    return_from_workcell_unified = mis.return_from_workcell(workcell_return_data_unified,'unified')

    logger.info('26. - Return from Workcell ran successfully')

    breakup_master = pd.concat([breakup_master, return_from_workcell], sort=True)
    unified_master = pd.concat([unified_master, return_from_workcell_unified], sort=True)

    # =============================================================================
    # 27. Total SKUs in stock
    # =============================================================================

    # prerequisite = inventory

    total_sku_instock = mis.total_sku_instock(inventory, 'breakup')
    total_sku_instock_unified = mis.total_sku_instock(inventory_unified, 'unified')

    logger.info('27. - Total SKUs in stock ran successfully')

    breakup_master = pd.concat([breakup_master, total_sku_instock], sort=True)
    unified_master = pd.concat([unified_master, total_sku_instock_unified], sort=True)

    # =============================================================================
    # 28. Chronic Acute quantity
    # =============================================================================

    # prerequisite = inventory

    chronic_acute_qty = mis.chronic_acute_qty(inventory,stores)
    chronic_acute_qty_unified = mis.chronic_acute_qty(inventory_unified ,stores)

    logger.info('28. - Chronic Acute quantity ran successfully')

    breakup_master = pd.concat([breakup_master, chronic_acute_qty], sort=True)
    unified_master = pd.concat([unified_master, chronic_acute_qty_unified], sort=True)

    # =============================================================================
    # 29. Local purchase
    # =============================================================================

    # prerequisite = local_purchase_data, sales

    lp_chronic_acute = mis.lp_chronic_acute(local_purchase_data,sales)
    lp_chronic_acute_unified = mis.lp_chronic_acute(local_purchase_data_unified ,sales_unified)

    logger.info('29. - Local purchase ran successfully')

    breakup_master = pd.concat([breakup_master, lp_chronic_acute], sort=True)
    unified_master = pd.concat([unified_master, lp_chronic_acute_unified], sort=True)

    # =============================================================================
    # 30. Repeat consumer sales
    # =============================================================================

    # prerequisite = sales, all_cons_initial_bill_date

    repeat_consumer_chronic_acute = mis.repeat_consumer_chronic_acute(sales,all_cons_initial_bill_date,stores,choose_year,choose_month)
    repeat_consumer_chronic_acute_unified = mis.repeat_consumer_chronic_acute(sales_unified,all_cons_initial_bill_date,stores,choose_year,choose_month)

    logger.info('30. - Repeat consumer sales ran successfully')

    breakup_master = pd.concat([breakup_master, repeat_consumer_chronic_acute], sort=True)
    unified_master = pd.concat([unified_master, repeat_consumer_chronic_acute_unified], sort=True)

    # =============================================================================
    # 31. Inventory 6 to 12 months
    # =============================================================================

    # prerequisite = inventory

    inventory_6to12months = mis.inventory_6to12months(inventory,stores,'breakup')
    inventory_6to12months_unified = mis.inventory_6to12months(inventory_unified,stores,'unified')

    logger.info('31. - Inventory 6 to 12 months ran successfully')

    breakup_master = pd.concat([breakup_master, inventory_6to12months], sort=True)
    unified_master = pd.concat([unified_master, inventory_6to12months_unified], sort=True)

    # =============================================================================
    # 32. Zippin P &L COGS
    # =============================================================================

    # prerequisite = sales, customer_returns

    zippin_pl_cogs = mis.zippin_pl_cogs(sales,customer_returns,stores)
    zippin_pl_cogs_unified = mis.zippin_pl_cogs(sales_unified,customer_returns_unified,stores)

    logger.info('32. - Zippin P &L COGS ran successfully')

    breakup_master = pd.concat([breakup_master, zippin_pl_cogs], sort=True)
    unified_master = pd.concat([unified_master, zippin_pl_cogs_unified], sort=True)

    # =============================================================================
    # 33. Repeat consumer other definition
    # =============================================================================

    # prerequisite = None

    last_day_of_prev_month = date.today().replace(day=1) - timedelta(days=1)

    six_months_first_date = (date.today() + relativedelta(months=-6)).replace(day=1)

    last_day_of_prev_month = datetime.datetime.combine(last_day_of_prev_month, datetime.time(23,59,59)).strftime('%Y-%m-%d %H:%M:%S')

    six_months_first_date = datetime.datetime.combine(six_months_first_date, datetime.time(0,0,0)).strftime('%Y-%m-%d %H:%M:%S')

    # last_day_of_prev_month = '2021-02-28 23:59:59'
    # six_months_first_date = '2020-09-01 00:00:00'

    sales_data_for_repeat_customer = mis.sales_data_for_repeat_customer(six_months_first_date,last_day_of_prev_month)

    logger.info('fetched data for sales of last 6 months, for repeat customer other definition')

    repeat_cons_other_def_curr_month = mis.repeat_cons_other_def_curr_month(sales_data_for_repeat_customer,stores,choose_month)

    three_month_last_date = ((date.today() +relativedelta(months=-3)).replace(day=1) -timedelta(days=1))

    five_months_first_date = (three_month_last_date + relativedelta(months=-5)).replace(day=1)

    three_month_last_date = datetime.datetime.combine(three_month_last_date, datetime.time(23,59,59)).strftime('%Y-%m-%d %H:%M:%S')

    five_months_first_date = datetime.datetime.combine(five_months_first_date, datetime.time(0,0,0)).strftime('%Y-%m-%d %H:%M:%S')

    # three_month_last_date = '2020-11-30 23:59:59'
    # five_months_first_date = '2020-06-01 00:00:00'

    sales_data_for_repeat_customer2 = mis.sales_data_for_repeat_customer(five_months_first_date,three_month_last_date)
    logger.info('fetched data for sales of last n-3 to n-8 months, for repeat customer other definition')

    repeat_cons_other_def_past3_month = mis.repeat_cons_other_def_past3_month(sales_data_for_repeat_customer2,stores,choose_month)

    repeat_cons_other_def = pd.concat([repeat_cons_other_def_curr_month,
                                       repeat_cons_other_def_past3_month])

    logger.info('33. - Repeat consumer other definition  ran successfully')

    breakup_master = pd.concat([breakup_master, repeat_cons_other_def], sort=True)
    unified_master = pd.concat([unified_master, repeat_cons_other_def], sort=True)

    # =============================================================================
    # 34.  Drug count by type
    # =============================================================================

    # prerequisite = inventory

    composition_count = mis.comp_count(inventory,'breakup')
    composition_count_unified = mis.comp_count(inventory_unified,'unified')

    logger.info('34. - Drug count by type ran successfully')

    breakup_master = pd.concat([breakup_master, composition_count], sort=True)
    unified_master = pd.concat([unified_master, composition_count_unified], sort=True)

    # =============================================================================
    # 35.  Generic composition type
    # =============================================================================

    # prerequisite = None

    generic_composition_count = mis.generic_composition_count()
    generic_composition_count_unified = generic_composition_count.copy(deep = True)

    logger.info('35. - Generic composition type ran successfully')

    breakup_master = pd.concat([breakup_master, generic_composition_count], sort=True)
    unified_master = pd.concat([unified_master, generic_composition_count_unified], sort=True)

    # =============================================================================
    # 36.  Ethical margin
    # =============================================================================

    # prerequisite = None

    ethical_margin = mis.ethical_margin()
    ethical_margin_unified = ethical_margin.copy(deep = True)

    logger.info('36. - Ethical margin ran successfully')

    breakup_master = pd.concat([breakup_master, ethical_margin], sort=True)
    unified_master = pd.concat([unified_master, ethical_margin_unified], sort=True)

    # =============================================================================
    # 37.  Chronic customers buying generics
    # =============================================================================

    # prerequisite = Sales

    chronic_generic_count = mis.chronic_generic_count(sales)
    chronic_generic_count_unified = mis.chronic_generic_count(sales_unified)

    logger.info('37. - Chronic customers buying generics ran successfully')

    breakup_master = pd.concat([breakup_master, chronic_generic_count], sort=True)
    unified_master = pd.concat([unified_master, chronic_generic_count_unified], sort=True)

    cols_to_move = ['tag_flag', 'type1', 'category', 'age_bracket_',
                    'payment', 'count', 'margin']
    breakup_master = breakup_master[ cols_to_move + [col for col in breakup_master.columns
                                             if col not in cols_to_move]]

    del unified_master['order_source']

    unified_master = unified_master[ cols_to_move + [col for col in unified_master.columns
                                             if col not in cols_to_move]]

    # breakup_master.to_csv(r'D:\MIS Automation\data validation unified\37_breakup.csv')
    # unified_master.to_csv(r'D:\MIS Automation\data validation unified\37_unified.csv')

    logger.info('Successfully ran MIS breakup & unified snippet, Now compiling other files')

    # =============================================================================
    # fetching other files that we sent with MIS
    # =============================================================================

    other_files_ethical_margin = mis.other_files_ethical_margin()
    logger.info('fetched other_files_ethical_margin')

    other_files_distributor_margin = mis.other_files_distributor_margin()
    logger.info('fetched other_files_distributor_margin')

    other_files_inventory_at_dc_near_expiry = mis.other_files_inventory_at_dc_near_expiry()
    logger.info('fetched other_files_inventory_at_dc_near_expiry')

    goodaid_gross_return = mis.goodaid_gross_return()
    logger.info("fetched goodaid_gross_return")

    goodaid_zippin_inventory = mis.goodaid_zippin_inventory()
    logger.info("fetched goodaid_zippin_inventory")

    goodaid_dc_inventory = mis.goodaid_dc_inventory()
    logger.info("fetched goodaid_dc_inventory")

    goodaid_wh_inventory = mis.goodaid_wh_inventory()
    logger.info("fetched goodaid_wh_inventory")

    store_info = mis.store_info()
    logger.info('fetched store info')

    status = True

    logger.info('MIS - all data fetch complete')

except Exception as error:
    logger.info('MIS - MIS breakup & unified snippet run failed, with error - {}'.format(error))
    status = False

if status==True:
    status_final = 'Success'
else:
    status_final = 'Failed'

email = Email()

if status == True:
    breakup_uri = s3.save_df_to_s3(df=breakup_master, file_name='final_breakup.csv')

    unified_uri = s3.save_df_to_s3(df=unified_master, file_name='final_unified.csv')

    other_files_ethical_margin_uri = s3.save_df_to_s3(df=other_files_ethical_margin, file_name='ethical_margin.csv')

    other_files_inventory_at_dc_near_expiry_uri = s3.save_df_to_s3(df=other_files_inventory_at_dc_near_expiry, file_name='inventory_at_dc_near_expiry.csv')

    other_files_distributor_margin_uri = s3.save_df_to_s3(df=other_files_distributor_margin, file_name='distributor_margin.csv')

    goodaid_gross_return_uri = s3.save_df_to_s3(df=goodaid_gross_return, file_name='goodaid_gross_return.csv')

    goodaid_wh_inventory_uri = s3.save_df_to_s3(df=goodaid_wh_inventory, file_name='goodaid_wh_inventory.csv')

    goodaid_zippin_inventory_uri = s3.save_df_to_s3(df=goodaid_zippin_inventory, file_name='goodaid_zippin_inventory.csv')

    goodaid_dc_inventory_uri = s3.save_df_to_s3(df=goodaid_dc_inventory, file_name='goodaid_dc_inventory.csv')

    store_info_uri = s3.save_df_to_s3(df=store_info, file_name='store_info.csv')

    email.send_email_file(subject='MIS- {}/{}'.format(choose_month,choose_year),
        mail_body= f"Dear MIS Team,\n"
                   f"\n"
                   f"Please find attached MIS for year - {choose_year}, month - {choose_month}\n"
                   f"Please review it at earliest\n"
                   f"\n"
                   f"Regards,\n"
                   f"Data Team\n",
        to_emails=mis_email_to, file_uris=[breakup_uri,unified_uri,other_files_ethical_margin_uri,other_files_inventory_at_dc_near_expiry_uri,other_files_distributor_margin_uri,goodaid_gross_return_uri,goodaid_wh_inventory_uri,goodaid_zippin_inventory_uri, goodaid_dc_inventory_uri,store_info_uri])
else:
    email.send_email_file(subject='{}-{}-MIS-{}-{}'.format(env,status_final,choose_year,choose_month),
        mail_body=f"MIS job failed, Please review it\n",
        to_emails=email_to, file_uris=[])


rs_db.close_connection()
rs_db_write.close_connection()