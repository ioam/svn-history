""" 
This is a set of simple demos designed to introduce new users to the system.

Run this script as follows:  python simple_demo.py 

For a better understanding of the system, please consult the
SimplePyScriptCommand in /dispatch/external/pyscript/commands.py . It
has a very short and concise definition and should be very readable.
"""
import tempfile, param, os

from dispatch import TaskLauncher, Spec, LinearSpecs, ListSpecs, review_and_launch
from dispatch.python import SimplePyScriptCommand

##############################
# Setting up the demo script #
##############################

simple_code = ['import sys',
               'arg1 = float(sys.argv[3]); arg2 = float(sys.argv[4])',
               'print "*EXECUTING*: Arg1 is %f, Arg2 is %f and their product is %f" % (arg1, arg2, arg1*arg2)']

(_,script_path) = tempfile.mkstemp()
with open(script_path,'w') as f:     f.write('\n'.join(simple_code))


# This is the proper way to specify where all your files will be generated
output_directory = os.path.join(os.getcwd(), 'Demo_Output', 'Simple_Demos')

# Demo I
# This is the simplest possible example of how dispatch is used
print "---DemoI---:"
if __name__ == '__main__':
    param.normalize_path.prefix = os.path.join(os.getcwd(), 'Demo_Output', 'Simple_Demos')
    task_specifier = Spec(arg1 = 3, arg2 = 5)
    task_command = SimplePyScriptCommand(script_path, argorder=['arg1','arg2'])
    task_launcher = TaskLauncher('DemoI', task_specifier, task_command)
    task_launcher.dispatch()

# Demo II
# Here is an demo to show how using the review_and_launch decorator (recommended) is useful.
print "---DemoII---:"
@review_and_launch(TaskLauncher, output_directory)
def demoII():
    task_specifier = Spec(arg1=3, arg2=5)
    task_command = SimplePyScriptCommand(script_path, argorder=['arg1','arg2'])
    return TaskLauncher('DemoII', task_specifier, task_command)

# Demo III
# Nothing much has gained over running './simple.py 3 5' manually.
# Here is a demo of the Cartesian product and the documentation system.
print "\n---DemoIII---:"
@review_and_launch(TaskLauncher, output_directory, review=True) # Set to review to False to disable review.
def demoIII():
    task_specifier = LinearSpecs('arg1',1,10,steps=5) * LinearSpecs('arg2',10,20,steps=5)

    task_specifier.rationale = """Is this better than a shell script?
    Consider the cross product of 3 parameters with 20 values each,
    ie. 8000 entries. The dispatch module aims to avoid constant
    rewriting of this sort of code with features such as modularity,
    composability, extensive documentation and pre-launch review. """

    task_command = SimplePyScriptCommand(script_path, argorder=['arg1','arg2'])
    task_launcher = TaskLauncher('DemoIII', task_specifier, task_command)
    task_launcher.description='This is documentation for demoIII'
    task_launcher.tag='demo3'
    task_launcher.print_info='stdout'
    return task_launcher

message = """Hopefully, this has conveyed the basic structure of the
system.  - For more in-depth examples, run python demos.py.  - For
topographica examples, run topographica topoI.py
"""

print "\n" + message
