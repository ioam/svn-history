import os, shutil, tempfile, time

import param
from dispatch import TaskLauncher, TaskSpecifier, Spec, LinearSpecs, ListSpecs, review_and_launch
from dispatch.python import SimplePyScriptCommand


explanation = """
This demo illustrates the operation of dynamic TaskSpecifiers. It is a
self-contained (toy!) example based on the Collatz conjecture:

For all natural numbers, if you repeatedly:

- Divide by two when even.
- Multiply by 3 and add one when odd

You will always end up at 1.

To show how TaskSpecifiers can dynamically evaluate parameters, we split
these two steps into two pieces - one for our TaskSpecifier and one for our
process. In reality this could be hillclimbing orientation map quality in
Topographica (for example) and you should think in these terms.

The script that is invoked handles the even case. Here it is: 

%s


The important point is that the metric (ie. the value) is pickled to a
known folder according to the scheme metric-<tid>.

The custom CollatzDemo TaskSpecifier is very simple and illustrates the
essense of a dynamic TaskSpecifier. In this example, it handles the Collatz
conjecture step for the odd case.

Now if you use this TaskSpecifier and point the TaskLauncher to the
appropriate metrics folder, we see how the CollatzDemo class computes new
values to pass to the script conditioned on previous results. This is the
basic pattern needed to implement usedul parameter search algorithms.

"""

collatz_code = ['import os, sys, pickle',
                'tid = int(sys.argv[1])',
                "metric_path = os.path.join(sys.argv[2], 'metrics')",
                'N = int(sys.argv[3])',
                'if (N % 2) == 0:',
                '   print ',
                '   print "Process: N is even. N :=  N/2"',
                '   N /= 2',
                'print "Process: N is now %d" % N',
                'pickle_path = os.path.join(metric_path, "metric-"+str(tid)+"-")',
                'with open(pickle_path,"w") as p: pickle.dump(N,p)']

print explanation % collatz_code

(_,script_path) = tempfile.mkstemp() # FIXME MAKE FIXED FILE AND DEMO QLAUNCHER
with open(script_path,'w') as f:     f.write("\n".join(collatz_code))



response = raw_input('Review? [y,n]: ')
if response == 'y': review_and_launch.review =  True

response = raw_input('Press any key to run demo. ')

class CollatzDemo(TaskSpecifier):
    ' An illustration of how dynamic TaskSpecifiers work'

    def __init__(self, starting_value, rationale=''):
        self.value = starting_value
        self.stop = False
        super(CollatzDemo, self).__init__(dynamic=True, rationale=rationale)

    def constant_keys(self): return []
    def varying_keys(self):  return ['n']

    def update(self, metrics):
        n = metrics[0]
        self.stop = False
        if (n == 1): 
            self.stop = True
            print "BASE CASE REACHED (1). Stopping."; return
        if (n % 2) == 1: 
            self.value = 3*n + 1
            print "Specifier: N is odd. N := 3N+1 (%d)" % self.value
        else: 
            self.value = n

    def next(self):
        if  self.stop: raise StopIteration
        self.stop = True
        return [{'n':str(self.value)}]

    def __repr__(self):
        return "CollatzDemo(%d)" % self.value


output_directory = os.path.join(os.getcwd(), 'Demo_Output')
@review_and_launch(TaskLauncher, output_directory, review=True)
def collatz():
    collatz_specifier = CollatzDemo(43, rationale='Illustrating dynamic specifiers')
    task_command = SimplePyScriptCommand(script_path)

    task_launcher = TaskLauncher('Collatz_demo', collatz_specifier, task_command)
    task_launcher.description='This is a dynamic example'
    task_launcher.tag='collatz'
    return task_launcher

