import json
from flask import current_app

import requests

pi_host = "http://172.29.236.153:8000/api"


def update_state(position, value, detect):
    headers = {'content-type': 'application/json'}
    res = requests.post(pi_host + "/update_state",
                        data=json.dumps({"position": position, "value": value, "detect": detect}), headers=headers)
    return json.loads(res.text).get("data")


def query_state(position):
    res = requests.post(pi_host + "/query_state", data=json.dumps({"position": position}))
    return json.loads(res.text).get("data")
