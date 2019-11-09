# Created by Xinyu Zhu on 10/7/2019, 6:03 PM
import datetime
import sys

import os

project_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(project_path)

from common.dataset import CSVDataset
from detectors.htm.htm_detector import HTMAnomalyDetector

# the data file should be csv file which contains at least timestamp and value
data_file_path = project_path + "/../data/NAB_data/data/realAWSCloudwatch/ec2_cpu_utilization_5f5533.csv"
# the docker_path is the htm docker's path
docker_path = project_path + "/../docker/htmDocker"


def test_detector():
    # read in the data
    file_path = data_file_path
    data = CSVDataset(file_path, header=1, timestamp=0, values=1, test_size=0).get_data()[0]
    data = list(zip([datetime.datetime.strptime(x, '%Y-%m-%d %H:%M:%S').timestamp() for x in data["timestamp"]],
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
    # set the probation_number to be 10% of the length of the original data set
    detector.initialize(docker_path=docker_path, probation_number=int(len(data) * 0.10),
                        lower_data_limit=min_value,
                        upper_data_limit=max_value)

    # train with data
    result = detector.train(data)
    result_anomaly_score = []
    for r in result:
        result_anomaly_score.append(r["anomalyScore"])

    # visualize the result
    # draw_array(result_anomaly_score)


def test_handle_data():
    htm = HTMAnomalyDetector("timestamp", "value")
    htm.initialize(docker_path=docker_path)
    # testing handle_record
    print("Testing handle_record()")
    # the testing data is in this format [[timestamp, value], [timestamp, value], ...] sorted by timestamp
    testing_data = [[12, 1], [13, 2], [15, 7], [17, 9], [18, 4]]

    streaming_result = []
    for record in testing_data:
        # feed in the testing_data one by one
        sub_result = htm.handle_record(record)
        streaming_result.append(sub_result)
    print(streaming_result)
    # testing train()
    print("Testing train()")
    # clear the previous memory by calling initialize
    htm.initialize(docker_path=docker_path)
    result = htm.train(testing_data)
    print(result)

    assert result == streaming_result


if __name__ == "__main__":
    test_detector()
    test_handle_data()
