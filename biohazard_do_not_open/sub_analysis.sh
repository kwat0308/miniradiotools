#!/bin/bash
#SBATCH --job-name=ana
#SBATCH --nodes=2
#SBATCH --cpus-per-task=12
#SBATCH --time=03:00:00
#SBATCH --tasks=2
######SBATCH --mem=50gb
######SBATCH --export=NONE
#######################SBATCH --gres=gpu:4

python3 /hkfs/home/project/hk-project-radiohfi/bg5912/virtual_env/lib/python3.8/site-packages/miniradiotools/biohazard_do_not_open/analysis.py /hkfs/work/workspace/scratch/bg5912-mysims/iron/sim_storage/inp/