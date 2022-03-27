#!/usr/bin/env python3
"""
Based on the IDS' output, this script calculates TP, TN, FP and FN and based on that
calculates precision, recall and accuracy. Recall is also calculated per individual
attack and per attack category.
"""

import argparse
import pathlib
import json
from utils import open_file, get_attack_details
from tabulate import tabulate
import json
import numpy as np
import sys


def main():
    parser = argparse.ArgumentParser(
        description="Create statistics for each attack type based on IDS IPAL output"
    )
    parser.add_argument(
        "-i",
        "--input-file",
        type=pathlib.Path,
        help="Input file (ipal, optionally gzipped) or stdin if omitted",
    )
    parser.add_argument(
        "-o",
        "--output-file",
        type=pathlib.Path,
        help="Write statistics in machine-readable JSON format to that location (optional)",
    )
    args = parser.parse_args()

    with open_file(
        args.input_file, "rt"
    ) if args.input_file is not None else sys.stdin as file:
        # create a table with rows for each attack category
        # and three columns: "attack type", "undetected count" and "detected count".
        # note that the first row corresponds to non-attack packets, meaning
        # "undetected" is actually the correct output.
        results_type = [[i, 0, 0] for i in range(36)]
        results_category = [[i, 0, 0] for i in range(8)]

        lines = [line for line in file.readlines() if line.strip()]
        count = len(lines)

        for l in lines:
            data = json.loads(l)

            attack_category, attack_type = get_attack_details(data)

            results_category[attack_category][2 if data["ids"] else 1] += 1
            results_type[attack_type][2 if data["ids"] else 1] += 1

        # calulate recall for types and categories.
        # use np.float64 to prevent DivisionByZero errors (return inf instead).
        with np.errstate(divide="ignore", invalid="ignore"):
            results_type[0].append(
                np.float64(results_type[0][1])
                / (results_type[0][1] + results_type[0][2])
            )
            for type_entry in results_type[1:]:
                type_entry.append(
                    np.float64(type_entry[2]) / (type_entry[1] + type_entry[2])
                )

            results_category[0].append(
                np.float64(results_category[0][1])
                / (results_category[0][1] + results_category[0][2])
            )
            for cat_entry in results_category[1:]:
                cat_entry.append(
                    np.float64(cat_entry[2]) / (cat_entry[1] + cat_entry[2])
                )

            # calculate global metrics
            true_positive = sum([row[2] for row in results_type[1:]])
            true_negative = results_type[0][1]
            false_positive = results_type[0][2]
            false_negative = sum([row[1] for row in results_type[1:]])
            assert count == (
                true_positive + true_negative + false_positive + false_negative
            )

            accuracy = np.float64(true_negative + true_positive) / count
            precision = np.float64(true_positive) / (true_positive + false_positive)
            recall = np.float64(true_positive) / (true_positive + false_negative)

        print(
            f"TP: {true_positive}, TN: {true_negative}, FP: {false_positive}, FN: {false_negative}, Count: {count}"
        )
        print(f"Global accuracy: {accuracy:.4f}")
        print(f"Global precision: {precision:.4f}")
        print(f"Global recall: {recall:.4f}")

        # output tables
        print("\n----- Attack Type Results -----")
        print(
            tabulate(
                results_type, headers=["attack type", "normal", "malicious", "recall"]
            )
        )

        print("\n----- Attack Category Results -----")
        print(
            tabulate(
                results_category,
                headers=["attack category", "normal", "malicious", "recall"],
            )
        )

    if args.output_file is not None:
        # create machine-readable output as json
        data = {
            "TP": true_positive,
            "TN": true_negative,
            "FP": false_positive,
            "FN": false_negative,
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "attack_types": {},
            "attack_categories": {},
        }

        for i in range(36):
            data["attack_types"][i] = {
                "labelled_normal": results_type[i][1],
                "labelled_malicious": results_type[i][2],
                "recall": results_type[i][3],
            }
        for i in range(8):
            data["attack_categories"][i] = {
                "labelled_normal": results_category[i][1],
                "labelled_malicious": results_category[i][2],
                "recall": results_category[i][3],
            }

        with open_file(args.output_file, "wt") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    main()
