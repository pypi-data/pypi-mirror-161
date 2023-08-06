"""main wrapper for IPC2.0 safety stock reset"""

import os
import sys
import argparse

import pandas as pd
import numpy as np
import datetime as dt
from dateutil.tz import gettz
from ast import literal_eval

sys.path.append('../../../..')
# sys.path.insert(0,'/Users/tusharuike/ETL')

from zeno_etl_libs.helper.aws.s3 import S3
from zeno_etl_libs.db.db import DB, PostGre
from zeno_etl_libs.django.api import Django
from zeno_etl_libs.logger import get_logger
from zeno_etl_libs.helper.email.email import Email
from zeno_etl_libs.helper import helper

from zeno_etl_libs.utils.ipc2.forecast_main import ipc_forecast
from zeno_etl_libs.utils.ipc2.safety_stock import safety_stock_calc
from zeno_etl_libs.utils.ipc2.portfolio_consolidation import wh_consolidation, \
    goodaid_consolidation, D_class_consolidation
from zeno_etl_libs.utils.ipc.store_portfolio_additions import generic_portfolio
from zeno_etl_libs.utils.ipc.npi_exclusion import omit_npi_drugs
from zeno_etl_libs.utils.ipc2.post_processing import post_processing
from zeno_etl_libs.utils.ipc2.helpers.correction_flag import compare_df, \
    add_correction_flag
from zeno_etl_libs.utils.ipc.doid_update_ss import doid_update
from zeno_etl_libs.utils.ipc2.helpers.outlier_check import check_oup_outlier


