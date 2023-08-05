import decimal
import os

# from zeno_etl_libs.queries.mis import mis_queries
#
# from zeno_etl_libs.helper.aws.s3 import S3
# from zeno_etl_libs.db.db import DB
# from zeno_etl_libs.helper import helper

import json
import datetime
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
import pandas as pd
import numpy as np

class Mis:
    def __init__(self,analysis_start_time,analysis_end_time,suffix_to_table,schema_to_select,choose_year,choose_month,rs_db=None,logger=None,mis_queries=None):
        self.analysis_start_time = analysis_start_time
        self.analysis_end_time = analysis_end_time
        self.suffix_to_table = suffix_to_table
        self.schema_to_select = schema_to_select
        self.choose_year = choose_year
        self.choose_month = choose_month
        self.rs_db = rs_db
        self.logger = logger
        self.logger.info('You have instantiated Mis class')
        self.mis_queries = mis_queries

    def sales(self):
        sales_query = self.mis_queries.sales_query.format(schema=self.schema_to_select, suffix_to_table=self.suffix_to_table,
                       analysis_start_time=self.analysis_start_time, analysis_end_time=self.analysis_end_time)


        df = self.rs_db.get_df(sales_query)
        df.columns = [c.replace('-', '_') for c in df.columns]

        return df

    def customer_returns(self):
        customer_returns_query = self.mis_queries.customer_returns_query.format(schema=self.schema_to_select, suffix_to_table=self.suffix_to_table, analysis_start_time=self.analysis_start_time,
                     analysis_end_time=self.analysis_end_time)
        df = self.rs_db.get_df(customer_returns_query)
        df.columns = [c.replace('-', '_') for c in df.columns]
        return df

    def order_source(self):
        order_source_query = self.mis_queries.order_source_query.format(schema=self.schema_to_select, suffix_to_table=self.suffix_to_table, analysis_start_time=self.analysis_start_time,
                   analysis_end_time=self.analysis_end_time)
        order_source = self.rs_db.get_df(order_source_query)
        order_source.columns = [c.replace('-', '_') for c in order_source.columns]
        return order_source

    def store_list(self):
        store_list_query = self.mis_queries.store_list_query.format(schema=self.schema_to_select, suffix_to_table=self.suffix_to_table)
        store_list = self.rs_db.get_df(store_list_query)
        store_list.columns = [c.replace('-', '_') for c in store_list.columns]
        return store_list

    def inventory(self):
        inventory_query = self.mis_queries.inventory_query.format(schema=self.schema_to_select, suffix_to_table=self.suffix_to_table)
        inventory = self.rs_db.get_df(inventory_query)
        inventory.columns = [c.replace('-', '_') for c in inventory.columns]
        return inventory

    def cumulative_consumers_data(self):
        cumulative_consumers_data_query = self.mis_queries.cumulative_consumers_data_query.format(schema=self.schema_to_select, suffix_to_table=self.suffix_to_table)
        cumulative_consumers_data = self.rs_db.get_df(cumulative_consumers_data_query)
        cumulative_consumers_data.columns = [c.replace('-', '_') for c in cumulative_consumers_data.columns]
        return cumulative_consumers_data

    def purchase_from_wc_data(self):
        purchase_from_wc_query = self.mis_queries.purchase_from_wc_query.format(schema=self.schema_to_select, suffix_to_table=self.suffix_to_table,
                       analysis_start_time=self.analysis_start_time, analysis_end_time=self.analysis_end_time)

        df = self.rs_db.get_df(purchase_from_wc_query)
        df.columns = [c.replace('-', '_') for c in df.columns]
        df['wc_purchase_net_value'] = (df['net_value'] / df['1_actual_quantity']) * df['2_actual_quantity']
        return df

    def zippin_return_data(self):
        zippin_return_data_query = self.mis_queries.zippin_return_data_query.format(schema=self.schema_to_select, suffix_to_table=self.suffix_to_table,
                       analysis_start_time=self.analysis_start_time, analysis_end_time=self.analysis_end_time)

        df = self.rs_db.get_df(zippin_return_data_query)
        df.columns = [c.replace('-', '_') for c in df.columns]
        return df

    def workcell_return_data(self):
        workcell_return_data_query = self.mis_queries.workcell_return_data_query.format(schema=self.schema_to_select, suffix_to_table=self.suffix_to_table,
                       analysis_start_time=self.analysis_start_time, analysis_end_time=self.analysis_end_time)

        df = self.rs_db.get_df(workcell_return_data_query)
        df.columns = [c.replace('-', '_') for c in df.columns]
        return df

    def cons_initial_bill_date(self,):
        customers_initial_bill_date_query = self.mis_queries.customers_initial_bill_date.format(schema=self.schema_to_select,
                                                             suffix_to_table=self.suffix_to_table)
        customers_initial_bill_date = self.rs_db.get_df(customers_initial_bill_date_query)
        customers_initial_bill_date.columns = [c.replace('-', '_') for c in customers_initial_bill_date.columns]
        return customers_initial_bill_date

    def local_purchase_data(self):
        local_purchase_data_query = self.mis_queries.local_purchase_data_query.format(schema=self.schema_to_select, suffix_to_table=self.suffix_to_table ,
                       analysis_start_time=self.analysis_start_time, analysis_end_time=self.analysis_end_time)
        local_purchase_data = self.rs_db.get_df(local_purchase_data_query )
        local_purchase_data.columns = [c.replace('-', '_') for c in local_purchase_data.columns]
        return local_purchase_data

    def home_delivery_data(self):
        home_delivery_data_query = self.mis_queries.home_delivery_data_query.format(schema=self.schema_to_select,
                                                                               suffix_to_table=self.suffix_to_table,
                                                                               analysis_start_time=self.analysis_start_time,
                                                                               analysis_end_time=self.analysis_end_time)

        df = self.rs_db.get_df(home_delivery_data_query)
        df.columns = [c.replace('-', '_') for c in df.columns]

        return df

    def delivery_bill_ids(self):
        delivery_bill_ids_query = self.mis_queries.delivery_bill_ids_query.format(schema=self.schema_to_select, suffix_to_table=self.suffix_to_table)
        delivery_bill_ids = self.rs_db.get_df(delivery_bill_ids_query)
        delivery_bill_ids.columns = [c.replace('-', '_') for c in delivery_bill_ids.columns]
        return delivery_bill_ids

    def order_type_tag(self,company, type_, tag):
        if tag == 'breakup':
            if company == 'GOODAID':
                return 'GOODAID'
            # elif type_ in ('ethical'):
            #     return 'ethical'
            # elif type_ in ('generic'):
            #     return 'generic'
            # else:
            #     return 'others'

            elif type_ in ('ethical', 'high-value-ethical'):
                return 'ethical'
            elif type_ in ('generic', 'high-value-generic'):
                return 'generic'
            else:
                return 'others'

        elif tag == 'unified':
            # if type_ in ('ethical'):
            #     return 'ethical'
            # elif type_ in ('generic'):
            #     return 'generic'
            # else:
            #     return 'others'

            if type_ in ('ethical', 'high-value-ethical'):
                return 'ethical'
            elif type_ in ('generic', 'high-value-generic'):
                return 'generic'
            else:
                return 'others'
        else:
            self.logger.info('please provide valid tag')

    def taxable_value(self,quantity,rate,cgst,sgst,igst):
        # igst = 0
        return quantity*rate/(1 + ((cgst+sgst+igst)/100))

    def taxable_value_vat_based(self,quantity,rate,vat):
        quantity = float(quantity)
        rate = float(rate)
        vat = float(vat)
        taxable = (quantity*rate)/(1 + ((vat)/100))
        taxable = float(taxable)
        return taxable

    def taxable_value_vat_based_2(self,value,vat):
        value = float(value)
        vat = float(vat)
        taxable = (value)/(1 + ((vat)/100))
        taxable = float(taxable)
        return taxable

    def gmv_gross_payment(self, Gross, stores):

        gross = Gross.copy(deep = True)

        gross['GMV_sale'] = gross['quantity'] * gross['mrp']
        gross['gross_sale'] = gross['quantity'] * gross['rate']

        gross_sale_summary = gross.groupby(['store_id', 'type1', 'category',
                              'payment_method', 'order_source'],
                                           as_index=False).agg({
            'quantity': ['sum'],
            'GMV_sale': ['sum'],
            'gross_sale': ['sum']
        }).reset_index(drop=True)
        gross_sale_summary.columns = ["_".join(x) for x in gross_sale_summary.columns.ravel()]

        gross_sale_summary.fillna(0, inplace=True)

        gross_sale = pd.merge(left=gross_sale_summary, right=stores,
                                  how='left',
                                  left_on=['store_id_'],
                                  right_on=['store_id'])

        gross_sale.rename(columns={'type1_': 'type1',
                                       'category_': 'category',
                                       'payment_method_': 'payment_method',
                                       'order_source_': 'order_source',
                                       'quantity_sum': 'quantity',
                                       'GMV_sale_sum': 'GMV_sales',
                                       'gross_sale_sum': 'gross_sales'}, inplace=True)

        gross_sale[['GMV_sales', 'gross_sales']] = gross_sale[['GMV_sales', 'gross_sales']].astype(float)

        gross_sale.fillna(0, inplace=True)

        # #GMV
        df_gross_returns2a = gross_sale.groupby(['store_id', 'store_name',
                                                     'type1', 'order_source'])[['GMV_sales']].sum().reset_index()
        df_gross_returns2 = pd.pivot_table(df_gross_returns2a,
                                           values='GMV_sales',
                                           index=['type1', 'order_source'],
                                           columns=['store_name']).reset_index()
        df_gross_returns2['tag_flag'] = 'gmv'

        # GROSS
        df_gross_returns3a = gross_sale.groupby(['store_id', 'store_name',
                                                     'type1', 'order_source'])[['gross_sales']].sum().reset_index()
        df_gross_returns3 = pd.pivot_table(df_gross_returns3a,
                                           values='gross_sales',
                                           index=['type1', 'order_source'],
                                           columns=['store_name']).reset_index()
        df_gross_returns3['tag_flag'] = 'gross'

        # Payment
        gross_sale['payment'] = np.where(gross_sale['payment_method'].isin(['cash', 'card']),
                                             gross_sale['payment_method'], 'upi')
        df_gross_returns4a = gross_sale.groupby(['store_id', 'store_name',
                                                     'payment', 'order_source'])[['gross_sales']].sum().reset_index()
        df_gross_returns4 = pd.pivot_table(df_gross_returns4a,
                                           values='gross_sales',
                                           index=['payment', 'order_source'],
                                           columns=['store_name']).reset_index()
        df_gross_returns4['tag_flag'] = 'payment'

        gmv_gross_payment = pd.concat([df_gross_returns2,
                                       df_gross_returns3,
                                       df_gross_returns4], sort=True)

        cols_to_move = ['tag_flag', 'type1', 'payment', 'order_source']
        gmv_gross_payment = gmv_gross_payment[cols_to_move +
                                              [col for col in gmv_gross_payment.columns
                                               if col not in cols_to_move]]

        return gmv_gross_payment

    def netsale_tax_cogs(self,Gross,Returns,stores):

        gross = Gross.copy(deep = True)
        returns = Returns.copy(deep = True)

        gross['gross_sale'] = gross['quantity'] * gross['rate']
        gross['gross_COGS'] = gross['quantity'] * gross['wc_ptr']

        gross['gross_sale_taxable'] = np.vectorize(self.taxable_value)(gross['quantity'], gross['rate'],
                                                                gross['cgst_rate'], gross['sgst_rate'],
                                                                gross['igst_rate'])
        gross['gross_COGS_taxable'] = np.vectorize(self.taxable_value)(gross['quantity'], gross['wc_ptr'],
                                                                       gross['cgst_rate'],
                                                                       gross['sgst_rate'], gross['igst_rate'])


        gross_sale_summary = gross.groupby(['store_id', 'type1', 'order_source'],
                                 as_index=False).agg({
            'quantity': ['sum'],
            'gross_sale': ['sum'],
            'gross_COGS': ['sum'],
            'gross_sale_taxable':['sum'],
            'gross_COGS_taxable':['sum']
        }).reset_index(drop=True)
        gross_sale_summary.columns = ["_".join(x) for x in gross_sale_summary.columns.ravel()]

        returns['gross_returns'] = returns['rate'] * returns['returned_quantity']
        returns['returns_COGS'] = returns['wc_ptr'] * returns['returned_quantity']

        returns['gross_returns_taxable'] = np.vectorize(self.taxable_value)(returns['returned_quantity'], returns['rate'],
                                                                       returns['cgst_rate'], returns['sgst_rate'],
                                                                       returns['igst_rate'])
        returns['returns_COGS_taxable'] = np.vectorize(self.taxable_value)(returns['returned_quantity'], returns['wc_ptr'],
                                                                       returns['cgst_rate'],
                                                                       returns['sgst_rate'], returns['igst_rate'])

        returns_summary = returns.groupby(['store_id', 'type1', 'order_source'],
                                          as_index=False).agg({
            'returned_quantity':['sum'],
            'gross_returns':['sum'],
            'returns_COGS':['sum'],
            'gross_returns_taxable': ['sum'],
            'returns_COGS_taxable': ['sum']}).reset_index(drop=True)
        returns_summary.columns = ["_".join(x) for x in returns_summary.columns.ravel()]

        gross_returns = pd.merge(left=gross_sale_summary, right=returns_summary,
                                 how='left', on=['store_id_', 'type1_', 'order_source_'])

        gross_returns.fillna(0, inplace=True)

        gross_returns['net_sale'] = gross_returns['gross_sale_sum'] - gross_returns['gross_returns_sum']
        gross_returns['net_sale_taxable'] = gross_returns['gross_sale_taxable_sum'] - gross_returns['gross_returns_taxable_sum']
        gross_returns['net_COGS'] = gross_returns['gross_COGS_sum'] - gross_returns['returns_COGS_sum']
        gross_returns['net_COGS_taxable'] = gross_returns['gross_COGS_taxable_sum'] - gross_returns[
            'returns_COGS_taxable_sum']

        gross_returns1 = pd.merge(left=gross_returns, right=stores,
                                  how='left',
                                  left_on=['store_id_'],
                                  right_on=['store_id'])

        gross_returns1.rename(columns={  'type1_': 'type1',
                                         'order_source_':'order_source',
                                         'quantity_sum':'quantity',
                                         'gross_sale_sum': 'gross_sales',
                                         'gross_COGS_sum': 'gross_COGS',
                                         'gross_sale_taxable_sum': 'gross_sale_taxable',
                                         'gross_COGS_taxable_sum': 'gross_COGS_taxable',
                                         'returned_quantity_sum': 'returned_quantity',
                                         'gross_returns_sum': 'gross_returns',
                                         'returns_COGS_sum': 'returns_COGS',
                                         'gross_returns_taxable_sum': 'gross_returns_taxable',
                                         'returns_COGS_taxable_sum': 'returns_COGS_taxable'}, inplace=True)

        gross_returns1[['net_sale','net_sale_taxable','net_COGS_taxable']] = gross_returns1[['net_sale','net_sale_taxable','net_COGS_taxable']].astype(float)

        gross_returns2 = pd.pivot_table(gross_returns1,
                                        values='net_sale',
                                        index=['type1', 'order_source'],
                                        columns=['store_name']).reset_index()
        gross_returns2['tag_flag'] = 'net_sale'

        gross_returns3 = pd.pivot_table(gross_returns1,
                                        values='net_sale_taxable',
                                        index=['type1', 'order_source'],
                                        columns=['store_name']).reset_index()
        gross_returns3['tag_flag'] = 'net_sale_taxable'

        gross_returns4 = pd.pivot_table(gross_returns1,
                                        values='net_COGS_taxable',
                                        index=['type1', 'order_source'],
                                        columns=['store_name']).reset_index()
        gross_returns4['tag_flag'] = 'net_COGS_taxable'

        net_sale_taxes_cogs = pd.concat([gross_returns2,
                                         gross_returns3,
                                         gross_returns4])

        cols_to_move = ['tag_flag', 'type1', 'order_source']
        net_sale_taxes_cogs = net_sale_taxes_cogs[cols_to_move +
                                                  [col for col in net_sale_taxes_cogs.columns
                                                   if col not in cols_to_move]]

        return net_sale_taxes_cogs

    def inventory_ageing(self, Inventory, stores, mis_tag = 'breakup'):

        inventory_data = Inventory.copy(deep = True)

        inventory_data['value'] = inventory_data['quantity'] * inventory_data['final_ptr']
        inventory_data['days'] = (pd.to_datetime('today') - inventory_data['created_at']).dt.days
        conditions = [
            (inventory_data['days'] >= 0) & (inventory_data['days'] <= 30),
            (inventory_data['days'] >= 31) & (inventory_data['days'] <= 60),
            (inventory_data['days'] >= 61) & (inventory_data['days'] <= 90),
            (inventory_data['days'] >= 91)]
        choices = ['0_30', '31_60', '61_90', '90+']
        inventory_data['age_bracket'] = np.select(conditions, choices)

        inventory_data['vat'] = inventory_data['vat'].fillna(0)
        inventory_data['vat'] = inventory_data['vat'].astype(float)

        inventory_data['taxable'] = np.vectorize(self.taxable_value_vat_based)(inventory_data['quantity'],
                                                                               inventory_data['final_ptr'],
                                                                               inventory_data['vat'])

        df_ageing = inventory_data.groupby(['store_id', 'type1', 'category', 'age_bracket'],
                                  as_index=False).agg({
            'drug_id': pd.Series.nunique,
            'value': ['sum'],
            'taxable': ['sum']}).reset_index(drop=True)
        df_ageing.columns = ["_".join(x) for x in df_ageing.columns.ravel()]

        df_ageing = pd.merge(left=df_ageing, right=stores,
                             how='left', left_on=['store_id_'], right_on=['store_id'])

        df_ageing_grp = df_ageing.groupby(['store_id_', 'store_name',
                                           'type1_', 'age_bracket_'])[['taxable_sum']].sum().reset_index()

        # generic
        df_ageing_generic = df_ageing_grp[df_ageing_grp['type1_'] == 'generic']
        df_ageing_generic1 = pd.pivot_table(df_ageing_generic,
                                            values='taxable_sum',
                                            index=['type1_', 'age_bracket_'],
                                            columns=['store_name']).reset_index()
        # ethical
        df_ageing_ethical = df_ageing_grp[df_ageing_grp['type1_'] == 'ethical']
        df_ageing_ethical1 = pd.pivot_table(df_ageing_ethical,
                                            values='taxable_sum',
                                            index=['type1_', 'age_bracket_'],
                                            columns=['store_name']).reset_index()
        # others
        df_ageing_grp_others = df_ageing.groupby(['store_id_', 'store_name',
                                                  'type1_'])[['taxable_sum']].sum().reset_index()
        df_ageing_others = df_ageing_grp_others[df_ageing_grp_others['type1_'] == 'others']
        df_ageing_others1 = pd.pivot_table(df_ageing_others,
                                           values='taxable_sum',
                                           index=['type1_'],
                                           columns=['store_name']).reset_index()

        if mis_tag == 'breakup':
            # GOODAID
            df_ageing_goodaid = df_ageing_grp[df_ageing_grp['type1_'] == 'GOODAID']
            df_ageing_goodaid1 = pd.pivot_table(df_ageing_goodaid,
                                                values='taxable_sum',
                                                index=['type1_', 'age_bracket_'],
                                                columns=['store_name']).reset_index()

            inventory_ageing = pd.concat([df_ageing_generic1,
                                          df_ageing_ethical1,
                                          df_ageing_others1,
                                          df_ageing_goodaid1],sort=True)

        elif mis_tag=='unified':
            inventory_ageing = pd.concat([df_ageing_generic1,
                                          df_ageing_ethical1,
                                          df_ageing_others1],sort=True)
        else:
            self.logger.info('please pass correct mis_tag')
            return None

        inventory_ageing['tag_flag'] = 'inventory_ageing'

        cols_to_move = ['tag_flag', 'type1_', 'age_bracket_']
        inventory_ageing = inventory_ageing[cols_to_move +
                                            [col for col in inventory_ageing.columns
                                             if col not in cols_to_move]]
        inventory_ageing.rename(columns={'type1_': 'type1'}, inplace=True)

        return inventory_ageing

    def near_expiry(self,Inventory,stores,mis_tag = 'breakup'):
        inventory_data = Inventory.copy(deep=True)

        inventory_data['value'] = inventory_data['quantity'] * inventory_data['final_ptr']

        inventory_data['expiry_date'] = pd.to_datetime(inventory_data['expiry'], format='%Y-%m-%d %H:%M:%S',
                                                       errors='coerce')

        inventory_data['days_to_expiry'] = (pd.to_datetime('today') - inventory_data['expiry_date']).dt.days

        inventory_data1 = inventory_data[
            (inventory_data['days_to_expiry'] < 0) & (inventory_data['days_to_expiry'] > -90)]

        inventory_data1['taxable'] = np.vectorize(self.taxable_value_vat_based)(inventory_data1['quantity'], inventory_data1['final_ptr'],inventory_data1['vat'])

        near_expiry = inventory_data1.groupby(['store_id', 'type1'],
                                     as_index=False).agg({
            'value': ['sum'],
            'taxable': ['sum']}).reset_index(drop=True)
        near_expiry.columns = ["_".join(x) for x in near_expiry.columns.ravel()]

        near_expiry = pd.merge(left=near_expiry, right=stores,
                               how='left', left_on=['store_id_'],
                               right_on=['store_id'])

        # generic
        near_expiry_generic = near_expiry[near_expiry['type1_'] == 'generic']
        near_expiry_generic1 = pd.pivot_table(near_expiry_generic,
                                              values='taxable_sum',
                                              index=['type1_'],
                                              columns=['store_name']).reset_index()
        # ethical
        near_expiry_ethical = near_expiry[near_expiry['type1_'] == 'ethical']
        near_expiry_ethical1 = pd.pivot_table(near_expiry_ethical,
                                              values='taxable_sum',
                                              index=['type1_'],
                                              columns=['store_name']).reset_index()
        # others
        near_expiry_others = near_expiry[near_expiry['type1_'] == 'others']
        near_expiry_others1 = pd.pivot_table(near_expiry_others,
                                             values='taxable_sum',
                                             index=['type1_'],
                                             columns=['store_name']).reset_index()
        if mis_tag == 'breakup':
            near_expiry_goodaid = near_expiry[near_expiry['type1_'] == 'GOODAID']

            # If there are no items in near expiry for goodaid
            if len(near_expiry_goodaid)!= 0:
                near_expiry_goodaid1 = pd.pivot_table(near_expiry_goodaid,
                                                      values='taxable_sum',
                                                      index=['type1_'],
                                                      columns=['store_name']).reset_index()
            else:
                near_expiry_goodaid1 = near_expiry_ethical1.copy(deep=True)
                near_expiry_goodaid1.loc[:] = np.nan
                near_expiry_goodaid1['type1_'][0] = 'GOODAID'

            near_expiry = pd.concat([near_expiry_generic1,
                                     near_expiry_ethical1,
                                     near_expiry_others1,
                                     near_expiry_goodaid1],sort=True)

        elif mis_tag=='unified':
            near_expiry = pd.concat([near_expiry_generic1,
                                     near_expiry_ethical1,
                                     near_expiry_others1],sort=True)
        else:
            self.logger.info('please pass correct mis_tag')
            return None


        near_expiry['tag_flag'] = 'near_expiry'

        cols_to_move = ['tag_flag', 'type1_']
        near_expiry = near_expiry[cols_to_move +
                                  [col for col in near_expiry.columns
                                   if col not in cols_to_move]]
        near_expiry.rename(columns={'type1_': 'type1'}, inplace=True)

        return near_expiry

    def sales_by_volume(self,Sales,stores):

        sales = Sales.copy(deep = True)

        generic_volume = sales.groupby(['store_id',
                                        'type1', 'order_source'])[['quantity']].sum().reset_index().rename(
            columns={'quantity': "generic_volume"})

        generic_volume = pd.merge(left=generic_volume, right=stores,
                                  how='left', left_on=['store_id'],
                                  right_on=['store_id'])

        generic_volume = pd.pivot_table(generic_volume,
                                         values='generic_volume',
                                         index=['type1', 'order_source'],
                                         columns=['store_name']).reset_index()

        generic_volume['tag_flag'] = 'sales_by_volume'

        return generic_volume

    def gross_rev_chronic_acute(self,Sales,Returns,stores):
        sales = Sales.copy(deep = True)
        returns = Returns.copy(deep = True)

        sales['COGS'] = sales['quantity'] * sales['final_ptr']
        df_a1a = sales.groupby(['store_id', 'type1', 'category', 'order_source'],
                               as_index=False).agg({
            'value': ['sum'],
            'quantity': ['sum'],
            'COGS': ['sum'],
            'bill_id': pd.Series.nunique,
            'drug_id': pd.Series.nunique}).reset_index(drop=True)
        df_a1a.columns = ["_".join(x) for x in df_a1a.columns.ravel()]

        returns['returned_value'] = returns['returned_quantity'] * returns['rate']
        returns['returned_COGS'] = returns['returned_quantity'] * returns['final_ptr']

        df_b2 = returns.groupby(['store_id', 'type1', 'category', 'order_source'],
                              as_index=False).agg({
            'returned_value': ['sum'],
            'returned_quantity': ['sum'],
            'returned_COGS': ['sum'],
            'returned_bill_id': pd.Series.nunique,
            'returned_drug_id': pd.Series.nunique}).reset_index(drop=True)
        df_b2.columns = ["_".join(x) for x in df_b2.columns.ravel()]

        df_a_b = pd.merge(left=df_a1a, right=df_b2,
                          how='left', on=['store_id_', 'type1_',
                                          'category_', 'order_source_'])
        df_a_b.fillna(0, inplace=True)

        df_a_b['net_sale'] = df_a_b['value_sum'] - df_a_b['returned_value_sum']
        df_a_b['net_COGS'] = df_a_b['COGS_sum'] - df_a_b['returned_COGS_sum']
        df_a_b['net_quantity'] = df_a_b['quantity_sum'] - df_a_b['returned_quantity_sum']

        df_a4 = df_a_b.groupby(['store_id_', 'category_',
                                'type1_', 'order_source_'],
                               as_index=False).agg({
            'net_sale': ['sum'],
            'net_quantity': ['sum'],
            'net_COGS': ['sum'],
            'bill_id_nunique': ['sum'],
            'drug_id_nunique': ['sum']}).reset_index(drop=True)
        df_a4.columns = ["_".join(x) for x in df_a4.columns.ravel()]

        df_a4 = pd.merge(left=df_a4, right=stores,
                         how='left', left_on=['store_id__'],
                         right_on=['store_id'])

        df_a5 = df_a4[df_a4['category__'] == 'chronic']
        df_a5_sale = df_a5.groupby(['store_id__', 'store_name',
                                    'category__', 'type1__', 'order_source__'])[['net_sale_sum']].sum().reset_index()
        df_a5_qty = df_a5.groupby(['store_id__', 'store_name',
                                   'category__', 'type1__', 'order_source__'])[['net_quantity_sum']].sum().reset_index()

        df_a5_sale['net_sale_sum'] = df_a5_sale['net_sale_sum'].astype(float)

        gross_rev_chronic_sale = pd.pivot_table(df_a5_sale,
                                                values='net_sale_sum',
                                                index=['category__', 'type1__', 'order_source__'],
                                                columns=['store_name']).reset_index()

        df_a5_qty['net_quantity_sum'] = df_a5_qty['net_quantity_sum'].astype(float)

        gross_rev_chronic_vol = pd.pivot_table(df_a5_qty,
                                               values='net_quantity_sum',
                                               index=['category__', 'type1__', 'order_source__'],
                                               columns=['store_name']).reset_index()

        df_a6 = df_a4[df_a4['category__'] == 'acute']
        df_a6_sale = df_a6.groupby(['store_id__', 'store_name',
                                    'category__', 'type1__', 'order_source__'])[['net_sale_sum']].sum().reset_index()
        df_a6_qty = df_a6.groupby(['store_id__', 'store_name',
                                   'category__', 'type1__', 'order_source__'])[['net_quantity_sum']].sum().reset_index()

        df_a6_sale['net_sale_sum'] = df_a6_sale['net_sale_sum'].astype(float)

        gross_rev_acute_sale = pd.pivot_table(df_a6_sale,
                                              values='net_sale_sum',
                                              index=['category__', 'type1__', 'order_source__'],
                                              columns=['store_name']).reset_index()

        df_a6_qty['net_quantity_sum'] = df_a6_qty['net_quantity_sum'].astype(float)

        gross_rev_acute_vol = pd.pivot_table(df_a6_qty,
                                             values='net_quantity_sum',
                                             index=['category__', 'type1__', 'order_source__'],
                                             columns=['store_name']).reset_index()

        gross_rev_chronic_sale_vol = pd.concat([gross_rev_chronic_sale,
                                                gross_rev_chronic_vol])
        gross_rev_chronic_sale_vol['tag_flag'] = 'gross_rev_chronic_sale_vol'
        gross_rev_chronic_sale_vol.rename(columns={'type1__': 'type1'}, inplace=True)
        gross_rev_chronic_sale_vol.rename(columns={'category__': 'category'}, inplace=True)
        gross_rev_chronic_sale_vol.rename(columns={'order_source__': 'order_source'}, inplace=True)

        gross_rev_acute_sale_vol = pd.concat([gross_rev_acute_sale,
                                              gross_rev_acute_vol])
        gross_rev_acute_sale_vol['tag_flag'] = 'gross_rev_acute_sale_vol'
        gross_rev_acute_sale_vol.rename(columns={'type1__': 'type1'}, inplace=True)
        gross_rev_acute_sale_vol.rename(columns={'category__': 'category'}, inplace=True)
        gross_rev_acute_sale_vol.rename(columns={'order_source__': 'order_source'}, inplace=True)

        return gross_rev_chronic_sale_vol, gross_rev_acute_sale_vol

    def cummulative_cons(self, Cumulative_consumers_data, mis_tag):

        cumulative_consumers_data = Cumulative_consumers_data.copy(deep=True)

        all_time_cons1 = pd.pivot_table(cumulative_consumers_data,
                                        values='total_cons',
                                        columns=['store_name']).reset_index()

        if mis_tag == 'breakup':

            cumulative_consumers_data.rename(columns={'generic_without_gaid_cons': 'total_generic_cons'}, inplace=True)

            all_time_generic_cons1 = pd.pivot_table(cumulative_consumers_data,
                                                    values='total_generic_cons',
                                                    columns=['store_name']).reset_index()

            all_time_gaid_cons1 = pd.pivot_table(cumulative_consumers_data,
                                                 values='total_gaid_cons',
                                                 columns=['store_name']).reset_index()

        else:
            cumulative_consumers_data.rename(columns={'generic_cons': 'total_generic_cons'}, inplace=True)
            all_time_generic_cons1 = pd.pivot_table(cumulative_consumers_data,
                                                    values='total_generic_cons',
                                                    columns=['store_name']).reset_index()

        all_time_chronic_cons1 = pd.pivot_table(cumulative_consumers_data,
                                                values='total_chronic_cons',
                                                columns=['store_name']).reset_index()

        cumulative_consumers_data['total_acute_cons'] = cumulative_consumers_data['total_cons'] - \
                                                        cumulative_consumers_data['total_chronic_cons']

        all_time_acute_cons1 = pd.pivot_table(cumulative_consumers_data,
                                              values='total_acute_cons',
                                              columns=['store_name']).reset_index()

        if mis_tag == 'breakup':
            cummulative_cons = pd.concat([all_time_cons1, all_time_generic_cons1,
                                          all_time_gaid_cons1,
                                          all_time_chronic_cons1, all_time_acute_cons1], sort=True)
        else:
            cummulative_cons = pd.concat([all_time_cons1, all_time_generic_cons1,
                                          all_time_chronic_cons1, all_time_acute_cons1], sort=True)

        cummulative_cons.rename(columns={'index': 'tag_flag'}, inplace=True)

        return cummulative_cons

    def total_cons_mis_month(self,Sales, Stores):
        sales = Sales.copy(deep = True)
        stores = Stores.copy(deep = True)

        sales = pd.merge(left=sales, right=stores,
                                  how='left', on=['store_id'])

        total_cons = sales.groupby(['store_id',
                                    'store_name', 'order_source'])[['patient_id']].nunique().reset_index().rename(
            columns={'patient_id': "total_consumers_MIS_month"})
        total_cons['tag_flag'] = 'total_cons_mis_month'

        total_cons_mis_month = pd.pivot_table(total_cons,
                                              values='total_consumers_MIS_month',
                                              index=['tag_flag', 'order_source'],
                                              columns=['store_name']).reset_index()

        # total_cons_mis_month.rename(columns={'index': 'tag_flag'}, inplace=True)

        return total_cons_mis_month

    def category_wise_customer_type_count(self,Sales,Store):
        sales = Sales.copy(deep = True)
        stores = Store.copy(deep = True)

        sales = pd.merge(left=sales, right=stores,
                                  how='left', on=['store_id'])

        sales['flag'] = np.where(sales['category'] == "chronic", 1, 0)

        sales_chronic = sales[sales['category'] == 'chronic']
        sales_chronic.loc[:,'tag_flag'] = "customer_type_chronic"
        df49 = sales_chronic.groupby(['store_id', 'store_name',
                                      'category', 'order_source', 'tag_flag'])[
            ['patient_id']].nunique().reset_index().rename(
            columns={'patient_id': "customer_type_chronic"})
        customer_type_chronic = pd.pivot_table(df49,
                                               values='customer_type_chronic',
                                               index=['tag_flag', 'category', 'order_source'],
                                               columns=['store_name']).reset_index()

        sales_acute = sales[sales['category'] == 'acute']
        sales_acute.loc[:,'tag_flag'] = "customer_type_acute"
        df50 = sales_acute.groupby(['store_id', 'store_name',
                                    'category', 'order_source', 'tag_flag'])[
            ['patient_id']].nunique().reset_index().rename(
            columns={'patient_id': "customer_type_acute"})
        customer_type_acute = pd.pivot_table(df50,
                                             values='customer_type_acute',
                                             index=['tag_flag', 'category', 'order_source'],
                                             columns=['store_name']).reset_index()

        category_wise_customer_type = pd.concat([customer_type_chronic, customer_type_acute])

        # customer_type.rename(columns={'index': 'tag_flag'}, inplace=True)

        return category_wise_customer_type

    def new_customers(self,Sales,All_cons_initial_bill_date,Stores):

        sales = Sales.copy(deep = True)
        all_cons_initial_bill_date = All_cons_initial_bill_date.copy(deep = True)
        stores = Stores.copy(deep= True)

        mis_month_cons_min_bill_date = sales.groupby(['store_id',
                                                      'order_source', 'patient_id'])[['created_at']].min().reset_index()

        new_cons_1 = pd.merge(left=all_cons_initial_bill_date, right=mis_month_cons_min_bill_date,
                              how='inner', on=['store_id', 'patient_id', 'created_at'])

        new_cons_1['flag'] = "new_cons"

        new_cons = new_cons_1.groupby(['store_id', 'order_source'])[['patient_id']].nunique().reset_index().rename(
            columns={'patient_id': "new_consumers"})

        new_cons = pd.merge(left=new_cons, right=stores,
                            how='left',
                            on=['store_id'])
        new_cons['tag_flag'] = 'new_consumers'

        new_cons_total = pd.pivot_table(new_cons,
                                        values='new_consumers',
                                        index=['tag_flag', 'order_source'],
                                        columns=['store_name']).reset_index()

        # new chronic consumers
        df_fe = pd.merge(left=new_cons_1[['store_id', 'order_source',
                                          'patient_id', 'flag']],
                         right=sales,
                         how='left',
                         on=['store_id', 'order_source', 'patient_id'])
        new_cons_chronic = df_fe.groupby(['store_id',
                                          'category', 'order_source'])[['patient_id']].nunique().reset_index().rename(
            columns={'patient_id': "new_chronic_consumers"})
        new_cons_chronic1 = new_cons_chronic[new_cons_chronic['category'].isin(['chronic'])]

        new_cons_chronic1 = pd.merge(left=new_cons_chronic1, right=stores,
                                     how='left',
                                     on=['store_id'])
        new_cons_chronic1['tag_flag'] = 'new_chronic_consumers'

        new_cons_chronic2 = pd.pivot_table(new_cons_chronic1,
                                           values='new_chronic_consumers',
                                           index=['tag_flag', 'order_source'],
                                           columns=['store_name']).reset_index()

        new_customers = pd.concat([new_cons_total, new_cons_chronic2],sort=True)

        return new_customers

    def tot_repeat_consumers(self, Sales,All_cons_initial_bill_date,Stores ):
        sales = Sales.copy(deep=True)
        all_cons_initial_bill_date = All_cons_initial_bill_date.copy(deep=True)
        stores = Stores.copy(deep=True)

        total_cons = sales.groupby(['store_id',
                                    'order_source'])[['patient_id']].nunique().reset_index().rename(
            columns={'patient_id': "total_consumers"})

        aug_cons_min = sales.groupby(['store_id', 'order_source', 'patient_id'])[['created_at']].min().reset_index()

        aug_new_cons = pd.merge(left=all_cons_initial_bill_date, right=aug_cons_min,
                                how='inner', on=['store_id', 'patient_id', 'created_at'])

        new_cons = aug_new_cons.groupby(['store_id', 'order_source'])[['patient_id']].nunique().reset_index().rename(
            columns={'patient_id': "new_consumers"})

        repeat_cons = pd.merge(left=total_cons, right=new_cons,
                               how='left', on=['store_id', 'order_source'])
        repeat_cons['repeat_consumers'] = repeat_cons['total_consumers'] - repeat_cons['new_consumers']

        repeat_cons = pd.merge(left=repeat_cons, right=stores,
                               how='left',
                               on=['store_id'])
        repeat_cons['tag_flag'] = 'repeat_consumers'

        repeat_cons1 = pd.pivot_table(repeat_cons,
                                      values='repeat_consumers',
                                      index=['tag_flag', 'order_source'],
                                      columns=['store_name']).reset_index()

        # repeat_cons1.rename(columns={'index': 'tag_flag'}, inplace=True)

        return repeat_cons1

    def new_cons_vol_qty(self, Sales, All_cons_initial_bill_date, Stores):
        sales = Sales.copy(deep=True)
        all_cons_initial_bill_date = All_cons_initial_bill_date.copy(deep=True)
        stores = Stores.copy(deep=True)

        aug_cons_min = sales.groupby(['store_id', 'order_source', 'patient_id'])[['created_at']].min().reset_index()

        aug_new_cons = pd.merge(left=all_cons_initial_bill_date, right=aug_cons_min,
                                how='inner', on=['store_id', 'patient_id', 'created_at'])

        new_cons = aug_new_cons.groupby(['store_id', 'order_source'])[['patient_id']].nunique().reset_index().rename(
            columns={'patient_id': "new_consumers"})

        aug_value_volumne = sales.groupby(['store_id', 'order_source', 'patient_id'],
                                          as_index=False).agg({
            'drug_id': pd.Series.nunique,
            'quantity': ['sum'],
            'value': ['sum']}).reset_index(drop=True)

        aug_value_volumne.columns = ["_".join(x) for x in aug_value_volumne.columns.ravel()]

        aug_value_volumne.rename(columns={'store_id_': "store_id",
                                          'patient_id_': "patient_id",
                                          'order_source_': "order_source"}, inplace=True)

        new_cons_value_vol = pd.merge(left=aug_new_cons, right=aug_value_volumne,
                                      how='left', on=['store_id', 'order_source', 'patient_id'])

        new_cons_value_vol1 = new_cons_value_vol.groupby(['store_id', 'order_source'],
                                                         as_index=False).agg({
            'quantity_sum': ['sum'],
            'value_sum': ['sum']}).reset_index(drop=True)
        new_cons_value_vol1.columns = ["_".join(x) for x in new_cons_value_vol1.columns.ravel()]

        new_cons_value_vol2 = pd.merge(left=new_cons_value_vol1, right=stores,
                                       how='left',
                                       left_on=['store_id_'],
                                       right_on=['store_id'])

        new_cons_value_vol2['value_sum_sum'] = new_cons_value_vol2['value_sum_sum'].astype(float)

        new_cons_volume = pd.pivot_table(new_cons_value_vol2,
                                         values='value_sum_sum',
                                         index=['order_source_'],
                                         columns=['store_name']).reset_index()
        new_cons_volume['tag_flag'] = 'new_consumer_value'

        new_cons_value_vol2['quantity_sum_sum'] = new_cons_value_vol2['quantity_sum_sum'].astype(float)

        new_cons_qty = pd.pivot_table(new_cons_value_vol2,
                                      values='quantity_sum_sum',
                                      index=['order_source_'],
                                      columns=['store_name']).reset_index()
        new_cons_qty['tag_flag'] = 'new_consumer_qty'

        new_cons_vol_qty = pd.concat([new_cons_volume, new_cons_qty], sort=True)

        new_cons_vol_qty.rename(columns={'order_source_': "order_source"}, inplace=True)

        # new_cons_vol_qty.rename(columns={'index': 'tag_flag'}, inplace=True)

        # new_cons_vol_qty.loc[new_cons_vol_qty.tag_flag == 'quantity_sum_sum', 'tag_flag'] = 'new_consumer_qty'
        # new_cons_vol_qty.loc[new_cons_vol_qty.tag_flag == 'value_sum_sum', 'tag_flag'] = 'new_consumer_value'

        return new_cons_vol_qty

    def total_bills_new_repeat(self, Sales, All_cons_initial_bill_date, Stores,choose_year,choose_month):
        sales = Sales.copy(deep=True)
        df1 = All_cons_initial_bill_date.copy(deep=True)
        stores = Stores.copy(deep=True)

        df1['year'] = df1['created_at'].dt.year
        df1["month"] = df1['created_at'].dt.month

        df1 = df1[(df1['year'] == int(choose_year)) & (df1['month'] == int(choose_month))]

        sales['flag'] = np.where(sales['category'] == "chronic", 1, 0)

        df2 = sales.groupby(['store_id', 'order_source', 'patient_id'])[['flag']].sum().reset_index()
        df2['check'] = np.where(df2['flag'] > 0, "chronic", "acute")

        df3 = pd.merge(left=df1, right=df2,
                       how='left', on=['store_id', 'patient_id'])

        df5 = pd.merge(left=df2, right=df1,
                       how='left', on=['store_id', 'patient_id'])
        df6 = df5[df5['year'].isnull()]

        df9 = sales.groupby(['store_id', 'order_source', 'patient_id'])[['bill_id']].nunique().reset_index()
        df10 = pd.merge(left=df3, right=df9,
                        how='left', on=['store_id', 'order_source', 'patient_id'])

        df11 = df10.groupby(['store_id', 'order_source'])[['bill_id']].sum().reset_index().rename(columns={
            "bill_id": "new_consumers_bills_count"})

        df12 = pd.merge(left=df6, right=df9,
                        how='left', on=['store_id', 'order_source', 'patient_id'])

        df13 = df12.groupby(['store_id', 'order_source'])[['bill_id']].sum().reset_index().rename(columns={
            "bill_id": "repeat_consumers_bills_count"})

        df14 = pd.merge(left=df11, right=df13,
                        how='left', on=['store_id', 'order_source'])

        df14 = pd.merge(left=df14, right=stores, how='left', on=['store_id'])

        total_bills_new = pd.pivot_table(df14,
                                         values='new_consumers_bills_count',
                                         index='order_source',
                                         columns=['store_name']).reset_index()
        total_bills_new['tag_flag'] = 'new_consumers_bills_count'

        total_bills_repeat = pd.pivot_table(df14,
                                            values='repeat_consumers_bills_count',
                                            index='order_source',
                                            columns=['store_name']).reset_index()
        total_bills_repeat['tag_flag'] = 'repeat_consumers_bills_count'

        total_bills_new_repeat = pd.concat([total_bills_new,
                                            total_bills_repeat], sort=True)

        return total_bills_new_repeat

    def total_bills_chronic_acute(self, Sales, Customer_returns, Stores):
        sales = Sales.copy(deep = True)
        customer_returns = Customer_returns.copy(deep = True)
        stores  = Stores.copy(deep = True)

        sales['value'] = sales['quantity'] * sales['rate']
        sales['COGS'] = sales['quantity'] * sales['final_ptr']

        df_a1a = sales.groupby(['store_id', 'order_source', 'type1', 'category'],
                               as_index=False).agg({
            'value': ['sum'],
            'quantity': ['sum'],
            'COGS': ['sum'],
            'bill_id': pd.Series.nunique,
            'drug_id': pd.Series.nunique}).reset_index(drop=True)
        df_a1a.columns = ["_".join(x) for x in df_a1a.columns.ravel()]

        customer_returns['returned_value'] = customer_returns['returned_quantity'] * customer_returns['rate']
        customer_returns['returned_COGS'] = customer_returns['returned_quantity'] * customer_returns['final_ptr']

        df_b2 = customer_returns.groupby(['store_id', 'order_source', 'type1', 'category'],
                                         as_index=False).agg({
            'returned_value': ['sum'],
            'returned_quantity': ['sum'],
            'returned_COGS': ['sum'],
            'returned_bill_id': pd.Series.nunique,
            'returned_drug_id': pd.Series.nunique}).reset_index(drop=True)
        df_b2.columns = ["_".join(x) for x in df_b2.columns.ravel()]

        df_a_b = pd.merge(left=df_a1a, right=df_b2,
                          how='left', on=['store_id_', 'order_source_', 'type1_', 'category_'])
        df_a_b.fillna(0, inplace=True)

        df_a_b['net_sale'] = df_a_b['value_sum'] - df_a_b['returned_value_sum']
        df_a_b['net_COGS'] = df_a_b['COGS_sum'] - df_a_b['returned_COGS_sum']
        df_a_b['net_quantity'] = df_a_b['quantity_sum'] - df_a_b['returned_quantity_sum']

        df_a4 = df_a_b.groupby(['store_id_', 'order_source_', 'category_', 'type1_'],
                               as_index=False).agg({
            'net_sale': ['sum'],
            'net_quantity': ['sum'],
            'net_COGS': ['sum'],
            'bill_id_nunique': ['sum'],
            'drug_id_nunique': ['sum']}).reset_index(drop=True)
        df_a4.columns = ["_".join(x) for x in df_a4.columns.ravel()]

        df_a4 = pd.merge(left=df_a4, right=stores,
                         how='left', left_on=['store_id__'],
                         right_on=['store_id'])

        df_a5 = df_a4[df_a4['category__'] == 'chronic']

        total_bills_chronic = pd.pivot_table(df_a5,
                                             values='bill_id_nunique_sum',
                                             index=['order_source__', 'category__', 'type1__'],
                                             columns=['store_name']).reset_index()

        df_a6 = df_a4[df_a4['category__'] == 'acute']

        total_bills_acute = pd.pivot_table(df_a6,
                                           values='bill_id_nunique_sum',
                                           index=['order_source__', 'category__', 'type1__'],
                                           columns=['store_name']).reset_index()

        total_bills_chronic_acute = pd.concat([total_bills_chronic, total_bills_acute])

        total_bills_chronic_acute['tag_flag'] = 'total_bills'

        total_bills_chronic_acute.rename(columns={'type1__': 'type1',
                                                  'category__': 'category',
                                                  'order_source__': 'order_source'}, inplace=True)

        return total_bills_chronic_acute

    def bills_per_cons_new_repeat(self, Sales, All_cons_initial_bill_date ,Stores, choose_year,choose_month):

        sales = Sales.copy(deep=True)
        df1 = All_cons_initial_bill_date.copy(deep=True)
        stores = Stores.copy(deep=True)

        df1['year'] = df1['created_at'].dt.year
        df1["month"] = df1['created_at'].dt.month

        df1 = df1[(df1['year'] == int(choose_year)) & (df1['month'] == int(choose_month))]

        sales['flag'] = np.where(sales['category'] == "chronic", 1, 0)

        df2 = sales.groupby(['store_id', 'order_source',
                             'patient_id'])[['flag']].sum().reset_index()
        df2['check'] = np.where(df2['flag'] > 0, "chronic", "acute")

        df3 = pd.merge(left=df1, right=df2,
                       how='left', on=['store_id', 'patient_id'])

        df5 = pd.merge(left=df2, right=df1,
                       how='left', on=['store_id', 'patient_id'])
        df6 = df5[df5['year'].isnull()]

        df30 = sales.groupby(['store_id', 'order_source',
                              'patient_id'])[['bill_id']].nunique().reset_index().rename(columns={
            "bill_id": "no_of_bills"})

        # new consumers
        df31 = pd.merge(left=df3, right=df30,
                        how='left', on=['store_id', 'order_source', 'patient_id'])
        df32 = df31.groupby(['store_id', 'order_source'])[['no_of_bills']].mean().reset_index().rename(columns={
            "no_of_bills": "new_consumers_avg_no_of_bills"})

        # repeat consumers
        df33 = pd.merge(left=df6, right=df30,
                        how='left', on=['store_id', 'order_source', 'patient_id'])
        df34 = df33.groupby(['store_id', 'order_source'])[['no_of_bills']].mean().reset_index().rename(columns={
            "no_of_bills": "repeat_consumers_avg_no_of_bills"})

        df35 = pd.merge(left=df32, right=df34,
                        how='left', on=['store_id', 'order_source'])

        df35 = pd.merge(left=df35, right=stores, how='left', on=['store_id'])

        bills_per_cons_new = pd.pivot_table(df35,
                                            values='new_consumers_avg_no_of_bills',
                                            index='order_source',
                                            columns=['store_name']).reset_index()
        bills_per_cons_new['tag_flag'] = 'new_consumers_avg_no_of_bills'

        bills_per_cons_repeat = pd.pivot_table(df35,
                                               values='repeat_consumers_avg_no_of_bills',
                                               index='order_source',
                                               columns=['store_name']).reset_index()
        bills_per_cons_repeat['tag_flag'] = 'repeat_consumers_avg_no_of_bills'

        bills_per_cons_new_repeat = pd.concat([bills_per_cons_new,
                                               bills_per_cons_repeat])

        # bills_per_cons_new_repeat.rename(columns={'index': 'tag_flag'}, inplace=True)

        return bills_per_cons_new_repeat

    def abv_new_repeat_chronic(self, Sales, All_cons_initial_bill_date ,Stores, choose_year,choose_month ):

        sales = Sales.copy(deep=True)
        df1 = All_cons_initial_bill_date.copy(deep=True)
        stores = Stores.copy(deep=True)

        df1['year'] = df1['created_at'].dt.year
        df1["month"] = df1['created_at'].dt.month

        df1 = df1[(df1['year'] == int(choose_year)) & (df1['month'] == int(choose_month))]

        sales['flag'] = np.where(sales['category'] == "chronic", 1, 0)

        df2 = sales.groupby(['store_id',
                             'order_source', 'patient_id'])[['flag']].sum().reset_index()
        df2['check'] = np.where(df2['flag'] > 0, "chronic", "acute")

        df3 = pd.merge(left=df1, right=df2,
                       how='left', on=['store_id', 'patient_id'])

        df5 = pd.merge(left=df2, right=df1,
                       how='left', on=['store_id', 'patient_id'])
        df6 = df5[df5['year'].isnull()]

        sales['value'] = sales['quantity'] * sales['rate']

        sales['value'] = sales['value'].astype(float)
        df36 = sales.groupby(['store_id', 'order_source',
                              'patient_id', 'bill_id'])[['value']].sum().reset_index()
        df37 = df36.groupby(['store_id', 'order_source',
                             'patient_id'])[['value']].mean().reset_index()

        # new consumers
        df38 = pd.merge(left=df3, right=df37,
                        how='left', on=['store_id', 'order_source', 'patient_id'])
        df39 = df38.groupby(['store_id', 'order_source'])[['value']].mean().reset_index().rename(columns={
            "value": "new_consumers_avg_bill_value"})

        # repeat consumers
        df40 = pd.merge(left=df6, right=df37,
                        how='left', on=['store_id', 'order_source', 'patient_id'])
        df41 = df40.groupby(['store_id', 'order_source'])[['value']].mean().reset_index().rename(columns={
            "value": "repeat_consumers_avg_bill_value"})

        df42 = pd.merge(left=df39, right=df41,
                        how='left', on=['store_id', 'order_source'])

        df42 = pd.merge(left=df42, right=stores, how='left', on=['store_id'])

        df42['new_consumers_avg_bill_value'] = df42['new_consumers_avg_bill_value'].astype(float)

        abv_new = pd.pivot_table(df42,
                                 values='new_consumers_avg_bill_value',
                                 index='order_source',
                                 columns=['store_name']).reset_index()
        abv_new['tag_flag'] = 'new_consumers_avg_bill_value'

        df42['repeat_consumers_avg_bill_value'] = df42['repeat_consumers_avg_bill_value'].astype(float)

        abv_repeat = pd.pivot_table(df42,
                                    values='repeat_consumers_avg_bill_value',
                                    index='order_source',
                                    columns=['store_name']).reset_index()
        abv_repeat['tag_flag'] = 'repeat_consumers_avg_bill_value'

        df_a9 = sales.groupby(['store_id', 'order_source',
                               'bill_id', 'category'])[['value']].sum().reset_index()
        df_a10 = df_a9.groupby(['store_id', 'order_source', 'category'])[['value']].mean().reset_index().rename(columns=
        {
            'value': "chronic_consumers_avg_bill_value"})

        df_a11 = df_a10[df_a10['category'] == 'chronic']
        df_a11 = pd.merge(left=df_a11, right=stores, how='left', on=['store_id'])

        abv_chronic = pd.pivot_table(df_a11,
                                     values='chronic_consumers_avg_bill_value',
                                     index='order_source',
                                     columns=['store_name']).reset_index()
        abv_chronic['tag_flag'] = 'chronic_consumers_avg_bill_value'

        abv_new_repeat_chronic = pd.concat([abv_new, abv_repeat, abv_chronic])

        return abv_new_repeat_chronic

    def items_per_cons_new_repeat(self,Sales, All_cons_initial_bill_date ,Stores, choose_year,choose_month ):

        sales = Sales.copy(deep=True)
        df1 = All_cons_initial_bill_date.copy(deep=True)
        stores = Stores.copy(deep=True)

        df1['year'] = df1['created_at'].dt.year
        df1["month"] = df1['created_at'].dt.month

        df1 = df1[(df1['year'] == int(choose_year)) & (df1['month'] == int(choose_month))]

        sales['flag'] = np.where(sales['category'] == "chronic", 1, 0)

        df2 = sales.groupby(['store_id',
                             'order_source', 'patient_id'])[['flag']].sum().reset_index()
        df2['check'] = np.where(df2['flag'] > 0, "chronic", "acute")

        df3 = pd.merge(left=df1, right=df2,
                       how='left', on=['store_id', 'patient_id'])

        df5 = pd.merge(left=df2, right=df1,
                       how='left', on=['store_id', 'patient_id'])
        df6 = df5[df5['year'].isnull()]

        df43 = sales.groupby(['store_id',
                              'order_source', 'patient_id'])[['drug_id']].nunique().reset_index()

        # new consumers
        df44 = pd.merge(left=df3, right=df43,
                        how='left', on=['store_id', 'order_source', 'patient_id'])
        df45 = df44.groupby(['store_id', 'order_source'])[['drug_id']].mean().reset_index().rename(columns={
            "drug_id": "new_consumers_avg_items"})

        # repeat consumers
        df46 = pd.merge(left=df6, right=df43,
                        how='left', on=['store_id', 'order_source', 'patient_id'])
        df47 = df46.groupby(['store_id', 'order_source'])[['drug_id']].mean().reset_index().rename(columns={
            "drug_id": "repeat_consumers_avg_items"})

        df48 = pd.merge(left=df45, right=df47,
                        how='left', on=['store_id', 'order_source'])

        df48 = pd.merge(left=df48, right=stores, how='left', on=['store_id'])

        items_per_cons_new = pd.pivot_table(df48,
                                            values='new_consumers_avg_items',
                                            index='order_source',
                                            columns=['store_name']).reset_index()
        items_per_cons_new['tag_flag'] = 'new_consumers_avg_items'

        items_per_cons_repeat = pd.pivot_table(df48,
                                               values='repeat_consumers_avg_items',
                                               index='order_source',
                                               columns=['store_name']).reset_index()
        items_per_cons_repeat['tag_flag'] = 'repeat_consumers_avg_items'

        items_per_cons_new_repeat = pd.concat([items_per_cons_new,
                                               items_per_cons_repeat])

        # items_per_cons_new_repeat.rename(columns={'index': 'tag_flag'}, inplace=True)

        return items_per_cons_new_repeat

    def tot_items_sold_new_repeat(self, Sales, All_cons_initial_bill_date, Stores, choose_year, choose_month):
        sales = Sales.copy(deep=True)
        df1 = All_cons_initial_bill_date.copy(deep=True)
        stores = Stores.copy(deep=True)

        df1['year'] = df1['created_at'].dt.year
        df1["month"] = df1['created_at'].dt.month

        df1 = df1[(df1['year'] == int(choose_year)) & (df1['month'] == int(choose_month))]

        sales['flag'] = np.where(sales['category'] == "chronic", 1, 0)

        df2 = sales.groupby(['store_id', 'order_source', 'patient_id'])[['flag']].sum().reset_index()
        df2['check'] = np.where(df2['flag'] > 0, "chronic", "acute")

        df3 = pd.merge(left=df1, right=df2,
                       how='left', on=['store_id', 'patient_id'])

        df5 = pd.merge(left=df2, right=df1,
                       how='left', on=['store_id', 'patient_id'])
        df6 = df5[df5['year'].isnull()]

        df24 = sales.groupby(['store_id',
                              'order_source', 'patient_id'])[['quantity']].sum().reset_index()

        # new consumers
        df25 = pd.merge(left=df3, right=df24,
                        how='left', on=['store_id', 'order_source', 'patient_id'])
        df26 = df25.groupby(['store_id', 'order_source'])[['quantity']].sum().reset_index().rename(columns={
            "quantity": "new_consumers_qty"})

        # repeat consumers
        df27 = pd.merge(left=df6, right=df24,
                        how='left', on=['store_id', 'order_source', 'patient_id'])
        df28 = df27.groupby(['store_id', 'order_source'])[['quantity']].sum().reset_index().rename(columns={
            "quantity": "repeat_consumers_qty"})

        df29 = pd.merge(left=df26, right=df28,
                        how='left', on=['store_id', 'order_source'])

        df29 = pd.merge(left=df29, right=stores, how='left', on=['store_id'])

        tot_items_sold_new = pd.pivot_table(df29,
                                            values='new_consumers_qty',
                                            index='order_source',
                                            columns=['store_name']).reset_index()
        tot_items_sold_new['tag_flag'] = 'new_consumers_qty'

        tot_items_sold_repeat = pd.pivot_table(df29,
                                               values='repeat_consumers_qty',
                                               index='order_source',
                                               columns=['store_name']).reset_index()
        tot_items_sold_repeat['tag_flag'] = 'repeat_consumers_qty'

        tot_items_sold_new_repeat = pd.concat([tot_items_sold_new,
                                               tot_items_sold_repeat])

        # tot_items_sold_new_repeat.rename(columns={'index': 'tag_flag'}, inplace=True)

        return tot_items_sold_new_repeat

    def generic_cons_overall_new(self, Sales, All_cons_initial_bill_date, Stores):
        sales = Sales.copy(deep=True)
        all_cons_first = All_cons_initial_bill_date.copy(deep=True)
        stores = Stores.copy(deep=True)

        generic_cons = sales.groupby(['store_id',
                                      'order_source', 'type'])[['patient_id']].nunique().reset_index().rename(columns={
            "patient_id": "generic_cons_overall"})
        generic_cons = generic_cons[generic_cons['type'].isin(['generic', 'high-value-generic'])]

        generic_cons = pd.merge(left=generic_cons, right=stores,
                                how='left', on=['store_id'])

        generic_cons_overall = pd.pivot_table(generic_cons,
                                              values='generic_cons_overall',
                                              index='order_source',
                                              columns=['store_name']).reset_index()
        generic_cons_overall['tag_flag'] = 'generic_cons_overall'

        aug_cons_min = sales.groupby(['store_id', 'order_source', 'patient_id'])[['created_at']].min().reset_index()

        aug_new_cons = pd.merge(left=all_cons_first, right=aug_cons_min,
                                how='inner', on=['store_id', 'patient_id', 'created_at'])
        aug_new_cons['flag'] = "aug_new"

        new_cons_generic = pd.merge(left=aug_new_cons[['store_id', 'order_source', 'patient_id', 'flag']],
                                    right=sales,
                                    how='left', on=['store_id', 'order_source', 'patient_id'])
        new_cons_generic1 = new_cons_generic.groupby(['store_id', 'order_source', 'type'])[
            ['patient_id']].nunique().reset_index().rename(columns={
            "patient_id": "generic_cons_new"})
        new_cons_generic1 = new_cons_generic1[new_cons_generic1['type'].isin(['generic', 'high-value-generic'])]

        new_cons_generic1 = pd.merge(left=new_cons_generic1, right=stores,
                                     how='left', on=['store_id'])

        generic_cons_new = pd.pivot_table(new_cons_generic1,
                                          values='generic_cons_new',
                                          index='order_source',
                                          columns=['store_name']).reset_index()
        generic_cons_new['tag_flag'] = 'generic_cons_new'

        generic_cons_overall_new = pd.concat([generic_cons_overall, generic_cons_new])

        return generic_cons_overall_new

    def power_cons_overall_new(self, Sales, All_cons_initial_bill_date, Stores, power_consumer_value):
        sales = Sales.copy(deep=True)
        all_cons_first = All_cons_initial_bill_date.copy(deep=True)
        stores = Stores.copy(deep=True)

        power_cons_aug = sales.groupby(['store_id', 'order_source', 'patient_id'])[['value']].sum().reset_index()
        power_cons_aug1 = power_cons_aug[power_cons_aug['value'] > power_consumer_value]

        power_cons = power_cons_aug1.groupby(['store_id', 'order_source'])[
            ['patient_id']].nunique().reset_index().rename(
            columns={
                "patient_id": "power_cons_overall"})

        power_cons = pd.merge(left=power_cons, right=stores, how='left', on=['store_id'])

        power_cons_overall = pd.pivot_table(power_cons,
                                            values='power_cons_overall',
                                            index='order_source',
                                            columns=['store_name']).reset_index()
        power_cons_overall['tag_flag'] = 'power_cons_overall'

        aug_cons_min = sales.groupby(['store_id', 'order_source', 'patient_id'])[['created_at']].min().reset_index()

        aug_new_cons = pd.merge(left=all_cons_first, right=aug_cons_min,
                                how='inner', on=['store_id', 'patient_id', 'created_at'])
        aug_new_cons['flag'] = "aug_new"

        df_fg = pd.merge(left=aug_new_cons[['store_id', 'order_source', 'patient_id', 'flag']], right=power_cons_aug1,
                         how='left', on=['store_id', 'order_source', 'patient_id'])
        df_fg1 = df_fg[df_fg['value'].notnull()]

        new_power_cons = df_fg1.groupby(['store_id', 'order_source'])[['patient_id']].nunique().reset_index().rename(
            columns={
                "patient_id": "power_cons_new"})

        new_power_cons = pd.merge(left=new_power_cons, right=stores,
                                  how='left', on=['store_id'])

        power_cons_new = pd.pivot_table(new_power_cons,
                                        values='power_cons_new',
                                        index='order_source',
                                        columns=['store_name']).reset_index()
        power_cons_new['tag_flag'] = 'power_cons_new'

        power_cons_overall_new = pd.concat([power_cons_overall, power_cons_new])

        # power_cons_overall_new.rename(columns={'index': 'tag_flag'}, inplace=True)

        return power_cons_overall_new

    def power_consumers_sale(self, Sales, Stores, power_consumer_value, mis_type):
        sales = Sales.copy(deep=True)
        stores = Stores.copy(deep=True)

        ad1 = sales.groupby(['store_id', 'order_source', 'patient_id'])[['value']].sum().reset_index()
        ad2 = ad1[ad1['value'] > power_consumer_value]

        ad3 = pd.merge(left=ad2[['store_id', 'order_source', 'patient_id']],
                       right=sales,
                       how='left', on=['store_id', 'order_source', 'patient_id'])

        power_cons_sales = ad3.groupby(['store_id', 'order_source', 'type1'])[['value']].sum().reset_index()

        power_cons_sales['value'] = power_cons_sales['value'].astype(float)

        power_cons_sales = pd.merge(left=power_cons_sales, right=stores,
                                    how='left', on=['store_id'])

        power_cons_sales_ethical = power_cons_sales[power_cons_sales['type1'] == 'ethical']

        power_cons_sales_ethical = pd.pivot_table(power_cons_sales_ethical,
                                                  values='value',
                                                  index=['type1', 'order_source'],
                                                  columns=['store_name']).reset_index()

        power_cons_sales_generic = power_cons_sales[power_cons_sales['type1'] == 'generic']

        power_cons_sales_generic = pd.pivot_table(power_cons_sales_generic,
                                                  values='value',
                                                  index=['type1', 'order_source'],
                                                  columns=['store_name']).reset_index()

        power_cons_sales_others = power_cons_sales[power_cons_sales['type1'] == 'others']
        power_cons_sales_others = pd.pivot_table(power_cons_sales_others,
                                                 values='value',
                                                 index=['type1', 'order_source'],
                                                 columns=['store_name']).reset_index()

        power_cons_sales_gaid = power_cons_sales[power_cons_sales['type1'] == 'GOODAID']
        power_cons_sales_gaid = pd.pivot_table(power_cons_sales_gaid,
                                               values='value',
                                               index=['type1', 'order_source'],
                                               columns=['store_name']).reset_index()

        power_cons_sales_overall = power_cons_sales.groupby(['store_id',
                                                             'store_name', 'order_source'])[
            ['value']].sum().reset_index().rename(columns={
            "value": "total"})
        power_cons_sales_overall = pd.pivot_table(power_cons_sales_overall,
                                                  values='total',
                                                  index=['order_source'],
                                                  columns=['store_name']).reset_index().rename(columns={
            "index": "type1"})

        if mis_type == 'breakup':
            power_consumers_sale = pd.concat([power_cons_sales_overall,
                                              power_cons_sales_ethical,
                                              power_cons_sales_generic,
                                              power_cons_sales_others,
                                              power_cons_sales_gaid], sort=True)
        elif mis_type == 'unified':
            power_consumers_sale = pd.concat([power_cons_sales_overall,
                                              power_cons_sales_ethical,
                                              power_cons_sales_generic,
                                              power_cons_sales_others], sort=True)
        else:
            self.logger.info('provide valid mis_type')
            return None

        power_consumers_sale['tag_flag'] = 'power_cons_sale'

        return power_consumers_sale

    def power_cons_bills(self, Sales, Stores, power_consumer_value):
        sales = Sales.copy(deep=True)
        stores = Stores.copy(deep=True)

        power_cons_aug = sales.groupby(['store_id', 'order_source', 'patient_id'])[['value']].sum().reset_index()
        power_cons_aug1 = power_cons_aug[power_cons_aug['value'] > power_consumer_value]

        df_lp = pd.merge(left=power_cons_aug1[['store_id', 'order_source', 'patient_id']],
                         right=sales,
                         how='left', on=['store_id', 'order_source', 'patient_id'])
        power_cons_bills = df_lp.groupby(['store_id', 'order_source'])[['bill_id']].nunique().reset_index().rename(
            columns={
                "bill_id": "no_of_bills"})

        power_cons_bills = pd.merge(left=power_cons_bills, right=stores,
                                    how='left', on=['store_id'])

        power_cons_bills = pd.pivot_table(power_cons_bills,
                                          values='no_of_bills',
                                          index='order_source',
                                          columns=['store_name']).reset_index()
        power_cons_bills['tag_flag'] = "no_of_bills"

        # power_cons_bills.rename(columns={'index': 'tag_flag'}, inplace=True)

        power_cons_bills.loc[power_cons_bills['tag_flag'] == 'no_of_bills',
                             'tag_flag'] = 'Power cons no_of_bills'

        return power_cons_bills

    def home_delivery(self, Sales, Customer_returns, Home_delivery_data, Stores, delivery_bill_ids,mis_tag ):

        sales = Sales.copy(deep=True)
        customer_returns = Customer_returns.copy(deep=True)
        home_delivery_data = Home_delivery_data.copy(deep=True)
        stores = Stores.copy(deep=True)
        delivery_bill_ids = delivery_bill_ids.copy(deep=True)

        # Consumer Count

        HD_cons = home_delivery_data.groupby(['store_id', 'order_source'])[
            ['patient_id']].nunique().reset_index().rename(columns={
            "patient_id": "no_of_HD_consumers"})

        HD_cons = pd.merge(left=HD_cons, right=stores,
                           how='left', on=['store_id'])

        HD_cons_count = pd.pivot_table(HD_cons,
                                       values='no_of_HD_consumers',
                                       index='order_source',
                                       columns=['store_name']).reset_index()
        HD_cons_count['tag_flag'] = 'no_of_HD_consumers'

        # Deliverd count

        home_delivery_data['key'] = home_delivery_data['patient_id'].astype(str) + '-' + home_delivery_data[
            'order_number'].astype(str) + '-' + home_delivery_data['bill_id'].astype(str)

        if mis_tag == 'breakup':
            home_delivery_data['order_source2'] = np.where(home_delivery_data.order_source_pso.isin(['zeno']),
                                                           "ecomm", "store")
        elif mis_tag == 'unified':
            home_delivery_data['order_source2'] = 'all'

        HD_count = home_delivery_data.groupby(['store_id', 'order_source2']).agg(
            {'key': pd.Series.nunique}).reset_index()

        HD_count = pd.merge(left=HD_count, right=stores,
                            how='left', on=['store_id'])

        HD_count.rename(columns={'key': 'count_of_HD_delivered'}, inplace=True)

        HD_count_delivered = pd.pivot_table(HD_count,
                                            values='count_of_HD_delivered',
                                            index='order_source2',
                                            columns=['store_name']).reset_index()
        HD_count_delivered.rename(columns={'order_source2': 'order_source'}, inplace =True)
        HD_count_delivered['tag_flag'] = 'count_of_HD_delivered'

        # HD sales

        sales = sales[['store_id', 'order_source', 'bill_id', 'rate', 'quantity', 'type1']]
        customer_returns = customer_returns[
            ['store_id', 'order_source', 'bill_id', 'rate', 'returned_quantity', 'type1']]

        customer_returns['returned_quantity'] = customer_returns['returned_quantity'] * (-1)

        customer_returns.rename(columns={'returned_quantity': 'quantity'}, inplace=True)

        sales = pd.concat([sales, customer_returns], sort=True)

        sales['quantity'] = sales['quantity'].astype(float)
        sales['rate'] = sales['rate'].astype(float)
        sales['value'] = sales['rate'] * sales['quantity']

        HD_bills = tuple(map(int, list(delivery_bill_ids[~delivery_bill_ids['bill_id'].isnull()]['bill_id'].unique())))

        HD_sales = sales[sales['bill_id'].isin(HD_bills)]

        HD_sales_by_type = HD_sales.groupby(['store_id', 'type1', 'order_source'])[["value"]].sum().reset_index()

        HD_sales_by_type = pd.merge(left=HD_sales_by_type, right=stores,
                                    how='left', on=['store_id'])

        HD_sales_by_type['value'] = HD_sales_by_type['value'].astype(float)

        HD_sales = pd.pivot_table(HD_sales_by_type,
                                  values='value',
                                  index=['type1', 'order_source'],
                                  columns=['store_name']).reset_index().rename(columns={
            "type1": "index"})
        HD_sales.rename(columns={'index': 'tag_flag'}, inplace=True)

        home_delivery = pd.concat([HD_cons_count, HD_count_delivered, HD_sales], sort=True)

        home_delivery.loc[home_delivery['tag_flag'] == 'ethical',
                          'tag_flag'] = 'HD ethical sale'

        home_delivery.loc[home_delivery['tag_flag'] == 'generic',
                          'tag_flag'] = 'HD generic sale'

        home_delivery.loc[home_delivery['tag_flag'] == 'others',
                          'tag_flag'] = 'HD others sale'

        if mis_tag == 'breakup':
            home_delivery.loc[home_delivery['tag_flag'] == 'GOODAID',
                              'tag_flag'] = 'GOODAID sale'

        return home_delivery

    def purchase_from_worckell(self, Purchase_from_workcell_data, Stores,mis_tag):
        purchase_from_wc_data = Purchase_from_workcell_data.copy(deep=True)
        stores = Stores.copy(deep=True)

        purchase_from_wc_data['zp_received_tax'] = np.vectorize(self.taxable_value_vat_based_2)(
            purchase_from_wc_data['zp_received_net_value'], purchase_from_wc_data['zp_vat'])

        purchase_from_wc_data['wc_purchased_tax'] = np.vectorize(self.taxable_value_vat_based_2)(
            purchase_from_wc_data['wc_purchase_net_value'], purchase_from_wc_data['wc_vat'])

        df_yy1 = purchase_from_wc_data.groupby(['store_id', 'type1', 'category'],
                                               as_index=False).agg({
            'zp_received_net_value': ['sum'],
            'zp_received_tax': ['sum'],
            'wc_purchase_net_value': ['sum'],
            'wc_purchased_tax': ['sum']}).reset_index(drop=True)
        df_yy1.columns = ["_".join(x) for x in df_yy1.columns.ravel()]
        df_yy1.columns = df_yy1.columns.str.rstrip('_x')

        df_yy2 = df_yy1.groupby(['store_id', 'type1'])[["zp_received_tax_sum"]].sum().reset_index()

        df_yy2 = pd.merge(left=df_yy2, right=stores,
                          how='left', on=['store_id'])

        purchase_from_wc = pd.pivot_table(df_yy2,
                                          values='zp_received_tax_sum',
                                          index='type1',
                                          columns=['store_name']).reset_index().rename(columns={
            "type1": "index"})

        purchase_from_wc.rename(columns={'index': 'tag_flag'}, inplace=True)

        purchase_from_wc.loc[purchase_from_wc['tag_flag'] == 'ethical',
                             'tag_flag'] = 'purchase_from_wc_ethical'

        purchase_from_wc.loc[purchase_from_wc['tag_flag'] == 'generic',
                             'tag_flag'] = 'purchase_from_wc_generic'

        purchase_from_wc.loc[purchase_from_wc['tag_flag'] == 'others',
                             'tag_flag'] = 'purchase_from_wc_others'

        if mis_tag == 'breakup':
            purchase_from_wc.loc[purchase_from_wc['tag_flag'] == 'GOODAID',
                                 'tag_flag'] = 'purchase_from_wc_GOODAID'

        return purchase_from_wc

    def cogs_for_wc(self, Purchase_from_workcell_data, Stores, mis_tag):

        purchase_from_wc_data = Purchase_from_workcell_data.copy(deep=True)
        stores = Stores.copy(deep=True)

        purchase_from_wc_data['zp_received_tax'] = np.vectorize(self.taxable_value_vat_based_2)(
            purchase_from_wc_data['zp_received_net_value'], purchase_from_wc_data['zp_vat'])

        purchase_from_wc_data['wc_purchased_tax'] = np.vectorize(self.taxable_value_vat_based_2)(
            purchase_from_wc_data['wc_purchase_net_value'], purchase_from_wc_data['wc_vat'])

        df_yy1 = purchase_from_wc_data.groupby(['store_id', 'type1', 'category'],
                                               as_index=False).agg({
            'zp_received_net_value': ['sum'],
            'zp_received_tax': ['sum'],
            'wc_purchase_net_value': ['sum'],
            'wc_purchased_tax': ['sum']}).reset_index(drop=True)
        df_yy1.columns = ["_".join(x) for x in df_yy1.columns.ravel()]
        df_yy1.columns = df_yy1.columns.str.rstrip('_x')

        df_yy2 = df_yy1.groupby(['store_id', 'type1'])[["wc_purchased_tax_sum"]].sum().reset_index()

        df_yy2 = pd.merge(left=df_yy2, right=stores,
                          how='left', on=['store_id'])

        cogs_for_wc = pd.pivot_table(df_yy2,
                                     values='wc_purchased_tax_sum',
                                     index='type1',
                                     columns=['store_name']).reset_index().rename(columns={
            "type1": "index"})

        cogs_for_wc.rename(columns={'index': 'tag_flag'}, inplace=True)

        cogs_for_wc.loc[cogs_for_wc['tag_flag'] == 'ethical',
                        'tag_flag'] = 'cogs_for_wc_ethical'

        cogs_for_wc.loc[cogs_for_wc['tag_flag'] == 'generic',
                        'tag_flag'] = 'cogs_for_wc_generic'

        cogs_for_wc.loc[cogs_for_wc['tag_flag'] == 'others',
                        'tag_flag'] = 'cogs_for_wc_others'

        if mis_tag == 'breakup':
            cogs_for_wc.loc[cogs_for_wc['tag_flag'] == 'GOODAID',
                            'tag_flag'] = 'cogs_for_wc_GOODAID'

        return cogs_for_wc

    def return_from_zippin(self, Zp_to_wc_return, mis_tag):
        zp_to_wc_return = Zp_to_wc_return.copy(deep=True)
        zp_to_wc_return1 = zp_to_wc_return.groupby(['cost_centre',
                                                    'type1'])[["taxable_value"]].sum().reset_index()
        zp_to_wc_return1['taxable_value'] = zp_to_wc_return1['taxable_value'].astype(float)

        return_from_zippin = pd.pivot_table(zp_to_wc_return1,
                                            values='taxable_value',
                                            index='type1',
                                            columns=['cost_centre']).reset_index().rename(columns={
            "type1": "index"})

        return_from_zippin.rename(columns={'index': 'tag_flag'}, inplace=True)

        return_from_zippin.loc[return_from_zippin['tag_flag'] == 'ethical',
                               'tag_flag'] = 'return_from_zp_ethical'

        return_from_zippin.loc[return_from_zippin['tag_flag'] == 'generic',
                               'tag_flag'] = 'return_from_zp_generic'

        return_from_zippin.loc[return_from_zippin['tag_flag'] == 'others',
                               'tag_flag'] = 'return_from_zp_others'
        if mis_tag == 'breakup':
            return_from_zippin.loc[return_from_zippin['tag_flag'] == 'GOODAID',
                                   'tag_flag'] = 'return_from_zp_GOODAID'

        return return_from_zippin

    def return_from_workcell(self, Wc_return, mis_tag):
        wc_return = Wc_return.copy(deep=True)

        wc_return1 = wc_return.groupby(['cost_centre',
                                        'type1'])[["taxable_value"]].sum().reset_index()

        wc_return1['taxable_value'] = wc_return1['taxable_value'].astype(float)

        return_from_workcell = pd.pivot_table(wc_return1,
                                              values='taxable_value',
                                              index='type1',
                                              columns=['cost_centre']).reset_index().rename(columns={
            "type1": "index"})

        return_from_workcell.rename(columns={'index': 'tag_flag'}, inplace=True)

        return_from_workcell.loc[return_from_workcell['tag_flag'] == 'ethical',
                                 'tag_flag'] = 'return_from_wc_ethical'

        return_from_workcell.loc[return_from_workcell['tag_flag'] == 'generic',
                                 'tag_flag'] = 'return_from_wc_generic'

        return_from_workcell.loc[return_from_workcell['tag_flag'] == 'others',
                                 'tag_flag'] = 'return_from_wc_others'

        return_from_workcell.loc[return_from_workcell['tag_flag'] == 'GOODAID',
                                 'tag_flag'] = 'return_from_wc_GOODAID'

        return return_from_workcell

    def total_sku_instock(self, Inventory, mis_tag):
        inventory = Inventory.copy(deep=True)
        total_sku_instock = inventory.groupby(['type1'])[["drug_id"]].nunique().reset_index()

        total_sku_instock.rename(columns={'type1': 'tag_flag'}, inplace=True)

        total_sku_instock.loc[total_sku_instock['tag_flag'] == 'ethical',
                              'tag_flag'] = 'total_sku_instock_ethical'

        total_sku_instock.loc[total_sku_instock['tag_flag'] == 'generic',
                              'tag_flag'] = 'total_sku_instock_generic'

        total_sku_instock.loc[total_sku_instock['tag_flag'] == 'others',
                              'tag_flag'] = 'total_sku_instock_others'

        if mis_tag == 'breakup':
            total_sku_instock.loc[total_sku_instock['tag_flag'] == 'GOODAID',
                                  'tag_flag'] = 'total_sku_instock_GOODAID'

        total_sku_instock.rename(columns={'drug_id': 'count'}, inplace=True)

        return total_sku_instock

    def chronic_acute_qty(self, Inventory, Stores):

        total_SKU = Inventory.copy(deep=True)
        stores = Stores.copy(deep=True)

        total_SKU['value'] = total_SKU['quantity'] * total_SKU['final_ptr']

        total_SKU_amount_qty = total_SKU.groupby(['store_id', 'type1', 'category'],
                                                 as_index=False).agg({
            'drug_id': pd.Series.nunique,
            'quantity': ['sum'],
            'value': ['sum']}).reset_index(drop=True)
        total_SKU_amount_qty.columns = ["_".join(x) for x in total_SKU_amount_qty.columns.ravel()]

        total_SKU_amount_qty = pd.merge(left=total_SKU_amount_qty, right=stores,
                                        how='left', left_on=['store_id_'], right_on=['store_id'])

        total_SKU_amount_qty2 = total_SKU_amount_qty[total_SKU_amount_qty['category_'] == 'chronic']
        chronic_qty = pd.pivot_table(total_SKU_amount_qty2,
                                     values='quantity_sum',
                                     index='type1_',
                                     columns=['store_name']).reset_index()
        chronic_qty['tag_flag'] = 'chronic_qty'

        total_SKU_amount_qty3 = total_SKU_amount_qty[total_SKU_amount_qty['category_'] == 'acute']
        acute_qty = pd.pivot_table(total_SKU_amount_qty3,
                                   values='quantity_sum',
                                   index='type1_',
                                   columns=['store_name']).reset_index()
        acute_qty['tag_flag'] = 'acute_qty'

        chronic_acute_qty = pd.concat([chronic_qty, acute_qty], sort=True)

        chronic_acute_qty.rename(columns={'type1_': 'type1'}, inplace=True)

        return chronic_acute_qty

    def lp_chronic_acute(self, Local_purchase_data, Sales):

        local_purchase_data = Local_purchase_data.copy(deep=True)

        sales = Sales.copy(deep=True)

        sold_local_purchase = sales.merge(local_purchase_data, on='inventory_id', how='inner')

        sold_local_purchase['sold_quantity'] = sold_local_purchase['quantity']

        sold_local_purchase['revenue'] = sold_local_purchase['quantity'] * sold_local_purchase['rate']

        df1 = sold_local_purchase.groupby(['inventory_id'], as_index=False).agg({
            'sold_quantity': ['sum'],
            'revenue': ['sum']}).reset_index(drop=True)
        df1.columns = ["_".join(x) for x in df1.columns.ravel()]
        df1.columns = df1.columns.str.rstrip('_')

        df2 = pd.merge(left=local_purchase_data, right=df1, how='left', on=['inventory_id'])

        lp1 = df2.groupby(['store_id', 'store_name',
                           'category', 'type1'])[['net_value']].sum().reset_index()

        lp_chronic = lp1[lp1['category'] == 'chronic']
        lp_chronic['net_value'] = lp_chronic['net_value'].astype(float)

        lp_chronic = pd.pivot_table(lp_chronic,
                                    values='net_value',
                                    index='type1',
                                    columns=['store_name']).reset_index()
        lp_chronic['tag_flag'] = 'local_purchase_chronic'

        lp_acute = lp1[lp1['category'] == 'acute']
        lp_acute['net_value'] = lp_acute['net_value'].astype(float)
        lp_acute = pd.pivot_table(lp_acute,
                                  values='net_value',
                                  index='type1',
                                  columns=['store_name']).reset_index()
        lp_acute['tag_flag'] = 'local_purchase_acute'

        lp_chronic_acute = pd.concat([lp_chronic, lp_acute], sort=True)

        return lp_chronic_acute

    def repeat_consumer_chronic_acute(self, Sales, All_cons_initial_bill_date, Stores,choose_year,choose_month):
        sales = Sales.copy(deep=True)
        df1 = All_cons_initial_bill_date.copy(deep=True)
        stores = Stores.copy(deep=True)

        df1['year'] = df1['created_at'].dt.year
        df1["month"] = df1['created_at'].dt.month

        df1 = df1[(df1['year'] == int(choose_year)) & (df1['month'] == int(choose_month))]

        sales['flag'] = np.where(sales['category'] == "chronic", 1, 0)

        df2 = sales.groupby(['store_id', 'order_source', 'patient_id'])[['flag']].sum().reset_index()
        df2['check'] = np.where(df2['flag'] > 0, "chronic", "acute")

        df5 = pd.merge(left=df2, right=df1,
                       how='left', on=['store_id', 'patient_id'])
        df6 = df5[df5['year'].isnull()]

        df6['repeat'] = "yes"
        zx = pd.merge(left=sales, right=df6[['store_id', 'order_source', 'patient_id', 'repeat']],
                      how='left', on=['store_id', 'order_source', 'patient_id'])

        zx1 = zx[zx['repeat'] == 'yes']

        zx1['value'] = zx1['rate'] * zx1['quantity']
        zx2 = zx1.groupby(['store_id', 'order_source',
                           'category', 'type1'])["value"].sum().reset_index()

        zx2 = pd.merge(left=zx2, right=stores,
                       how='left', on=['store_id'])

        repeat_chronic_sale = zx2[zx2['category'] == 'chronic']

        repeat_chronic_sale['value'] = repeat_chronic_sale['value'].astype(float)
        repeat_chronic_sale = pd.pivot_table(repeat_chronic_sale,
                                             values='value',
                                             index=['type1', 'order_source'],
                                             columns=['store_name']).reset_index()
        repeat_chronic_sale['tag_flag'] = 'repeat_consumer_chronic_sale'

        repeat_acute_sale = zx2[zx2['category'] == 'acute']

        repeat_acute_sale['value'] = repeat_acute_sale['value'].astype(float)
        repeat_acute_sale = pd.pivot_table(repeat_acute_sale,
                                           values='value',
                                           index=['type1', 'order_source'],
                                           columns=['store_name']).reset_index()
        repeat_acute_sale['tag_flag'] = 'repeat_consumer_acute_sale'

        repeat_consumer_chronic_acute = pd.concat([repeat_chronic_sale, repeat_acute_sale],sort=True)

        return repeat_consumer_chronic_acute

    def inventory_6to12months(self, Inventory, Stores, mis_tag = 'breakup'):
        df_dd = Inventory.copy(deep=True)
        stores = Stores.copy(deep=True)
        df_dd['value'] = df_dd['quantity'] * df_dd['final_ptr']
        df_dd['days'] = (pd.to_datetime('today') - df_dd['created_at']).dt.days
        conditions = [
            (df_dd['days'] >= 180) & (df_dd['days'] <= 365),
            (df_dd['days'] >= 365)]
        choices = ['6_12', '12+']
        df_dd['age_bracket'] = np.select(conditions, choices)
        df_dd['type1'] = np.where(df_dd['type'].isin(['ethical', 'high-value-ethical']),
                                  "ethical", df_dd['type'])
        df_dd['type1'] = np.where(df_dd['type'].isin(['generic', 'high-value-generic']),
                                  "generic", df_dd['type'])
        df_dd['type1'] = np.where(~df_dd['type1'].isin(['ethical', 'generic']), "others", df_dd['type1'])
        if mis_tag == 'breakup':
            df_dd['type1'] = np.where(df_dd['company'].isin(['GOODAID']),
                                      "GOODAID", df_dd['type1'])

        df_dd['taxable'] = (df_dd['quantity'] * df_dd['final_ptr']) / (1 + ((df_dd['vat']) / 100))

        df_ageing = df_dd.groupby(['store_id', 'category', 'type1', 'age_bracket'],
                                  as_index=False).agg({
            'drug_id': pd.Series.nunique,
            'value': ['sum'],
            'taxable': ['sum']}).reset_index(drop=True)
        df_ageing.columns = ["_".join(x) for x in df_ageing.columns.ravel()]

        df_ageing1 = df_ageing[df_ageing['age_bracket_'].isin(['6_12', '12+'])]

        df_ageing1 = pd.merge(left=df_ageing1, right=stores,
                              how='left', left_on=['store_id_'], right_on=['store_id'])

        df_ageing1['taxable_sum'] = df_ageing1['taxable_sum'].astype(float)

        inventory_6to12months = pd.pivot_table(df_ageing1,
                                               values='taxable_sum',
                                               index=['age_bracket_', 'category_', 'type1_'],
                                               columns=['store_name']).reset_index()

        inventory_6to12months.rename(columns={'type1_': 'type1'}, inplace=True)
        inventory_6to12months.rename(columns={'category_': 'category'}, inplace=True)

        inventory_6to12months['tag_flag'] = 'inventory_6to12months'

        return inventory_6to12months

    def zippin_pl_cogs(self, Sales, Customer_returns, Stores):
        df_aa = Sales.copy(deep=True)
        df_bb = Customer_returns.copy(deep=True)
        stores = Stores.copy(deep=True)

        df_aa['GMV'] = df_aa['quantity'] * df_aa['mrp']
        df_aa['GMV_tax'] = np.vectorize(self.taxable_value)(df_aa['quantity'], df_aa['mrp'],
                                                            df_aa['cgst_rate'], df_aa['sgst_rate'],
                                                            df_aa['igst_rate'])

        df_aa['REVENUE'] = df_aa['quantity'] * df_aa['rate']
        df_aa['REVENUE_tax'] = np.vectorize(self.taxable_value)(df_aa['quantity'], df_aa['rate'],
                                                                df_aa['cgst_rate'], df_aa['sgst_rate'],
                                                                df_aa['igst_rate'])
        df_aa['COGS'] = df_aa['quantity'] * df_aa['final_ptr']
        df_aa['COGS_tax'] = np.vectorize(self.taxable_value)(df_aa['quantity'], df_aa['final_ptr'],
                                                             df_aa['cgst_rate'],
                                                             df_aa['sgst_rate'], df_aa['igst_rate'])
        # df_aa['TAX'] = (df_aa['quantity'] * df_aa['final_ptr']) / (1 + ((df_aa['cgst_rate'] + df_aa['sgst_rate']) / 100))

        df_aa[['GMV', 'GMV_tax', 'REVENUE', 'REVENUE_tax', 'COGS', 'COGS_tax']] = df_aa[
            ['GMV', 'GMV_tax', 'REVENUE', 'REVENUE_tax', 'COGS', 'COGS_tax']].astype(float)

        df_gross = df_aa.groupby(['store_id', 'type1', 'category', 'payment_method',
                                  'order_source'],
                                 as_index=False).agg({
            'drug_id': pd.Series.nunique,
            'quantity': ['sum'],
            'GMV': ['sum'],
            'GMV_tax': ['sum'],
            'REVENUE': ['sum'],
            'REVENUE_tax': ['sum'],
            'COGS': ['sum'],
            'COGS_tax': ['sum'],
            'bill_id': pd.Series.nunique
            # 'net_payable': ['mean']
        }).reset_index(drop=True)
        df_gross.columns = ["_".join(x) for x in df_gross.columns.ravel()]
        df_gross.rename(columns={'store_id_': 'store_id',
                                 'type1_': 'type1',
                                 'category_': 'category',
                                 'payment_method_': 'payment_method',
                                 'order_source_': 'order_source'}, inplace=True)

        ABV_temp = df_aa.drop_duplicates(subset=['store_id', 'type1', 'category',
                                                 'payment_method', 'bill_id',
                                                 'net_payable', 'order_source'])
        ABV_temp['net_payable'] = ABV_temp['net_payable'].astype(float)
        ABV = ABV_temp.groupby(['store_id', 'type1', 'category',
                                'payment_method', 'order_source'])["net_payable"].mean().reset_index()

        df_gross_all = pd.merge(left=df_gross, right=ABV,
                                how='left', on=['store_id', 'type1', 'category',
                                                'payment_method', 'order_source'])

        df_bb['GMV'] = df_bb['returned_quantity'] * df_bb['mrp']
        df_bb['GMV_tax'] = np.vectorize(self.taxable_value)(df_bb['returned_quantity'], df_bb['mrp'],
                                                            df_bb['cgst_rate'], df_bb['sgst_rate'],
                                                            df_bb['igst_rate'])

        df_bb['REVENUE'] = df_bb['returned_quantity'] * df_bb['rate']
        df_bb['REVENUE_tax'] = np.vectorize(self.taxable_value)(df_bb['returned_quantity'], df_bb['rate'],
                                                                df_bb['cgst_rate'], df_bb['sgst_rate'],
                                                                df_bb['igst_rate'])

        df_bb['COGS'] = df_bb['returned_quantity'] * df_bb['final_ptr']
        df_bb['COGS_tax'] = np.vectorize(self.taxable_value)(df_bb['returned_quantity'], df_bb['final_ptr'],
                                                             df_bb['cgst_rate'], df_bb['sgst_rate'],
                                                             df_bb['igst_rate'])

        # df_bb['TAX'] = (df_bb['returned_quantity'] * df_bb['final_ptr']) / (1 + ((df_bb['cgst_rate'] + df_bb['sgst_rate']) / 100))

        df_bb[['GMV', 'GMV_tax', 'REVENUE', 'REVENUE_tax', 'COGS', 'COGS_tax']] = df_bb[
            ['GMV', 'GMV_tax', 'REVENUE', 'REVENUE_tax', 'COGS', 'COGS_tax']].astype(float)

        df_returns = df_bb.groupby(['store_id', 'type1', 'category',
                                    'payment_method', 'order_source'],
                                   as_index=False).agg({
            'drug_id': pd.Series.nunique,
            'returned_quantity': ['sum'],
            'GMV': ['sum'],
            'GMV_tax': ['sum'],
            'REVENUE': ['sum'],
            'REVENUE_tax': ['sum'],
            'COGS': ['sum'],
            'COGS_tax': ['sum']}).reset_index(drop=True)
        df_returns.columns = ["_".join(x) for x in df_returns.columns.ravel()]
        df_returns.rename(columns={'store_id_': 'store_id',
                                   'type1_': 'type1',
                                   'category_': 'category',
                                   'payment_method_': 'payment_method',
                                   'order_source_': 'order_source'}, inplace=True)

        df_gross_returns = pd.merge(left=df_gross_all, right=df_returns,
                                    how='left', on=['store_id', 'type1', 'category',
                                                    'payment_method', 'order_source'])

        df_gross_returns.rename(columns={'store_id_': 'store_id',
                                         'type1_': 'type',
                                         'category_': 'category',

                                         'drug_id_nunique_x': 'no_of_drugs_sales',

                                         'GMV_sum_x': 'GMV_sales',
                                         'GMV_tax_sum_x': 'GMV_sales_tax',

                                         'REVENUE_sum_x': 'REVENUE_sales',
                                         'REVENUE_tax_sum_x': 'REVENUE_sales_tax',

                                         'COGS_sum_x': 'COGS_sales',
                                         'COGS_tax_sum_x': 'COGS_sales_tax',

                                         'drug_id_nunique_y': 'no_of_drugs_returns',

                                         'GMV_sum_y': 'GMV_returns',
                                         'GMV_tax_sum_y': 'GMV_returns_tax',

                                         'REVENUE_sum_y': 'REVENUE_returns',
                                         'REVENUE_tax_sum_y': 'REVENUE_returns_tax',

                                         'COGS_sum_y': 'COGS_returns',
                                         'COGS_tax_sum_y': 'COGS_returns_tax'}, inplace=True)

        df_gross_returns.fillna(0, inplace=True)

        df_gross_returns['net_cogs'] = df_gross_returns['COGS_sales_tax'] - df_gross_returns['COGS_returns_tax']

        df_gross_returns = pd.merge(left=df_gross_returns, right=stores,
                                    how='left', on=['store_id'])

        zp_pl_cogs = df_gross_returns.groupby(['store_id', 'store_name',
                                               'type1', 'order_source'])[['net_cogs']].sum().reset_index()

        zp_pl_cogs['net_cogs'] = zp_pl_cogs['net_cogs'].astype(float)

        zp_pl_cogs1 = pd.pivot_table(zp_pl_cogs,
                                     values='net_cogs',
                                     index=['type1', 'order_source'],
                                     columns=['store_name']).reset_index()

        zp_pl_cogs1['tag_flag'] = 'zp_pl_cogs'

        return zp_pl_cogs1

    def comp_count(self, Inventory, mis_tag):
        inventory = Inventory.copy(deep=True)

        if mis_tag == 'breakup':
            conditions = [inventory['type1'] == 'GOODAID', inventory['type1'] != 'GOODAID']
            choices = ['GOODAID', inventory['type']]
            inventory['type'] = np.select(conditions, choices)

        comp_count = inventory.groupby(['type'])['drug_id'].nunique().reset_index()

        comp_count['tag_flag'] = 'drug_count_by_type'
        comp_count.rename(columns = {'drug_id':'count',
                                     'type':'type1'}, inplace = True)

        return comp_count

    def generic_composition_count(self):
        generic_composition_count_query = self.mis_queries.generic_composition_count_query.format(
            schema=self.schema_to_select,
            suffix_to_table=self.suffix_to_table)
        generic_composition_count = self.rs_db.get_df(generic_composition_count_query)
        generic_composition_count.columns = [c.replace('-', '_') for c in generic_composition_count.columns]

        generic_composition_count['tag_flag'] = 'generic_composition_count'

        return generic_composition_count

    def ethical_margin(self):
        ethical_margin_query = self.mis_queries.ethical_margin_query.format(
            schema=self.schema_to_select,
            suffix_to_table=self.suffix_to_table,
            analysis_start_time=self.analysis_start_time,
            analysis_end_time=self.analysis_end_time)
        ethical_margin = self.rs_db.get_df(ethical_margin_query)
        ethical_margin.columns = [c.replace('-', '_') for c in ethical_margin.columns]

        ethical_margin['margin'] = 1 - (ethical_margin['net_value']/ethical_margin['value1'])

        ethical_margin = ethical_margin[['margin']]

        ethical_margin['tag_flag'] = 'ethical_margin'

        return ethical_margin

    def chronic_generic_count(self, Sales):

        df_r = Sales.copy(deep=True)
        df_r['flag'] = np.where((df_r['category'] == 'chronic'), 1, 0)

        df_r['flag2'] = np.where(((df_r['category'] == 'chronic') &
                                  (df_r['type'] == 'generic')), 1, 0)
        df_r3 = df_r.groupby(['store_id',
                              'patient_id'])[['flag2']].sum().reset_index()

        chronic_generic = df_r3[df_r3['flag2'] > 0].count()["flag2"]
        total = df_r3['flag2'].count()
        chronic_generic_percentage = chronic_generic / total

        chronic_generic_count = pd.DataFrame({'tag_flag': pd.Series("Chronic customers buying generics",
                                                                    dtype='str'),
                                              'count': pd.Series(chronic_generic, dtype='float')})

        return chronic_generic_count

    def sales_data_for_repeat_customer(self,date1,date2):
        sales_query = self.mis_queries.sales_query.format(schema=self.schema_to_select, suffix_to_table=self.suffix_to_table,
                       analysis_start_time=date1, analysis_end_time=date2)

        df = self.rs_db.get_df(sales_query)
        df.columns = [c.replace('-', '_') for c in df.columns]

        return df

    def repeat_cons_other_def_curr_month(self, sales_data_for_repeat_customer, stores,choose_month):

        choose_month = int(choose_month)

        df_aa = sales_data_for_repeat_customer.copy(deep=True)

        df_aa['year'] = df_aa['created_at'].dt.year
        df_aa['month'] = df_aa['created_at'].dt.month

        df_aa['type1'] = np.where(df_aa['type'].isin(['ethical', 'high-value-ethical']),
                                  "ethical", df_aa['type'])
        df_aa['type1'] = np.where(df_aa['type'].isin(['generic', 'high-value-generic']),
                                  "generic", df_aa['type'])
        df_aa['type1'] = np.where(~df_aa['type1'].isin(['ethical', 'generic']),
                                  "others", df_aa['type1'])

        df1 = df_aa.groupby(['store_id', 'patient_id', 'type1', 'category',
                             'bill_id', 'year', 'month'])[["value"]].sum().reset_index()

        df2 = df1.groupby(['store_id', 'patient_id',
                           'type1', 'category'])[["month"]].nunique().reset_index().rename(columns={
            'month': 'unique_months_billed'})

        # =============================================================================
        # Total repeat consumers
        # =============================================================================
        df3 = df2[df2['unique_months_billed'] >= 2]
        df4 = df3.groupby(['store_id',
                           'type1', 'category'])[["patient_id"]].count().reset_index().rename(columns={
            'patient_id': 'repeat_consumers_count'})
        df4['tag_flag'] = 'repeat_cons_other_def_curr_month_count'

        df4 = pd.merge(left=df4, right=stores,
                       how='left', on=['store_id'])

        df4 = pd.pivot_table(df4,
                             values='repeat_consumers_count',
                             index=['tag_flag', 'type1', 'category'],
                             columns=['store_name']).reset_index()

        # =============================================================================
        # Repeat consumers lost
        # =============================================================================

        # df5 = df1[df1['month'].isin([9, 10, 11])]

        def previous_months(month):
            month = int(month)
            if month<=0:
                return month + 12
            else:
                return month

        df5 = df1[df1['month'].isin([previous_months(choose_month-5), previous_months(choose_month-4), previous_months(choose_month-3)])]

        df6 = df5.groupby(['store_id', 'patient_id',
                           'type1', 'category'])[["month"]].nunique().reset_index().rename(columns={
            'month': 'unique_months_billed_till_July'})

        # df7 = df1[df1['month'].isin([12, 1, 2])]

        df7 = df1[df1['month'].isin([previous_months(choose_month-2), previous_months(choose_month-1), previous_months(choose_month)])]

        df8 = df7.groupby(['store_id', 'patient_id',
                           'type1', 'category'])[["month"]].nunique().reset_index().rename(columns={
            'month': 'unique_months_billed_after_July'})

        df9 = pd.merge(left=df6, right=df8,
                       how='left', on=['store_id', 'patient_id', 'type1', 'category'])

        df10 = df9[df9['unique_months_billed_after_July'].isnull()]

        df11 = df10.groupby(['store_id', 'type1', 'category'])[["patient_id"]].count().reset_index()

        df11['tag_flag'] = 'repeat_cons_other_def_curr_month_lost'

        df11 = pd.merge(left=df11, right=stores,
                        how='left', on=['store_id'])

        df11 = pd.pivot_table(df11,
                              values='patient_id',
                              index=['tag_flag', 'type1', 'category'],
                              columns=['store_name']).reset_index()

        repeat_cons_other_def_curr_month = pd.concat([df4, df11])

        return repeat_cons_other_def_curr_month

    def repeat_cons_other_def_past3_month(self, sales_data_for_repeat_customer, stores,choose_month):
        choose_month = int(choose_month)
        df_aa = sales_data_for_repeat_customer.copy(deep=True)

        df_aa['year'] = df_aa['created_at'].dt.year
        df_aa['month'] = df_aa['created_at'].dt.month

        df_aa['type1'] = np.where(df_aa['type'].isin(['ethical', 'high-value-ethical']),
                                  "ethical", df_aa['type'])
        df_aa['type1'] = np.where(df_aa['type'].isin(['generic', 'high-value-generic']),
                                  "generic", df_aa['type'])
        df_aa['type1'] = np.where(~df_aa['type1'].isin(['ethical', 'generic']), "others", df_aa['type1'])

        df1 = df_aa.groupby(['store_id', 'patient_id', 'type1', 'category',
                             'bill_id', 'year', 'month'])[["value"]].sum().reset_index()

        df2 = df1.groupby(['store_id', 'patient_id', 'type1', 'category'])[["month"]].nunique().reset_index().rename(
            columns={
                'month': 'unique_months_billed'})

        # =============================================================================
        # Total repeat consumers
        # =============================================================================
        df3 = df2[df2['unique_months_billed'] >= 2]
        df4 = df3.groupby(['store_id',
                           'type1', 'category'])[["patient_id"]].count().reset_index().rename(columns={
            'patient_id': 'repeat_consumers_count'})

        df4['tag_flag'] = 'repeat_cons_other_def_past3_month_count'

        df4 = pd.merge(left=df4, right=stores,
                       how='left', on=['store_id'])

        df4 = pd.pivot_table(df4,
                             values='repeat_consumers_count',
                             index=['tag_flag', 'type1', 'category'],
                             columns=['store_name']).reset_index()

        # =============================================================================
        # Repeat consumers lost
        # =============================================================================
        # df5 = df1[df1['month'].isin([6, 7, 8])]

        def previous_months(month):
            month = int(month)
            if month <= 0:
                return month + 12
            else:
                return month

        df5 = df1[df1['month'].isin(
            [previous_months(choose_month - 8), previous_months(choose_month - 7), previous_months(choose_month - 6)])]

        df6 = df5.groupby(['store_id', 'patient_id', 'type1', 'category'])[["month"]].nunique().reset_index().rename(
            columns={
                'month': 'unique_months_billed_till_July'})

        # df7 = df1[df1['month'].isin([9, 10, 11])]

        df7 = df1[df1['month'].isin(
            [previous_months(choose_month - 5), previous_months(choose_month - 4), previous_months(choose_month-3)])]

        df8 = df7.groupby(['store_id', 'patient_id', 'type1', 'category'])[["month"]].nunique().reset_index().rename(
            columns={
                'month': 'unique_months_billed_after_July'})

        df9 = pd.merge(left=df6, right=df8,
                       how='left', on=['store_id', 'patient_id', 'type1', 'category'])

        df10 = df9[df9['unique_months_billed_after_July'].isnull()]

        df11 = df10.groupby(['store_id', 'type1', 'category'])[["patient_id"]].count().reset_index()

        df11['tag_flag'] = 'repeat_cons_other_def_past3_month_lost'

        df11 = pd.merge(left=df11, right=stores,
                        how='left', on=['store_id'])

        df11 = pd.pivot_table(df11,
                              values='patient_id',
                              index=['tag_flag', 'type1', 'category'],
                              columns=['store_name']).reset_index()

        repeat_cons_other_def_past3_month = pd.concat([df4, df11])

        return repeat_cons_other_def_past3_month

    def other_files_ethical_margin(self):
        other_files_ethical_margin_query = self.mis_queries.other_files_ethical_margin_query.format(schema=self.schema_to_select, suffix_to_table=self.suffix_to_table)
        other_files_ethical_margin = self.rs_db.get_df(other_files_ethical_margin_query)
        other_files_ethical_margin.columns = [c.replace('-', '_') for c in other_files_ethical_margin.columns]
        return other_files_ethical_margin

    def other_files_distributor_margin(self):
        other_files_distributor_margin_query = self.mis_queries.other_files_distributor_margin_query.format(schema=self.schema_to_select, suffix_to_table=self.suffix_to_table, choose_year=self.choose_year, choose_month = self.choose_month)
        other_files_distributor_margin = self.rs_db.get_df(other_files_distributor_margin_query)
        other_files_distributor_margin.columns = [c.replace('-', '_') for c in other_files_distributor_margin.columns]
        return other_files_distributor_margin

    def other_files_inventory_at_dc_near_expiry(self):
        other_files_inventory_at_dc_near_expiry_data_query = self.mis_queries.other_files_inventory_at_dc_near_expiry_data_query.format(schema=self.schema_to_select, suffix_to_table=self.suffix_to_table)
        df_yy = self.rs_db.get_df(other_files_inventory_at_dc_near_expiry_data_query)
        df_yy.columns = [c.replace('-', '_') for c in df_yy.columns]

        df_yy['type1'] = np.where(df_yy['type'].isin(['ethical', 'high-value-ethical']),
                                  "ethical", df_yy['type'])
        df_yy['type1'] = np.where(df_yy['type'].isin(['generic', 'high-value-generic']),
                                  "generic", df_yy['type'])
        df_yy['type1'] = np.where(~df_yy['type1'].isin(['ethical', 'generic']), "others", df_yy['type1'])

        df_yy['taxable'] = (df_yy['actual_quantity'] * df_yy['final_ptr']) / (1 + ((df_yy['vat']) / 100))

        df_yy['days'] = (pd.to_datetime('today') - df_yy['created_at']).dt.days
        conditions = [
            (df_yy['days'] >= 0) & (df_yy['days'] <= 30),
            (df_yy['days'] >= 31) & (df_yy['days'] <= 60),
            (df_yy['days'] >= 61) & (df_yy['days'] <= 90),
            (df_yy['days'] >= 91)]
        choices = ['0_30', '31_60', '61_90', '90+']
        df_yy['age_bracket'] = np.select(conditions, choices)

        df_yy['expiry_date'] = pd.to_datetime(df_yy['expiry'], format='%Y-%m-%d %H:%M:%S', errors='coerce')

        df_yy['days_to_expiry'] = (pd.to_datetime('today') - df_yy['expiry_date']).dt.days

        df_yy2 = df_yy[(df_yy['days_to_expiry'] < 0) & (df_yy['days_to_expiry'] > -90)]

        DC_near_expiry = df_yy2.groupby(['store_id', 'type1', 'category', 'age_bracket'],
                                        as_index=False).agg({
            'drug_id': pd.Series.nunique,
            'net_value': ['sum'],
            'taxable': ['sum']}).reset_index(drop=True)
        DC_near_expiry.columns = ["_".join(x) for x in DC_near_expiry.columns.ravel()]

        return DC_near_expiry

    def goodaid_gross_return(self):
        goodaid_store_sales_query = self.mis_queries.goodaid_store_sales_query.format(schema=self.schema_to_select, suffix_to_table=self.suffix_to_table, choose_year=self.choose_year, choose_month = self.choose_month)
        goodaid_store_sales = self.rs_db.get_df(goodaid_store_sales_query)
        goodaid_store_sales.columns = [c.replace('-', '_') for c in goodaid_store_sales.columns]

        goodaid_store_returns_query = self.mis_queries.goodaid_store_returns_query.format(schema=self.schema_to_select, suffix_to_table=self.suffix_to_table, choose_year=self.choose_year, choose_month = self.choose_month)
        goodaid_store_returns = self.rs_db.get_df(goodaid_store_returns_query)
        goodaid_store_returns.columns = [c.replace('-', '_') for c in goodaid_store_returns.columns]

        gross_and_returns = pd.merge(left=goodaid_store_sales, right=goodaid_store_returns,
                                     how='left', on=['year', 'month', 'store_id', 'store_name'])

        return gross_and_returns

    def goodaid_zippin_inventory(self):
        goodaid_zippin_inventory_query =  self.mis_queries.goodaid_zippin_inventory_query.format(schema=self.schema_to_select, suffix_to_table=self.suffix_to_table)
        df_gg = self.rs_db.get_df(goodaid_zippin_inventory_query)
        df_gg.columns = [c.replace('-', '_') for c in df_gg.columns]

        df_gg['days'] = (pd.to_datetime('today') - df_gg['created_at']).dt.days
        conditions = [
            (df_gg['days'] >= 0) & (df_gg['days'] <= 30),
            (df_gg['days'] >= 31) & (df_gg['days'] <= 60),
            (df_gg['days'] >= 61) & (df_gg['days'] <= 90),
            (df_gg['days'] >= 91)]
        choices = ['0_30', '31_60', '61_90', '90+']
        df_gg['ageing'] = np.select(conditions, choices)

        df_gg['expiry_date'] = pd.to_datetime(df_gg['expiry'], format='%Y-%m-%d %H:%M:%S', errors='coerce')

        df_gg['days_to_expiry'] = (df_gg['expiry_date'] - pd.to_datetime('today')).dt.days

        del df_gg['days']
        del df_gg['expiry']

        return df_gg

    def goodaid_dc_inventory(self):
        goodaid_dc_inventory_query =  self.mis_queries.goodaid_dc_inventory_query.format(schema=self.schema_to_select, suffix_to_table=self.suffix_to_table)
        df_jk1 = self.rs_db.get_df(goodaid_dc_inventory_query)
        df_jk1.columns = [c.replace('-', '_') for c in df_jk1.columns]

        return df_jk1

    def goodaid_wh_inventory(self):
        date = datetime.datetime(int(self.choose_year), int(self.choose_month)+1, 1, 0, 0, 0).strftime('%Y-%m-%d')
        goodaid_wh_inventory_query =  self.mis_queries.goodaid_wh_inventory_query.format(date = date)
        wh_inv = self.rs_db.get_df(goodaid_wh_inventory_query)
        wh_inv.columns = [c.replace('-', '_') for c in wh_inv.columns]

        goodaid_drugs_query = self.mis_queries.goodaid_drugs_query.format(schema=self.schema_to_select, suffix_to_table=self.suffix_to_table)
        goodaid_drugs = self.rs_db.get_df(goodaid_drugs_query)
        goodaid_drugs.columns = [c.replace('-', '_') for c in goodaid_drugs.columns]

        wh_inventory = pd.merge(left=wh_inv, right=goodaid_drugs,
                                how='inner', on=['drug_id'])

        return wh_inventory






        return df_jk1

    def store_info(self):
        store_info_query = self.mis_queries.store_info_query.format(schema=self.schema_to_select,
                                                                                   suffix_to_table=self.suffix_to_table)
        store_info = self.rs_db.get_df(store_info_query)
        store_info.columns = [c.replace('-', '_') for c in store_info.columns]

        return store_info








