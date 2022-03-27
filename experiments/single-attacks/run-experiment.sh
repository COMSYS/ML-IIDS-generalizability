#!/usr/bin/env bash
# ----------------------------------------------------------------------------
# This script runs one single attacks experiment consisting of 5 folds.
#
# Parameters:
#     -c    Sets the classifier to be used: rf, svm or blstm.
#     -t    Sets one or multiple special anomaly/attack types. Attacks of
#           this type will be the only attack types present in the train
#           set. All other attacks will only be in the test set.
#     -s    Sets one or multiple special anomaly/attack categories. Attacks of
#           this category will be the only attack types present in the train
#           set. All other attacks will only be in the test set.
#     -p    [Optional] Sets a custom prefix for all created files created
#           files. Defaults to the current timestamp.
# ----------------------------------------------------------------------------

set -e
set -o pipefail

# --- Option processing ------------------------------------------------------
usage() {
    echo "Usage: $0 -c <rf|svm|blstm> [-t <attack type>] [-s <attack category>] [-p <string>]" 1>&2
    exit 1
}

PREFIX="../../data/$(date +"%s")"
while getopts c:t:s:m:p: flag; do
    case "${flag}" in
    # config file which is fed to metaids
    c) CLASSIFIER=${OPTARG} ;;
    # which anomaly types should not appear in the train set
    t) SPECIAL_TYPES="${SPECIAL_TYPES}${OPTARG} " ;;
    # which anomaly categories should not appear in the train set
    s) SPECIAL_CATEGORIES="${SPECIAL_CATEGORIES}${OPTARG} " ;;
    # string prefix for all created files
    p) PREFIX=${OPTARG} ;;
    *) usage ;;
    esac
done

if [ -z "${CLASSIFIER}" ]; then
    usage
fi

# when none of the arguments is given, we go into the special categories
# branch where nothing is considered special anomaly.
if [[ ! -z "$SPECIAL_TYPES" ]] && [[ ! -z "$SPECIAL_CATEGORIES" ]]; then
    echo "Arguments '-t' and '-s' can not be used simultaneously"
    exit 1
fi

case "${CLASSIFIER}" in
"rf")
    IDS_CONFIG="../../config/rf-arff.config"
    FILTER_MODE="packet-by-packet"
    ;;
"svm")
    IDS_CONFIG="../../config/svm-arff.config"
    FILTER_MODE="packet-by-packet"
    ;;
"blstm")
    IDS_CONFIG="../../config/blstm-arff.config"
    FILTER_MODE="sequence-of-four"
    ;;
*)
    echo "Unrecognized classifier ${CLASSIFIER}"
    usage
    ;;
esac

echo "EXPERIMENT: Exclusively train special attacks"
echo "CLASSIFIER: $CLASSIFIER"
echo "IDS_CONFIG: $IDS_CONFIG"
echo "FILTER_MODE: $FILTER_MODE"
echo "SPECIAL_TYPES: $SPECIAL_TYPES"
echo "SPECIAL_CATEGORIES: $SPECIAL_CATEGORIES"
echo "OUTPUT_PREFIX: $PREFIX"
echo ""

DATASET_FOLDER="../../dataset"
FILTER_CMD="../../scripts/filter-dataset.py -m ${FILTER_MODE}"
METAIDS_CMD="ipal-iids"
EXTEND_ALARMS_CMD="ipal-extend-alarms"

