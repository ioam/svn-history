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
import copy

from numpy.oldnumeric import arange, cos, pi, array, transpose, argmax, argmin

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


def vectorplot(vec,title=None, label=None):
    """
    Simple line plotting for any vector or list of numbers.

    Intended for interactive debugging or analyzing from the command
    prompt.  See MatPlotLib's pylab functions to create more elaborate
    or customized plots; this is just a simple example.

    An optional string can be supplied as a title for the figure, if
    desired.  At present, this is only used for the body of the figure,
    not the 
    """
    pylab.plot(vec, label=label)
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


def activityplot(sheet,activity=None,title=None,cmap=pylab.cm.Greys):    
    """
    Plots the activity in a sheetx.

    Gets plot's extent from sheet.bounds.aarect(). Adds a title and
    allows the selection of a colormap.  If activity is not given,
    the sheet's current activity is used.
    """
    l,b,r,t = sheet.bounds.aarect().lbrt()
    if activity is None:
        activity = sheet.activity
    pylab.imshow(activity, extent=(l,r,b,t),cmap=cmap)


def topographic_grid(xsheet_view_name='XPreference',ysheet_view_name='YPreference',axis=[-0.5,0.5,-0.5,0.5]):
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
            pylab.axis(axis)
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
    y_values=[sheet.curve_dict[x_axis][curve_label][key].view()[0][i_value,j_value] for key in x_values]
    return x_values, y_values

def or_tuning_curve(x_axis,plot_type,unit):
    """
    Plots a tuning curve for orientation which rotates the curve 
    values so that minimum y values are at the minimum x value.
    The y_values and labels are rotated by an amount determined by the minmum 
    y_value for the first curve plotted (usually the lowest contrast curve). 

    The curve datapoints are collected from the curve_dict for each
    sheet, depending on the value of topo.commands.analysis.sheet_name
    and topo.commands.analysis.coordinate (which may be set by the GUI or
    by hand).
    """
    # There may be cases (ie when the lowest contrast curve gives a lot of zero y_values)
    # in which the maximum is not in the centre.
    # Ideally this should be changed so that the preferred orientation is in the centre.
    # This may also be useful for other tuning curve types, not just orientation ie. direction.
    
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
    manager.window.title(topo.sim.name+': '+x_axis.capitalize()+' Tuning Curve')

    def rotate(seq, n=1):
        n = n % len(seq) # n=hop interval
        return seq[n:] + seq[:n]

    first_curve=True
    for curve_label in sorted(sheet.curve_dict[x_axis].keys()):
	if first_curve==True:
	    x_values, y_values = tuning_curve_data(sheet,x_axis, curve_label, i_value, j_value)
	    min_arg=argmin(y_values)
	    x_min=x_values[min_arg] 
	    y_min=y_values[min_arg]
	    y_values=rotate(y_values, n=min_arg)
	    ticks=rotate(x_values, n=min_arg)
	    label_min=ticks[0]
	    x_max=min(x_values)+pi
	    x_values.append(x_max)
	    y_values.append(y_min)
	    first_curve=False
	else:
	    y_values=[sheet.curve_dict[x_axis][curve_label][key].view()[0][i_value,j_value] for key in ticks]
	    y_min=sheet.curve_dict[x_axis][curve_label][x_min].view()[0][i_value,j_value] 
	    y_values.append(y_min)
	labels = copy.copy(ticks)
	labels.append(label_min)
	labels= [x*180/pi for x in labels]
	labels_new = [str(int(x)) for x in labels]
	pylab.xticks(x_values, labels_new)
	plot_type(x_values, y_values, label=curve_label)
         
    if isint: pylab.ion()
    pylab.legend(loc=4)
    pylab.show._needmain = False 
    pylab.show()

def tuning_curve(x_axis,plot_type,unit):
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
    manager.window.title(topo.sim.name+': '+x_axis.capitalize()+' Tuning Curve')


    for curve_label in sorted(sheet.curve_dict[x_axis].keys()):
        x_values, y_values = tuning_curve_data(sheet,x_axis, curve_label, i_value, j_value)
        plot_type(x_values, y_values, label=curve_label)
         
    if isint: pylab.ion()
    pylab.legend(loc=4)
    pylab.show._needmain = False 
    pylab.show()
      	   

def plot_cfproj_mapping(dest,proj='Afferent',style='b-'):
    """
    Given a CF sheet receiving a CFProjection, plot
    the mapping of the dests CF centers on the src sheet.
    """
    if isinstance(dest,str):
        from topo import sim
        dest = sim[dest]
    plot_coord_mapping(dest.projections()[proj].coord_mapper,
                       dest,style=style)

def plot_coord_mapping(mapper,sheet,style='b-'):
    """
    Plot a coordinate mapping for a sheet.
    
    Given a CoordinateMapperFn (as for a CFProjection) and a sheet
    of the projection, plot a grid showing where the sheet's units
    are mapped.
    """

    from pylab import plot,hold,ishold
    
    xs = sheet.sheet_rows()
    ys = sheet.sheet_cols()

    hold_on = ishold()
    if not hold_on:
        plot()
    hold(True)

    for y in ys:
        pts = [mapper(x,y) for x in xs]
        plot([u for u,v in pts],
             [v for u,v in pts],
             style)

    for x in xs:
        pts = [mapper(x,y) for y in ys]
        plot([u for u,v in pts],
             [v for u,v in pts],
             style)

    hold(hold_on)
    
