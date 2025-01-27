import torch
import torch.nn as nn
import numpy as np
import unittest


class AutoEncoder(nn.Module):
    def __init__(self, num_attributes):
        super(AutoEncoder, self).__init__()
        # The structure of this model is suggested by
        # online document
        self.encode = nn.Sequential(
            nn.Linear(num_attributes, 16),
            nn.Tanh(),
            nn.Linear(16, 8),
            nn.ReLU()
        )
        self.decode = nn.Sequential(
            nn.Linear(8, 16),
            nn.Tanh(),
            nn.Linear(16, num_attributes),
            nn.ReLU()
        )

    def forward(self, x):
        x = self.encode(x)
        x = self.decode(x)
        return x


class AutoEncoder2(nn.Module):
    def __init__(self, num_attributes):
        super(AutoEncoder, self).__init__()
        # The structure of this model is suggested by
        # online video https://www.youtube.com/watch?v=V0r2zDhdi6c
        self.encode = nn.Sequential(
            nn.Linear(num_attributes, num_attributes // 2),
            nn.ReLU(),
            nn.Linear(num_attributes // 2, num_attributes // 4),
            nn.ReLU()
        )
        self.decode = nn.Sequential(
            nn.Linear(num_attributes // 4, num_attributes // 2),
            nn.ReLU(),
            nn.Linear(num_attributes // 2, num_attributes),
            nn.ReLU()
        )

    def forward(self, x):
        x = self.encode(x)
        x = self.decode(x)
        return x


class TestAutoEncoder(unittest.TestCase):
    def test_dims(self):
        batch_size = 10
        for num_attributes in [25, 35, 45]:
            auto_encoder = AutoEncoder(num_attributes)
            x = np.ones([batch_size, num_attributes], dtype=np.float32)
            x = torch.FloatTensor(torch.from_numpy(x))
            y = auto_encoder(x)
            self.assertEqual(y.shape, torch.Size([batch_size, num_attributes]))


if __name__ == "__main__":
    unittest.main()
