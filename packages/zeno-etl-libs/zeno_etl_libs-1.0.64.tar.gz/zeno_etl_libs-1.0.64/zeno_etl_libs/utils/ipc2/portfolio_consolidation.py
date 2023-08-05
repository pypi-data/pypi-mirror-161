import pandas as pd
import numpy as np


def wh_consolidation(safety_stock_df, db, schema, logger):
    """
    replace for drugs which has a substitute available in WH
    (corrected logic)
    """
    # getting list of SKUs to be rejected and substituted
    wh_subs_query = f"""
            select "drug-id" , "drug-id-replaced" , "same-release" 
            from "{schema}"."wh-sku-subs-master"
            where "add-wh" = 'No'
            """
    df_wh_subs = db.get_df(wh_subs_query)
    df_wh_subs.columns = [c.replace('-', '_') for c in df_wh_subs.columns]

    all_assort_drugs = list(safety_stock_df.loc[
        safety_stock_df["order_upto_point"] > 0]["drug_id"].unique())

    # reject cases
    reject_cases_1 = df_wh_subs.loc[
        df_wh_subs["drug_id"] == df_wh_subs["drug_id_replaced"]]
    reject_drugs_lst_1 = list(reject_cases_1["drug_id"].unique())
    reject_cases_2 = df_wh_subs.loc[
        (df_wh_subs["drug_id"] != df_wh_subs["drug_id_replaced"]) &
        (df_wh_subs["same_release"] == 'NO')]
    reject_drugs_lst_2 = list(reject_cases_2["drug_id"].unique())

    # replace cases
    replace_cases = df_wh_subs.loc[
        (df_wh_subs["drug_id"] != df_wh_subs["drug_id_replaced"]) &
        (df_wh_subs["same_release"] == 'YES')]
    reject_drugs_lst_3 = list(replace_cases["drug_id"].unique())

    replace_merge_df = safety_stock_df.merge(
        replace_cases, on="drug_id", how="inner").drop("same_release", axis=1)[
        ["drug_id", "drug_id_replaced", "safety_stock", "reorder_point", "order_upto_point"]]

    # get preferred entry in case of multiple drug_id with same drug_id_replaced
    # choosing the case with highest OUP
    replace_merge_df = replace_merge_df.sort_values(
        by=['drug_id_replaced', 'order_upto_point'], ascending=False)
    preferred_drug_replace_map = replace_merge_df.groupby(
        "drug_id_replaced").agg({"drug_id": "first"}) # first will have highest OUP

    preferred_drug_replace_df = replace_merge_df.merge(
        preferred_drug_replace_map, on=["drug_id", "drug_id_replaced"], how="inner")

    substitute_drugs_add_df = preferred_drug_replace_df.copy()
    substitute_drugs_add_df = substitute_drugs_add_df.drop("drug_id", axis=1)
    substitute_drugs_add_df.rename(columns={"drug_id_replaced": "drug_id"}, inplace=True)

    # only need to add the substitute if below condition satisfy
    substitute_drugs_add_df = substitute_drugs_add_df.loc[
        (substitute_drugs_add_df["order_upto_point"] > 0) &
        (~substitute_drugs_add_df["drug_id"].isin(all_assort_drugs))]

    # remove previous entry with 0 OUP for substitute drug if present (avoids duplicate)
    substitute_drugs = list(substitute_drugs_add_df["drug_id"].unique())
    safety_stock_df = safety_stock_df.loc[~(
        (safety_stock_df["order_upto_point"] == 0) &
        (safety_stock_df["drug_id"].isin(substitute_drugs)))]

    # filling the relevant columns
    substitute_drugs_add_df['model'] = 'NA'
    substitute_drugs_add_df['bucket'] = 'NA'
    substitute_drugs_add_df['fcst'] = 0
    substitute_drugs_add_df['std'] = 0
    substitute_drugs_add_df['lead_time_mean'] = 0
    substitute_drugs_add_df['lead_time_std'] = 0

    reject_drugs_lst = list(set(reject_drugs_lst_1 + reject_drugs_lst_2 + reject_drugs_lst_3))
    logger.info(f"Drugs to reject: {len(reject_drugs_lst)}")
    logger.info(f"Drugs to add as substitute: {substitute_drugs_add_df.shape[0]}")

    ss_zero_cases = safety_stock_df.loc[safety_stock_df["drug_id"].isin(reject_drugs_lst)]
    ss_rest_cases = safety_stock_df.loc[~safety_stock_df["drug_id"].isin(reject_drugs_lst)]

    ss_zero_cases["safety_stock"] = 0
    ss_zero_cases["reorder_point"] = 0
    ss_zero_cases["order_upto_point"] = 0

    safety_stock_df_final = pd.concat(
        [ss_rest_cases, ss_zero_cases, substitute_drugs_add_df])

    return safety_stock_df_final


