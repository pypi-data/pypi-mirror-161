"""
General purpose module to write Min,SS,Max values to DOID
(NOT FOR IPC)
"""

import pandas as pd
import numpy as np
import time
from zeno_etl_libs.django.api import Sql
from zeno_etl_libs.db.db import MySQL


def doid_custom_write(data, logger, ss_col=None, rop_col=None, oup_col=None):
    """
    data : (pd.DataFrame) can contains columns ["store_id", "drug_id", ss_col, rop_col, oup_col]

    if only "store_id" and "drug_id" present then ss,rop,oup is set to zero
    and updated into DOID
    """
    data = data.drop_duplicates()
    if None in [ss_col, rop_col, oup_col]:
        data["min"] = 0
        data["safe_stock"] = 0
        data["max"] = 0
    else:
        data.rename({ss_col: 'min', rop_col: 'safe_stock', oup_col: 'max'},
                    axis=1, inplace=True)

    mysql = MySQL(read_only=False)
    mysql.open_connection()
    sql = Sql()
    missed_entries = pd.DataFrame()

    logger.info("MySQL DOID write starts")
    for store_id in data['store_id'].unique():
        logger.info('Mysql upload for store ' + str(store_id))
        current_ss_query = f"""
            SELECT doid.id, doid.`store-id` , doid.`drug-id` , doid.min,
            doid.`safe-stock` , doid.max
            FROM `drug-order-info-data` doid 
            where doid.`store-id` = {store_id}
            """
        current_ss = pd.read_sql(current_ss_query, mysql.connection)
        current_ss.columns = [c.replace('-', '_') for c in current_ss.columns]

        data_store = data.loc[
            data['store_id'] == store_id,
            ['store_id', 'drug_id', 'min', 'safe_stock', 'max']]

        ss_joined = current_ss.merge(
            data_store, on=['store_id', 'drug_id'], how='right',
            suffixes=('_old', ''))

        ss_joined['flag'] = np.where(
            (ss_joined['min_old'] == ss_joined['min']) &
            (ss_joined['safe_stock_old'] == ss_joined['safe_stock']) &
            (ss_joined['max_old'] == ss_joined['max']),
            'values same', 'values changed')

        ss_to_upload = ss_joined.loc[
            ss_joined['flag'] == 'values changed',
            ['id', 'min', 'safe_stock', 'max']]

        logger.info('SS to update only for ' + str(
            ss_joined[ss_joined['flag'] != 'values same'].shape[0]))

        ss_to_upload["id"] = ss_to_upload["id"].astype(float)

        data_to_be_updated_list = list(ss_to_upload.apply(dict, axis=1))
        if len(data_to_be_updated_list) > 0:
            chunk_size = 1000
            for i in range(0, len(data_to_be_updated_list), chunk_size):
                status, msg = sql.update(
                    {'table': 'DrugOrderInfoData',
                     'data_to_be_updated': data_to_be_updated_list[
                                           i:i + chunk_size]}, logger)
                logger.info(f"DrugOrderInfoData update API "
                            f"count: {min(i + chunk_size, len(data_to_be_updated_list))}, "
                            f"status: {status}, msg: {msg}")

            drug_list = str(list(ss_joined.loc[
                                     ss_joined[
                                         'flag'] == 'values changed', 'drug_id'].unique())
                            ).replace('[', '(').replace(']', ')')

            update_test_query = f"""
                                SELECT `store-id` , `drug-id` , min , `safe-stock` , max
                                from `drug-order-info-data` doid 
                                where `store-id` = {store_id}
                                and `drug-id` in {drug_list}
                                """
            time.sleep(15)
            update_test = pd.read_sql(update_test_query, mysql.connection)
            update_test.columns = [c.replace('-', '_') for c in
                                   update_test.columns]

            update_test = ss_joined.loc[
                ss_joined['flag'] == 'values changed',
                ['store_id', 'drug_id', 'min', 'safe_stock', 'max']].merge(
                update_test, on=['store_id', 'drug_id'],
                suffixes=('_new', '_prod'))
            update_test['mismatch_flag'] = np.where(
                (update_test['min_new'] == update_test['min_prod']) &
                (update_test['safe_stock_new'] == update_test[
                    'safe_stock_prod']) &
                (update_test['max_new'] == update_test['max_prod']),
                'updated', 'not updated')

            missed_entries = missed_entries.append(
                update_test[update_test['mismatch_flag'] == 'not updated'])

            logger.info(
                'Entries updated successfully: ' +
                str(update_test[
                        update_test['mismatch_flag'] == 'updated'].shape[0]))

            logger.info(
                'Entries not updated successfully: ' +
                str(update_test[
                        update_test['mismatch_flag'] == 'not updated'].shape[
                        0]))

    mysql.close()

    return missed_entries
