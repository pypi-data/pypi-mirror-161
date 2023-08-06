#@owner: akshay.bhutada@zeno.health

#@Purpose: To replicate the table from warehouse db to redshift

import os
import sys

sys.path.append('../../../..')
from zeno_etl_libs.helper.aws.s3 import S3
from zeno_etl_libs.db.db import DB
from zeno_etl_libs.db.db import MSSql
from zeno_etl_libs.logger import get_logger
from zeno_etl_libs.helper import helper
import argparse
import pandas as pd


parser = argparse.ArgumentParser(description="This is ETL script.")
parser.add_argument('-e', '--env', default="dev", type=str, required=False)
args, unknown = parser.parse_known_args()
env = args.env
os.environ['env'] = env

logger = get_logger()

logger.info(f"env: {env}")

rs_db = DB()
rs_db.open_connection()

s3 = S3()

schema = 'prod2-generico'

# from bhiwandi wh
mssql = MSSql(connect_via_tunnel=False)
cnxn = mssql.open_connection()
cursor = cnxn.cursor()

query = ''' SELECT  * FROM Salepurchase2 WHERE Vtype not in  ('SB')'''
salepur_bhw= pd.read_sql(query, cnxn)
salepur_bhw['warehouse'] = 'BHW'
salepur_bhw['warehouseId'] = 199
logger.info("Data from BHW acquired: " +str(len(salepur_bhw)))

# from Goodaid wh
mssql_ga = MSSql(connect_via_tunnel=False,db='Esdata_WS_2')
cnxn_ga = mssql_ga.open_connection()
cursor_ga = cnxn_ga.cursor()

query = ''' 
SELECT  * FROM Salepurchase2 WHERE Vtype not in  ('SB') '''
salepur_ga= pd.read_sql(query, cnxn_ga)
salepur_ga['warehouse'] = 'GA'
salepur_ga['warehouseId'] = 343
logger.info("Data from GAW acquired: " +str(len(salepur_ga)))

# concating the above dataframes
df_new = pd.concat([salepur_bhw, salepur_ga]).reset_index(drop= True)

df_new[['scm1','scm2','Gacno','Sman','Area','route','CodeCent','ChlnSrlno',
        'RefVno', 'SRGGVno','SBPsrlno','CompCode','mState','PsTypeTOM','ICase',
        'IBox','ILoose','PorderNo','StockLocation']] \
    = df_new[['scm1','scm2','Gacno','Sman','Area','route','CodeCent','ChlnSrlno',
        'RefVno', 'SRGGVno','SBPsrlno','CompCode','mState','PsTypeTOM','ICase',
        'IBox','ILoose','PorderNo','StockLocation']]\
    .apply(pd.to_numeric, errors='ignore').astype('Int64')

df_new.columns= df_new.columns.str.lower()

logger.info("Data from both BHW and GAW concatenated: " +str(len(df_new)))

# def main(rs_db, s3):
table_name = 'salepurchase2'
table_info = helper.get_table_info(db=rs_db, table_name=table_name, schema=schema)

# =========================================================================
# Writing table in Redshift
# =========================================================================
if isinstance(table_info, type(None)):
    raise Exception(f"table: {table_name} do not exist, create the table first")
else:
    print(f"Table:{table_name} exists")
truncate_query = f''' DELETE FROM "{schema}"."{table_name}" '''
rs_db.execute(truncate_query)
logger.info(f"Table:{table_name} table truncated")

s3.write_df_to_db(df=df_new[table_info['column_name']], table_name=table_name, db=rs_db,
                      schema=schema)

logger.info(f"Table:{table_name} table uploaded")
df_new.drop(df_new.index, inplace=True)


#salepurchase1 table
# SP1 form BHW
query = ''' 
SELECT * FROM Salepurchase1 s WHERE Vtyp not in ('SB') '''
salepur1_bhw= pd.read_sql(query, cnxn)
salepur1_bhw['warehouse'] = 'BHW'
salepur1_bhw['warehouseId'] = 199
logger.info("Data from BHW acquired: " +str(len(salepur1_bhw)))

