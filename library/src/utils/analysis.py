# Created by Xinyu Zhu on 10/3/2019, 1:40 AM
import matplotlib.pyplot as plt


def drawArray(sequence):
    assert isinstance(sequence, list)
    plt.style.use('seaborn-whitegrid')
    x = range(len(sequence))
    plt.plot(x, sequence)
    plt.show()
