"""
Output functions (see basic.py) that apply to a whole Projection. For example, for a CFProjection this involves iterating through all the CFs and applying an output function to each.

$Id$
"""
__version__='$Revision$'

from topo.base.cf import CFPOutputFn

# imported here so that all projection-level output functions are in the
# same package
from topo.base.cf import CFPOF_Plugin
