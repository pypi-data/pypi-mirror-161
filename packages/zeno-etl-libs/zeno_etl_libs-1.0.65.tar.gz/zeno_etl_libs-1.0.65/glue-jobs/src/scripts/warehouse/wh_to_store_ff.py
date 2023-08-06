# -*- coding: utf-8 -*-
"""
Created on Mon Apr 21 21:45:59 2022

@author: vivek.sidagam@zeno.health

@Purpose: To update wh_to_store_ff table
"""

import os
import sys
import argparse
import pandas as pd
from datetime import datetime, timedelta
from dateutil.tz import gettz

sys.path.append('../../../..')

from zeno_etl_libs.db.db import DB, MSSql
from zeno_etl_libs.helper.aws.s3 import S3
from zeno_etl_libs.logger import get_logger
from zeno_etl_libs.helper.email.email import Email

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="To update wh_to_store_ff table.")
    parser.add_argument('-e', '--env', default="dev", type=str, required=False)
    parser.add_argument('-et', '--email_to', default="vivek.sidagam@zeno.health", type=str, required=False)

    args, unknown = parser.parse_known_args()

    env = args.env
    os.environ['env'] = env
    email_to = args.email_to

    logger = get_logger()
    logger.info("Scripts begins")

    status = False
    schema = 'prod2-generico'
    err_msg = ''

    # getting run date for the script
    run_date = datetime.now(tz=gettz('Asia/Kolkata')).strftime("%Y-%m-%d %H:%M:%S")

    try:
        mssql = MSSql(connect_via_tunnel=False)
        mssql_connection = mssql.open_connection()
        q = """
        select
            a.adnlordno,
            a.qty as [ordered_quantity],
            case
                when OrderDt is null then null else CONVERT(DATETIME, concat(CONVERT(date, OrderDt), ' ', a.mTime), 0)
            end as [wms_ordered_at],
            case
                when S2.VDT is null then null else CONVERT(DATETIME, concat(CONVERT(date, S2.VDT), ' ', s1.mTime), 0)
            end as [wms_invoiced_at],
            case
                when ds.FinalDate is null then null else CONVERT(DATETIME, concat(CONVERT(date, ds.FinalDate), ' ', ds.FinalTime), 0)
            end as [wms_dispatched_at],
            a.itemc,
            a.ordno,
            S1.gstVno AS [invoice_number],
            BTM.Name AS [wms_invoice_status],
            CONVERT(INT, A1.ALTERCODE) AS [store_id],
            ap.picktime,
            A1.NAME AS [wms_store_name],
            CONVERT(INT, I.BARCODE) AS [drug_id],
            I.NAME AS [wms_drug_name],
            '' as [batch_no],
            -- S2.BATCH AS [batch_no],
            CONVERT(DECIMAL(18, 0), S2.QTY) AS [wms_qty], 
            CONVERT(DECIMAL(18, 0), S2.FQTY) AS [wms_free_qty],
            CASE
                WHEN CONVERT(DECIMAL(18, 0), (S2.QTY + S2.FQTY))>a.qty THEN a.qty
                ELSE CONVERT(DECIMAL(18, 0), (S2.QTY + S2.FQTY))
            END AS [wms_actual_qty],
            (S2.NETAMT + (S2.IGSTAmt + S2.CGSTAmt + S2.SGSTAmt)) AS [wms_net_value],
            (S2.IGSTAmt + S2.CGSTAmt + S2.SGSTAmt) AS [wms_net_value_tax],
            s1.uid as [checker_name],
            mst.name as [picker_name],
            mr.name as [route],
            case
                when S1.Acno = 59353 then 'npi'
                else 'non_npi'
            end as npi_drug,
            I.Location as rack_location,
            CASE
                when I.Location >= 11001011 and I.Location <= 11306041 then 'npi_rack'
                else 'non_npi_rack'
            end as npi_rack
        from
            (
            select
                *
            from
                PorderUPD
          union
            select
                *
            from
                Porder) a
          left join ProofSp2 b on
            b.Itemc = a.itemc
            and b.Ordno = a.Ordno
            and b.Vdt = a.PurVdt 
            and b.Vtype = a.PurVtype 
          left join ProofSp1 c on
            b.Vno = c.vno
            and b.Vtype = c.Vtype 
            and b.Vdt = c.Vdt  
          left join (
            select
                Vno,
                Vdt,
                Vtype,
                Itemc,
                acno,
                slcd,
                area,
                max(Psrlno) as [Psrlno],
                sum(Qty) as [Qty],
                sum(fqty) as [fqty],
                sum(NetAmt) as [NetAmt],
                sum(IGSTAmt) as [IGSTAmt],
                sum(CGSTAmt) as [CGSTAmt],
                sum(SGSTAmt) as [SGSTAmt]
            from
                SalePurchase2
            group by
                Vno,
                Vdt,
                Vtype,
                Itemc,
                acno,
                slcd,
                area ) as s2 on
            s2.vno = c.RefVno
            and s2.Itemc = a.itemc
            and s2.Vtype = c.RefVtype 
            and s2.Vdt = c.RefVdt 
          left join SalePurchase1 S1 on
            c.RefVno = S1.Vno and
            c.acno = S1.Acno and 
            c.RefVdt = S1.Vdt 
          left JOIN ACM A1 ON
            a.ACNO = A1.CODE
            -- AND S2.SLCD = A.SLCD
          left join (
            select
                vno,
                vdt,
                vtype,
                itemc,
                max(PickTime) as PickTime,
                max(PickerID) as PickerID
            from
                App_SP2
            group by 
                vno,
                vdt,
                vtype,
                itemc
          union
            select
                vno,
                vdt,
                vtype,
                itemc,
                max(PickTime) as PickTime,
                max(PickerID) as PickerID
            from
                App_SP2Upd 
            group by 
                vno,
                vdt,
                vtype,
                itemc
            ) ap on
            ap.vno = c.Vno
            and ap.vdt = c.Vdt
            and ap.Vtype = c.Vtype
            and AP.itemc = a.Itemc
          left join DispatchStmt ds on
            ds.Vdt = s2.Vdt
            and ds.Vno = s2.Vno
            and ds.Vtype = s2.Vtype
          LEFT JOIN MASTER M ON
            S2.AREA = M.CODE
            AND M.SLCD = 'AR'
          LEFT JOIN ACMEXTRA AE ON
            A1.CODE = AE.CODE
            AND A1.SLCD = AE.SLCD
          left JOIN Item I ON
            a.ITEMC = I.CODE
          left JOIN COMPANY C1 ON
            I.COMPCODE = C1.CODE
            --    left JOIN
            -- FIFO F ON S2.PSRLNO = F.PSRLNO
          LEFT JOIN MASTER CC ON
            CC.CODE = AE.CUSTCAT
            AND CC.SLCD = 'CC'
          LEFT JOIN BillTrackMst BTM ON
            S1.SyncTag = BTM.Srl
          left join (
            select
                code,
                name
            from
                MASTER
            where
                slcd = 'SM') as mst on
            mst.code = ap.PickerID
          left join MASTER mr on mr.code = a1.route
        WHERE
            OrderDt >= cast(DATEADD(month, -1, GETDATE()) - day(GETDATE()) + 1 as date)
            and AdnlOrdNo is not null
            and isnumeric(I.BARCODE) = 1
        """
        df = pd.read_sql(q, mssql_connection)
        df['sbid'] = df['adnlordno'].str[-8:].astype(int)
        sbid = tuple(df['sbid'])

        rs_db_read = DB()
        rs_db_read.open_connection()
        q2 = """
        select 
            id as sbid, 
            case
                when "auto-short" = 1 then 'as/ms'
                else 'pr'
            end as order_type 
        from 
            "prod2-generico"."short-book-1" 
        where 
            id in {}
        """.format(sbid)
        as_pr = rs_db_read.get_df(q2)

        df = df.merge(as_pr, on='sbid', how='left')

        q3 = """
        select
                id as drug_id,
                type,
                case
                    when company = 'GOODAID' then 'goodaid'
                    when "type" = 'ethical' then 'ethical'
                    when "type" = 'generic' then 'generic'
                    else 'other'
                end as sub_type
            from
                "prod2-generico".drugs
        """
        drugs = rs_db_read.get_df(q3)

        q4 = """
        select
            id as store_id,
            case
                when "franchisee-id" = 1 then 'coco'
                else 'fofo'
            end as store_type
        from
            "prod2-generico"."stores-master" sm
        """
        stores = rs_db_read.get_df(q4)
        df = df.merge(stores, on='store_id', how='left')
        df['run_time'] = run_date
        rs_db_write = DB(read_only=False)
        rs_db_write.open_connection()
        s3 = S3()
        logger.info('truncating table wh-to-store-ff')
        rs_db_write.execute("""delete from "prod2-generico"."wh-to-store-ff" """)
        logger.info('wh-to-store-ff table truncated')
        logger.info('writing data tp table wh-to-store-ff')
        s3.write_df_to_db(df, 'wh-to-store-ff', rs_db_write, schema=schema)
        logger.info('wh-to-store-ff table refreshed')
        status = True

    except Exception as error:
        err_msg = str(error)
        logger.exception(str(error))

    email = Email()
    if not status:
        result = 'Failed'
        email.send_email_file(subject=f"wh_to_store_ff ({env}): {result}",
                              mail_body=f"Run time: {datetime.now()} {err_msg}",
                              to_emails=email_to, file_uris=[])

    logger.info("Script ended")
