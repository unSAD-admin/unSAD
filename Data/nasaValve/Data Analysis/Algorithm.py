from collections import defaultdict

counter = defaultdict(int)
prefix_table = defaultdict(dict)


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
    for key in counter:
        if (len(key) > 1):
            prefix = key[0:-1]
            value = key[-1]
            if value not in prefix_table[prefix]:
                prefix_table[prefix][value] = 0
            prefix_table[prefix][value] += counter[key]
    return prefix_table


def predict(tupleInput, reduceFactor=2):
    length = 1
    current_weight = 1

    startTuple = tuple(tupleInput[len(tupleInput) - length:])
    result = defaultdict(int)
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


def trainSequence(sequence, window_size):
    countSubsequence(sequence, window_size)
    prefixTable()


def avgSequence(sequence, window_size):
    pass


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
    window_size = 30

    trainingids = list(data["training1"].keys())
    testingids = list(data["testing"].keys())
    testingnormal = list(data["training2"].keys())

    testingrecover = list(data["recover"].keys())

    print(len(trainingids), len(testingids), len(testingnormal))

    # training
    for i in trainingids:
        sequence_to_train = data["training1"][i]
        if len(sequence_to_train) <= window_size:
            continue
        print(i, sequence_to_train)
        countSubsequence(sequence_to_train, window_size)

    # training 2
    for i in testingnormal:
        sequence_to_train = data["training2"][i]
        if len(sequence_to_train) <= window_size:
            continue
        print(i, sequence_to_train)
        countSubsequence(sequence_to_train, window_size)

    prefixTable()
    # testing
    tempIndex = 1
    sequence_to_test = data["testing"][testingids[tempIndex]]
    #sequence_to_test = data["training2"][testingnormal[tempIndex]]
    #sequence_to_test = data["recover"][testingrecover[tempIndex]]

    # sequence_to_test = sequence_to_train

    result = [-1] * window_size
    for pointer in range(window_size, len(sequence_to_test)):
        pred = predict(sequence_to_test[pointer - window_size: pointer])
        if sequence_to_test[pointer] not in pred:
            result.append(0)
            print("000000000000:", sequence_to_test[pointer - window_size: pointer], "->" , sequence_to_test[pointer])
            print("000000000000:", sequence_to_test[pointer - window_size: pointer], "->", pred)
        else:
            result.append(pred[sequence_to_test[pointer]])

    print("test", sequence_to_test)
    print(list(zip(sequence_to_test, result)))
    print(result)
    print("Sum", sum(result))

    import matplotlib.pyplot as plt

    plt.style.use('seaborn-whitegrid')


    fig = plt.figure()
    ax = plt.axes()

    x = range(len(result))

    plt.plot(x, result)
    plt.show()
