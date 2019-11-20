import sys
import random
import torch
import torch.optim as optim
import os

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

    # train the data for num_epoches epoches
    @BaseDetector.require_initialize
    def train(self, x_train, num_epoches=300, verbose=False, learning_rate=1e-3):
        if self.use_gpu:
            x_train = x_train.cuda()

        print("--------training--------")

        # Begin to train the model
        optimiser = optim.Adam(self.model.parameters(), lr=learning_rate)
        loss_fn = torch.nn.L1Loss()
        for i in range(num_epoches):
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
    def predict(self, x_new):
        print("--------training--------")
        if self.use_gpu:
            x_new = x_new.cuda()

        x_pred = self.model(x_new)

        if self.use_gpu:
            x_pred = x_pred.cpu()

        return x_pred

