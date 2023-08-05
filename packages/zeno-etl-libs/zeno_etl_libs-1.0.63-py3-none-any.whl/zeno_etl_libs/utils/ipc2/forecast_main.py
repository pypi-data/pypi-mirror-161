import pandas as pd
import numpy as np
import datetime as dt
import time
from dateutil.relativedelta import relativedelta
from scipy.stats import norm

from zeno_etl_libs.utils.ipc2.config_ipc import *
from zeno_etl_libs.utils.ipc2.engine.data_load import LoadData
from zeno_etl_libs.utils.ipc2.engine.data_pre_process import PreprocessData
from zeno_etl_libs.utils.ipc2.engine.segmentation import Segmentation
from zeno_etl_libs.utils.ipc2.engine.ts_fcst import TS_forecast
from zeno_etl_libs.utils.ipc2.engine.forecast import Forecast
from zeno_etl_libs.utils.ipc2.engine.feat_engg import Feature_Engg


def ipc_forecast(store_id, reset_date, type_list, schema, db, logger):
    store_id_list = ("({})").format(store_id)  # for sql pass
    last_date = dt.date(day=1, month=4, year=2019)  # max history

    # define empty variables in case of fail
    weekly_fcst = pd.DataFrame()
    ts_fcst = pd.DataFrame()
    ts_fcst_cols = []

    logger.info("Data Loading Started...")
    data_load_obj = LoadData()

    (
        drug_list,
        sales_history,
        cfr_pr,
        calendar,
        first_bill_date
    ) = data_load_obj.load_all_input(
        type_list=type_list,
        store_id_list=store_id_list,
        last_date=last_date,
        reset_date=reset_date,
        schema=schema,
        db=db
    )

    logger.info("Data Pre Processing Started...")
    data_prep_obj = PreprocessData()

    (
        sales,
        sales_pred,
        cal_sales,
        sales_daily
    ) = data_prep_obj.preprocess_all(
        sales=sales_history,
        drug_list=drug_list,
        cfr_pr=cfr_pr,
        calendar=calendar,
        first_bill_date=first_bill_date,
        last_date=last_date
    )

    train_max_date = sales[date_col].max()
    end_date = sales_pred[date_col].max()

    logger.info("Segmentation Started...")
    seg_obj = Segmentation()

    seg_df, drug_class = seg_obj.get_weekly_segmentation(
        df=sales.copy(deep=True),
        df_sales_daily=sales_daily.copy(deep=True),
        train_max_date=train_max_date,
        end_date=end_date
    )

    seg_df['reset_date'] = str(reset_date)

    merged_df1 = pd.merge(sales_pred, seg_df, how='left', on=['ts_id'])
    merged_df1 = merged_df1[merged_df1['PLC Status L1'].isin(['Mature', 'NPI'])]

    if runs_ts_flag == 1:
        ts_fcst_obj = TS_forecast()
        # df_ts_fcst = applyParallel(
        #     merged_df1.groupby('ts_id'),
        #     func=TS_forecast.ts_forecast(
        #         df=merged_df1.copy(), train_max_date = train_max_date,
        #         forecast_start = train_max_date + relativedelta(weeks=2)))
        ts_fcst, ts_fcst_cols = ts_fcst_obj.apply_ts_forecast(
            df=merged_df1.copy(),
            train_max_date=train_max_date,
            forecast_start=train_max_date + relativedelta(weeks=2))

    # ========================= Forecast for 1-4 weeks =========================

    if run_ml_flag == 1:
        start_time = time.time()

        forecast_start = train_max_date + relativedelta(weeks=2)

        merged_df1['All'] = 'All'
        slice_col = 'All'
        forecast_volume = merged_df1[merged_df1[date_col] > train_max_date][
            target_col].sum()
        assert forecast_volume == 0
        logger.info(
            "forecast start {} total volume: {}".format(forecast_start,
                                                        forecast_volume)
        )

        forecast_df = pd.DataFrame()
        validation_df = pd.DataFrame()

        for i in range(1, 5):

            num_shift_lags = i + 1

            # for group_name in merged_df1[slice_col].dropna.unique():
            for group_name in ['All']:
                logger.info('Group: {}'.format(group_name))
                logger.info("Feature Engineering Started...")
                feat_df = pd.DataFrame()
                for one_df in [merged_df1]:
                    feat_engg_obj = Feature_Engg()
                    one_feat_df = feat_engg_obj.feat_agg(
                        one_df[
                            one_df[slice_col] == group_name
                            ].drop(slice_col, axis=1).copy(deep=True),
                        train_max_date=train_max_date,
                        num_shift_lag=num_shift_lags
                    )
                    feat_df = pd.concat([one_feat_df, feat_df])

                if pd.DataFrame(feat_df).empty:
                    continue

                logger.info(
                    "Forecasting Started for {}...".format(forecast_start))
                forecast_obj = Forecast()
                fcst_df, val_df, Feature_Imp_all = forecast_obj.get_STM_forecast(
                    feat_df.copy(deep=True),
                    forecast_start=forecast_start,
                    num_shift_lags=num_shift_lags
                )
                forecast_df = pd.concat([forecast_df, fcst_df], axis=0)
                validation_df = pd.concat([validation_df, val_df])
                ml_fc_cols = [i for i in forecast_df.columns if
                              i.startswith('preds_')]
                forecast_df['AE'] = forecast_df[ml_fc_cols].mean(axis=1)

            end_time = time.time()
            logger.info(
                "total time for {} forecast: {}"
                    .format(forecast_start, end_time - start_time)
            )

            forecast_start = forecast_start + relativedelta(weeks=1)

            weekly_fcst = pd.concat([weekly_fcst, forecast_df])
            weekly_fcst['reset_date'] = reset_date

    if runs_ts_flag == 0:
        weekly_fcst = weekly_fcst.copy(deep=True)
    if run_ml_flag == 0:
        weekly_fcst = ts_fcst.copy(deep=True)
        weekly_fcst['reset_date'] = reset_date
    if (run_ml_flag == 1 & runs_ts_flag == 1):
        weekly_fcst = pd.merge(weekly_fcst,
                               ts_fcst[[key_col, date_col] + ts_fcst_cols],
                               how='left', on=[key_col, date_col])

    weekly_fcst.drop_duplicates(inplace=True)
    weekly_fcst['model'] = 'LGBM'
    weekly_fcst[[store_col, drug_col]] = weekly_fcst[key_col].str.split('_',
                                                                        expand=True)
    weekly_fcst.rename(columns={'preds_lgb': 'fcst'}, inplace=True)
    # weekly_fcst.rename(columns={'preds_xgb_rf_target':'fcst'},inplace=True)
    weekly_fcst = pd.merge(weekly_fcst, seg_df[['ts_id', 'std', 'Mixed']],
                           how='left', on=['ts_id'])
    weekly_fcst.rename(columns={'Mixed': 'bucket'}, inplace=True)
    for key in percentile_bucket_dict.keys():
        print(key, percentile_bucket_dict[key])
        indexs = weekly_fcst[weekly_fcst.bucket == key].index
        weekly_fcst.loc[indexs, 'percentile'] = percentile_bucket_dict[key]
        weekly_fcst.loc[indexs, 'fcst'] = np.round(
            weekly_fcst.loc[indexs, 'fcst'] +
            norm.ppf(percentile_bucket_dict[key]) *
            weekly_fcst.loc[indexs, 'std'])
    weekly_fcst = weekly_fcst[
        ['store_id', 'drug_id', 'model', 'date', 'fcst', 'std', 'bucket',
         'percentile']]

    fc_cols = [i for i in weekly_fcst.columns if i.startswith('preds_')]
    weekly_fcst['std'].fillna(seg_df['std'].mean(), inplace=True)
    # agg_fcst = weekly_fcst.groupby(
    # ['model', 'store_id', 'drug_id', 'bucket', 'percentile']).\
    # agg({'fcst': 'sum', 'std': sum_std}).reset_index()
    agg_fcst = weekly_fcst.groupby(
        ['model', 'store_id', 'drug_id', 'bucket', 'percentile']). \
        agg({'fcst': 'sum', 'std': 'mean'}).reset_index()

    agg_fcst['store_id'] = agg_fcst['store_id'].astype(int)
    agg_fcst['drug_id'] = agg_fcst['drug_id'].astype(int)

    return agg_fcst, cal_sales, weekly_fcst, seg_df, drug_class
