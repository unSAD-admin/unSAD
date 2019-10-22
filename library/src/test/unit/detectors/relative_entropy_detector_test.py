# Created by Xinyu Zhu on 10/7/2019, 12:53 AM
import sys
import unittest
import datetime

from analysis import draw_array

sys.path.append("../../../")

from detectors.relative_entropy_detector import RelativeEntropyDetector
from common.dataset import CSVDataset


class TestHTMDetector(unittest.TestCase):

    def test_detector(self):

        # read in the data
        file_path = "../../../../data/NAB_data/data/realAWSCloudwatch/ec2_cpu_utilization_5f5533.csv"
        data = CSVDataset(file_path, header=1, values=1, test_size=0).getData()[0]["values"]

        # finding min max of the value
        min_value = 10e10
        max_value = -10e10
        for record in data:
            if min_value > record:
                min_value = record
            if max_value < record:
                max_value = record

        # initialize the detector
        detector = RelativeEntropyDetector()
        detector.initialize(input_min=min_value, input_max=max_value)

        # handle all the record
        result = detector.handle_record_sequence(data)
        draw_array(result)


if __name__ == '__main__':
    unittest.main()
