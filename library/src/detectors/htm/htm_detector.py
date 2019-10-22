import sys

sys.path.append("../../")

from detectors.base import BaseDetector
from common.htm_docker_api import HTMApiProvider


class HTMAnomalyDetector(BaseDetector):

    def __init__(self, timestamp_col_name=None, value_col_name=None):
        if timestamp_col_name is None:  # since timestamp column name is essential for super class
            timestamp_col_name = "timestamp"

        super(HTMAnomalyDetector, self).__init__(timestamp_col_name=timestamp_col_name,
                                                 measure_col_names=[value_col_name], symbolic=False)

    def initialize(self, docker_path=None, lower_data_limit=-1e9, upper_data_limit=1e9, probation_number=750,
                   spatial_tolerance=0.05, *args, **kwargs):
        super(HTMAnomalyDetector, self).initialize(*args, **kwargs)

        # Create HTMApiProvider
        self.htm = HTMApiProvider(docker_path)

        self.htm.recycle_detector()

        if "max_detector_num" in kwargs:
            self.htm.set_max_detector_num(kwargs["max_detector_num"])

        # Create new detector with default parameters and keep the detector_key
        self.detector_key = self.htm.create_new_detector(lower_data_limit, upper_data_limit, probation_number,
                                                         spatial_tolerance)

    def handle_record(self, record):
        record = self._pre_process_record(record)
        if record is None:
            raise Exception("Data input does not match the input format")

        return self.htm.pass_record_to_detector(self.detector_key, record[0], record[1])

    def train(self, training_data):
        # creating lists for timestamp and values and filling them up from training data
        ts = []
        vs = []
        for list_element in training_data:
            list_element = self._pre_process_record(list_element)
            ts.append(list_element[0])
            vs.append(list_element[1])

        # pass an array of data to the detector
        return self.htm.pass_block_record_to_detector(self.detector_key, ts, vs)

    def visualize(self):
        pass


if __name__ == '__main__':
    htm = HTMAnomalyDetector("timestamp", "value")
    htm.initialize(docker_path="../../../docker/htmDocker/")
    # testing handle_record
    print("Testing handle_record()")
    for i in range(5):
        htm.handle_record([2 + i, 6 * i + 3])

    # testing train()
    print("Testing train()")
    for i in range(5):
        result = htm.train([[2 + i, 6 * i + 3], [5 - i, 5 * i + 1], [9 - i, i + 9]])
        print(result)
