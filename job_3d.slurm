#!/bin/bash
# Created by the VLSCI job script generator for SLURM on x86
# Sat Apr 19 2014 22:11:00 GMT+1000 (EST)

# check that the script is launched with sbatch
if [ "x$SLURM_JOB_ID" == "x" ]; then
   echo "You need to submit your job to the queuing system with sbatch"
   exit 1
fi

# Partition for the job:
#SBATCH -p main

# The name of the job:
#SBATCH --job-name="plot_doublets"

# Maximum number of CPU cores used by the job:
#SBATCH --ntasks=1

# The amount of memory in megabytes per process in the job:
#SBATCH --mem-per-cpu=10240

# Send yourself an email when the job:
# aborts abnormally (fails)
#SBATCH --mail-type=FAIL
# ends successfully
#SBATCH --mail-type=END

# The maximum running time of the job in days-hours:mins:sec
#SBATCH --time=0-24:0:00

# Run the job from the directory where it was launched (default):
# The modules to load:
module load python-gcc/2.7.5

# The job command(s):
#python dump_eic.py --mzml data/t30.mzML --hits data/results-neg-t30-lt500-64-1599744.list
python dump_3d.py --mzml data/t30.mzML --hits data/results-neg-t30-lt500-64-1114994-top100.list
