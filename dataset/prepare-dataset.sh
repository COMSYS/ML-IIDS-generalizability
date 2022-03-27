#!/usr/bin/env bash
# ----------------------------------------------------------------------------
# This script prepares the source dataset as follows:
# 1. It transcribes the Morris Arff dataset to IPAL using the
#    `transcribe-to-ipal.py` script.
# 2. It runs the `preprocess-dataset.py` script which preprocesses features of
#    the dataset and adds cached state.
# 3. It splits it into 5 parts of equal size to be used with cross-validation.
#
# Parameters:
#     -d    Sets the path to the source dataset (in Arff format) to be used.
# ----------------------------------------------------------------------------

set -e
set -o pipefail

# --- Option processing ------------------------------------------------------
usage() {
    echo "Usage: $0 -d <source dataset file>" 1>&2
    exit 1
}

while getopts d: flag; do
    case "${flag}" in
    # custom dataset file path
    d) SOURCE_DATASET=${OPTARG} ;;
    *) usage ;;
    esac
done
echo "SOURCE_DATASET: ${SOURCE_DATASET}"
echo ""

if [ -z "${SOURCE_DATASET}" ]; then
    usage
fi

# --- Transcribe to IPAL -----------------------------------------------------
echo "Transcribing dataset to IPAL..."

../scripts/transcribe-to-ipal.py \
    -o dataset.ipal \
    "${SOURCE_DATASET}"

# --- Prepare dataset --------------------------------------------------------
echo "Preparing dataset..."

../scripts/preprocess-dataset.py \
    -i dataset.ipal \
    -o dataset-processed.ipal
# first 4 messages are always skipped due to incomplete state
tail -n +5 dataset-processed.ipal >dataset.ipal
rm dataset-processed.ipal

# --- Splitting dataset ------------------------------------------------------
echo "Shuffling and splitting dataset..."

../scripts/split-dataset.py \
    -i dataset.ipal \
    -n 5 \
    -m sequence-of-four \
    -o "part-"

rm dataset.ipal
gzip -f part*.ipal

echo "Done"
