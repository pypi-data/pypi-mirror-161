# -*- coding: utf-8 -*-
"""
Created on Mon Apr 21 21:45:59 2022

@author: vivek.sidagam@zeno.health

@Purpose: To generate replenishment figures for Warehouse as part of wh_forecast_reset code
"""

import numpy as np
import pandas as pd
from calendar import monthrange
from dateutil.relativedelta import relativedelta

from zeno_etl_libs.db.db import MSSql
from zeno_etl_libs.helper.aws.s3 import S3
from zeno_etl_libs.utils.warehouse.data_prep.wh_data_prep import get_launch_stock_per_store


def lead_time():
    mssql = MSSql(connect_via_tunnel=False)
    cnxn = mssql.open_connection()
    cursor = cnxn.cursor()

    # Reading lead time data
    # Last 90 days
    # excluding TEPL distributor
    # Diff between PO created date and Purchase confirm date

    sql = '''
            SELECT
            CAST(i.Barcode as int) as "drug_id" ,
            i.name as "drug_name",
            a.Altercode as "distributor_id",
            a.Name as "distributor_name",
            --sp.Vdt as "purchase_date",
            --sp.RefVdt as "po_opend_date",
            --s.PBillDt as "po_created_date",
            --s.UpdatedOn as "purchase_confirm_date",
            sp.Qty as "quantity" ,
            DATEDIFF(day, s.PBillDt , s.UpdatedOn) as "lead_time"
            FROM
            SalePurchase2 sp
            left join Item i on
            sp.Itemc = i.code
            left join Salepurchase1 s on
            sp.Vtype = s.Vtyp
            and sp.Vno = s.Vno
            and sp.Vdt = s.Vdt
            left join acm a on
            sp.Acno = a.code
            Where
            sp.Vtype = 'PB'
            and sp.Vdt >= cast(DATEADD(day, -90, GETDATE()) as date)
            and i.Compname NOT IN ('GOODAID', 'PURE & C')
            and i.Barcode NOT LIKE '%[^0-9]%' and isnumeric(i.Barcode) = 1
            and a.code NOT IN  (59468,59489)
    '''

    data = pd.read_sql(sql, cnxn)

    # Reading Preferred distributor from S3
    s3 = S3()
    preferred_distributor = pd.read_csv(s3.download_file_from_s3(file_name="warehouse/preferred_distributors.csv"))

    df_new = pd.merge(data, preferred_distributor, how='left', on='drug_id')

    df_new[["lead_time", "distributor_1"]] = df_new[["lead_time", "distributor_1"]].fillna(0)

    df_new[["distributor_1"]] = df_new[["distributor_1"]].astype('int')

    # function for weighted mean
    def w_avg(df, values, weights):
        d = df[values]
        w = df[weights]
        return (d * w).sum() / w.sum()

    df_new_1 = df_new.groupby(["drug_id", "distributor_id"]).apply(w_avg, 'lead_time', 'quantity').rename(
        'weighted_lead_time').reset_index()
    df_std = df_new.groupby(["drug_id", "distributor_id"])[["lead_time"]].std().reset_index()
    df_std.rename(columns={'lead_time': 'lead_time_std'}, inplace=True)
    df_drug_distributor = pd.merge(df_new_1, df_std, how='left', on=['drug_id', 'distributor_id'])
    df_drug_distributor = pd.merge(df_drug_distributor, preferred_distributor, how='left', on=["drug_id"])
    df_drug_distributor[["distributor_1", "lead_time_std"]] = df_drug_distributor[
        ["distributor_1", "lead_time_std"]].fillna(0)
    df_drug_distributor[["distributor_1"]] = df_drug_distributor[["distributor_1"]].astype('int')
    # lead time mean Capping 7 days.
    df_drug_distributor['weighted_lead_time'] = np.where(df_drug_distributor['weighted_lead_time'] > 7, 7,
                                                         df_drug_distributor['weighted_lead_time'])
    # minimum lead time 2 days
    df_drug_distributor['weighted_lead_time'] = np.where(df_drug_distributor['weighted_lead_time'] < 2, 2,
                                                         df_drug_distributor['weighted_lead_time'])
    # Lead time Std  capping of 2 days
    df_drug_distributor['lead_time_std'] = np.where(df_drug_distributor['lead_time_std'] > 2, 2,
                                                    df_drug_distributor['lead_time_std'])
    # Minimum Lead time std is 1 day
    df_drug_distributor['lead_time_std'] = np.where(df_drug_distributor['lead_time_std'] < 1, 1,
                                                    df_drug_distributor['lead_time_std'])
    df_drug_distributor[["distributor_id"]] = df_drug_distributor[["distributor_id"]].astype('int')
    df_drug_distributor['same_distributor'] = np.where(
        df_drug_distributor['distributor_id'] == df_drug_distributor["distributor_1"], True, False)
    preferred_distributor_drug = df_drug_distributor[df_drug_distributor["same_distributor"] == True]
    other_distributor_drug = df_drug_distributor[df_drug_distributor["same_distributor"] == False]

    # Drugs not in preferred distributor
    drugs_not_in_preferred_distributor = df_drug_distributor[
        ~df_drug_distributor['drug_id'].isin(preferred_distributor_drug['drug_id'])]
    drugs_not_in_preferred_distributor_mean = drugs_not_in_preferred_distributor.groupby(["drug_id"])[
        ["weighted_lead_time"]].mean().reset_index()
    drugs_not_in_preferred_distributor_std = drugs_not_in_preferred_distributor.groupby(["drug_id"])[
        ["weighted_lead_time"]].std().reset_index()
    drugs_not_in_preferred_distributor_1 = pd.merge(drugs_not_in_preferred_distributor_mean,
                                                    drugs_not_in_preferred_distributor_std, how='left', on='drug_id')
    drugs_not_in_preferred_distributor_1 = drugs_not_in_preferred_distributor_1.fillna(0)

    # Capping
    drugs_not_in_preferred_distributor_1['weighted_lead_time_x'] = np.where(
        drugs_not_in_preferred_distributor_1['weighted_lead_time_x'] > 7, 7,
        drugs_not_in_preferred_distributor_1['weighted_lead_time_x'])
    drugs_not_in_preferred_distributor_1['weighted_lead_time_x'] = np.where(
        drugs_not_in_preferred_distributor_1['weighted_lead_time_x'] < 2, 2,
        drugs_not_in_preferred_distributor_1['weighted_lead_time_x'])
    drugs_not_in_preferred_distributor_1['weighted_lead_time_y'] = np.where(
        drugs_not_in_preferred_distributor_1['weighted_lead_time_y'] > 2, 2,
        drugs_not_in_preferred_distributor_1['weighted_lead_time_y'])
    drugs_not_in_preferred_distributor_1['weighted_lead_time_y'] = np.where(
        drugs_not_in_preferred_distributor_1['weighted_lead_time_y'] < 1, 1,
        drugs_not_in_preferred_distributor_1['weighted_lead_time_y'])
    drugs_not_in_preferred_distributor_1.rename(
        columns={'weighted_lead_time_x': 'weighted_lead_time', 'weighted_lead_time_y': 'lead_time_std'}, inplace=True)
    drug_in_preferred_distributor = preferred_distributor_drug.drop(
        ['drug_name', 'distributor_id', 'distributor_1', 'distributor_name_1', 'same_distributor'], axis=1)
    drug_lead_time_std = pd.concat([drug_in_preferred_distributor, drugs_not_in_preferred_distributor_1], sort=False,
                                   ignore_index=True)
    weighted_lead_time_mean = drug_lead_time_std[["drug_id", "weighted_lead_time"]]
    weighted_lead_time_std = drug_lead_time_std[["drug_id", "lead_time_std"]]

    return weighted_lead_time_mean, weighted_lead_time_std


