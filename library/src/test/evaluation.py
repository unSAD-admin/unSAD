import sys
import os
import json
import datetime
import csv
import time

def writecsv(file,filename):
    csvfile = open(filename, 'w')
    writer = csv.writer(csvfile,lineterminator='\n')
    for line in file:
        writer.writerow(line)
    csvfile.close()

def expriment_window(path):
    files = {}
    output = []
    for dirpath, dirnames, filenames in os.walk(path):

        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            if filename == 'all_res.csv':
                continue
            data = []

            with open(filepath, newline='') as f:
                reader = csv.reader(f)
                for idx, row in enumerate(reader):
                    #ts, value, label, anomaly, res_label
                    data.append(row)
            for window_size in range(10, 200, 10):
                tot_window = 0
                TP = 0
                TN = 0
                FP = 0
                FN = 0
                for base in range(0, len(data), window_size):
                    tot_window += 1
                    end = min(base + window_size, len(data))
                    window_label = 0
                    window_res = 0
                    for i in range(base, end):
                        if data[i][2] == '1':
                            window_label = 1
                        if data[i][4] == '1':
                            window_res = 1
                    if window_label == window_res:
                        if window_label == 1:
                            TP += 1
                        else :
                            TN += 1
                    else:
                        if window_res == 0:
                            FN += 1
                        else:
                            FP += 1
                
                precision = 0
                recall = 0
                if TP + FP != 0:
                    precision = TP / (TP + FP)
                if TP + FN != 0:
                    recall = TP / (TP + FN)
                f1 = 0 
                if precision + recall != 0:
                    f1 = 2 * precision * recall / ( precision + recall )
                print ('---------', filename, f1, precision, recall, '--------')
                if filename not in files:
                    files[filename] = []
                files[filename].append(f1)
    
           #output.append([filename, f1, precision, recall])
    output = []
    for filename in files:
        cur = [filename]
        for item in files[filename]:
            cur.append(item)
        output.append(cur)

    writecsv(output, 'window_experiment.csv')


def cal_window_f1(path, window_size=50):
    files = {}
    output = []
    for dirpath, dirnames, filenames in os.walk(path):

        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            if filename == 'all_res.csv':
                continue
            data = []

            with open(filepath, newline='') as f:
                reader = csv.reader(f)
                for idx, row in enumerate(reader):
                    #ts, value, label, anomaly, res_label
                    data.append(row)
            
            tot_window = 0
            TP = 0
            TN = 0
            FP = 0
            FN = 0
            for base in range(0, len(data), window_size):
                tot_window += 1
                end = min(base + window_size, len(data))
                window_label = 0
                window_res = 0
                for i in range(base, end):
                    if data[i][2] == '1':
                        window_label = 1
                    if data[i][4] == '1':
                        window_res = 1
                if window_label == window_res:
                    if window_label == 1:
                        TP += 1
                    else :
                        TN += 1
                else:
                    if window_res == 0:
                        FN += 1
                    else:
                        FP += 1
            
            precision = 0
            recall = 0
            if TP + FP != 0:
                precision = TP / (TP + FP)
            if TP + FN != 0:
                recall = TP / (TP + FN)
            f1 = 0 
            if precision + recall != 0:
                f1 = 2 * precision * recall / ( precision + recall )
            print ('---------', filename, f1, precision, recall, '--------')
            files[filename] = [f1, precision, recall]
            output.append([filename, f1, precision, recall])
    writecsv(output, 'window_evaluation.csv')
if __name__ == '__main__':
    #cal_window_f1('2019-10-10_00:09:18_res')
    expriment_window('2019-10-10_00-09-18_res')
