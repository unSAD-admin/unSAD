# Created by Xinyu Zhu on 11/19/2019, 4:51 PM
import os, sys
import torch.nn as nn
import torch
import numpy as np

project_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_path)


class AutoEncoder(nn.Module):
    def __init__(self, window_size=2):
        super(AutoEncoder, self).__init__()

        self.window_size = window_size
        # 压缩
        self.encoder = nn.Sequential(
            nn.Linear(self.window_size, 16),
            nn.Tanh(),
            nn.Linear(16, 8),
            nn.ReLU(),
        )
        # 解压
        self.decoder = nn.Sequential(
            nn.Linear(8, 16),
            nn.Tanh(),
            nn.Linear(16, self.window_size),
            nn.ReLU(),

        )

    def forward(self, x):
        encoded = self.encoder(x)
        decoded = self.decoder(encoded)
        return encoded, decoded


autoencoder = AutoEncoder()
learning_rate = 1e-3
optimizer = torch.optim.Adam(autoencoder.parameters(), lr=learning_rate)
loss_func = nn.MSELoss()
EPOCH = 10
train_loader = None
# print(torch.tensor([2,3]))
a = torch.tensor([[[1.1995, -1.3181],
                   [-0.2499, -0.4134]],

                  [[1.1995, -1.3181],
                   [-0.2499, -0.4134]]
                  ])

encoded, decoded = autoencoder(a)
print(encoded, decoded)
loss = loss_func(decoded, a)

print(loss)

from torch.utils.data import DataLoader

loader = DataLoader(torch.tensor([[1.1995, -1.3181],
                     [-0.2499, -0.4134]]), batch_size=2, shuffle=True)

for data in loader:

    print(data)
    encoded, decoded = autoencoder(data)
    print(encoded, decoded)

# #
# for epoch in range(EPOCH):
#     for step, (x, b_label) in enumerate(train_loader):
#         b_x = x.view(-1, 28 * 28)  # batch x, shape (batch, 28*28)
#         b_y = x.view(-1, 28 * 28)  # batch y, shape (batch, 28*28)
#
#         encoded, decoded = autoencoder(b_x)
#
#         loss = loss_func(decoded, b_y)  # mean square error
#         optimizer.zero_grad()  # clear gradients for this training step
#         loss.backward()  # backpropagation, compute gradients
#         optimizer.step()
