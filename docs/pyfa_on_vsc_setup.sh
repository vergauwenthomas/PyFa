#!/usr/bin/env bash

module purge
module load Python/3.10.4-GCCcore-11.3.0 
module load Tkinter/3.10.4-GCCcore-11.3.0
module load GDAL/3.5.0-foss-2022a
module load R/4.2.1-foss-2022a

#Load the v-env
source /dodrio/scratch/projects/starting_2022_075/Software/PyFa/pyfa_env/bin/activate