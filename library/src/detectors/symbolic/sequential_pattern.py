#!/usr/bin/python
# -*- coding: utf-8 -*-
# Created by Xinyu Zhu on 10/3/2019, 1:33 AM

import sys

sys.path.append('../../')
from detectors.base import BaseDetector
from utils.collection_tools import normalize

from collections import defaultdict


class SequentialPatternAnomalyDetector(BaseDetector):
    """
    This detector is designed for detecting low frequency patterns in symbolic sequence
    The detector is based on pattern based prediction, given the first n symbols, the detector
    will predict a list of possible next symbol as well as a probability distribution over
    them based on previous observation. An anomaly score will be given after the detector
    receive the next symbol.

    There are two hyper-parameters for this model:
    window_size (int): how many previous symbol will the detector used at most to predict the next symbol
    reduce_factor (float): The prediction is based on a weighted schema, if both of the following patterns
    are presented : (a,b) -> c, (b) -> d. The longer pattern (first one) will be assign more weight when
    doing prediction according to the reduce_factor, if reduce_factor == 2, the weight will be 2 times
    larger.
    """

    def __init__(self, measure_col_names=None):
        super(SequentialPatternAnomalyDetector,
              self).__init__(timestamp_col_name=None,
                             measure_col_names=measure_col_names,
                             symbolic=True)

    def initialize(
            self,
            window_size=60,
            reduce_factor=2,
            *args,
            **kwargs
    ):

        super(SequentialPatternAnomalyDetector, self).initialize(*args,
                                                                 **kwargs)

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
                    result[key] += self.counter[base_tuple][key] \
                                   * current_weight
                current_weight *= self.reduce_factor

        return normalize(result)

    @BaseDetector.require_initialize
    def handle_record(self, record):
        record = self._pre_process_record(record)
        next_candidate = self._predict()
        result = 0
        if record in next_candidate:
            result = next_candidate[record]
        self.buffer.append(record)
        while len(self.buffer) > self.window_size:
            self.buffer.pop(0)
        self._count_subsequence(self.buffer)
        return result

    @BaseDetector.require_initialize
    def train(self, training_data):
        for record in training_data:
            self.handle_record(record)
