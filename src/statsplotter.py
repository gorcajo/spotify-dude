import base64
import matplotlib.pyplot as plt
import numpy as np
import os


TMP_FILENAME = "/tmp/spotify-dude-stats.png"


def dict_as_bar_graph(data :dict, title: str, ylabel: str) -> str:
    x_axis = []
    y_axis = []

    for key, value in data.items():
        x_axis.append(key)
        y_axis.append(value)

    y_pos = np.arange(len(x_axis))
    
    plt.bar(y_pos, y_axis, align="center", alpha=0.5)
    plt.xticks(y_pos, x_axis, rotation="vertical")
    plt.title(title)
    plt.ylabel(ylabel)

    for i, j in zip(y_pos, y_axis):
        plt.annotate(j, xy=(i, j), ha="center")
    
    return _get_image_base64(TMP_FILENAME)


def _get_image_base64(filename: str) -> str:
    plt.savefig(TMP_FILENAME, format="png")

    with open(filename, "rb") as file:
        encoded_image = base64.b64encode(file.read()).decode("utf-8")
    
    os.remove(filename)

    return encoded_image