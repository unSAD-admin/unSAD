# Created by Xinyu Zhu on 10/6/2019, 1:42 AM

import sys
import json
import logging

sys.path.append("../")
from common.http_api_client import HttpApiClient
from common.unsad_exceptions import UnSADException
from utils.docker_manager import init_docker_environment

"""
Due to some reason, the docker may not be able to start itself on some environment like windows.
You can just use the following commands to start it manually from the Dockerfile directory

docker build -t htm/htm:1.0 .
-> get image id [image id], you will see a line: Successfully built [image id]
docker run -p 127.0.0.1:8081:8081 -it [image id],
python /home/htmHome/detector_service_provider.py

"""


class HTMApiProvider:
    """
    This class is the Api provider used by HTM detector
    """

    def __init__(self, docker_path=None, docker_ip=None, port=8081, tag="htm/htm:1.0"):

        if docker_ip is not None:
            self.ip = docker_ip
            self.port = port
            self.api_client = HttpApiClient(ip_address=self.ip, port=self.port)
            if not self.health_check():
                logging.warning("The provided ip address:" + docker_ip + " is not accessible")
                self.ip = None
                self.port = None
                self.api_client = None
            else:
                return
        elif docker_path is not None:
            try:
                self.ip = init_docker_environment(docker_path, tag=tag)
                self.port = port
                self.api_client = HttpApiClient(ip_address=self.ip, port=self.port)
                if not self.health_check():
                    logging.warning("The provided docker path:" + docker_path + " is not usable")
                else:
                    return
            except Exception as e:
                logging.warning(
                    "Can't create docker environment from the provided docker path: {path}, Exception: {error}".format(
                        path=docker_path, error=e))

        # if the above doesn't work, try to access 127.0.0.1
        self.ip = "127.0.0.1"
        self.port = port
        self.api_client = HttpApiClient(ip_address=self.ip, port=self.port)
        if not self.health_check():
            # raise exception if can't find any usable docker environment
            raise UnSADException.docker_exception()

    def health_check(self):
        try:
            result = self.api_client.call(path="health_check")
        except:
            return False
        return result == "success"

    def set_max_detector_num(self, num=100):
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
        return self.api_client.call("new_detector",
                                    [lower_data_limit, upper_data_limit, probation_number, spatial_tolerance])

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
