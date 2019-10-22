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
        data = CSVDataset(file_path, header=1, timestamp=0, values=1, test_size=0).getData()[0]
        data = [list(x) for x in
                list(zip([datetime.datetime.strptime(x, '%Y-%m-%d %H:%M:%S').timestamp() for x in data["timestamp"]],
                         data["values"]))]

        # finding min max of the value
        min_value = 10e10
        max_value = -10e10
        for record in data:
            if min_value > record[1]:
                min_value = record[1]
            if max_value < record[1]:
                max_value = record[1]


        detector = RelativeEntropyDetector()
        detector.initialize(input_min=min_value, input_max=max_value)
        print(data)
        result = detector.handle_record_sequence(data)
        print(result)

        # all_result = []
        # for i in range(1, 101):
        #     if i == 40:
        #         result = detector.handle_record({
        #
        #             "value": 99
        #         })
        #         all_result.append(result)
        #         continue
        #     result = detector.handle_record({
        #
        #         "value": i
        #     })
        #     all_result.append(result)
        #
        # print(all_result)
        #
        # draw_array(all_result)


if __name__ == '__main__':
    unittest.main()
