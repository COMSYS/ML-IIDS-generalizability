#!/usr/bin/env python
import json
import numpy as np
import os
from tabulate import tabulate


def main():
    with open(
        os.path.join(os.path.dirname(__file__), "../experiments/results.json"), "r"
    ) as f:
        data = json.load(f)

    table = []

    for classifier in ["rf", "blstm", "svm"]:
        cdata = data[classifier]
        baseline = cdata["baseline"]["precision"]["mean"]

        type_changes = []
        for entry in cdata["omit-attacks"].values():
            type_changes.append(entry["precision"]["mean"] - baseline)

        cat_changes = []
        for entry in cdata["omit-categories"].values():
            cat_changes.append(entry["precision"]["mean"] - baseline)

        table.append(
            [
                classifier,
                np.average(type_changes),
                np.min(type_changes),
                np.max(type_changes),
                np.average(cat_changes),
                np.min(cat_changes),
                np.max(cat_changes),
            ]
        )

    print("Precision changes when omitting attacks/categories:\n")
    print(
        tabulate(
            table,
            headers=[
                "Classifier",
                "Omit attacks: avg change",
                "Omit attacks: min change",
                "Omit attacks: max change",
                "Omit categories: avg change",
                "Omit categories: min change",
                "Omit categories: max change",
            ],
        )
    )


if __name__ == "__main__":
    main()
