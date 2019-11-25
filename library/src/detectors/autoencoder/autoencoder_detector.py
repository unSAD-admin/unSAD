import sys
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
from detectors.autoencoder.model import AutoEncoder
from common.k_mean_cluster import KMeanTools


class AutoEncoderDetector(BaseDetector):
    def __init__(self):

        super(
            AutoEncoderDetector,
            self).__init__(
            timestamp_col_name=None,
            measure_col_names=None,
            symbolic=False)

    def initialize(self, num_attributes, use_gpu=True):
        super(AutoEncoderDetector, self).initialize()

        self.use_gpu = use_gpu and torch.cuda.is_available()
        self.model = AutoEncoder(num_attributes)
        self.avg_distance = 0
        self.std_distance = 1

        if self.use_gpu:
            self.model.cuda()

    # train the data for num_epoches epochs
    @BaseDetector.require_initialize
    def train(self, x_train, num_epochs=300, verbose=False, learning_rate=1e-3):
        if self.use_gpu:
            x_train = x_train.cuda()

        loss_list = []

        # Begin to train the model
        optimiser = optim.Adam(self.model.parameters(), lr=learning_rate)
        loss_fn = torch.nn.L1Loss()
        for i in range(num_epochs):
            # ---------Forward-----------
            x_pred = self.model(x_train)
            loss = loss_fn(x_pred, x_train)
            if verbose:
                print("epoch: %d, loss: " % i, loss.item())
            loss_list.append(loss.item())

            # ---------Backward----------
            optimiser.zero_grad()
            loss.backward()
            optimiser.step()

        # after training finish, we need the average distance on
        # the training sample to normalize
        # the later distance calculation
        x_pred = self.predict(x_train)
        all_distance = np.mean(np.power(x_train.cpu().detach().numpy() - x_pred.detach().numpy(), 2), axis=1)
        self.avg_distance = np.mean(all_distance)
        self.std_distance = np.std(all_distance)
        return loss_list
        # self.avg_distance = np.mean(np.mean(np.abs(x_train - x_pred), axis=1))

    @BaseDetector.require_initialize
    def predict(self, x_test):
        if self.use_gpu:
            x_new = x_test.cuda()
        else:
            x_new = x_test

        x_pred = self.model(x_new)

        if self.use_gpu:
            x_pred = x_pred.cpu()

        return x_pred

    @BaseDetector.require_initialize
    def handle_record(self, record):
        """
        :param record: [v1, v2, v3, ...]
        :return: anomaly score
        """
        record = torch.from_numpy(np.array([record], dtype="float32"))
        x_pred = self.predict(record)
        distance = np.mean(np.power(record.detach().numpy() - x_pred.detach().numpy(), 2))
        # may consider using mae distance
        # distance = np.sum(np.abs(record.detach().numpy() - x_pred.detach().numpy()))
        return abs((distance - self.avg_distance) / self.std_distance)

    @BaseDetector.require_initialize
    def handle_record_sequence(self, record_sequence):
        record_sequence = torch.from_numpy(np.array(record_sequence, dtype="float32"))
        x_pred = self.predict(record_sequence)
        distance = np.mean(np.power(record_sequence.detach().numpy() - x_pred.detach().numpy(), 2), axis=1)
        result = np.abs((distance - self.avg_distance) / self.std_distance)
        return result

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


class AutoEncoderDetectorForest(BaseDetector):
    def __init__(self):
        super(
            AutoEncoderDetectorForest,
            self).__init__(
            timestamp_col_name=None,
            measure_col_names=None,
            symbolic=False)

    def initialize(self, num_attributes, cluster_num, use_gpu=True):
        super(AutoEncoderDetectorForest, self).initialize()

        self.cluster_num = cluster_num
        self.autoEncoders = []
        self.clusters = []
        for i in range(cluster_num):
            self.autoEncoders.append(AutoEncoderDetector())
            self.autoEncoders[-1].initialize(num_attributes=num_attributes, use_gpu=use_gpu)

    @BaseDetector.require_initialize
    def train(self, x_train, num_epochs=300, verbose=False, learning_rate=1e-3):
        self.kmean = KMeanTools(x_train.numpy(), self.cluster_num)
        result = []
        training_data = self.kmean.get_clustered_data()
        for i, data_cluster in enumerate(training_data):
            result.append(self.autoEncoders[i].train(torch.from_numpy(np.array(data_cluster, dtype="float32")),
                                                     num_epochs, verbose, learning_rate))
        return result

    @BaseDetector.require_initialize
    def predict(self, x_test):
        encoder = self.autoEncoders[self.kmean.predict(x_test.numpy())]
        return encoder.predict(x_test)

    @BaseDetector.require_initialize
    def handle_record(self, record):
        """
        :param record: [v1, v2, v3, ...]
        :return: anomaly score
        """
        encoder = self.autoEncoders[self.kmean.predict(record)]
        return encoder.handle_record(record)


class TestAutoEncoderDetector(unittest.TestCase):
    def test_vis(self):
        x_new = np.array([1, 2, 3, 3, 2, 6, 2, 3, 7, 1, 2])
        x_new = x_new.reshape((len(x_new), 1))
        x_pred = np.array([2, 2, 3, 4, 2, 3, 2, 2, 3, 1, 2])
        x_pred = x_pred.reshape((len(x_pred), 1))
        y_label = np.array([0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0])
        detector = AutoEncoderDetector()
        detector.visualize(x_new, x_pred, y_label)


if __name__ == '__main__':
    unittest.main()
