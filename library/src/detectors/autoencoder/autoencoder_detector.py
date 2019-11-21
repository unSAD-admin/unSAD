import sys
import random
import torch
import torch.optim as optim
import os
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import unittest

project_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_path)
from detectors.base import BaseDetector
from model import AutoEncoder

class AutoEncoderDetector(BaseDetector):
    def __init__(self, timestamp_col_name=None, value_col_name=None):
        if timestamp_col_name is None:  # since timestamp column name is essential for super class
            timestamp_col_name = "timestamp"

        super(
            AutoEncoderDetector,
            self).__init__(
            timestamp_col_name=timestamp_col_name,
            measure_col_names=[value_col_name],
            symbolic=False)

    def initialize(self, num_attributes, use_gpu=True):
        super(AutoEncoderDetector, self).initialize()

        self.use_gpu = use_gpu and torch.cuda.is_available()
        self.model = AutoEncoder(num_attributes)

        if self.use_gpu:
            self.model.cuda()

    # train the data for num_epoches epochs
    @BaseDetector.require_initialize
    def train(self, x_train, num_epochs=300, verbose=False, learning_rate=1e-3):
        if self.use_gpu:
            x_train = x_train.cuda()

        print("--------training--------")

        # Begin to train the model
        optimiser = optim.Adam(self.model.parameters(), lr=learning_rate)
        loss_fn = torch.nn.L1Loss()
        for i in range(num_epochs):
            # ---------Forward-----------
            x_pred = self.model(x_train)
            loss = loss_fn(x_pred, x_train)
            if verbose:
                print("epoch: %d, loss: " % i, loss.item())

            # ---------Backward----------
            optimiser.zero_grad()
            loss.backward()
            optimiser.step()

    @BaseDetector.require_initialize
    def predict(self, x_test):
        print("--------training--------")
        if self.use_gpu:
            x_new = x_test.cuda()
        else:
            x_new = x_test

        x_pred = self.model(x_new)

        if self.use_gpu:
            x_pred = x_pred.cpu()

        return x_pred

    def visualize(self, x_new, x_pred, y_label):
        colors = ['dodgerblue', 'coral']
        markers = ['o', '^']
        # calculate MSE, MAE
        mse = np.mean(np.power(x_new - x_pred, 2), axis=1)
        mae = np.mean(np.abs(x_new - x_pred), axis=1)
        index = np.arange(len(mse))
        # plot
        plt.figure(figsize=(14, 5))
        plt.subplot(121)
        plt.scatter(index, mse, c=y_label, cmap=matplotlib.colors.ListedColormap(colors))
        plt.title('MSE for normal and abnormal data')
        plt.xlabel('Index')
        plt.ylabel('MSE')

        plt.subplot(122)
        plt.scatter(index, mae, c=y_label, cmap=matplotlib.colors.ListedColormap(colors))
        plt.title('MAE for normal and abnormal data')
        plt.xlabel('Index')
        plt.ylabel('MAE')
        plt.show()


class TestAutoEncoderDetector(unittest.TestCase):
    def test_vis(self):
        x_new = np.array([1,2,3,3,2,6,2,3,7,1,2])
        x_new = x_new.reshape((len(x_new), 1))
        x_pred = np.array([2,2,3,4,2,3,2,2,3,1,2])
        x_pred = x_pred.reshape((len(x_pred), 1))
        y_label = np.array([0,0,0,0,0,1,0,0,1,0,0])
        detector = AutoEncoderDetector()
        detector.visualize(x_new, x_pred, y_label)

if __name__ == '__main__':
    unittest.main()
