import os
import sys

import torch

project_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_path)

from detectors.autoencoder.autoencoder_detector import AutoEncoderDetector


def test_detector():
    detector = AutoEncoderDetector()

    # tell the detector, each input record is of length 2
    detector.initialize(2)

    # training the data with some size 2 records
    x_train = torch.tensor([[1.0, 2.0], [2.0, 3.0], [4.0, 5.0]])

    # set epochs number to 3000, show the loss value during training
    detector.train(x_train, num_epochs=1, verbose=True)

    # predict the result, you don't need a prediction if you just the anomaly score
    x_pred = detector.predict(x_train)
    print(detector.predict(torch.tensor([[1.0, 2.0], [2, 3]])))

    # get an anomaly score of a new single record
    print(detector.handle_record([1.0, 2.0]))

    print(detector.handle_record_sequence([[1, 2], [2, 3]]))


if __name__ == '__main__':
    test_detector()
