import sys
import os
project_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_path)

from detectors.base import BaseDetector
from sklearn.ensemble import IsolationForest
import numpy as np
class IforestAnomalyDetecor(BaseDetector):

    def __init__(self, timestamp_col_name=None, value_col_name=None):
        if timestamp_col_name is None:
            timestamp_col_name = 'timestamp'

        super(IforestAnomalyDetecor,
              self).__init__(timestamp_col_name=timestamp_col_name,
                             measure_col_names=[value_col_name],
                             symbolic=False)

    def initialize(
            self,
            n_estimators=100,
            max_samples="auto",
            contamination=0.1,
            max_features=1.,
            bootstrap=False,
            n_jobs=1,
            behaviour='new',
            random_state=None,
            verbose=0,
            *args,
            **kwargs
            ):

        super(IforestAnomalyDetecor, self).initialize(*args, **kwargs)
        self.n_estimators = n_estimators
        self.max_samples = max_samples
        self.contamination = contamination
        self.max_features = max_features
        self.bootstrap = bootstrap
        self.n_jobs = n_jobs
        self.behaviour = behaviour
        self.random_state = random_state
        self.verbose = verbose
        # Create iforest instance

        self.iforest = IsolationForest(n_estimators=self.n_estimators,
                                             max_samples=self.max_samples,
                                             contamination=self.contamination,
                                             max_features=self.max_features,
                                             bootstrap=self.bootstrap,
                                             n_jobs=self.n_jobs,
                                             behaviour=self.behaviour,
                                             random_state=self.random_state,
                                             verbose=self.verbose)
    @BaseDetector.require_initialize
    def train(self, training_X, training_Y=None):
        self.iforest.fit(X=training_X, y=training_Y, sample_weight=None)
        return

    @BaseDetector.require_initialize
    def predict(self, X):
        return self.iforest.predict(X)

    @BaseDetector.require_initialize
    def handle_record(self, record):
        return self.iforest.decision_function(X=record)


# if __name__ == '__main__'
#     X = np.random.rand(100, 2)
#     print(X)
#     iforest_detector = IforestAnomalyDetecor()
#     iforest_detector.initialize()
#     iforest_detector.train(X)
#     res = iforest_detector.handle_record(X)
#     print (res)