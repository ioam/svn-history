"""
A family of high-level user commands acting on the entire simulator.

Any new commands added to this directory will automatically become
available for any program.

Commands here should be 'bullet-proof' and work 'from scratch'.
That is, they should print warnings if required but should not raise
errors that would interrupt e.g. a long batch run of simulation work.

$Id$
"""
__version__='$Revision$'

# Automatically discover all .py files in this directory. 
import re,os
__all__ = [re.sub('\.py$','',f) for f in os.listdir(__path__[0])
           if re.match('^[^_].*\.py$',f)]
