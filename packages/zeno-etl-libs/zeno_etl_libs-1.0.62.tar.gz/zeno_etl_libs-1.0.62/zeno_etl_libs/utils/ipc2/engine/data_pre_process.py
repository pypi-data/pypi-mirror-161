"""data preparation for drug forecast at store level"""
import pandas as pd
import datetime
import numpy as np

from zeno_etl_libs.utils.ipc2.config_ipc import date_col, store_col, \
    drug_col, target_col, key_col, local_testing


class PreprocessData:

    def add_ts_id(self, df):
        df = df[~df[drug_col].isnull()].reset_index(drop=True)
        df['ts_id'] = (
                df[store_col].astype(int).astype(str)
                + '_'
                + df[drug_col].astype(int).astype(str)
        )
        return df

    def preprocess_sales(self, df, drug_list):

        df.rename(columns={
            'net_sales_quantity': target_col
        }, inplace=True)

        df.rename(columns={
            'sales_date': date_col
        }, inplace=True)

        set_dtypes = {
            store_col: int,
            drug_col: int,
            date_col: str,
            target_col: float
        }
        df = df.astype(set_dtypes)
        df[target_col] = df[target_col].round()

        df[date_col] = pd.to_datetime(df[date_col])

        df = df.groupby(
            [store_col, drug_col, key_col, date_col]
        )[target_col].sum().reset_index()

        df = df[df[drug_col].isin(drug_list[drug_col].unique().tolist())]

        return df

    def get_formatted_data(self, df):

        df_start = df.groupby([key_col])[date_col].min().reset_index().rename(
            columns={date_col: 'sales_start'})
        df = df[[key_col, date_col, target_col]]
        min_date = df[date_col].dropna().min()
        end_date = df[date_col].dropna().max()
        date_range = []
        date_range = pd.date_range(
            start=min_date,
            end=end_date,
            freq='d'
        )
        date_range = list(set(date_range) - set(df[date_col]))

        df = (
            df
                .groupby([date_col] + [key_col])[target_col]
                .sum()
                .unstack()
        )

        for date in date_range:
            df.loc[date, :] = np.nan

        df = (
            df
                .fillna(0)
                .stack()
                .reset_index()
                .rename(columns={0: target_col})
        )

        df = pd.merge(df, df_start, how='left', on=key_col)
        df = df[df[date_col] >= df['sales_start']]
        df[[store_col, drug_col]] = df[key_col].str.split('_', expand=True)
        df[[store_col, drug_col]] = df[[store_col, drug_col]].astype(int)
        return df

    def preprocess_cfr_pr(self, df):

        set_dtypes = {
            store_col: int,
            drug_col: int,
            'loss_quantity': int
        }
        df = df.astype(set_dtypes)
        df['shortbook_date'] = pd.to_datetime(df['shortbook_date'])

        return df

    def merge_cfr_pr(self, sales, cfr_pr):

        df = sales.merge(cfr_pr,
                         left_on=[store_col, drug_col, date_col],
                         right_on=[store_col, drug_col, 'shortbook_date'],
                         how='left')
        df[date_col] = df[date_col].combine_first(df['shortbook_date'])
        df[target_col].fillna(0, inplace=True)
        df['loss_quantity'].fillna(0, inplace=True)
        df[target_col] += df['loss_quantity']
        df.drop(['shortbook_date', 'loss_quantity'], axis=1, inplace=True)

        return df

    def preprocess_calendar(self, df, last_date):
        df.rename(columns={'date': date_col}, inplace=True)
        df[date_col] = pd.to_datetime(df[date_col])

        cal_sales = df.copy()
        cal_sales['week_begin_dt'] = cal_sales.apply(
            lambda x: x[date_col] - datetime.timedelta(x['day_of_week']),
            axis=1)
        cal_sales['month_begin_dt'] = cal_sales.apply(
            lambda x: x['date'] - datetime.timedelta(x['date'].day - 1), axis=1)
        cal_sales['key'] = 1
        ld = pd.to_datetime(last_date)
        cal_sales = cal_sales[cal_sales[date_col] > ld]
        return df, cal_sales

    def merge_calendar(self, sales, calendar):
        df = sales.merge(calendar,
                         how='left',
                         on=date_col
                         )

        # df_week_days_count = df.groupby([key_col, 'year', 'week_of_year'])[date_col].count().reset_index().rename(columns = {date_col:'week_days_count'})
        # df['week_days_count'] = 1
        df['week_begin_dt'] = df.apply(
            lambda x: x[date_col] - datetime.timedelta(x['day_of_week']),
            axis=1)
        df_week_days_count = df.groupby(['ts_id', 'week_begin_dt'])[
            date_col].count().reset_index().rename(
            columns={date_col: 'week_days_count'})
        # df = df.groupby(['ts_id', store_col, drug_col, ]).resample('W-Mon', on =date_col )[target_col].sum().reset_index()
        df = df.groupby(['ts_id', store_col, drug_col, 'week_begin_dt'])[
            target_col].sum().reset_index()
        df = pd.merge(df, df_week_days_count, how='left',
                      on=[key_col, 'week_begin_dt'])
        df = df[df['week_days_count'] == 7].reset_index(drop=True)
        df.drop(columns=['week_days_count'], inplace=True)
        df.rename(columns={'week_begin_dt': date_col}, inplace=True)
        return df

    def preprocess_bill_date(self, df):
        df.rename(columns={'store-id': store_col}, inplace=True)
        df['bill_date'] = pd.to_datetime(df['bill_date'])
        return df

    def merge_first_bill_date(self, sales, first_bill_date):
        df = pd.merge(sales, first_bill_date, on=[store_col])
        df = df[df[date_col] >= df['bill_date']].reset_index(drop=True)
        df.drop(columns=['bill_date'], inplace=True)
        return df

    def make_future_df(self, df):
        start_date_df = (
            df
                .groupby(key_col)[date_col]
                .min()
                .reset_index()
                .rename(columns={date_col: 'start_date'})
        )

        df = df[[key_col, date_col, target_col]]
        end_date = df[date_col].max() + datetime.timedelta(weeks=5)
        min_date = df[date_col].min()
        date_range = pd.date_range(
            start=min_date,
            end=end_date,
            freq="W-MON"
        )
        date_range = list(set(date_range) - set(df[date_col]))

        df = (
            df
                .groupby([date_col] + [key_col])[target_col]
                .sum()
                .unstack()
        )

        for date in date_range:
            df.loc[date, :] = 0

        df = (
            df
                .fillna(0)
                .stack()
                .reset_index()
                .rename(columns={0: target_col})
        )

        df = df.merge(start_date_df, on=key_col, how='left')

        df = df[
            df[date_col] >= df['start_date']
            ]

        df.drop('start_date', axis=1, inplace=True)

        df[[store_col, drug_col]] = df[key_col].str.split('_', expand=True)
        return df

    def preprocess_all(
            self,
            sales=None,
            cfr_pr=None,
            drug_list=None,
            calendar=None,
            first_bill_date=None,
            last_date=None,
    ):
        sales = self.add_ts_id(sales)
        # filter
        #################################################
        if local_testing == 1:
            tsid_list = \
            sales.sort_values(by=['net_sales_quantity'], ascending=False)[
                key_col].unique().tolist()[:10]
            sales = sales[sales[key_col].isin(tsid_list)]
        #################################################
        sales = self.preprocess_sales(sales, drug_list)
        sales = self.get_formatted_data(sales)
        cfr_pr = self.preprocess_cfr_pr(cfr_pr)
        sales_daily = self.merge_cfr_pr(sales, cfr_pr)
        calendar, cal_sales = self.preprocess_calendar(calendar, last_date)
        sales = self.merge_calendar(sales_daily, calendar)
        first_bill_date = self.preprocess_bill_date(first_bill_date)
        sales = self.merge_first_bill_date(sales, first_bill_date)
        sales_pred = self.make_future_df(sales.copy())

        return (
            sales,
            sales_pred,
            cal_sales,
            sales_daily
        )
