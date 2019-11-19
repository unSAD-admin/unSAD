# Created by Xinyu Zhu on 10/22/2019, 10:11 PM

import sys
import json
import os
from .experiment_utils import read_data, f_score_calc, get_min_max

project_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_path)
from detectors.relative_entropy_detector import RelativeEntropyDetector

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

    result_collector = []
    for window in window_size:
        for nbin in n_nins:
            detector = RelativeEntropyDetector("value")
            for key in all_data_keys:

                if key not in result:
                    result[key] = []

                data_value = data[key]
                min_value, max_value = get_min_max(data_value, probation_number)

                detector.initialize(input_min=min_value, input_max=max_value, n_bins=nbin, window_size=window)

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

                f_score, precision, recall = f_score_calc(windowed_result)

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
