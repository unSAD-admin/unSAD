import os
import json
import datetime


def fileExplore(root=".", fileType=[]):
    result = {"files": []}
    allFiles = [root + "/" + name for name in os.listdir(root)]
    for file in allFiles:
        if os.path.isdir(file):
            next = fileExplore(file, fileType)
            if len(next) == 0:
                continue
            else:
                result[file] = next
        else:
            if len(fileType) == 0:
                result["files"].append(file)
            elif file.split(".")[-1] in fileType:
                result["files"].append(file)
    if len(result["files"]) == 0:
        del result["files"]
    return result


def loadfile(file, split=","):
    result = []
    with open(file) as f:
        content = f.read().split("\n")
        header = content[0]

        for line in content[1:]:
            if line != "":
                record = line.split(split)
                timestamp = datetime.datetime.strptime(record[0], '%Y-%m-%d %H:%M:%S').timestamp()
                result.append([timestamp, float(record[1])])

    return result


all_data = {}


def readAllData(fileTree=fileExplore(fileType=["csv"])):
    for file in fileTree:
        if file == "files":
            for datafile in fileTree[file]:
                filename = datafile.split("/")[-1]
                if filename in all_data:
                    print("Error", filename + " is duplicated!")
                print(datafile)
                all_data[filename] = loadfile(datafile)
        else:
            readAllData(fileTree[file])
    return all_data


def toTableauFormat(data):
    processedData = []
    labelinfo = readLabel()
    for key in data:

        for record in data[key]:
            atti = 0
            obj = {
                "file": key,
                "label": 0
            }

            for val in record:
                obj["a" + str(atti)] = val
                atti += 1
            if key in labelinfo and obj["a0"] in labelinfo[key]:
                obj["label"] = 1
            processedData.append(obj)

    return processedData

def toCSVFormat(data):
    labelinfo = readLabel()
    dir_path = "./csv/"
    if not os.path.isdir(dir_path):
        os.mkdir(dir_path)
    for key in data:
        with open(os.path.join(dir_path, key), 'w') as f:
            for record in data[key]:
                label = 0
                if key in labelinfo and record[0] in labelinfo[key]:
                    label = 1
                f.write("%f,%f,%d\n"%(record[0], record[1], label))


def readLabel():
    root = "./labels/raw"
    anomaly = {

    }
    allLabelFiles = [root + "/" + name for name in os.listdir(root)]
    for file in allLabelFiles:
        with open(file) as f:
            content = f.read()
            obj = json.loads(content)
            for key in obj:
                filename = key.split("/")[-1]
                anomaly[filename] = set()
                for time in obj[key]:
                    stamp = datetime.datetime.strptime(time, '%Y-%m-%d %H:%M:%S.%f').timestamp()
                    anomaly[filename].add(stamp)
    return anomaly

if __name__ == '__main__':
    toCSVFormat(readAllData())
    # result = toTableauFormat(readAllData())
    # with open("allNABData.json", "w") as f:
    #     for r in result:
    #         f.write(json.dumps(r) + "\n")
    # readLabel()