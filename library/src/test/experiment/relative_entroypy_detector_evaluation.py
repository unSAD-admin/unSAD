# Created by Xinyu Zhu on 10/22/2019, 10:11 PM

import sys
import datetime
import json

sys.path.append("../../")
from detectors.relative_entropy_detector import RelativeEntropyDetector


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

    window_size = [5, 10, 20, 30, 40, 50, 60, 100, 120, 150, 200]
    probation_number = 750

    # Number of bins into which util is to be quantized
    n_nins = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    threshold = 0.512250003693

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
    for window in window_size:
        for nbin in n_nins:
            detector = RelativeEntropyDetector("value")
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

                detector.initialize(input_min=min_value, input_max=max_value, n_nins=nbin, window_size=window)

                training_data = []
                for record in data_value:
                    training_data.append(record["value"])
                detect_result = detector.handle_record_sequence(training_data)

                sample_num = len(detect_result)

                # Look at each window
                windowed_result = {}
                for i in range(sample_num):
                    window_index = i // window
                    if window_index not in windowed_result:
                        windowed_result[window_index] = {
                            "window_label": 0,
                            "window_result": 0
                        }
                    score = detect_result[i]
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
                    "window": window, "F": f_score, "precision": precision, "recall": recall, "n_bins": nbin
                })

                obj = {
                    "file": key,
                    "window": window,
                    "n_bins": nbin,
                    "F": f_score,
                    "precision": precision,
                    "recall": recall
                }
                with open("relative_entroypy_detector_evaluation_result.json", "a") as f:
                    f.write(json.dumps(obj) + "\n")
                print(str(obj))

    print("OK")
