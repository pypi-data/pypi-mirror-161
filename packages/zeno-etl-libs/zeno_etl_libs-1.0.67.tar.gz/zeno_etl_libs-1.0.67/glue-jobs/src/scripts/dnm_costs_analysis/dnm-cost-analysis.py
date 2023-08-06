# Owner - saurav.maskar@zeno.health
# Purpose - Compare cost of different Distribution Network Models

import os
import sys

sys.path.append('../../../..')

# import json
import argparse
import pandas as pd
import numpy as np
import datetime
import math
# import traceback
# from datetime import date, timedelta
# from dateutil.relativedelta import relativedelta

from zeno_etl_libs.helper.aws.s3 import S3
from zeno_etl_libs.helper.email.email import Email
from zeno_etl_libs.db.db import DB
from zeno_etl_libs.logger import get_logger
from zeno_etl_libs.helper import helper
from dateutil.tz import gettz

parser = argparse.ArgumentParser(description="This is ETL script.")
parser.add_argument('-e', '--env', default="dev", type=str, required=False)
parser.add_argument('-et', '--email_to', default="saurav.maskar@zeno.health", type=str, required=False)
parser.add_argument('-n', '--number_of_stores', default="10", type=str, required=False)
parser.add_argument('-cn', '--city_name', default="Nagpur", type=str, required=False)
parser.add_argument('-cd', '--city_distance_from_mumbai_in_km', default="836", type=str, required=False)
parser.add_argument('-inp', '--increase_in_purchasing_power_compared_to_mumbai', default="86.99", type=str, required=False)
args, unknown = parser.parse_known_args()
env = args.env
email_to = args.email_to
number_of_stores = args.number_of_stores
city_name = args.city_name
city_distance_from_mumbai_in_km = args.city_distance_from_mumbai_in_km
increase_in_purchasing_power_compared_to_mumbai = args.increase_in_purchasing_power_compared_to_mumbai

number_of_stores = int(number_of_stores)
city_distance_from_mumbai_in_km = float(city_distance_from_mumbai_in_km)
increase_in_purchasing_power_compared_to_mumbai = float(increase_in_purchasing_power_compared_to_mumbai)

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
logger.info(f"email_to: {email_to}")
logger.info(f"number_of_stores: {number_of_stores}")
logger.info(f"city_name: {city_name}")
logger.info(f"city_distance_from_mumbai_in_km: {city_distance_from_mumbai_in_km}")
logger.info(f"increase_in_purchasing_power_compared_to_mumbai: {increase_in_purchasing_power_compared_to_mumbai}")

# date parameter
logger.info("code started at {}".format(datetime.datetime.now(tz=gettz('Asia/Kolkata')).strftime(
    '%Y-%m-%d %H:%M:%S')))

city_cost_parity = 1/((increase_in_purchasing_power_compared_to_mumbai+100)/100)

status = False

