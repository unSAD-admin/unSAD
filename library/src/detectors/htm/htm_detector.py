import sys

sys.path.append("../../")

from detectors.base import BaseDetector
from collections import defaultdict

from utils.collection_tools import normalize


class SequentialPatternAnomalyDetector(BaseDetector):

    def __init__(self, measure_col_names=None):
        # super(SequentialPatternAnomalyDetector, self).__init__(timestamp_col_name=None,
        #                                                        measure_col_names=measure_col_names, symbolic=True)
        super(SequentialPatternAnomalyDetector, self).__init__(timestamp_col_name="Timestamp",
                                                               measure_col_names="List", symbolic=False)
    #     overwrite, pass diff params to default: "Timestamp","list",false

    def initialize(self, window_size=60, reduce_factor=2, *args, **kwargs):
        super(SequentialPatternAnomalyDetector, self).initialize(*args, **kwargs)

        # the window size: the detector use prefix patterns with length <= window size to predict next symbol
        self.window_size = window_size

        # for pattern rule counting, ("a","b","c") -> 2 means given the current prefix "a","b", there are 2 times that
        # the next symbol is "c"
        self.counter = {}

        # with the length of the prefix decrease by 1, the weight decrease by a factor
        self.reduce_factor = reduce_factor

        # data structure used to keep previous symbols
        self.buffer = []

    def _count_subsequence(self, input):
        """
        input is a list of symbol with length <= window_size + 1
        window_size == 3: ["a","b","c","d"] =>
         "a","b","c" -> "d" --> ("a","b","c","d") += 1 --> ("a","b","c") -> {"d":1}
         "b","c" -> "d"  --> (b","c","d") += 1 -->  ("b","c") -> {"d":1}
         "c" -> "d"  --> ("c","d") += 1 -->  ("c") -> {"d":1}
        """
        for i in range(len(input) - 2, -1, -1):
            if len(input) - i > self.window_size + 1:
                break
            pattern = tuple(input[i:-1])
            if pattern not in self.counter:
                self.counter[pattern] = defaultdict(int)
            self.counter[pattern][input[-1]] += 1

    def _predict(self):
        if len(self.buffer) > self.window_size:
            self.buffer = self.buffer[-self.window_size:]

        current_weight = 1
        result = defaultdict(int)

        for index in range(-1, -self.window_size - 1, -1):
            base_tuple = tuple(self.buffer[index:])
            if base_tuple not in self.counter:
                break
            else:
                for key in self.counter[base_tuple]:
                    result[key] += self.counter[base_tuple][key] * current_weight
                current_weight *= self.reduce_factor

        return normalize(result)

    def handle_record(self, record):
        record = self._pre_process_record(record)
        if record is None:
            raise RuntimeError("Data input does not match the input format")
        # record will contain a list of values [timestamp, value] after pre_processing
        #  PASS RECORD TO HTMApiProvider (htm_docker_api class) object, and return result to user
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
        for record in training_data:
            self.handle_record(record)