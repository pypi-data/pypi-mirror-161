import pandas as pd
import numpy as np
import datetime as dt


def v3_corrections(final_ss_df, store_id, corrections_selling_probability_cutoff,
                   corrections_cumulative_probability_cutoff, schema, db, logger):

    final_ss_df['store_id'] = store_id

    q_prob = f"""
        select *
        from "{schema}"."ipc-corrections-rest-cases"
        where "store-id" = {store_id}
        """
    q_prob_111 = f"""
        select *
        from "{schema}"."ipc-corrections-111-cases"
        where "store-id" = {store_id}
        """
    prob_matrix = db.get_df(q_prob)
    df_111 = db.get_df(q_prob_111)
    prob_matrix.columns = [c.replace('-', '_') for c in prob_matrix.columns]
    df_111.columns = [c.replace('-', '_') for c in df_111.columns]

    # list of drugs for which corrections is required. i.e. max value 0.
    df_corrections_list = final_ss_df[
        final_ss_df['order_upto_point'] == 0][['store_id', 'drug_id']]
    df_corrections = pd.merge(
        df_corrections_list, prob_matrix, how='inner',
        on=['store_id', 'drug_id'], validate='one_to_one')

    df_corrections = df_corrections.drop(columns={'corrected_max'})
    df_corrections['order_upto_point'] = np.round(
        df_corrections['current_ma_3_months'])

    df_corrections_1 = df_corrections[
        (df_corrections['cumm_prob'] >=
         corrections_cumulative_probability_cutoff['ma_less_than_2']) &
        (df_corrections['current_flag_ma_less_than_2'] == 1)]
    df_corrections_2 = df_corrections[
        (df_corrections['cumm_prob'] >=
         corrections_cumulative_probability_cutoff['ma_more_than_2']) &
        (df_corrections['current_flag_ma_less_than_2'] == 0)]

    df_corrections_1 = df_corrections_1[
        (df_corrections_1['selling_probability'] >=
         corrections_selling_probability_cutoff['ma_less_than_2']) &
        (df_corrections_1['current_flag_ma_less_than_2'] == 1)]
    df_corrections_2 = df_corrections_2[
        (df_corrections_2['selling_probability'] >=
         corrections_selling_probability_cutoff['ma_more_than_2']) &
        (df_corrections_2['current_flag_ma_less_than_2'] == 0)]

    df_corrections = pd.concat(
        [df_corrections_1, df_corrections_2]).reset_index(drop=True)
    df_corrections_final = df_corrections.copy()[
        ['store_id', 'drug_id', 'current_bucket', 'selling_probability',
         'cumm_prob', 'current_flag_ma_less_than_2', 'avg_ptr',
         'current_ma_3_months']]

    df_corrections = df_corrections[
        ['store_id', 'drug_id', 'order_upto_point']]
    df_corrections['reorder_point'] = np.floor(
        df_corrections['order_upto_point'] / 2)
    df_corrections['safety_stock'] = np.floor(
        df_corrections['order_upto_point'] / 4)

    df_corrections = df_corrections.set_index(['store_id', 'drug_id'])
    final_ss_df = final_ss_df.set_index(['store_id', 'drug_id'])

    final_ss_df.update(df_corrections)
    final_ss_df = final_ss_df.reset_index()
    df_corrections = df_corrections.reset_index()

    df_corrections = pd.merge(
        df_corrections, df_corrections_final, on=['store_id', 'drug_id'],
        how='left', validate='one_to_one')

    # update 111 cases here.
    df_corrections_111 = pd.merge(
        df_corrections_list, df_111, how='inner',
        on=['store_id', 'drug_id'], validate='one_to_one')

    df_corrections_111 = df_corrections_111.drop(
        columns={'original_max', 'corrected_max',
                 'inv_impact', 'max_impact'}, axis=1)

    df_corrections_111['order_upto_point'] = np.round(
        df_corrections_111['ma_3_months'])
    df_corrections_111['reorder_point'] = np.floor(
        df_corrections_111['order_upto_point'] / 2)
    df_corrections_111['safety_stock'] = np.floor(
        df_corrections_111['order_upto_point'] / 4)

    df_corrections_111 = df_corrections_111.set_index(
        ['store_id', 'drug_id'])
    final_ss_df = final_ss_df.set_index(['store_id', 'drug_id'])
    final_ss_df.update(df_corrections_111)

    final_ss_df = final_ss_df.reset_index()
    df_corrections_111 = df_corrections_111.reset_index()

    # set reset date
    curr_date = str(dt.date.today())
    df_corrections['reset_date'] = curr_date
    df_corrections_111['reset_date'] = curr_date

    final_ss_df.drop('store_id', axis=1, inplace=True)

    return final_ss_df
