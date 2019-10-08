# Created by Xinyu Zhu on 10/3/2019, 2:47 AM

import sys

sys.path.append("../")

from collections import defaultdict

from detectors.symbolic.sequential_pattern import SequentialPatternAnomalyDetector
from utils.analysis import drawArray
from utils.collection_tools import simple_filter, mean_filter


def readFile(filename):
    result = defaultdict(list)
    with open(filename) as f:
        content = f.read()
        content = content.split("\n")
        for line in content:
            if line != None and line != "":
                cline = line.split(' ')
                result[cline[0]].append(cline[1])

    newResult = {}
    for key in result:
        if len(result[key]) == 1:
            continue
        else:
            newResult[key] = result[key]

    return newResult


if __name__ == '__main__':

    data = {}

    data["training1"] = readFile("../../data/login_trace/login.trace_9809181415.int")
    data["training2"] = readFile("../../data/login_trace/login.trace_9809251022.int")
    data["testing"] = readFile("../../data/login_trace/login-homegrown.int")
    data["recover"] = readFile("../../data/login_trace/login-recovered.int")

    trainingids = list(data["training1"].keys())
    testingids = list(data["testing"].keys())
    testingnormal = list(data["training2"].keys())
    testingrecover = list(data["recover"].keys())

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
    window_size = 60
    detector.initialize(window_size)

    result = detector.handle_record_sequence(sequence)

    result = simple_filter(result, mean_filter, window_size)
    # print(result)
    drawArray(result)
    # detector.handle_record_sequence()
