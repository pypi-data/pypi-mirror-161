import numpy as np


def compare_df(df_pre, df_post, logger, cols_to_compare=None):
    num_drugs = len(df_pre["drug_id"].unique())
    if num_drugs != df_pre.shape[0]:
        logger.info("WARNING: Duplicate drug entries present!")

    if cols_to_compare is None:
        cols_to_compare = ["safety_stock", "reorder_point", "order_upto_point"]

    df_pre = df_pre[["drug_id"] + cols_to_compare]
    df_post = df_post[["drug_id"] + cols_to_compare]

    df_comb = df_pre.merge(df_post, on="drug_id", how="outer",
                           suffixes=('_pre', '_post'))

    df_comb["changed"] = 'N'
    for col in cols_to_compare:
        df_comb["changed"] = np.where(
            df_comb[col+str('_pre')] != df_comb[col+str('_post')],
            'Y', df_comb["changed"])

    drugs_corrected = list(df_comb.loc[df_comb["changed"] == 'Y']["drug_id"].unique())

    return drugs_corrected


def add_correction_flag(df, corr_drug_list, corr_flag):
    if "correction_flags" not in df.columns:
        df["correction_flags"] = ""
    df["correction_flags"] = df["correction_flags"].fillna("")

    df["correction_flags"] = np.where(
        (df["drug_id"].isin(corr_drug_list)) & (df["correction_flags"] != ""),
        df["correction_flags"] + '-' + corr_flag, df["correction_flags"])
    df["correction_flags"] = np.where(
        (df["drug_id"].isin(corr_drug_list)) & (df["correction_flags"] == ""),
        corr_flag, df["correction_flags"])

    return df
