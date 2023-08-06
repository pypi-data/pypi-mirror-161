import argparse
import sys
import os
sys.path.append('../../../..')

from zeno_etl_libs.logger import get_logger
from zeno_etl_libs.db.db import DB


def main(db, table_suffix):
    table_name = f"sales"
    bill_table_name = "bill-flags"
    stores_master_table_name = "stores-master"
    if table_suffix:
        table_name = f"sales_{table_suffix}"
        bill_table_name = f"bill-flags-{table_suffix}"
        stores_master_table_name = f"stores-master-{table_suffix}"

    db.execute(query="begin ;")

    #Update drugs

    drugs_update_query = f"""
        update
            "prod2-generico"."{table_name}"
        set
            "updated-at" = convert_timezone('Asia/Calcutta', GETDATE()),
            "drug-name" = c."drug-name",
            "type" = c."type",
            "category" = c."category",
            "hsncode" = c."hsncode",
            "is-repeatable" = c."is-repeatable",
            "composition" = c."composition",
            "company" = c."company"
        from
            "prod2-generico"."{table_name}" s
        join "prod2-generico"."drugs" c on
            c."id" = s."drug-id"
        where
            (NVL(s."drug-name",'') != c."drug-name"
            or NVL(s."type",'') != c."type"
            or NVL(s."category",'') != c."category"
            or NVL(s."hsncode",'') != c."hsncode"
            or NVL(s."is-repeatable") != c."is-repeatable"
            or NVL(s."composition",'') != c."composition"
            or NVL(s."company",'') != c."company");              
                            """

    db.execute(query=drugs_update_query)

    # Update patients info

    patients_update_query = f"""    
        update
            "prod2-generico"."{table_name}"
        set
            "updated-at" = convert_timezone('Asia/Calcutta', GETDATE()),
            "patient-category" = p."patient-category",
            "p-reference" = p."reference"
        from
            "prod2-generico"."{table_name}" s
        join "prod2-generico"."patients" p on
            s."patient-id" = p."id"
        where
            (NVL(s."patient-category",'') != p."patient-category" or
            NVL(s."p-reference",'') != p."reference");
                            """
    db.execute(query=patients_update_query)

    # Update patients_metadata info

    patients_m_update_query = f"""    
            update
                "prod2-generico"."{table_name}"
            set
                "updated-at" = convert_timezone('Asia/Calcutta', GETDATE()),
                "first-bill-date" = pm."first-bill-date"
            from
                "prod2-generico"."{table_name}" s
            join "prod2-generico"."patients-metadata" pm on
                s."patient-id" = pm."patient-id"
            where
                (NVL(to_char(s."first-bill-date", 'YYYY-MM-DD'),'') != to_char(pm."first-bill-date", 'YYYY-MM-DD'));
                                """
    db.execute(query=patients_m_update_query)

    # Update stores information

    stores_update_query = f"""    
        update
            "prod2-generico"."{table_name}"
        set
            "updated-at" = convert_timezone('Asia/Calcutta', GETDATE()),
            "store-manager" = msm."store-manager",
            "line-manager" = msm."line-manager",
            "abo" = msm.abo,
            "city" = msm.city,
            "store-b2b" = msm."store-b2b",
            "acquired" = msm."acquired" ,
            "old-new-static" = msm."old-new-static",
            "store-name" = msm.store
        from
            "prod2-generico"."{table_name}" s
        join "prod2-generico"."{stores_master_table_name}" as msm on
            s."store-id" = msm."id"
        where
            (NVL(s."store-manager",'') != msm."store-manager"
            or NVL(s."line-manager",'') != msm."line-manager"
            or NVL(s."abo",'') != msm.abo
            or NVL(s."city",'') != msm.city
            or NVL(s."store-b2b",'') != msm."store-b2b"
            or NVL(s."acquired",999) != msm."acquired"
            or NVL(s."old-new-static",'') != msm."old-new-static"
            or NVL(s."store-name",'') != msm.store);
                            """

    db.execute(query=stores_update_query)

    # Update bill_flags information

    bill_flags_update_query = f"""               
        update
            "prod2-generico"."{table_name}"
        set
            "updated-at" = convert_timezone('Asia/Calcutta', GETDATE()),
            "pr-flag" = NVL(pso2."pr-flag", false),
            "hd-flag" = NVL(pso2."hd-flag", false),
            "ecom-flag" = NVL(pso2."ecom-flag", false),
            "crm-flag" = NVL(pso2."crm-flag", false)
        from
            "prod2-generico"."{table_name}" s
        join "prod2-generico"."{bill_table_name}" as pso2 on
            s."bill-id" = pso2."id"
        where
            (NVL(s."pr-flag",false) != NVL(pso2."pr-flag", false) or NVL(s."hd-flag",false) != NVL(pso2."hd-flag", false) or NVL(s."ecom-flag", false) != NVL(pso2."ecom-flag", false)
            or NVL(s."crm-flag", false) != NVL(pso2."crm-flag", false));
                                """

    db.execute(query=bill_flags_update_query)

    """ committing the transaction """
    db.execute(query=" commit; ")



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="This is ETL script.")
    parser.add_argument('-e', '--env', default="dev", type=str, required=False,
                        help="This is env(dev, stag, prod)")
    parser.add_argument('-ts', '--table_suffix', default="", type=str, required=False,
                        help="Table suffix for testing.")
    args, unknown = parser.parse_known_args()
    env = args.env
    os.environ['env'] = env
    logger = get_logger()
    table_suffix = args.table_suffix
    logger.info(f"env: {env}")

    rs_db = DB()
    rs_db.open_connection()

    """ For single transaction  """
    rs_db.connection.autocommit = False

    """ calling the main function """
    main(db=rs_db, table_suffix=table_suffix)

    # Closing the DB Connection
    rs_db.close_connection()
