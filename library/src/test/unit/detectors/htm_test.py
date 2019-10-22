# Created by Xinyu Zhu on 10/7/2019, 6:03 PM
import sys
import datetime
import unittest

sys.path.append("../../../")
from utils.analysis import draw_array
from common.dataset import CSVDataset
from detectors.htm.htm_detector import HTMAnomalyDetector


class TestHTMDetector(unittest.TestCase):

    def test_detector(self):

        # read in the data
        file_path = "../../../../data/NAB_data/data/realAWSCloudwatch/ec2_cpu_utilization_5f5533.csv"
        data = CSVDataset(file_path, header=1, timestamp=0, values=1, test_size=0).getData()[0]
        data =  list(zip([datetime.datetime.strptime(x, '%Y-%m-%d %H:%M:%S').timestamp() for x in data["timestamp"]],
                         data["values"]))


        # finding min max of the value
        min_value = 10e10
        max_value = -10e10
        for record in data:
            if min_value > record[1]:
                min_value = record[1]
            if max_value < record[1]:
                max_value = record[1]

        # initialize the detector, assume a docker service is already running
        detector = HTMAnomalyDetector("timestamp", "value")
        detector.initialize(docker_path="../../../../docker/htmDocker", probation_number=int(len(data) * 0.10),
                            lower_data_limit=min_value,
                            upper_data_limit=max_value)

        # train with data
        result = detector.train(data)
        result_anomaly_score = []
        for r in result:
            result_anomaly_score.append(r["anomalyScore"])

        # visualize the result
        draw_array(result_anomaly_score)


if __name__ == '__main__':
    unittest.main()
