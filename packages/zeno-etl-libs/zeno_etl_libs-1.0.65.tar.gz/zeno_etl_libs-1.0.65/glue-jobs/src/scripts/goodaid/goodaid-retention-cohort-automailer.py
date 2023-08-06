#!/usr/bin/env python
# coding: utf-8
import os
import sys

sys.path.append('../../../..')

from zeno_etl_libs.db.db import DB
from zeno_etl_libs.helper.aws.s3 import S3
from zeno_etl_libs.helper.email.email import Email
from zeno_etl_libs.logger import get_logger


import pandas as pd
import datetime
import argparse
import operator as op

parser = argparse.ArgumentParser(description="This is ETL script.")
parser.add_argument('-e', '--env', default="dev", type=str, required=False)
parser.add_argument('-et', '--email_to', default="sanjay.bohra@zeno.health,rohan.kamble@zeno.health,"
                                                 "renuka.rawal@zeno.health", type=str, required=False)
args, unknown = parser.parse_known_args()
email_to = args.email_to
env = args.env
os.environ['env'] = env

logger = get_logger()

logger.info(f"env: {env}")

rs_db = DB()
rs_db.open_connection()

s3 = S3()

query = '''
        select
            s."patient-id" ,
            s."created-at" ,
            s."drug-id",
            s.composition ,
            g.category
        from
            "prod2-generico"."prod2-generico".sales s
        left join "prod2-generico"."prod2-generico"."goodaid-atc-sr" g on
            s."drug-id" = g."drug-id"
        where
            s."company-id" = 6984
            and
             date(s."created-at") >= '2021-03-01'  ;'''
data = rs_db.get_df(query)
data.columns = [c.replace('-', '_') for c in data.columns]
df = data


# this function returns a DataFrame containing the acquisition date and order date
def get_cohorts(df, period='M'):
    df = df[['patient_id', 'created_at']].drop_duplicates()
    df = df.assign(Month=df.groupby('patient_id') \
        ['created_at'].transform('min').dt.to_period(period))
    df = df.assign(order_date=df['created_at'].dt.to_period(period))
    return df


# calculates the retention of customers after their acquisition
def get_retention(df, period='M'):
    df = get_cohorts(df, period).groupby(['Month', 'order_date']) \
        .agg(patients=('patient_id', 'nunique')) \
        .reset_index(drop=False)
    df['periods'] = (df.order_date - df.Month).apply(op.attrgetter('n'))
    return df


# Returns a cohort matrix
def get_cohort_matrix(df, period='M', percentage=False):
    df = get_retention(df, period).pivot_table(index='Month',
                                               columns='periods',
                                               values='patients')
    if percentage:
        df = df.divide(df.iloc[:, 0], axis=0) * 100
    return df


# overall Cohort monthly
overall_mon = get_cohort_matrix(df, 'M', percentage=False).reset_index()
overall_mon_per = get_cohort_matrix(df, 'M', percentage=True).round(2).reset_index()
overall_mon_per[0] = overall_mon[0]

# overall Cohort quarter
overall_quat = get_cohort_matrix(df, 'Q', percentage=False).reset_index()
overall_quat_per = get_cohort_matrix(df, 'Q', percentage=True).round(2).reset_index()
overall_quat_per[0] = overall_quat[0]

# chronic cohort monthly
df = data[data['category'] == 'chronic']
chronic_mon = get_cohort_matrix(df, 'M', percentage=False).reset_index()
chronic_mon_per = get_cohort_matrix(df, 'M', percentage=True).round(2).reset_index()
chronic_mon_per[0] = chronic_mon[0]

# chronic cohort quarterly
chronic_quat = get_cohort_matrix(df, 'Q', percentage=False).reset_index()
chronic_quat_per = get_cohort_matrix(df, 'Q', percentage=True).round(2).reset_index()
chronic_quat_per[0] = chronic_quat[0]

# acute cohorts monthly
df = data[data['category'] == 'acute']
acute_mon = get_cohort_matrix(df, 'M', percentage=False).reset_index()
acute_mon_per = get_cohort_matrix(df, 'M', percentage=True).round(2).reset_index()
acute_mon_per[0] = acute_mon[0]

# acute cohort quarterly
acute_quat = get_cohort_matrix(df, 'Q', percentage=False).reset_index()
acute_quat_per = get_cohort_matrix(df, 'Q', percentage=True).round(2).reset_index()
acute_quat_per[0] = acute_quat[0]

# Formatting Excel
path = "/".join(os.getcwd().split("/")[:-2]) + "/tmp/"
if not os.path.exists(path):
    os.mkdir(path, 0o777)

time_now = datetime.datetime.now().strftime('%Y-%m-%d')
currentMonth= datetime.datetime.now().strftime('%m')
currentDay = datetime.datetime.now().day
datetime_object = datetime.datetime.strptime(currentMonth, "%m")
full_month_name = datetime_object.strftime("%B")

file_name = "Cohorts_{}.xlsx".format(time_now)
local_file_full_path = path + file_name


# writing in a Excel

with pd.ExcelWriter(local_file_full_path) as writer:
    overall_mon.to_excel(writer, sheet_name='Overall Monthly', index=False)
    overall_mon_per.to_excel(writer, sheet_name='Overall Monthly', index=False, startrow=len(overall_mon) + 4)
    overall_quat.to_excel(writer, sheet_name='Overall Quarterly', index=False)
    overall_quat_per.to_excel(writer, sheet_name='Overall Quarterly', index=False, startrow=len(overall_quat) + 4)
    chronic_mon.to_excel(writer, sheet_name='Chronic Monthly', index=False)
    chronic_mon_per.to_excel(writer, sheet_name='Chronic Monthly', index=False, startrow=len(chronic_mon) + 4)
    chronic_quat.to_excel(writer, sheet_name='Chronic Quarterly', index=False)
    chronic_quat_per.to_excel(writer, sheet_name='Chronic Quarterly', index=False, startrow=len(chronic_quat) + 4)
    acute_mon.to_excel(writer, sheet_name='Acute Monthly', index=False)
    acute_mon_per.to_excel(writer, sheet_name='Acute Monthly', index=False, startrow=len(acute_mon) + 4)
    acute_quat.to_excel(writer, sheet_name='Acute Quarterly', index=False)
    acute_quat_per.to_excel(writer, sheet_name='Acute Quarterly', index=False, startrow=len(acute_quat) + 4)

email = Email()
email.send_email_file(subject="Cohorts for {}".format(full_month_name),
                      mail_body='Hi Rohan please find the attached Cohorts till {}-{}'.format(currentDay,full_month_name),
                      to_emails=email_to, file_paths=[local_file_full_path])

# closing the connection
rs_db.close_connection()