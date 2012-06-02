import os
import topo

from dispatch import QLauncher, TaskLauncher, Spec, LinearSpecs, ListSpecs
from dispatch.topographica import TopoRunBatchAnalysis, TopoRunBatchCommand, topo_batch_analysis

from jan_run.jaanalysis import gc_homeo_af #complex_analysis_function


CLUSTER = False
if CLUSTER:  Launcher = QLauncher; batch_name = 'gcal_cluster'
else:        Launcher = TaskLauncher; batch_name = 'gcal_local'



# Warnings:
# Time: 000000.00 HomeostaticResponse00290: Warning: Setting non-parameter attribute eta=0.001 using a mechanism intended only for parameters

# eta -> learning_rate ???

# Time: 000000.00 HomeostaticResponse00290: Warning: Setting non-parameter attribute input_output_ratio=4.2 using a mechanism intended only for parameters

# input_output_ratio -> target_activity ???
# 1 / 4.2 = 0.23809523809523808
# target_activity = param.Number(default=0.024,doc="""
# The target average activity.""")


# Warning: Setting non-Parameter class attribute FeatureResponses.num_repetitions = 10 
# Warning: Setting non-Parameter class attribute FeatureMaps.selectivity_multiplier = 2.0 



output_directory = os.path.join(os.getcwd(), 'GCAL')
@topo_batch_analysis(Launcher, output_directory, review=True)
def gcal_paper():
    scalespecs = (LinearSpecs('scale', 0.1, 0.9, 9, fp_precision=1) 
                  + LinearSpecs('scale', 1.0, 2.0, 7, fp_precision=1))
    scalespecs.rationale = 'For some reason the scale step size is not always constant.'
    lat_inh_lrspecs = LinearSpecs('lat_inh_lr', 0.3, 1.0, fp_precision=1)

    # *Equivalently*
    # scalespecs = ListSpecs('scale', 
    #                        [0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9]+[1.0,1.2,1.4,1.6,1.8,1.9,2.0],
    #                        fp_precision=1)
    # lat_inh_lrspecs = ListSpecs('lat_inh_lr', [0.3, 1.0], fp_precision=1)

    cartesian_product = scalespecs * lat_inh_lrspecs

    run_batch_settings = Spec(times=[1,5,10], 
                              rationale='Avoiding default of 10000 iterations for testing purposes.')

    constant_params = Spec(default_density=96,
                           CS=0.5,
                           LatLGNStr=0.6,
                           SurrSize=0.25,
                           ti=0.15,
                           aff_str=1.5,
                           MU=0.024,
                           tracking=False,
                           intrinsic_noise=0.0,
                           exc_strength=1.7,
                           dataset='Gaussian',
                           scaling=False,
                           inh_strength=1.4,
                           fp_precision=1)

    
    GCAL_components = Spec(Adaptation='Absolute',  GC=True, ah=False)

    constant_spec = constant_params * run_batch_settings * GCAL_components
    constant_spec.rationale = 'Bit confused why GCAL_components constant -is the idea not to change these?'
    combined_spec = constant_spec * cartesian_product 

    # Command
    run_batch_command = TopoRunBatchCommand('./jan_run/gc_alissom.ty',analysis='TopoRunBatchAnalysis')

    # Launcher

    qsub_settings = dict(w='w', P='inf_ndtc', l='h_rt=47:50:0', R='y') # Need to read-up on theses...

    tasklauncher = Launcher(batch_name,combined_spec,run_batch_command)
    tasklauncher.print_info = 'stdout'
    tasklauncher.tag = '[gcal_paper]'

    # Analysis
    batch_analysis = TopoRunBatchAnalysis()
    batch_analysis.add_map_fn(gc_homeo_af, 'Supplied by Jan Antolik')
    return (tasklauncher, batch_analysis)




#!/bin/bash

# Usage: ./my-qsub-for-jl.sh number_of_processes_to_run
# the number_of_processes_to_run should correspond to the number of parameter combinations that you want to run from the file ./gc_alissom_job.sh (from top of course)

#for ((i=0;i<=($1-1);i+=1)); do
#   qsub -w w -P inf_ndtc -l h_rt=47:50:0  -R y ./gc_alissom_job.sh $i       
#   sleep 10
#done



# Constant:
# default_density=96
# CS=0.5
# LatLGNStr=0.6
# SurrSize=0.25
# ti=0.15
# aff_str=1.5
# MU=0.024
# tracking=False
# intrinsic_noise=0.0
# exc_strength=1.7
# dataset='Gaussian'
# scaling=False
# inh_strength=1.4

# HUH?
# Adaptation='Absolute'
# GC=True
# ah=False

# Changing [THIS IS A CARTESIAN-PRODUCT]
# scale=[0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9]+[1.0,1.2,1.4,1.6,1.8,1.9,2.0]
# lat_inh_lr = [0.3, 1.0]


#args='import matplotlib; matplotlib.use("Agg"); from topo.command.basic import run_batch ; import contrib.jaanalysis; run_batch("./contrib/gc_alissom.ty",analysis_fn=contrib.jaanalysis.gc_homeo_af,output_directory="/exports/informatics/inf_ianc/s0570140/GC_ALISSOM_Job_RENEWED_LL/",times=[2,1000,2000,3000,4000,5000,6000,7000,8000,9000,10000,11000,12000,13000,14000,15000,16000,17000,18000,19000,20000,20001],snapshot=False,dirname_prefix=' 
# STRING REALLY ENDS HERE

# NEW VARIABLE concat of (args + '' + ALL THE KWARGS)
# a="$args $1 , $argsprefix ${arguments[$1]}  )" 

# $1 selects out of list
# argsprefix is empty.
