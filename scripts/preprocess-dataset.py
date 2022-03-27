#!/usr/bin/env python3
"""
This script prepares a dataset in IPAL format. This includes the following activities:
- Normalizing certain data fields
- Performing categorical preprocessing on some data fields (essentially one-hot encoding)
- Adding system state to every packet using the "keep-last" method
- Adding an "id" field to each packet which corresponds to its position in the original dataset
"""

import argparse
import pathlib
import json
import numpy as np
import sys
from utils import open_file
from itertools import chain


# the keys of the arguments to be normalized
normalize_args = [
    "data;PID Setpoint",
    "data;PID Gain",
    "data;PID Reset",
    "data;PID Deadband",
    "data;PID Cycle Time",
    "data;PID Rate",
    # We do not normalize pressure in accordance with the original dataset
    # "data;Scaled Gas Pressure",
    "crc",
    "length",
    "timestamp",
]
categoricalize_args = ["type", "data;system mode"]


def getkey(data, key):
    if key.startswith("data;"):
        return data["data"][key[5:]] if key[5:] in data["data"] else None
    else:
        return data[key] if key in data else None


def setkey(data, key, value):
    if key.startswith("data;"):
        data["data"][key[5:]] = value
    else:
        data[key] = value


def main():
    parser = argparse.ArgumentParser(
        description="Preprocess MorrisDS4 dataset by normalizing and adding state"
    )
    parser.add_argument(
        "-i",
        "--input-file",
        required=True,
        type=pathlib.Path,
        help="Input file (ipal, optionally gzipped) or stdin if omitted",
    )
    parser.add_argument(
        "-o",
        "--output-file",
        required=True,
        type=pathlib.Path,
        help="Output file (ipal, optionally gzipped) or stdout if omitted",
    )
    args = parser.parse_args()

    # Open file handles
    f_in = (
        open_file(args.input_file, "rt") if args.input_file is not None else sys.stdin
    )
    f_out = (
        open_file(args.output_file, "wt")
        if args.output_file is not None
        else sys.stdout
    )

    with f_in, f_out:
        # skip empty lines
        packets = [json.loads(line) for line in f_in.readlines() if line.strip()]

        # save all values for each arg for normalizing and categoricalizing
        keys_to_save = list(chain(normalize_args, categoricalize_args))
        values = {arg: [] for arg in keys_to_save}

        # first pass to populate the values array
        for p in packets:
            for arg in keys_to_save:
                val = getkey(p, arg)
                if val is not None:
                    values[arg].append(val)

        # calculate means and stds
        norm_parameters = {
            arg: {"mean": np.mean(values[arg]), "std": np.std(values[arg])}
            for arg in normalize_args
        }
        cat_parameters = {
            arg: {val: f"{arg}_{val}" for val in list(set(values[arg]))}
            for arg in categoricalize_args
        }

        # second pass to add state and complete normalization
        cached_state = {}

        for i, p in enumerate(packets):
            # apply normalization
            for arg in normalize_args:
                val = getkey(p, arg)
                if val is not None:
                    setkey(
                        p,
                        arg,
                        (val - norm_parameters[arg]["mean"])
                        / norm_parameters[arg]["std"],
                    )

            # apply categoricalization
            for arg in categoricalize_args:
                val = getkey(p, arg)
                # only add the keys if the data-arg is present
                if val is not None:
                    keys = cat_parameters[arg]
                    for (value, strkey) in cat_parameters[arg].items():
                        setkey(p, strkey, value == val)

            # apply state caching
            for (key, value) in p["data"].items():
                cached_state[f"{p['src']}:{key}"] = value
            p["state"] = cached_state

            # add index as id
            p["id"] = i

            # copy packet over
            f_out.write(json.dumps(p))
            f_out.write("\n")


if __name__ == "__main__":
    main()
