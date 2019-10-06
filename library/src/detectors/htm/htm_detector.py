import sys

sys.path.append("../../")

import time
from detectors.base import BaseDetector
from collections import defaultdict
from common.htm_docker_api import HTMApiProvider

from utils.collection_tools import normalize


class HTMAnomalyDetector(BaseDetector):

    def __init__(self, timestamp_col_name=None, value_col_name=None):
        if timestamp_col_name is None:
            timestamp_col_name = "Timestamp"

        super(HTMAnomalyDetector, self).__init__(timestamp_col_name=timestamp_col_name,
                                                               measure_col_names=[value_col_name], symbolic=False)

    def initialize(self, docker_path, *args, **kwargs):
        super(HTMAnomalyDetector, self).initialize(*args, **kwargs)

        # Create htmAPIprovider
        self.htm = HTMApiProvider(docker_path)

        # Create new detector with default parameters
        self.detector_key = self.htm.create_new_detector() # keep the detector_key



    def handle_record(self, record):
        record = self._pre_process_record(record)
        if record is None:
            raise RuntimeError("Data input does not match the input format")


        result = (self.htm.pass_record_to_detector(self.detector_key, record[0], record[1]))  # (key,timestamp,value)

        return result


        # TODO: record will contain a list of values [timestamp, value] after pre_processing
        # TODO: PASS RECORD TO HTMApiProvider (htm_docker_api class) object, and return result to user

        # next_candidate = self._predict()
        # result = 0
        # if record in next_candidate:
        #     result = next_candidate[record]
        # self.buffer.append(record)
        # while len(self.buffer) > self.window_size:
        #     self.buffer.pop(0)
        # self._count_subsequence(self.buffer)
        return result

    def train(self, training_data):
        # for record in training_data:
        #     self.handle_record(record)
        ts = []
        vs = []
        for list_element in training_data:
            list_element = self._pre_process_record(list_element)
            ts.append(list_element[0])
            vs.append(list_element[1])

        # pass an array of data to the detector
        result = self.htm.pass_block_record_to_detector(self.detector_key, ts, vs)
        return result

if __name__ == '__main__':
    htm = HTMAnomalyDetector("timestamp", "value")
    htm.initialize(docker_path="../../../docker/htmDocker/")
    for i in range(5):
        htm.handle_record([2+i,6*i+3])

#     htm = HTMApiProvider(docker_path="../../../docker/htmDocker/")
#     # Test basic API
#     print(htm.recycle_detector())
#     print(htm.set_max_detector_num(10))
#
#     # create new detector with default parameters
#     detector_key = htm.create_new_detector() # keep the detector_key
#
#
#     sample_list = [[123,5],[342,6]] # inner list is [timestamp,value]
#
#     print(detector_key)
#     result = []
#     now = time.time()
#     for list_element in sample_list:
#         # pass the data record to the detector
#         result.append(htm.pass_record_to_detector(detector_key, list_element[0], list_element[1])) # (key,timestamp,value)
#     t = time.time() - now
#     print(result)
#     print(t)
#
#     ts = []
#     vs = []
#     for list_element in sample_list:
#         ts.append(list_element[0])
#         vs.append(list_element[1])
#     now = time.time()
#     # pass an array of data to the detector
#     result = htm.pass_block_record_to_detector(detector_key, ts, vs)
#     t = time.time() - now
#
#     for r in result:
#         print(r)
#     print(result)
#     print(t)
