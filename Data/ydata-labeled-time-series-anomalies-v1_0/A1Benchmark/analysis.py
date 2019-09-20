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


# load data from the file as a python array
def loadfile(file, split=","):
    result = []
    with open(file) as f:
        content = f.read().split("\n")
        header = content[0].split(split)
        for line in content[1:]:
            if line != "":
                record = line.split(split)
                result.append([float(a) for a in record])

    return (header, result)


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
    for key in data:
        header = data[key][0]
        for record in data[key][1]:

            atti = 0
            obj = {
                "file": key,
            }

            for val in record:
                obj[header[atti]] = val
                atti += 1
            processedData.append(obj)

    return processedData

if __name__ == '__main__':
    result = toTableauFormat(readAllData())
    with open("allYahooData.json", "w") as f:
        for r in result:
            f.write(json.dumps(r) + "\n")