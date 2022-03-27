#!/usr/bin/env python3
"""
This script generates scatter plots for both experiments with accuracy, precision, recall and f1-scores.
The metrics are calculated over the whole test set and averaged over all folds.
"""

import os
import json
import numpy as np
import matplotlib.pyplot as plt

CLASSIFIERS = ["rf", "svm", "blstm"]
F_SCORE_BETA = 1


def get_f_score(precision, recall):
    return (
        (1 + (F_SCORE_BETA ** 2))
        * precision
        * recall
        / ((F_SCORE_BETA ** 2) * precision + recall)
    )


def plot(
    baseline: np.ndarray,
    attack_data: np.ndarray,
    category_data: np.ndarray,
    ylabel: str,
):
    colors = ["r", "b", "g"]
    fig, (ax1, ax2) = plt.subplots(1, 2, gridspec_kw={"width_ratios": [7, 35]})

    ax1.set_ylabel(ylabel)
    ax1.set_xlabel("Attack categories")
    ax1.set_xticks(range(1, 8))
    ax2.set_xlabel("Individual attacks")

    category_data *= 100
    attack_data *= 100
    baseline *= 100

    for i, classifier in enumerate(CLASSIFIERS):
        ax1.plot(
            [1, 7],
            [baseline[i], baseline[i]],
            "--",
            color=colors[i],
            label=f"{classifier} baseline",
        )
        ax1.scatter(range(1, 8), category_data[i, :], color=colors[i], label=classifier)

        ax2.plot(
            [1, 35],
            [baseline[i], baseline[i]],
            "--",
            color=colors[i],
            label=f"{classifier} baseline",
        )
        ax2.scatter(range(1, 36), attack_data[i, :], color=colors[i], label=classifier)

    ax2.legend()
    fig.tight_layout()

    return fig


def main():
    with open(
        os.path.join(os.path.dirname(__file__), "../experiments/results.json"), "r"
    ) as f:
        data = json.load(f)

    cdata = [data[classifier] for classifier in CLASSIFIERS]

    ####################################
    # Omit attacks
    ####################################

    accuracy_types = np.array(
        [
            [c["omit-attacks"][str(i)]["accuracy"]["mean"] for i in range(1, 36)]
            for c in cdata
        ]
    )
    accuracy_cats = np.array(
        [
            [c["omit-categories"][str(i)]["accuracy"]["mean"] for i in range(1, 8)]
            for c in cdata
        ]
    )
    accuracy_baseline = np.array([c["baseline"]["accuracy"]["mean"] for c in cdata])
    plot(
        accuracy_baseline,
        accuracy_types,
        accuracy_cats,
        "Omit Experiment: Accuracy [%]",
    ).savefig(
        os.path.join(os.path.dirname(__file__), "aggregated-metrics/omit_accuracy.png")
    )

    precision_types = np.array(
        [
            [c["omit-attacks"][str(i)]["precision"]["mean"] for i in range(1, 36)]
            for c in cdata
        ]
    )
    precision_cats = np.array(
        [
            [c["omit-categories"][str(i)]["precision"]["mean"] for i in range(1, 8)]
            for c in cdata
        ]
    )
    precision_baseline = np.array([c["baseline"]["precision"]["mean"] for c in cdata])
    plot(
        precision_baseline,
        precision_types,
        precision_cats,
        "Omit Experiment: Precision [%]",
    ).savefig(
        os.path.join(os.path.dirname(__file__), "aggregated-metrics/omit_precision.png")
    )

    recall_types = np.array(
        [
            [c["omit-attacks"][str(i)]["recall"]["total"]["mean"] for i in range(1, 36)]
            for c in cdata
        ]
    )
    recall_cats = np.array(
        [
            [
                c["omit-categories"][str(i)]["recall"]["total"]["mean"]
                for i in range(1, 8)
            ]
            for c in cdata
        ]
    )
    recall_baseline = np.array(
        [c["baseline"]["recall"]["total"]["mean"] for c in cdata]
    )
    plot(
        recall_baseline, recall_types, recall_cats, "Omit Experiment: Recall [%]"
    ).savefig(
        os.path.join(os.path.dirname(__file__), "aggregated-metrics/omit_recall.png")
    )

    f_types = get_f_score(precision_types, recall_types)
    f_cats = get_f_score(precision_cats, recall_cats)
    f_baseline = get_f_score(precision_baseline, recall_baseline)
    plot(
        recall_baseline,
        recall_types,
        recall_cats,
        f"Omit Experiment: F{F_SCORE_BETA} [%]",
    ).savefig(
        os.path.join(
            os.path.dirname(__file__), f"aggregated-metrics/omit_f{F_SCORE_BETA}.png",
        )
    )

    ####################################
    # Single attacks
    ####################################

    accuracy_types = np.array(
        [
            [c["single-attacks"][str(i)]["accuracy"]["mean"] for i in range(1, 36)]
            for c in cdata
        ]
    )
    accuracy_cats = np.array(
        [
            [c["single-categories"][str(i)]["accuracy"]["mean"] for i in range(1, 8)]
            for c in cdata
        ]
    )
    accuracy_baseline = np.array([c["baseline"]["accuracy"]["mean"] for c in cdata])
    plot(
        accuracy_baseline,
        accuracy_types,
        accuracy_cats,
        "Single Experiment: Accuracy [%]",
    ).savefig(
        os.path.join(
            os.path.dirname(__file__), "aggregated-metrics/single_accuracy.png"
        )
    )

    precision_types = np.array(
        [
            [c["single-attacks"][str(i)]["precision"]["mean"] for i in range(1, 36)]
            for c in cdata
        ]
    )
    precision_cats = np.array(
        [
            [c["single-categories"][str(i)]["precision"]["mean"] for i in range(1, 8)]
            for c in cdata
        ]
    )
    precision_baseline = np.array([c["baseline"]["precision"]["mean"] for c in cdata])
    plot(
        precision_baseline,
        precision_types,
        precision_cats,
        "Single Experiment: Precision [%]",
    ).savefig(
        os.path.join(
            os.path.dirname(__file__), "aggregated-metrics/single_precision.png"
        )
    )

    recall_types = np.array(
        [
            [
                c["single-attacks"][str(i)]["recall"]["total"]["mean"]
                for i in range(1, 36)
            ]
            for c in cdata
        ]
    )
    recall_cats = np.array(
        [
            [
                c["single-categories"][str(i)]["recall"]["total"]["mean"]
                for i in range(1, 8)
            ]
            for c in cdata
        ]
    )
    recall_baseline = np.array(
        [c["baseline"]["recall"]["total"]["mean"] for c in cdata]
    )
    plot(
        recall_baseline, recall_types, recall_cats, "Single Experiment: Recall [%]"
    ).savefig(
        os.path.join(os.path.dirname(__file__), "aggregated-metrics/single_recall.png")
    )

    f_types = get_f_score(precision_types, recall_types)
    f_cats = get_f_score(precision_cats, recall_cats)
    f_baseline = get_f_score(precision_baseline, recall_baseline)
    plot(
        recall_baseline,
        recall_types,
        recall_cats,
        f"Single Experiment: F{F_SCORE_BETA} [%]",
    ).savefig(
        os.path.join(
            os.path.dirname(__file__), f"aggregated-metrics/single_f{F_SCORE_BETA}.png",
        )
    )


if __name__ == "__main__":
    main()
