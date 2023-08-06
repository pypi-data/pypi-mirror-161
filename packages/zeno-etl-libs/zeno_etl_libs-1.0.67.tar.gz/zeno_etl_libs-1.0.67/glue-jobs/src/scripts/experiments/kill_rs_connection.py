import argparse
import os
import sys
from zeno_etl_libs.db.db import DB

sys.path.append('../../../..')

from zeno_etl_libs.logger import get_logger

parser = argparse.ArgumentParser(description="This is ETL script.")
parser.add_argument('-e', '--env', default="dev", type=str, required=False,
                    help="This is env(dev, stage, prod)")
parser.add_argument('-ul', '--user_list', default="", type=str, required=False,
                    help="This is env(dev, stage, prod)")

args, unknown = parser.parse_known_args()
env = args.env
user_list = args.user_list or ""
os.environ['env'] = env
user_list = user_list.split(",")

rs_db = DB()
rs_db.open_connection()
logger = get_logger()


def get_pids(user=""):
    query = f"""
    select
        s.process as process_id,
        c.remotehost || ':' || c.remoteport as remote_address,
        s.user_name as username,
        s.starttime as session_start_time,
        s.db_name,
        i.starttime as current_query_time,
        i.text as query
    from
        stv_sessions s
    left join pg_user u on
        u.usename = s.user_name
    left join stl_connection_log c
              on
        c.pid = s.process
        and c.event = 'authenticated'
    left join stv_inflight i 
              on
        u.usesysid = i.userid
        and s.process = i.pid
    where
        username = '{user}'
    order by
        session_start_time desc;
    """
    df = rs_db.get_df(query=query)
    return df


def kill_connection(pid):
    query = f"""
        select pg_terminate_backend({pid});
    """
    rs_db.execute(query=query)


for user in user_list:
    pids_df = get_pids(user=user)
    """ extra filter to be 100% sure """
    pids_df['username'] = pids_df['username'].apply(lambda x: x.strip())
    pids_df1 = pids_df[pids_df['username'].isin(["ro_django_accounts"])]
    for pid in pids_df1['process_id']:
        kill_connection(pid=pid)
        logger.info(f"Killed, pid: {pid}")

rs_db.close_connection()

logger.info(f"info message")
