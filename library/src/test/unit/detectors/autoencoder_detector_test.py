import os
import sys

import torch
import numpy as np
import random

project_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(project_path)

from detectors.autoencoder.autoencoder_detector import AutoEncoderDetector
from common.dataset import CSVDataset
from utils.collection_tools import windowed_list
from utils.analysis import draw_array


def test_detector():
    detector = AutoEncoderDetector()

    # tell the detector, each input record is of length 2
    detector.initialize(2)

    # training the data with some size 2 records
    x_train = torch.tensor([[1.0, 2.0], [2.0, 3.0], [4.0, 5.0]])

    # set epochs number to 3000, show the loss value during training
    detector.train(x_train, num_epochs=3000, verbose=True)

    # predict the result, you don't need a prediction if you just the anomaly score
    x_pred = detector.predict(x_train)
    print(detector.predict(torch.tensor([[1.0, 2.0], [2, 3]])))

    # get an anomaly score of a new single record
    print(detector.handle_record([1.0, 2.0]))

    print(detector.handle_record_sequence([[1, 2], [2, 3]]))


def test_detector_on_file():
    detector = AutoEncoderDetector()

    window_size = 4

    # tell the detector, each input record is of length 2
    detector.initialize(window_size)

    file_path = project_path + "/../data/NAB_data/data/realAWSCloudwatch/ec2_cpu_utilization_5f5533.csv"
    data = CSVDataset(file_path, header=1, values=1, test_size=0).get_data()[0]["values"]

    windowed_data = windowed_list(data, window_size=window_size)

    # randomly choice 15% of data to train
    training_data = random.choices(windowed_data, k=int(len(windowed_data) * 0.15))

    training_data = torch.from_numpy(np.array(training_data, dtype="float32"))

    detector.train(training_data, num_epochs=4000, verbose=True)

    result = detector.handle_record_sequence(windowed_data)

    draw_array(data)

    draw_array(result)


if __name__ == '__main__':
    test_detector()
    test_detector_on_file()
