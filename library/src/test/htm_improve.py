import sys

sys.path.append("../")
from detectors.htm.htm_detector import *
import os
import json
import datetime
import csv

def load_data_label():
    file_2_data = load_data()
    file_2_label = load_label() 
    labeled_file_2_data = {}
    for file in file_2_data:
        labeled_file_2_data[file] = []
        anomaly_ranges = file_2_label[file]
        label_cnt = 0
        for data_row in file_2_data[file]:
            timestamp = data_row[0]
            value = data_row[1]
            label = 0
            
            for range in anomaly_ranges:
                if timestamp >= range[0] and timestamp <= range[1]:
                    label = 1
                    label_cnt += 1
            labeled_file_2_data[file].append([timestamp, value, label])
        
        #print (file,'--------', label_cnt)
        #print (labeled_file_2_data[file][:30])
    return labeled_file_2_data, file_2_data 

def load_data():
    path = "../../../Data/NAB-master/data"
    file_2_data = {}
    for dirpath, dirnames, filenames in os.walk(path):

        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            if filepath[-4:] == '.csv':
                #data_files.append(filepath)
                csv_name = filepath.split('/')[-1]
                file_2_data[csv_name] = []
                
                with open(filepath, newline='') as f:
                    reader = csv.reader(f)
                    for idx, row in enumerate(reader):
                        if idx != 0:
                            file_2_data[csv_name].append([datetime.datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S').timestamp(), float(row[1])])
                #print (csv_name)
                #print (file_2_data[csv_name][:100])
                #print (filepath)
                #print ('--------------------------------')
    
    return file_2_data

def load_label():
    path = "../../../Data/NAB-master/labels/combined_windows.json"
    anomaly = {

    }
    
    with open(path) as f:
        content = f.read()
        obj = json.loads(content)
        for key in obj:
            filename = key.split("/")[-1]
            anomaly[filename] = []
            for time_range in obj[key]:
                start_stamp = datetime.datetime.strptime(time_range[0], '%Y-%m-%d %H:%M:%S.%f').timestamp()
                end_stamp = datetime.datetime.strptime(time_range[1], '%Y-%m-%d %H:%M:%S.%f').timestamp()
                anomaly[filename].append([start_stamp, end_stamp])
    return anomaly

def cal_f_one(data, label_col, res_col):
    TP = 0
    TN = 0
    FP = 0
    FN = 0
    for row in data:
        label = row[label_col]
        res = row[res_col]

        if label == res:
            if label == 1:
                TP += 1
            else:
                TN += 1
        else:
            if res == 0:
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

    print (f1, precision, recall)
    return f1, precision, recall

def writecsv(file,filename):
    csvfile = open(filename, 'w')
    writer = csv.writer(csvfile,lineterminator='\n')
    for line in file:
        writer.writerow(line)
    csvfile.close()

if __name__ == '__main__':
    labeled_data, unlabeled_data = load_data_label()
    print ('load labeled data over, try to improve htm')
    
    print('test train by real data')

    threshold = 0.512250003693
    print (len(unlabeled_data))
    all_res = []
    cnt = 0
    for file in unlabeled_data:
        cnt += 1
        print ('-----',file, cnt,'-----')
        #print ('sample:', unlabeled_data[file][:10])
        min_value = 1e9
        max_value = -1e9
        for sample in unlabeled_data[file][:750]:
            if sample[1] < min_value:
                min_value = sample[1]
            if sample[1] > max_value:
                max_value = sample[1]
        
        print ('min_value:', min_value, 'max_value:', max_value)
        htm = HTMAnomalyDetector("timestamp", "value")

        htm.initialize(docker_path="../../../docker/htmDocker/", lower_data_limit=min_value, upper_data_limit=max_value)

        res = htm.train(unlabeled_data[file])
        for i in range(len(labeled_data[file])):
            labeled_data[file][i].append(res[i]['anomalyScore'])
            if res[i]['anomalyScore'] >= threshold:
                labeled_data[file][i].append(1)
            else:
                labeled_data[file][i].append(0)
        f1, precision, recall = cal_f_one(labeled_data[file], 2, 4)
        all_res.append([file, f1, precision,recall])
        
    writecsv(all_res, 'all_res.csv')