# Topographica Package Include List
#
# $Id$

# For using .ty file types.
import topo.base.tyimputil

### JABHACKALERT!
### 
### Surely not all of these packages need to be imported by default.
### E.g., why on earth would cfsom need to be imported by everyone?
### Surely that is useful only to people actually using a CFSOM.
### 
### Most of the other packages below seem optional, and it does not
### seem like a good idea to have them all loaded by default.  At
### best, this surely makes the program start up slower.  At worst,
### people will end up having to get every single subpackage working
### on their platform just to get a Topographica prompt, which seems
### wholly unnecessary.
### 
### This file should be pared down to the few packages that are actually
### required by any reasonable user of Topographica.  The rest can be grouped
### into chunks, if desired, so that a user could import all the plotting code
### if they want (and not otherwise). 

# core
import topo.base.registry
import topo.base.simulator
import topo.base.parameter
import topo.base.utils
import topo.base.commandline

# sheets and sheet geometry
import topo.base.sheet
import topo.base.boundingregion

# patterns
import topo.base.patterngenerator

# sheet types
import topo.sheets.generatorsheet

# plotting
import topo.plotting.bitmap
import topo.base.sheetview
import topo.plotting.plot
import topo.plotting.plotengine
import topo.plotting.histogram
import topo.plotting.palette
import topo.plotting.plotgroup
import topo.plotting.plotfilesaver

# Documentation
import topo.base.gendocs

# import all the important stuff directly into the package
# namespace.
from topo.base.simulator import *
from topo.base.sheet import *


