# Created by Xinyu Zhu on 10/4/2019, 3:09 AM
from flask import Flask
from flask import jsonify
from datetime import datetime

from htm_detector import DetectorServiceProvider

app = Flask(__name__)

detectorServiceProvider = DetectorServiceProvider(10)


@app.route('/new_detector/<lower_limit>/<upper_limit>/<probation_number>/<spatial_tolerace>')
def new_detector(lower_data_limit=-1e9, upper_data_limit=1e9, probation_number=750,
                 spatial_tolerance=0.05):
    return detectorServiceProvider.create_htm_detector(float(lower_data_limit), float(upper_data_limit),
                                                       int(probation_number),
                                                       float(spatial_tolerance))


@app.route('/recycle')
def recycle():
    detectorServiceProvider.recycle_all_detectors()
    return "success"


@app.route('/set_max/<new_max>')
def set_max(new_max=10):
    detectorServiceProvider.set_max_detector(int(new_max))
    return "success"


@app.route("/handle/<key>/<timestamp>/<value>")
def handle_record(key, timestamp, value):
    record = {
        "timestamp": datetime.fromtimestamp(float(timestamp)),
        "value": float(value)
    }
    result = detectorServiceProvider.handle_record(record, key)

    if result is None:
        return ""

    return jsonify(anomalyScore=result[0], rawScore=result[1])


if __name__ == '__main__':
    app.run(port=8081, host="0.0.0.0")