# --- Main fold function -----------------------------------------------------
run_one_fold() {
    # --- Initialize ---------------------------------------------------------
    local FOLD_INDEX="$1"

    if [[ -z "${FOLD_INDEX}" ]]; then
        echo "FOLD_INDEX must be supplied to run_one_fold()" 1>&2
        exit 1
    fi

    # Select train and test sets
    local TRAIN_SET_PARTS=("part-0.ipal.gz" "part-1.ipal.gz" "part-2.ipal.gz" "part-3.ipal.gz" "part-4.ipal.gz")
    local TEST_SET_PART="${TRAIN_SET_PARTS[FOLD_INDEX]}"
    unset TRAIN_SET_PARTS[$FOLD_INDEX]
    echo "TRAIN_SET_PARTS: ${TRAIN_SET_PARTS[@]}"
    echo "TEST_SET_PART: ${TEST_SET_PART}"

    # Files for a fold get a suffix
    local FOLD_PREFIX="${PREFIX}_fold-${FOLD_INDEX}"
    local TRAIN_SET="${FOLD_PREFIX}.dataset-train.ipal"
    local TEST_SET="${FOLD_PREFIX}.dataset-test.ipal"

    # --- Filter dataset -----------------------------------------------------
    rm -f "${TRAIN_SET}" "${TEST_SET}"

    if [[ ! -z "$SPECIAL_TYPES" ]]; then
        echo "Filtering dataset based on special types"

        # Prepare the train set: merge all parts meant to go to the train set.
        # Keep only attacks of "special type" from them and move the rest to the test set.
        for part in "${TRAIN_SET_PARTS[@]}"; do
            $FILTER_CMD \
                -i "${DATASET_FOLDER}/${part}" \
                --only-types $SPECIAL_TYPES 0 >>"${TRAIN_SET}"

            $FILTER_CMD \
                -i "${DATASET_FOLDER}/${part}" \
                --except-types $SPECIAL_TYPES 0 >>"${TEST_SET}"
        done
    elif [[ ! -z "$SPECIAL_CATEGORIES" ]]; then
        echo "Filtering dataset based on special categories"

        # Prepare the train set: merge all parts meant to go to the train set.
        # Keep only attacks of "special type" from them and move the rest to the test set.
        for part in "${TRAIN_SET_PARTS[@]}"; do
            $FILTER_CMD \
                -i "${DATASET_FOLDER}/${part}" \
                --only-categories $SPECIAL_CATEGORIES 0 >>"${TRAIN_SET}"

            $FILTER_CMD \
                -i "${DATASET_FOLDER}/${part}" \
                --except-categories $SPECIAL_CATEGORIES 0 >>"${TEST_SET}"
        done
    else
        echo "Preparing baseline run"

        for part in "${TRAIN_SET_PARTS[@]}"; do
            zcat "${DATASET_FOLDER}/${part}" >>"${TRAIN_SET}"
        done
    fi

    # Prepare the test set
    zcat "${DATASET_FOLDER}/${TEST_SET_PART}" >>"${TEST_SET}"

    # Compress
    gzip -f "${TRAIN_SET}" "${TEST_SET}"

    # --- Run classifier -----------------------------------------------------
    echo "Running classifier..."
    local OUTPUT_FILE="${FOLD_PREFIX}.dataset-live-output.ipal.gz"
    local STATS_FILE="${FOLD_PREFIX}.statistics.json"
    local FILTERED_STATS_FILE="${FOLD_PREFIX}.statistics-filtered.json"
    local CONFIG_FILE="${FOLD_PREFIX}.config"

    # MODEL_FILE is used in envsubst and hence needs to be exported
    export MODEL_FILE="$(realpath ${FOLD_PREFIX}.model.pickle)"
    # Insert the 'model-file' value into the config file using envsubst
    cat "${IDS_CONFIG}" | envsubst '${MODEL_FILE}' >"${CONFIG_FILE}"

    "${METAIDS_CMD}" \
        --config "${CONFIG_FILE}" \
        --train.ipal "${TRAIN_SET}.gz" \
        --live.ipal "${TEST_SET}.gz" \
        --output "${OUTPUT_FILE}" \
        --log info \
        --retrain

    rm -f "${TRAIN_SET}.gz" "${TEST_SET}.gz"

    # BLSTM requires a special post-processing step to add its output to every packet
    if [ "${CLASSIFIER}" == "blstm" ]; then
        "${EXTEND_ALARMS_CMD}" "${OUTPUT_FILE}"
    fi

    # --- Create statistics --------------------------------------------------
    echo "Calculating statistics..."
    ../../scripts/create-statistics.py \
        -o "${STATS_FILE}" \
        -i "${OUTPUT_FILE}"

    # Calculate statistics over the _filtered_ test set, meaning the test set with the same filter
    # applied as during training.
    # if [[ ! -z "$SPECIAL_TYPES" ]]; then
    #     ../../scripts/filter-dataset.py \
    #         -m "packet-by-packet" \
    #         -i "${OUTPUT_FILE}" \
    #         --only-types $SPECIAL_TYPES 0 |
    #         ../../scripts/create-statistics.py \
    #             -o "${FILTERED_STATS_FILE}"
    # else
    #     ../../scripts/filter-dataset.py \
    #         -m "packet-by-packet" \
    #         -i "${OUTPUT_FILE}" \
    #         --only-categories $SPECIAL_CATEGORIES 0 |
    #         ../../scripts/create-statistics.py \
    #             -o "${FILTERED_STATS_FILE}"
    # fi
}

# --- Execute all 5 folds ----------------------------------------------------
for i in {0..4}; do
    echo "--------------------------------------------------------------------"
    echo "Running fold $((i + 1))/5 - $(date)"
    echo "--------------------------------------------------------------------"
    echo ""
    run_one_fold $i
    echo ""
done

echo "--------------------------------------------------------------------"
echo "All folds completed - $(date)"
echo "--------------------------------------------------------------------"