#SP1 from GAW
query = ''' 
SELECT * FROM Salepurchase1 s WHERE Vtyp not in ('SB') '''
salepur1_ga= pd.read_sql(query, cnxn_ga)
salepur1_ga['warehouse'] = 'GA'
salepur1_ga['warehouseId'] = 343
logger.info("Data from GAW acquired: " +str(len(salepur1_ga)))

salepurchase1 = pd.concat([salepur1_bhw, salepur1_ga]).reset_index(drop= True)
salepurchase1[['SyncNo','StndVno','BillTocode']] = salepurchase1[['SyncNo','StndVno','BillTocode']]\
    .apply(pd.to_numeric, errors='ignore').astype('Int64')

salepurchase1.columns= salepurchase1.columns.str.lower()

# def main(rs_db, s3):
table_name = 'salepurchase1'
table_info = helper.get_table_info(db=rs_db, table_name=table_name, schema=schema)

# =========================================================================
# Writing table in Redshift
# =========================================================================
if isinstance(table_info, type(None)):
    raise Exception(f"table: {table_name} do not exist, create the table first")
else:
    print(f"Table:{table_name} exists")
truncate_query = f''' DELETE FROM "{schema}"."{table_name}" '''
rs_db.execute(truncate_query)
logger.info(f"Table:{table_name} table truncated")

s3.write_df_to_db(df=salepurchase1[table_info['column_name']], table_name=table_name, db=rs_db,
                      schema=schema)

logger.info(f"Table:{table_name} table uploaded")
salepurchase1.drop(salepurchase1.index, inplace=True)

# Fifo from bhiwandi
query = '''
SELECT * FROM FIFO f '''
fifo_bhw = pd.read_sql(query, cnxn)
fifo_bhw['warehouse'] = 'BHW'
fifo_bhw['warehouseId'] = 199
logger.info("FIFO Data from BHW acquired: " +str(len(fifo_bhw)))

#Fifo from GA warehouse
query = ''' 
SELECT * FROM FIFO f '''
fifo_ga = pd.read_sql(query, cnxn_ga)
fifo_ga['warehouse'] = 'GA'
fifo_ga['warehouseId'] = 343
logger.info("FIFO Data from GAW acquired: " +str(len(fifo_ga)))

fifo = pd.concat([fifo_bhw, fifo_ga]).reset_index(drop= True)

fifo[['ScmOfferNo','WUCode','PsrlnoGDNTrf','StockLocation','SyncNo']] \
    = fifo[['ScmOfferNo','WUCode','PsrlnoGDNTrf','StockLocation','SyncNo']]\
    .apply(pd.to_numeric, errors='ignore').astype('Int64')

fifo.columns = fifo.columns.str.lower()

logger.info("FIFO Data from both GA and BHW acquired: " +str(len(fifo)))

# def main(rs_db, s3):
table_name = 'fifo'
table_info = helper.get_table_info(db=rs_db, table_name=table_name, schema=schema)

# =========================================================================
# Writing table in Redshift
# =========================================================================
if isinstance(table_info, type(None)):
    raise Exception(f"table: {table_name} do not exist, create the table first")
else:
    print(f"Table:{table_name} exists")
truncate_query = f''' DELETE FROM "{schema}"."{table_name}" '''
rs_db.execute(truncate_query)
logger.info(f"Table:{table_name} table truncated")

s3.write_df_to_db(df=fifo[table_info['column_name']], table_name=table_name, db=rs_db,
                      schema=schema)

logger.info(f"Table:{table_name} table uploaded")
fifo.drop(fifo.index, inplace=True)

#acknow table from BHW and GAW
#acknow from BHW
query = ''' 
SELECT * FROM Acknow a '''
acknow_bhw= pd.read_sql(query, cnxn)
acknow_bhw['warehouse'] = 'BHW'
acknow_bhw['warehouseId'] = 199
logger.info("Acknow Data from BHW acquired: " +str(len(acknow_bhw)))

#acknow from GAW
query = ''' 
SELECT * FROM Acknow a '''
acknow_ga = pd.read_sql(query, cnxn_ga)
acknow_ga['warehouse'] = 'GA'
acknow_ga['warehouseId'] = 343
logger.info("Acknow Data from GAW acquired: " +str(len(acknow_ga)))

acknow = pd.concat([acknow_bhw, acknow_ga]).reset_index(drop= True)
logger.info("Acknow Data from after combining: " +str(len(acknow)))

