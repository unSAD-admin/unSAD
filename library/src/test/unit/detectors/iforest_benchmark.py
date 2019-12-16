# Created by Yash Shahani on 11/18/2019, 2:03 PM
# Made for easy addition of more algorithms, just follow commented directions at HERE comments
# Prerequisite: Install pyod

from __future__ import division
from __future__ import print_function
from time import time
import sys
import os

# temporary solution for relative imports in case pyod is not installed
# if pyod is installed, no need to use the following line
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname("__file__"), '..')))
# supress warnings for clean output
import warnings

warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from scipy.io import loadmat

# HERE: Import the other models you want to test
from pyod.models.iforest import IForest

from pyod.utils.utility import standardizer
from pyod.utils.utility import precision_n_scores
from sklearn.metrics import roc_auc_score

# Define data file and read X and y
mat_file_list = ['arrhythmia.mat',
                 'cardio.mat',
                 'glass.mat',
                 'ionosphere.mat',
                 'letter.mat',
                 'lympho.mat',
                 'mnist.mat',
                 'musk.mat',
                 'optdigits.mat',
                 'pendigits.mat',
                 'pima.mat',
                 'satellite.mat',
                 'satimage-2.mat',
                 'shuttle.mat',
                 'vertebral.mat',
                 'vowels.mat',
                 'wbc.mat']

# define the number of iterations
# HERE: Change n_classifiers to the number of classifiers you want to benchmark
n_ite = 10
n_classifiers = 1

# HERE: Add additional classifiers as parameters in df_columns
df_columns = ['Data', '#Samples', '#Dimensions', 'Outlier Perc',
              'IForest']

# initialize the container for saving the results
roc_df = pd.DataFrame(columns=df_columns)
prn_df = pd.DataFrame(columns=df_columns)
time_df = pd.DataFrame(columns=df_columns)

for j in range(len(mat_file_list)):

    mat_file = mat_file_list[j]
    data_file = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/data/' + mat_file

    mat = loadmat(data_file)

    X = mat['X']
    y = mat['y'].ravel()
    outliers_fraction = np.count_nonzero(y) / len(y)
    outliers_percentage = round(outliers_fraction * 100, ndigits=4)

    # Construct containers for saving results
    roc_list = [mat_file[:-4], X.shape[0], X.shape[1], outliers_percentage]
    prn_list = [mat_file[:-4], X.shape[0], X.shape[1], outliers_percentage]
    time_list = [mat_file[:-4], X.shape[0], X.shape[1], outliers_percentage]

    roc_mat = np.zeros([n_ite, n_classifiers])
    prn_mat = np.zeros([n_ite, n_classifiers])
    time_mat = np.zeros([n_ite, n_classifiers])

    for i in range(n_ite):
        print("\n... Processing", mat_file, '...', 'Iteration', i + 1)
        random_state = np.random.RandomState(i)

        # 60% data for training and 40% for testing
        X_train, X_test, y_train, y_test = \
            train_test_split(X, y, test_size=0.4, random_state=random_state)

        # Standardizing data for processing
        X_train_norm, X_test_norm = standardizer(X_train, X_test)

        # HERE: Add the other classifiers after Isolation Forest, seperated by commas
        classifiers = {
            'Isolation Forest': IForest(contamination=outliers_fraction,
                                        random_state=random_state),
        }
        # HERE: Give indices to these additional classifiers
        classifiers_indices = {
            'Isolation Forest': 0,
        }

        for clf_name, clf in classifiers.items():
            t0 = time()
            clf.fit(X_train_norm)
            test_scores = clf.decision_function(X_test_norm)
            t1 = time()
            duration = round(t1 - t0, ndigits=4)

            roc = round(roc_auc_score(y_test, test_scores), ndigits=4)
            prn = round(precision_n_scores(y_test, test_scores), ndigits=4)

            print('{clf_name} ROC:{roc}, precision @ rank n:{prn}, '
                  'execution time: {duration}s'.format(
                clf_name=clf_name, roc=roc, prn=prn, duration=duration))

            time_mat[i, classifiers_indices[clf_name]] = duration
            roc_mat[i, classifiers_indices[clf_name]] = roc
            prn_mat[i, classifiers_indices[clf_name]] = prn

    time_list = time_list + np.mean(time_mat, axis=0).tolist()
    temp_df = pd.DataFrame(time_list).transpose()
    temp_df.columns = df_columns
    time_df = pd.concat([time_df, temp_df], axis=0)

    roc_list = roc_list + np.mean(roc_mat, axis=0).tolist()
    temp_df = pd.DataFrame(roc_list).transpose()
    temp_df.columns = df_columns
    roc_df = pd.concat([roc_df, temp_df], axis=0)

    prn_list = prn_list + np.mean(prn_mat, axis=0).tolist()
    temp_df = pd.DataFrame(prn_list).transpose()
    temp_df.columns = df_columns
    prn_df = pd.concat([prn_df, temp_df], axis=0)

    # Save the results for each run
    time_df.to_csv('time.csv', index=False, float_format='%.3f')
    roc_df.to_csv('roc.csv', index=False, float_format='%.3f')
    prn_df.to_csv('prc.csv', index=False, float_format='%.3f')
