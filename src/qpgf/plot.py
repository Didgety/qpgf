# qpgf/plot.py

import numpy as np
import matplotlib.pyplot as plt
from .pgf import marginal_from_joint


def plot_pgf(pgf, title="Error Distribution (PGF)", ax=None, threshold=None, scale='log'):
    """
    Plot a single probability generating function (PGF).

    Args:
        pgf (np.ndarray): PGF coefficients.
        title (str): Title for the plot.
        ax (matplotlib.axes.Axes or None): Optional matplotlib axis to draw on. Used by plot_joint_marginals.
        threshold (float or None): If set, exclude values below this probability.
        scale (str): Y-axis scale mode: 'linear', 'log', or 'semilog'.
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 4))
    start = 0 if threshold is None else int(np.floor(threshold + 1))
    x = range(start, len(pgf))
    y = pgf[start:]
    ax.bar(x, y)
    ax.set_xlabel("Total Number of Qubit Errors")
    ax.set_ylabel("Probability")
    if scale == 'log':
        ax.set_yscale('log')
    elif scale == 'semilog':
        ax.set_yscale('symlog')
    ax.set_title(title)
    ax.grid(True)
    plt.tight_layout()
    return ax

def plot_joint_marginals(joint_pgf, max_qubits=9, threshold=None, scale='log'):
    """
    Plot marginal PGFs for qubits 0 -> max_qubits in the joint PGF.

    Args:
        joint_pgf (dict): Joint PGF (dict of tuple -> probability).
        max_qubits (int): Maximum number of qubits to plot.
        threshold (float or None): Optional minimum probability to show.
        scale (str): 'linear', 'log', or 'semilog' for y-axis.
    """
    qubit_count = len(next(iter(joint_pgf)))
    if qubit_count > max_qubits:
        print(f"Too many qubits ({qubit_count}) to plot all marginals")
        return
    fig, axes = plt.subplots(1, qubit_count, figsize=(4 * qubit_count, 4))
    if qubit_count == 1:
        axes = [axes]
    for i in range(qubit_count):
        marginal = marginal_from_joint(joint_pgf, i)
        plot_pgf(marginal, title=f"Qubit {i} Marginal", ax=axes[i], threshold=threshold, scale=scale)
    plt.tight_layout()
    plt.show()

def compare_pgfs(pgfs, labels, title="PGF Comparison", threshold=None, log_scale='none'):
    """
    Compare multiple PGFs on the same plot.

    Args:
        pgfs (list): List of PGF arrays.
        labels (list or None): Optional list of labels for each PGF.
        title (str): Plot title.
        threshold (float or None): Optional minimum probability to show.
        scale (str): 'linear', 'log', or 'semilog' scaling.
    """
    plt.figure(figsize=(8, 4))
    for pgf, label in zip(pgfs, labels):
        start = threshold + 1 if threshold is not None else 0
        x = range(start, len(pgf))
        y = pgf[start:]
        plt.plot(x, y, label=label, marker="o")
    plt.xlabel("Number of Qubit Errors")
    if log_scale == 'log':
        plt.yscale('log')
    elif log_scale == 'semilog':
        plt.yscale('symlog')
    plt.ylabel("Probability")
    plt.title(title)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()