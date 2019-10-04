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

from nupic.algorithms import anomaly_likelihood
from nupic.frameworks.opf.common_models.cluster_params import (
    getScalarMetricWithTimeOfDayAnomalyParams)

try:
    from nupic.frameworks.opf.model_factory import ModelFactory
except:
    # Try importing it the old way (version < 0.7.0.dev0)
    from nupic.frameworks.opf.modelfactory import ModelFactory


def getProbationPeriod(probationPercent, fileLength):
    """Return the probationary period index."""
    return min(
        math.floor(probationPercent * fileLength),
        probationPercent * 5000)


class HtmDetector():
    """
    This detector uses an HTM based anomaly detection technique.
    """

    def __init__(self, *args, **kwargs):
        self.model = None
        self.sensorParams = None
        self.anomalyLikelihood = None
        # Keep track of value range for spatial anomaly detection

        # getProbationPeriod(
        #   0.15, 4032)

        self.minVal = None

        self.maxVal = None

        # Set this to False if you want to get results based on raw scores
        # without using AnomalyLikelihood. This will give worse results, but
        # useful for checking the efficacy of AnomalyLikelihood. You will need
        # to re-optimize the thresholds when running with this setting.
        self.useLikelihood = True

    def handleRecord(self, inputData):
        """Returns a tuple (anomalyScore, rawScore).

    Internally to NuPIC "anomalyScore" corresponds to "likelihood_score"
    and "rawScore" corresponds to "anomaly_score". Sorry about that.

    inputData should be in this format:
    {"timestamp": datetime.fromtimestamp(timestamp), "value": value}
    timestamp must be a datatime object
    value must be a float value
    """
        # Send it to Numenta detector and get back the results
        result = self.model.run(inputData)

        # Get the value
        value = inputData["value"]

        # Retrieve the anomaly score and write it to a file
        rawScore = result.inferences["anomalyScore"]

        # Update min/max values and check if there is a spatial anomaly
        spatialAnomaly = False
        if self.minVal != self.maxVal:
            tolerance = (self.maxVal - self.minVal) * self.spatial_tolerance
            maxExpected = self.maxVal + tolerance
            minExpected = self.minVal - tolerance
            if value > maxExpected or value < minExpected:
                spatialAnomaly = True
        if self.maxVal is None or value > self.maxVal:
            self.maxVal = value
        if self.minVal is None or value < self.minVal:
            self.minVal = value

        if self.useLikelihood:
            # Compute log(anomaly likelihood)
            anomalyScore = self.anomalyLikelihood.anomalyProbability(
                inputData["value"], rawScore, inputData["timestamp"])
            logScore = self.anomalyLikelihood.computeLogLikelihood(anomalyScore)
            finalScore = logScore
        else:
            finalScore = rawScore

        if spatialAnomaly:
            finalScore = 1.0

        return (finalScore, rawScore)

    def initialize(self, lower_data_limit=-1e9, upper_data_limit=1e9, probation_number=750, spatial_tolerance=0.05):
        """
            Any data that is not in the range [lower_data_limit, upper_data_limit]
            will be regarded as anomaly directly

            the algorithm will treat the first probation_number input as a reference to calculate likelihood
            It is expect that no anomaly should be in the first probation_number sample, the longer the better
        """
        self.probationaryPeriod = probation_number
        self.inputMin = lower_data_limit
        self.inputMax = upper_data_limit

        # Fraction outside of the range of values seen so far that will be considered
        # a spatial anomaly regardless of the anomaly likelihood calculation. This
        # accounts for the human labelling bias for spatial values larger than what
        # has been seen so far.
        self.spatial_tolerance = spatial_tolerance

        # Get config params, setting the RDSE resolution
        rangePadding = abs(self.inputMax - self.inputMin) * 0.2
        modelParams = getScalarMetricWithTimeOfDayAnomalyParams(
            metricData=[0],
            minVal=self.inputMin - rangePadding,
            maxVal=self.inputMax + rangePadding,
            minResolution=0.001,
            tmImplementation="cpp"
        )["modelConfig"]

        self._setupEncoderParams(
            modelParams["modelParams"]["sensorParams"]["encoders"])

        self.model = ModelFactory.create(modelParams)

        self.model.enableInference({"predictedField": "value"})

        if self.useLikelihood:
            # Initialize the anomaly likelihood object
            numentaLearningPeriod = int(math.floor(self.probationaryPeriod / 2.0))
            self.anomalyLikelihood = anomaly_likelihood.AnomalyLikelihood(
                learningPeriod=numentaLearningPeriod,
                estimationSamples=self.probationaryPeriod - numentaLearningPeriod,
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


import time
from datetime import datetime

if __name__ == '__main__':
    detector = HtmDetector()
    detector.initialize()
    result = []
    with open("ec2_cpu_utilization_5f5533.csv") as f:
        content = f.read().split("\n")
        for raw in content[1:]:
            if raw != None and raw != "":
                r = raw.split(",")
                timestamp = time.mktime(time.strptime(r[0], '%Y-%m-%d  %H:%M:%S'))
                value = float(r[1])

                result.append(detector.handleRecord({"timestamp": datetime.fromtimestamp(timestamp), "value": value}))
    with open("output.txt", "w") as f:
        for r in result:
            f.write(str(r) + "\n")
