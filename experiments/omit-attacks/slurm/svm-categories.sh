#!/usr/bin/env zsh

#SBATCH --array=1-7
#SBATCH --cpus-per-task=5
#SBATCH --mem=16G
#SBATCH --output=../../data/%A_svm-cat-%a.out

### begin of executable commands
export PATH="/opt/kus/miniconda3/envs/ml-and-ids/bin:$PATH"

echo "SLURM_JOB: $SLURM_ARRAY_JOB_ID"
echo "Omit attacks experiment: category $SLURM_ARRAY_TASK_ID/7"
echo ""

\time -f "\nTime elapsed:\t%E\nMax memory use:\t%M KB" \
    ./run-experiment.sh \
    -c svm \
    -s $SLURM_ARRAY_TASK_ID \
    -p "$(printf "../../data/%s_svm-cat-%02d" "${SLURM_ARRAY_JOB_ID}" "${SLURM_ARRAY_TASK_ID}")"
