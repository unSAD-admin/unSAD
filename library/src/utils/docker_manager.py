# Created by Xinyu Zhu on 10/4/2019, 10:35 PM

import docker
import time

from utils.annotations import simple_thread


@simple_thread
def build_image(path, tag):
    client = docker.from_env()
    image = client.images.build(path=path, tag=tag)[0]

    # start the docker server
    client.containers.run(image, "python /home/htmHome/detector_service_provider.py",
                          ports={"8081/tcp": ('127.0.0.1', 8081)})

    # the session will maintain


def get_ip_address(container_id):
    return docker.APIClient().inspect_container(container_id)['NetworkSettings']['Networks']['bridge']['IPAddress']


def query_container_id(client):
    container_list = client.containers.list()
    result = []
    for container in container_list:
        result.append(container.id)
    return result


def init_docker_environment(path, tag="htm/htm:1.0", timeout=600):
    client = docker.from_env()
    if len(query_container_id(client)) != 0:
        return get_ip_address(query_container_id(client)[0])
    build_image(path, tag)
    while len(query_container_id(client)) == 0:
        time.sleep(1)
        timeout -= 1
        if timeout < 0:
            raise Exception("Docker launch failed!")

    ip_address = get_ip_address(query_container_id(client)[0])
    return ip_address


if __name__ == '__main__':
    print(init_docker_environment(path="../../docker/htmDocker"))
