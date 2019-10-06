# Created by Xinyu Zhu on 10/5/2019, 11:02 PM
from library.src.common.http_api_client import HttpApiClient
from library.src.utils.docker_manager_cmd import get_target_ip_address

ip = get_target_ip_address("../../../docker/htmDocker/")


print(ip)

client = HttpApiClient(ip_address=ip, port=8081)

result = client.call("recycle")

print(result)