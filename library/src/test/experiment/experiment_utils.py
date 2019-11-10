# Created by Xinyu Zhu on 11/9/2019, 12:21 PM
import datetime
import json
import os
import sys

project_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_path)

"""
This file provides functions to load and parse NAB data set for experiments
"""


def to_timestamp(timestr):
    if timestr.endswith(".000000"):
        # Remove the ".000000" postfix to normalize the string format
        time_str = timestr[0:-7]
    timestamp = datetime.datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S').timestamp()
    return timestamp


def read_data():
    # This is the path to the labels of the data set
    file_path = project_path + "/../data/NAB_data/labels/combined_windows.json"
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
        # This is the path to the data file
        path = project_path + "/../data/NAB_data/data/" + key
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


def f_score_calc(windowed_result):
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
        # there is no positive response, define the precision to be 1 in this case
        precision = 1

    if true_positive + false_negative != 0:
        recall = true_positive / (true_positive + false_negative)
    else:
        # the dataset does not contain any abnormal, define the recall to be 1 in this case
        recall = 1

    if precision + recall != 0:
        f_score = 2 * (precision * recall) / (precision + recall)
    else:
        f_score = 0
    return f_score, precision, recall


def get_min_max(data_value, probation_number):
    min_value = 10e10
    max_value = -10e10
    for i in range(min(probation_number, len(data_value))):
        if min_value > data_value[i]["value"]:
            min_value = data_value[i]["value"]
        if max_value < data_value[i]["value"]:
            max_value = data_value[i]["value"]
    return min_value, max_value