def review_time():
    # Review Time for distributor
    s3 = S3()
    df_1 = pd.read_csv(s3.download_file_from_s3(file_name="warehouse/review_time_warehouse_distributor.csv"))

    # Preferred distributor
    df_2 = pd.read_csv(s3.download_file_from_s3(file_name="warehouse/preferred_distributors.csv"))

    # If null then take 4 days of review time

    df_1 = df_1.fillna(4)

    df_1['review_time'] = df_1['review_time'].astype('int')
    review_time_new = pd.merge(df_2, df_1, left_on='distributor_1', right_on='distributor_id', how='left')
    review_time_new = review_time_new.drop(
        ["drug_name", "distributor_1", "distributor_name_1", "distributor_id", "distributor_name"], axis=1)
    return review_time_new


def wh_safety_stock_calc(
        ss_runtime_var, wh_drug_list, forecast, last_month_sales, demand_daily_deviation, current_month_date,
        forecast_date, reset_date, logger=None, expected_nso=0, nso_history_days=90, rs_db=None):
    """ Safety stock calculation for warehouse """
    # Lead time mean & Std
    lead_time_mean, lead_time_std = lead_time()
    service_level = ss_runtime_var['service_level']  # 0.95
    ordering_freq = ss_runtime_var['ordering_freq']  # 4
    max_review_period = review_time()
    z = ss_runtime_var['z']
    cap_ss_days = ss_runtime_var['cap_ss_days']
    if cap_ss_days == 0:
        cap_ss_days = 100000

    # getting latest month forecast
    forecast['month_begin_dt'] = pd.to_datetime(
        forecast['month_begin_dt']).dt.date
    first_month = forecast['month_begin_dt'].min()
    forecast_first_month = forecast[forecast['month_begin_dt'] == first_month]

    # creating inventory level dataframe
    repln = forecast_first_month.copy()

    repln = pd.merge(repln, lead_time_mean, how='left', on='drug_id')  # merge lead time mean
    repln = pd.merge(repln, lead_time_std, how='left', on='drug_id')  # merge lead time std
    repln = pd.merge(repln, max_review_period, how='left', on='drug_id')  # merge review time
    # rename the columns
    repln.rename(columns={'weighted_lead_time': 'lead_time_mean', 'review_time': 'max_review_period'}, inplace=True)

    # Use default of 4 , 2 and 4 lead time mean , std and r.t if data is missing
    repln['lead_time_mean'] = repln['lead_time_mean'].fillna(4)
    repln['lead_time_std'] = repln['lead_time_std'].fillna(2)

    repln['max_review_period'] = repln['max_review_period'].fillna(4)
    repln['ordering_freq'] = ordering_freq
    repln['service_level'] = service_level
    repln['z_value'] = z
    repln = wh_drug_list.merge(repln, on='drug_id')
    num_days = monthrange(first_month.year, first_month.month)[1]
    repln['demand_daily'] = repln['fcst'] / num_days

    # check to see if forecast error is to be used instead of actual demand daily deviation
    if ss_runtime_var['use_fcst_error'] == 'Y':
        hist_fcst_err = get_forecast_error(rs_db, ss_runtime_var['fcst_hist_to_use'], last_month_sales,
                                           current_month_date, forecast_date, num_days)
        hist_fcst_err['demand_daily_deviation'] = hist_fcst_err['demand_daily_deviation'] / np.sqrt(num_days)
        repln = repln.merge(hist_fcst_err, on='drug_id', how='left')
        print("used forecast error instead of demand deviation")
    else:
        repln = repln.merge(demand_daily_deviation, on='drug_id', how='left')

    repln['demand_daily_deviation'].fillna(0, inplace=True)
    # warehouse overall safety stock
    repln['ss_wo_cap'] = np.round(repln['z_value'] * np.sqrt(
        (
                repln['lead_time_mean'] *
                repln['demand_daily_deviation'] *
                repln['demand_daily_deviation']
        ) +
        (
                repln['lead_time_std'] *
                repln['lead_time_std'] *
                repln['demand_daily'] *
                repln['demand_daily']
        )))
    repln = repln.merge(last_month_sales, on='drug_id', how='left')
    repln['safety_stock_days'] = np.round(
        repln['ss_wo_cap'] * num_days / repln['fcst'], 1)
    # calculate capping days
    repln['cap_ss_days'] = np.round(repln['lead_time_mean'] +
                                    repln['z_value'] * repln['lead_time_std'] +
                                    repln['max_review_period'])
    repln['cap_ss_days'] = np.where(repln['cap_ss_days'] > cap_ss_days, cap_ss_days, repln['cap_ss_days'])
    # capping SS days based in forecasted sales
    repln['safety_stock'] = np.where(repln['safety_stock_days'] > repln['cap_ss_days'],
                                     np.round(repln['cap_ss_days'] * repln['fcst'] / num_days),
                                     repln['ss_wo_cap'])
    # setting min SS at 2 days based on forecasted sales
    repln['safety_stock'] = np.where(repln['safety_stock_days'] < 2, np.round(2 * repln['fcst'] / num_days),
                                     repln['safety_stock'])
    # capping SS days based on last month's sales
    repln['safety_stock'] = np.where(repln['safety_stock'] * num_days / repln['last_month_sales'] > cap_ss_days,
                                     np.round(cap_ss_days * repln['last_month_sales'] / num_days),
                                     repln['safety_stock'])
    repln['rop_without_nso'] = np.round(repln['safety_stock'] + repln['demand_daily'] * (repln['lead_time_mean'] +
                                                                                         repln['max_review_period']))

    # tweaking ROP to include launch stock
    launch_stock_per_store = get_launch_stock_per_store(rs_db, nso_history_days, reset_date)
    repln = repln.merge(launch_stock_per_store, on='drug_id', how='left')
    repln['launch_stock_per_store'].fillna(0, inplace=True)
    repln['expected_nso'] = expected_nso
    repln['reorder_point'] = repln['rop_without_nso'] + \
                             np.round((repln['lead_time_mean'] + repln['max_review_period']) *
                             repln['expected_nso'] / num_days) * \
                             repln['launch_stock_per_store']
    repln['reorder_point'] = np.round(repln['reorder_point'])

    repln['oup_without_nso'] = np.round(
        repln['rop_without_nso'] +
        repln['demand_daily'] * repln['ordering_freq'])
    repln['order_upto_point'] = np.round(
        repln['reorder_point'] +
        repln['demand_daily'] * repln['ordering_freq'])

    # shelf safety stock
    repln['shelf_min'] = np.round(repln['safety_stock'] / 2)
    repln['shelf_max'] = repln['safety_stock']

    # days of safety stock, reorder point and order upto point calculations
    repln['last_month_sales'].fillna(0, inplace=True)
    repln['safety_stock_days'] = np.round(
        repln['safety_stock'] * num_days / repln['last_month_sales'], 1)
    repln['reorder_point_days'] = np.round(
        repln['reorder_point'] * num_days / repln['last_month_sales'], 1)
    repln['order_upto_days'] = np.round(
        repln['order_upto_point'] * num_days / repln['last_month_sales'], 1)

    return repln


