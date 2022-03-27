#!/usr/bin/env python3
"""
This script filters a dataset in IPAL format. Filtering is done based on the entry
in the 'attack-details' field of the dataset.

The filter is specified using command line parameters.
"""

import argparse
import pathlib
import json
import sys
from utils import chunks, eprint, open_file, get_attack_details


def main():
    parser = argparse.ArgumentParser(
        description="Filter certain attack types or categories from MorrisDS4 dataset in IPAL format"
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
        help="Output file (ipal, optionally gzipped) or stdout if omitted",
    )
    parser.add_argument(
        "-m",
        "--mode",
        required=True,
        choices=["packet-by-packet", "sequence-of-four"],
        help="Should each packet be considered individually or should each sequence of four packets be considered one unit",
    )
    types_group = parser.add_mutually_exclusive_group()
    types_group.add_argument(
        "--except-types",
        nargs="*",
        type=int,
        help="Specify attack types to filter out (block list)",
    )
    types_group.add_argument(
        "--only-types",
        nargs="*",
        type=int,
        help="Specify the only attack types to keep (allow list)",
    )
    categories_group = parser.add_mutually_exclusive_group()
    categories_group.add_argument(
        "--except-categories",
        nargs="*",
        type=int,
        help="Specify attack categories to filter out (block list)",
    )
    categories_group.add_argument(
        "--only-categories",
        nargs="*",
        type=int,
        help="Specify the only attack categories to keep (allow list)",
    )
    args = parser.parse_args()

    # Keep track of stats
    filtered = 0
    total = 0

    # Load data
    with open_file(
        args.input_file, "rt"
    ) if args.input_file is not None else sys.stdin as f:
        # skip empty lines
        lines = [line for line in f.readlines() if line.strip()]

    sequence_len = 4 if args.mode == "sequence-of-four" else 1
    sequences = chunks(lines, sequence_len)

    with (
        open_file(args.output_file, "wt")
        if args.output_file is not None
        else sys.stdout
    ) as f:
        for sequence in sequences:
            remove = False

            for entry in sequence:
                data = json.loads(entry)

                attack_category, attack_type = get_attack_details(data)

                blocked_by_category = (
                    args.except_categories is not None
                    and attack_category in args.except_categories
                ) or (
                    args.only_categories is not None
                    and attack_category not in args.only_categories
                )
                blocked_by_type = (
                    args.except_types is not None and attack_type in args.except_types
                ) or (
                    args.only_types is not None and attack_type not in args.only_types
                )

                if blocked_by_category or blocked_by_type:
                    remove = True

            total += 1
            if remove:
                filtered += 1
            else:
                # copy packets of sequence over
                for entry in sequence:
                    f.write(entry)

    eprint(
        f"Removed {(filtered/total*100):.2f}% ({filtered}/{total}) of total sequences"
    )


if __name__ == "__main__":
    main()
