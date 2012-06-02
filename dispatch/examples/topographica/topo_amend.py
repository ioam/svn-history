import os
import topo

from dispatch import StaticSpecs
from dispatch.topographica import TopoRunBatchAnalysis

def V1_mean_activity():  return numpy.mean(topo.sim['V1'].activity)

def V1_reduce(map_data, root_directory):      
    import pylab
    time1_rd2 = [(float(spec['cortex_density']), v) for  (v, t, spec) in map_data 
                 if ((t==1) and (spec['retina_density'] == '2.0000'))]

    cortex_density, activities = zip(*sorted(time1_rd2))
    pylab.plot(cortex_density, activities)
    pylab.title('Amended plot.')
    figure_path = os.path.join(root_directory, 'cluster_figures')
    try: os.mkdir(figure_path)
    except :pass
    pylab.savefig(os.path.join(figure_path, 'rd2_mean_activity_amend.png'))
    print "Saved figure rd2_mean_activity_amend.png in folder cluster_figures"


root_directory = os.path.abspath('./Demo_Output/2012-05-15_1110-topo_analysis_cluster')
log_path = os.path.join(root_directory, 'topo_analysis_cluster.log')

analysisfn = TopoRunBatchAnalysis.load(root_directory)
analysisfn.source_path = os.path.abspath('./topo_amend.py')
analysisfn.set_map_reduce_fns([V1_mean_activity],[V1_reduce],['Amending the plot'])
specs = StaticSpecs.extract_log_specification(log_path)
spec_log = zip(specs[0],specs[1])

if __name__ == '__main__':
    analysisfn.reduce(spec_log, root_directory)
