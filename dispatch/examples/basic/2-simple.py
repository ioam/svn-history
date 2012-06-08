""" 
This is a set of simple demos designed to introduce new users to the system.

Run this script as follows:  python 2-simple.py 

For a better understanding of the system, please consult the
SimplePyScriptCommand in /dispatch/external/pyscript/commands.py . It
has a very short and concise definition and should be very readable.
"""
import tempfile, os
from dispatch import Launcher, Spec, LinearSpecs, ListSpecs, review_and_launch
from dispatch.python import SimplePyScriptCommand

##############################
# Setting up the demo script #
##############################

simple_code = ['import sys',
               'arg1 = float(sys.argv[3]); arg2 = float(sys.argv[4])',
               'print "*EXECUTING*: Arg1 is %f, Arg2 is %f and their product is %f" % (arg1, arg2, arg1*arg2)']

(_,script_path) = tempfile.mkstemp()
with open(script_path,'w') as f:     f.write('\n'.join(simple_code))


# Here is an demo to show how to use the review_and_launch decorator
output_directory = os.path.join(os.getcwd(), 'Demo_Output', 'Simple_Demos')
@review_and_launch(Launcher, output_directory)
def demoI():
    task_specifier = Spec(arg1=3, arg2=5)
    task_command = SimplePyScriptCommand(script_path, argorder=['arg1','arg2'])
    return Launcher('DemoII', task_specifier, task_command)

# Nothing much has gained over running './simple.py 3 5' manually.
# Here is a demo of the Cartesian product and the documentation system.
print "\n---DemoIII---:"
@review_and_launch(Launcher, output_directory, review=True) # Set to review to False to disable review.
def demoII():
    task_specifier = LinearSpecs('arg1',1,10,steps=5) * LinearSpecs('arg2',10,20,steps=5)

    task_specifier.rationale = """Is this better than a shell script?
    Consider the cross product of 3 parameters with 20 values each,
    ie. 8000 entries. The dispatch module aims to avoid constant
    rewriting of this sort of code with features such as modularity,
    composability, extensive documentation and pre-launch review. """

    task_command = SimplePyScriptCommand(script_path, argorder=['arg1','arg2'])
    task_launcher = Launcher('DemoII', task_specifier, task_command)
    task_launcher.description='This is documentation for demoII'
    task_launcher.tag='demo2'
    return task_launcher

message = """Hopefully, this has conveyed the basic structure of the
system.  Check the 'stream's subdirectory of the root directory
(printed above in the review) in './Demo_Output/Simple_Demos' for the
generated output."""

print "\n" + message
