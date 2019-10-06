# Created by Xinyu Zhu on 10/6/2019, 1:42 AM

import sys
import json

sys.path.append("../")
from common.http_api_client import HttpApiClient
from utils.docker_manager import init_docker_environment
from utils.docker_manager_cmd import get_target_ip_address


class HTMApiProvider:

    def __init__(self, docker_path, port=8081, tag="htm/htm:1.0"):
        """
        There should be only one Api Provider running on one port, please maintain a single instance
        For this class
        :param port: Should be the port exposed by the docker server
        :param docker_path: Should be the path to the fold which contains the Dockerfile
        :param tag: the tag you would like to assign to the docker image
        """
        ip = None
        try:
            ip = init_docker_environment(docker_path, tag=tag)
            print("Got ip address:", ip, "from python docker API")
        except RuntimeError:
            try:
                ip = get_target_ip_address(docker_path, tag=tag)
                print("Got ip address:", ip, "from command line")
            except RuntimeError:
                pass
        if ip is None:
            raise RuntimeError("Docker is not set up correctly on your environment. "
                               "Please make sure docker command is accessible")

        self.ip = ip
        self.port = port
        self.api_client = HttpApiClient(ip_address=self.ip, port=self.port)

    def set_max_detector_num(self, num=10):
        """
        You need to set the maximum detector number supported by the docker server
        The server can only maintain a certain number of detector at the same time
        to serve different client. Each detector has its own memory and should be used by
        one anomaly detection task. The default number is 10. If more detectors are created
        than the maximum number, old detectors will be recycled.
        """
        result = self.api_client.call(path="set_max", params=[num])
        if result == "success":
            return True
        else:
            return False

    def create_new_detector(self, lower_data_limit=-1e9, upper_data_limit=1e9, probation_number=750,
                            spatial_tolerance=0.05):
        """
        This API will ask the server to create a new detector based on the input parameter.
        A detector key will be returned for you. Since the server can keep multiple detector at
        the same time, you need to pass the key to the server to indicate which detector you want
        to use
        """
        result = self.api_client.call("new_detector",
                                      [lower_data_limit, upper_data_limit, probation_number, spatial_tolerance])
        return result

    def pass_record_to_detector(self, key, timestamp, value):
        """
        pass your record to the detector and get a result in json format
        The HTM detector is recognized by the key, which is the key returned by create_new_detector
        Since the HTM detector takes in two parameter: timestamp and value, you need to provide
        these two values.
        """
        result = self.api_client.call("handle", [key, timestamp, value])
        if result is not None:
            result = result.split(",")
            return {
                "anomalyScore": float(result[0]),
                "rawScore": float(result[1])
            }
        return None

    def pass_block_record_to_detector(self, key, timestamps, values):
        """
        In order to reduce the number of http request to make it more efficient
        This method is provided to pass a block of data to the server at one run
        the timestamps and values are two array of data.
        """
        data = {
            "timestamps": timestamps,
            "values": values
        }
        rt = []
        result = self.api_client.call_with_data("handle_block", [key], data)
        result = json.loads(result)["result"]
        for record in result:
            record = record.split(",")
            rt.append({
                "anomalyScore": float(record[0]),
                "rawScore": float(record[1])
            })
        return rt

    def recycle_detector(self):
        """
        delete all the detectors
        """
        result = self.api_client.call("recycle", [])
        if result == "success":
            return True
        else:
            return False


"""
The following code are example about how to use this htm docker api to train
"""

import time

if __name__ == '__main__':
    htm = HTMApiProvider(docker_path="../../docker/htmDocker/")
    # Test basic API
    print(htm.recycle_detector())
    print(htm.set_max_detector_num(10))

    # create new detector with default parameters
    detector_key = htm.create_new_detector() # keep the detector_key


    print(detector_key)
    result = []
    now = time.time()
    for i in range(4):
        # pass the data record to the detector
        result.append(htm.pass_record_to_detector(detector_key, i + 1, 0.12 + i * 2))
    t = time.time() - now
    print(result)
    print(t)

    ts = []
    vs = []
    for i in range(4, 400):
        ts.append(i + 1)
        vs.append(0.12 + i * 2)
    now = time.time()
    # pass an array of data to the detector
    result = htm.pass_block_record_to_detector(detector_key, ts, vs)
    t = time.time() - now

    for r in result:
        print(r)
    print(result)
    print(t)
