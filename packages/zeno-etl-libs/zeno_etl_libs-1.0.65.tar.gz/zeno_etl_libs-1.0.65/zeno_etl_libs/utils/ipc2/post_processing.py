import pandas as pd
import numpy as np


def post_processing(safety_stock_df, weekly_fcst, seg_df, store_id, schema,
                    db, logger):
    # get drug_name, type and grade
    seg_df[['store_id', 'drug_id']] = seg_df['ts_id'].str.split('_', expand=True)
    seg_df['store_id'] = seg_df['store_id'].astype(int)
    seg_df['drug_id'] = seg_df['drug_id'].astype(int)
    drug_list1 = list(safety_stock_df["drug_id"].unique())
    drug_list2 = list(seg_df["drug_id"].unique())
    drug_list = tuple(set(drug_list1+drug_list2))  # get drugs in both tables

    q_drug_info = f"""
        select d.id as drug_id, "drug-name" as drug_name, type,
            coalesce(doi."drug-grade", 'NA') as drug_grade
        from "{schema}".drugs d 
        left join "{schema}"."drug-order-info" doi
        on d.id = doi."drug-id"
        where d.id in {drug_list}
        and doi."store-id" = {store_id}
        """
    df_drug_info = db.get_df(q_drug_info)

    # get store name
    q_store_name = f""" select name from "{schema}".stores where id = {store_id} """
    store_name = db.get_df(q_store_name)['name'][0]

    # get current inventory and avg_ptr info
    q_inv = f"""
            select "drug-id" as drug_id, sum("locked-quantity"+quantity+
                "locked-for-audit"+"locked-for-transfer"+"locked-for-check"+
                "locked-for-return") as curr_inventory
            from "{schema}"."inventory-1" i 
            where "store-id" = {store_id}
            and "drug-id" in {drug_list}
            group by "drug-id" 
            """
    df_inv = db.get_df(q_inv)

    q_avg_ptr_store = f"""
            select "drug-id" as drug_id, avg(ptr) as avg_ptr
            from "{schema}"."inventory-1" i 
            where "store-id" = {store_id}
            and "drug-id" in {drug_list}
            and DATEDIFF(day, date("created-at"), current_date) < 365
            group by "drug-id" 
            """
    df_avg_ptr_store = db.get_df(q_avg_ptr_store)

    q_avg_ptr_sys = f"""
            select "drug-id" as drug_id, "avg-ptr" as avg_ptr_sys
            from "{schema}"."drug-std-info" dsi 
            """
    df_avg_ptr_sys = db.get_df(q_avg_ptr_sys)

    # add all to ss table
    safety_stock_df['store_id'] = store_id
    safety_stock_df['store_name'] = store_name
    safety_stock_df = safety_stock_df.merge(
        df_drug_info, on='drug_id', how='left')
    safety_stock_df['drug_grade'].fillna('NA', inplace=True)
    safety_stock_df = safety_stock_df.merge(
        df_inv, on='drug_id', how='left')
    safety_stock_df = safety_stock_df.merge(
        df_avg_ptr_store, on='drug_id', how='left')
    safety_stock_df = safety_stock_df.merge(
        df_avg_ptr_sys, on='drug_id', how='left')

    # replace NA in avg_ptr with system-avg_ptr
    safety_stock_df["avg_ptr"] = np.where(safety_stock_df["avg_ptr"].isna(),
                                          safety_stock_df["avg_ptr_sys"],
                                          safety_stock_df["avg_ptr"])
    safety_stock_df.drop("avg_ptr_sys", axis=1, inplace=True)
    safety_stock_df["avg_ptr"] = safety_stock_df["avg_ptr"].astype(float)

    # calculate DOH
    safety_stock_df['safety_stock_days'] = np.where(
        (safety_stock_df['fcst'] == 0) | (safety_stock_df['safety_stock'] == 0),
        0, safety_stock_df['safety_stock'] / (safety_stock_df['fcst'] / 28))
    safety_stock_df['reorder_days'] = np.where(
        (safety_stock_df['fcst'] == 0) | (safety_stock_df['reorder_point'] == 0),
        0, safety_stock_df['reorder_point'] / (safety_stock_df['fcst'] / 28))
    safety_stock_df['order_upto_days'] = np.where(
        (safety_stock_df['fcst'] == 0) | (safety_stock_df['order_upto_point'] == 0),
        0, safety_stock_df['order_upto_point'] / (safety_stock_df['fcst'] / 28))

    # calculate max-value, to-order-qty and to-order-val
    safety_stock_df["max_value"] = safety_stock_df['order_upto_point'] * \
                                   safety_stock_df['avg_ptr']

    safety_stock_df['to_order_quantity'] = np.where(
        safety_stock_df['curr_inventory'] <= safety_stock_df['reorder_point'],
        safety_stock_df['order_upto_point'] - safety_stock_df['curr_inventory'],
        0)
    safety_stock_df['to_order_value'] = safety_stock_df['to_order_quantity'] * \
                                        safety_stock_df['avg_ptr']

    # formatting weekly_fcst table
    weekly_fcst['store_name'] = store_name
    weekly_fcst.rename(
        columns={'date': 'week_begin_dt', 'fcst': 'weekly_fcst',
                 'std': 'fcst_std'}, inplace=True)

    # formatting segmentation table
    seg_df.rename(columns={'std': 'sales_std', 'cov': 'sales_cov',
                           'Mixed': 'bucket', 'Group': 'group',
                           'PLC Status L1': 'plc_status', 'ADI': 'adi',
                           'total_LY_sales': 'total_ly_sales',
                           'start_date': 'sale_start_date'}, inplace=True)
    seg_df['plc_status'] = np.where(seg_df['plc_status'] == 'NPI',
                                       'New Product', seg_df['plc_status'])
    seg_df['sale_start_date'] = seg_df['sale_start_date'].dt.date
    seg_df['store_name'] = store_name
    seg_df = seg_df.merge(df_drug_info, on='drug_id', how='left')
    seg_df['drug_grade'].fillna('NA', inplace=True)

    # get oder_value_summary for email attachment
    order_value = safety_stock_df.pivot_table(
        index=['store_id', 'store_name', 'type'],
        values=['to_order_quantity', 'to_order_value'], aggfunc='sum',
        margins=True, margins_name='Total').reset_index()

    return safety_stock_df, order_value, weekly_fcst, seg_df

