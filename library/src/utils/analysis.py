# Created by Xinyu Zhu on 10/3/2019, 1:40 AM
import matplotlib.pyplot as plt

default_style = 'seaborn-whitegrid'


def draw_array(sequence):
    """Visualize a 1D numerical sequence"""
    plt.style.use(default_style)
    x = range(len(sequence))
    plt.plot(x, sequence)
    plt.show()


def draw_xy(sequence_x, sequence_y):
    """Visualize a line with the given x, y list"""
    plt.style.use(default_style)
    plt.plot(sequence_x, sequence_y)
