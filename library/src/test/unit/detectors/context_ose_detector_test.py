# Created by Xinyu Zhu on 10/7/2019, 12:00 AM

import sys
import unittest

sys.path.append("../../../")

from detectors.context_ose_detector import ContextOSEDetector
from common.dataset import CSVDataset
from utils.analysis import draw_array


class TestContextOseDetector(unittest.TestCase):

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
        detector = ContextOSEDetector()
        detector.initialize(min_value=min_value, max_value=max_value, probationary_period=150)

        # handle all the record
        all_result = detector.handle_record_sequence(data)
        draw_array(all_result)


if __name__ == '__main__':
    unittest.main()
