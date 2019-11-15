# Created by Xinyu Zhu on 10/21/2019, 10:23 PM

import sys
import os

project_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(project_path)
from common.htm_docker_api import HTMApiProvider


def test_api():
    htm = HTMApiProvider(docker_path=project_path + "/../docker/htmDocker/")
    # Test basic API
    assert htm.recycle_detector() is True
    assert htm.set_max_detector_num(10) is True

    # create new detector with default parameters
    detector_key = htm.create_new_detector()  # keep the detector_key

    print(detector_key)
    result = []
    # the testing data is in this format [[timestamp, value], [timestamp, value], ...] sorted by timestamp
    testing_data = [[12, 1], [13, 2], [15, 7], [17, 9], [18, 4]]
    for record in testing_data:
        # pass the data record to the detector
        result.append(htm.pass_record_to_detector(detector_key, record[0],record[1]))
    print(result)

    ts = []
    vs = []
    for record in testing_data:
        ts.append(record[0])
        vs.append(record[1])
    # pass an array of data to the detector
    next_result = htm.pass_block_record_to_detector(detector_key, ts, vs)
    print(next_result)
    # these two result should not be equal although the input are the same
    # because the calculation of next_result is based on previous memory
    assert result != next_result


if __name__ == '__main__':
    test_api()
