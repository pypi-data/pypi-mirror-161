platform_prod = 0 

store_col = 'store_id'
drug_col = 'drug_id'
date_col = 'date'
target_col = 'actual_demand'
key_col = 'ts_id'
eol_cutoff = 13
mature_cutoff = 52
forecast_horizon = 4

flag_weather = 0
flag_seasonality_index = {
    'ctb': 0,
    'lgbm': 0,
    'xgb': 0
}

flag_sample_weights = {
    'ctb': 0,
    'lgbm': 0,
    'xgb': 0
}

num_shift_lag = 3

lags = [1]

add_lags_diff_flag = 1
lags_diff = [(1, 2)]

add_monthly_lags_flag = 1
# monthly_lags = [1, 2, 3, 6, 12]
monthly_lags = [1, 2, 3, 6]

rolling_time_feat = {
    'lags': [5, 13, 26, 53],
    'agg_func_dict': {'min', 'max', 'mean', 'median', 'std'}
}

ewma_lags = [4, 8]

# trend_lags = [13, 26, 53]
trend_lags = [13, 26]

perc_noise = [0.2, 0.5, 0.1]

# fc_cols = ['preds_xgb_rf_target','preds_cb_target','preds_lgb','AE', 'croston_fcst']
# models = ['croston', 'prophet', 'ETS', 'MA', 'AE_ts', 'lgbm']

run_ml_flag = 1
runs_ts_flag = 0
models = ['LGBM']
local_testing = 0

percentile_bucket_dict = {
    'AW': 0.5, 'AX': 0.5, 'AY': 0.5, 'AZ': 0.5,
    'BW': 0.5, 'BX': 0.5, 'BY': 0.6, 'BZ': 0.6,
    'CW': 0.5, 'CX': 0.5, 'CY': 0.6, 'CZ': 0.6,
    'DW': 0.5, 'DX': 0.5, 'DY': 0.6, 'DZ': 0.6}

# fc_cols = ['croston_fcst', 'ETS_fcst', 'ma_fcst','prophet_fcst', 'AE_ts_fcst']

# cols_rename = {
#     'preds_xgb_rf_target': 'fcst_1',
#     'preds_cb_target': 'fcst_2', 
#     'preds_lgb':'fcst_3',
#     'AE':'fcst_4',
#     'croston_fcst':'fcst_5'
# }

# cols_rename = {
#     'croston_fcst': 'fcst_1',
#     'ETS_fcst': 'fcst_2', 
#     'ma_fcst':'fcst_3',
#     'prophet_fcst':'fcst_4',
#     'AE_ts_fcst':'fcst_5'
# }