def get_forecast_error(rs_db, fcst_hist_to_use, last_month_sales, current_month_date, forecast_date, num_days):
    first_forecast_month = str(current_month_date - relativedelta(months=fcst_hist_to_use))
    q = """
        select
            wss."drug-id" as drug_id,
            wss."month-begin-dt" as month_forecasted,
            wss."fcst" as forecast,
            (
                select
                    wss1."last-month-sales"
                from
                    "prod2-generico"."wh-safety-stock" wss1
                where
                    wss."drug-id" = wss1."drug-id"
                    and date(add_months(wss."month-begin-dt",
                    1))= wss1."month-begin-dt"
                order by
                    wss1."drug-id",
                    wss1."month-begin-dt"
                limit 1
            ) as actual
        from
                "prod2-generico"."wh-safety-stock" wss
        where
            1 = 1
            and wss.fcst notnull
            and wss."month-begin-dt" >= '{}'
            and wss."month-begin-dt" >= '2022-02-01'
        order by
            wss."drug-id",
            wss."month-begin-dt"
    """.format(first_forecast_month)
    hist_fcst_err = rs_db.get_df(q)
    last_month_date = pd.to_datetime(forecast_date) - relativedelta(months=1)
    last_month_sales['last_month_date'] = last_month_date.date()
    hist_fcst_err = hist_fcst_err.merge(last_month_sales, left_on=['drug_id', 'month_forecasted'],
                                        right_on=['drug_id', 'last_month_date'], how='left')
    hist_fcst_err['actual'] = np.where(np.isnan(hist_fcst_err['actual']), hist_fcst_err['last_month_sales'],
                                       hist_fcst_err['actual'])
    hist_fcst_err.drop(columns=['last_month_sales', 'last_month_date'], inplace=True)
    hist_fcst_err = hist_fcst_err[np.isnan(hist_fcst_err['actual']) == False]
    hist_fcst_err['squared_error'] = (hist_fcst_err['forecast'] - hist_fcst_err['actual']) ** 2
    hist_fcst_err = hist_fcst_err.groupby('drug_id').apply(get_rmse).reset_index()
    hist_fcst_err['demand_daily_deviation'] = hist_fcst_err['rmse'] / np.sqrt(num_days)
    return hist_fcst_err[['drug_id', 'demand_daily_deviation']]


def get_rmse(df):
    if len(df) >= 2:
        rmse = np.sqrt(df['squared_error'].sum() / len(df))
    else:
        rmse = None
    return pd.Series(dict(rmse=rmse))