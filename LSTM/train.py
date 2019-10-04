# reference: https://github.com/jessicayung/blog-code-snippets/blob/master/lstm-pytorch/lstm-baseline.py
import torch
import torch.optim as optim

# Get data, random data for now
import unittest

class Trainer:
    def __init__(self):
        pass
    def train(self, model, x_train, num_epoches = 200):
        # train the model
        # TODO: add non-seq2seq training
        batch_size = 1
        output_size = 1
        learning_rate = 1e-3
        optimiser = optim.Adam(model.parameters(), lr=learning_rate)
        loss_fn = torch.nn.L1Loss()
        for i in range(num_epoches):
            # Zero out gradient,
            optimiser.zero_grad()
            x_pred = model(x_train)
            loss = loss_fn(x_pred, x_train)
            # Backward pass
            loss.backward()
            # Update parameters
            optimiser.step()
    def pred(self, model, x_data, n_preds=None):
        # TODO: add non-seq2seq training
        # seq2seq
        with torch.no_grad():
            x_pred = model(x_data)
            return x_pred
