# Take city Name as input
# Calculate Distance from Mumbai in Code
# Give Rate of transportation based on distance
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
parser.add_argument('-n', '--number_of_stores', default=10, type=int, required=False)
parser.add_argument('-cn', '--city_name', default="Nagpur", type=str, required=False)
parser.add_argument('-cd', '--city_distance_from_mumbai_in_km', default=836, type=int, required=False)
parser.add_argument('-inp', '--increase_in_purchasing_power_compared_to_mumbai', default=86.99, type=int, required=False)
args, unknown = parser.parse_known_args()
env = args.env
email_to = args.email_to
number_of_stores = args.number_of_stores
city_name = args.city_name
city_distance_from_mumbai_in_km = args.city_distance_from_mumbai_in_km
increase_in_purchasing_power_compared_to_mumbai = args.increase_in_purchasing_power_compared_to_mumbai

city_cost_parity = 1/((increase_in_purchasing_power_compared_to_mumbai+100)/100)

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

logger.info("")

# date parameter
logger.info("code started at {}".format(datetime.datetime.now(tz=gettz('Asia/Kolkata')).strftime(
    '%Y-%m-%d %H:%M:%S')))
logger.info("")

status = False
# assumptions = pd.read_csv(r'D:\Distribution Network Model\assumptions.csv')
assumptions = pd.read_csv(s3.download_file_from_s3(file_name="dnm-cost-input/assumptions.csv"))
# assumptions.set_index('variable',inplace=True)

