# Created by Xinyu Zhu on 10/6/2019, 1:42 AM

import sys
import json

sys.path.append("../")
from common.http_api_client import HttpApiClient
from utils.docker_manager import init_docker_environment

"""
Due to some reason, the docker may not be able to start itself on some environment like windows.
You can just use the following commands to start it manually from the Dockerfile directory

docker build -t htm/htm:1.0 .
-> get image id  91bf6cb14f72, [you will see a line: Successfully built 91bf6cb14f72]
docker run -p 127.0.0.1:8081:8081 -it 91bf6cb14f72
python /home/htmHome/detector_service_provider.py

"""


class HTMApiProvider:

    def __init__(self, docker_path, docker_ip=None, port=8081, tag="htm/htm:1.0"):
        """
        There should be only one Api Provider running on one port, please maintain a single instance
        For this class
        :param port: Should be the port exposed by the docker server
        :param docker_path: Should be the path to the fold which contains the Dockerfile
        :param tag: the tag you would like to assign to the docker image
        """
        if docker_path is not None:
            ip = None
            try:
                ip = init_docker_environment(docker_path, tag=tag)
                ip = "127.0.0.1"
                print("Got ip address:", ip, "from python docker API")
            except Exception:
                ip = "127.0.0.1"
                self.ip = ip
                self.port = port
                self.api_client = HttpApiClient(ip_address=self.ip, port=self.port)
                print("Testing whether the docker is set up")
                if not self.health_check():
                    ip = None
            if ip is None:
                raise Exception("Ooops! Something goes wrong which the docker environment! Don't worry"
                                   "This is a step by step instruction for you to make it work."
                                   "1. Make sure docker is installed in your environment correctly. Open a "
                                   "command line tools and type in docker, you should be able to see some response"
                                   "2. Maker sure you pass in a correct docker_path, a Dockerfile should be"
                                   "under docker_path, if you are using relative path, make sure it is correct"
                                   "3. Ok, there may be some trouble with your environment, for example the "
                                   "python docker library is not compatible with your Windows 10. You can start"
                                   "the docker manually. (Actually, we prefer you to do that) "
                                   "Go to the docker_path and open a command line interface:"
                                   "key in the following command to build you docker image: "
                                   "docker build -t htm/htm:1.0 ."
                                   "You will see something like: Successfully built 91bf6cb14f72 near the end"
                                   "the 91bf6cb14f72 can be different, it is the image id. Keep that id and type"
                                   "docker run -p 127.0.0.1:8081:8081 -it [91bf6cb14f72]"
                                   "this will start you docker instance. And you will be inside the docker "
                                   "environment automatically. Now start the server program inside the docker:"
                                   "nohup python /home/htmHome/detector_service_provider.py"
                                   "If you see something like: Running on http://0.0.0.0:8081/ (Press CTRL+C to quit)"
                                   "You are done, maintain the command line session there, don't close it and "
                                   "rerun this program, it should work."
                                   "4. If there is still problem. It seems that you encounter some unknown case."
                                   "Maybe you can try other detectors which do not need a docker.")

            self.ip = ip
            self.port = port
            self.api_client = HttpApiClient(ip_address=self.ip, port=self.port)

        else:
            if docker_ip is not None or docker_ip == "":
                print("User didn't provide a docker path, assume the ip address is provided")
                self.ip = docker_ip
                self.port = port
                self.api_client = HttpApiClient(ip_address=self.ip, port=self.port)
            else:
                raise Exception(
                    "Please either provide an docker path for the program to initialize the docker "
                    "environment or set up an accessible docker environment and provide"
                    " an ip address(for example: 127.0.0.1) to the APIs")

    def health_check(self):
        result = self.api_client.call(path="health_check")
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
    detector_key = htm.create_new_detector()  # keep the detector_key

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
