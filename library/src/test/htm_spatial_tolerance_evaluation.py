# Created by Xinyu Zhu on 10/12/2019, 12:23 PM

import sys
import datetime
import json
import time

sys.path.append("../")
from utils.annotations import simple_thread
from detectors.htm.htm_detector import HTMAnomalyDetector


def to_timestamp(timestr):
    if timestr.endswith(".000000"):
        timestr = timestr[0:-7]
    timestamp = datetime.datetime.strptime(timestr, '%Y-%m-%d %H:%M:%S').timestamp()
    return timestamp


def read_data():
    file_path = "../../data/NAB_data/labels/combined_windows.json"
    with open(file_path) as f:
        content = f.read()
        obj = json.loads(content)
    result = {}
    for key in obj:
        result[key] = []
        for slot in obj[key]:
            result[key].append([to_timestamp(slot[0]), to_timestamp(slot[1])])

    data = {}
    for key in result:
        path = "../../data/NAB_data/data/" + key
        data[key] = []
        with open(path) as f:
            content = f.read().split("\n")[1:-1]
            for line in content:
                line = line.split(",")
                timestamp = to_timestamp(line[0])
                obj = {"timestamp": timestamp, "value": float(line[1])}
                label = 0
                for slot in result[key]:
                    if slot[0] <= timestamp <= slot[1]:
                        label = 1
                obj["label"] = label
                data[key].append(obj)

    """
    data = 
    {
        "path":[{"timestamp":time, "value":value, "label":1/0}],
    }
    """
    return data


if __name__ == '__main__':
    data = read_data()
    window_size = 50
    probation_number = 750

    threshold = 0.512250003693

    spatial_tolerance_to_test = [0.01, 0.05, 0.1, 0.15, 0.2, 0.3, 0.4, 0.6, 0.8]

    # spatial_tolerance_to_test = [0.001, 0.002, 0.003, 0.004, 0.005, 0.006, 0.007, 0.008, 0.009]

    # spatial_tolerance_to_test = [0.007, 0.008, 0.009]

    spatial_tolerance_to_test = [0.001, 0.002, 0.003]  # 0.004, 0.005, 0.006, 0.007, 0.008, 0.009]

    # curl http:127.0.0.1:8081/recycle -> success

    """
    result = 
    {"path":[{"spatial_tolerance":tolerance, "F1 score":F1, "Precision": precision, "Recall": Recall}, ..]
    """
    result = {}

    all_data_keys = list(data.keys())
    all_data_keys.sort()

    all_data_keys = all_data_keys[0:]  # 57

    # detector = HTMAnomalyDetector("timestamp", "value")

    all_data_keys = all_data_keys[0:]  # 57

    # detector = HTMAnomalyDetector("timestamp", "value")

    result_collector = []
    for spatial_tolerance in spatial_tolerance_to_test:
        detector = HTMAnomalyDetector("timestamp", "value")
        for key in all_data_keys:

            if key not in result:
                result[key] = []

            data_value = data[key]
            min_value = 10e10
            max_value = -10e10
            for i in range(min(probation_number, len(data_value))):
                if min_value > data_value[i]["value"]:
                    min_value = data_value[i]["value"]
                if max_value < data_value[i]["value"]:
                    max_value = data_value[i]["value"]

            detector.initialize("../../docker/htmDocker", probation_number=probation_number, lower_data_limit=min_value,
                                upper_data_limit=max_value, spatial_tolerance=spatial_tolerance, max_detector_num=200)

            training_data = []
            for record in data_value:
                training_data.append([record["timestamp"], record["value"]])
            detect_result = detector.train(training_data=training_data)

            sample_num = len(detect_result)

            # Look at each window
            windowed_result = {}
            for i in range(sample_num):
                window_index = i // window_size
                if window_index not in windowed_result:
                    windowed_result[window_index] = {
                        "window_label": 0,
                        "window_result": 0
                    }
                score = detect_result[i]["anomalyScore"]
                if score >= threshold:
                    windowed_result[window_index]["window_result"] = 1
                if data_value[i]["label"] == 1:
                    windowed_result[window_index]["window_label"] = 1

            true_positive = 0
            true_negative = 0
            false_positive = 0
            false_negative = 0

            for i in windowed_result:
                if windowed_result[i]["window_label"] == 1:
                    if windowed_result[i]["window_result"] == 1:
                        true_positive += 1
                    else:
                        false_negative += 1
                else:
                    if windowed_result[i]["window_result"] == 1:
                        false_positive += 1
                    else:
                        true_negative += 1

            if true_positive + false_positive != 0:
                precision = true_positive / (true_positive + false_positive)
            else:
                precision = 1

            if true_positive + false_negative != 0:
                recall = true_positive / (true_positive + false_negative)
            else:
                recall = 1

            if precision + recall != 0:
                f_score = 2 * (precision * recall) / (precision + recall)
            else:
                f_score = 0

            result[key].append({
                "spatial_tolerance": spatial_tolerance, "F": f_score, "precision": precision, "recall": recall
            })

    data_result = []
    for key in result:
        for r in result[key]:
            if spatial_tolerance == r["spatial_tolerance"]:
                obj = {
                    "file": key,
                    "spatial_tolerance": r["spatial_tolerance"],
                    "F": r["F"],
                    "precision": r["precision"],
                    "recall": r["recall"]
                }
                data_result.append(obj)

    with open("spatial_tolerance_experiment_result.json", "a") as f:
        for data_record in data_result:
            f.write(json.dumps(data_record) + "\n")

    print("OK", spatial_tolerance)
