import sys
import gzip


def eprint(*args):
    print(*args, file=sys.stderr)


def open_file(filepath, mode):
    return (gzip.open if filepath.suffix == ".gz" else open)(filepath, mode)


def get_attack_details(ipal_entry):
    """
    Parse the attack-details IPAL field.

    The field is expected to have the format "<attack category>;<attack type>".
    Example: "2;12".
    """
    split = ipal_entry["attack-details"].split(";")
    assert (
        len(split) == 2
    ), "'attack-details' field in IPAL has wrong format, expected 'attack category;attack type'"
    attack_category = int(split[0])
    attack_type = int(split[1])
    return attack_category, attack_type


def chunks(list, n):
    """
    Partition the list into successive n-sized chunks.
    https://stackoverflow.com/a/312464
    """
    for i in range(0, len(list), n):
        yield list[i : i + n]
