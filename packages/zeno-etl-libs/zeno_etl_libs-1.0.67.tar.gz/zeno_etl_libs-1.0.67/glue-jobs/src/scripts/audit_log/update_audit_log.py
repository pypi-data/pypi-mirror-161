import boto3
import sys
import os
import argparse
import pandas as pd
import numpy as np
from datetime import datetime

sys.path.append('../../../..')
from zeno_etl_libs.db.db import DB
from zeno_etl_libs.helper.aws.s3 import S3
from zeno_etl_libs.logger import get_logger
from zeno_etl_libs.helper import helper

client = boto3.client('glue')

parser = argparse.ArgumentParser(description="This is ETL script.")
parser.add_argument('-e', '--env', default="dev", type=str, required=False)
args, unknown = parser.parse_known_args()
env = args.env
os.environ['env'] = env

logger = get_logger()
db = DB()
db.open_connection()
s3 = S3()
record_list = []

table_name = 'audit-log'
schema = 'prod2-generico'

table_info = helper.get_table_info(db=db, table_name=table_name, schema=schema)
job_list_response = client.list_jobs(MaxResults=500)
job_list = job_list_response['JobNames']

for i in job_list:
    if i.__contains__(env):
        query = """select max("started-on") from "{}"."{}" where "job-name" = '{}';""".format(schema, table_name, i)
        df_init = db.get_df(query)
        max_processing_date = df_init.values[0][0]
        response = client.get_job_runs(
            JobName=i
        )
        response_list = response['JobRuns']
        for i in response_list:
            if max_processing_date is None:
                record_list.append(i)
            elif i['StartedOn'].strftime('%Y-%m-%d %H:%M:%s') > datetime.utcfromtimestamp((max_processing_date - np.datetime64('1970-01-01T00:00:00')) / np.timedelta64(1, 's')).strftime('%Y-%m-%d %H:%M:%s'):
                record_list.append(i)

df = pd.DataFrame(record_list)
if df.empty:
    logger.info(df)
else:
    logger.info(df.columns)
    df.drop(['Arguments', 'PredecessorRuns', 'AllocatedCapacity', 'Timeout', 'MaxCapacity', 'LogGroupName', 'GlueVersion'],
            axis=1, inplace=True)
    column_list = df.columns
    logger.info(df.columns)
    if 'ErrorMessage' not in column_list:
        df['ErrorMessage'] = 'NULL'
    if 'TriggerName' not in column_list:
        df['TriggerName'] = 'NULL'
    if column_list.__contains__('WorkerType') or column_list.__contains__('NumberOfWorkers'):
        df.drop(['WorkerType', 'NumberOfWorkers'], axis=1, inplace=True)
    logger.info(df.columns)
    df = df.reindex(columns=['Id', 'Attempt', 'TriggerName','JobName', 'StartedOn', 'LastModifiedOn', 'CompletedOn', 'JobRunState', 'ExecutionTime', 'ErrorMessage'])
    df.columns = ['id', 'attempt', 'trigger-name', 'job-name', 'started-on', 'last-modified-on', 'completed-on',
                  'job-run-state', 'execution-time', 'error-message']
    s3.write_df_to_db(df=df[table_info['column_name']], table_name=table_name, db=db,
                      schema=schema)


