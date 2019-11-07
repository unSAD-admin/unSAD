# Created by Xinyu Zhu on 10/7/2019, 12:00 AM

import sys

import os

project_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(project_path)


from detectors.context_ose_detector import ContextOSEDetector
from common.dataset import CSVDataset
from utils.analysis import draw_array


def test_detector():
    # read in the data
    file_path = project_path + "/../data/NAB_data/data/realAWSCloudwatch/ec2_cpu_utilization_5f5533.csv"
    data = CSVDataset(file_path, header=1, values=1, test_size=0).get_data()[0]["values"]

    # finding min max of the value
    min_value = min(data)
    max_value = max(data)

    # initialize the detector
    detector = ContextOSEDetector()
    detector.initialize(min_value=min_value, max_value=max_value, probationary_period=150)

    # handle all the record
    all_result = detector.handle_record_sequence(data)
    draw_array(all_result)


if __name__ == "__main__":
    test_detector()