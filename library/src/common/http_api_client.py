# Created by Xinyu Zhu on 10/5/2019, 11:04 PM
import requests


class HttpApiClient:
    def __init__(self, ip_address, port=8080):
        self.ip = ip_address
        self.port = str(port)

    def call(self, path, params=[]):
        assert isinstance(params, list)
        url = "http://" + self.ip + ":" + self.port + "/" + path
        if len(params) != 0:
            for param in params:
                url += "/" + str(params)
        print(url)
        r = requests.get(url)
        return r.text
