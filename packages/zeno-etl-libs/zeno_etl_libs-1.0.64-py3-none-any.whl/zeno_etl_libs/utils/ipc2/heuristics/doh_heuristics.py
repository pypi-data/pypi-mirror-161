"""
Capping on SS-DOH, Logic:
* For WH drugs, keep maximum of 7 days SS-DOH
* For Non-WH drugs, keep maximum of 14 days SS-DOH
"""
import pandas as pd
import numpy as np


def ss_doh_wh_cap(safety_stock_df, schema, db, cap_doh=7):
    drug_list = get_wh_drug_list(schema, db)

    ss_correct = safety_stock_df.loc[safety_stock_df["drug_id"].isin(drug_list)]
    ss_rest = safety_stock_df.loc[~safety_stock_df["drug_id"].isin(drug_list)]

    ss_correct['safety_stock_max'] = np.round((ss_correct['fcst'] / 28) * cap_doh)
    ss_correct['safety_stock'] = np.where(
        ss_correct['safety_stock'] > ss_correct['safety_stock_max'],
        ss_correct['safety_stock_max'], ss_correct['safety_stock'])
    ss_correct.drop('safety_stock_max', axis=1, inplace=True)

    safety_stock_df = pd.concat([ss_rest, ss_correct])

    return safety_stock_df


def ss_doh_non_wh_cap(safety_stock_df, schema, db, cap_doh=14):
    drug_list = get_wh_drug_list(schema, db)

    ss_correct = safety_stock_df.loc[~safety_stock_df["drug_id"].isin(drug_list)]
    ss_rest = safety_stock_df.loc[safety_stock_df["drug_id"].isin(drug_list)]

    ss_correct['safety_stock_max'] = np.round((ss_correct['fcst'] / 28) * cap_doh)
    ss_correct['safety_stock'] = np.where(
        ss_correct['safety_stock'] > ss_correct['safety_stock_max'],
        ss_correct['safety_stock_max'], ss_correct['safety_stock'])
    ss_correct.drop('safety_stock_max', axis=1, inplace=True)

    safety_stock_df = pd.concat([ss_rest, ss_correct])

    return safety_stock_df


def get_wh_drug_list(schema, db):
    q_wh_active_drugs = f"""
                   select distinct "drug-id" as drug_id
                   from "{schema}"."wh-sku-subs-master" wssm 
                   where "add-wh" = 'Yes'
                   """
    drug_list = db.get_df(q_wh_active_drugs)["drug_id"].values

    return drug_list
