# Created by Xinyu Zhu on 10/3/2019, 2:23 AM


def normalize(collection):
    """
    Normalize the value of all element in a collection
    each element will be divided by the sum
    """
    if isinstance(collection, dict):
        total = 0
        result = {}
        for key in collection:
            total += collection[key]
        if total == 0:
            return {}
        for key in collection:
            result[key] = collection[key] / total
    else:
        total = sum(collection)
        result = [0] * len(collection)
        if total == 0:
            return result
        for i in range(len(collection)):
            result[i] = collection[i] / total

    return result


def windowed_list(array, window_size):
    result = []
    for i in range(0, len(array) - window_size):
        result.append(array[i: i + window_size])
    return result


def simple_filter(array, filter_func, window_size):
    """
    apply 1D convolution operation on array using filter_func as the
    activation function and window_size for window size
    """
    result = []
    for i in range(window_size - 1):
        result.append(array[i])
    for i in range(window_size - 1, len(array)):
        result.append(filter_func(array[i - window_size + 1:i + 1]))
    return result


def mean_filter(array):
    """
    a mean filter function
    :param array: the input array
    :return: the mean of the array
    """
    return sum(array) / len(array)
