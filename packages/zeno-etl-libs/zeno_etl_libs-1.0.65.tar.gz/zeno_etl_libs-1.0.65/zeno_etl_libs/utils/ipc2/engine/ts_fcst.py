import numpy as np
np.random.seed(0)
import pandas as pd
# import time
# import re
# from datetime import date
# from dateutil.relativedelta import relativedelta
# from statsmodels.tsa.exponential_smoothing.ets import ETSModel
from prophet import Prophet
from statsmodels.tsa.api import ExponentialSmoothing

# import sktime
from sktime.forecasting.ets import AutoETS
from zeno_etl_libs.utils.ipc2.helpers.helper_functions import sum_std,\
    applyParallel, applyParallel_croston
# from boruta import BorutaPy

from zeno_etl_libs.utils.ipc2.config_ipc import (
    date_col,
    target_col,
    models
)

import logging
logger = logging.getLogger("_logger")
logging.basicConfig(level=logging.DEBUG, format='%(message)s')


class TS_forecast:

    def train_test_split(self, df, train_max_date, forecast_start):
        df.rename(columns={date_col: 'ds', target_col: 'y'}, inplace=True)
        df.sort_values(by=['ds'], inplace=True)
        train = df[df['ds'] <= train_max_date]
        test = df[df['ds'] >= forecast_start]

        return train, test

    def Croston_TSB(self, ts, extra_periods=4, alpha=0.4, beta=0.4):
        d = np.array(ts)  # Transform the input into a numpy array
        cols = len(d)  # Historical period length
        d = np.append(d, [
            np.nan] * extra_periods)  # Append np.nan into the demand array to cover future periods

        # level (a), probability(p) and forecast (f)
        a, p, f = np.full((3, cols + extra_periods), np.nan)
        # Initialization
        first_occurence = np.argmax(d[:cols] > 0)
        a[0] = d[first_occurence]
        p[0] = 1 / (1 + first_occurence)
        f[0] = p[0] * a[0]

        # Create all the t+1 forecasts
        for t in range(0, cols):
            if d[t] > 0:
                a[t + 1] = alpha * d[t] + (1 - alpha) * a[t]
                p[t + 1] = beta * (1) + (1 - beta) * p[t]
            else:
                a[t + 1] = a[t]
                p[t + 1] = (1 - beta) * p[t]
            f[t + 1] = p[t + 1] * a[t + 1]

        # Future Forecast
        a[cols + 1:cols + extra_periods] = a[cols]
        p[cols + 1:cols + extra_periods] = p[cols]
        f[cols + 1:cols + extra_periods] = f[cols]

        df = pd.DataFrame.from_dict(
            {"Demand": d, "Forecast": f, "Period": p, "Level": a,
             "Error": d - f})
        return df[-extra_periods:]

    def ETS_forecast(self, train, test):
        try:
            train.set_index(['ds'], inplace=True)
            test.set_index(['ds'], inplace=True)
            train.index.freq = train.index.inferred_freq
            test.index.freq = test.index.inferred_freq

            # fit in statsmodels
            # model = AutoETS(sp=52,auto=True,allow_multiplicative_trend = False, additive_only=True)
            # fit = model.fit(train['y'])
            try:
                # fit =  ETSModel(np.asarray(train['y']) ,seasonal_periods=52 ,trend='add', seasonal='add').fit()
                fit = AutoETS(auto=True).fit(train['y'])
                preds = fit.predict(test.index)
            except Exception as e:
                logger.info("error in Auto-ETS")
                logger.info(str(e))
                fit = ExponentialSmoothing(train['y']).fit()
                preds = fit.forecast(len(test) + 1)
            preds = preds[-len(test):]
        except Exception as e:
            logger.info("error in ETS fcst")
            logger.info(str(e))
            preds = 0

        return preds

    def ma_forecast(self, data):
        """
        Purpose: Compute MA forecast for the for the forecast horizon specified
        Inputs: time series to create forecast
        Output: series with forecasted values
        """

        sma_df = data.copy(deep=True)
        yhat = []
        if len(data) >= 8:
            for i in range(5):
                sma_val = sma_df.rolling(8).mean().iloc[-1]
                sma_df.loc[sma_df.index.max() + 1] = sma_val
                yhat.append(sma_val)
        else:
            for i in range(5):
                sma_val = sma_df.rolling(len(data)).mean().iloc[-1]
                sma_df.loc[sma_df.index.max() + 1] = sma_val
                yhat.append(sma_val)
        logger.info(yhat)
        return yhat[-4:]

    def prophet_fcst(self, train, test, params=None):
        # reg_list = []
        try:
            if params is None:
                pro = Prophet()
            else:
                pro = Prophet(n_changepoints=params)
            # for j in train.columns:
            #     if j not in col_list:
            #         pro.add_regressor(j)
            #         reg_list.append(j)
            pro.fit(train[['ds', 'y']])
            pred_f = pro.predict(test)
            test = test[["ds", "y"]]
            test = pd.merge(test, pred_f, on="ds", how="left")
        except Exception as e:
            logger.info("error in prophet fcst")
            logger.info(str(e))
            test['yhat'] = 0
        return test

    def ts_forecast(self, df, train_max_date, forecast_start):
        train, test = self.train_test_split(df, train_max_date=train_max_date,
                                            forecast_start=forecast_start)
        test = test.sort_values(by=['ds'])
        if 'croston' in models:
            preds_croston = self.Croston_TSB(train['y'])
            test['preds_croston'] = preds_croston['Forecast'].values
        if 'ETS' in models:
            preds_ETS = self.ETS_forecast(train.copy(), test.copy())
            try:
                test['preds_ETS'] = preds_ETS.values
            except:
                test['preds_ETS'] = 0
        if 'MA' in models:
            preds_ma = self.ma_forecast(train['y'])
            test['preds_ma'] = preds_ma
        if 'prophet' in models:
            preds_prophet = self.prophet_fcst(train.copy(), test.copy())
            test['preds_prophet'] = preds_prophet['yhat'].values

        return test

    def apply_ts_forecast(self, df, train_max_date, forecast_start):
        # global train_date
        # train_date = train_max_date
        # global forecast_start_date
        # forecast_start_date  = forecast_start  
        preds = applyParallel_croston(
            df.groupby('ts_id'),
            func=self.ts_forecast, train_max_date=train_max_date,
            forecast_start=forecast_start
        )

        preds.rename(columns={'ds': date_col, 'y': target_col}, inplace=True)
        ts_fcst_cols = [i for i in preds.columns if i.startswith('preds_')]
        for col in ts_fcst_cols:
            preds[col].fillna(0, inplace=True)
            preds[col] = np.where(preds[col] < 0, 0, preds[col])

        preds['preds_AE_ts'] = preds[ts_fcst_cols].mean(axis=1)

        return preds, ts_fcst_cols
