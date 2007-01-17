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




def windowtitle(title):
    """
    Helper function to set the title of this PyLab plot window to a string.

    At the moment, PyLab does not offer a window-manager-independent
    means for controlling the window title, so what we do is to try
    what should work with Tkinter, and then suppress all errors.  That
    way we should be ok when rendering to a file-based backend, but
    will get nice titles in Tk windows.  If other toolkits are in use,
    the title can be set here using a similar try/except mechanism, or
    else there can be a switch based on the backend type.
    """
    try: 
        manager = pylab.get_current_fig_manager()
        manager.window.title(title)
    except:
        pass


def vectorplot(vec,title=None):
    """
    Simple line plotting for any vector or list of numbers.

    Intended for interactive debugging or analyzing from the command
    prompt.  See MatPlotLib's pylab functions to create more elaborate
    or customized plots; this is just a simple example.

    An optional string can be supplied as a title for the figure, if
    desired.  At present, this is only used for the body of the figure,
    not the 
    """
    pylab.plot(vec)
    pylab.grid(True)
    if (title): windowtitle(title)
    pylab.show._needmain = False
    pylab.show()


def matrixplot(mat,title=None):
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
    if (title): windowtitle(title)
    pylab.show._needmain = False     
    pylab.show()


def topographic_grid(xsheet_view_name='XPreference',ysheet_view_name='YPreference'):
    """
    By default, plot the XPreference and YPreference preferences for all
    Sheets for which they are defined, using MatPlotLib.

    If sheet_views other than XPreference and YPreference are desired,
    the names of these can be passed in as arguments.
    """
    for sheet in topo.sim.objects(Sheet).values():
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
            windowtitle('Topographic mapping to '+sheet.name+' at time '+str(topo.sim.time()))

            # Will need to provide a way to save this output
            # when there is no GUI
            #pylab.savefig('simple_plot')

            if isint: pylab.ion()
            
            # Allow multiple concurrent plots; there may be a
            # cleaner way to do this...
            pylab.show._needmain = False 
            pylab.show()


def tuning_curve_data(sheet, x_axis, curve_label, i_value, j_value):
    """
    Collect data for one tuning curve from the curve_dict of each sheet.

    The unit to plot is specified as a matrix index (i_value,j_value).
    There may be many possible curves in the curve_dict; the specific
    one is determined by the x_axis (i.e., what feature to plot), and
    the curve_label (which determines other parameters that specify a
    particular plot).  Returns the feature values (the x_values,
    i.e. locations along the x axis), x_values) and the corresponding
    responses (the y_values).
    """
    x_values= sorted(sheet.curve_dict[x_axis][curve_label].keys())
    y_values=[sheet.curve_dict[x_axis][curve_label][key][i_value,j_value] for key in x_values]
    return x_values, y_values

	   
def tuning_curve(x_axis,plot_type,x_ticks,x_labels,x_lim,unit):
    """
    Plots a tuning curve for the appropriate feature type, such as orientation, contrast or size.

    The curve datapoints are collected from the curve_dict for each
    sheet, depending on the value of topo.commands.analysis.sheet_name
    and topo.commands.analysis.coordinate (which may be set by the GUI or
    by hand).
    """

    sheet=topo.sim[topo.commands.analysis.sheet_name]
    coordinate=topo.commands.analysis.coordinate
    i_value,j_value=sheet.sheet2matrixidx(coordinate[0],coordinate[1])
    

    pylab.figure(figsize=(7,7))
    isint=pylab.isinteractive()
    pylab.ioff()
    manager = pylab.get_current_fig_manager()
    
    pylab.ylabel('Response')
    pylab.xlabel(x_axis.capitalize()+' ('+unit+')')
    pylab.title('Sheet '+topo.commands.analysis.sheet_name+', coordinate(x,y)='+'('+
	 	str(coordinate[0])+','+str(coordinate[1])+')'+' at time '+str(topo.sim.time()))
    manager.window.title(x_axis.capitalize()+' Tuning Curve')


    for curve_label in sorted(sheet.curve_dict[x_axis].keys()):
        x_values, y_values = tuning_curve_data(sheet,x_axis, curve_label, i_value, j_value)
        plot_type(x_values, y_values, label=curve_label)
	if (x_ticks): pylab.xticks(x_ticks,x_labels)
        if (x_lim): pylab.xlim(x_lim)

	   
    if isint: pylab.ion()
    
    pylab.legend()
    pylab.show._needmain = False 
    pylab.show()
