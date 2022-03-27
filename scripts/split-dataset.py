#!/usr/bin/env python3
"""
This script splits the given IPAL dataset into a specified number of parts of equal size.

The split is done in one of two modes:
- packet-by-packet: each packet is treated individually.
- sequence-of-four: considers sequences of 4 consecutive packets. Those sequences are distributed among the parts.
                    Required for BLSTM.

The dataset is shuffled before splitting.
"""

import numpy as np
import argparse
from pathlib import Path
import sys
from utils import open_file, chunks
from math import floor


def main():
    parser = argparse.ArgumentParser(description="Split IPAL dataset into equal parts")
    parser.add_argument(
        "-i",
        "--input-file",
        type=Path,
        help="Input file (ipal, optionally gzipped) or stdin if omitted",
    )
    parser.add_argument(
        "-d",
        "--output-directory",
        type=Path,
        default=Path.cwd(),
        help="Output folder (defaults to working directory)",
    )
    parser.add_argument(
        "-o",
        "--output-prefix",
        type=str,
        default="",
        help="Prefix for names of output files",
    )
    parser.add_argument(
        "-n",
        "--part-count",
        required=True,
        type=int,
        help="Number of parts the dataset should be split into",
    )
    parser.add_argument(
        "-m",
        "--mode",
        required=True,
        choices=["packet-by-packet", "sequence-of-four"],
        help="Which splitting mode should be used",
    )
    args = parser.parse_args()

    with open_file(
        args.input_file, "rt"
    ) if args.input_file is not None else sys.stdin as f:
        # skip empty lines
        lines = [line for line in f.readlines() if line.strip()]

    # create chunks depending on mode
    sequence_len = 4 if args.mode == "sequence-of-four" else 1
    sequences = list(chunks(lines, sequence_len))

    # random permutation of sequence indices
    seq_permutation = np.random.permutation(len(sequences))

    # partition the permutation into the parts
    part_length = len(sequences) / args.part_count
    parts = [
        seq_permutation[floor(i * part_length) : floor((i + 1) * part_length)]
        for i in range(args.part_count)
    ]

    print(f"Part lengths: {','.join([str(len(part)) for part in parts])}")
    assert sum([len(part) for part in parts]) == len(
        sequences
    ), "Not all sequences are assigned to parts. Numerical problem?"

    for i, part in enumerate(parts):
        with open(args.output_directory / f"{args.output_prefix}{i}.ipal", "w") as f:
            # get all lines from all sequences
            lines = [line for seq_index in part for line in sequences[seq_index]]
            for line in lines:
                f.write(line)


if __name__ == "__main__":
    main()
