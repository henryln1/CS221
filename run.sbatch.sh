#!/bin/bash 

#all commands that start with SBATCH contain commands that are just used by SLURM for scheduling  
#################
#set a job name  
#SBATCH --job-name=221
#################  
#a file for job output, you can check job progress
#SBATCH --output=221_${file}.out
#################
# a file for errors from the job
#SBATCH --error=221_${file}.err
#################
#time you think you need; default is one hour
#in minutes in this case, hh:mm:ss
#SBATCH --time=24:00:00
#################
#quality of service; think of it as job priority
#SBATCH --qos=normal
#################
#SBATCH --mem=16000
#################

#SBATCH --mail-type=END,FAIL # notifications for job done & fail
#SBATCH --mail-user=henryln1@stanford.edu

module load python

python readData.py recipes.csv full_format_recipes.json testIngredientsBigger.txt