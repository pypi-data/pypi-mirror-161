import numpy as np
np.random.seed(0)
import pandas as pd
import time
import re
from dateutil.relativedelta import relativedelta

from category_encoders.target_encoder import TargetEncoder
from category_encoders.leave_one_out import LeaveOneOutEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import GradientBoostingRegressor
from category_encoders.cat_boost import CatBoostEncoder
from xgboost import XGBRegressor
from xgboost import XGBRFRegressor
from lightgbm import LGBMRegressor
from catboost import CatBoostRegressor
# from boruta import BorutaPy

from zeno_etl_libs.utils.ipc2.config_ipc import (
    date_col,
    target_col,
    flag_sample_weights,
    flag_seasonality_index,
    models
)

import logging
logger = logging.getLogger("_logger")
logging.basicConfig(level=logging.DEBUG, format='%(message)s')


class Forecast:

    def one_hot_encode(self, df, one_hot_cols):
        added_one_hot_cols = []
        for col in one_hot_cols:
            one_hot_df = pd.get_dummies(df[col], prefix=col, drop_first=False)
            df = pd.concat([df.drop(col, axis=1), one_hot_df], axis=1)
            added_one_hot_cols += one_hot_df.columns.to_list()
        return df, added_one_hot_cols

    def encode(self, X_train, y_train, cat_cols, encoder_type='Target'):
        if len(cat_cols) == 0:
            return X_train, None

        cat_cols = list(set(cat_cols) & set(X_train.columns))

        logger.debug('Categorical Encoding Started...')
        if encoder_type == 'Target':
            encoder = TargetEncoder(cols=cat_cols)
        elif encoder_type == 'Catboost':
            encoder = CatBoostEncoder(cols=cat_cols)
        elif encoder_type == 'LeaveOneOut':
            encoder = LeaveOneOutEncoder(cols=cat_cols)
        X_train_enc = encoder.fit_transform(
            X_train, y_train
        )

        return X_train_enc, encoder

    # def get_target_encode(X_train, y_train, target_encode_cols):
    #     for col in target_encode_cols:
    #         encoder = TargetEncoder()
    #         encoder.fit_transform(df[[col, province_col]], df[target_col])
    #         encoder.transform()

    #     return df

    def get_feature_imp(self, algo, algo_name, feature_cols, forecast_month):
        importance = algo.feature_importances_.round(4)
        names = np.array(feature_cols)
        Feature_Imp = pd.DataFrame(data=np.column_stack((names, importance)
                                                        ),
                                   columns=['names', 'importance'])
        Feature_Imp.columns = ['Feature', 'Feature_Importance']
        Feature_Imp[date_col] = forecast_month
        Feature_Imp = Feature_Imp[[date_col, 'Feature', 'Feature_Importance']]
        Feature_Imp = Feature_Imp.rename(
            columns={'Feature_Importance': algo_name})
        return (Feature_Imp)

    def get_train_test_split(
            self, df, train_max_date, forecast_start_date, forecast_end_date,
            num_shift_lags=1
    ):
        # TODO - no need to do this. Lags are offset enough. we can use latest week data
        train = df[df[date_col] <= train_max_date]

        # train
        train = train[
            (train[date_col] < forecast_start_date)
        ]
        # train.dropna(inplace = True)
        train.set_index(['ts_id', date_col], inplace=True)
        X_train = train.drop(target_col, axis=1)
        y_train = train[target_col].fillna(0)

        # test
        test = df[
            (df[date_col] >= forecast_start_date) &
            (df[date_col] <= forecast_end_date)
            ]
        test.set_index(['ts_id', date_col], inplace=True)
        X_test = test.drop(target_col, axis=1)
        y_test = test[target_col]
        return X_train, y_train, X_test, y_test

    def get_regex_filtered_data(self, l):
        regex = re.compile(r"\[|\]|<", re.IGNORECASE)
        filtered_l = [
            regex.sub("_", col) if any(
                x in str(col) for x in set(("[", "]", "<", " "))) else col
            for col in l
        ]

        filtered_l = [i.replace(" ", "_") for i in filtered_l]
        return filtered_l

    def add_sample_weights(self, df, max_date, forecast_start):
        df['days_till_last_day'] = (df[date_col] - max_date).dt.days
        df['sample_weights'] = np.exp(df['days_till_last_day'] / 2)
        df.loc[
            df[date_col] == (forecast_start - relativedelta(months=12)),
            'sample_weights'
        ] = 1
        df.loc[
            df[date_col] == (forecast_start - relativedelta(months=24)),
            'sample_weights'
        ] = 1
        df = df.set_index(['ts_id', date_col])
        return df['sample_weights']

    def get_model_predictions(
            self, model, model_name, X_test, y_test, Feature_Imp_all,
            feature_cols, forecast_start
    ):
        if Feature_Imp_all.empty:
            Feature_Imp_all = self.get_feature_imp(
                model, model_name, feature_cols, forecast_start
            )
        else:
            Feature_Imp_all = pd.merge(
                Feature_Imp_all,
                self.get_feature_imp(model, model_name, feature_cols,
                                     forecast_start),
                how='outer',
                on=[date_col, 'Feature']
            )

        if pd.DataFrame(X_test).empty:
            return y_test, Feature_Imp_all

        y_pred = model.predict(X_test)

        pred_col = 'preds_{}'.format(model_name)
        y_test[pred_col] = y_pred
        y_test.loc[y_test[pred_col] < 0, pred_col] = 0
        y_test[pred_col] = y_test[pred_col].fillna(0)
        lgb_acc = 1 - self.wmape(y_test[target_col], y_test[pred_col])
        logger.info(
            "{} Accuracy {}: {}"
                .format(model_name, forecast_start.strftime("%b"), lgb_acc)
        )
        return y_test, Feature_Imp_all

    def wmape(self, actuals, forecast):
        error = abs(actuals - forecast)
        wmape_val = error.sum() / actuals.sum()
        return wmape_val

    def get_STM_forecast(self, df, forecast_start, num_shift_lags=1):
        global num_cols, cat_cols

        ts_features = [
            i for i in df.columns if (
                    ('lag' in i)
                    | ('_Sin' in i)
                    | ('_Cos' in i)
                    | ('_mean' in i)
                    | ('_trend' in i)
                    | ('ewm' in i)
                    | ('seasonality_index' in i)
            )
        ]

        flag_cols = [i for i in df.columns if i.endswith('_flag')]
        num_cols = (
            ts_features
        )
        target_encode_cols = [

        ]

        one_hot_cols = [
            'classification',
            'Group',
            'ABC',
            'WXYZ',
            'PLC Status L1'
        ]

        df, added_one_hot_cols = self.one_hot_encode(df, one_hot_cols)

        # df = self.get_target_encode(df, target_encode_cols)

        train_max_date = (forecast_start - relativedelta(weeks=num_shift_lags))
        X_train, y_train, X_test, y_test = self.get_train_test_split(
            df, train_max_date, forecast_start, forecast_start,
            num_shift_lags=num_shift_lags
        )
        # TODO: 
        # Add more cat features from item heirarchy and province, planning item, 
        # rolling features
        # ewma 
        # promo
        # Nan --> keep it
        # ETS as a feature
        cat_features = [
                           # 'covid_flag'
                       ] + target_encode_cols

        feature_cols = num_cols + flag_cols + added_one_hot_cols + [
            'LOL',
            'Year_Num', 'Quarter_Num', 'Quarter_Sin', 'Quarter_Cos',
            'Month_Num', 'Month_Sin', 'Month_Cos',
            'cov', 'ADI'
        ]
        feature_cols = list(set(df.columns) & set(feature_cols))
        # cat_features = []
        X_train = X_train[feature_cols + cat_features]
        X_test = X_test[feature_cols + cat_features]
        X_train.columns = self.get_regex_filtered_data(X_train.columns)
        X_test.columns = self.get_regex_filtered_data(X_test.columns)

        y_test = y_test.reset_index()

        val = (
            X_train
                .reset_index()
                .merge(y_train.reset_index(), on=[date_col, 'ts_id'],
                       how='left')
        )
        _, _, X_val, y_val = self.get_train_test_split(
            val,
            train_max_date=train_max_date - relativedelta(weeks=8),
            forecast_start_date=train_max_date - relativedelta(weeks=7),
            forecast_end_date=train_max_date,
            num_shift_lags=num_shift_lags
        )
        y_val = y_val.reset_index()

        filtered_cat_features = self.get_regex_filtered_data(cat_features)
        # X_train.dropna()
        Feature_Imp_all = pd.DataFrame()

        # X_train[filtered_cat_features] = X_train[filtered_cat_features].astype(str)

        # Encoding
        X_train_target, encoder = self.encode(X_train, y_train,
                                              filtered_cat_features, 'Target')
        if encoder != None:
            X_test_target = encoder.transform(
                X_test[encoder.get_feature_names()])
            X_val_target = encoder.transform(X_val[encoder.get_feature_names()])
        else:
            X_test_target = X_test.copy(deep=True)
            X_val_target = X_val.copy(deep=True)

        smaple_weights = self.add_sample_weights(
            X_train_target.reset_index()[['ts_id', date_col]],
            max_date=train_max_date,
            forecast_start=forecast_start
        )

        if 'XGB' in models:
            ###XGBRF##
            logger.info("Forecasting XGRF...")
            xgb_rf = XGBRFRegressor(n_estimators=750, random_state=42)

            xgb_sample_weights = None
            if flag_sample_weights['xgb']:
                xgb_sample_weights = smaple_weights

            X_train_xgb = X_train_target
            X_test_xgb = X_test_target
            X_val_xgb = X_val_target

            if flag_seasonality_index['xgb']:
                seas_cols = [i for i in X_train_target.columns if
                             'seasonality_index' in i]
                X_train_xgb = X_train_target.drop(seas_cols, axis=1).copy()
                X_test_xgb = X_test_target.drop(seas_cols, axis=1).copy()
                X_val_xgb = X_val_target.drop(seas_cols, axis=1).copy()

            xgb_rf.fit(X_train_xgb, y_train, sample_weight=xgb_sample_weights)

            y_test, Feature_Imp_all = self.get_model_predictions(
                model=xgb_rf,
                model_name='xgb_rf_target',
                X_test=X_test_xgb,
                y_test=y_test,
                Feature_Imp_all=Feature_Imp_all,
                feature_cols=X_train_xgb.columns,
                forecast_start=forecast_start
            )

            y_val, Feature_Imp_all = self.get_model_predictions(
                model=xgb_rf,
                model_name='xgb_rf_target',
                X_test=X_val_xgb,
                y_test=y_val,
                Feature_Imp_all=Feature_Imp_all,
                feature_cols=X_train_xgb.columns,
                forecast_start=forecast_start
            )

        if 'CTB' in models:
            ###Catboost Target##
            logger.info("Forecasting CB...")
            cb = CatBoostRegressor(
                n_estimators=1000, learning_rate=0.01,
                cat_features=filtered_cat_features,
                # one_hot_max_size = 16,
                random_state=42, verbose=0
            )

            ctb_sample_weights = None
            if flag_sample_weights['ctb']:
                ctb_sample_weights = smaple_weights

            X_train_ctb = X_train
            X_test_ctb = X_test
            X_val_ctb = X_val

            if flag_seasonality_index['ctb']:
                seas_cols = [i for i in X_train.columns if
                             'seasonality_index' in i]
                X_train_ctb = X_train.drop(seas_cols, axis=1).copy()
                X_test_ctb = X_test.drop(seas_cols, axis=1).copy()
                X_val_ctb = X_val.drop(seas_cols, axis=1).copy()

            cb.fit(X_train_ctb, y_train, sample_weight=ctb_sample_weights)

            y_test, Feature_Imp_all = self.get_model_predictions(
                model=cb,
                model_name='cb_target',
                X_test=X_test_ctb,
                y_test=y_test,
                Feature_Imp_all=Feature_Imp_all,
                feature_cols=X_train_ctb.columns,
                forecast_start=forecast_start
            )

            y_val, Feature_Imp_all = self.get_model_predictions(
                model=cb,
                model_name='cb_target',
                X_test=X_val_ctb,
                y_test=y_val,
                Feature_Imp_all=Feature_Imp_all,
                feature_cols=X_train_ctb.columns,
                forecast_start=forecast_start
            )

        if 'LGBM' in models:
            ###LGBM##
            logger.info("Forecasting LGBM...")
            lgb = LGBMRegressor(
                n_estimators=2000, learning_rate=0.005,
                max_depth=10, num_leaves=int((2 ** 10) / 2), max_bin=1000,
                random_state=42, verbose=-1,
                categorical_feature=filtered_cat_features,
            )
            X_train1 = X_train.copy(deep=True)
            X_test1 = X_test.copy(deep=True)
            X_val1 = X_val.copy(deep=True)

            logger.info("LGBM train: {}".format(X_train1.head(2)))
            logger.info(
                'Filtered cat features:{}'.format(filtered_cat_features))
            logger.info('Filtered cat features columns:{}'.format(
                X_train1[filtered_cat_features].columns))
            logger.info('Filtered cat features dtypes:{}'.format(
                X_train1[filtered_cat_features].dtypes))
            # X_train1[filtered_cat_features] = X_train1[filtered_cat_features].astype('category')
            # X_test1[filtered_cat_features] = X_test1[filtered_cat_features].astype('category')
            # X_val1[filtered_cat_features] = X_val1[filtered_cat_features].astype('category')

            lgb_sample_weights = None
            if flag_sample_weights['lgbm']:
                lgb_sample_weights = smaple_weights

            X_train_lgbm = X_train1
            X_test_lgbm = X_test1
            X_val_lgbm = X_val1

            if flag_seasonality_index['lgbm']:
                seas_cols = [i for i in X_train1.columns if
                             'seasonality_index' in i]
                X_train_lgbm = X_train1.drop(seas_cols, axis=1).copy()
                X_test_lgbm = X_test1.drop(seas_cols, axis=1).copy()
                X_val_lgbm = X_val1.drop(seas_cols, axis=1).copy()

            lgb.fit(X_train_lgbm, y_train, sample_weight=lgb_sample_weights)

            y_test, Feature_Imp_all = self.get_model_predictions(
                model=lgb,
                model_name='lgb',
                X_test=X_test_lgbm,
                y_test=y_test,
                Feature_Imp_all=Feature_Imp_all,
                feature_cols=X_test_lgbm.columns,
                forecast_start=forecast_start
            )

            y_val, Feature_Imp_all = self.get_model_predictions(
                model=lgb,
                model_name='lgb',
                X_test=X_val_lgbm,
                y_test=y_val,
                Feature_Imp_all=Feature_Imp_all,
                feature_cols=X_test_lgbm.columns,
                forecast_start=forecast_start
            )
        return y_test, y_val, Feature_Imp_all
