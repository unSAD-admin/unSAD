# Created by Xinyu Zhu on 10/2/2019, 11:46 PM
from collections import Iterable
import logging
import sys

import os

project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_path)
from common.unsad_exceptions import UnSADException


class BaseDetector:
    """
    Base class for all anomaly detectors. When inheriting from this class please
    take note of which methods MUST be overridden, as documented below.
    """

    def __init__(self, timestamp_col_name=None, measure_col_names=None, symbolic=False):
        """
        Detector independent initialization, initialize resource that is
        common for all detectors

        Data format definition
        timestamp_col_name: the column name for timestamp
        measure_col_names: the list of column name that need to be considered by detector
        """
        assert timestamp_col_name is None or isinstance(
            timestamp_col_name, str)
        assert measure_col_names is None or (isinstance(
            measure_col_names, list) and len(measure_col_names) > 0)
        assert isinstance(symbolic, bool)
        self.timestamp = timestamp_col_name
        self.measure = measure_col_names
        self.symbolic = symbolic

        self.initialized = False

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
                logging.error(
                    "Didn't tell the detector the name of the key pointing to the value to detect")
                raise UnSADException.data_format_exception()
            if self.timestamp is not None:
                if self.timestamp in data:
                    try:
                        result.append(float(data[self.timestamp]))
                        [result.append(data[measure])
                         for measure in self.measure]
                    except RuntimeError:
                        logging.error("The input data type is invalid, please make sure "
                                      "the timestamp is a numerical type")
                        logging.error("Please make sure the input carries all the field "
                                      "that are specified when initialize the detector: " + str(self.measure))
                        raise UnSADException.data_type_exception()
                else:
                    logging.error("This detector requires a timestamp field:" + str(self.timestamp)
                                  + "but is not presented in input")
                    raise UnSADException.data_format_exception()
            else:
                try:
                    [result.append(data[measure]) for measure in self.measure]
                except RuntimeError:
                    logging.error("Please make sure the input carries all the field "
                                  "that are specified when initialize the detector: " + str(self.measure))
                    raise UnSADException.data_format_exception()
        elif isinstance(data, Iterable) and not isinstance(data, str):
            if self.timestamp is not None:
                if len(data) == len(self.measure) + 1:
                    try:
                        result = list(data)
                        result[0] = float(result[0])
                    except RuntimeError as e:
                        logging.error("The input data type is invalid, please make sure "
                                      "the timestamp (which in at index 0) is a numerical type")
                        raise UnSADException.data_type_exception()
                else:
                    logging.error("The number of input parameters:" + str(
                        len(data)) + " does not match with this detectors:" + str(len(self.measure) + 1))
                    raise UnSADException.input_number_exception()
            else:
                if len(data) == len(self.measure):
                    result = data
                else:
                    logging.error("The number of input parameters:" + str(
                        len(data)) + " does not match with this detectors:" + str(len(self.measure)))
                    raise UnSADException.input_number_exception()
        else:
            if (self.measure is None or len(self.measure) == 1) and self.timestamp is None:
                if self.symbolic:
                    return str(data)
                else:
                    try:
                        return float(data)
                    except RuntimeError as e:
                        logging.error("This detector is for numerical data, make sure"
                                      " the input can be converted to numerical data")
                        raise UnSADException.data_type_exception()
            else:
                logging.error("This detector is not initialized properly")
                raise UnSADException.not_proper_initialize_exception()

        if not self.symbolic:
            try:
                processed_result = [float(result[i])
                                    for i in range(len(result))]
            except RuntimeError as e:
                logging.error("This detector is for numerical data, make sure"
                              " the input can be converted to numerical data")
                raise UnSADException.data_type_exception()

            return processed_result[0] if len(processed_result) == 1 else processed_result

        else:
            if self.timestamp is not None:
                return [result[0], symbolic_split.join([str(s) for s in result[1:]])]
            else:
                return symbolic_split.join([str(s) for s in result])

    def require_initialize(func):
        """
        This is a function decorator to help check whether the detector has
        been initialize, some function can only be called after initialization
        You can just add  @BaseDetector.require_initialize to the top of those
        function
        """

        def check_initialize(self, *args, **kwargs):
            if not self.initialized:
                logging.error("You didn't initialize the detector by calling "
                              "initialize method, or you forget to call super.initialize() in child class")
                raise UnSADException.not_proper_initialize_exception()
            else:
                return func(self, *args, **kwargs)

        return check_initialize

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
        self.initialized = True

    def process_training_data(self, data, processors):
        res = data.copy()
        for processor in processors:
            res = processor.process_training_data(res)
        return res

    @require_initialize
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

    @require_initialize
    def handle_record(self, record):
        """
        This is the main anomaly detection method, it deals with streaming data
        instead of a block data.
        """
        raise NotImplementedError

    @require_initialize
    def handle_record_sequence(self, record_sequence):
        """
        This function provide an ability to handle a list of data record sequentially
        """
        result = []
        for record in record_sequence:
            result.append(self.handle_record(record))
        return result

    def visualize(self):
        pass
