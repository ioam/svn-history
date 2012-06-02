#!/bin/bash

# Usage: ./my-qsub-for-jl.sh number_of_processes_to_run
# the number_of_processes_to_run should correspond to the number of parameter combinations that you want to run from the file ./gc_alissom_job.sh (from top of course)

for ((i=0;i<=($1-1);i+=1)); do
   qsub -w w -P inf_ndtc -l h_rt=47:50:0  -R y ./gc_alissom_job.sh $i       
   sleep 10
done