try:
    # assumptions = pd.read_csv(r'D:\Distribution Network Model\assumptions.csv')
    assumptions = pd.read_csv(s3.download_file_from_s3(file_name="dnm-cost-input/dnm-assumption-input.csv"))
    # assumptions.set_index('variable',inplace=True)

    # Calculating last 30 days sales figures
    store_sales_query = f"""
        select
            s3."s-type" as "variable",
            round(avg(s3.value), 0) as values,
            round(avg(s3.quantity), 0) as quantity,
            round(avg(s3."purchase-rate"), 0) as "purchase-rate",
            -- round(avg(s3.ptr), 0) as ptr,
            'type wise last 30 days sales per store avg' as "description"
        from
            (
            select
                s2."store-id",
                s2."s-type",
                sum(s2.value) as "value" ,
                sum(s2.quantity) as "quantity",
                sum(s2."purchase-rate") as "purchase-rate",
                sum(s2.ptr) as ptr
            from
                (
                select
                    s."store-id" ,
                    round(sum(s.quantity * s.rate), 0) as "value",
                    sum(quantity) as quantity,
                    sum(s."purchase-rate"*s.quantity) as "purchase-rate" ,
                    sum(s.ptr*s.quantity) as "ptr",
                    case
                        when s.company = 'GOODAID' then 'goodaid'
                        when s."type" = 'ethical' then 'ethical'
                        when s."type" = 'generic' then 'generic'
                        else 'others'
                    end as "s-type"
                from
                    "prod2-generico"."prod2-generico".sales s
                where
                    date(s."created-at") >= current_date -31
                    and date(s."created-at") <= current_date - 1
                    and date(s."store-opened-at") <= current_date - 60
                    and date(s."first-bill-date") <= current_date - 60
                group by
                    s."store-id",
                    s."type" ,
                    s.company)s2
            group by
                s2."store-id",
                s2."s-type")s3
        group by
            s3."s-type"
    """
    store_sales = rs_db.get_df(store_sales_query)
    logger.info('fetched store_sales')

    return_ratio_query = f"""
         select
            avg(combine.sold_quantity) as "avg_sold_qty_per_store",
            avg(combine.returned_quantity) as "avg_return_qty_per_store"
        from
            ((
            select
                s."store-id" ,
                sum(quantity) as sold_quantity
            from
                "prod2-generico"."prod2-generico".sales s
            where
                date(s."created-at") >= current_date -31
                and date(s."created-at") <= current_date - 1
                and date(s."store-opened-at") <= current_date - 60
                and date(s."first-bill-date") <= current_date - 60
            group by
                s."store-id")s2
        left join (
            select
                    rtd."store-id" ,
                    sum(ri."returned-quantity") as returned_quantity
            from
                    "prod2-generico"."prod2-generico"."return-items-1" ri
            left join "prod2-generico"."prod2-generico"."returns-to-dc-1" rtd 
                on
                ri."return-id" = rtd.id
            left join "prod2-generico"."prod2-generico".stores s2 
                on
                s2.id = rtd."store-id"
            where
                    date(rtd."created-at") >= current_date -31
                    and date(rtd."created-at") <= current_date - 1
                        and date(s2."opened-at") <= current_date - 60
                    group by
                        rtd."store-id"
               )ret
            on
            ret."store-id" = s2."store-id")combine
    """
    return_ratio = rs_db.get_df(return_ratio_query)
    logger.info('fetched return_ratio')

    avg_store_sale = store_sales['values'].sum()
    avg_quantity = store_sales['quantity'].sum()
    avg_cogs = store_sales['purchase-rate'].sum()
    logger.info(f'average sale of current stores  - {avg_store_sale}')
    logger.info(f'quantity per store as per current stores  - {avg_quantity}')
    logger.info(f'cogs per store as per current stores  - {avg_cogs}')

    # fofo_store_factor = float(assumptions.where(assumptions['variable'] == 'fofo_store_sales_as_percentage_of_total',axis=0).dropna()['value'])
    #
    # avg_fofo_store_sale = float(avg_store_sale)*float(fofo_store_factor)


    total_model = [1,2,3,4]
    summary_final = pd.DataFrame()

    # total_model = [4]

    for model in total_model:
        if model== 1:
            model_name =  'wh_to_store_direct'
        elif model==2:
            model_name = 'wh_to_store_via_dc'
        elif model==3:
            model_name = 'wh_to_store_via_dc_more_local_vendors'
        elif model == 4:
            model_name = 'wh_to_store_via_dc_plus_dc_storing_items'

        result = pd.DataFrame(columns=['variable','values'])
        i = 0

        result.loc[i,'variable'] = 'Model Name'
        result.loc[i,'values'] = model_name
        result.loc[i,'description'] = 'Model'
        i = i+1

        result.loc[i,'variable'] = 'Number of Stores'
        result.loc[i,'values'] = number_of_stores
        result.loc[i,'description'] = 'input'
        i = i+1

        result.loc[i,'variable'] = 'city'
        result.loc[i,'values'] = city_name
        result.loc[i,'description'] = 'input'
        i = i+1

        result.loc[i,'variable'] = 'distance from Mumbai in KM'
        result.loc[i,'values'] = city_distance_from_mumbai_in_km
        result.loc[i,'description'] = 'input'
        i = i+1

        result.loc[i,'variable'] = 'increase in purcahsing power in the city compared to mumbai'
        result.loc[i,'values'] = increase_in_purchasing_power_compared_to_mumbai
        result.loc[i,'description'] = 'input'
        i = i+1

        result.loc[i,'variable'] = 'city cost parity'
        result.loc[i,'values'] = round(city_cost_parity,2)
        result.loc[i,'description'] = 'calculation based on purchasing power'
        result.loc[i,'calculation'] = '1/((increase_in_purchasing_power_compared_to_mumbai+100)/100)'
        i = i+1

        result = pd.concat([result,store_sales[['variable', 'values', 'quantity', 'description']]],sort=True)
        i = i + 4

        result.reset_index(inplace=True,drop=True)

        result.loc[i,'variable'] = 'revenue'
        result.loc[i,'values'] = avg_store_sale*number_of_stores
        result.loc[i,'description'] = f'monthly revenue for {number_of_stores} stores'
        i = i+1

        result.loc[i,'variable'] = 'cogs'
        result.loc[i,'values'] = avg_cogs*number_of_stores
        result.loc[i,'description'] = f'monthly cogs for {number_of_stores} stores'
        i = i+1

        result.loc[i,'variable'] = 'quantity'
        result.loc[i,'values'] = avg_quantity*number_of_stores
        result.loc[i,'description'] = f'monthly quantity sold in {number_of_stores} stores'
        i = i+1

        if model==1:
            distribution = {'wh_ethical': 1,
            'wh_goodaid':1,
            'wh_generic':1,
            'wh_others':1}

        elif model==2:
            distribution = {'wh_ethical': 0.7,
            'wh_goodaid':1,
            'wh_generic':0.9,
            'wh_others':0.6}

        elif model==3:
            distribution = {'wh_ethical': 0.4,
            'wh_goodaid':1,
            'wh_generic':0.7,
            'wh_others':0.3}

        elif model==4:
            distribution = {'wh_ethical': 0.4,
            'wh_goodaid':1,
            'wh_generic':0.7,
            'wh_others':0.3}

        result.loc[i,'variable'] = 'wh others'
        result.loc[i,'values'] = distribution['wh_others']
        result.loc[i,'description'] = f'value - % Quantity Transfer through WH for others per day for {number_of_stores} stores'
        result.loc[i,'quantity'] =(distribution['wh_others']*float(result.where(result['variable'] == 'others',axis=0)['quantity'].dropna())/30)*number_of_stores
        result.loc[i, 'calculation'] = "wh_share_for_wh_others*(others_flow_per_store_per_month/30)*number_of_stores"
        i = i+1

        result.loc[i,'variable'] = 'wh ethical'
        result.loc[i,'values'] = distribution['wh_ethical']
        result.loc[i,'description'] = f'value - % Quantity Transfer through WH for Ethical,quantity transfer per day for {number_of_stores} stores'
        result.loc[i,'quantity'] =(distribution['wh_ethical']*float(result.where(result['variable'] == 'ethical',axis=0)['quantity'].dropna())/30)*number_of_stores
        result.loc[i,'calculation'] = "wh_share_for_wh_ethical*(ethical_flow_per_store_per_month/30)*number_of_stores"
        i = i+1

        result.loc[i,'variable'] = 'wh goodaid'
        result.loc[i,'values'] = distribution['wh_goodaid']
        result.loc[i,'description'] = f'value - % Quantity Transfer through WH for goodaid per day for {number_of_stores} stores'
        result.loc[i,'quantity'] =(distribution['wh_goodaid']*float(result.where(result['variable'] == 'goodaid',axis=0)['quantity'].dropna())/30)*number_of_stores
        result.loc[i, 'calculation'] = "wh_share_for_wh_goodaid*(goodaid_flow_per_store_per_month/30)*number_of_stores"
        i = i+1

        result.loc[i,'variable'] = 'wh generic'
        result.loc[i,'values'] = distribution['wh_generic']
        result.loc[i,'description'] = f'value - % Quantity Transfer through WH for generic per day for {number_of_stores} stores'
        result.loc[i,'quantity'] =(distribution['wh_generic']*float(result.where(result['variable'] == 'generic',axis=0)['quantity'].dropna())/30)*number_of_stores
        result.loc[i, 'calculation'] = "wh_share_for_wh_generic*(generic_flow_per_store_per_month/30)*number_of_stores"
        i = i+1

        wh_throghput = result.where(result['variable'].isin(['wh ethical', 'wh generic', 'wh goodaid', 'wh others']),axis=0)['quantity'].dropna().sum()
        result.loc[i,'variable'] = 'wh throghput'
        result.loc[i,'quantity'] = wh_throghput
        result.loc[i,'description'] = f'quantity flow through wh on daily basis for {number_of_stores} stores'
        result.loc[i, 'calculation'] = "sum of all types flow"
        i = i+1

        wh_staff = assumptions[assumptions['type']=='wh_staff'][['variable', 'throghput', 'Salary_per_person', 'description']]
        conditions = [
            wh_staff['description'] == 'throughput-qty_per_person_per_day',
            (wh_staff['description'] == 'per city')]
        choices = [wh_throghput/wh_staff['throghput'], wh_staff['throghput']]
        wh_staff['quantity'] = np.select(conditions, choices)
        wh_staff['values'] = wh_staff['quantity']*wh_staff['Salary_per_person']
        wh_staff['type'] = 'wh_variable'
        result = pd.concat([result,wh_staff],sort=True)
        i = i + 10

        result.reset_index(inplace=True,drop=True)

        wh_variable = assumptions[assumptions['type']=='wh_variable'][['variable', 'throghput', 'Salary_per_person', 'description']]
        wh_variable.reset_index(inplace=True,drop=True)
        wh_variable.loc[0,'values'] = wh_throghput*float(wh_variable.where(wh_variable['variable'] == 'wh_stationary',axis=0)['throghput'].dropna())
        wh_variable.loc[1,'values'] = wh_staff['quantity'].sum()*float(wh_variable.where(wh_variable['variable'] == 'wh_staff_welfare',axis=0)['throghput'].dropna())
        wh_variable.loc[2,'values'] = float(avg_cogs)*float(number_of_stores)*float(wh_variable.where(wh_variable['variable'] == 'wh_shrinkages',axis=0)['throghput'].dropna())
        wh_variable['type'] = 'wh_variable'
        result = pd.concat([result,wh_variable],sort=True)
        i = i + 3
        result.reset_index(inplace=True,drop=True)

        wh_fixed = assumptions[assumptions['type']=='wh_fixed'][['variable', 'value' , 'Salary_per_person', 'description']]

        wh_fixed.rename(columns = { 'value': 'throghput'}, inplace=True)
        wh_fixed['description'] = 'throghput - total cost per month, value = marginal increase'
        wh_fixed['values'] = 0
        wh_fixed['type'] = 'wh_fixed'
        result = pd.concat([result,wh_fixed],sort=True)
        i = i + 5
        result.reset_index(inplace=True,drop=True)

        result.loc[i,'variable'] = 'dc others'
        result.loc[i,'values'] = 1 - distribution['wh_others']
        result.loc[i,'description'] = f'value - % Quantity Transfer directly through dc for others'
        result.loc[i,'quantity'] =((1- distribution['wh_others'])*float(result.where(result['variable'] == 'others',axis=0)['quantity'].dropna())/30)*number_of_stores
        result.loc[i, 'calculation'] = "dc_share_for_dc_others*(others_flow_per_store_per_month/30)*number_of_stores"
        i = i+1

        result.loc[i,'variable'] = 'dc ethical'
        result.loc[i,'values'] = 1-distribution['wh_ethical']
        result.loc[i,'description'] = f'value - % Quantity Transfer directly through dc for Ethical'
        result.loc[i,'quantity'] =((1 - distribution['wh_ethical'])*float(result.where(result['variable'] == 'ethical',axis=0)['quantity'].dropna())/30)*number_of_stores
        result.loc[i, 'calculation'] = "dc_share_for_dc_ethical*(ethical_flow_per_store_per_month/30)*number_of_stores"
        i = i+1

        result.loc[i,'variable'] = 'dc goodaid'
        result.loc[i,'values'] = 1 - distribution['wh_goodaid']
        result.loc[i,'description'] = f'value - % Quantity Transfer directly through dc for goodaid'
        result.loc[i,'quantity'] =((1 - distribution['wh_goodaid'])*float(result.where(result['variable'] == 'goodaid',axis=0)['quantity'].dropna())/30)*number_of_stores
        result.loc[i, 'calculation'] = "dc_share_for_dc_goodaid*(goodaid_flow_per_store_per_month/30)*number_of_stores"
        i = i+1

        result.loc[i,'variable'] = 'dc generic'
        result.loc[i,'values'] = 1 - distribution['wh_generic']
        result.loc[i,'description'] = f'value - % Quantity Transfer directly through dc for generic'
        result.loc[i,'quantity'] =((1-distribution['wh_generic'])*float(result.where(result['variable'] == 'generic',axis=0)['quantity'].dropna())/30)*number_of_stores
        result.loc[i, 'calculation'] = "dc_share_for_dc_generic*(generic_flow_per_store_per_month/30)*number_of_stores"
        i = i+1

        dc_throghput = result.where(result['variable'].isin(['dc ethical', 'dc generic', 'dc goodaid', 'dc others']),axis=0)['quantity'].dropna().sum()
        result.loc[i,'variable'] = 'dc throghput'
        result.loc[i,'quantity'] = dc_throghput
        result.loc[i,'description'] = f'quantity flow through dc on daily basis'
        i = i+1

        if model ==4:
            result.loc[i,'variable'] = 'dc holding inventory flag'
            result.loc[i,'values'] = 1
            result.loc[i,'description'] = 'if 1 then yes, if 0 then no'
            result.loc[i,'calculation'] = 'model dependent'
            i = i+1
        else:
            result.loc[i,'variable'] = 'dc holding inventory flag'
            result.loc[i,'values'] = 0
            result.loc[i,'description'] = 'if 1 then yes, if 0 then no'
            result.loc[i,'calculation'] = 'model dependent'
            i = i+1

        if model ==4:
            dc_holding_inventory_for_n_days = float(assumptions.where(assumptions['variable'] == 'inventory_holding_for_n_days',axis=0)['value'].dropna())
        else:
            dc_holding_inventory_for_n_days = 0

        result.loc[i, 'variable'] = 'dc holding inventory for n days'
        result.loc[i, 'values'] = dc_holding_inventory_for_n_days
        result.loc[i, 'description'] = 'value - number of days, Input'
        result.loc[i, 'calculation'] = 'input'
        i = i + 1

        result.loc[i,'variable'] = 'cogs per quantity'
        result.loc[i,'values'] = avg_cogs/avg_quantity
        result.loc[i,'description'] = f'avg cogs per quantity'
        result.loc[i, 'calculation'] = 'avg_cogs/avg_quantity'
        i = i+1

        result.loc[i, 'variable'] = 'dc inventory holding'
        result.loc[i, 'quantity'] = dc_holding_inventory_for_n_days*dc_throghput
        dc_holding_value = float(avg_cogs/avg_quantity)*dc_holding_inventory_for_n_days*dc_throghput
        result.loc[i, 'values'] = dc_holding_value
        result.loc[i, 'description'] = 'inventory holding per day'
        result.loc[i, 'calculation'] = 'cogs per quantity*dc_holding_inventory_for_n_days*dc_throghput'
        i = i + 1

        result.loc[i, 'variable'] = 'inventory carrying cost'
        result.loc[i, 'Salary_per_person'] = 12
        result.loc[i, 'values'] = dc_holding_value*12/1200
        result.loc[i, 'description'] = 'value - rs per month, Salary_per_person- interest per annum'
        result.loc[i, 'calculation'] = 'dc_holding_value * interest per annum/1200'
        result.loc[i,'type'] = 'dc_variable'
        i = i + 1

        def percentage_increase_in_dc_fixed_cost_due_to_inv_holding(quantity):
            return (quantity/200000)*100

        result.loc[i, 'variable'] = 'dc_fixed_cost_increase_inv_holding'
        result.loc[i, 'values'] = percentage_increase_in_dc_fixed_cost_due_to_inv_holding(dc_holding_inventory_for_n_days*dc_throghput)
        result.loc[i, 'description'] = 'percentage increase_in_dc_fixed_cost_due_to_inv_holding'
        result.loc[i, 'calculation'] = 'Dc holding quantity/200000'
        i = i + 1

        dc_staff = assumptions[assumptions['type']=='dc_staff'][['variable', 'Salary_per_person', 'description', 'throghput']]

        conditions = [
            dc_staff['variable'].isin(['dc_barcoder']),
            dc_staff['variable'].isin(['dc_purchaser','dc_inward_team']),
            dc_staff['variable'].isin(['dc_returns_team']),
            dc_staff['variable'].isin(['dc_manager','dc_inventory_manager'])]
        choices = [(dc_throghput/dc_staff['throghput']),
                   ((dc_throghput/4)/dc_staff['throghput']),
                   ((dc_throghput/10)/dc_staff['throghput']),
                   dc_staff['throghput']]
        dc_staff['quantity'] = np.select(conditions, choices)
        conditions = [dc_staff['quantity']<=1,dc_staff['quantity']>1]
        choices = [1,dc_staff['quantity'].apply(np.round)]
        dc_staff['quantity'] = dc_staff['quantity'].apply(np.ceil)
        dc_staff['values'] = dc_staff['quantity']*dc_staff['Salary_per_person']
        dc_staff['type'] = 'dc_variable'
        dc_staff.reset_index(inplace=True,drop = True)
        dc_employees = dc_staff['quantity'].sum()
        dc_staff.loc[5,'quantity'] = dc_employees
        dc_staff.loc[5,'values'] = dc_employees*dc_staff.loc[5,'throghput']*30

        if dc_throghput==0:
            dc_staff['values']=0
            dc_staff['quantity']=0

        result = pd.concat([result,dc_staff],sort=True)
        i = i + 7
        result.reset_index(inplace=True,drop=True)

        dc_fixed = assumptions[assumptions['type']=='dc_fixed'][['variable', 'value' , 'Salary_per_person', 'description']]

        dc_fixed.rename(columns = { 'value': 'throghput'}, inplace=True)
        dc_fixed['description'] = f'value = final cost in {city_name},throghput - total cost per month in mumbai,Salary_per_person - according to cities cost parity,quantity - percentage_impact of inventory holding'
        dc_fixed['Salary_per_person'] = dc_fixed['throghput']*city_cost_parity
        dc_fixed['quantity'] = percentage_increase_in_dc_fixed_cost_due_to_inv_holding(dc_holding_inventory_for_n_days*dc_throghput)
        dc_fixed['values'] = dc_fixed['throghput']*city_cost_parity*(100 +percentage_increase_in_dc_fixed_cost_due_to_inv_holding(dc_holding_inventory_for_n_days*dc_throghput) )/100
        dc_fixed['type'] = 'dc_fixed'

        if dc_throghput==0:
            dc_fixed['values']=0
            dc_fixed['quantity']=0

        result = pd.concat([result,dc_fixed],sort=True)
        i = i + 7
        result.reset_index(inplace=True,drop=True)

        if dc_throghput <= 0:
            number_of_biker = number_of_stores / 5
        else:
            number_of_biker = number_of_stores / 10

        result.loc[i, 'variable'] = f'delivery assosiate required for {city_name}'
        result.loc[i, 'quantity'] = number_of_biker
        result.loc[i, 'description'] = 'for intercity transport'
        result.loc[i, 'Salary_per_person'] = 15000
        result.loc[i, 'values'] = number_of_biker * 15000
        result.loc[i, 'type'] = 'logistics'
        result.loc[i, 'calculation'] = 'if dc available 1 biker per 10 stores, if no dc 1 biker per 5 stores'
        i = i + 1

        result.loc[i,'variable'] = 'kg_per_quantity'
        result.loc[i,'values'] = float(assumptions.where(assumptions['variable'] == 'kg_per_quantity',axis=0)['value'].dropna())
        result.loc[i,'description'] = 'input'
        i = i+1

        result.loc[i,'variable'] = 'flow_through_wh_in_kg'
        result.loc[i,'values'] = wh_throghput*float(assumptions.where(assumptions['variable'] == 'kg_per_quantity',axis=0)['value'].dropna())
        result.loc[i,'description'] = 'on daily basis'
        i = i+1

        def cost_of_transport(km):
            if km<=100:
                return 30
            elif km<=200:
                return 30
            elif km<=300:
                return 30
            elif km <= 400:
                return 30
            elif km <= 500:
                return 35
            elif km <= 1000:
                return 40
            elif km<= 2000:
                return 45
            else:
                return 50

        result.loc[i,'variable'] = 'cost per kg'
        result.loc[i,'values'] = cost_of_transport(city_distance_from_mumbai_in_km)
        result.loc[i,'description'] = 'cost assumed based on distance'
        i = i+1

        if dc_throghput<= 0:
            result.loc[i,'variable'] = 'extra cost based on delivery convinience'
            result.loc[i,'values'] =2
            result.loc[i,'description'] = 'If DC available single localtion of delivery otherwise multiple'
            i = i+1
            cost_of_transport_ = cost_of_transport(city_distance_from_mumbai_in_km)+2
        else:
            result.loc[i,'variable'] = 'extra cost based on delivery convinience'
            result.loc[i,'values'] =0
            result.loc[i,'description'] = 'If DC available single localtion of delivery otherwise multiple'
            i = i+1
            cost_of_transport_ = cost_of_transport(city_distance_from_mumbai_in_km) + 0

        result.loc[i,'variable'] = 'cost of transport till courier destination'
        result.loc[i,'values'] = wh_throghput*float(assumptions.where(assumptions['variable'] == 'kg_per_quantity',axis=0)['value'].dropna())*cost_of_transport_*30
        result.loc[i,'description'] = 'on monthly basis in Rs'
        result.loc[i,'type'] = 'logistics_1'
        i = i+1

        result.loc[i,'variable'] = 'sold vs returned quatity'
        result.loc[i,'quantity'] = return_ratio.loc[0,'avg_sold_qty_per_store']
        result.loc[i,'throghput'] = return_ratio.loc[0,'avg_return_qty_per_store']
        return_ratio_value = return_ratio.loc[0,'avg_return_qty_per_store']/return_ratio.loc[0,'avg_sold_qty_per_store']
        result.loc[i,'values'] = return_ratio_value
        result.loc[i,'description'] = 'quantity - avg_sold_qty_per_store, throughput - avg_return_qty_per_store '
        i = i+1

        result.loc[i,'variable'] = 'wh return quantity'
        result.loc[i,'quantity'] = wh_throghput*return_ratio_value
        result.loc[i,'description'] = 'quantity received from wh will be returned to wh'
        result.loc[i,'calculation'] = 'wh_throghput*return_ratio_value'
        i = i+1

        result.loc[i,'variable'] = 'flow_through_store_to_wh_in_kg'
        result.loc[i,'values'] = wh_throghput*return_ratio_value*float(assumptions.where(assumptions['variable'] == 'kg_per_quantity',axis=0)['value'].dropna())
        result.loc[i,'description'] = 'on daily basis'
        result.loc[i,'calculation'] = 'wh_throghput*return_ratio_value*kg_per_quantity'
        i = i+1

        def additional_cost_while_returning(km):
            if km<=10:
                return 150
            elif km<=20:
                return 300
            else:
                return 450

        additiona_cost_while_returns = additional_cost_while_returning(float(result.where(result['variable'] == 'flow_through_store_to_wh_in_kg', axis=0)['values'].dropna()))

        result.loc[i,'variable'] = 'flat additional cost for wh returns'
        result.loc[i,'values'] = additiona_cost_while_returns
        result.loc[i,'description'] = 'on daily basis'
        result.loc[i,'calculation'] = 'if <10 Kg per day 150, 20 - 300, else - 450'
        i = i+1

        result.loc[i, 'variable'] = 'cost of transport of wh returns'
        result.loc[i, 'values'] = (wh_throghput*return_ratio_value * float(
            assumptions.where(assumptions['variable'] == 'kg_per_quantity', axis=0)[
                'value'].dropna()) * cost_of_transport_  + additiona_cost_while_returns)* 30
        result.loc[i, 'description'] = 'on monthly basis in Rs'
        result.loc[i, 'type'] = 'logistics_1'
        result.loc[i,'calculation'] = '(flow_through_store_to_wh_in_kg*cost_of_transport + flat_rate)*30'
        i = i + 1

        tempo_rent = float(assumptions.where(assumptions['variable'] == 'tempo_rent', axis=0)['value'].dropna())
        tempo_mileage = float(assumptions.where(assumptions['variable'] == 'tempo_mileage', axis=0)['value'].dropna())
        petrol_cost = float(assumptions.where(assumptions['variable'] == 'petrol_cost', axis=0)['value'].dropna())
        quantity_per_tempo = float(assumptions.where(assumptions['variable'] == 'quantity_per_tempo', axis=0)['value'].dropna())

        result.loc[i,'variable'] = 'tempo travel info'
        result.loc[i,'Salary_per_person'] =tempo_rent
        result.loc[i, 'throghput'] = tempo_mileage
        result.loc[i, 'quantity'] = quantity_per_tempo
        result.loc[i, 'values'] = petrol_cost
        result.loc[i,'description'] = 'values-petrol_cost, quantity=quantity_per_tempo, throghput=tempo_mileage, Salary_per_person=tempo_rent'
        result.loc[i,'calculation'] = 'input'
        i = i+1

        if model==4:
            tempo_trips_per_day = math.ceil(wh_throghput*dc_holding_inventory_for_n_days/quantity_per_tempo)/dc_holding_inventory_for_n_days
        else:
            tempo_trips_per_day = math.ceil(wh_throghput/ quantity_per_tempo)

        result.loc[i,'variable'] = 'tempo trips per day'
        result.loc[i,'values'] =tempo_trips_per_day
        result.loc[i, 'quantity'] = (city_distance_from_mumbai_in_km/tempo_mileage*2)
        result.loc[i,'description'] = 'values - trips per day, quantity - petrol used per trip'
        result.loc[i,'calculation'] = 'if no inv holding at dc - ceil(dc_throghput/ quantity_per_tempo), if dc - ceil(dc_throghput*dc_holding_inventory_for_n_days/quantity_per_tempo)/dc_holding_inventory_for_n_days '
        i = i+1

        result.loc[i,'variable'] = 'tempo trips cost per month'
        result.loc[i, 'quantity'] = tempo_trips_per_day*30
        result.loc[i,'values'] =(tempo_trips_per_day)*30*(tempo_rent+(city_distance_from_mumbai_in_km/tempo_mileage*2)*petrol_cost)
        result.loc[i, 'throghput'] = (tempo_trips_per_day)*30*(tempo_rent)
        result.loc[i, 'Salary_per_person'] = (city_distance_from_mumbai_in_km/tempo_mileage*2)*petrol_cost
        result.loc[i,'description'] = 'per month basis'
        result.loc[i,'type'] = 'logistics_2'
        result.loc[i,'calculation'] = 'quantity- trips,throghput = flat charge,Salary_per_person = Petrol charge per trip'
        i = i+1

        logistic_comparison = result[result['type'].isin(['logistics_1','logistics_2'])].groupby(['type']).agg({'values': [np.sum]}).reset_index()
        logistic_comparison.columns = ["-".join(x) for x in logistic_comparison.columns.ravel()]

        if logistic_comparison.loc[0,'values-sum']>=logistic_comparison.loc[1,'values-sum']:
            output_logistic = logistic_comparison.loc[1,'type-']
            logistic_value = logistic_comparison.loc[1,'values-sum']
        else:
            output_logistic = logistic_comparison.loc[0,'type-']
            logistic_value = logistic_comparison.loc[0,'values-sum']

        result.loc[i,'variable'] = 'best-logistic'
        result.loc[i, 'quantity'] = output_logistic
        result.loc[i,'values'] =logistic_value
        result.loc[i, 'throghput'] = f"logistic_1 - {round(logistic_comparison.loc[0,'values-sum'])}"
        result.loc[i, 'Salary_per_person'] = f"logistic_2 - {round(logistic_comparison.loc[1,'values-sum'])}"
        result.loc[i,'description'] = 'per month basis'
        result.loc[i,'type'] = 'logistics'
        result.loc[i,'calculation'] = 'min of logistics_1 & 2'
        i = i+1

        cols_to_move = ['variable', 'values', 'quantity', 'Salary_per_person', 'throghput', 'type', 'description','calculation']
        result = result[cols_to_move + [col for col in result.columns
                                        if col not in cols_to_move]]

        summary = result[(result['type'].notna())&(~result['type'].isin(['logistics_1','logistics_2']))].groupby(['type']).agg({'values': [np.sum]}).reset_index()

        summary.columns = ["-".join(x) for x in summary.columns.ravel()]

        summary['model-name'] = model_name

        summary['model-number'] = model

        summary['desciption'] = f'logistic_choosed - {output_logistic}'

        summary.rename(columns = {'type-':'type',
                                  'values-sum':'values'}, inplace = True)

        cols_to_move = ['model-number','model-name', 'type', 'values']
        summary = summary[cols_to_move + [col for col in summary.columns
                                        if col not in cols_to_move]]

        summary_final = summary_final.append(summary)

        if model==1:
            model1 = result.copy(deep = True)
        elif model ==2:
            model2 =  result.copy(deep = True)
        elif model ==3:
            model3 = result.copy(deep = True)
        elif model ==4:
            model4 = result.copy(deep = True)

    model_cost=summary_final.groupby(['model-name','model-number']).agg({'values': [np.sum]}).reset_index()
    model_cost.columns = ["-".join(x) for x in model_cost.columns.ravel()]
    model_cost.rename(columns={'model-name-': 'model-name',
                            'model-number-': 'model-number',
                            'values-sum': 'values'}, inplace=True)
    model_cost['values'] = round(model_cost['values'],0)
    model_cost['values'] = model_cost['values'].astype(int)
    model_cost['revenue'] = int(round(avg_store_sale*number_of_stores,0))
    model_cost['revenue-percentage'] = round((model_cost['values'].astype(float)*100)/float(avg_store_sale*number_of_stores),2)
    cols_to_move = [ 'model-number', 'model-name', 'values']
    model_cost = model_cost[cols_to_move + [col for col in model_cost.columns
                                      if col not in cols_to_move]]

    # model_cost.idxmax(axis = 0, skipna = True)
    # model1.to_csv('model1.csv')
    # model2.to_csv('model2.csv')
    # model3.to_csv('model3.csv')
    # model4.to_csv('model4.csv')
    # summary_final.to_csv('summary.csv')

    # model_1 = s3.save_df_to_s3(df=model1, file_name=f'{city_name}_model1.csv')
    # model_2 = s3.save_df_to_s3(df=model2, file_name=f'{city_name}_model2.csv')
    # model_3 = s3.save_df_to_s3(df=model3, file_name=f'{city_name}_model3.csv')
    # model_4 = s3.save_df_to_s3(df=model4, file_name=f'{city_name}_model4.csv')
    # summary_1 = s3.save_df_to_s3(df=summary_final, file_name=f'{city_name}_summary.csv')
    # model_cost_ = s3.save_df_to_s3(df=model_cost, file_name=f'{city_name}_total.csv')

    # Formatting Excel
    path = "/".join(os.getcwd().split("/")[:-2]) + "/tmp/"
    if not os.path.exists(path):
        os.mkdir(path, 0o777)

    file_name = f"DNM_{city_name}_{number_of_stores}_stores.xlsx"
    local_file_full_path = path + file_name

    # writing in a Excel

    with pd.ExcelWriter(local_file_full_path) as writer:
        model_cost.to_excel(writer, sheet_name='total', index=False)
        summary_final.to_excel(writer, sheet_name='model_summay', index=False)
        model1.to_excel(writer, sheet_name='model_1', index=False)
        model2.to_excel(writer, sheet_name='model_2', index=False)
        model3.to_excel(writer, sheet_name='model_3', index=False)
        model4.to_excel(writer, sheet_name='model_4', index=False)
        assumptions.to_excel(writer, sheet_name='assumptions', index=False)

    status = True

