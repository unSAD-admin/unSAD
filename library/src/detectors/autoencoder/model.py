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
            nn.Tanh(),
            nn.Linear(16, 8),
            nn.ReLU(True)
        )
        self.decode = nn.Sequential(
            nn.Linear(8, 16),
            nn.Tanh(),
            nn.Linear(16, num_attributes),
            nn.ReLU(True)
        )

    def forward(self, x):
        x = self.encode(x)
        x = self.decode(x)
        return x


class TestAutoEncoder(unittest.TestCase):
    def test_dims(self):
        batch_size = 10
        for num_attributes in  [25, 35, 45]:
            auto_encoder = AutoEncoder(num_attributes)
            x = np.ones([batch_size, num_attributes], dtype=np.float32)
            x = torch.FloatTensor(torch.from_numpy(x))
            y = auto_encoder(x)
            self.assertEqual(y.shape, torch.Size([batch_size, num_attributes]))


if __name__ == "__main__":
    unittest.main()
