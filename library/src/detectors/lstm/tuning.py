import numpy as np
import argparse
from sklearn.metrics import f1_score, confusion_matrix
parser = argparse.ArgumentParser(
        description='Train and Test anomaly detection algorithm')
parser.add_argument('--save_dir', type=str, default='', required=True,
        help = 'seed for numpy and torch to maintain reproducibility')
args = parser.parse_args()

total_val_score =  np.load(args.save_dir + "/total_val_score.npy")
total_test_score = np.load(args.save_dir + "/total_test_score.npy")
total_y_val = np.load(args.save_dir + "/total_y_val.npy")
total_y_test = np.load(args.save_dir + "/total_y_test.npy")

f1_val_list = []
f1_test_list = []
thresh_list = [a/10. for a in list(range(0, 20, 1))]
for thresh in thresh_list:
    tn, fp, fn, tp = confusion_matrix(total_y_val,
            (total_val_score < thresh).astype(int), labels=[0,1]).ravel()
    f1_val = f1_score((total_val_score < thresh).astype(int), total_y_val, pos_label=1)
    f1_test = f1_score((total_test_score < thresh).astype(int), total_y_test, pos_label=1)
    f1_val_list.append(f1_val)
    f1_test_list.append(f1_test)

# import pdb;pdb.set_trace()
import matplotlib.pyplot as plt
plt.plot(thresh_list, f1_val_list)
plt.show()
