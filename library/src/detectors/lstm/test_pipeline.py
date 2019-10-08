
import argparse
import numpy as np
import torch
import matplotlib.pyplot as plt

import sys
sys.path.append("../../")
from utils.normalizer import Normalizer
from dataset import SynthDataset
from detectors.lstm.lstm_detector import LSTMPredAnomalyDetector


parser = argparse.ArgumentParser(description='Train and Test anomaly detection algorithm')
parser.add_argument('--dataset', type=str, default='synth',
                    help='type of dataset to use')
parser.add_argument('--model', type=str, default='lstm-seq2seq')
parser.add_argument('--thresh', type=float, default=0.01)
args = parser.parse_args()

def anomaly_score(a, b):
    return np.linalg.norm(a-b)

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
        model = LSTMPredAnomalyDetector()
        model.initialize(output_size, seq2seq = True)
    else:
        raise ValueError("model %s not recognized" % args.model)
    model.train(x_train_torch.view((1, -1, output_size)), num_epoches=200)

    # put the whole sequence in pred
    x_pred_norm = model.predict(
            torch.cat((x_train_torch, x_test_torch), 0).view((1, -1, output_size)))
    x_pred_norm = x_pred_norm[0, : ,0]
    # convert to numpy
    x_pred_norm = x_pred_norm.numpy()
    # calculate score
    score = anomaly_score(x_pred_norm[-len(x_test_torch):], x_test_norm)
    # de-normalize
    x_pred = normalizer.denorm(x_pred_norm)
    # visualization
    model.visualize(np.concatenate((x_train, x_test), 0), x_pred, score, len(x_train))

if __name__ == "__main__":
    main()
