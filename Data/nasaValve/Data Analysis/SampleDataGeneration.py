import random


def getRandomInt(start=1, end=5):
    return random.randint(start, end)


class AttributeList:
    def __init__(self):
        self.length = random.randint(1, 5)

        self.mu = []
        self.sigma = []
        for i in range(self.length):
            self.mu.append(getRandomInt(20, 100))
            self.sigma.append(getRandomInt(1, 4))

    def getRandomValue(self):
        result = []
        for i in range(self.length):
            result.append(random.normalvariate(self.mu[i], self.sigma[i]))
        return result


class Item:
    def __init__(self, index):
        self.index = index
        self.attributes = AttributeList()

    def sample(self):
        return self.attributes.getRandomValue()


def genGraph(group):
    selectableSet = []
    graph = {}
    for i in range(len(group)):
        if len(selectableSet) == 0:
            selectableSet.append(group[i].index)
            graph[group[i].index] = []
        else:
            index = random.choice(selectableSet)
            if index not in graph:
                graph[index] = []
            graph[index].append(group[i].index)
            selectableSet.append(group[i].index)
    for item in group:
        if len(selectableSet) == 0:
            selectableSet.append(item.index)
        else:
            random.choice(selectableSet)

    for key in graph:
        if len(graph[key]) > 1:
            for i in range(3):
                if random.randint(1, 5) == 1:
                    graph[key].append(random.choice(graph[key][0:-1]))
    return graph


def processGraph(graph):
    most_call_time = 5;
    newgraph = {}
    for key in graph:
        newgraph[key] = []
        for index in graph[key]:
            newgraph[key].append((index, random.randint(0, 1), random.randint(2, most_call_time + 1)))
    return newgraph


def genLog(graph, itemList):
    logs = []
    stack = []

    start_point = min(graph.keys())

    stack.append(start_point)
    while len(stack) > 0:
        next = stack.pop()
        if next in graph:
            arr = graph[next]
            arr = processArr(arr)
            for i in arr[::-1]:
                stack.append(i)

        logs.append({
            "f": start_point,
            "attr": itemList[next].sample()
        })
    return logs


def processArr(arr):
    result = []
    for item in arr:
        times = random.randint(item[1], item[2])
        for i in range(times):
            result.append(item[0])
    return result

import json
if __name__ == '__main__':

    item_group = 20

    AllItems = []
    allitemList = []
    index = 0
    for i in range(item_group):
        group_size = random.randint(1, 10)
        group = []
        for j in range(group_size):
            group.append(Item(index))
            allitemList.append(group[-1])
            index += 1
        AllItems.append(group)

    allgraph = []
    for group in AllItems:
        graph = processGraph(genGraph(group))
        allgraph.append(graph)

    sample_size = 10
    result = []
    for i in range(sample_size):
        print(i)
        result += genLog(random.choice(allgraph), allitemList)

    with open("sample.json", "w") as f:
        ind = 0
        for r in result:
            obj = {
                "i": ind,
                "f": r["f"],
            }

            for at in range(len(r["attr"])):
                obj["a" + str(at)] = r["attr"][at]
            f.write(json.dumps(obj)+"\n")
            ind += 1

    # for obj in result:
    #     obj["label"] = 0
    # insertAttack(10, )


def insertAttack(num, list, allItemList):
    for i in range(num):
        position = random.randint(0, len(list))
        list.insert(position, allItemList[random.randint(0, len(allItemList)-1)].sample())
    return list

def removeAttack(num, list):
    for i in range(num):
        position = random.randint(0, len(list))
        del list[position]
    return list




















