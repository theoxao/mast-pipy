import json

import requests

pi_host = "http://172.29.236.153:8000/api"


def update_state(position, value):
    return requests.post(pi_host + "/update_state", data=json.dumps({"position": position, "value": value}))


def query_state(position):
    return requests.post(pi_host + "/query_state", data=json.dumps({"position": position}))
