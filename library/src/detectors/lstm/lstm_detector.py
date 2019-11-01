import sys
import random
import torch
import torch.optim as optim

sys.path.append("../../")
from model import ADLSTM, ADCNN
from detectors.base import BaseDetector


class LSTMPredAnomalyDetector(BaseDetector):
    def __init__(self, timestamp_col_name=None, value_col_name=None):
        if timestamp_col_name is None:  # since timestamp column name is essential for super class
            timestamp_col_name = "timestamp"

        super(
            LSTMPredAnomalyDetector,
            self).__init__(
            timestamp_col_name=timestamp_col_name,
            measure_col_names=[value_col_name],
            symbolic=False)

    def initialize(
            self,
            output_size=1,
            seq2seq=True,
            use_gpu=True,
            model='lstm',
            window_size=0):
        self.window_size = window_size
        self.use_gpu = use_gpu and torch.cuda.is_available()
        self.seq2seq = seq2seq

        super(LSTMPredAnomalyDetector, self).initialize()

        # init model
        if model == 'lstm':
            self.model = ADLSTM(output_size, seq2seq=self.seq2seq)
        else:
            self.model = ADCNN(
                window_size=self.window_size,
                output_size=output_size)
        if self.use_gpu:
            self.model.cuda()

    # train the data for num_epoches epoches
    @BaseDetector.require_initialize
    def train(self, x_train, num_epoches=300, verbose=False):
        # train the model
        # TODO: add non-seq2seq training
        if self.use_gpu:
            x_train = x_train.cuda()
        print("--------training--------")
        if self.seq2seq:
            self.train_seq2seq(x_train, num_epoches, verbose=verbose)
        else:
            self.train_nonseq2seq(x_train, num_epoches, verbose=verbose)

    @BaseDetector.require_initialize
    def train_seq2seq(self, x_train, num_epochs=300, verbose=False):
        learning_rate = 1e-3
        optimiser = optim.Adam(self.model.parameters(), lr=learning_rate)
        loss_fn = torch.nn.L1Loss()
        for i in range(num_epochs):
            # Zero out gradient,
            optimiser.zero_grad()
            x_pred = self.model(x_train)
            loss = loss_fn(x_pred[:, self.window_size:, ],
                           x_train[:, self.window_size:, ])
            # TODO: what is the loss for ocnn
            # Backward pass
            if verbose:
                print("loss:\t", loss.item())
            loss.backward()
            # Update parameters
            optimiser.step()

    @BaseDetector.require_initialize
    def train_nonseq2seq(
            self,
            x_train,
            num_epoches=300,
            batch_size=160,
            verbose=False):
        # make sure it's one sequence
        learning_rate = 1e-3
        assert(x_train.shape[0] == 1)
        x_train = x_train[0, :, :]

        # legnth of the sequence
        length = x_train.shape[0]
        assert(length > self.window_size)

        optimizer = optim.Adam(self.model.parameters(), lr=learning_rate)
        loss_fn = torch.nn.L1Loss()
        # NOTE: set batch size as sequence size
        for i in range(num_epoches):
            for ite in range(len(x_train) // batch_size):
                # sample index
                # Zero out gradient,
                optimizer.zero_grad()

                y_test_list = []
                x_data_list = []
                for _ in range(batch_size):
                    index = random.randint(self.window_size, length - 1)
                    y_test = x_train[index, :]
                    x_data = x_train[index - self.window_size:index, :]
                    y_test_list.append(y_test)
                    x_data_list.append(x_data)
                y_test = torch.stack(y_test_list, 0)
                x_data = torch.stack(x_data_list, 0)

                y_pred = self.model(x_data)
                loss = loss_fn(y_pred, y_test)
                if verbose:
                    print("loss:\t", loss.item())
                # Backward pass
                loss.backward()
                # Update parameters
                optimizer.step()

    @BaseDetector.require_initialize
    def predict(self, x_new, start=None):
        print("--------prediction--------")
        if self.use_gpu:
            x_new = x_new.cuda()
        if self.seq2seq:
            x_pred = self.predict_seq2seq(x_new)
        else:
            x_pred = self.predict_nonseq2seq(x_new, start)
        if self.use_gpu:
            x_pred = x_pred.cpu()
        return x_pred

    @BaseDetector.require_initialize
    def predict_seq2seq(self, x_new):
        with torch.no_grad():
            x_pred = self.model(x_new)
        return x_pred

    @BaseDetector.require_initialize
    def predict_nonseq2seq(self, x_new, start=None):
        # seq2seq
        assert(x_new.shape[0] == 1)
        x_new = x_new[0, :, :]
        x_data_list = []
        for index in range(start, x_new.shape[0]):
            x_data = x_new[index - self.window_size: index, :]
            x_data_list.append(x_data)
        x_data = torch.stack(x_data_list, 0)

        with torch.no_grad():
            x_pred = self.model(x_data)
        return torch.cat((x_new[:start, ], x_pred), 0).unsqueeze(0)

    # TODO: put this in base detector
    def visualize(self, x_train, x_pred, score, y_label, len_train):
        #####################
        # Plot preds and performance
        #####################
        # TODO: add plot for train, test, score, pred
        import matplotlib.pyplot as plt
        # import numpy as np
        # x_pred = np.load("x_pred.npy")
        plt.plot(x_train, label="Data")
        plt.plot(x_pred, label="Preds")
        plt.axvline(x=len_train, c='r', linestyle='--')
        x_list = []
        y_list = []
        for index, value in enumerate(list(y_label)):
            if value == 1:
                x_list.append(index)
                y_list.append(x_train[index])
        plt.plot(x_list, y_list, 'ro')
        plt.legend()
        plt.show()

        # TODO: plot training loss
        # plt.plot(hist, label="Training loss")
        # plt.legend()
        # plt.show()
