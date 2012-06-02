#$ -S /bin/bash
#$ -cwd 

#USAGE: you can add as many parameter combination to the arguments list as you want.
#Further parameters can be adjusted in the args line (4th from bottom, refer to topographica run_batch method for details)
# This script basicly gets a command line number I and than runs topographica batch command with the Ith parameter list in the arguments list

argsprefix=""
echo $argsprefix
let "a=RANDOM/160"
sleep $a

arguments=(
"default_density=96,CS=0.5,LatLGNStr=0.6,SurrSize=0.25,ti=0.15,aff_str=1.5,MU=0.024,tracking=False,lat_inh_lr=0.3,intrinsic_noise=0.0,exc_strength=1.7,dataset='Gaussian',scale=0.1,scaling=False,inh_strength=1.4,Adaptation='Absolute',GC=True,ah=False"
"default_density=96,CS=0.5,LatLGNStr=0.6,SurrSize=0.25,ti=0.15,aff_str=1.5,MU=0.024,tracking=False,lat_inh_lr=0.3,intrinsic_noise=0.0,exc_strength=1.7,dataset='Gaussian',scale=0.2,scaling=False,inh_strength=1.4,Adaptation='Absolute',GC=True,ah=False"
"default_density=96,CS=0.5,LatLGNStr=0.6,SurrSize=0.25,ti=0.15,aff_str=1.5,MU=0.024,tracking=False,lat_inh_lr=0.3,intrinsic_noise=0.0,exc_strength=1.7,dataset='Gaussian',scale=0.3,scaling=False,inh_strength=1.4,Adaptation='Absolute',GC=True,ah=False"
"default_density=96,CS=0.5,LatLGNStr=0.6,SurrSize=0.25,ti=0.15,aff_str=1.5,MU=0.024,tracking=False,lat_inh_lr=0.3,intrinsic_noise=0.0,exc_strength=1.7,dataset='Gaussian',scale=0.4,scaling=False,inh_strength=1.4,Adaptation='Absolute',GC=True,ah=False"
"default_density=96,CS=0.5,LatLGNStr=0.6,SurrSize=0.25,ti=0.15,aff_str=1.5,MU=0.024,tracking=False,lat_inh_lr=0.3,intrinsic_noise=0.0,exc_strength=1.7,dataset='Gaussian',scale=0.5,scaling=False,inh_strength=1.4,Adaptation='Absolute',GC=True,ah=False"
"default_density=96,CS=0.5,LatLGNStr=0.6,SurrSize=0.25,ti=0.15,aff_str=1.5,MU=0.024,tracking=False,lat_inh_lr=0.3,intrinsic_noise=0.0,exc_strength=1.7,dataset='Gaussian',scale=0.6,scaling=False,inh_strength=1.4,Adaptation='Absolute',GC=True,ah=False"
"default_density=96,CS=0.5,LatLGNStr=0.6,SurrSize=0.25,ti=0.15,aff_str=1.5,MU=0.024,tracking=False,lat_inh_lr=0.3,intrinsic_noise=0.0,exc_strength=1.7,dataset='Gaussian',scale=0.7,scaling=False,inh_strength=1.4,Adaptation='Absolute',GC=True,ah=False"
"default_density=96,CS=0.5,LatLGNStr=0.6,SurrSize=0.25,ti=0.15,aff_str=1.5,MU=0.024,tracking=False,lat_inh_lr=0.3,intrinsic_noise=0.0,exc_strength=1.7,dataset='Gaussian',scale=0.8,scaling=False,inh_strength=1.4,Adaptation='Absolute',GC=True,ah=False"
"default_density=96,CS=0.5,LatLGNStr=0.6,SurrSize=0.25,ti=0.15,aff_str=1.5,MU=0.024,tracking=False,lat_inh_lr=0.3,intrinsic_noise=0.0,exc_strength=1.7,dataset='Gaussian',scale=0.9,scaling=False,inh_strength=1.4,Adaptation='Absolute',GC=True,ah=False"
"default_density=96,CS=0.5,LatLGNStr=0.6,SurrSize=0.25,ti=0.15,aff_str=1.5,MU=0.024,tracking=False,lat_inh_lr=0.3,intrinsic_noise=0.0,exc_strength=1.7,dataset='Gaussian',scale=1.0,scaling=False,inh_strength=1.4,Adaptation='Absolute',GC=True,ah=False"
"default_density=96,CS=0.5,LatLGNStr=0.6,SurrSize=0.25,ti=0.15,aff_str=1.5,MU=0.024,tracking=False,lat_inh_lr=0.3,intrinsic_noise=0.0,exc_strength=1.7,dataset='Gaussian',scale=1.2,scaling=False,inh_strength=1.4,Adaptation='Absolute',GC=True,ah=False"
"default_density=96,CS=0.5,LatLGNStr=0.6,SurrSize=0.25,ti=0.15,aff_str=1.5,MU=0.024,tracking=False,lat_inh_lr=0.3,intrinsic_noise=0.0,exc_strength=1.7,dataset='Gaussian',scale=1.4,scaling=False,inh_strength=1.4,Adaptation='Absolute',GC=True,ah=False"
"default_density=96,CS=0.5,LatLGNStr=0.6,SurrSize=0.25,ti=0.15,aff_str=1.5,MU=0.024,tracking=False,lat_inh_lr=0.3,intrinsic_noise=0.0,exc_strength=1.7,dataset='Gaussian',scale=1.6,scaling=False,inh_strength=1.4,Adaptation='Absolute',GC=True,ah=False"
"default_density=96,CS=0.5,LatLGNStr=0.6,SurrSize=0.25,ti=0.15,aff_str=1.5,MU=0.024,tracking=False,lat_inh_lr=0.3,intrinsic_noise=0.0,exc_strength=1.7,dataset='Gaussian',scale=1.8,scaling=False,inh_strength=1.4,Adaptation='Absolute',GC=True,ah=False"
"default_density=96,CS=0.5,LatLGNStr=0.6,SurrSize=0.25,ti=0.15,aff_str=1.5,MU=0.024,tracking=False,lat_inh_lr=0.3,intrinsic_noise=0.0,exc_strength=1.7,dataset='Gaussian',scale=2.0,scaling=False,inh_strength=1.4,Adaptation='Absolute',GC=True,ah=False"
"default_density=96,CS=0.5,LatLGNStr=0.6,SurrSize=0.25,ti=0.15,aff_str=1.5,MU=0.024,tracking=False,lat_inh_lr=1.0,intrinsic_noise=0.0,exc_strength=1.7,dataset='Gaussian',scale=0.1,scaling=False,inh_strength=1.4,Adaptation='Absolute',GC=True,ah=False"
"default_density=96,CS=0.5,LatLGNStr=0.6,SurrSize=0.25,ti=0.15,aff_str=1.5,MU=0.024,tracking=False,lat_inh_lr=1.0,intrinsic_noise=0.0,exc_strength=1.7,dataset='Gaussian',scale=0.2,scaling=False,inh_strength=1.4,Adaptation='Absolute',GC=True,ah=False"
"default_density=96,CS=0.5,LatLGNStr=0.6,SurrSize=0.25,ti=0.15,aff_str=1.5,MU=0.024,tracking=False,lat_inh_lr=1.0,intrinsic_noise=0.0,exc_strength=1.7,dataset='Gaussian',scale=0.3,scaling=False,inh_strength=1.4,Adaptation='Absolute',GC=True,ah=False"
"default_density=96,CS=0.5,LatLGNStr=0.6,SurrSize=0.25,ti=0.15,aff_str=1.5,MU=0.024,tracking=False,lat_inh_lr=1.0,intrinsic_noise=0.0,exc_strength=1.7,dataset='Gaussian',scale=0.4,scaling=False,inh_strength=1.4,Adaptation='Absolute',GC=True,ah=False"
"default_density=96,CS=0.5,LatLGNStr=0.6,SurrSize=0.25,ti=0.15,aff_str=1.5,MU=0.024,tracking=False,lat_inh_lr=1.0,intrinsic_noise=0.0,exc_strength=1.7,dataset='Gaussian',scale=0.5,scaling=False,inh_strength=1.4,Adaptation='Absolute',GC=True,ah=False"
"default_density=96,CS=0.5,LatLGNStr=0.6,SurrSize=0.25,ti=0.15,aff_str=1.5,MU=0.024,tracking=False,lat_inh_lr=1.0,intrinsic_noise=0.0,exc_strength=1.7,dataset='Gaussian',scale=0.6,scaling=False,inh_strength=1.4,Adaptation='Absolute',GC=True,ah=False"
"default_density=96,CS=0.5,LatLGNStr=0.6,SurrSize=0.25,ti=0.15,aff_str=1.5,MU=0.024,tracking=False,lat_inh_lr=1.0,intrinsic_noise=0.0,exc_strength=1.7,dataset='Gaussian',scale=0.7,scaling=False,inh_strength=1.4,Adaptation='Absolute',GC=True,ah=False"
"default_density=96,CS=0.5,LatLGNStr=0.6,SurrSize=0.25,ti=0.15,aff_str=1.5,MU=0.024,tracking=False,lat_inh_lr=1.0,intrinsic_noise=0.0,exc_strength=1.7,dataset='Gaussian',scale=0.8,scaling=False,inh_strength=1.4,Adaptation='Absolute',GC=True,ah=False"
"default_density=96,CS=0.5,LatLGNStr=0.6,SurrSize=0.25,ti=0.15,aff_str=1.5,MU=0.024,tracking=False,lat_inh_lr=1.0,intrinsic_noise=0.0,exc_strength=1.7,dataset='Gaussian',scale=0.9,scaling=False,inh_strength=1.4,Adaptation='Absolute',GC=True,ah=False"
"default_density=96,CS=0.5,LatLGNStr=0.6,SurrSize=0.25,ti=0.15,aff_str=1.5,MU=0.024,tracking=False,lat_inh_lr=1.0,intrinsic_noise=0.0,exc_strength=1.7,dataset='Gaussian',scale=1.0,scaling=False,inh_strength=1.4,Adaptation='Absolute',GC=True,ah=False"
"default_density=96,CS=0.5,LatLGNStr=0.6,SurrSize=0.25,ti=0.15,aff_str=1.5,MU=0.024,tracking=False,lat_inh_lr=1.0,intrinsic_noise=0.0,exc_strength=1.7,dataset='Gaussian',scale=1.2,scaling=False,inh_strength=1.4,Adaptation='Absolute',GC=True,ah=False"
"default_density=96,CS=0.5,LatLGNStr=0.6,SurrSize=0.25,ti=0.15,aff_str=1.5,MU=0.024,tracking=False,lat_inh_lr=1.0,intrinsic_noise=0.0,exc_strength=1.7,dataset='Gaussian',scale=1.4,scaling=False,inh_strength=1.4,Adaptation='Absolute',GC=True,ah=False"
"default_density=96,CS=0.5,LatLGNStr=0.6,SurrSize=0.25,ti=0.15,aff_str=1.5,MU=0.024,tracking=False,lat_inh_lr=1.0,intrinsic_noise=0.0,exc_strength=1.7,dataset='Gaussian',scale=1.6,scaling=False,inh_strength=1.4,Adaptation='Absolute',GC=True,ah=False"
"default_density=96,CS=0.5,LatLGNStr=0.6,SurrSize=0.25,ti=0.15,aff_str=1.5,MU=0.024,tracking=False,lat_inh_lr=1.0,intrinsic_noise=0.0,exc_strength=1.7,dataset='Gaussian',scale=1.8,scaling=False,inh_strength=1.4,Adaptation='Absolute',GC=True,ah=False"
"default_density=96,CS=0.5,LatLGNStr=0.6,SurrSize=0.25,ti=0.15,aff_str=1.5,MU=0.024,tracking=False,lat_inh_lr=1.0,intrinsic_noise=0.0,exc_strength=1.7,dataset='Gaussian',scale=2.0,scaling=False,inh_strength=1.4,Adaptation='Absolute',GC=True,ah=False")

echo $argsprefix

args='import matplotlib; matplotlib.use("Agg"); from topo.command.basic import run_batch ; import contrib.jaanalysis; run_batch("./contrib/gc_alissom.ty",analysis_fn=contrib.jaanalysis.gc_homeo_af,output_directory="/exports/informatics/inf_ianc/s0570140/GC_ALISSOM_Job_RENEWED_LL/",times=[2,1000,2000,3000,4000,5000,6000,7000,8000,9000,10000,11000,12000,13000,14000,15000,16000,17000,18000,19000,20000,20001],snapshot=False,dirname_prefix='
a="$args $1 , $argsprefix ${arguments[$1]}  )"
echo "${a}"
/exports/informatics/inf_ianc/s0570140/topographica/topographica  -c "${a}"

 

