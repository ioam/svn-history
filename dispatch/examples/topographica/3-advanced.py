""" 
../../topographica topo_analysis.py
"""
import os, random
import numpy as np
import topo

from dispatch import QLauncher, Launcher, Spec, LinearSpecs, ListSpecs
from dispatch.topographica import RunBatchAnalysis, RunBatchCommand, launch_batch_analysis

CLUSTER = False
if CLUSTER:  
    Launcher = QLauncher
    batch_name = 'topo_analysis_cluster'
else: 
    batch_name = 'topo_analysis_local'

############
# Analysis #
############

import logging
logging.basicConfig(level=logging.INFO)
from dispatch.utils import Collate, Select, PILImageLoader
from dispatch.pytables import PyTableUtils

def V1_mean_activity(times=None, **kwargs):  
    return np.mean(topo.sim['V1'].activity)

def retina_std_activity(times=None, **kwargs): 
    return np.std(topo.sim['Retina'].activity)

def OR_plotgroup(times=None, **kwargs): 
    from topo.command.analysis import save_plotgroup
    save_plotgroup("Orientation Preference",use_cached_results=True)

def activity_plotgroup(times=None, **kwargs): 
    from topo.command.analysis import save_plotgroup
    save_plotgroup("Activity")

def V1_reduce(info, activity_V1, accumulator):
    import pylab
    collation = Collate(*info, V1_activity=activity_V1)
    s = Select(collation)
    s.view(float_keys=['time', 'retina_density', 'cortex_density', 'V1_activity'])
    
    condition = (s.cortex_density > 0.5) & (s.retina_density == 2.0)
    pylab.plot(s[condition].V1_activity, s[condition].cortex_density)
    pylab.title('Mean activity (cortex) against cortex density at time = 1.0 for retina density=2')

    [root_directory, _] = info
    figure_path = os.path.join(root_directory, 'cluster_figures')
    try: os.mkdir(figure_path)
    except :pass
    pylab.savefig(os.path.join(figure_path, 'rd2_mean_activity.png'))
    print "Saved figure rd2_mean_activity.png in folder cluster_figures"
    return collation

def retina_reduce(info, activity_retina, collation):
    collation.insert_columns(retina_activity=activity_retina)
    s = Select(collation)
    s.view(int_keys=['time'], 
           float_keys=['retina_density', 'cortex_density', 'V1_activity', 'retina_activity'])

    condition = (s.retina_density > 2.0) & (s.time == 1)
    result = np.mean(s[condition].retina_activity)
    print "Average std. of retina activity vs cortex density for retina density of 2.0 (@time=1): %f" % result
    return collation

def empty_map(times=None, **kwargs): return None

def save_simulations(info, data, collation):
    # Collect files of interest....
    collation.extract_filelist('ORPref', 
                               ['*_t{tid}_*/*_{time:0>9.2f}_*Orientation_Preference.png'],
                               key_type={'time':float})
    collation.show()

    loader = PILImageLoader(['.png'], transform = lambda im: im.rotate(180))
    (images, metadata, labels) = collation.extract_files(loader, 'ORPref','ORPrefLabels')

    [root_directory, _] = info
    print "Saving all simulation results to HDF5"
    h5_path = os.path.join(root_directory, 'topo_analysis.h5')
    with PyTableUtils(h5_path, 'topo_analysis', 
                      'Analysis demonstration', title='Analysis') as pytable:

        pytable.declare_group('selector', 'The Selector object for the topo analysis demo')
        pytable.store_selector('selector', Select(collation), 'topo_analysis_selector')

        pytable.declare_group('images', 'Demonstration of how to store images')

        for (ims, mdata, imlabels) in zip(images, metadata, labels):
            for (im, info, imlabel) in zip(images, mdata, imlabels):
                pytable.store_array('images', np.array(im[0]), imlabel, info=info)


# Normally in Topographica, the prefix is set to the Documents subdirectory of home (by default)
output_directory = os.path.join(os.getcwd(), 'Demo_Output')
@launch_batch_analysis(Launcher, output_directory, review=True)
def advanced():
    cross_product_densities = (LinearSpecs("retina_density", 2,7,3)
                               * LinearSpecs("cortex_density", 1,6,3, fp_precision=2))

    run_batch_spec = Spec(times=[1,5,10], 
                          rationale='Avoiding default of 10000 iterations for testing purposes.')

    # Completed Specifier
    combined_spec = run_batch_spec * cross_product_densities    

    # Command
    run_batch_command = RunBatchCommand('../../../examples/tiny.ty', analysis='RunBatchAnalysis')
    run_batch_command.allowed_list = ['retina_density','cortex_density', 'times']

    run_batch_command.name_time_format = '%d-%m-%Y@%H%M'
    run_batch_command.param_formatter.abbreviations = {'retina_density':'rd', 'cortex_density':'cd'}

    # Launcher
    tasklauncher = Launcher(batch_name,combined_spec,run_batch_command)
    tasklauncher.print_info = 'stdout'
    # tasklauncher.timestamp_format = None

    # Analysis
    batch_analysis = RunBatchAnalysis()
    # Adding map functions
    batch_analysis.add_map_fn(OR_plotgroup, 'Recording orientation preference')
    batch_analysis.add_map_fn(activity_plotgroup, 'Recording sheet activities')
    # Adding map-reduce function
    batch_analysis.add_map_reduce_fn(V1_mean_activity, V1_reduce, 
                                     'Processing the mean V1 activity')
    batch_analysis.add_map_reduce_fn(retina_std_activity, retina_reduce, 
                                     'Computing the standard deviation of the retinal activity')
    
    batch_analysis.add_map_reduce_fn(empty_map, save_simulations, ' Saving the simulation results.')
    return (tasklauncher, batch_analysis)



