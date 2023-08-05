import pandas as pd
import numpy as np
from dateutil.relativedelta import relativedelta
from tqdm import tqdm

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
    eol_cutoff
)


class Segmentation:

    def add_ts_id(self, df):
        df['ts_id'] = (
                df[store_col].astype(int).astype(str)
                + '_'
                + df[drug_col].astype(int).astype(str)
        )
        return df

    def _calc_abc(self, df52):
        B_cutoff = 0.8
        C_cutoff = 0.95
        D_cutoff = 0.995

        tot_sales = (
            df52.groupby([
                'ts_id'
            ])[target_col].sum().reset_index()
        )

        tot_sales.rename(columns={target_col: 'total_LY_sales'}, inplace=True)
        tot_sales.sort_values('total_LY_sales', ascending=False, inplace=True)
        tot_sales["perc_sales"] = (
                tot_sales['total_LY_sales'] / tot_sales['total_LY_sales'].sum()
        )
        tot_sales["cum_perc_sales"] = tot_sales.perc_sales.cumsum()
        tot_sales["ABC"] = "A"
        tot_sales.loc[tot_sales.cum_perc_sales > B_cutoff, "ABC"] = "B"
        tot_sales.loc[tot_sales.cum_perc_sales > C_cutoff, "ABC"] = "C"
        tot_sales.loc[tot_sales.cum_perc_sales > D_cutoff, "ABC"] = "D"

        # tot_sales = self.add_ts_id(tot_sales)

        return tot_sales[['ts_id', 'ABC', 'total_LY_sales']]

    # TODO: lower COV cutoffs

    def get_abc_classification(self, df52):
        province_abc = df52.groupby(
            [store_col]
        ).apply(self._calc_abc)

        province_abc = province_abc[['ts_id', "ABC"]].reset_index(drop=True)

        # one
        tot_sales = (
            df52
                .groupby(['ts_id'])[target_col]
                .agg(['sum', 'mean'])
                .reset_index()
        )

        tot_sales.rename(
            columns={'sum': 'total_LY_sales', 'mean': 'avg_ly_sales'},
            inplace=True)
        tot_sales = tot_sales.merge(
            province_abc,
            on=['ts_id'],
            how='left'
        )

        tot_sales = tot_sales.drop_duplicates()
        # tot_sales = self.add_ts_id(tot_sales)
        tot_sales = tot_sales[['ts_id', 'ABC']]
        return tot_sales

    def get_xyzw_classification(self, df1):
        input_ts_id = df1['ts_id'].unique()

        df1 = df1[df1[target_col] > 0]

        cov_df = df1.groupby(['ts_id'])[target_col].agg(
            ["mean", "std", "count", "sum"])

        cov_df.reset_index(drop=False, inplace=True)

        cov_df['cov'] = np.where(
            ((cov_df["count"] > 2) & (cov_df["sum"] > 0)),
            (cov_df["std"]) / (cov_df["mean"]),
            np.nan
        )
        cov_df['WXYZ'] = 'Z'
        cov_df.loc[cov_df['cov'] <= 1.2, 'WXYZ'] = 'Y'
        cov_df.loc[cov_df['cov'] <= 0.8, 'WXYZ'] = 'X'
        cov_df.loc[cov_df['cov'] <= 0.5, 'WXYZ'] = 'W'

        # cov_df = self.add_ts_id(cov_df)
        cov_df = cov_df[['ts_id', 'cov', 'WXYZ']]
        non_mapped_ts_ids = list(
            set(input_ts_id) - set(cov_df['ts_id'].unique())
        )
        non_mapped_cov = pd.DataFrame({
            'ts_id': non_mapped_ts_ids,
            'cov': [np.nan] * len(non_mapped_ts_ids),
            'WXYZ': ['Z'] * len(non_mapped_ts_ids)
        })
        cov_df = pd.concat([cov_df, non_mapped_cov], axis=0)
        cov_df = cov_df.reset_index(drop=True)
        return cov_df

    def get_std(self, df1):
        input_ts_id = df1['ts_id'].unique()

        # df1 = df1[df1[target_col]>0]

        std_df = df1.groupby(['ts_id'])[target_col].agg(["std"])

        return std_df

    def calc_interval_mean(self, x, key):
        df = pd.DataFrame({"X": x, "ts_id": key}).reset_index(
            drop=True).reset_index()
        df = df[df.X > 0]
        df["index_shift"] = df["index"].shift(-1)
        df["interval"] = df["index_shift"] - df["index"]
        df = df.dropna(subset=["interval"])
        df['ADI'] = np.mean(df["interval"])
        return df[['ts_id', 'ADI']]

    def calc_adi(self, df):
        # df = self.add_ts_id(df)
        logger.info(
            'Combinations entering adi: {}'.format(df['ts_id'].nunique()))
        dict_of = dict(iter(df.groupby(['ts_id'])))
        logger.info("Total tsids in df: {}".format(df.ts_id.nunique()))
        logger.info("Total dictionary length: {}".format(len(dict_of)))

        list_dict = [
            self.calc_interval_mean(dict_of[x][target_col], x) for x in
            tqdm(dict_of.keys())
        ]

        data = (
            pd.concat(list_dict)
                .reset_index(drop=True)
                .drop_duplicates()
                .reset_index(drop=True)
        )
        logger.info('Combinations exiting adi: {}'.format(data.ts_id.nunique()))
        return data

    def get_PLC_segmentation(self, df, mature_cutoff_date, eol_cutoff_date):
        df1 = df[df[target_col] > 0]
        df1 = df1.groupby(['ts_id']).agg({date_col: [min, max]})

        df1.reset_index(drop=False, inplace=True)
        df1.columns = [' '.join(col).strip() for col in df1.columns.values]

        df1['PLC Status L1'] = 'Mature'
        df1.loc[
            (df1[date_col + ' min'] > mature_cutoff_date), 'PLC Status L1'
        ] = 'NPI'
        df1.loc[
            (df1[date_col + ' max'] <= eol_cutoff_date), 'PLC Status L1'
        ] = 'EOL'

        # df1 = self.add_ts_id(df1)
        df1 = df1[['ts_id', 'PLC Status L1']]
        return df1

    def get_group_mapping(self, seg_df):
        seg_df['Mixed'] = seg_df['ABC'].astype(str) + seg_df['WXYZ'].astype(str)
        seg_df['Group'] = 'Group3'

        group1_mask = seg_df['Mixed'].isin(['AW', 'AX', 'BW', 'BX'])
        seg_df.loc[group1_mask, 'Group'] = 'Group1'

        group2_mask = seg_df['Mixed'].isin(['AY', 'AZ', 'BY', 'BZ'])
        seg_df.loc[group2_mask, 'Group'] = 'Group2'

        return seg_df

    def calc_dem_pat(self, cov_df, adi_df):
        logger.info('Combinations entering calc_dem_pat: {}'.format(
            cov_df.ts_id.nunique()))
        logger.info('Combinations entering calc_dem_pat: {}'.format(
            adi_df.ts_id.nunique()))

        df = pd.merge(cov_df, adi_df, how='left', on='ts_id')

        df["cov2"] = np.power(df["cov"], 2)
        df["classification"] = "Lumpy"
        df.loc[
            (df.ADI >= 1.32) & (df.cov2 < 0.49), "classification"
        ] = "Intermittent"
        df.loc[
            (df.ADI < 1.32) & (df.cov2 >= 0.49), "classification"
        ] = "Erratic"
        df.loc[
            (df.ADI < 1.32) & (df.cov2 < 0.49), "classification"
        ] = "Smooth"
        logger.info(
            'Combinations exiting calc_dem_pat: {}'.format(df.ts_id.nunique()))
        return df[['ts_id', 'classification']]

    def get_start_end_dates_df(self, df, key_col, date_col, target_col,
                               train_max_date, end_date):
        start_end_date_df = (
            df[df[target_col] > 0]
                .groupby(key_col)[date_col]
                .agg({'min', 'max'})
                .reset_index()
                .rename(columns={'min': 'start_date', 'max': 'end_date'})
        )

        start_end_date_df.loc[
            (
                    start_end_date_df['end_date'] > (
                    train_max_date - relativedelta(weeks=eol_cutoff)
            )
            ), 'end_date'
        ] = end_date

        return start_end_date_df

    def get_weekly_segmentation(self, df, df_sales_daily, train_max_date,
                                end_date):
        df = df[df[date_col] <= train_max_date]

        df1 = df[
            df[date_col] > (train_max_date - relativedelta(weeks=52))
            ].copy(deep=True)

        df_std = df_sales_daily[
            df_sales_daily[date_col] > (train_max_date - relativedelta(days=90))
            ].copy(deep=True)

        df1 = self.add_ts_id(df1)

        abc_df = self._calc_abc(df1)
        xyzw_df = self.get_xyzw_classification(df1)
        std_df = self.get_std(df_std)
        adi_df = self.calc_adi(df1)
        demand_pattern_df = self.calc_dem_pat(xyzw_df[['ts_id', 'cov']], adi_df)

        mature_cutoff_date = train_max_date - relativedelta(weeks=52)
        eol_cutoff_date = train_max_date - relativedelta(weeks=13)
        plc_df = self.get_PLC_segmentation(df, mature_cutoff_date,
                                           eol_cutoff_date)
        start_end_date_df = self.get_start_end_dates_df(
            df, key_col='ts_id',
            date_col=date_col,
            target_col=target_col,
            train_max_date=train_max_date,
            end_date=end_date
        )

        seg_df = plc_df.merge(abc_df, on='ts_id', how='outer')
        seg_df = seg_df.merge(xyzw_df, on='ts_id', how='outer')
        seg_df = seg_df.merge(adi_df, on='ts_id', how='outer')
        seg_df = seg_df.merge(demand_pattern_df, on='ts_id', how='outer')
        seg_df = seg_df.merge(start_end_date_df, on='ts_id', how='outer')
        seg_df = seg_df.merge(std_df, on='ts_id', how='outer')

        seg_df = self.get_group_mapping(seg_df)

        drug_class = seg_df[
            ['ts_id', 'total_LY_sales', 'std', 'cov', 'ABC', 'WXYZ']]
        drug_class[[store_col, drug_col]] = drug_class['ts_id'].str.split('_',
                                                                          expand=True)
        drug_class.rename(
            columns={'total_LY_sales': 'net_sales', 'std': 'sales_std_dev',
                     'cov': 'sales_cov', 'ABC': 'bucket_abc',
                     'WXYZ': 'bucket_xyz'}, inplace=True)
        drug_class.drop(columns=['ts_id'], inplace=True)

        # seg_df[[store_col, drug_col]] = seg_df['ts_id'].str.split('_', expand = True)
        # seg_df.drop(columns=['ts_id'],inplace=True)
        # seg_df.rename(columns={'std':'sales_std_dev', 'cov':'sales_cov', 'ABC':'bucket_abcd', 'WXYZ':'bucket_wxyz', 'Mixed':'bucket'}, inplace=True)
        # seg_df['PLC Status L1'] = np.where(seg_df['PLC Status L1']=='NPI', 'New_Product', seg_df['PLC Status L1'])
        # seg_df['start_date'] = seg_df['start_date'].astype(str)
        # seg_df = seg_df[[store_col, drug_col,'PLC Status L1', 'total_LY_sales', 'bucket_abcd', 'bucket_wxyz', 'bucket', 'classification', 'Group', 'sales_std_dev', 'sales_cov', 'ADI', 'start_date' ]]

        # seg_df = pd.merge(seg_df, drug_class[[store_col, 'store_name',  drug_col, ]])

        return seg_df, drug_class
