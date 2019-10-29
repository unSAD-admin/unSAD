# Created by Xinyu Zhu on 10/22/2019, 10:33 PM

import sys
import datetime
import json

sys.path.append("../../")
from detectors.context_ose_detector import ContextOSEDetector


def to_timestamp(timestr):
    if timestr.endswith(".000000"):
        timestr = timestr[0:-7]
    timestamp = datetime.datetime.strptime(timestr, '%Y-%m-%d %H:%M:%S').timestamp()
    return timestamp


def read_data():
    file_path = "../../../data/NAB_data/labels/combined_windows.json"
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
        path = "../../../data/NAB_data/data/" + key
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

    probation_number = [10, 50, 100, 150, 200, 300, 400, 500, 600, 700, 800, 900, 1000]

    window_size = 50

    threshold = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]

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

    result_collector = []
    for probation in probation_number:
        for thread in threshold:
            detector = ContextOSEDetector("value")
            for key in all_data_keys:

                if key not in result:
                    result[key] = []

                data_value = data[key]
                min_value = 10e10
                max_value = -10e10
                for i in range(min(probation, len(data_value))):
                    if min_value > data_value[i]["value"]:
                        min_value = data_value[i]["value"]
                    if max_value < data_value[i]["value"]:
                        max_value = data_value[i]["value"]

                detector.initialize(min_value=min_value, max_value=max_value, probationary_period=probation)

                training_data = []
                for record in data_value:
                    training_data.append(record["value"])
                detect_result = detector.handle_record_sequence(training_data)

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
                    score = detect_result[i]
                    if score >= thread:
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
                    "probation_number": probation, "F": f_score, "precision": precision, "recall": recall,
                    "threshold": thread
                })

                obj = {
                    "file": key,
                    "probation_number": probation,
                    "threshold": thread,
                    "F": f_score,
                    "precision": precision,
                    "recall": recall
                }
                with open("context_ose_detector_evaluation_result.json", "a") as f:
                    f.write(json.dumps(obj) + "\n")
                print(str(obj))

    print("OK")