# Calculating last 30 days sales figures
store_sales_query = f"""
    select
        s3."s-type" as "variable",
        round(avg(s3.value), 0) as values,
        round(avg(s3.quantity), 0) as quantity,
        round(avg(s3."purchase-rate"), 0) as "purchase-rate",
        -- round(avg(s3.ptr), 0) as ptr,
        'type wise last 30 days sales' as "description"
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
                sum(s."purchase-rate") as "purchase-rate" ,
                sum(s.ptr) as "ptr",
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

avg_store_sale = store_sales['values'].sum()
avg_quantity = store_sales['quantity'].sum()
avg_cogs = store_sales['purchase-rate'].sum()
logger.info(f'average sale of current stores  - {avg_store_sale}')
logger.info(f'quantity per store as per current stores  - {avg_quantity}')
logger.info(f'cogs per store as per current stores  - {avg_cogs}')

# fofo_store_factor = float(assumptions.where(assumptions['variable'] == 'fofo_store_sales_as_percentage_of_total',axis=0).dropna()['value'])
#
# avg_fofo_store_sale = float(avg_store_sale)*float(fofo_store_factor)

model = [1,2]
if model== 1:
    model_name =  'wh_to_store_direct'
if model==2:
    model_name = 'wh_to_store_via_dc'

result = pd.DataFrame(columns=['variable','values'])

model = 2
i = 0
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
result.loc[i,'values'] = number_of_stores
result.loc[i,'description'] = 'calculation based on purchasing power'
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
    distribution = {'wh_ethical': 0.7,
    'wh_goodaid':1,
    'wh_generic':0.9,
    'wh_others':0.6}

elif model==2:
    distribution = {'wh_ethical': 0.7,
    'wh_goodaid':1,
    'wh_generic':0.9,
    'wh_others':0.6}

result.loc[i,'variable'] = 'wh ethical'
result.loc[i,'values'] = distribution['wh_ethical']
result.loc[i,'description'] = f'value - % Quantity Transfer through WH for Ethical,quantity transfer per day'
result.loc[i,'quantity'] =(distribution['wh_ethical']*float(result.where(result['variable'] == 'ethical',axis=0)['quantity'].dropna())/30)*number_of_stores
i = i+1

result.loc[i,'variable'] = 'wh goodaid'
result.loc[i,'values'] = distribution['wh_goodaid']
result.loc[i,'description'] = f'value - % Quantity Transfer through WH for goodaid'
result.loc[i,'quantity'] =(distribution['wh_goodaid']*float(result.where(result['variable'] == 'goodaid',axis=0)['quantity'].dropna())/30)*number_of_stores
i = i+1

result.loc[i,'variable'] = 'wh generic'
result.loc[i,'values'] = distribution['wh_generic']
result.loc[i,'description'] = f'value - % Quantity Transfer through WH for generic'
result.loc[i,'quantity'] =(distribution['wh_generic']*float(result.where(result['variable'] == 'generic',axis=0)['quantity'].dropna())/30)*number_of_stores
i = i+1

result.loc[i,'variable'] = 'wh others'
result.loc[i,'values'] = distribution['wh_others']
result.loc[i,'description'] = f'value - % Quantity Transfer through WH for others'
result.loc[i,'quantity'] =(distribution['wh_others']*float(result.where(result['variable'] == 'others',axis=0)['quantity'].dropna())/30)*number_of_stores
i = i+1

wh_throghput = result.where(result['variable'].isin(['wh ethical', 'wh generic', 'wh goodaid', 'wh others']),axis=0)['quantity'].dropna().sum()
result.loc[i,'variable'] = 'wh throghput'
result.loc[i,'quantity'] = wh_throghput
result.loc[i,'description'] = f'quantity flow through wh on daily basis'
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

result.loc[i,'variable'] = 'dc ethical'
result.loc[i,'values'] = 1-distribution['wh_ethical']
result.loc[i,'description'] = f'value - % Quantity Transfer directly through dc for Ethical'
result.loc[i,'quantity'] =((1 - distribution['wh_ethical'])*float(result.where(result['variable'] == 'ethical',axis=0)['quantity'].dropna())/30)*number_of_stores
i = i+1

result.loc[i,'variable'] = 'dc goodaid'
result.loc[i,'values'] = 1 - distribution['wh_goodaid']
result.loc[i,'description'] = f'value - % Quantity Transfer directly through dc for goodaid'
result.loc[i,'quantity'] =((1 - distribution['wh_goodaid'])*float(result.where(result['variable'] == 'goodaid',axis=0)['quantity'].dropna())/30)*number_of_stores
i = i+1

result.loc[i,'variable'] = 'dc generic'
result.loc[i,'values'] = 1 - distribution['wh_generic']
result.loc[i,'description'] = f'value - % Quantity Transfer directly through dc for generic'
result.loc[i,'quantity'] =((1-distribution['wh_generic'])*float(result.where(result['variable'] == 'generic',axis=0)['quantity'].dropna())/30)*number_of_stores
i = i+1

result.loc[i,'variable'] = 'dc others'
result.loc[i,'values'] = 1 - distribution['wh_others']
result.loc[i,'description'] = f'value - % Quantity Transfer directly through dc for others'
result.loc[i,'quantity'] =((1- distribution['wh_others'])*float(result.where(result['variable'] == 'others',axis=0)['quantity'].dropna())/30)*number_of_stores
i = i+1

dc_throghput = result.where(result['variable'].isin(['dc ethical', 'dc generic', 'dc goodaid', 'dc others']),axis=0)['quantity'].dropna().sum()
result.loc[i,'variable'] = 'dc throghput'
result.loc[i,'quantity'] = dc_throghput
result.loc[i,'description'] = f'quantity flow through wh on daily basis'
i = i+1

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
dc_staff['quantity'] = dc_staff['quantity'].apply(np.ceil)
dc_staff['values'] = dc_staff['quantity']*dc_staff['Salary_per_person']
dc_staff['type'] = 'dc_variable'
dc_staff.reset_index(inplace=True,drop = True)
dc_employees = dc_staff['quantity'].sum()
dc_staff.loc[5,'quantity'] = dc_employees
dc_staff.loc[5,'values'] = dc_employees*dc_staff.loc[5,'throghput']*30

result = pd.concat([result,dc_staff],sort=True)
i = i + 7
result.reset_index(inplace=True,drop=True)

dc_fixed = assumptions[assumptions['type']=='dc_fixed'][['variable', 'value' , 'Salary_per_person', 'description']]

dc_fixed.rename(columns = { 'value': 'throghput'}, inplace=True)
dc_fixed['description'] = f'throghput - total cost per month in mumbai, value = cost in {city_name}'
dc_fixed['values'] = dc_fixed['throghput']*city_cost_parity
dc_fixed['type'] = 'dc_fixed'
result = pd.concat([result,dc_fixed],sort=True)
i = i + 7
result.reset_index(inplace=True,drop=True)


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
        return 20
    elif km<=200:
        return 25
    elif km<=300:
        return 30
    elif km <= 400:
        return 35
    elif km <= 500:
        return 40
    elif km <= 1000:
        return 50
    elif km<= 2000:
        return 70
    else:
        return 100

result.loc[i,'variable'] = 'cost per kg'
result.loc[i,'values'] = cost_of_transport(city_distance_from_mumbai_in_km)
result.loc[i,'description'] = 'cost assumed based on distance'
i = i+1

result.loc[i,'variable'] = 'cost of transport till courier destination'
result.loc[i,'values'] = wh_throghput*cost_of_transport(city_distance_from_mumbai_in_km)*30
result.loc[i,'description'] = 'on monthly basis in Rs'
i = i+1

result.loc[i,'variable'] = 'delivery assosiate required'
result.loc[i,'values'] = wh_throghput*cost_of_transport(city_distance_from_mumbai_in_km)*30
result.loc[i,'description'] = 'for transport from Courier Destination to Stores'
result.loc[i,'Salary_per_person'] = 15000
i = i+1


cols_to_move = ['variable', 'values', 'quantity', 'Salary_per_person', 'throghput','description']
result = result[cols_to_move + [col for col in result.columns
                                                if col not in cols_to_move]]


npi_added_uri = s3.save_df_to_s3(df=final_list, file_name='npi_removal_details_{}.csv'.format(cur_date))

status = True

if status is True:
    status = 'Success'
else:
    status = 'Failed'

end_time = datetime.datetime.now()
difference = end_time - start_time
min_to_complete = round(difference.total_seconds() / 60, 2)
email = Email()

email.send_email_file(subject=f"{env}-{status} : DMV-Costs",
                      mail_body=f"abc",
                      to_emails=email_to, file_uris=[npi_added_uri])

rs_db.close_connection()
rs_db_write.close_connection()

