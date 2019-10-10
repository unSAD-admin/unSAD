# Created by Xinyu Zhu on 10/7/2019, 6:03 PM
import sys
import datetime

sys.path.append("../")
from utils.analysis import draw_array

from detectors.htm.htm_detector import HTMAnomalyDetector


def read_file(file_path):
    with open(file_path) as f:
        content = f.read().split("\n")[1:]
        data = []
        for row in content:
            if row is not None and row != "":
                row_data = row.split(",")
                timestamp = datetime.datetime.strptime(row_data[0], '%Y-%m-%d %H:%M:%S').timestamp()
                data.append([timestamp, float(row_data[1])])
    return data


def read_result(file_path):
    with open(file_path) as f:
        content = f.read().split("\n")[1:]
        data = []
        for row in content:
            if row is not None and row != "":
                row_data = row.split(",")
                data.append(float(row_data[2]))
        return data


if __name__ == '__main__':
    # # file_path = "../../data/NAB_data/data/realAWSCloudwatch/ec2_cpu_utilization_5f5533.csv"
    # # data = read_file(file_path)
    # # min_value = 10e10
    # # max_value = -10e10
    # # for record in data:
    # #     if min_value > record[1]:
    # #         min_value = record[1]
    # #     if max_value < record[1]:
    # #         max_value = record[1]
    # # print(min_value, max_value)
    # #
    # # detector = HTMAnomalyDetector("timestamp", "value")
    # # detector.initialize("../../docker/htmDocker", probation_number=int(len(data) * 0.10), lower_data_limit=min_value,
    # #                     upper_data_limit=max_value)
    # #
    # # result = detector.train(data)
    # # result_anomaly_score = []
    # # for r in result:
    # #     result_anomaly_score.append(r["anomalyScore"])
    #
    # draw_array(result_anomaly_score)

    result_path = "../../data/NAB_data/results/numenta/realAWSCloudwatch/numenta_ec2_cpu_utilization_5f5533.csv"

    result_score = read_result(result_path)
    draw_array(result_score)