acknow.columns = acknow.columns.str.lower()

# def main(rs_db, s3):
table_name = 'acknow'
table_info = helper.get_table_info(db=rs_db, table_name=table_name, schema=schema)

# =========================================================================
# Writing table in Redshift
# =========================================================================
if isinstance(table_info, type(None)):
    raise Exception(f"table: {table_name} do not exist, create the table first")
else:
    print(f"Table:{table_name} exists")
truncate_query = f''' DELETE FROM "{schema}"."{table_name}" '''
rs_db.execute(truncate_query)
logger.info(f"Table:{table_name} table truncated")

s3.write_df_to_db(df=acknow[table_info['column_name']], table_name=table_name, db=rs_db,
                      schema=schema)

logger.info(f"Table:{table_name} table uploaded")

acknow.drop(acknow.index, inplace=True)

# Getting item, master and acm from BHW warehouse
query = '''
select * from Item '''
item = pd.read_sql(query, cnxn)
item[['Saltcode','IucCode','SyncIdMod','SyncNo']] = item[['Saltcode','IucCode','SyncIdMod','SyncNo']]\
    .apply(pd.to_numeric, errors='ignore').astype('Int64')
item.columns = item.columns.str.lower()
logger.info("Item Data from BHW acquired: " +str(len(item)))

# def main(rs_db, s3):
table_name = 'item'
table_info = helper.get_table_info(db=rs_db, table_name=table_name, schema=schema)

# =========================================================================
# Writing table in Redshift
# =========================================================================
if isinstance(table_info, type(None)):
    raise Exception(f"table: {table_name} do not exist, create the table first")
else:
    print(f"Table:{table_name} exists")
truncate_query = f''' DELETE FROM "{schema}"."{table_name}" '''
rs_db.execute(truncate_query)
logger.info(f"Table:{table_name} table truncated")

s3.write_df_to_db(df=item[table_info['column_name']], table_name=table_name, db=rs_db,
                      schema=schema)

logger.info(f"Table:{table_name} table uploaded")
item.drop(item.index, inplace=True)

# ACM table
query = '''
select * from Acm '''
acm = pd.read_sql(query, cnxn)
acm[['BillToCode','SyncNo']] = acm[['BillToCode','SyncNo']].apply(pd.to_numeric, errors='ignore').astype('Int64')
acm.columns = acm.columns.str.lower()
logger.info("acm Data from BHW acquired: " +str(len(acm)))

# def main(rs_db, s3):
table_name = 'acm'
table_info = helper.get_table_info(db=rs_db, table_name=table_name, schema=schema)

# =========================================================================
# Writing table in Redshift
# =========================================================================
if isinstance(table_info, type(None)):
    raise Exception(f"table: {table_name} do not exist, create the table first")
else:
    print(f"Table:{table_name} exists")
truncate_query = f''' DELETE FROM "{schema}"."{table_name}" '''
rs_db.execute(truncate_query)
logger.info(f"Table:{table_name} table truncated")

s3.write_df_to_db(df=acm[table_info['column_name']], table_name=table_name, db=rs_db,
                      schema=schema)

logger.info(f"Table:{table_name} table uploaded")

# from Master table
query = '''
select * from Master '''
master = pd.read_sql(query, cnxn)
master[['SyncNo']] = master[['SyncNo']].apply(pd.to_numeric, errors='ignore').astype('Int64')
master.columns = master.columns.str.lower()

logger.info("master Data from BHW acquired: " +str(len(master)))

# def main(rs_db, s3):
table_name = 'master'
table_info = helper.get_table_info(db=rs_db, table_name=table_name, schema=schema)

# =========================================================================
# Writing table in Redshift
# =========================================================================
if isinstance(table_info, type(None)):
    raise Exception(f"table: {table_name} do not exist, create the table first")
else:
    print(f"Table:{table_name} exists")
truncate_query = f''' DELETE FROM "{schema}"."{table_name}" '''
rs_db.execute(truncate_query)
logger.info(f"Table:{table_name} table truncated")

s3.write_df_to_db(df=master[table_info['column_name']], table_name=table_name, db=rs_db,
                      schema=schema)
logger.info(f"Table:{table_name} table uploaded")


# closing the DB connection in the end
rs_db.close_connection()
mssql.close_connection()