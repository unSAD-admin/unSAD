import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.autograd import Variable
import numpy as np
import unittest


class ADCNN(nn.Module):  # window size: 25, 35, 45
    def __init__(self, window_size, output_size=1):
        super().__init__()
        #  conv(relu)-maxpool-conv(relu)-maxpool-fc-1
        #  in_channels, out_channels, kernel_size
        self.window_size = window_size
        self.conv1 = nn.Conv1d(1, 32, 3, padding=1)
        # self.bn1 = nn.BatchNorm1d(32)
        self.maxpool1 = nn.MaxPool1d(2)
        self.conv2 = nn.Conv1d(32, 32, 3, padding=1)
        # self.bn2 = nn.BatchNorm2d(32)
        self.maxpool2 = nn.MaxPool1d(2)
        self.fc = nn.Linear(window_size // 4 * 32, output_size)
        self.initialize()

    def forward(self, x):
        x = x.new(x.shape[0], x.shape[2], x.shape[1])
        x = self.conv1(x)
        # x = self.bn1(x)
        x = F.relu(x)
        x = self.maxpool1(x)
        x = self.conv2(x)
        # x = self.bn2(x)
        x = F.relu(x)
        x = self.maxpool2(x)
        x = x.view(x.size(0), -1)
        x = self.fc(x)
        # Sigmoid to avoid explode
        # x = 2 *  torch.sigmoid(x) - 1
        x = torch.clamp(x, -1, 1)
        return x

    def initialize(self):
        for name, param in self.named_parameters():
            if 'bias' in name:
                nn.init.constant_(param, 0.0)
            elif 'weight' in name and param.dim() > 1:
                nn.init.xavier_normal_(param)


class ADLSTM(nn.Module):
    # reference:
    # https://github.com/jessicayung/blog-code-snippets/blob/master/lstm-pytorch/lstm-baseline.py
    def __init__(self, output_size=1, seq2seq=True):
        super().__init__()
        # sequence 2 sequence
        self.seq2seq = seq2seq
        self.hidden_dim = 32
        self.num_layers = 2
        # input dimension is 1
        self.lstm = nn.LSTM(input_size=1, hidden_size=self.hidden_dim,
                            num_layers=self.num_layers, batch_first=True)
        # output dimension is 1
        self.fc = nn.Linear(self.hidden_dim, output_size)
        self.initialize()

    def forward(self, x):
        # TODO: move lstm intialization to a separate function
        h_0 = Variable(torch.zeros(
            self.num_layers, x.size(0), self.hidden_dim))

        c_0 = Variable(torch.zeros(
            self.num_layers, x.size(0), self.hidden_dim))

        if x.is_cuda:
            h_0 = h_0.cuda()
            c_0 = c_0.cuda()
        # Propagate input through LSTM
        ula, (h_out, _) = self.lstm(x, (h_0, c_0))
        # TODO: why it's using hidden feature here:
        # https://github.com/spdin/time-series-prediction-lstm-pytorch/blob/master/Time_Series_Prediction_with_LSTM_Using_PyTorch.ipynb
        # seq2seq model
        # TODO: add maxpooling instead of using hidden layer
        if self.seq2seq:
            out = self.fc(ula)
        else:
            h_out = h_out[-1].view(-1, self.hidden_dim)
            out = self.fc(h_out)
        return out

    def initialize(self):
        for name, param in self.named_parameters():
            if 'bias' in name:
                nn.init.constant_(param, 0.0)
            elif 'weight' in name:
                nn.init.xavier_normal_(param)


class TestCNNDims(unittest.TestCase):
    def test_dims(self):
        batch_size = 11
        for window_size in [25, 35, 45]:
            for output_size in [1, 10, 100]:
                adcnn = ADCNN(window_size, output_size)
                # 3d input
                x = np.ones([batch_size, window_size, 1], dtype=np.float32)
                x = torch.FloatTensor(torch.from_numpy(x))
                y = adcnn(x)
                self.assertEqual(y.shape, torch.Size(
                    [batch_size, output_size]))


class TestLSTMDims(unittest.TestCase):
    def test_dims(self):
        batch_size = 11
        for window_size in [25, 35, 45]:
            for output_size in [1, 10, 100]:
                adlstm = ADLSTM(output_size, seq2seq=False)
                # 3d input
                x = np.ones([batch_size, window_size, 1], dtype=np.float32)
                x = torch.FloatTensor(torch.from_numpy(x))
                y = adlstm(x)
                self.assertEqual(y.shape, torch.Size(
                    [batch_size, output_size]))

    def test_dims_seq2seq(self):
        batch_size = 11
        for window_size in [25, 35, 45]:
            for output_size in [1, 10, 100]:
                adlstm = ADLSTM(output_size, seq2seq=True)
                # 3d input
                x = np.ones([batch_size, window_size, 1], dtype=np.float32)
                x = torch.FloatTensor(torch.from_numpy(x))
                y = adlstm(x)
                self.assertEqual(y.shape, torch.Size(
                    [batch_size, window_size, output_size]))


if __name__ == "__main__":
    unittest.main()
