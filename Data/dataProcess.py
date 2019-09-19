
# load data from the file as a python array
def loadfile(file, split=","):
    result = []
    with open(file) as f:
        content = f.read().split("\n")
        header = content[0].split(split)
        if split == None:
            for line in content[1:]:
                if line != "":
                    record = line.split()
                    result.append([float(a) for a in record])
        else:
            for line in content[1:]:
                if line != "":
                    record = line.split(split)
                    result.append([float(a) for a in record])

    return header , result

def toTableauFormat(header, data):
    # sort and assign a uniqe id to each point

    # transform into json format

    result = []
    for record in data:
        obj = {}
        for i in range(len(header)):
            obj[header[i]] = record[i]
        result.append(obj)
    result.sort(key=lambda a:a["Time"])
    index = 0
    for r in result:
        r["index"] = index
        index += 1
    return result

import json
if __name__ == '__main__':
    header, data = loadfile("shuttle.csv")
    result = toTableauFormat(header, data)
    with open("shuttle_tableau.json", "w") as f:
        for record in result:
            f.write(json.dumps(record)+"\n")