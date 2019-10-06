# Created by Xinyu Zhu on 10/5/2019, 11:02 PM

import sys

sys.path.append("../../")

from docker_manager import init_docker_environment

from common.http_api_client import HttpApiClient
from utils.docker_manager_cmd import get_target_ip_address

try:
    ip = init_docker_environment("../../../docker/htmDocker/", tag="htm/htm:1.0")
    print("Got ip address:", ip, "from python docker API")
except RuntimeError:
    ip = get_target_ip_address("../../../docker/htmDocker/", tag="htm/htm:1.0")
    print("Got ip address:", ip, "from command line")

print(ip)

client = HttpApiClient(ip_address=ip, port=8081)

result = client.call("recycle")

print(result)
