# Created by Xinyu Zhu on 10/3/2019, 2:47 AM

import os
import sys

project_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(project_path)

from collections import defaultdict

from detectors.symbolic.sequential_pattern import SequentialPatternAnomalyDetector
from utils.collection_tools import simple_filter, mean_filter
from utils.analysis import draw_array


def readFile(filename):
    result = defaultdict(list)
    with open(filename) as f:
        content = f.read()
        content = content.split("\n")
        for line in content:
            if line is not None and line != "":
                cline = line.split(' ')
                result[cline[0]].append(cline[1])

    new_result = {}
    for key in result:
        if len(result[key]) == 1:
            continue
        else:
            new_result[key] = result[key]

    return new_result


def test_detector():
    # read in the data
    data = {"training1": readFile(project_path + "/../data/login_trace/login.trace_9809181415.int"),
            "training2": readFile(project_path + "/../data/login_trace/login.trace_9809251022.int"),
            "testing": readFile(project_path + "/../data/login_trace/login-homegrown.int"),
            "recover": readFile(project_path + "/../data/login_trace/login-recovered.int")}

    sequence = []
    for key in data["training1"]:
        sequence += data["training1"][key]

    print(sequence.__len__())
    for key in data["training2"]:
        sequence += data["training2"][key]

    print(sequence.__len__())
    for key in data["testing"]:
        sequence += data["testing"][key]

    print(sequence.__len__())
    for key in data["recover"]:
        sequence += data["recover"][key]

    print(sequence.__len__())
    print(sequence)

    detector = SequentialPatternAnomalyDetector()
    window_size = 20
    detector.initialize(window_size)

    result = detector.handle_record_sequence(sequence)

    result = simple_filter(result, mean_filter, window_size)
    print(result)
    draw_array(result)
    # detector.handle_record_sequence()


if __name__ == '__main__':
    test_detector()
