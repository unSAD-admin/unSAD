# Created by Xinyu Zhu on 10/21/2019, 10:23 PM

import sys
import logging
import time

sys.path.append("../../")
from common.htm_docker_api import HTMApiProvider

if __name__ == '__main__':
    htm = HTMApiProvider(docker_path="../../../docker/htmDocker/")
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