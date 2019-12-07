import os
import sys

import torch
import numpy as np
import random
import matplotlib
import matplotlib.pyplot as plt

project_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(project_path)

from detectors.autoencoder.autoencoder_detector import AutoEncoderDetector
from common.dataset import CSVDataset
from utils.collection_tools import windowed_list
from utils.analysis import draw_array


def ttest_detector():
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


def ttest_credit_card_data():
    detector = AutoEncoderDetector()
    detector.initialize(29)
    windowed_data = []
    data = []
    with open(project_path + "/../data/SofaSofa_Anomaly.csv") as f:
        content = f.read().split("\n")[1:]
        for line in content:
            if line != "":
                line = line.split(",")[1:]
                data.append(float(line[-1]))
                line = line[0:-1]
                buffer = []
                for value in line:
                    buffer.append(float(value))
                windowed_data.append(buffer)

    normal = []
    abnomal = []
    for i, value in enumerate(data):
        if value > 0.5:
            abnomal.append(windowed_data[i])
        else:
            normal.append(windowed_data[i])
    data.sort()
    windowed_data = normal + abnomal

    training_data = random.choices(normal, k=int(len(normal) * 0.99))

    training_data = torch.from_numpy(np.array(training_data, dtype="float32"))

    loss_list = detector.train(training_data, num_epochs=16000, verbose=True)

    result = detector.handle_record_sequence(normal + abnomal)

    plt.subplot(311)
    plt.plot(np.arange(len(loss_list)), loss_list)
    # plt.title('Loss During Training')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')

    plt.subplot(312)
    plt.plot(np.arange(len(data)), data)
    # plt.title('Original Data')
    plt.xlabel('Index')
    plt.ylabel('Value')

    plt.subplot(313)
    plt.plot(np.arange(len(result)), result)
    # plt.title('Anomaly score')
    plt.xlabel('Index')
    plt.ylabel('Score')
    plt.show()

    print(len(normal), len(abnomal))


def ttest_detector_on_file():
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

    loss_list = detector.train(training_data, num_epochs=4000, verbose=True)

    result = detector.handle_record_sequence(windowed_data)

    plt.subplot(311)
    plt.plot(np.arange(len(loss_list)), loss_list)
    # plt.title('Loss During Training')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')

    plt.subplot(312)
    plt.plot(np.arange(len(data)), data)
    # plt.title('Original Data')
    plt.xlabel('Index')
    plt.ylabel('Value')

    plt.subplot(313)
    plt.plot(np.arange(len(result)), result)
    # plt.title('Anomaly score')
    plt.xlabel('Index')
    plt.ylabel('Score')
    plt.show()

    # draw_array(loss_list)
    #
    # draw_array(data)
    #
    # draw_array(result)


if __name__ == '__main__':
    # ttest_detector()
    # ttest_detector_on_file()
    ttest_detector_on_file()
