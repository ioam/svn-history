# Topographica Package Include List
#
# $Id$

# For using .ty file types.
import tyimputil

### JABHACKALERT!
### 
### Surely not all of these packages need to be imported by default.
### E.g. everything still seems to work if I skip "import gui" and
### run the simulator without a GUI, so presumably "import gui" 
### should be omitted unless a GUI is actually requested.
### 
### Similarly, why on earth would cfsom need to be imported by everyone?
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
import simulator
import parameter
import utils
import commandline
import registry

# sheets and sheet geometry
import sheet
import boundingregion

# kernels
import kernelfactory

# sheet types
import inputsheet

# plotting
import bitmap
import sheetview
import plot
import plotengine
import histogram
import palette
import plotgroup
import plotfilesaver

# Documentation
import gendocs

# import all the important stuff directly into the package
# namespace.
from simulator import *
from sheet import *


