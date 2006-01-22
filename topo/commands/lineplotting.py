"""
Line-based plotting commands using MatPlotLib.

Before importing this file, you will probably want to do something
like:

  import matplotlib
  matplotlib.use('TkAgg')

to select a backend, or else select an appropriate one in your
matplotlib.rc file (if any).  There are many backends available for
different GUI or non-GUI uses.

$Id$
"""
__version__='$Revision$'

import matplotlib
import pylab
import re, os

from Numeric import arange, cos, pi, array, transpose

import topo

from topo.base.arrayutils import octave_output
from topo.base.sheet import Sheet
from topo.base.utils import frange


def topographic_grid():
    """
    Plot the CoG for all Sheets for which measure_cog returned results,
    using MatPlotLib.
    """
    sim = topo.base.simulator.get_active_sim()
    for sheet in sim.objects(Sheet).values():
        if (('XPreference' in sheet.sheet_view_dict) and
            ('YPreference' in sheet.sheet_view_dict)):

            x = sheet.sheet_view_dict['XPreference'].view()[0]
            y = sheet.sheet_view_dict['YPreference'].view()[0]

            pylab.figure(figsize=(6,6))

            # This one-liner works in Octave, but in matplotlib it
            # results in lines that are all connected across rows and columns,
            # so here we plot each line separately.
            # The "k-" means plot in black using solid lines; see matplotlib for
            # more info.
            #pylab.plot(x,y,"k-",transpose(x),transpose(y),"k-")
            for r,c in zip(y,x):
                pylab.plot(c,r,"k-")
            for r,c in zip(transpose(y),transpose(x)):
                pylab.plot(c,r,"k-")
            
            pylab.xlabel('x')
            pylab.ylabel('y')
            
            pylab.title('Topographic mapping to '+sheet.name)

            # Will need to provide a way to save this output
            # when there is no GUI
            #pylab.savefig('simple_plot')

            # Allow multiple concurrent plots; there may be a
            # cleaner way to do this...
            pylab.show._needmain = False 
            pylab.show()



