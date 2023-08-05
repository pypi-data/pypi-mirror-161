import requests
import json

from zeno_etl_libs.config.common import Config


class Websocket:
    def __init__(self):
        configobj = Config.get_instance()
        secrets = configobj.get_secrets()
        self.token = secrets["ZENO_WEBSOC_API_TOKEN"]
        self.url = secrets["ZENO_WEBSOC_BASE_URL"]

    def send(self, payload):
        """
        payload : {
            "destinations": [
                36
            ],
            "message": "cluster-request",
            "payload": "112234-82"
        }
        """

        payload = json.dumps(payload)
        headers = {
            'token': self.token,
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", f"{self.url}/send", headers=headers, data=payload)

        if response.status_code == 200:
            return response
        raise Exception(f"websocket send API failed : {response}")
