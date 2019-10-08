# Created by Xinyu Zhu on 10/2/2019, 11:46 PM
from collections import Iterable
import numpy as np


class BaseDetector:
    """
    Base class for all anomaly detectors. When inheriting from this class please
    take note of which methods MUST be overridden, as documented below.
    """

    """
    Current concern:
    Symbolic detection or numerical detection?
    With timestamp or no timestamp
    Single measure or multiple measure
    """

    def __init__(self, timestamp_col_name=None, measure_col_names=None, symbolic=False):
        """
        Detector independent initialization, initialize resource that is
        common for all detectors

        Data format definition
        timestamp_col_name: the column name for timestamp
        measure_col_names: the list of column name that need to be considered by detector
        """
        assert timestamp_col_name is None or isinstance(timestamp_col_name, str)
        assert measure_col_names is None or (isinstance(measure_col_names, list) and len(measure_col_names) > 0)
        assert isinstance(symbolic, bool)
        self.timestamp = timestamp_col_name
        self.measure = measure_col_names
        self.symbolic = symbolic

    def _check_parameter(self, data):
        """
        Check whether an input data record has correct data format
        """
        return self._pre_process_record(data) is not None

    def _pre_process_record(self, data):
        """
        Return a preprocessed data format for the detector to use
        The result is a list of float value with the first to be
        timestamp (if timestamp is specified), or a list of two
        elements with the first to be timestamp and second to be
        the symbol (if it is a symbolic anomaly detection)
        """
        result = []
        symbolic_split = ","
        if isinstance(data, dict):
            if self.measure is None:
                return None
            if self.timestamp is not None:
                if self.timestamp in data:
                    try:
                        result.append(float(data[self.timestamp]))
                        [result.append(data[measure]) for measure in self.measure]
                    except RuntimeError:
                        return None
                else:
                    return None
            else:
                try:
                    [result.append(data[measure]) for measure in self.measure]
                except RuntimeError:
                    return None
        elif isinstance(data, Iterable) and not isinstance(data, str):
            if self.timestamp is not None:
                if len(data) == len(self.measure) + 1:
                    try:
                        result = data
                        result[0] = float(result[0])
                    except RuntimeError as e:
                        return None
                else:
                    return None
            else:
                if len(data) == len(self.measure):
                    try:
                        result = data
                    except RuntimeError as e:
                        return None
                else:
                    return None
        else:
            if (self.measure is None or len(self.measure) == 1) and self.timestamp is None:
                if self.symbolic:
                    return str(data)
                else:
                    try:
                        return float(data)
                    except RuntimeError as e:
                        return None
            else:
                return None

        if not self.symbolic:
            return [float(result[i]) for i in range(len(result))]
        else:
            if self.timestamp is not None:
                return [result[0], symbolic_split.join([str(s) for s in result[1:]])]
            else:
                return symbolic_split.join([str(s) for s in result])

    def get_data_format(self):
        """
        Return the data record format that is accepted by this detector
        """
        return {
            "timestamp": self.timestamp,
            "measure": self.measure,
            "symbolic": self.symbolic
        }

    def initialize(self, *args, **kwargs):
        """
        Detector specific initialization, initialize resource that is
        unique for a specific detector
        """
        pass

    def process_training_data(self, data, processors):
        res = data.copy()
        for processor in processors:
            res = processor.processTrainingData(res)
        return res

    def train(self, training_data):
        """
        This is a optional training process for the anomaly detection
        It should be call before handle_record to improve performance
        """
        pass

    def process_new_data(self, data, processors):
        res = data.copy()
        for processor in processors:
            res = processor.processTestingdata(res)
        return res

    def handle_record(self, record):
        """
        This is the main anomaly detection method, it deals with streaming data
        instead of a block data.
        """
        raise NotImplementedError

    def handle_record_sequence(self, record_sequence):
        """
        This function provide an ability to handle a list of data record sequentially
        """
        result = []
        for record in record_sequence:
            result.append(self.handle_record(record))
        return result
