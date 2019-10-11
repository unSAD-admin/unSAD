
import glob
import argparse
import numpy as np
import random
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
parser.add_argument('--seed', type=int, default=1234,
        help = 'seed for numpy and torch to maintain reproducibility')
parser.add_argument('--dataset', type=str, default='synth',
        choices=['synth','yahoo', 'nab'], help='type of dataset to use')
parser.add_argument('--file_prefix', type=str, default='',
        help='filepath for the data file')
parser.add_argument('--model', type=str, default='lstm', choices=['lstm','cnn'])
parser.add_argument('--epoches', type=int, default=300)
parser.add_argument('--thresh', type=float, default=0.25)
parser.add_argument('--validate', help='Test on Validation set', action='store_true')
parser.add_argument('--no_gpu', help='Test on Validation set', action='store_false')
parser.add_argument('--test_size', help='test data percentage', default=0.4)
parser.add_argument('--val_size',
        help='validation data percentage in total training data', default=0.1)
parser.add_argument('--window_size',
        help='percentage of data to ignore in calculating the loss', default=45)
parser.add_argument('--seq2seq', help='use sequence to sequence model',
        action='store_true')
parser.add_argument('--verbose', help='use to print loss', action='store_true')
parser.add_argument('--save_dir', type=str, default='results',
    help='directory to save file')
args = parser.parse_args()
if args.model == 'cnn' and args.seq2seq:
    args.seq2seq = False
    print("WARNING: cnn must be non-seq2seq")

def anomaly_score(a, b):
    return np.abs(a-b)

def main():
    # reproducibility
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    random.seed(args.seed)

    # conf_mat_list = []
    val_score_list = []
    test_score_list = []
    y_val_list = []
    y_test_list = []
    if args.dataset == "synth":
        # This is a hack, only one data file
        file_list = [""]
    elif args.dataset == 'yahoo' or args.dataset == 'nab':
        file_list = glob.glob(args.file_prefix+"*")
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
            y_train = y_train.astype(int)
            y_test = y_test.astype(int)
        elif args.dataset == 'nab':
            dataset = CSVDataset(filename, timestamp=0, values=1, label=2,
                    test_size=args.test_size)
            data_train, data_test = dataset.getData()
            x_train, y_train = data_train["values"], data_train["label"]
            x_test, y_test = data_test["values"], data_test["label"]
            y_train = y_train.astype(int)
            y_test = y_test.astype(int)
        else:
            raise ValueError("dataset %s not recognized" % args.dataset)
        normalizer = Normalizer(zero_mean=True)
        x_train_norm = normalizer.processTrainingData(x_train)
        x_test_norm = normalizer.processTestingData(x_test)
        # train, val split
        if args.validate:
            x_train_norm, x_val_norm, y_train, y_val = train_test_split(x_train_norm, y_train,
                test_size=args.val_size, shuffle=False)
            x_val_torch = torch.from_numpy(x_val_norm)
        # convert to torch tensor
        x_train_torch = torch.from_numpy(x_train_norm)
        x_test_torch = torch.from_numpy(x_test_norm)
        output_size = 1
        if args.model in ['lstm', 'cnn']:
            model = LSTMPredAnomalyDetector()
            model.initialize(output_size, seq2seq = args.seq2seq,
                    use_gpu=args.no_gpu, window_size=args.window_size, model=args.model)
        else:
            raise ValueError("model %s not recognized" % args.model)

        # train the model
        model.train(x_train_torch.view((1, -1, output_size)),
                num_epoches=args.epoches, verbose=args.verbose)

        # put the whole sequence in pred
        if args.validate:
            x_total = torch.cat((x_train_torch, x_val_torch, x_test_torch), 0)
        else:
            x_total = torch.cat((x_train_torch, x_test_torch), 0)
        # predict
        x_pred_norm = model.predict(x_total.view((1, -1, output_size)), start=x_train_torch.shape[0])
        x_pred_norm = x_pred_norm[0, : ,0]
        # convert to numpy
        x_pred_norm = x_pred_norm.numpy()
        # calculate score
        test_score = anomaly_score(x_pred_norm[-len(x_test_torch):], x_test_norm)
        if args.validate:
            val_score = anomaly_score(
                x_pred_norm[len(x_train_torch):len(x_train_torch)+len(x_val_torch)], x_val_norm)
            test_score = anomaly_score(
                x_pred_norm[-len(x_test_torch):], x_test_norm)
            # conf_mat = confusion_matrix((score < args.thresh).astype(int),
            #         y_val, labels=[0,1]).ravel()
            # conf_mat_list.append(conf_mat)
            val_score_list.append(val_score)
            test_score_list.append(test_score)
            y_val_list.append(y_val)
            y_test_list.append(y_test)
        else:
            # if there is label
            # try:
            #     conf_mat = confusion_matrix((score < args.thresh).astype(int),
            #             y_test, labels=[0,1]).ravel()
            #     conf_mat_list.append(conf_mat)
            # except NameError:
            #     pass
            # de-normalize
            x_pred = normalizer.recoverData(x_pred_norm)
            # visualization
            model.visualize(np.concatenate((x_train, x_test), 0), x_pred, test_score, len(x_train))
    # rate_list = []
    # for i in range(4):
    #     rate = sum([a[i] for a in conf_mat_list])
    #     rate_list.append(rate)
    # print("confusion matrix(tn, fp, fn, tp): ", rate_list)
    if args.validate:
        total_val_score = np.concatenate(tuple(val_score_list), 0)
        total_test_score = np.concatenate(tuple(test_score_list), 0)
        total_y_val = np.concatenate(tuple(y_val_list), 0)
        total_y_test = np.concatenate(tuple(y_test_list), 0)
        import os
        if not os.path.exists(args.save_dir):
            os.makedirs(args.save_dir)
        np.save(args.save_dir + "/total_val_score", total_val_score)
        np.save(args.save_dir + "/total_test_score", total_test_score)
        np.save(args.save_dir + "/total_y_val", total_y_val)
        np.save(args.save_dir + "/total_y_test", total_y_test)

    # Do something with confusion matrix
if __name__ == "__main__":
    main()
