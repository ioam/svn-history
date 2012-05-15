""" 
../../topographica topo_analysis.py
"""
import os, random, numpy
import topo

from dispatch import QLauncher, TaskLauncher, Spec, LinearSpecs, ListSpecs
from dispatch.topographica import TopoRunBatchAnalysis, TopoRunBatchCommand, topo_batch_analysis


CLUSTER = True
if CLUSTER:  Launcher = QLauncher; batch_name = 'topo_analysis_cluster'
else:        Launcher = TaskLauncher; batch_name = 'topo_analysis_local'


############
# Analysis #
############

from collections import defaultdict

def V1_mean_activity():  return numpy.mean(topo.sim['V1'].activity)

def retina_std_activity(): return numpy.std(topo.sim['Retina'].activity)

def OR_plotgroup(): 
    from topo.command.analysis import save_plotgroup
    save_plotgroup("Orientation Preference",use_cached_results=True)

def activity_plotgroup(): 
    from topo.command.analysis import save_plotgroup
    save_plotgroup("Activity")

def V1_reduce(map_data, root_directory):      
    import pylab
    time1_rd2 = [(float(spec['cortex_density']), v) for  (v, t, spec) in map_data 
                 if ((t==1) and (spec['retina_density'] == '2.0000'))]

    cortex_density, activities = zip(*sorted(time1_rd2))
    pylab.plot(cortex_density, activities)
    
    pylab.title('Mean activity (cortex) again cortex density at time = 1.0 for retina density=2')
    figure_path = os.path.join(root_directory, 'cluster_figures')
    try: os.mkdir(figure_path)
    except :pass
    pylab.savefig(os.path.join(figure_path, 'rd2_mean_activity.png'))
    print "Saved figure rd2_mean_activity.png in folder cluster_figures"

# Data is of form [<(<value>, <topo_time>, <spec>)>]
def retina_reduce(map_data,root_directory):  
    time1_rd2 = [(float(spec['cortex_density']), v) for  (v, t, spec) in map_data 
                 if ((t==1) and (spec['retina_density'] == '2.0000'))]

    print "Average activity standard deviation in retina across cortex density for retina density of 2.0: "
    print numpy.mean(time1_rd2)

#########
# Batch #
#########

# Normally in Topographica, the prefix is set to the Documents subdirectory of home (by default)
output_directory = os.path.join(os.getcwd(), 'Demo_Output')
@topo_batch_analysis(Launcher, output_directory, review=True)
def topo_analysis():
    cross_product_densities = (LinearSpecs("retina_density", 2,7,3) 
                               * LinearSpecs("cortex_density", 1,6,3, fp_precision=2))

    run_batch_spec = Spec(times=[1,5,10], 
                          rationale='Avoiding default of 10000 iterations for testing purposes.')

    # Completed Specifier
    combined_spec = run_batch_spec * cross_product_densities    

    # Command
    run_batch_command = TopoRunBatchCommand('../../../examples/tiny.ty', analysis='TopoRunBatchAnalysis')
    run_batch_command.allowed_list = ['retina_density','cortex_density', 'times']

    run_batch_command.name_time_format = '%d-%m-%Y@%H%M'
    run_batch_command.param_formatter.abbreviations = {'retina_density':'rd', 'cortex_density':'cd'}

    # Launcher
    tasklauncher = Launcher(batch_name,combined_spec,run_batch_command)
    tasklauncher.print_info = 'stdout'
    # tasklauncher.timestamp_format = None

    # Analysis
    batch_analysis = TopoRunBatchAnalysis()
    # Adding map functions
    batch_analysis.add_map_fn(OR_plotgroup, 'A recording orientation preference in tiny.ty because...')
    batch_analysis.add_map_fn(activity_plotgroup, 'Record of sheet activities in tiny.ty because...')
    # Adding map-reduce function
    batch_analysis.add_map_reduce_fn(V1_mean_activity, V1_reduce, 
                                     ' The mean V1 activity is processed by... ')
    batch_analysis.add_map_reduce_fn(retina_std_activity, retina_reduce, 
                                     ' The standard deviation of retina activity is.... ')

    return (tasklauncher, batch_analysis)

