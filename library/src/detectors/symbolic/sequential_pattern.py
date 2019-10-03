# Created by Xinyu Zhu on 10/3/2019, 1:33 AM
from library.src.detectors.base import BaseDetector


class SequentialPatternAnomalyDetector(BaseDetector):
    def initialize(self, window_size=60, *args, **kwargs):
        super(SequentialPatternAnomalyDetector, self).initialize(*args, **kwargs)
        self.window_size = 60

    def handle_record(self, record):
        pass

    def train(self, training_data):
        pass
