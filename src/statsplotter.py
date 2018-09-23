import matplotlib.pyplot as plt
import numpy as np
import uuid

from entities import Plottable


def plot_as_bar_graph(plottable: Plottable) -> str:
    x_axis = []
    y_axis = []

    for x_value in plottable.x_axis:
        x_axis.append(x_value)

    for y_value in plottable.y_axis:
        y_axis.append(y_value)

    y_pos = np.arange(len(x_axis))
    
    plt.bar(y_pos, y_axis, align="center", alpha=0.5)
    plt.xticks(y_pos, x_axis, rotation="vertical")
    plt.title(plottable.title)
    plt.ylabel(plottable.ylabel)

    for i, j in zip(y_pos, y_axis):
        plt.annotate(j, xy=(i, j), ha="center")
    
    filename = f"/tmp/{uuid.uuid1()}.png"
    plt.savefig(filename, format="png")
    plt.clf()

    return filename


def plot_as_line_graph(plottable: Plottable) -> str:
    x_axis = []
    y_axis = []

    for x_value in plottable.x_axis:
        x_axis.append(x_value)

    for y_value in plottable.y_axis:
        y_axis.append(y_value)

    y_pos = np.arange(len(x_axis))
    
    plt.plot(y_pos, y_axis, alpha=0.5)
    plt.xticks(y_pos, x_axis, rotation="vertical")
    plt.title(plottable.title)
    plt.ylabel(plottable.ylabel)
    
    filename = f"/tmp/{uuid.uuid1()}.png"
    plt.savefig(filename, format="png")
    plt.clf()

    return filename
