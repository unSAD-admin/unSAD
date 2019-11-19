# Created by Xinyu Zhu on 10/12/2019, 12:23 PM

import sys
import json
import os
from .experiment_utils import read_data, f_score_calc, get_min_max

project_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_path)
from detectors.htm.htm_detector import HTMAnomalyDetector

if __name__ == '__main__':
    """
    Test the relationship between HTM algorithm performance and probation_number
    """
    data = read_data()
    window_size = 50
    threshold = 0.512250003693
    spatial_tolerance = 0.05

    probation_number_to_test = [150, 350, 550, 750, 950, 1150, 1350]

    # curl http:127.0.0.1:8081/recycle -> success
    """
    result = 
    {"path":[{"spatial_tolerance":tolerance, "F1 score":F1, "Precision": precision, "Recall": Recall}, ..]
    """
    result = {}

    all_data_keys = list(data.keys())
    all_data_keys.sort()

    # detector = HTMAnomalyDetector("timestamp", "value")
    result_collector = []
    for probation_number in probation_number_to_test:
        detector = HTMAnomalyDetector("timestamp", "value")
        for key in all_data_keys:

            if key not in result:
                result[key] = []

            data_value = data[key]
            min_value, max_value = get_min_max(data_value, probation_number)

            # max_detector_num is set to be 20 so that we can run 20 different experiments at the same time
            detector.initialize(project_path + "/../docker/htmDocker", probation_number=probation_number,
                                lower_data_limit=min_value,
                                upper_data_limit=max_value, spatial_tolerance=spatial_tolerance, max_detector_num=20)

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

            f_score, precision, recall = f_score_calc(windowed_result)

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

        with open("probation_experiment_result.json", "a") as f:
            for data_record in data_result:
                f.write(json.dumps(data_record) + "\n")

        print("OK", spatial_tolerance)
