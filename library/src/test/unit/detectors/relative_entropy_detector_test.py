# Created by Xinyu Zhu on 10/7/2019, 12:53 AM
import sys
import unittest

from analysis import draw_array

sys.path.append("../../../")

from detectors.relative_entropy_detector import RelativeEntropyDetector
from common.dataset import CSVDataset


class TestRelativeEntropyDetector(unittest.TestCase):

    def test_detector(self):
        # read in the data
        file_path = "../../../../data/NAB_data/data/realAWSCloudwatch/ec2_cpu_utilization_5f5533.csv"
        data = CSVDataset(file_path, header=1, values=1, test_size=0).get_data()[0]["values"]

        # finding min max of the value
        min_value = min(data)
        max_value = max(data)

        # initialize the detector
        detector = RelativeEntropyDetector()
        detector.initialize(input_min=min_value, input_max=max_value, window_size=52, n_nins=5)

        # handle all the record
        result = detector.handle_record_sequence(data)
        draw_array(result)


if __name__ == '__main__':
    unittest.main()
