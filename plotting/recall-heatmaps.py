#!/usr/bin/env python3
"""
This script creates detailed recall heatmaps showing the recall in each individual attack
or attack category for each experiment.
"""

import numpy as np
from itertools import product
import matplotlib.pyplot as plt
from matplotlib.colors import SymLogNorm
import json
import os

# We have 36 attack types: type 0 is "benign", types 1-35 are malicious.
PACKET_TYPE_COUNT = 36
# Category 0 is also benign here
PACKET_CATEGORY_COUNT = 8


def plot_relative_heatmap(
    results: np.ndarray, xlabel: str, ylabel: str, title: str, figsize=(13, 13)
):
    ####################################
    # Move some data around
    ####################################

    # Calculate relative difference to the baseline
    stacked_baseline = np.repeat(
        results[0, :].reshape((1, -1)), results.shape[0] - 1, axis=0
    )
    heatmap_relative = (stacked_baseline - results[1:, :]) / stacked_baseline

    # Convert all numbers to percent
    heatmap_relative *= 100

    # Reverse y-axis so that baseline is at the top
    heatmap_relative = np.flip(heatmap_relative, axis=0)

    ####################################
    # Prepare relative heatmap
    ####################################
    fig, ax = plt.subplots(figsize=figsize)
    ax.imshow(
        heatmap_relative,
        cmap=plt.get_cmap("bwr"),
        norm=SymLogNorm(linthresh=5, vmin=-100, vmax=100),
    )

    ax.set_xticks(range(heatmap_relative.shape[1]))
    ax.set_xticklabels(["benign"] + list(range(1, heatmap_relative.shape[1])))
    ax.set_yticks(range(heatmap_relative.shape[0]))
    ax.set_yticklabels([*reversed(range(1, heatmap_relative.shape[0])), "baseline"])

    # Minor ticks for grid lines
    ax.set_xticks(np.arange(-0.5, heatmap_relative.shape[1], 1), minor=True)
    ax.set_yticks(np.arange(-0.5, heatmap_relative.shape[0], 1), minor=True)
    ax.grid(which="minor", color="black", linestyle="-", linewidth=0.5)

    ax.invert_yaxis()

    for (i, j) in product(
        range(heatmap_relative.shape[0]), range(heatmap_relative.shape[1])
    ):
        val = heatmap_relative[i, j]
        if heatmap_relative.shape[0] < 10 or abs(val) > 5:
            ax.text(
                j,
                i,
                f"{val:.1f}",
                ha="center",
                va="center",
                color=("w" if abs(val) > 5 else "gray"),
            )

    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    fig.tight_layout()

    return fig


def plot_absolute_heatmap(
    results: np.ndarray, xlabel: str, ylabel: str, title: str, figsize=(13, 13)
):
    ####################################
    # Move some data around
    ####################################

    # Reverse y-axis so that baseline is at the top
    results = np.flip(results, axis=0)

    # Convert all numbers to percent
    results *= 100

    ####################################
    # Prepare absolute heatmap
    ####################################
    fig, ax = plt.subplots(figsize=figsize)
    ax.imshow(results, cmap=plt.get_cmap("cividis_r"), vmin=0, vmax=100)

    ax.set_xticks(range(results.shape[1]))
    ax.set_xticklabels(["benign"] + list(range(1, results.shape[1])))
    ax.set_yticks(range(results.shape[0]))
    ax.set_yticklabels([*reversed(range(1, results.shape[0])), "baseline"])

    # Minor ticks for grid lines
    ax.set_xticks(np.arange(-0.5, results.shape[1], 1), minor=True)
    ax.set_yticks(np.arange(-0.5, results.shape[0], 1), minor=True)
    ax.grid(which="minor", color="black", linestyle="-", linewidth=0.5)

    ax.invert_yaxis()

    for (i, j) in product(range(results.shape[0]), range(results.shape[1])):
        val = results[i, j]
        ax.text(
            j,
            i,
            f"{val:.1f}",
            ha="center",
            va="center",
            color=("k" if val < 50 else "w"),
            fontsize=8,
        )

    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    fig.tight_layout()

    return fig


