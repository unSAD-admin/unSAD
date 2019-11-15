# Created by Xinyu Zhu on 10/22/2019, 10:33 PM

import sys
import json
import os
from .experiment_utils import read_data, f_score_calc, get_min_max

project_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_path)

from detectors.context_ose_detector import ContextOSEDetector

if __name__ == '__main__':
    data = read_data()

    probation_number = [10, 50, 100, 150, 200, 300, 400, 500, 600, 700, 800, 900, 1000]

    window_size = 50

    threshold = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]

    """
    result = 
    {"path":[{"spatial_tolerance":tolerance, "F1 score":F1, "Precision": precision, "Recall": Recall}, ..]
    """
    result = {}

    all_data_keys = list(data.keys())
    all_data_keys.sort()

    result_collector = []
    # for each probation number
    for probation in probation_number:
        # for each threshold do an experiment
        for thread in threshold:
            detector = ContextOSEDetector("value")
            for key in all_data_keys:

                if key not in result:
                    result[key] = []

                # find out the min max value in the probational part of the data

                data_value = data[key]
                min_value, max_value = get_min_max(data_value, probation)

                detector.initialize(min_value=min_value, max_value=max_value, probationary_period=probation)

                # prepare the data
                training_data = []
                for record in data_value:
                    training_data.append(record["value"])

                # get the detection result
                detect_result = detector.handle_record_sequence(training_data)

                # calculate the performance
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

                f_score, precision, recall = f_score_calc(windowed_result)

                result[key].append({
                    "probation_number": probation, "F": f_score, "precision": precision, "recall": recall,
                    "threshold": thread
                })
                # get the F1 score, precision and recall for a specific file
                # under a specific threshold and probation_number setting
                obj = {
                    "file": key,
                    "probation_number": probation,
                    "threshold": thread,
                    "F": f_score,
                    "precision": precision,
                    "recall": recall
                }
                # record the performance result
                with open("context_ose_detector_evaluation_result.json", "a") as f:
                    f.write(json.dumps(obj) + "\n")
                print(str(obj))

    print("OK")
