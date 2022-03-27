#!/usr/bin/env python3
"""
This script aggregates the results of all omit attacks and single attacks experiments
into a single file "results.json" containing all relevant data.
"""

import os
from typing import Dict, List
import numpy as np
import json

CLASSIFIERS = ["rf", "svm", "blstm"]
FOLD_COUNT = 5
# We have 36 attack types: type 0 is "benign", types 1-35 are malicious.
PACKET_TYPE_COUNT = 36
# Category 0 is also benign here
PACKET_CATEGORY_COUNT = 8


def load_cross_validation(fold_files: List[str]) -> Dict[str, List[float]]:
    """
    Load results for one run with cross-validation. The fold_files should contain the filenames
    for all folds.
    """
    # Statistics per attack or category
    recall_types = np.empty((len(fold_files), PACKET_TYPE_COUNT))
    recall_cats = np.empty((len(fold_files), PACKET_CATEGORY_COUNT))

    # Statistics over the whole dataset
    precision = np.empty(len(fold_files))
    accuracy = np.empty(len(fold_files))
    recall = np.empty(len(fold_files))

    for (index, filename) in enumerate(fold_files):
        with open(filename, "r") as f:
            data = json.load(f)

        for i in range(PACKET_TYPE_COUNT):
            recall_types[index, i] = data["attack_types"][f"{i}"]["recall"]

        for i in range(PACKET_CATEGORY_COUNT):
            recall_cats[index, i] = data["attack_categories"][f"{i}"]["recall"]

        precision[index] = data["precision"]
        accuracy[index] = data["accuracy"]
        recall[index] = data["recall"]

    # Data returned for one conducted experiment
    return {
        "precision": {
            "mean": np.mean(precision),
            "std": np.std(precision),
            "values": precision.tolist(),
        },
        "accuracy": {
            "mean": np.mean(accuracy),
            "std": np.std(accuracy),
            "values": accuracy.tolist(),
        },
        "recall": {
            "total": {
                "mean": np.mean(recall),
                "std": np.std(recall),
                "values": recall.tolist(),
            },
            "detailed": {
                "types": {
                    i: {"mean": mean, "std": std, "values": values}
                    for (i, (values, mean, std)) in enumerate(
                        zip(
                            recall_types.transpose().tolist(),
                            np.mean(recall_types, axis=0),
                            np.std(recall_types, axis=0),
                        )
                    )
                },
                "categories": {
                    i: {"mean": mean, "std": std, "values": values}
                    for (i, (values, mean, std)) in enumerate(
                        zip(
                            recall_cats.transpose().tolist(),
                            np.mean(recall_cats, axis=0),
                            np.std(recall_cats, axis=0),
                        )
                    )
                },
            },
        },
    }


def main():
    experiments_folder = os.path.dirname(__file__)
    data = {}

    for classifier in CLASSIFIERS:
        data[classifier] = {
            "baseline": {},
            "omit-attacks": {},
            "omit-categories": {},
            "single-attacks": {},
            "single-categories": {},
        }

        baseline_stats_files = [
            os.path.join(
                experiments_folder,
                f"omit-attacks/results/{classifier}/{classifier}-baseline_fold-{fold}.statistics.json",
            )
            for fold in range(FOLD_COUNT)
        ]
        data[classifier]["baseline"] = load_cross_validation(baseline_stats_files)

        for attack_type in range(1, PACKET_TYPE_COUNT):
            omit_fold_files = [
                os.path.join(
                    experiments_folder,
                    f"omit-attacks/results/{classifier}/{classifier}-type-{attack_type:02d}_fold-{fold}.statistics.json",
                )
                for fold in range(FOLD_COUNT)
            ]
            data[classifier]["omit-attacks"][attack_type] = load_cross_validation(
                omit_fold_files
            )

            single_fold_files = [
                os.path.join(
                    experiments_folder,
                    f"single-attacks/results/{classifier}/{classifier}-type-{attack_type:02d}_fold-{fold}.statistics.json",
                )
                for fold in range(FOLD_COUNT)
            ]
            data[classifier]["single-attacks"][attack_type] = load_cross_validation(
                single_fold_files
            )

        for attack_category in range(1, PACKET_CATEGORY_COUNT):
            omit_fold_files = [
                os.path.join(
                    experiments_folder,
                    f"omit-attacks/results/{classifier}/{classifier}-cat-{attack_category:02d}_fold-{fold}.statistics.json",
                )
                for fold in range(FOLD_COUNT)
            ]
            data[classifier]["omit-categories"][
                attack_category
            ] = load_cross_validation(omit_fold_files)

            single_fold_files = [
                os.path.join(
                    experiments_folder,
                    f"single-attacks/results/{classifier}/{classifier}-cat-{attack_category:02d}_fold-{fold}.statistics.json",
                )
                for fold in range(FOLD_COUNT)
            ]
            data[classifier]["single-categories"][
                attack_category
            ] = load_cross_validation(single_fold_files)

    with open(os.path.join(os.path.dirname(__file__), "results.json"), "w") as f:
        json.dump(data, f, indent=4)


if __name__ == "__main__":
    main()
