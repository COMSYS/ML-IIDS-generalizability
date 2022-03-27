#!/usr/bin/env zsh

#SBATCH --array=1-35
#SBATCH --cpus-per-task=5
#SBATCH --mem=8G
#SBATCH --output=../../data/%A_rf-type-%a.out

### begin of executable commands
export PATH="/opt/kus/miniconda3/envs/ml-and-ids/bin:$PATH"

echo "SLURM_JOB: $SLURM_ARRAY_JOB_ID"
echo "Omit attacks experiment: type $SLURM_ARRAY_TASK_ID/35"
echo ""

\time -f "\nTime elapsed:\t%E\nMax memory use:\t%M KB" \
    ./run-experiment.sh \
    -c rf \
    -t $SLURM_ARRAY_TASK_ID \
    -p "$(printf "../../data/%s_rf-type-%02d" "${SLURM_ARRAY_JOB_ID}" "${SLURM_ARRAY_TASK_ID}")"
