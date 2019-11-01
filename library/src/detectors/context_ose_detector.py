# Created by Xinyu Zhu on 10/6/2019, 11:51 PM


import sys

sys.path.append("../")
from common.context_ose.cad_ose import ContextualAnomalyDetectorOSE
from detectors.base import BaseDetector


class ContextOSEDetector(BaseDetector):
    """
    This detector uses Contextual Anomaly Detector - Open Source Edition
    2016, Mikhail Smirnov   smirmik@gmail.com
    https://github.com/smirmik/CAD
    """

    def __init__(self, value_col_name=None):
        if value_col_name is not None:
            super(ContextOSEDetector, self).__init__(timestamp_col_name=None,
                                                     measure_col_names=[value_col_name], symbolic=False)
        else:
            super(ContextOSEDetector, self).__init__(timestamp_col_name=None,
                                                     measure_col_names=["value"], symbolic=False)

    def initialize(self, min_value, max_value, probationary_period=150, *args, **kwargs):
        """A fact about this detector is that is requires the knowledge of the min_value and max_value"""
        super(ContextOSEDetector, self).initialize(args, kwargs)
        self.cadose = ContextualAnomalyDetectorOSE(
            min_value=min_value,
            max_value=max_value,
            rest_period=probationary_period / 5.0,
        )

    @BaseDetector.require_initialize
    def handle_record(self, input_data):
        # input_data = self._pre_process_record(input_data)
        input_data = self._pre_process_record(input_data)
        input_data = {"value": input_data}
        anomaly_score = self.cadose.getAnomalyScore(input_data)
        return anomaly_score
