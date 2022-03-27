#!/usr/bin/env python3
"""
This script transcribes the dataset from Arff into IPAL format.
"""

from argparse import ArgumentParser
from pathlib import Path
import sys
import json
import re
from utils import open_file

# how to handle data values
ipal_data_config = {
    "pressure measurement": {
        "name": "Scaled Gas Pressure",
        "function": (lambda x: max(0, float(x))),
    },
    "control scheme": {"name": "control schema", "function": int},
    "system mode": {"name": "system mode", "function": int},
    "pump": {"name": "pump", "function": int},
    "solenoid": {"name": "solenoid", "function": int},
    "setpoint": {"name": "PID Setpoint", "function": float},
    "reset rate": {"name": "PID Reset", "function": float},
    "gain": {"name": "PID Gain", "function": int},
    "rate": {"name": "PID Rate", "function": float},
    "deadband": {"name": "PID Deadband", "function": float},
    "cycle time": {"name": "PID Cycle Time", "function": float},
}


def main():
    parser = ArgumentParser(description="transcribes arff to ipal")
    parser.add_argument(
        "input_file", type=Path, help="input arff file in plain text or gzip format",
    )
    parser.add_argument(
        "-o",
        "--output-file",
        type=Path,
        help="specify a file where the output should be saved, defaults to stdout",
    )
    args = parser.parse_args()

    # loop variables
    data_section = False
    attribute_list = []
    attribute_regex = re.compile("@attribute '([^']+)'")
    running_id = 0

    with open_file(args.input_file, "rt") as f_in, (
        open_file(args.output_file, "wt")
        if args.output_file is not None
        else sys.stdout
    ) as f_out:
        for l in f_in:
            l = l.strip()

            if not data_section:
                # header section
                if match := attribute_regex.match(l):
                    attribute_list.append(match.group(1))
                elif l == "@data":
                    data_section = True
            else:
                # data section
                l = l.split(",")
                # parses the data into dict with attribute name as key
                parsed = {name: value for (name, value) in zip(attribute_list, l)}

                data = {}
                for (arff_name, ipal_config) in ipal_data_config.items():
                    value = parsed[arff_name]
                    if value != "?":
                        data[ipal_config["name"]] = (
                            ipal_config["function"](value)
                            if "function" in ipal_config
                            else value
                        )

                out = {
                    "src": int(parsed["address"]),
                    "dest": int(parsed["address"]),
                    "timestamp": float(parsed["time"]),
                    "activity": int(parsed["command response"]),
                    "type": int(parsed["function"]),
                    "malicious": int(parsed["specific result"]) != 0,
                    "attack-details": f'{parsed["categorized result"]};{parsed["specific result"]}',
                    "protocol": "modbus",
                    "length": int(parsed["length"], 16),
                    "crc": int(parsed["crc rate"]),
                    "data": data,
                }

                running_id += 1
                f_out.write(json.dumps(out))
                f_out.write("\n")


if __name__ == "__main__":
    main()
