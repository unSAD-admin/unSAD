import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.autograd import Variable
import numpy as np
import unittest

class AutoEncoder(nn.Module):  # 16 8
    def __init__(self, num_attributes):
        super(AutoEncoder, self).__init__()
        self.encode = nn.Sequential(
            nn.Linear(num_attributes, 16),
            nn.Tanh(True),
            nn.Linear(16, 8),
            nn.ReLU(True)
        )
        self.decode = nn.Sequential(
            nn.Linear(8, 16),
            nn.Tanh(True),
            nn.Linear(16, num_attributes),
            nn.ReLU(True)
        )

    def forward(self, x):
        x = self.encode(x)
        x = self.decode(x)
        return x
