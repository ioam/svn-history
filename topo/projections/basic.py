"""
This simple file brings CFProjection into topo.projections so that users can
select CFProjection under this name space which contains all useful 
implementations of projections.

Also, quoted from Jim:
"Eventually, we will have a menu of things that are valid Projections, and it 
will include only the things in topo.projections."

$Id$
"""

__version__ = "$Revision$"

from topo.base.connectionfield import CFProjection

# JABALERT: Uncomment this when SharedWeightProjection is ready for prime time
#from topo.base.connectionfield import SharedWeightProjection
