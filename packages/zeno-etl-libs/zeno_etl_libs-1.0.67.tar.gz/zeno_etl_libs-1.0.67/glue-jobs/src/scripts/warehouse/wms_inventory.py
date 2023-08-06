# -*- coding: utf-8 -*-
"""
Created on Mon Apr 21 21:45:59 2022

@author: vivek.sidagam@zeno.health

@Purpose: To populate table wh-inventory-ss that takes daily snapshot of warehouse inventory
"""

import os
import sys
import argparse
import pandas as pd
import datetime

sys.path.append('../../../..')

from zeno_etl_libs.db.db import DB, MSSql
from zeno_etl_libs.helper.aws.s3 import S3
from zeno_etl_libs.logger import get_logger
from zeno_etl_libs.helper.email.email import Email
from dateutil.tz import gettz

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Populates table wh-inventory-ss that takes daily snapshot of warehouse inventory.")
    parser.add_argument('-e', '--env', default="dev", type=str, required=False)
    parser.add_argument('-et', '--email_to', default="vivek.sidagam@zeno.health",
                        type=str, required=False)
    args, unknown = parser.parse_known_args()
    env = args.env
    os.environ['env'] = env
    email_to = args.email_to

    err_msg = ''

    logger = get_logger()
    logger.info("Script begins")

    cur_date = datetime.datetime.now(tz=gettz('Asia/Kolkata'))
    status = False

    try:
        # MSSql connection
        mssql = MSSql(connect_via_tunnel=False)
        mssql_connection = mssql.open_connection()
        # RS Connection
        rs_db = DB()
        rs_db.open_connection()
        q1 = """
        select
            199 as wh_id,
            b.code as wms_drug_code,
            b.Barcode as drug_id,
            a2.Altercode as distributor_id,
            a2.Name as distributor_name,
            a.Acno as wms_distributor_code,
            a.Vdt as purchase_date,
            b.name as drug_name,
            a.Srate,
            coalesce(a.TQty, 0) as total_quantity,
            case
                when a.Vno < 0 then 0
                else coalesce(a.bqty, 0)
            end as balance_quantity,
            case
                when a.Vno > 0 then 0
                else coalesce(a.tqty, 0)
            end as locked_quantity,
            coalesce(a.TQty * a.cost, 0) as total_value,
            case
                when a.Vno < 0 then 0
                else coalesce(a.bqty * a.cost, 0)
            end as balance_value,
            case
                when a.Vno > 0 then 0
                else coalesce(a.tqty * a.cost, 0)
            end as locked_value,
            a.Evdt as expiry,
            b.Compname as company_name,
            b.Compcode as company_code,
            b.Pack as pack,
            a.Cost as purchase_rate,
            a.Pbillno as purchase_bill_no,
            a.Psrlno as purchase_serial_no,
            a.Batch as batch_number,
            a.mrp as mrp,
            b.Prate,
            m.name as "drug_type",
            s.name as "composition",
            a.Gdn2 as godown_qty,
            a.BQty - a.Gdn2 as store_qty,
            sp.NetAmt invoice_net_amt,
            sp.Taxamt invoice_tax_amt,
            sp.Disamt invoice_dis_amt,
            sp.qty as invoice_qty,
            sp.cgst,
            sp.sgst,
            sp.igst,
            a.vno,
            b.MinQty as shelf_min,
            b.MaxQty as shelf_max
        from
            fifo a
        right join item b on
            a.itemc = b.code
        left join Acm a2 on
            a2.code = a.Acno
            and a2.Slcd in ('SL', 'GL')
        left join Master m on
            b.ItemCat = m.code
        left join Salt s on
            b.Saltcode = s.Code
        left join SalePurchase2 sp on
            a.Pbillno = sp.Pbillno
            and a.Psrlno = sp.Psrlno
            and a.Itemc = sp.Itemc
            and sp.Vdt = a.Vdt
        where
            b.code > 0
            and a.Psrlno in (
            select
                Psrlno
            from
                SalePurchase2)
            and b.Barcode not like '%[^0-9]%'
        """
        logger.info("getting data from esdata1 tables")
        bhw = pd.read_sql(q1, mssql_connection)
        logger.info("Data pulled from esdata1 tables")

        # MSSql2 connection
        mssql2 = MSSql(connect_via_tunnel=False, db='Esdata_WS_2')
        mssql2_connection = mssql2.open_connection()
        q2 = """
        select
            343 as wh_id,
            b.code as wms_drug_code,
            b.Barcode as drug_id,
            a2.Altercode as distributor_id,
            a2.Name as distributor_name,
            a.Acno as wms_distributor_code,
            a.Vdt as purchase_date,
            b.name as drug_name,
            a.Srate,
            coalesce(a.TQty, 0) as total_quantity,
            case
                when a.Vno < 0 then 0
                else coalesce(a.bqty, 0)
            end as balance_quantity,
            case
                when a.Vno > 0 then 0
                else coalesce(a.tqty, 0)
            end as locked_quantity,
            coalesce(a.TQty * a.cost, 0) as total_value,
            case
                when a.Vno < 0 then 0
                else coalesce(a.bqty * a.cost, 0)
            end as balance_value,
            case
                when a.Vno > 0 then 0
                else coalesce(a.tqty * a.cost, 0)
            end as locked_value,
            a.Evdt as expiry,
            b.Compname as company_name,
            b.Compcode as company_code,
            b.Pack as pack,
            a.Cost as purchase_rate,
            a.Pbillno as purchase_bill_no,
            a.Psrlno as purchase_serial_no,
            a.Batch as batch_number,
            a.mrp as mrp,
            b.Prate,
            m.name as "drug_type",
            s.name as "composition",
            a.Gdn2 as godown_qty,
            a.BQty - a.Gdn2 as store_qty,
            sp.NetAmt invoice_net_amt,
            sp.Taxamt invoice_tax_amt,
            sp.Disamt invoice_dis_amt,
            sp.qty as invoice_qty,
            sp.cgst,
            sp.sgst,
            sp.igst,
            a.vno,
            b.MinQty as shelf_min,
            b.MaxQty as shelf_max
        from
            fifo a
        right join item b on
            a.itemc = b.code
        left join Acm a2 on
            a2.code = a.Acno
            and a2.Slcd in ('SL', 'GL')
        left join Master m on
            b.ItemCat = m.code
        left join Salt s on
            b.Saltcode = s.Code
        left join SalePurchase2 sp on
            a.Pbillno = sp.Pbillno
            and a.Psrlno = sp.Psrlno
            and a.Itemc = sp.Itemc
            and sp.Vdt = a.Vdt
        where
            b.code > 0
            and a.Psrlno in (
            select
                Psrlno
            from
                SalePurchase2)
            and b.Barcode not like '%[^0-9]%'
        """
        logger.info("getting data from esdata2 tables")
        gaw = pd.read_sql(q2, mssql2_connection)
        logger.info("Data pulled from esdata2 tables")

        df1 = pd.concat([bhw, gaw])

        # getting safety stock data
        doi_query = """
        select
            "store-id" as "wh_id",
            "drug-id" as "drug_id",
            "safe-stock" as "reorder_point",
            min as "safety_stock",
            max as "order_upto_point",
            'NA' as bucket,
            'NA' as history_bucket,
            'NA' as category
        from
            "prod2-generico"."drug-order-info" doi
        where
            "store-id" in (199, 343)
            -- and max > 0
        """
        logger.info("Getting data from RS")
        doi_data = rs_db.get_df(doi_query)
        logger.info("Data pulled from RS")
        # doi_data.columns = doi_data.columns.str.decode("utf-8")
        doi_data.columns = [c.replace('-', '_') for c in doi_data.columns]

        wh_portfolio_query = """
            select
                "drug-id"
            from
                "prod2-generico"."wh-sku-subs-master" wssm
            left join "prod2-generico".drugs d on
                wssm."drug-id" = d.id
            where
                wssm."add-wh" = 'Yes'
                and d."type" not in ('discontinued-products', 'banned')
        """
        wh_portfolio = rs_db.get_df(wh_portfolio_query)
        wh_portfolio.columns = [c.replace('-', '_') for c in wh_portfolio.columns]
        wh_portfolio["in_wh_portfolio"] = 1

        # merging two data sets
        doi_data['drug_id'] = doi_data['drug_id'].astype(str)
        wh_inventory = df1.merge(doi_data, on=['drug_id', 'wh_id'], how='left')
        wh_inventory['bucket'].fillna('NA', inplace=True)
        wh_inventory['history_bucket'].fillna('NA', inplace=True)
        wh_inventory['category'].fillna('NA', inplace=True)
        wh_inventory['safety_stock'].fillna(0, inplace=True)
        wh_inventory['reorder_point'].fillna(0, inplace=True)
        wh_inventory['order_upto_point'].fillna(0, inplace=True)
        wh_inventory['shelf_min'].fillna(0, inplace=True)
        wh_inventory['shelf_max'].fillna(0, inplace=True)
        wh_inventory['invoice_qty'].fillna(0, inplace=True)
        wh_inventory['snapshot_date'] = cur_date.strftime("%Y-%m-%d %H:%M:%S")
        wh_inventory['created-at'] = datetime.datetime.now(tz=gettz('Asia/Kolkata')).strftime(
            "%Y-%m-%d %H:%M:%S")
        wh_inventory['created-by'] = 'etl-automation'
        wh_inventory['updated-by'] = 'etl-automation'
        wh_inventory['updated-at'] = datetime.datetime.now(tz=gettz('Asia/Kolkata')).strftime(
            "%Y-%m-%d %H:%M:%S")

        # Writing data
        wh_inventory['safety_stock'] = wh_inventory['safety_stock'].astype(int)
        wh_inventory['reorder_point'] = wh_inventory['reorder_point'].astype(int)
        wh_inventory['order_upto_point'] = wh_inventory['order_upto_point'].astype(int)
        wh_inventory['total_quantity'] = wh_inventory['total_quantity'].astype(int)
        wh_inventory['balance_quantity'] = wh_inventory['balance_quantity'].astype(int)
        wh_inventory['locked_quantity'] = wh_inventory['locked_quantity'].astype(int)
        wh_inventory['godown_qty'] = wh_inventory['godown_qty'].astype(int)
        wh_inventory['store_qty'] = wh_inventory['store_qty'].astype(int)
        wh_inventory['invoice_qty'] = wh_inventory['invoice_qty'].astype(int)
        wh_inventory['drug_id'] = wh_inventory['drug_id'].astype(int)
        wh_inventory = wh_inventory.merge(wh_portfolio, on="drug_id", how='left')
        wh_inventory['in_wh_portfolio'] = wh_inventory['in_wh_portfolio'].fillna(0).astype(int)
        wh_inventory.columns = [c.replace('_', '-') for c in wh_inventory.columns]
        wh_inventory = wh_inventory[
            ['wms-drug-code', 'drug-id', 'distributor-id', 'distributor-name',
             'wms-distributor-code', 'purchase-date', 'drug-name', 'Srate',
             'total-quantity', 'balance-quantity', 'locked-quantity', 'total-value',
             'balance-value', 'locked-value', 'expiry', 'company-name',
             'company-code', 'pack', 'purchase-rate', 'purchase-bill-no',
             'purchase-serial-no', 'batch-number', 'mrp', 'Prate', 'drug-type',
             'composition', 'bucket', 'history-bucket', 'category', 'safety-stock',
             'reorder-point', 'order-upto-point', 'shelf-min', 'shelf-max',
             'snapshot-date', 'godown-qty', 'store-qty', 'invoice-net-amt',
             'invoice-tax-amt', 'invoice-dis-amt', 'invoice-qty', 'cgst', 'sgst',
             'igst', 'vno', 'created-at', 'created-by', 'updated-at', 'updated-by', 'in-wh-portfolio', 'wh-id']]

        s3 = S3()
        logger.info("Writing data to wh-inventory-ss")
        rs_db_write = DB(read_only=False)
        rs_db_write.open_connection()
        s3.write_df_to_db(df=wh_inventory, table_name='wh-inventory-ss',
                          db=rs_db_write, schema='prod2-generico')
        logger.info("wh-inventory-ss table updated")
        rs_db.close_connection()
        rs_db_write.close_connection()
        status = True

    except Exception as e:
        err_msg = str(e)
        logger.info('wms_inventory job failed')
        logger.exception(e)

    # Sending email
    email = Email()
    if status:
        result = 'Success'
        email.send_email_file(subject=f"wms_inventory ({env}): {result}",
                              mail_body=f"Run time: {cur_date}",
                              to_emails=email_to, file_uris=[])
    else:
        result = 'Failed'
        email.send_email_file(subject=f"wms_inventory ({env}): {result}",
                              mail_body=f"Run time: {cur_date}  {err_msg}",
                              to_emails=email_to, file_uris=[])

    logger.info("Script ended")
