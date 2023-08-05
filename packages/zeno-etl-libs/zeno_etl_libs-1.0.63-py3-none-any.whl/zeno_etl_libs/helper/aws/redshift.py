import boto3
import datetime

from dateutil.tz import tzutc
from zeno_etl_libs.config.common import Config


class Redshift:
    def __init__(self):
        configobj = Config.get_instance()
        self.secrets = configobj.get_secrets()
        self.client = boto3.client('redshift')
        self.cluster_identifier = self.secrets["CLUSTER_IDENTIFIER"]
        self.database_name = self.secrets["REDSHIFT_WRITE_DB"]

    def get_snapshot_identifier(self, snapshot_type='automated', utc_date: str = None) -> str:
        """
        :param snapshot_type: 'automated' | 'manual'
        :param utc_date: format "%Y-%m-%d"

        Returns:
                Automated snapshot identifier of given utc_date, if utc_date is not given then latest snapshot
        """
        end_time = datetime.datetime.strptime(utc_date, "%Y-%m-%d") if utc_date else datetime.datetime.now(tz=tzutc())
        end_time = end_time.replace(hour=23, minute=59, second=59)
        # utc_date = str(end_time.date())
        """ last 1 year """
        start_time = end_time - datetime.timedelta(days=365)

        response = self.client.describe_cluster_snapshots(
            ClusterIdentifier=self.cluster_identifier,
            SnapshotType=snapshot_type,
            StartTime=start_time,
            EndTime=end_time,
            MaxRecords=100,
            ClusterExists=True,
            SortingEntities=[
                {
                    'Attribute': 'CREATE_TIME',
                    'SortOrder': 'DESC'
                },
            ]
        )
        for snap in response['Snapshots']:
            print(snap['SnapshotIdentifier'])
            if not utc_date:
                return snap['SnapshotIdentifier']
            else:
                if utc_date in snap['SnapshotIdentifier']:
                    return snap['SnapshotIdentifier']

        return ""

    def create_manual_snapshot(self):
        """
        resource to read:
        1. https://n2ws.com/blog/aws-automation/3-reasons-to-automate-your-manual-redshift-snapshots
        2. https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/redshift.html#Redshift.Client.create_cluster_snapshot
        3. https://aws.amazon.com/redshift/pricing/
        """

        # Keeping the minutes and seconds constant
        time_now = datetime.datetime.now(tz=tzutc()).strftime('%Y-%m-%d-%H-00-00')
        snapshot_identifier = f"{self.cluster_identifier}-{time_now}"

        print(f"snapshot_identifier: {snapshot_identifier}")
        print("MANUAL_SNAPSHOT_RETENTION_PERIOD type: ", type(int(self.secrets["MANUAL_SNAPSHOT_RETENTION_PERIOD"])))
        # TODO: take MANUAL_SNAPSHOT_RETENTION_PERIOD period from secrets(type int needed str was coming, so fix it)
        response = self.client.create_cluster_snapshot(
            SnapshotIdentifier=snapshot_identifier,
            ClusterIdentifier=self.cluster_identifier,
            ManualSnapshotRetentionPeriod=int(self.secrets["MANUAL_SNAPSHOT_RETENTION_PERIOD"]),
            Tags=[
                {
                    'Key': 'backup_type',
                    'Value': 'monthly'
                },
            ]
        )
        return response
