"""
Script to manually write SS, ROP, OUP into DOID from CSV in S3 bucket

* File should be uploded into "s3://aws-glue-temporary-921939243643-ap-south-1/doid_manual_update_csv/"
* Required columns in input csv file: ["store_id", "drug_id", "ss_col", "rop_col", "oup_col"]
* ss_col, rop_col, oup_col names present in csv is specified via input params.
* End path of the file "doid_manual_update_csv/file_name.csv" should also be passed as input param.

author: vivek.revi@zeno.health
"""

import os
import sys

import pandas as pd

sys.path.append('../../../..')

from zeno_etl_libs.helper.aws.s3 import S3
from zeno_etl_libs.utils.doid_write import doid_custom_write
from zeno_etl_libs.logger import get_logger
from zeno_etl_libs.helper.email.email import Email

import argparse


def main(s3_file_end_path, ss_col_name, rop_col_name, oup_col_name, s3,
         debug_mode, logger):

    logger.info(f"Debug Mode: {debug_mode}")
    status = 'Failed'
    missed_entries = pd.DataFrame()

    try:
        # Read csv file from S3 into pandas datafame
        logger.info("Reading file from S3 into pd.DataFrame")
        file_path = s3.download_file_from_s3(s3_file_end_path)
        df_upload = pd.read_csv(file_path)
        logger.info(f"Input DF shape: {df_upload.shape}")

        if debug_mode == 'N':
            # Upload values into DOID
            logger.info("Updating new values into DOID")
            missed_entries = doid_custom_write(df_upload, logger,
                                               ss_col=ss_col_name,
                                               rop_col=rop_col_name,
                                               oup_col=oup_col_name)

            # Delete file from S3
            logger.info("Deleting uploaded file from S3")
            s3_file_uri = "s3://aws-glue-temporary-921939243643-ap-south-1/" + s3_file_end_path
            s3.delete_s3_obj(uri=s3_file_uri)

        status = 'Success'
        logger.info(f"DOID manual update code execution status: {status}")

    except Exception as error:
        logger.exception(error)
        logger.info(f"DOID manual update code execution status: {status}")

    return status, missed_entries


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="This is ETL script.")
    parser.add_argument('-e', '--env', default="dev", type=str,
                        required=False)
    parser.add_argument('-d', '--debug_mode', default="Y", type=str,
                        required=False)
    parser.add_argument('-et', '--email_to',
                        default="vivek.revi@zeno.health", type=str,
                        required=False)
    parser.add_argument('-s3fn', '--s3_file_end_path',
                        default="doid_manual_update_csv/file_name.csv", type=str,
                        required=False)
    parser.add_argument('-ss', '--ss_col_name',
                        default="ss", type=str, required=False)
    parser.add_argument('-rop', '--rop_col_name',
                        default="rop", type=str, required=False)
    parser.add_argument('-oup', '--oup_col_name',
                        default="oup", type=str, required=False)

    args, unknown = parser.parse_known_args()

    env = args.env
    os.environ['env'] = env
    debug_mode = args.debug_mode
    email_to = args.email_to
    s3_file_end_path = args.s3_file_end_path
    ss_col_name = args.ss_col_name
    rop_col_name = args.rop_col_name
    oup_col_name = args.oup_col_name

    logger = get_logger()
    s3 = S3()

    status, missed_entries = main(s3_file_end_path, ss_col_name, rop_col_name,
                                  oup_col_name, s3, debug_mode, logger)

    missed_entries_uri = s3.save_df_to_s3(
        missed_entries, file_name=f"missed_entries_manual_update.csv")

    # SEND EMAIL ATTACHMENTS
    logger.info("Sending email attachments..")
    email = Email()
    email.send_email_file(
        subject=f"DOID Manual Update (GLUE-{env}): {status}",
        mail_body=f"""
                   Debug Mode: {debug_mode}
                   Job Params: {args}
                   """,
        to_emails=email_to, file_uris=[missed_entries_uri])

    logger.info("Script ended")
