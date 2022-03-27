#!/usr/bin/env zsh

#SBATCH --cpus-per-task=5
#SBATCH --mem=16G
#SBATCH --output=../../data/%A_svm-baseline.out

### begin of executable commands
export PATH="/opt/kus/miniconda3/envs/ml-and-ids/bin:$PATH"

echo "SLURM_JOB: $SLURM_JOB_ID"
echo "Omit attacks experiment: baseline"
echo ""

\time -f "\nTime elapsed:\t%E\nMax memory use:\t%M KB" \
    ./run-experiment.sh \
    -c svm \
    -p "../../data/${SLURM_JOB_ID}_svm-baseline"
