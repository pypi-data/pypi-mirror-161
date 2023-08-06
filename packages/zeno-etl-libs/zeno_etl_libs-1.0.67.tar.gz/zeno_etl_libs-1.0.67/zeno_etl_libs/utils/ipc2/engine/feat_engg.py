from datetime import date
import pandas as pd
import numpy as np
from dateutil.relativedelta import relativedelta
from tqdm import tqdm
import time
from statsmodels.tsa.arima_model import ARMA
from sklearn.linear_model import LinearRegression

import logging
import warnings
warnings.filterwarnings("ignore")
logger = logging.getLogger("_logger")
logging.basicConfig(level=logging.DEBUG, format='%(message)s')

from zeno_etl_libs.utils.ipc2.config_ipc import (
    date_col,
    target_col,
    store_col,
    drug_col,
    eol_cutoff,
    add_lags_diff_flag,
    add_monthly_lags_flag, 
    rolling_time_feat,
    ewma_lags,
    trend_lags,
    lags,
    lags_diff,
    monthly_lags,
)


class Feature_Engg:

    def add_week_of_month(self, df):
        df["week_of_month"] = df[date_col].apply(lambda d: (d.day - 1) // 7 + 1)
        return df

    def add_month(self, df):
        df['Month'] = df[date_col].dt.month
        return df

    def calc_si(self, df, num_shift_lag=1):

        max_date = df[date_col].max()
        time_lag = (len(df) // cutoff_dic["si_week_freq"]) * cutoff_dic[
            "si_week_freq"]
        min_date = max_date + relativedelta(months=-time_lag)

        df = df[(df[date_col] > min_date)]

        try:
            tsid_mean = np.mean(df[target_col].shift(num_shift_lag))
        except BaseException as e:
            logger.info(df.ts_id.iloc[0])
            logger.info(e)
            # continue

        df = df.groupby(["ts_id", "Week_Number"])[
            target_col].mean().reset_index()
        df["Seas_index"] = df[target_col] / tsid_mean
        df = df[["ts_id", "Week_Number", "Seas_index"]]

        return df

    def ratio_based_si(self, df, train_max_date, num_shift_lag):

        if 'ts_id' not in df.columns:
            df = self.add_ts_id(df)

        train = df[df[date_col] <= train_max_date]

        dict_of = dict(iter(train.groupby(["ts_id"])))
        si_list = [self.calc_si(dict_of[x], num_shift_lag) for x in
                   dict_of.keys()]
        si_df = pd.concat(si_list)

        if 'Seas_index' in df.columns:
            df.drop(['Seas_index'], axis=1, inplace=True)

        df = pd.merge(df, si_df, how="left", on=["ts_id", "Week_Number"])
        df['Seas_index'].fillna(1, inplace=True)
        return df

    def add_ARMA_forecast(self, data):

        model = ARMA(data[target_col], order=(0, 1))
        model_fit = model.fit(disp=False)
        # forecast for required time priods
        yhat = model_fit.predict(
            len(data) - cutoff_dic["forecast_horizon_period"], len(data) - 1
        )
        data["ARMA_Forecast"] = yhat
        data["Actuals + ARMA"] = np.where(
            data["ARMA_Forecast"].isnull(), data[target_col],
            data["ARMA_Forecast"]
        )
        return data[["ts_id", date_col, "Actuals + ARMA"]]

    def trend_sim_lin_reg(self, df):

        df.sort_values(by=date_col, inplace=True)
        df.reset_index()
        df["index"] = df.index
        x = df["index"].values.reshape(-1, 1)
        y = df[target_col].values.reshape(-1, 1)

        # fit linear regression
        regressor = LinearRegression()
        regressor.fit(x, y)
        return regressor.coef_

    def add_trend_lags(self, actuals, fcst):
        # for i in lags:
        #     fcst['Lag_' + str(i)] = fcst['Actuals + ARMA'].shift(i)
        # fcst = fcst.fillna(0)
        # fcst["rolling_ly_lag"] = (0.1 * fcst["Lag_104"]) + (0.9 * fcst["Lag_52"])

        # fcst.drop(['Lag_' + str(i) for i in lags], axis = 1, inplace = True)

        actuals_trend = actuals.groupby(["ts_id"])[
            target_col].sum().reset_index()
        actuals_trend["trend_value"] = self.trend_sim_lin_reg(actuals)[0, 0]
        return actuals_trend, fcst

    def add_lags(self, df, lag_list, num_shift_lag=1):
        is_drop_ts_id = False
        if 'ts_id' not in df.columns:
            df = self.add_ts_id(df)
            is_drop_ts_id = True

        df_grp_sum = (df.groupby([date_col, "ts_id"])[target_col]
                      .sum()
                      .unstack())
        lag_l = []
        lag_l_diff = []
        for lag in lag_list:
            lag_df = (
                df_grp_sum
                    .shift(lag + num_shift_lag - 1)
                    .fillna(method="bfill")
                    .stack()
                    .reset_index()
            )
            lag_df_diff = (
                df_grp_sum
                    .shift(lag + num_shift_lag - 1)
                    .diff(1)
                    .fillna(method="bfill")
                    .stack()
                    .reset_index()
            )

            lag_df.rename(columns={0: "lag_" + str(lag)}, inplace=True)
            lag_df_diff.rename(columns={0: "lag_" + str(lag) + '_diff'},
                               inplace=True)

            if "lag_" + str(lag) in df.columns:
                df.drop("lag_" + str(lag), axis=1, inplace=True)

            if "lag_" + str(lag) + '_diff' in df.columns:
                df.drop("lag_" + str(lag) + '_diff', axis=1, inplace=True)

            lag_l.append(lag_df.set_index(["ts_id", date_col]))
            lag_l.append(lag_df_diff.set_index(["ts_id", date_col]))

        lag_df = None
        for l in lag_l:
            if lag_df is None:
                lag_df = l
            else:
                lag_df = lag_df.join(l)

        df = df.merge(lag_df.reset_index(), on=["ts_id", date_col], how="left")

        df.drop("ts_id", axis=1, inplace=is_drop_ts_id)
        return df

    def add_lag_diff(self, df, lags_diff, num_shift_lag=1):
        drop_cols = []
        for i, j in lags_diff:
            col_name = 'lag_diff_{}_{}'.format(i, j)
            if col_name in df.columns:
                df.drop(col_name, axis=1, inplace=True)

            if 'lag_' + str(i) not in df.columns:
                df = self.add_lags(df, [i], num_shift_lag=num_shift_lag)
                drop_cols.append('lag_' + str(i))

            if 'lag_' + str(j) not in df.columns:
                df = self.add_lags(df, [j], num_shift_lag=num_shift_lag)
                drop_cols.append('lag_' + str(j))
                drop_cols.append('lag_' + str(j) + '_diff')

            df[col_name] = df['lag_' + str(i)] - df['lag_' + str(j)]

        if len(drop_cols) > 0:
            df.drop(drop_cols, axis=1, inplace=True)

        return df

    def add_montly_lags(self, df, monthly_lags, num_shift_lag=1):

        start = time.time()
        mo_lag_dict = {}
        for lag in monthly_lags:
            mo_lag_dict[lag] = []

        for week_num in df['week_of_month'].unique():
            one_week_df = df[df['week_of_month'] == week_num][
                ['ts_id', date_col, target_col]]
            df_grp = one_week_df.groupby([date_col, 'ts_id'])[
                target_col].sum().unstack()
            df_grp.sort_index(axis=1, inplace=True)

            for lag in monthly_lags:
                lag1 = lag

                mo_lag = (
                    df_grp
                        .shift(lag1)
                        .bfill()
                        .unstack()
                        .reset_index()
                        .rename(columns={0: str(lag) + '_mo_lag'})
                )

                # for diff_num in range(1,5):
                #     diff_col = str(lag)+'_mo_lag_diff'+ str(diff_num)
                #     mo_lag_diff = (
                #         df_grp
                #         .shift(lag1)
                #         .diff(diff_num)
                #         .bfill()
                #         .unstack()
                #         .reset_index()
                #         .rename(columns = {0: str(lag) +'_mo_lag_diff' + str(diff_num)})
                #     )
                #     mo_lag = mo_lag.merge(mo_lag_diff, on = ['ts_id', date_col], how = 'left')

                mo_lag_dict[lag].append(mo_lag)

        for lag in monthly_lags:
            col_name = str(lag) + '_mo_lag'
            if col_name in df.columns:
                df.drop(col_name, axis=1, inplace=True)

            for diff_num in range(1, 5):
                diff_col = str(lag) + '_mo_lag_diff' + str(diff_num)
                if diff_col in df.columns:
                    df.drop(diff_col, axis=1, inplace=True)

            mo_lag = pd.concat(mo_lag_dict[lag])
            for diff_num in range(1, 5):
                diff_col = str(lag) + '_mo_lag_diff' + str(diff_num)

                mo_lag_diff = (
                    mo_lag
                        .groupby([date_col, 'ts_id'])
                    [str(lag) + '_mo_lag']
                        .sum()
                        .unstack()
                        .sort_index()
                        .diff(diff_num)
                        .bfill()
                        .stack()
                        .reset_index()
                        .rename(columns={0: diff_col})
                )
                mo_lag = mo_lag.merge(mo_lag_diff, on=['ts_id', date_col],
                                      how='left')

            df = df.merge(mo_lag, on=['ts_id', date_col], how='left')

        end = time.time()
        logger.debug(
            "Time for updated monthly lags: {} mins".format((end - start) / 60))
        return df

    def add_rolling_lag(self, df, num_shift_lag=1):

        df["rolling lag"] = (
                (0.4 * df[target_col].shift(num_shift_lag))
                + (0.3 * df[target_col].shift(num_shift_lag + 1))
                + (0.2 * df[target_col].shift(num_shift_lag + 2))
                + (0.1 * df[target_col].shift(num_shift_lag + 3))
        )
        return df

    def add_start_end_dates(self, df):
        # Look for monthly format 4-4-5 and then make logic
        is_drop_week_of_month = False
        if 'week_of_month' not in df.columns:
            df = self.add_week_of_month(df)
            is_drop_week_of_month = True

        df["MonthStart"] = 0
        df.loc[df['week_of_month'] == 1, 'MonthStart'] = 1
        df.drop('week_of_month', axis=1, inplace=is_drop_week_of_month)
        # df[date_col]= pd.to_datetime(df[date_col])
        month_end_list = (
                df[df['MonthStart'] == 1][date_col].dt.date - relativedelta(
            weeks=1)
        ).values

        df['MonthEnd'] = 0
        df.loc[
            df[date_col].isin(month_end_list), 'MonthEnd'
        ] = 1

        # df["MonthEnd"] = df[date_col].dt.is_month_end.astype(int)
        df["QuarterStart"] = (
                df[date_col].dt.month.isin([1, 4, 7, 10]).astype(int)
                & df['MonthStart']
        )
        df["QuarterEnd"] = (
                df[date_col].dt.month.isin([3, 6, 9, 12]).astype(int)
                & df['MonthEnd']
        )
        return df

    def add_holiday_ratio(self, df):
        df["Holiday_Ratio"] = df["holiday_count"].fillna(0) / 7
        return df

    def add_rolling_time_features(self, df, week_list, agg_dict,
                                  num_shift_lag=1):
        roll_l = []
        roll_l_diff = []
        drop_cols = set()
        df_grp_sum = (
            df.groupby([date_col, "ts_id"])[target_col]
                .sum()
                .unstack()
                .shift(num_shift_lag)
        )
        for num in week_list:
            week_df = (
                df_grp_sum
                    .rolling(num)
                    .agg(agg_dict)
                    .bfill()
                    .ffill()
                    .unstack()
                    .unstack(level=1)
                    .reset_index()
            ).rename(
                columns={
                    "level_0": "ts_id",
                    "mean": "avg_week" + str(num),
                    "median": "median_week" + str(num),
                    "std": "std_week" + str(num),
                    "max": "max_week" + str(num),
                    "min": "min_week" + str(num),
                }
            )

            week_df_diff = (
                df_grp_sum
                    .rolling(num)
                    .agg('mean')
                    .diff(1)
                    .bfill()
                    .ffill()
                    .unstack()
                    .reset_index()
            ).rename(columns={0: "avg_week" + str(num) + "_diff"})

            drop_cols = drop_cols.union(
                set(week_df.drop(["ts_id", date_col], axis=1).columns)
                | set(week_df_diff.drop(["ts_id", date_col], axis=1).columns)
            )
            roll_l.append(week_df.set_index(["ts_id", date_col]))
            roll_l.append(week_df_diff.set_index(["ts_id", date_col]))

        drop_cols = list(drop_cols & set(df.columns))
        df.drop(drop_cols, axis=1, inplace=True)

        week_df = None
        for l in roll_l:
            if week_df is None:
                week_df = l
            else:
                week_df = week_df.join(l)
        df = df.merge(week_df.reset_index(), on=["ts_id", date_col], how="left")

        # for i in [13, 25, 52]:
        #     roll_df = df_grp_sum.shift(num_shift_lag).bfill().rolling(i, min_periods = 1)

        #     roll_df = (
        #         roll_df.quantile(0.75)
        #         - roll_df.quantile(0.25)
        #     ).unstack().reset_index().rename(columns = {0: 'Quantile_diff_'+str(i)})

        #     if 'Quantile_diff_'+str(i) in df.columns:
        #         df.drop('Quantile_diff_'+str(i), axis = 1, inplace = True)

        #     df = df.merge(roll_df, on = ['ts_id', date_col], how = 'left')

        return df

    def add_ewma(self, df, week_list, agg_dict, num_shift_lag=1):
        ewma_l = []
        df_grp_sum = (df.groupby([date_col, "ts_id"])[target_col]
                      .sum()
                      .unstack()
                      .shift(num_shift_lag)
                      .bfill()
                      .ffill())
        for num in week_list:
            week_df = (
                df_grp_sum
                    .ewm(span=num, ignore_na=True, adjust=True, min_periods=1)
                    .agg(agg_dict)
                    .bfill()
                    .ffill()
                    .unstack()
                    .unstack(level=1)
                    .reset_index()
            )

            week_df.rename(columns={
                "level_0": "ts_id",
                "mean": "ewma_" + str(num)
            }, inplace=True)

            if "ewma_" + str(num) in df.columns:
                df.drop("ewma_" + str(num), axis=1, inplace=True)
            ewma_l.append(week_df.set_index(["ts_id", date_col]))

        week_df = None
        for l in ewma_l:
            if week_df is None:
                week_df = l
            else:
                week_df = week_df.join(l)
        df = df.merge(week_df.reset_index(), on=["ts_id", date_col], how="left")
        return df

    def add_trend(self, df, week_list, num_shift_lag=1):
        # is_drop = True
        if 'ts_id' not in df.columns:
            df = self.add_ts_id(df)

        df_grp = (
            df.groupby([date_col, "ts_id"])[target_col]
                .sum()
                .unstack()
        )
        df_grp = df_grp.shift(num_shift_lag).bfill()
        numerator = df_grp.rolling(5, min_periods=1).mean()

        # all_trends_df = None
        df.set_index([date_col, "ts_id"], inplace=True)
        for num in week_list:
            denominator = df_grp.rolling(num, min_periods=1).mean()
            one_trend_df = (numerator / (
                        denominator + 1e-8)).bfill().ffill().stack().reset_index()
            one_trend_df.rename(columns={0: "trend_week" + str(num)},
                                inplace=True)
            if "trend_week" + str(num) in df.columns:
                df.drop(columns="trend_week" + str(num), inplace=True)
            df = df.join(one_trend_df.set_index([date_col, "ts_id"]),
                         how='left')
            # all_trends_df.append(one_trend_df)

        return df.reset_index()

    def create_one_hot_holiday(self, df, col, name, on="holiday"):
        df[name] = 0
        df.loc[df[on] == col, name] = 1
        return df

    def add_week_of_month(self, df):
        df["week_of_month"] = df[date_col].apply(lambda d: (d.day - 1) // 7 + 1)
        return df

    def add_year_month(self, df):
        year_df = df[date_col].dt.year
        month_df = df[date_col].dt.month
        df['YearMonth'] = year_df.astype(str) + '_' + month_df.astype(str)
        return df

    def add_month(self, df):
        df['Month'] = df[date_col].dt.month
        return df

    def feat_agg(self, df, train_max_date, num_shift_lag):
        if pd.DataFrame(df).empty:
            return df

        if target_col not in df.columns:
            raise ValueError(
                "{} col not in dataframe passed".format(target_col))
        if date_col not in df.columns:
            raise ValueError("{} col not in dataframe passed".format(date_col))

        df = self.add_week_of_month(df)

        df = self.add_month(df)

        df.loc[df[date_col] > train_max_date, target_col] = np.nan

        logger.debug("Adding TS Features...")

        logger.debug("Adding lags...")
        logger.debug("Lags: {}".format(lags))
        df = self.add_lags(df, lags, num_shift_lag=num_shift_lag)

        if add_lags_diff_flag:
            logger.debug("Adding Lag Diff")
            logger.debug(
                "lags_diff: {}".format(lags_diff, num_shift_lag=num_shift_lag))
            df = self.add_lag_diff(df, lags_diff)

        if add_monthly_lags_flag:
            logger.debug("Adding Monthly lags..")
            df = self.add_montly_lags(df, monthly_lags,
                                      num_shift_lag=num_shift_lag)

        logger.debug("Adding start end dates...")
        df = self.add_start_end_dates(df)

        logger.debug("Adding rolling time features...")
        df = self.add_rolling_time_features(
            df, rolling_time_feat["lags"], rolling_time_feat["agg_func_dict"],
            num_shift_lag=num_shift_lag
        )
        logger.debug("Adding ewma...")
        df = self.add_ewma(df, ewma_lags, {"mean"}, num_shift_lag=num_shift_lag)

        logger.debug("Adding trend...")
        df = self.add_trend(df, trend_lags, num_shift_lag=num_shift_lag)

        logger.debug("TS Features added successfully...")
        logger.info("maxdate after TS: {}".format(df[date_col].max()))

        return df
