# Created by Yash Shahani on 11/19/2019, 6:00 PM

from __future__ import division
from __future__ import print_function

import sys
import os
import numpy as np
from sklearn.model_selection import train_test_split
from scipy.io import loadmat
from pyod.utils.utility import standardizer

project_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(project_path)

from detectors.iforest.iforest_detector import IforestAnomalyDetecor

# define the number of iterations
n_ite = 10

data_file = '{0}/data/wbc'.format(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
mat = loadmat(data_file)

X = mat['X']
y = mat['y'].ravel()
outliers_fraction = np.count_nonzero(y) / len(y)
outliers_percentage = round(outliers_fraction * 100, ndigits=4)

# 60% data for training and 40% for testing
random_state = np.random.RandomState(1)
X_train, X_test, y_train, y_test = \
            train_test_split(X, y, test_size=0.4, random_state=random_state)

# standardizing data for processing
X_train_norm, X_test_norm = standardizer(X_train, X_test)

def test_detector():
    detector = IforestAnomalyDetecor()
    detector.initialize(n_estimators=100,
            max_samples="auto",
            contamination=0.1,
            max_features=1.,
            bootstrap=False,
            n_jobs=1,
            behaviour='old',
            random_state=None,
            verbose=0)

def test_train():
    print("Testing Train")
    detector = IforestAnomalyDetecor()
    detector.initialize()
    result = detector.train(X_train_norm, y_train)
    print result

def test_handle_record():
    print("Testing Handle Record")
    detector = IforestAnomalyDetecor()
    detector.initialize()
    detector.train(X_train_norm, y_train)
    result = detector.handle_record(X_test)
    for x,y in zip(result,y_test):
        print(x,y)


if __name__ == "__main__":
    test_detector()
    test_train()
    test_handle_record()
    print(data_file)