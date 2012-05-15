""" 
For a better understanding of the system, please consult the
BasicPyScriptCommand in /dispatch/external/pyscript/commands.py . It
has a very short and concise definition and should be very readable.
"""
import os, tempfile, time
import numpy
from numpy.random import randint, permutation

from dispatch import Spec, QLauncher, TaskLauncher, TaskSpecifier, LinearSpecs, ListSpecs, review_and_launch
from dispatch.python import SimplePyScriptCommand


CLUSTER = True
if CLUSTER:  Launcher = QLauncher; batch_name = 'Haystack_demo_cluster'
else:        Launcher = TaskLauncher; batch_name = 'Haystack_demo_local'


##############################
# Setting up the demo script #
##############################

def make_script(output_directory):
    num_optima = 3; size = 3
    optima = [ (randint(0,size), randint(0,size)) for i in range(num_optima)]
    random_optima = ["import sys, os, pickle, json",
                     "tid = int(sys.argv[1])",
                     "root_directory = sys.argv[2]",
                     "x=int(sys.argv[3]); y= int(sys.argv[4])",
                     "metric_directory=os.path.join(root_directory, 'metrics')",
                     "optima = %s" % str(optima),
                     "found_optimum = ((x,y) in optima)",
                     "if found_optimum: print '*HIT* at %s!' % str((x,y))",
                     "else:             print 'MISS at %s.' %  str((x,y))",
                     "pickle_path = os.path.join(metric_directory, 'metric-'+str(tid)+'-')",
                     "with open(pickle_path,'w') as p:", 
                     "\tpickle.dump(((x,y), found_optimum), p)"]

    if not os.path.isdir(output_directory): os.makedirs(output_directory)
    script_path = os.path.join(output_directory, 'haystack.py')
    with open(script_path,'w') as f:     f.write('\n'.join(random_optima))
    return script_path


class RandomSample2D(TaskSpecifier):    
    """ N random seeds which randomly choose new position """
    def __init__(self, grid_size, sample_count, hits_needed, 
                 max_iterations=None, rationale=''):

        self.grid_size = grid_size; self.sample_count = sample_count
        self.hits_needed = hits_needed; self.max_iterations = max_iterations
        super(RandomSample2D, self).__init__(dynamic=True, rationale=rationale)

        # Minimum number of iterations for all points to have been sampled.
        max_iterations_needed = numpy.ceil((grid_size**2) / float(sample_count))
        if (max_iterations is None) or (max_iterations > max_iterations_needed):
            self.max_iterations = max_iterations_needed
        
        # A list of the possible (remaining) grid positions
        self._possible_positions = [(x,y) for x in range(grid_size) for y in range(grid_size)]
        self.hits = [] # The positions of the hits found.
        self._iteration_counter = 0; self.updated = True

    def constant_keys(self): return []
    def varying_keys(self):  return ['x','y']
    def schedule(self):       return [self.sample_count] * self.max_iterations
    def update(self, data):
        if data is None: data = []
        self.updated=True
        self.hits += [position for (position,hit) in data if hit]

    def next(self):
        if not self.updated: raise StopIteration
        if self._iteration_counter == self.max_iterations+1: 
            self.message("**Maximum number of iterations reached! Stopping.**")
            self.message("Hits found: %s" % str(self.hits))
            raise StopIteration
        if len(self.hits) == self.hits_needed:
            self.message("**Required number of hits reached! Stopping.**")
            self.message("Hits found: %s" % str(self.hits))
            raise StopIteration

        rand_selection = permutation(len(self._possible_positions))[:self.sample_count]

        selected_positions = [self._possible_positions[ind] for ind in rand_selection]
        [self._possible_positions.remove(pos) for pos in selected_positions]

        self._iteration_counter += 1; self.updated = False
        return [{'x':str(x), 'y':str(y)} for (x,y) in selected_positions]

    def __str__(self):
        args = [self.grid_size, self.sample_count,  self.hits_needed]
        return "RandomSample2D(%s)" % ','.join([str(arg) for arg in args])

output_directory = os.path.join(os.getcwd(), 'Demo_Output')
@review_and_launch(Launcher, output_directory, review=True)
def demoIII():
    time.localtime()
    script_path = make_script(output_directory)
    task_specifier = RandomSample2D(3,3,3)
    task_command = SimplePyScriptCommand(script_path, argorder=['x','y'])
    task_launcher = Launcher(batch_name, task_specifier, task_command)
    task_launcher.print_info = 'stdout'
    return task_launcher


# NOTES:
# max_iterations should be a parameter for all dynamic specifiers.
# task_specifier = Spec(x=3, y=5) # SHOULD BE SORTED ALPHABETICALLY! FIX ME!
