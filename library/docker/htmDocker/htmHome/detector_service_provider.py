# Created by Xinyu Zhu on 10/4/2019, 3:09 AM
from flask import Flask
from flask import request
from datetime import datetime
import json
from htm_detector import DetectorServiceProvider

app = Flask(__name__)

detector_service_provider = DetectorServiceProvider(10)


@app.route('/new_detector/<lower_data_limit>/<upper_data_limit>/<probation_number>/<spatial_tolerance>')
def new_detector(lower_data_limit=-1e9, upper_data_limit=1e9, probation_number=750,
                 spatial_tolerance=0.05):
    """
    Create a new detector for a new anomaly detection tasks, every new detector will remember information about
    previous input, but the memory is not sharable between each detector
    :param lower_data_limit: Expected minimum value of the normal data
    :param upper_data_limit: Expected maximum value of the normal data
    :param probation_number: Number of training data used to help learn normal pattern
    :param spatial_tolerance: Expected percentage of anomaly data
    :return: A key in plain text used in a dictionary pointing to the detector
    """
    return detector_service_provider.create_htm_detector(float(lower_data_limit), float(upper_data_limit),
                                                         int(probation_number),
                                                         float(spatial_tolerance))


@app.route('/recycle')
def recycle():
    """
    recycle all the existing detectors
    :return: "success"
    """
    detector_service_provider.recycle_all_detectors()
    return "success"


@app.route('/set_max/<new_max>')
def set_max(new_max=10):
    """
    set maximum number of detectors that can exist at the same time
    :param new_max: the new maximum number
    :return: "success"
    """
    detector_service_provider.set_max_detector(int(new_max))
    return "success"


@app.route("/handle/<key>/<timestamp>/<value>")
def handle_record(key, timestamp, value):
    """

    :param key: the key pointing to the detector
    :param timestamp: the timestamp (float value) of a data record
    :param value: the value of the data record
    :return: dictionary in plain text containing anomaly score and raw score
    """
    record = {
        "timestamp": datetime.fromtimestamp(float(timestamp)),
        "value": float(value),
    }
    result = detector_service_provider.handle_record(record, key)

    if result is None:
        return ""
    return str(result)[1:-1]


@app.route("/handle_block/<key>", methods=['POST'])
def handle_block(key):
    """
    A post request handle to handle a block of data
    :param key: the key pointing to the detector
    :return: A list in plain text containing all the dictionary with
    anomaly score and raw score
    """
    obj = json.loads(request.data)
    timestamps = obj["timestamps"]
    values = obj["values"]

    result = []
    for i in range(len(timestamps)):
        record = {
            "timestamp": datetime.fromtimestamp(float(timestamps[i])),
            "value": float(values[i])
        }
        result.append(str(detector_service_provider.handle_record(record, key))[1:-1])
    result_obj = {
        "result": result
    }
    return str(result_obj).replace("'", '"')


@app.route("/health_check")
def health_check():
    """
    used to check whether the service is available
    :return: "success"
    """
    return "success"


if __name__ == '__main__':
    app.run(port=8081, host="0.0.0.0")
