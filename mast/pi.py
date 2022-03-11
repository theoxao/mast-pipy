import json
from flask import current_app

import requests

pi_host = "http://172.29.236.153:8000/api"

headers = {'content-type': 'application/json'}


def update_state(position, value, detect):
    res = requests.post(pi_host + "/update_state",
                        data=json.dumps({"position": position, "value": value, "detect": detect}), headers=headers)
    return json.loads(res.text).get("data")


def query_state(detect):
    res = requests.post(pi_host + "/query_state", data=json.dumps({"detect": detect}), headers=headers)
    return json.loads(res.text).get("data")
