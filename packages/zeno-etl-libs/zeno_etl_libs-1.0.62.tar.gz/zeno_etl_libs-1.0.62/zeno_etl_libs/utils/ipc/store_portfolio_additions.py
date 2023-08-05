import numpy as np


def generic_portfolio(safety_stock_df, db, schema, logger=None):
    """
    To keep at least 1 drug in every active generic compositions
    """
    comp_drugs_to_keep = get_preference_drugs(db, schema, logger)

    # get compositions of all generic drugs in store with OUP>0
    all_drugs = tuple(safety_stock_df.loc[
                          safety_stock_df["order_upto_point"] > 0][
                          "drug_id"].unique())
    q_gen_drugs = f"""
            select id as "drug-id", composition 
            from "{schema}".drugs d 
            where id in {all_drugs}
            and "type" = 'generic'
            """
    df_gen_drugs = db.get_df(q_gen_drugs)
    df_gen_drugs.columns = [c.replace('-', '_') for c in df_gen_drugs.columns]

    df_gen_drugs = df_gen_drugs.loc[df_gen_drugs["composition"] != '']
    compostitions_in_store = list(df_gen_drugs["composition"].unique())

    # get additional composition-drugs to add
    compositon_not_in_store = comp_drugs_to_keep.loc[
        ~comp_drugs_to_keep["composition"].isin(compostitions_in_store)]

    logger.info(f"To keep {compositon_not_in_store.shape[0]} additional "
                f"composition-drugs in store")

    # drugs to add in current ss table
    drugs_to_add = compositon_not_in_store[["drug_id", "std_qty"]]

    final_df = safety_stock_df.merge(drugs_to_add, on="drug_id",
                                     how="outer")

    # handle NaN columns for additional drugs
    final_df["model"] = final_df["model"].fillna('NA')
    final_df["bucket"] = final_df["bucket"].fillna('NA')
    final_df['fcst'] = final_df['fcst'].fillna(0)
    final_df['std'] = final_df['std'].fillna(0)
    final_df['lead_time_mean'] = final_df['lead_time_mean'].fillna(0)
    final_df['lead_time_std'] = final_df['lead_time_std'].fillna(0)

    final_df["safety_stock"] = final_df["safety_stock"].fillna(0)
    final_df["reorder_point"] = final_df["reorder_point"].fillna(0)
    final_df["order_upto_point"] = final_df["order_upto_point"].fillna(0)

    # set OUP=STD_QTY for added drugs
    final_df["order_upto_point"] = np.where(final_df["std_qty"].notna(),
                                            final_df["std_qty"],
                                            final_df["order_upto_point"])

    final_df = final_df.drop("std_qty", axis=1)

    return final_df


def get_preference_drugs(db, schema, logger=None):
    """
    Get all active generic compositions in WH and the preferred drugs in that
    compositions, the preference order is as follows:
    * Choose GAID if available
    * Else choose highest selling drug in past 90 days at system level
    """
    q_wh_gen_sku = f"""
        select wssm."drug-id" , d.composition , d."company-id" 
        from "{schema}"."wh-sku-subs-master" wssm 
        left join "{schema}".drugs d on wssm."drug-id" = d.id 
        where "add-wh" = 'Yes' 
        and d."type" = 'generic' 
        """
    df_wh_gen_sku = db.get_df(q_wh_gen_sku)
    df_wh_gen_sku.columns = [c.replace('-', '_') for c in df_wh_gen_sku.columns]

    # clear drugs with no composition present
    df_wh_gen_sku = df_wh_gen_sku.loc[df_wh_gen_sku["composition"] != '']

    logger.info(f"Distinct generic compositions in WH: {len(df_wh_gen_sku.composition.unique())}")
    logger.info(f"Distinct generic drugs in WH: {df_wh_gen_sku.shape[0]}")

    drug_ids = tuple(df_wh_gen_sku.drug_id.unique())

    # get past 90 days sales info of the preferred drugs
    q_sales = f"""
        select "drug-id" , sum("revenue-value") as "gross-sales"
        from "{schema}".sales s 
        where "drug-id" in {drug_ids}
        and datediff('day', date("created-at"), CURRENT_DATE ) < 90
        and "bill-flag" = 'gross' 
        group by "drug-id" 
        """
    df_sales = db.get_df(q_sales)
    df_sales.columns = [c.replace('-', '_') for c in df_sales.columns]

    df_wh_gen_sku = df_wh_gen_sku.merge(df_sales, on="drug_id", how="left")

    df_wh_gen_sku["gross_sales"] = df_wh_gen_sku["gross_sales"].fillna(0)
    df_wh_gen_sku["is_gaid"] = np.where(df_wh_gen_sku["company_id"] == 6984, 1, 0)

    # order priority: GA, Sales
    df_wh_gen_sku = df_wh_gen_sku.sort_values(
        by=['composition', 'is_gaid', 'gross_sales'],
        ascending=False)

    # choose the first preference for every composition
    comp_drug_list = df_wh_gen_sku.groupby('composition', as_index=False).agg(
        {'drug_id': 'first'})

    # get std-qty to keep
    q_drug_std_info = f"""
                select "drug-id" , "std-qty"
                from "{schema}"."drug-std-info" dsi 
                """
    df_drug_std_info = db.get_df(q_drug_std_info)
    df_drug_std_info.columns = [c.replace('-', '_') for c in df_drug_std_info.columns]

    comp_drug_list = comp_drug_list.merge(df_drug_std_info, on="drug_id",
                                          how="left")

    # fill NA values with defaults
    comp_drug_list["std_qty"] = comp_drug_list["std_qty"].fillna(1)

    return comp_drug_list
