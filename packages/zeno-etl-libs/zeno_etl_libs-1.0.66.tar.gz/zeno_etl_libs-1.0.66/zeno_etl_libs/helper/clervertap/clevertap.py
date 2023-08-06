import json

import requests

from zeno_etl_libs.config.common import Config
from zeno_etl_libs.logger import get_logger


class CleverTap:
    """
    class: is used to fetch the data from CleverTap using API calls
    """

    def __init__(self, api_name=None, event_name=None, batch_size=None, from_date=None, to_date=None, query=None):
        """
        :params account_id: CleverTap Account ID
        :params passcode: CleverTap passcode
        :params api_name: CleverTap api name to fetch the different type of  data eg: "profiles.json"
        :params batch_size: no of records to be fetched per batch
        :params from_date: start date filter, YYYYMMDD
        :params to_date: end date filter, YYYYMMDD
        :params query:
        """
        self.logger = get_logger()

        configobj = Config.get_instance()
        secrets = configobj.get_secrets()

        account_id = secrets['CLEVERTAP_ACCOUNT_ID']
        passcode = secrets['CLEVERTAP_PASSCODE']
        self.uri = "api.clevertap.com"
        self.account_id = account_id if account_id else "TEST-K5Z-K95-RZ6Z"
        self.passcode = passcode if passcode else 'd1d2cc1f8624434dbb3038b77d3fcf9d'
        self.api_name = api_name if api_name else "profiles.json"
        self.event_name = event_name if event_name else "App Launched"
        self.batch_size = batch_size if batch_size else 5
        self.from_date = from_date if from_date else 20220101
        self.to_date = to_date if to_date else 20220101
        self.cursor = None
        self.all_records = list()
        self.query = query or {
            "event_name": self.event_name,
            "from": self.from_date,
            "to": self.to_date
        }

        self.headers = {
            'X-CleverTap-Account-Id': self.account_id,
            'X-CleverTap-Passcode': self.passcode,
            'Content-Type': 'application/json'
        }
        self.logger.info(f"account_id: {account_id}, api_name: {api_name}, event_name:{event_name}")

    def set_cursor(self):
        url = f"https://{self.uri}/1/{self.api_name}?batch_size={self.batch_size}"
        response = requests.request("POST", url, headers=self.headers, data=json.dumps(self.query))
        if response.status_code == 200:
            self.cursor = response.json()['cursor']
            self.logger.info("Cursor set successfully!")
            return self.cursor
        else:
            raise Exception(f"CleverTap cursor getting failed: {str(response.text)}")

    def get_profile_data_batch(self):
        url = f"https://{self.uri}/1/{self.api_name}?cursor={self.cursor}"
        response = requests.request("GET", url, headers=self.headers, data="")
        if response.status_code == 200:
            data = response.json()

            """ it will be set to None if all records fetched """
            self.cursor = data.get("next_cursor")

            """ adding batch records to all records list """
            self.all_records += data['records']
            self.logger.info(f"Batch records fetched successfully, count: {len(data['records'])}")
            # self.logger.info(f"Batch records: {data['records']}")
            return data['records']
        else:
            raise Exception(f"CleverTap profile_data getting failed: {str(response.text)}")

    def get_profile_data_all_records(self):
        self.set_cursor()
        while self.cursor:
            self.get_profile_data_batch()

    def create_target(self):
        """
        eg. query:
        {"name": "My Sms API campaign", "estimate_only": True, "target_mode": "sms",
         "where": {"event_name": "Charged", "from": 20171001, "to": 20171220, "common_profile_properties": {
             "profile_fields": [{"name": "Customer Type", "operator": "equals", "value": "Platinum"}]}},
         "respect_frequency_caps": True, "content": {"body": "Sms body"}, "when": "now"}
        """

        response = requests.post(f'https://in1.{self.uri}/1/targets/{self.api_name}', headers=self.headers,
                                 data=json.dumps(self.query))
        if 200 <= response.status_code <= 299:
            res = response.text
            self.logger.info(f"create target successful, status code:{response.status_code} text: {res}")
            return res
        else:
            raise Exception(f"create target failed, status code:{response.status_code} text: {response.text}")
