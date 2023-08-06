import argparse
import sys
import os

sys.path.append('../../../..')

from zeno_etl_libs.logger import get_logger
from zeno_etl_libs.helper.aws.redshift import Redshift

parser = argparse.ArgumentParser(description="This is ETL script.")
parser.add_argument('-e', '--env', default="dev", type=str, required=False,
                    help="This is env(dev, stage, prod)")
args, unknown = parser.parse_known_args()
env = args.env
os.environ['env'] = env
logger = get_logger()

logger.info(f"env: {env}")

""" redshift class """
rs = Redshift()

logger.info(f"started: cluster_identifier: {rs.cluster_identifier}")
response = rs.create_manual_snapshot()

logger.info(f"ended, response: {response}")
