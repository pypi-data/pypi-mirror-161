import numpy as np
import pandas as pd
import datetime as dt


def check_oup_outlier(safety_stock_df, store_id, reset_date, db, schema):
    """
    Find cases where OUP > Past 90 days net-sales + pr_loss
    """
    safety_stock_df.columns = [c.replace('-', '_') for c in
                               safety_stock_df.columns]

    # check only for cases where fcst & oup > 0
    df_check_cases = safety_stock_df.loc[
        (safety_stock_df["fcst"] > 0) & (safety_stock_df["order_upto_point"] > 0)]
    df_check_cases = df_check_cases[[
        "store_id", "store_name", "drug_id", "drug_name", "type", "model", "fcst",
        "safety_stock", "reorder_point", "order_upto_point", "correction_flags",
        "curr_inventory", "to_order_quantity", "to_order_value"]]

    drug_list = list(df_check_cases["drug_id"].unique())
    drug_list_str = str(drug_list).replace('[', '(').replace(']', ')')
    p90d_begin_date = dt.datetime.strptime(reset_date, '%Y-%m-%d').date() - \
                      dt.timedelta(days=90)
    p90d_begin_date = p90d_begin_date.strftime("%Y-%m-%d")
    q_p90d_sales = f"""
            select "drug-id" as drug_id, sum("net-quantity") as net_sales_p90d
            from "{schema}".sales s 
            where "store-id" = {store_id}
            and "drug-id" in {drug_list_str}
            and date("created-at") >= '{p90d_begin_date}'
            and date("created-at") < '{reset_date}' 
            group by "drug-id" 
            """
    df_p90d_sales = db.get_df(q_p90d_sales)

    q_p90d_pr_loss = f"""
            select "drug-id" as drug_id, sum("loss-quantity") as pr_loss_p90d
            from "{schema}"."cfr-patient-request"
            where "store-id" = {store_id}
            and "shortbook-date" >= '{p90d_begin_date}'
            and "shortbook-date" < '{reset_date}'
            and "drug-id" in {drug_list_str}
            and ("drug-category" = 'chronic' or "repeatability-index" >= 40)
            and "loss-quantity" > 0
            group by "drug-id" 
            """
    df_p90d_pr_loss = db.get_df(q_p90d_pr_loss)

    df_check_cases = df_check_cases.merge(df_p90d_sales, on="drug_id",
                                          how="left")
    df_check_cases = df_check_cases.merge(df_p90d_pr_loss, on="drug_id",
                                          how="left")
    df_check_cases["net_sales_p90d"] = df_check_cases["net_sales_p90d"].fillna(0).astype(int)
    df_check_cases["pr_loss_p90d"] = df_check_cases["pr_loss_p90d"].fillna(0).astype(int)
    df_check_cases["p90d_demand"] = df_check_cases["net_sales_p90d"] + df_check_cases["pr_loss_p90d"]

    df_check_cases["outlier"] = 'NA'
    df_check_cases["outlier"] = np.where(
        df_check_cases["order_upto_point"] > df_check_cases["p90d_demand"],
        'Y', 'N')

    df_outliers = df_check_cases.loc[df_check_cases["outlier"] == 'Y']
    outlier_drugs = list(df_outliers["drug_id"].unique())

    manual_doid_upd_df = df_outliers[["store_id", "drug_id", "safety_stock",
                                      "reorder_point", "order_upto_point"]]
    manual_doid_upd_df.rename(columns={"safety_stock": "ss",
                                       "reorder_point": "rop",
                                       "order_upto_point": "oup"},
                              inplace=True)

    return outlier_drugs, df_outliers, manual_doid_upd_df
