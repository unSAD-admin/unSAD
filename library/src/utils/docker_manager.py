# Created by Xinyu Zhu on 10/4/2019, 10:35 PM

import docker


def init_docker_environment():
    client = docker.from_env()

    result = client.images.list()
    print(result)
    ##client.images.build(path="../../docker/htmDocker")


if __name__ == '__main__':
    init_docker_environment()
