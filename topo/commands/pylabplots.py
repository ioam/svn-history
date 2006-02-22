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
### JABHACKALERT: Need to figure out how to use Agg by default, but
### override it with TkAgg, so that the documentation file for this
### file can be generated.  It's apparently not as simple as just
### doing "matplotlib.use('Agg')" here.
import pylab
import re, os

from Numeric import arange, cos, pi, array, transpose

import topo

from topo.base.arrayutils import octave_output
from topo.base.sheet import Sheet
from topo.misc.utils import frange


def vectorplot(vec):
    """
    Simple line plotting for any vector or list of numbers.

    Intended for interactive debugging or analyzing from the command
    prompt.  See MatPlotLib's pylab functions to create more elaborate
    or customized plots; this is just a simple example.
    """
    pylab.plot(vec)
    pylab.grid(True)
    pylab.show._needmain = False
    pylab.show()


def matrixplot(mat):
    """
    Simple plotting for any matrix as a bitmap with axes.

    Like MatLab's imagesc, scales the values to fit in the range 0 to 1.0.
    Intended for interactive debugging or analyzing from the command
    prompt.  See MatPlotLib's pylab functions to create more elaborate
    or customized plots; this is just a simple example.
    """
    pylab.gray()
    pylab.figure(figsize=(5,5))
    pylab.imshow(mat,interpolation='nearest')
    pylab.show._needmain = False     
    pylab.show()


def topographic_grid(xsheet_view_name='XPreference',ysheet_view_name='YPreference'):
    """
    By default, plot the XPreference and YPreference preferences for all
    Sheets for which they are defined, using MatPlotLib.

    If sheet_views other than XPreference and YPreference are desired,
    the names of these can be passed in as arguments.
    """
    sim = topo.base.simulator.get_active_sim()
    for sheet in sim.objects(Sheet).values():
        if ((xsheet_view_name in sheet.sheet_view_dict) and
            (ysheet_view_name in sheet.sheet_view_dict)):

            x = sheet.sheet_view_dict[xsheet_view_name].view()[0]
            y = sheet.sheet_view_dict[ysheet_view_name].view()[0]

            pylab.figure(figsize=(5,5))

            # This one-liner works in Octave, but in matplotlib it
            # results in lines that are all connected across rows and columns,
            # so here we plot each line separately:
            #   pylab.plot(x,y,"k-",transpose(x),transpose(y),"k-")
            # Here, the "k-" means plot in black using solid lines;
            # see matplotlib for more info.
            isint=pylab.isinteractive() # Temporarily make non-interactive for plotting
            pylab.ioff()
            for r,c in zip(y,x):
                pylab.plot(c,r,"k-")
            for r,c in zip(transpose(y),transpose(x)):
                pylab.plot(c,r,"k-")
            
            pylab.xlabel('x')
            pylab.ylabel('y')
            # Currently sets the input range arbitrarily; should presumably figure out
            # what the actual possible range is for this simulation (which would presumably
            # be the maximum size of any GeneratorSheet?).
            pylab.axis([-0.5,0.5,-0.5,0.5])
            pylab.title('Topographic mapping to '+sheet.name+' at time '+str(sim.time()))

            # Will need to provide a way to save this output
            # when there is no GUI
            #pylab.savefig('simple_plot')

            if isint: pylab.ion()
            
            # Allow multiple concurrent plots; there may be a
            # cleaner way to do this...
            pylab.show._needmain = False 
            pylab.show()



