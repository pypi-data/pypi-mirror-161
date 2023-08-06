"""
Author:shubham.gupta@zeno.health
Purpose: Near Expiry Promo Trigger
"""

import argparse
import os
import sys
from datetime import datetime as dt

sys.path.append('../../../..')

from zeno_etl_libs.logger import get_logger
from zeno_etl_libs.helper.aws.s3 import S3
from zeno_etl_libs.db.db import DB
from zeno_etl_libs.helper.email.email import Email
from zeno_etl_libs.helper.parameter.job_parameter import parameter

parser = argparse.ArgumentParser(description="This is ETL script.")
parser.add_argument('-e', '--env', default="dev", type=str, required=False)

args, unknown = parser.parse_known_args()
env = args.env
os.environ['env'] = env

job_params = parameter.get_params(job_id=126)

email_to = job_params['email_to']
logger = get_logger()

logger.info(f"env: {env}")

rs_db = DB()
rs_db.open_connection()

s3 = S3()

read_schema = 'prod2-generico'
report_date = dt.now().date()

promo_q = """
        select
            "promo-code",
            "total-used",
            "max-time" "total-available",
            expiry,
            datediff('days', current_date, date(expiry)) "expiry-in-days"
        from
            "prod2-generico"."promo-codes" pc
        where
            "code-type" != 'referral'
            and status = 'active'
            and current_date <= expiry
            and datediff('days', current_date, date(expiry)) <= 7
        order by
            "expiry";
        """
promo = rs_db.get_df(promo_q)

if promo.shape[0] >= 1:
    # Uploading the file to s3
    promo_uri = s3.save_df_to_s3(df=promo, file_name='Promo_Near_Expiry.csv')

    # Sending email
    subject = 'PROMO NEAR EXPIRY | ALERT !! ALERT !! ALERT !! ALERT !! '
    mail_body = """
    Hey Team,
    
    Some promos are about to expire in less than a week
    Please check attached file and take actions
                
    Thanks & Regards
    """

    file_uris = [promo_uri]
    email = Email()
    email.send_email_file(subject=subject, mail_body=mail_body, to_emails=email_to, file_uris=file_uris)
