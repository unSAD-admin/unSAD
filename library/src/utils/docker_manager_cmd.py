# Created by Xinyu Zhu on 10/5/2019, 9:48 PM

import subprocess
import time

from utils.annotations import simple_thread

target_ip_address = None


def run_cmd(command):
    popen = subprocess.Popen(command.split(), stdout=subprocess.PIPE, universal_newlines=True)

    for stdout_line in iter(popen.stdout.readline, ""):
        yield stdout_line
    popen.stdout.close()
    return_code = popen.wait()
    if return_code:
        raise subprocess.CalledProcessError(return_code, command)


@simple_thread
def build_image(docker_directory="../../docker/htmDocker/", tag="htm/htm:1.0"):
    print("building image start")
    for line in run_cmd("docker build -t " + tag + " " + docker_directory):
        print(line)
        # yield line
        if "http://0.0.0.0" in line:
            query_ip_address()


def query_ip_address():
    global target_ip_address
    result = list(run_cmd("docker container ls"))
    container_id = result[1].split()[0]
    result = list(run_cmd('docker inspect -f "{{.NetworkSettings.IPAddress}}" ' + container_id))[0]
    target_ip_address = result[1:-2]
    print(target_ip_address)


def get_target_ip_address(docker_directory="../../docker/htmDocker/", tag="htm/htm:1.0", max_time_out=600):
    global target_ip_address
    target_ip_address = None
    build_image(docker_directory, tag)
    print("waiting")

    while target_ip_address is None:
        time.sleep(1)
        max_time_out -= 1
        if max_time_out < 0:
            raise RuntimeError("Docker launch failed!")
    return target_ip_address


if __name__ == '__main__':
    print("ip:", get_target_ip_address())
