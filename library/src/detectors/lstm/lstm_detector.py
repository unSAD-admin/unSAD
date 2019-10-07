import sys

sys.path.append("../../")
from detectors.base import BaseDetector

class LSTMAnomalyDetector(BaseDetector):

    def __init__(self, timestamp_col_name=None, value_col_name=None):
        if timestamp_col_name is None:  # since timestamp column name is essential for super class
            timestamp_col_name = "timestamp"

        super(LSTMAnomalyDetector, self).__init__(timestamp_col_name=timestamp_col_name,
                                                 measure_col_names=[value_col_name], symbolic=False)


