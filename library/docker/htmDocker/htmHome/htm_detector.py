# Created by Xinyu Zhu on 10/4/2019, 12:48 AM

# ----------------------------------------------------------------------
# Copyright (C) 2014, Numenta, Inc.  Unless you have an agreement
# with Numenta, Inc., for a separate license for this software code, the
# following terms and conditions apply:
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero Public License version 3 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU Affero Public License for more details.
#
# You should have received a copy of the GNU Affero Public License
# along with this program.  If not, see http://www.gnu.org/licenses.
#
# http://numenta.org/licenses/
# ----------------------------------------------------------------------

import math
import time
import random

from nupic.algorithms import anomaly_likelihood
from nupic.frameworks.opf.common_models.cluster_params import (
    getScalarMetricWithTimeOfDayAnomalyParams)

try:
    from nupic.frameworks.opf.model_factory import ModelFactory
except:
    # Try importing it the old way (version < 0.7.0.dev0)
    from nupic.frameworks.opf.modelfactory import ModelFactory


class HtmDetector:
    """
    This is the algorithm layer of HTM which will provides basic algorithm service
    This class is mainly copied and modified based on
    https://github.com/numenta/NAB/blob/master/nab/detectors/numenta/numenta_detector.py
    """

    def __init__(self):
        self.model = None
        # self.sensorParams = None
        self.anomaly_likelihood = None
        # Keep track of value range for spatial anomaly detection

        self.min_val = None

        self.max_val = None

        # Set this to False if you want to get results based on raw scores
        # without using AnomalyLikelihood. This will give worse results, but
        # useful for checking the efficacy of AnomalyLikelihood. You will need
        # to re-optimize the thresholds when running with this setting.
        self.useLikelihood = True

    def handle_record(self, input_data):
        """
        :param input_data:  dict in the following format:
        {"timestamp": datetime.fromtimestamp(timestamp), "value": value}
        timestamp must be a datetime object, value must be a float value
        :return: a tuple (anomalyScore, raw_score)

       """
        # Send it to Numenta detector and get back the results
        result = self.model.run(input_data)

        # Get the value
        value = input_data["value"]

        # Retrieve the anomaly score and write it to a file
        raw_score = result.inferences["anomalyScore"]

        # Update min/max values and check if there is a spatial anomaly
        spatial_anomaly = False
        if self.min_val != self.max_val:
            tolerance = (self.max_val - self.min_val) * self.spatial_tolerance
            max_expected = self.max_val + tolerance
            min_expected = self.min_val - tolerance
            if value > max_expected or value < min_expected:
                spatial_anomaly = True
        if self.max_val is None or value > self.max_val:
            self.max_val = value
        if self.min_val is None or value < self.min_val:
            self.min_val = value

        if spatial_anomaly:
            final_score = 1.0
            return (final_score, raw_score)

        if self.useLikelihood:
            # Compute log(anomaly likelihood)
            anomaly_score = self.anomaly_likelihood.anomalyProbability(
                input_data["value"], raw_score, input_data["timestamp"])
            log_score = self.anomaly_likelihood.computeLogLikelihood(anomaly_score)
            final_score = log_score
        else:
            final_score = raw_score

        return (final_score, raw_score)

    def initialize(self, lower_data_limit=-1e9, upper_data_limit=1e9, probation_number=750, spatial_tolerance=0.05):
        """
        Any data that is not in the range [lower_data_limit, upper_data_limit]
        will be regarded as anomaly directly

        the algorithm will treat the first probation_number input as a reference to calculate likelihood
        It is expect that no anomaly should be in the first probation_number sample, the longer the better
        """
        self.probationary_period = probation_number
        self.input_min = lower_data_limit
        self.input_max = upper_data_limit

        # Fraction outside of the range of values seen so far that will be considered
        # a spatial anomaly regardless of the anomaly likelihood calculation. This
        # accounts for the human labelling bias for spatial values larger than what
        # has been seen so far.
        self.spatial_tolerance = spatial_tolerance

        # Get config params, setting the RDSE resolution
        range_padding = abs(self.input_max - self.input_min) * 0.2
        model_params = getScalarMetricWithTimeOfDayAnomalyParams(
            metricData=[0],
            minVal=self.input_min - range_padding,
            maxVal=self.input_max + range_padding,
            minResolution=0.001,
            tmImplementation="cpp"
        )["modelConfig"]

        self._setupEncoderParams(
            model_params["modelParams"]["sensorParams"]["encoders"])

        self.model = ModelFactory.create(model_params)
        self.model.enableInference({"predictedField": "value"})

        if self.useLikelihood:
            # Initialize the anomaly likelihood object
            numenta_learning_period = int(math.floor(self.probationary_period / 2.0))
            self.anomaly_likelihood = anomaly_likelihood.AnomalyLikelihood(
                learningPeriod=numenta_learning_period,
                estimationSamples=self.probationary_period - numenta_learning_period,
                reestimationPeriod=100
            )


    def _setupEncoderParams(self, encoderParams):
        # The encoder must expect the NAB-specific datafile headers
        encoderParams["timestamp_dayOfWeek"] = encoderParams.pop("c0_dayOfWeek")
        encoderParams["timestamp_timeOfDay"] = encoderParams.pop("c0_timeOfDay")
        encoderParams["timestamp_timeOfDay"]["fieldname"] = "timestamp"
        encoderParams["timestamp_timeOfDay"]["name"] = "timestamp"
        encoderParams["timestamp_weekend"] = encoderParams.pop("c0_weekend")
        encoderParams["value"] = encoderParams.pop("c1")
        encoderParams["value"]["fieldname"] = "value"
        encoderParams["value"]["name"] = "value"

        self.sensorParams = encoderParams["value"]


class DetectorServiceProvider:
    """
    This is the resource management layer
    """

    def __init__(self, max_size=100):

        self.max_size = max_size
        self.all_detectors = []
        self.detectors = {}

    def create_htm_detector(self, lower_data_limit=-1e9, upper_data_limit=1e9, probation_number=750,
                            spatial_tolerance=0.05):
        htm_detector = HtmDetector()
        htm_detector.initialize(lower_data_limit, upper_data_limit, probation_number, spatial_tolerance)
        key = str(time.time()) + str(random.randint(0, 1000))

        self.all_detectors.append(key)
        self.detectors[key] = htm_detector
        # FIFO protocol to recycle the detectors
        while len(self.all_detectors) > self.max_size:
            key_to_delete = self.all_detectors.pop(0)
            del self.detectors[key_to_delete]
        return key

    def recycle_all_detectors(self):
        self.all_detectors = []
        self.detectors = {}

    def set_max_detector(self, max_num):
        self.max_size = max_num

    def handle_record(self, input_data, detector_key):
        if detector_key in self.detectors:
            return self.detectors[detector_key].handle_record(input_data)
        else:
            # the detector is no longer exist
            return None
