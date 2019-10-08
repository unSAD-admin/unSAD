import sys
import torch
import torch.optim as optim
import matplotlib.pyplot as plt

sys.path.append("../../")
from detectors.base import BaseDetector
from utils.normalizer import Normalizer
from model import ADLSTM

class LSTMAnomalyDetector(BaseDetector):

    def __init__(self, timestamp_col_name=None, value_col_name=None):
        if timestamp_col_name is None:  # since timestamp column name is essential for super class
            timestamp_col_name = "timestamp"

        super(LSTMAnomalyDetector, self).__init__(timestamp_col_name=timestamp_col_name,
                                                  measure_col_names=[value_col_name], symbolic=False)

    def initialize(self, output_size=1, seq2seq=True):
        self.model = ADLSTM(output_size, seq2seq=seq2seq)

    def train(self, x_train, num_epoches=200):
        # train the model
        # TODO: add non-seq2seq training
        print("--------training--------")
        batch_size = 1
        output_size = 1
        learning_rate = 1e-3
        optimiser = optim.Adam(self.model.parameters(), lr=learning_rate)
        loss_fn = torch.nn.L1Loss()
        for i in range(num_epoches):
            # Zero out gradient,
            optimiser.zero_grad()
            x_pred = self.model(x_train)
            loss = loss_fn(x_pred, x_train)
            # TODO: what is the loss for ocnn
            # Backward pass
            loss.backward()
            # Update parameters
            optimiser.step()

    def predict(self, x_new, n_preds=None):
        # TODO: add non-seq2seq training
        # seq2seq
        print("--------prediction--------")
        with torch.no_grad():
            x_pred = self.model(x_new)
            return x_pred
    def visualize(self, x_train, x_pred, score, len_train):
        #####################
        # Plot preds and performance
        #####################
        # TODO: add plot for train, test, score, pred
        plt.plot(x_train, label="Data")
        plt.plot(x_pred, label="Preds")
        plt.axvline(x=len_train, c='r', linestyle='--')
        plt.legend()
        plt.show()

        # TODO: plot training loss
        # plt.plot(hist, label="Training loss")
        # plt.legend()
        # plt.show()