except Exception as error:
    logger.exception(error)
    logger.info(f'code failed in between')
    status = False

if status is True:
    status = 'Success'
else:
    status = 'Failed'

end_time = datetime.datetime.now(tz=gettz('Asia/Kolkata'))
difference = end_time - start_time
min_to_complete = round(difference.total_seconds() / 60, 2)
email = Email()

if status=="Success":
    email.send_email_file(subject=f"Distributor Network Model - Costs Analysis",
                          mail_body=f"Dear User,\n"
                                    f"\n"
                                    f"Distributor Network Model- Costs Analysis\n"
                                    f"city - {city_name}\n"
                                    f"number of stores - {number_of_stores}\n"
                                    f"expected revenue - {int(round(avg_store_sale*number_of_stores,0))}\n"
                                    f"Recommendation - {model_cost.loc[model_cost['values'].idxmin(),'model-name']}\n"
                                    f"\n"
                                    f"Summary\n"
                                    f"{model_cost[['model-number','model-name','values','revenue-percentage']].to_string(col_space=25)}\n"
                                    f"\n"
                                    f"Regards,\n"
                                    f"Data Team\n",
                          to_emails=email_to, file_paths=[local_file_full_path])
else:
    email.send_email_file(subject=f"{env}-{status}-dnm-cost-analysis",
                          mail_body=f"Dear User,\n"
                                    f"Distributor Network Model- Costs Analysis - job is failed, Please connect with Data team to resolve this issue"
                                    f"\n"
                                    f"Regards,\n"
                                    f"Data Team\n",
                          to_emails=email_to, file_uris=[])

rs_db.close_connection()
rs_db_write.close_connection()