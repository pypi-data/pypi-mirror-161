"""
To use different Service Level (SL) for different buckets.
Aligned based on Inventory-OOS-PR analysis and business requirements.
"""

import pandas as pd
import numpy as np
from scipy.stats import norm


def calculate_ss(safety_stock_df, fcst_weeks, logger):

    # ========================= DEFINE BUCKET SL HERE =========================
    sl_buckets = {'AW': 0.95, 'AX': 0.95, 'AY': 0.95, 'AZ': 0.95,
                  'BW': 0.90, 'BX': 0.90, 'BY': 0.90, 'BZ': 0.90,
                  'CW': 0.90, 'CX': 0.90, 'CY': 0.90, 'CZ': 0.90,
                  'DW': 0.90, 'DX': 0.90, 'DY': 0.90, 'DZ': 0.90}
    # =========================================================================

    logger.info("Base SS calculation starts")
    ss_calculated_all = pd.DataFrame()
    list_buckets = list(safety_stock_df["bucket"].unique())
    list_buckets.sort()

    for bucket in list_buckets:
        service_level = sl_buckets[bucket]
        z = norm.ppf(service_level)

        ss_calculated = safety_stock_df.loc[safety_stock_df["bucket"] == bucket]

        # calculate SS - variation in demand & lead time
        ss_calculated['safety_stock'] = ss_calculated.apply(
            lambda row: np.round(z * np.sqrt(
                ((row['lead_time_mean'] * np.square(row['std'])) +
                 np.square(row['lead_time_std'] * row['fcst'] / fcst_weeks / 7))
            )), axis=1)
        ss_calculated['safety_stock'] = np.where(
            ss_calculated['fcst'] == 0, 0, ss_calculated['safety_stock'])

        logger.info(f"Bucket: {bucket}, SL: {service_level}, "
                    f"Num Drugs: {ss_calculated.shape[0]}")

        ss_calculated_all = ss_calculated_all.append(ss_calculated)

    assert ss_calculated_all.shape[0] == safety_stock_df.shape[0]

    return ss_calculated_all
