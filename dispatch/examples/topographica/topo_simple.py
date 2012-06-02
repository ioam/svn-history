import sys, os, param
from dispatch import QLauncher, TaskLauncher, Spec, LinearSpecs, review_and_launch

import logging
logging.basicConfig(level=logging.DEBUG)


CLUSTER = False
Launcher = QLauncher if CLUSTER else TaskLauncher
batch_name = 'topo_cluster' if CLUSTER else 'topo_local'
max_concurrency = None if CLUSTER else 2

def exit_function(launch_info, root_directory):
    print "**This is the function that is called once all the simulations are complete.**"

output_directory = os.path.join(os.getcwd(), 'Demo_Output')
@review_and_launch(Launcher, output_directory, review=True)
def topo_simple():
    from dispatch.topographica import TopoRunBatchCommand
    cross_product_densities = LinearSpecs("retina_density", 2,7,3) * LinearSpecs("cortex_density", 1,6,3)
    run_batch_spec = Spec(times=[1,5,10], rationale='Avoiding default of 10000 iterations for testing purposes.')
    combined_spec = run_batch_spec * cross_product_densities

    # This is a Topographica specific component to generate a run_batch command
    run_batch_command = TopoRunBatchCommand('../../../examples/tiny.ty')

    tasklauncher = Launcher(batch_name,combined_spec,run_batch_command)
    tasklauncher.exit_callable = exit_function

    # Launcher options
    tasklauncher.tag = 'example_tag'
    # The default for local (you can change it). Ignored for cluster.
    tasklauncher.max_concurrency = max_concurrency 
    return tasklauncher