def main():
    with open(
        os.path.join(os.path.dirname(__file__), "../experiments/results.json"), "r"
    ) as f:
        data = json.load(f)

    for classifier in ["rf", "svm", "blstm"]:
        ####################################
        # Omit attacks
        ####################################

        # Create a 2d array of recall values for heatmap generation.
        # first axis: experiments, second axis: attacks for which recall is measured.
        omit_attacks_experiments = [
            data[classifier]["baseline"],
            *[
                data[classifier]["omit-attacks"][str(i)]
                for i in range(1, PACKET_TYPE_COUNT)
            ],
        ]
        omit_attacks_recall = np.array(
            [
                [
                    experiment["recall"]["detailed"]["types"][str(i)]["mean"]
                    for i in range(PACKET_TYPE_COUNT)
                ]
                for experiment in omit_attacks_experiments
            ]
        )

        plot_relative_heatmap(
            omit_attacks_recall,
            xlabel="Classified attack",
            ylabel="Omitted attack",
            title="Recall change relative to baseline [%]",
        ).savefig(
            os.path.join(
                os.path.dirname(__file__),
                f"recall-heatmaps/omit-attacks_{classifier}_relative.png",
            )
        )
        plot_absolute_heatmap(
            omit_attacks_recall,
            xlabel="Classified attack",
            ylabel="Omitted attack",
            title="Absolute recall [%]",
        ).savefig(
            os.path.join(
                os.path.dirname(__file__),
                f"recall-heatmaps/omit-attacks_{classifier}_absolute.png",
            )
        )

        ####################################
        # Omit categories
        ####################################

        omit_categories_experiments = [
            data[classifier]["baseline"],
            *[
                data[classifier]["omit-categories"][str(i)]
                for i in range(1, PACKET_CATEGORY_COUNT)
            ],
        ]
        omit_categories_recall = np.array(
            [
                [
                    experiment["recall"]["detailed"]["categories"][str(i)]["mean"]
                    for i in range(PACKET_CATEGORY_COUNT)
                ]
                for experiment in omit_categories_experiments
            ]
        )

        plot_relative_heatmap(
            omit_categories_recall,
            xlabel="Classified attack category",
            ylabel="Omitted attack category",
            title="Recall change relative to baseline [%]",
            figsize=(8, 8),
        ).savefig(
            os.path.join(
                os.path.dirname(__file__),
                f"recall-heatmaps/omit-categories_{classifier}_relative.png",
            )
        )
        plot_absolute_heatmap(
            omit_categories_recall,
            xlabel="Classified attack category",
            ylabel="Omitted attack category",
            title="Absolute recall [%]",
            figsize=(8, 8),
        ).savefig(
            os.path.join(
                os.path.dirname(__file__),
                f"recall-heatmaps/omit-categories_{classifier}_absolute.png",
            )
        )

        ####################################
        # Single attacks
        ####################################

        # Create a 2d array of recall values for heatmap generation.
        # first axis: experiments, second axis: attacks for which recall is measured.
        single_attacks_experiments = [
            data[classifier]["baseline"],
            *[
                data[classifier]["single-attacks"][str(i)]
                for i in range(1, PACKET_TYPE_COUNT)
            ],
        ]
        single_attacks_recall = np.array(
            [
                [
                    experiment["recall"]["detailed"]["types"][str(i)]["mean"]
                    for i in range(PACKET_TYPE_COUNT)
                ]
                for experiment in single_attacks_experiments
            ]
        )

        plot_absolute_heatmap(
            single_attacks_recall,
            xlabel="Classified attack",
            ylabel="Trained attack",
            title="Absolute recall [%]",
        ).savefig(
            os.path.join(
                os.path.dirname(__file__),
                f"recall-heatmaps/single-attacks_{classifier}.png",
            )
        )

        ####################################
        # Single categories
        ####################################

        single_categories_experiments = [
            data[classifier]["baseline"],
            *[
                data[classifier]["single-categories"][str(i)]
                for i in range(1, PACKET_CATEGORY_COUNT)
            ],
        ]
        single_categories_recall = np.array(
            [
                [
                    experiment["recall"]["detailed"]["categories"][str(i)]["mean"]
                    for i in range(PACKET_CATEGORY_COUNT)
                ]
                for experiment in single_categories_experiments
            ]
        )

        plot_absolute_heatmap(
            single_categories_recall,
            xlabel="Classified attack category",
            ylabel="Trained attack category",
            title="Absolute recall [%]",
            figsize=(8, 8),
        ).savefig(
            os.path.join(
                os.path.dirname(__file__),
                f"recall-heatmaps/single-categories_{classifier}.png",
            )
        )


if __name__ == "__main__":
    main()
