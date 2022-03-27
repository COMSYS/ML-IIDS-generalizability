#!/usr/bin/env zsh

#SBATCH --cpus-per-task=6
#SBATCH --mem=8G
#SBATCH --output=../../data/%A_blstm-baseline.out

### begin of executable commands
export PATH="/opt/kus/miniconda3/envs/ml-and-ids/bin:$PATH"

echo "SLURM_JOB: $SLURM_JOB_ID"
echo "Omit attacks experiment: baseline"
echo ""

\time -f "\nTime elapsed:\t%E\nMax memory use:\t%M KB" \
    ./run-experiment.sh \
    -c blstm \
    -p "../../data/${SLURM_JOB_ID}_blstm-baseline"
