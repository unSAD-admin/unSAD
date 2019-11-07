# Created by Xinyu Zhu on 10/7/2019, 12:53 AM
import sys
import os
project_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(project_path)

from detectors.relative_entropy_detector import RelativeEntropyDetector
from common.dataset import CSVDataset




def test_detector():
    # read in the data
    file_path = project_path + "/../data/NAB_data/data/realAWSCloudwatch/ec2_cpu_utilization_5f5533.csv"
    data = CSVDataset(file_path, header=1, values=1, test_size=0).get_data()[0]["values"]

    # finding min max of the value
    min_value = min(data)
    max_value = max(data)

    # initialize the detector
    detector = RelativeEntropyDetector()
    detector.initialize(input_min=min_value, input_max=max_value, window_size=52, n_nins=5)

    # handle all the record
    result = detector.handle_record_sequence(data)
    # draw_array(result)


if __name__ == "__main__":
    test_detector()
