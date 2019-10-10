
import glob
import argparse
import numpy as np
import torch
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix

import sys
sys.path.append("../../")
from utils.data_processor import Normalizer
from common.dataset import SynthDataset, CSVDataset
from detectors.lstm.lstm_detector import LSTMPredAnomalyDetector


parser = argparse.ArgumentParser(
        description='Train and Test anomaly detection algorithm')
parser.add_argument('--dataset', type=str, default='synth',
        choices=['synth','yahoo'], help='type of dataset to use')
parser.add_argument('--filepath', type=str, default='',
        help='filepath for the data file')
parser.add_argument('--model', type=str, default='lstm-seq2seq')
parser.add_argument('--epoches', type=int, default=200)
parser.add_argument('--thresh', type=float, default=0.25)
parser.add_argument('--validate', help='Test on Validation set', action='store_true')
parser.add_argument('--test_size', help='test data percentage', default=0.4)
parser.add_argument('--val_size',
        help='validation data percentage in total training data', default=0.1)
parser.add_argument('--window_size',
        help='percentage of data to ignore in calculating the loss', default=45)
args = parser.parse_args()

def anomaly_score(a, b):
    return np.abs(a-b)

def main():
    conf_mat_list = []
    if args.dataset == "synth":
        # This is a hack, only one data file
        file_list = [""]
    elif args.dataset == 'yahoo':
        file_list = glob.glob(args.filepath)
    else:
        raise ValueError("dataset %s not recognized" % args.dataset)
    for filename in file_list:
        if args.dataset == "synth":
            dataset = SynthDataset()
            x_train, x_test = dataset.getData()
        elif args.dataset == 'yahoo':
            dataset = CSVDataset(filename, header = 1, values = 1, label = 2,
                    timestamp = 0, test_size=args.test_size)
            data_train, data_test = dataset.getData()
            x_train, y_train = data_train["values"], data_train["label"]
            x_test, y_test = data_test["values"], data_test["label"]
        else:
            raise ValueError("dataset %s not recognized" % args.dataset)
        normalizer = Normalizer()
        x_train_norm = normalizer.processTrainingData(x_train)
        x_test_norm = normalizer.processTestingData(x_test)
        # train, val split
        if args.validate:
            x_train_norm, x_val_norm, y_train, y_val = train_test_split(x_train, y_train,
                test_size=args.val_size, shuffle=False)
            x_val_torch = torch.from_numpy(x_val_norm)
        # convert to torch tensor
        x_train_torch = torch.from_numpy(x_train_norm)
        x_test_torch = torch.from_numpy(x_test_norm)
        output_size = 1
        if args.model == 'lstm-seq2seq':
            model = LSTMPredAnomalyDetector()
            model.initialize(output_size, seq2seq = True)
        else:
            raise ValueError("model %s not recognized" % args.model)

        # train the model
        model.train(x_train_torch.view((1, -1, output_size)),
                num_epoches=args.epoches, ignore_size=args.window_size)

        # put the whole sequence in pred
        if args.validate:
            x_total = torch.cat((x_train_torch, x_val_torch, x_test_torch), 0)
        else:
            x_total = torch.cat((x_train_torch, x_test_torch), 0)
        # predict
        x_pred_norm = model.predict(x_total.view((1, -1, output_size)))
        x_pred_norm = x_pred_norm[0, : ,0]
        # convert to numpy
        x_pred_norm = x_pred_norm.numpy()
        # calculate score
        if args.validate:
            score = anomaly_score(
                x_pred_norm[len(x_train_torch):len(x_train_torch)+len(x_val_torch)], x_val_norm)
        else:
            score = anomaly_score(x_pred_norm[-len(x_test_torch):], x_test_norm)
        if args.validate:
            conf_mat = confusion_matrix((score > args.thresh).astype(int),
                    y_val.astype('int'), labels=[0,1]).ravel()
            conf_mat_list.append(conf_mat)
        else:
            # de-normalize
            x_pred = normalizer.recoverData(x_pred_norm)
            # visualization
            model.visualize(np.concatenate((x_train, x_test), 0), x_pred, score, len(x_train))
    rate_list = []
    for i in range(4):
        rate = sum([a[i] for a in conf_mat_list])
        rate_list.append(rate)
    print("confusion matrix(tn, fp, fn, tp): ", rate_list)
    # Do something with confusion matrix
if __name__ == "__main__":
    main()
