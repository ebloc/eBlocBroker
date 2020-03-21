#!/bin/bash
#SBATCH -o slurm.out        # STDOUT
#SBATCH -e slurm.err        # STDERR
#SBATCH --mail-type=ALL

hostname > completed.txt
uptime >> completed.txt
echo ENDED >> completed.txt
