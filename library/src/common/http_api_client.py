# Created by Xinyu Zhu on 10/5/2019, 11:04 PM
import requests
import json

class HttpApiClient:
    def __init__(self, ip_address, port=8080):
        self.ip = ip_address
        self.port = str(port)

    def call(self, path, params=[]):
        assert isinstance(params, list)
        url = "http://" + self.ip + ":" + self.port + "/" + path
        if len(params) != 0:
            for param in params:
                url += "/" + str(param)
        r = requests.get(url)
        return r.text

    def call_with_data(self, path, params=[], data={}, method="get"):
        assert isinstance(params, list)
        assert isinstance(data, dict)
        url = "http://" + self.ip + ":" + self.port + "/" + path
        if len(params) != 0:
            for param in params:
                url += "/" + str(param)
        if method.lower() == "get":
            r = requests.get(url, params=data)
        else:
            r = requests.post(url, data=json.dumps(data))
        return r.text
