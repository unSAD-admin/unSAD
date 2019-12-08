import torch
import glob
import numpy as np
import argparse

import os
import sys
project_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_path)
from utils.data_processor import Normalizer
from common.dataset import SynthDataset, CSVDataset
from autoencoder_detector import AutoEncoderDetector

def _get_file_list():
    if args.absolute_path:
        filename = args.file
    else:
        filename = os.path.join(sys.path[0], args.file)
    if os.path.isdir(filename):
        file_list = glob.glob(filename + "*")
    else:
        file_list = [filename,]
    return file_list

def _organize_data(dataset):
    data_train, data_test = dataset.get_data()
    x_train, y_train = data_train["values"], data_train["label"]
    x_test, y_test = data_test["values"], data_test["label"]
    y_train = y_train.astype(int)
    y_test = y_test.astype(int)
    return x_train, y_train, x_test, y_test

def main():
    file_list = _get_file_list()

    for filename in file_list:
        if args.dataset == "credit":
            dataset = CSVDataset(filename, header=1, timestamp=0, values=tuple(range(1, 30)), label=30,
                                 test_size=args.test_size, shuffle=args.shuffle)
            x_train, y_train, x_test, y_test = _organize_data(dataset)
        else:
            raise ValueError("dataset %s cannot be recognized" % args.dataset)

        normalizer = Normalizer(zero_mean=True)
        x_train_norm = normalizer.process_training_data(x_train)
        x_test_norm = normalizer.process_testing_data(x_test)
        # convert to torch tensor
        x_train_torch = torch.from_numpy(x_train_norm)
        x_test_torch = torch.from_numpy(x_test_norm)

        model = AutoEncoderDetector()
        model.initialize(x_train.shape[1], use_gpu=~args.no_gpu)

        # train the model
        model.train(x_train_torch, num_epochs=args.epochs, verbose=args.verbose)

        # predict the test data
        x_pred_torch = model.predict(x_test_torch)
        x_pred = x_pred_torch.detach().numpy()

        # visualization
        model.visualize(x_test_norm, x_pred, y_test)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train and Test anomaly detection algorithm")
    parser.add_argument('-d', "--dataset", type=str, default='credit')
    parser.add_argument('-a', "--absolute_path", action='store_true', help='Use absolute path')
    parser.add_argument('-f', "--file", type=str, default='', help="path to file or directory")
    parser.add_argument('-t', "--test_size", help="test data percentage", default=0.4)
    parser.add_argument('-v', "--verbose", help="use to print loss", action='store_true')
    parser.add_argument("--epochs", type=int, default=300)
    parser.add_argument("--no_gpu", help="no GPU to run model", action='store_true')
    parser.add_argument("--shuffle", help="use to shuffle the data", action="store_true")
    args = parser.parse_args()
    # start to run
    main()
