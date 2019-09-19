import os
import json


# load data from the file as a python array
def loadfile(file, split=None):
    result = []
    with open(file) as f:
        content = f.read().split("\n")
        if split == None:
            for line in content:
                if line != "":
                    record = line.split()
                    result.append([float(a) for a in record])
        else:
            for line in content:
                if line != "":
                    record = line.split(split)
                    result.append([float(a) for a in record])

    return result


# generate a dictionary tree of the files of specific type in the root folder
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


def readAllData(fileTree=fileExplore(fileType=["txt", "cvs", "TXT", "CSV"])):
    for file in fileTree:
        if file == "files":
            for datafile in fileTree[file]:
                filename = datafile.split("/")[-1]
                if filename in all_data:
                    print("Error", filename + " is duplicated!")
                print(datafile)
                if ("CSV" in filename):
                    all_data[filename] = loadfile(datafile, ",")
                else:
                    all_data[filename] = loadfile(datafile)
        else:
            readAllData(fileTree[file])
    return all_data


def toTableauFormat(data):
    processedData = []
    for key in data:
        index = 0
        for record in data[key]:
            atti = 0
            obj = {
                "file": key,
                "index": index
            }
            index += 1
            for val in record:
                obj["a" + str(atti)] = val
                atti += 1
            processedData.append(obj)

    return processedData


all_data = {}

if __name__ == '__main__':
    result = toTableauFormat(readAllData())
    with open("allData.json", "w") as f:
        for r in result:
            f.write(json.dumps(r) + "\n")
