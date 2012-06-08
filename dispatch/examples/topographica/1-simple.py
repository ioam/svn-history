import sys, os
from dispatch import QLauncher, Launcher, Spec, LinearSpecs, review_and_launch
from dispatch.topographica import RunBatchCommand

import logging
logging.basicConfig(level=logging.DEBUG)

CLUSTER = True
if CLUSTER: Launcher = QLauncher
batch_name = 'topo_cluster' if CLUSTER else 'topo_local'
max_concurrency = None if CLUSTER else 2

output_directory = os.path.join(os.getcwd(), 'Demo_Output')
@review_and_launch(Launcher, output_directory, review=True)
def simple():
    cross_product_densities = LinearSpecs("retina_density", 2,7,steps=3) * LinearSpecs("cortex_density", 1,6,steps=3)
    run_batch_spec = Spec(times=[1,5,10], rationale='Avoiding default of 10000 iterations for testing purposes.')
    combined_spec = run_batch_spec * cross_product_densities

    # This is a Topographica specific component to generate a run_batch command
    run_batch_command = RunBatchCommand('../../../examples/tiny.ty')
    tasklauncher = Launcher(batch_name,combined_spec,run_batch_command)
    tasklauncher.tag = 'example_tag'
    tasklauncher.max_concurrency = max_concurrency  # Ignored for cluster.
    return tasklauncher
