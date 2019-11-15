# Created by Xinyu Zhu on 10/5/2019, 11:04 PM
import requests
import json


class HttpApiClient:
    """
    This is a class used to communicate with Flask server running on docker
    """

    def __init__(self, ip_address, port=8081):
        self.ip = ip_address
        self.port = str(port)

    def call(self, path, params=[]):
        """
        Send a Http Get request to call a certain function on the server
        :param path: the function path of the url
        :param params: the parameters of the function
        :return: result of the function call in plain text
        """
        url = "http://{ip}:{port}/{path}".format(ip=self.ip, port=self.port, path=path)
        if len(params) != 0:
            for param in params:
                url += "/" + str(param)
        r = requests.get(url)
        return r.text

    def call_with_data(self, path, params=[], data={}):
        """
        Send a Http Post request to call a certain function on the server
        :param path: the function path of the url
        :param params: the parameters of the function
        :param data: the post data
        :return: result of the function call in plain text
        """
        url = "http://{ip}:{port}/{path}".format(ip=self.ip, port=self.port, path=path)
        if len(params) != 0:
            for param in params:
                url += "/" + str(param)

        r = requests.post(url, data=json.dumps(data),
                          headers={'Content-Type': 'application/json', 'Accept': 'application/json'})

        return r.text