def goodaid_consolidation(safety_stock_df, db, schema, logger,
                          substition_type=None):
    """
    for goodaid compositions, only keep goodaid and those drugs in same
    composition which are part of WH portfolio.
    reject all other drugs in that composition
    """
    if substition_type is None:
        substition_type = ['generic']

    # Good Aid SKU list
    ga_sku_query = """
                select wh."drug-id" , d.composition 
                from "{schema}"."wh-sku-subs-master" wh
                left join "{schema}".drugs d 
                on d.id = wh."drug-id" 
                where wh."add-wh" = 'Yes'
                and d."company-id" = 6984
                and d.type in {0}
                """.format(
        str(substition_type).replace('[', '(').replace(']', ')'),
        schema=schema)
    ga_sku = db.get_df(ga_sku_query)
    ga_sku.columns = [c.replace('-', '_') for c in ga_sku.columns]
    logger.info('GoodAid SKU list ' + str(ga_sku.shape[0]))

    # Generic Top SKU
    ga_active_composition = tuple(ga_sku['composition'].values)
    top_sku_query = """
                select wh."drug-id" , d.composition 
                from "{schema}"."wh-sku-subs-master" wh
                left join "{schema}".drugs d 
                on d.id = wh."drug-id" 
                where wh."add-wh" = 'Yes'
                and d."company-id" != 6984
                and d.type in {0}
                and d.composition in {1}
                """.format(
        str(substition_type).replace('[', '(').replace(']', ')'),
        str(ga_active_composition), schema=schema)
    top_sku = db.get_df(top_sku_query)
    top_sku.columns = [c.replace('-', '_') for c in top_sku.columns]
    logger.info('GoodAid comp Top SKU list ' + str(top_sku.shape[0]))

    # SS substition for other drugs
    rest_sku_query = """
                select id as drug_id, composition
                from "{schema}".drugs
                where composition in {0}
                and id not in {1}
                and "company-id" != 6984
                and type in {2}
                """.format(str(ga_active_composition),
                           str(tuple(top_sku['drug_id'].values)),
                           str(substition_type).replace('[', '(').replace(']', ')'),
                           schema=schema)
    rest_sku = db.get_df(rest_sku_query)
    logger.info('GoodAid comp rest SKU list ' + str(rest_sku.shape[0]))

    # substitution logic starts
    gaid_drug_list = list(rest_sku["drug_id"].unique())
    top_drug_list = list(top_sku["drug_id"].unique())
    reject_drug_list = list(rest_sku["drug_id"].unique())

    ss_zero_cases = safety_stock_df.loc[safety_stock_df["drug_id"].isin(reject_drug_list)]
    ss_rest_cases = safety_stock_df.loc[~safety_stock_df["drug_id"].isin(reject_drug_list)]

    logger.info('Setting rest sku SS, ROP, OUP to zero')
    ss_zero_cases["safety_stock"] = 0
    ss_zero_cases["reorder_point"] = 0
    ss_zero_cases["order_upto_point"] = 0

    safety_stock_df_final = pd.concat([ss_rest_cases, ss_zero_cases])

    return safety_stock_df_final
