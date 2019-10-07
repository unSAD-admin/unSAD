from dataset import SynthDataset
from model import ADLSTM
from train import Trainer
import argparse
import numpy as np
import torch
import matplotlib.pyplot as plt

# Normalize to 0-1
# Format:numpy array
# NOTE: only work for 1D data
class Normalizer:
    def __init__(self):
        pass
    def getNorm(self, x_train):
        self.max = np.max(x_train)
        self.min = np.min(x_train)
        self.gap = self.max - self.min
        return self.norm(x_train)
    def norm(self, data):
        return (data - self.min)/self.gap
    def denorm(self, data):
        return data * self.gap + self.min

parser = argparse.ArgumentParser(description='Train and Test anomaly detection algorithm')
parser.add_argument('--dataset', type=str, default='synth',
                    help='type of dataset to use')
parser.add_argument('--model', type=str, default='lstm-seq2seq')
parser.add_argument('--thresh', type=float, default=0.01)
args = parser.parse_args()

def anomaly_score(a, b):
    return np.linalg.norm(a-b)

def viz(x_train, x_pred, score, len_train):
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

def main():
    if args.dataset == "synth":
        dataset = SynthDataset()
    else:
        raise ValueError("dataset %s not recognized" % args.dataset)
    x_train, x_test = dataset.getData()
    normalizer = Normalizer()
    x_train_norm = normalizer.getNorm(x_train)
    x_test_norm = normalizer.norm(x_test)
    # convert to torch tensor
    x_train_torch = torch.from_numpy(x_train_norm)
    x_test_torch = torch.from_numpy(x_test_norm)
    output_size = 1
    if args.model == 'lstm-seq2seq':
        model = ADLSTM(output_size, seq2seq = True)
    else:
        raise ValueError("model %s not recognized" % args.model)
    trainer = Trainer()
    trainer.train(model, x_train_torch.view((1, -1, output_size)), num_epoches=200)

    # put the whole sequence in pred
    x_pred_norm = trainer.pred(model,
            torch.cat((x_train_torch, x_test_torch), 0).view((1, -1, output_size)))
    x_pred_norm = x_pred_norm[0, : ,0]
    # convert to numpy
    x_pred_norm = x_pred_norm.numpy()
    # calculate score
    score = anomaly_score(x_pred_norm[-len(x_test_torch):], x_test_norm)
    # de-normalize
    x_pred = normalizer.denorm(x_pred_norm)
    # visualization
    viz(np.concatenate((x_train, x_test), 0), x_pred, score, len(x_train))

if __name__ == "__main__":
    main()
