from collections import defaultdict
import matplotlib.pyplot as plt

counter = defaultdict(int)


def countSubsequence(input, maxLength):
    if len(input) == 1:
        counter[(input[0],)] = 1
        return counter
    countSubsequence(input[0:len(input) - 1], maxLength)
    for i in range(maxLength):
        if len(input) - 1 - i < 0:
            break
        pattern = tuple(input[len(input) - 1 - i:])
        counter[pattern] += 1
    return counter


def prefixTable():
    prefix_table = defaultdict(dict)
    for key in counter:
        if (len(key) > 1):
            prefix = key[0:-1]
            value = key[-1]
            if value not in prefix_table[prefix]:
                prefix_table[prefix][value] = 0
            prefix_table[prefix][value] += counter[key]
    return prefix_table


def predict(tupleInput, prefix_table, reduceFactor=2):
    length = 1
    current_weight = 1

    result = defaultdict(int)
    startTuple = tuple(tupleInput[len(tupleInput) - length:])
    while (startTuple in prefix_table):

        for key in prefix_table[startTuple]:
            result[key] += prefix_table[startTuple][key] * current_weight
        length += 1
        current_weight *= reduceFactor
        if len(tupleInput) < length:
            break
        startTuple = tuple(tupleInput[len(tupleInput) - length:])

    totalOccurance = 0
    for key in result:
        totalOccurance += result[key]
    for key in result:
        result[key] /= totalOccurance
    return result


def streammingLearn(symbol, prefix_table, previousSequence):
    # return a anomaly score and update prefix_table and counter, and previousSequence whose lenghth is a windowSize
    scores = predict(previousSequence, prefix_table)
    if symbol not in scores:
        score = 0
    else:
        score = scores[symbol]

    for i in range(len(previousSequence)):
        if len(previousSequence) - 1 - i < 0:
            break
        pattern = tuple(previousSequence[len(previousSequence) - 1 - i:])
        if pattern not in prefix_table:
            prefix_table[pattern] = defaultdict(int)
        prefix_table[pattern][symbol] += 1
    previousSequence.pop(0)
    previousSequence.append(symbol)

    return score


def predictSequence(sequence, windowSize):
    previousSequence = ["-1"] * windowSize
    prefix_table = defaultdict(dict)
    score = []
    for symbol in sequence:
        s = streammingLearn(symbol, prefix_table, previousSequence)
        if symbol == "-1":
            score.append(-1)
        else:
            score.append(s)

    drawArray(score)


def drawArray(sequence):
    plt.style.use('seaborn-whitegrid')

    x = range(len(sequence))

    plt.plot(x, sequence)
    plt.show()


def readFile(filename):
    result = defaultdict(list)
    with open(filename) as f:
        content = f.read()
        content = content.split("\n")
        for line in content:
            if line != None and line != "":
                cline = line.split(' ')
                result[cline[0]].append(cline[1])

    newResult = {}
    for key in result:
        if len(result[key]) == 1:
            continue
        else:
            newResult[key] = result[key]

    return newResult


fileroot = "D:/CMULearn/Study/2019 Fall/Practicum/Sequential-Anomaly-Detection-Library/Data/HMM Data/origin/login/"
filename = ["login.trace_9809181415.int", "login.trace_9809251022.int", "login-homegrown.int", "login-recovered.int"]

data = {

}

data["training1"] = readFile(fileroot + filename[0])
data["training2"] = readFile(fileroot + filename[1])
data["testing"] = readFile(fileroot + filename[2])
data["recover"] = readFile(fileroot + filename[3])

for key in data["testing"]:
    print("testing:", data["testing"][key])

for key in data["training2"]:
    print("training2:", data["training2"][key])

for key in data["recover"]:
    print("recover:", data["recover"][key])

if __name__ == '__main__':
    window_size = 500

    trainingids = list(data["training1"].keys())
    testingids = list(data["testing"].keys())
    testingnormal = list(data["training2"].keys())
    testingrecover = list(data["recover"].keys())

    sequence = []
    for key in data["training1"]:
        sequence += data["training1"][key]
        sequence += ["-1"] * window_size
    print(sequence.__len__())
    for key in data["training2"]:
        sequence += data["training2"][key]
        sequence += ["-1"] * window_size
    print(sequence.__len__())
    for key in data["testing"]:
        sequence += data["testing"][key]
        sequence += ["-1"] * window_size
    print(sequence.__len__())
    for key in data["recover"]:
        sequence += data["recover"][key]
        sequence += ["-1"] * window_size
    print(sequence.__len__())
    print(sequence)
    predictSequence(sequence, window_size)
