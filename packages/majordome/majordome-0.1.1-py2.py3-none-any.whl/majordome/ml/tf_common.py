# -*- coding: utf-8 -*-
from typing import Optional
from matplotlib import pyplot as plt
from matplotlib.figure import Figure


def plot_history(
        data_history: dict[str, list[float]],
        metric: str,
        style: Optional[str] = "seaborn-white",
        gridstyle: Optional[str] = ":"
    ) -> Figure:
    """ Plot trainning history data for Tensorflow.
    
    Parameters
    ----------
    data_history : dict[str, list[float]]
        Training and validation data history returned by Tensorflow.
    metric : str
        Name of metric function used for training.
    style : Optional[str] = "seaborn-white"
        Matplotlib plotting style for customizing figure.
    gridstyle : Optional[str] = ":"
        Grid style to apply in plots.

    Returns
    -------
    Figure
        Matplotlib figure for user display or save.
    """
    legend = ["Train", "Test"]

    plt.close("all")
    plt.style.use(style)
    fig = plt.figure(figsize=(12, 6))

    plt.subplot(121)
    plt.plot(data_history[metric])
    plt.plot(data_history[F"val_{metric}"])
    plt.title("Metric over epochs")
    plt.ylabel("Metric")
    plt.xlabel("Epoch")

    if gridstyle is not None:
        plt.grid(linestyle=gridstyle)

    plt.legend(legend, loc="upper left")

    plt.subplot(122)
    plt.plot(data_history["loss"])
    plt.plot(data_history["val_loss"])
    plt.title("Loss over epochs")
    plt.ylabel("Loss")
    plt.xlabel("Epoch")

    if gridstyle is not None:
        plt.grid(linestyle=gridstyle)

    plt.legend(legend, loc="upper left")

    fig.tight_layout()
    return fig