def main(debug_mode, reset_stores, reset_date, type_list, reset_store_ops,
         v3_active_flag, v4_active_flag, v5_active_flag, v6_active_flag,
         d_class_consolidation, wh_gen_consolidation, goodaid_ss_flag,
         keep_all_generic_comp, omit_npi, ga_inv_weight, rest_inv_weight,
         top_inv_weight, v6_type_list, v6_ptr_cut_off,
         corrections_selling_probability_cutoff,
         corrections_cumulative_probability_cutoff, drug_type_list_v4,
         outlier_check, rs_db_read, rs_db_write, read_schema, write_schema,
         s3, django, logger):

    logger.info(f"Debug Mode: {debug_mode}")
    status = 'Failed'

    # Define empty variables if required in case of fail
    order_value_all = pd.DataFrame()
    new_drug_entries = pd.DataFrame()
    missed_entries = pd.DataFrame()
    df_outliers_all = pd.DataFrame()
    manual_doid_upd_all = pd.DataFrame()

    try:
        for store_id in reset_stores:
            logger.info(f"Running for store id: {store_id} and reset date: {reset_date}")

            if not type_list:
                type_list = str(
                    list(reset_store_ops.loc[reset_store_ops['store_id'] ==
                                             store_id, 'type'].unique()))
                type_list = type_list.replace('[', '(').replace(']', ')')

            # RUNNING IPC2.0 FORECAST PIPELINE
            logger.info("Forecast Pipeline starts...")
            agg_fcst, cal_sales, weekly_fcst, seg_df, drug_class = ipc_forecast(
                store_id, reset_date, type_list, read_schema, rs_db_read,
                logger)

            # SAFETY STOCK CALCULATIONS
            logger.info("Safety Stock Calculations starts...")
            safety_stock_df = safety_stock_calc(
                agg_fcst, cal_sales, store_id, reset_date, v3_active_flag,
                corrections_selling_probability_cutoff,
                corrections_cumulative_probability_cutoff,
                v4_active_flag, drug_type_list_v4, v5_active_flag, read_schema,
                rs_db_read, logger)

            # D-CLASS SKU CONSOLIDATION
            if d_class_consolidation == 'Y':
                logger.info("D Class Consolidation starts")
                df_pre_corr = safety_stock_df.copy()
                safety_stock_df = D_class_consolidation(
                    safety_stock_df, store_id, rs_db_read, read_schema, logger)
                df_post_corr = safety_stock_df.copy()
                logger.info(f"Sum OUP before: {df_pre_corr['order_upto_point'].sum()}")
                logger.info(f"Sum OUP after: {df_post_corr['order_upto_point'].sum()}")

                corr_drug_lst = compare_df(df_pre_corr, df_post_corr, logger)
                safety_stock_df = add_correction_flag(safety_stock_df, corr_drug_lst, 'DCC')

            # WAREHOUSE GENERIC SKU CONSOLIDATION
            if wh_gen_consolidation == 'Y':
                logger.info("WH Generic Consolidation starts")
                df_pre_corr = safety_stock_df.copy()
                safety_stock_df = wh_consolidation(
                    safety_stock_df, rs_db_read, read_schema, logger)
                df_post_corr = safety_stock_df.copy()
                logger.info(f"Sum OUP before: {df_pre_corr['order_upto_point'].sum()}")
                logger.info(f"Sum OUP after: {df_post_corr['order_upto_point'].sum()}")

                corr_drug_lst = compare_df(df_pre_corr, df_post_corr, logger)
                safety_stock_df = add_correction_flag(safety_stock_df, corr_drug_lst, 'WH')

            # GOODAID SAFETY STOCK MODIFICATION
            if goodaid_ss_flag == 'Y':
                logger.info("GA SS Modification starts")
                df_pre_corr = safety_stock_df.copy()
                safety_stock_df = goodaid_consolidation(
                    safety_stock_df, rs_db_read, read_schema, logger)
                df_post_corr = safety_stock_df.copy()
                logger.info(f"Sum OUP before: {df_pre_corr['order_upto_point'].sum()}")
                logger.info(f"Sum OUP after: {df_post_corr['order_upto_point'].sum()}")

                corr_drug_lst = compare_df(df_pre_corr, df_post_corr, logger)
                safety_stock_df = add_correction_flag(safety_stock_df, corr_drug_lst, 'GA')

            # KEEP ALL GENERIC COMPOSITIONS IN STORE
            if keep_all_generic_comp == 'Y':
                logger.info("All Generic Composition starts")
                df_pre_corr = safety_stock_df.copy()
                safety_stock_df = generic_portfolio(safety_stock_df, rs_db_read,
                                                    read_schema, logger)
                df_post_corr = safety_stock_df.copy()
                logger.info(f"Sum OUP before: {df_pre_corr['order_upto_point'].sum()}")
                logger.info(f"Sum OUP after: {df_post_corr['order_upto_point'].sum()}")

                corr_drug_lst = compare_df(df_pre_corr, df_post_corr, logger)
                safety_stock_df = add_correction_flag(safety_stock_df, corr_drug_lst, 'AG')

            # OMIT NPI DRUGS
            if omit_npi == 'Y':
                logger.info("Omit NPI starts")
                df_pre_corr = safety_stock_df.copy()
                safety_stock_df = omit_npi_drugs(safety_stock_df, store_id,
                                                 reset_date, rs_db_read,
                                                 read_schema, logger)
                df_post_corr = safety_stock_df.copy()
                logger.info(f"Sum OUP before: {df_pre_corr['order_upto_point'].sum()}")
                logger.info(f"Sum OUP after: {df_post_corr['order_upto_point'].sum()}")

                corr_drug_lst = compare_df(df_pre_corr, df_post_corr, logger)
                safety_stock_df = add_correction_flag(safety_stock_df, corr_drug_lst, 'NPI')

            # POST PROCESSING AND ORDER VALUE CALCULATIONS
            logger.info("Post Processing starts")
            safety_stock_df, order_value, weekly_fcst, \
                seg_df = post_processing(safety_stock_df, weekly_fcst, seg_df,
                                         store_id, read_schema, rs_db_read,
                                         logger)
            order_value_all = order_value_all.append(order_value, ignore_index=True)

            # WRITING TO RS-DB
            if debug_mode == 'N':
                logger.info("Writing table to RS-DB")
                # writing table ipc2-weekly-forecast
                weekly_fcst['store_id'] = weekly_fcst['store_id'].astype(int)
                weekly_fcst['drug_id'] = weekly_fcst['drug_id'].astype(int)
                weekly_fcst['reset_date'] = dt.datetime.strptime(reset_date, '%Y-%m-%d').date()
                weekly_fcst['created-at'] = dt.datetime.now(
                    tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
                weekly_fcst['created-by'] = 'etl-automation'
                weekly_fcst['updated-at'] = dt.datetime.now(
                    tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
                weekly_fcst['updated-by'] = 'etl-automation'
                weekly_fcst.columns = [c.replace('_', '-') for c in
                                       weekly_fcst.columns]
                table_info = helper.get_table_info(db=rs_db_write,
                                                   table_name='ipc2-weekly-forecast',
                                                   schema=write_schema)
                columns = list(table_info['column_name'])
                weekly_fcst = weekly_fcst[columns]  # required column order

                logger.info("Writing to table: ipc2-weekly-forecast")
                s3.write_df_to_db(df=weekly_fcst,
                                  table_name='ipc2-weekly-forecast',
                                  db=rs_db_write, schema=write_schema)

                # writing table ipc2-safety-stock
                safety_stock_df['store_id'] = safety_stock_df['store_id'].astype(int)
                safety_stock_df['drug_id'] = safety_stock_df['drug_id'].astype(int)
                safety_stock_df['reset_date'] = dt.datetime.strptime(reset_date, '%Y-%m-%d').date()
                safety_stock_df['created-at'] = dt.datetime.now(
                    tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
                safety_stock_df['created-by'] = 'etl-automation'
                safety_stock_df['updated-at'] = dt.datetime.now(
                    tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
                safety_stock_df['updated-by'] = 'etl-automation'
                safety_stock_df.columns = [c.replace('_', '-') for c in
                                           safety_stock_df.columns]
                table_info = helper.get_table_info(db=rs_db_write,
                                                   table_name='ipc2-safety-stock',
                                                   schema=write_schema)
                columns = list(table_info['column_name'])
                safety_stock_df = safety_stock_df[columns]  # required column order

                logger.info("Writing to table: ipc2-safety-stock")
                s3.write_df_to_db(df=safety_stock_df,
                                  table_name='ipc2-safety-stock',
                                  db=rs_db_write, schema=write_schema)

                # writing table ipc2-segmentation
                seg_df['store_id'] = seg_df['store_id'].astype(int)
                seg_df['drug_id'] = seg_df['drug_id'].astype(int)
                seg_df['reset_date'] = dt.datetime.strptime(reset_date, '%Y-%m-%d').date()
                seg_df['created-at'] = dt.datetime.now(
                    tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
                seg_df['created-by'] = 'etl-automation'
                seg_df['updated-at'] = dt.datetime.now(
                    tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
                seg_df['updated-by'] = 'etl-automation'
                seg_df.columns = [c.replace('_', '-') for c in seg_df.columns]
                table_info = helper.get_table_info(db=rs_db_write,
                                                   table_name='ipc2-segmentation',
                                                   schema=write_schema)
                columns = list(table_info['column_name'])
                seg_df = seg_df[columns]  # required column order

                logger.info("Writing to table: ipc2-segmentation")
                s3.write_df_to_db(df=seg_df,
                                  table_name='ipc2-segmentation',
                                  db=rs_db_write, schema=write_schema)
                logger.info("All writes to RS-DB completed!")

                # OUP OUTLIER CHECK
                if outlier_check == 'Y':
                    logger.info("Outlier detection starts")
                    outlier_drugs, df_outliers, \
                    manual_doid_upd_df = check_oup_outlier(
                        safety_stock_df, store_id, reset_date, rs_db_read,
                        read_schema)
                    df_outliers_all = df_outliers_all.append(df_outliers)
                    manual_doid_upd_all = manual_doid_upd_all.append(manual_doid_upd_df)
                else:
                    outlier_drugs = []

                # UPLOADING MIN, SS, MAX in DOI-D
                logger.info("Updating new SS to DrugOrderInfo-Data")
                safety_stock_df.columns = [c.replace('-', '_') for c in safety_stock_df.columns]
                ss_data_upload = safety_stock_df.loc[
                    (safety_stock_df["order_upto_point"] > 0) &
                    (~safety_stock_df["drug_id"].isin(outlier_drugs))]
                ss_data_upload = ss_data_upload[['store_id', 'drug_id',
                        'safety_stock', 'reorder_point', 'order_upto_point']]
                ss_data_upload.columns = ['store_id', 'drug_id', 'corr_min',
                                          'corr_ss', 'corr_max']
                new_drug_entries_str, missed_entries_str = doid_update(
                    ss_data_upload, type_list, rs_db_write, write_schema,
                    logger)
                new_drug_entries = new_drug_entries.append(new_drug_entries_str)
                missed_entries = missed_entries.append(missed_entries_str)

                # INTERNAL TABLE SCHEDULE UPDATE - OPS ORACLE
                logger.info(f"Rescheduling SID:{store_id} in OPS ORACLE")
                if isinstance(reset_store_ops, pd.DataFrame):
                    content_type = 74
                    object_id = reset_store_ops.loc[
                        reset_store_ops[
                            'store_id'] == store_id, 'object_id'].unique()
                    for obj in object_id:
                        request_body = {"object_id": int(obj),
                                        "content_type": content_type}
                        api_response, _ = django.django_model_execution_log_create_api(
                            request_body)
                        reset_store_ops.loc[
                            reset_store_ops['object_id'] == obj,
                            'api_call_response'] = api_response

            else:
                logger.info("Writing to RS-DB skipped")

        status = 'Success'
        logger.info(f"IPC code execution status: {status}")

    except Exception as error:
        logger.exception(error)
        logger.info(f"IPC code execution status: {status}")

    return status, order_value_all, new_drug_entries, missed_entries,\
           df_outliers_all, manual_doid_upd_all


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="This is ETL script.")
    parser.add_argument('-e', '--env', default="dev", type=str, required=False)
    parser.add_argument('-et', '--email_to',
                        default="vivek.revi@zeno.health,tushar.uike@zeno.health",
                        type=str, required=False)
    parser.add_argument('-d', '--debug_mode', default="N", type=str,
                        required=False)
    parser.add_argument('-exsto', '--exclude_stores',
                        default=[52, 60, 92, 243, 281], nargs='+', type=int,
                        required=False)
    parser.add_argument('-gad', '--goodaid_ss_flag', default="Y", type=str,
                        required=False)
    parser.add_argument('-giw', '--ga_inv_weight', default=0.5, type=float,
                        required=False)
    parser.add_argument('-riw', '--rest_inv_weight', default=0.0, type=float,
                        required=False)
    parser.add_argument('-tiw', '--top_inv_weight', default=1, type=float,
                        required=False)
    parser.add_argument('-dcc', '--d_class_consolidation', default="Y", type=str,
                        required=False)
    parser.add_argument('-wgc', '--wh_gen_consolidation', default="Y", type=str,
                        required=False)
    parser.add_argument('-v4', '--v4_active_flag', default="Y", type=str,
                        required=False)
    parser.add_argument('-v5', '--v5_active_flag', default="N", type=str,
                        required=False)
    parser.add_argument('-v6', '--v6_active_flag', default="N", type=str,
                        required=False)
    parser.add_argument('-v6lst', '--v6_type_list',
                        default=['ethical', 'generic', 'others'], nargs='+',
                        type=str, required=False)
    parser.add_argument('-v6ptr', '--v6_ptr_cut_off', default=400, type=int,
                        required=False)
    parser.add_argument('-rd', '--reset_date', default="YYYY-MM-DD", type=str,
                        required=False)
    parser.add_argument('-rs', '--reset_stores',
                        default=[0], nargs='+', type=int,
                        required=False)
    parser.add_argument('-v3', '--v3_active_flag', default="Y", type=str,
                        required=False)
    parser.add_argument('-v3sp', '--corrections_selling_probability_cutoff',
                        default="{'ma_less_than_2': 0.40, 'ma_more_than_2' : 0.40}",
                        type=str, required=False)
    parser.add_argument('-v3cp', '--corrections_cumulative_probability_cutoff',
                        default="{'ma_less_than_2':0.50,'ma_more_than_2':0.63}",
                        type=str, required=False)
    parser.add_argument('-v4tl', '--drug_type_list_v4',
                        default="{'generic':'{0:[0,0,0], 1:[0,0,1], 2:[0,1,2],3:[1,2,3]}',"
                                "'ethical':'{0:[0,0,0], 1:[0,0,1], 2:[0,1,2],3:[1,2,3]}',"
                                "'others':'{0:[0,0,0], 1:[0,1,2], 2:[0,1,2],3:[1,2,3]}'}",
                        type=str, required=False)
    parser.add_argument('-npi', '--omit_npi', default='Y', type=str,
                        required=False)
    parser.add_argument('-kagc', '--keep_all_generic_comp', default='Y',
                        type=str, required=False)
    parser.add_argument('-oc', '--outlier_check', default='Y',
                        type=str, required=False)

    args, unknown = parser.parse_known_args()

    env = args.env
    os.environ['env'] = env
    email_to = args.email_to
    debug_mode = args.debug_mode

    # JOB EXCLUSIVE PARAMS
    exclude_stores = args.exclude_stores
    goodaid_ss_flag = args.goodaid_ss_flag
    ga_inv_weight = args.ga_inv_weight
    rest_inv_weight = args.rest_inv_weight
    top_inv_weight = args.top_inv_weight
    d_class_consolidation = args.d_class_consolidation
    wh_gen_consolidation = args.wh_gen_consolidation
    v5_active_flag = args.v5_active_flag
    v6_active_flag = args.v6_active_flag
    v6_type_list = args.v6_type_list
    v6_ptr_cut_off = args.v6_ptr_cut_off
    reset_date = args.reset_date
    reset_stores = args.reset_stores
    v3_active_flag = args.v3_active_flag
    v4_active_flag = args.v4_active_flag
    corrections_selling_probability_cutoff = args.corrections_selling_probability_cutoff
    corrections_cumulative_probability_cutoff = args.corrections_cumulative_probability_cutoff
    drug_type_list_v4 = args.drug_type_list_v4
    omit_npi = args.omit_npi
    keep_all_generic_comp = args.keep_all_generic_comp
    outlier_check = args.outlier_check

    # EVALUATE REQUIRED JSON PARAMS
    corrections_selling_probability_cutoff = literal_eval(
        corrections_selling_probability_cutoff)
    corrections_cumulative_probability_cutoff = literal_eval(
        corrections_cumulative_probability_cutoff)
    drug_type_list_v4 = literal_eval(drug_type_list_v4)

    logger = get_logger()
    s3 = S3()
    django = Django()
    rs_db_read = DB(read_only=True)
    rs_db_write = DB(read_only=False)
    read_schema = 'prod2-generico'
    write_schema = 'prod2-generico'

    # open RS connection
    rs_db_read.open_connection()
    rs_db_write.open_connection()

    if reset_date == 'YYYY-MM-DD':  # Take current date
        reset_date = dt.date.today().strftime("%Y-%m-%d")

    if reset_stores == [0]:  # Fetch scheduled IPC stores from OPS ORACLE
        store_query = """
            select "id", name, "opened-at" as opened_at
            from "{read_schema}".stores
            where name <> 'Zippin Central'
            and "is-active" = 1
            and "opened-at" != '0101-01-01 00:00:00'
            and id not in {0}
            """.format(str(exclude_stores).replace('[', '(').replace(']', ')'),
                       read_schema=read_schema)
        stores = rs_db_read.get_df(store_query)
        # only stores aged > 3 months are eligible
        store_id = stores.loc[dt.datetime.now() -
                              stores['opened_at'] >
                              dt.timedelta(days=90), 'id'].values

        # QUERY TO GET SCHEDULED STORES AND TYPE FROM OPS ORACLE
        pg_internal = PostGre(is_internal=True)
        pg_internal.open_connection()
        reset_store_query = """
            SELECT
                "ssr"."id" as object_id,
                "s"."bpos_store_id" as store_id,
                "dc"."slug" as type,
                "ssr"."drug_grade"
            FROM
                "safety_stock_reset_drug_category_mapping" ssr
                INNER JOIN "ops_store_manifest" osm
                ON ( "ssr"."ops_store_manifest_id" = "osm"."id" )
                INNER JOIN "retail_store" s
                ON ( "osm"."store_id" = "s"."id" )
                INNER JOIN "drug_category" dc
                ON ( "ssr"."drug_category_id" = "dc"."id")
            WHERE
                (
                    ( "ssr"."should_run_daily" = TRUE OR
                        "ssr"."trigger_dates" && ARRAY[ date('{reset_date}')] )
                    AND "ssr"."is_auto_generate" = TRUE
                    AND "osm"."is_active" = TRUE
                AND "osm"."is_generate_safety_stock_reset" = TRUE
                AND "dc"."is_safety_stock_reset_enabled" = TRUE
                AND "dc"."is_active" = TRUE
                AND s.bpos_store_id in {store_list}
                )
            """.format(
            store_list=str(list(store_id)).replace('[', '(').replace(']', ')'),
            reset_date=reset_date)
        reset_store_ops = pd.read_sql_query(reset_store_query,
                                            pg_internal.connection)
        pg_internal.close_connection()

        reset_store_ops['api_call_response'] = False
        reset_stores = reset_store_ops['store_id'].unique()
        type_list = None

    else:
        type_list = "('ethical', 'ayurvedic', 'generic', 'discontinued-products', " \
                    "'banned', 'general', 'high-value-ethical', 'baby-product'," \
                    " 'surgical', 'otc', 'glucose-test-kit', 'category-2', " \
                    "'category-1', 'category-4', 'baby-food', '', 'category-3')"
        reset_store_ops = None

    """ calling the main function """
    status, order_value_all, new_drug_entries, missed_entries, \
    df_outliers_all, manual_doid_upd_all = main(
        debug_mode, reset_stores, reset_date, type_list, reset_store_ops,
        v3_active_flag, v4_active_flag, v5_active_flag, v6_active_flag,
        d_class_consolidation, wh_gen_consolidation, goodaid_ss_flag,
        keep_all_generic_comp, omit_npi, ga_inv_weight, rest_inv_weight,
        top_inv_weight, v6_type_list, v6_ptr_cut_off,
        corrections_selling_probability_cutoff,
        corrections_cumulative_probability_cutoff, drug_type_list_v4,
        outlier_check, rs_db_read, rs_db_write, read_schema, write_schema,
        s3, django, logger)

    # close RS connection
    rs_db_read.close_connection()
    rs_db_write.close_connection()

    # save email attachements to s3
    order_value_all_uri = s3.save_df_to_s3(order_value_all,
                                           file_name=f"order_value_all_{reset_date}.csv")
    new_drug_entries_uri = s3.save_df_to_s3(new_drug_entries,
                                            file_name=f"new_drug_entries_{reset_date}.csv")
    missed_entries_uri = s3.save_df_to_s3(missed_entries,
                                          file_name=f"missed_entries_{reset_date}.csv")
    df_outliers_all_uri = s3.save_df_to_s3(df_outliers_all,
                                          file_name=f"df_outliers_all_{reset_date}.csv")
    manual_doid_upd_all_uri = s3.save_df_to_s3(manual_doid_upd_all,
                                          file_name=f"manual_doid_upd_all_{reset_date}.csv")

    # SEND EMAIL ATTACHMENTS (IPC-RUN STATUS)
    logger.info("Sending email attachments..")
    email = Email()
    email.send_email_file(
        subject=f"IPC2.0 SS Reset (SM-{env}) {reset_date}: {status}",
        mail_body=f"""
                Debug Mode: {debug_mode}
                Reset Stores: {reset_stores}
                Job Params: {args}
                """,
        to_emails=email_to, file_uris=[order_value_all_uri,
                                       new_drug_entries_uri,
                                       missed_entries_uri])

    # SEND EMAIL ATTACHMENTS (OUTLIER WARNING)
    outlier_count = df_outliers_all.shape[0]
    if outlier_count > 0:
        outlier_order_qty = df_outliers_all["to_order_quantity"].sum()
        outlier_order_val = round(df_outliers_all["to_order_value"].sum(), 2)
        outlier_stores = list(df_outliers_all["store_id"].unique())
        email.send_email_file(
            subject=f"IPC2.0 OUTLIER WARNING (SM-{env}) {reset_date}: "
                    f"Cases {outlier_count}",
            mail_body=f"""
                        Stores: {outlier_stores}
                        Cases: {outlier_count}
                        Order Quantity: {outlier_order_qty}
                        Order Value: {outlier_order_val}
                        Note: For the detected cases SS, ROP & OUP is set to 0.
                        Please verify and upload attached file using DOID-GLUE JOB.
                        """,
            to_emails=email_to, file_uris=[df_outliers_all_uri,
                                           manual_doid_upd_all_uri])

    logger.info("Script ended")
