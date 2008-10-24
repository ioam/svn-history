"""
Line-based and matrix-based plotting commands using MatPlotLib.

Before importing this file, you will probably want to do something
like:

  from matplotlib import rcParams
  rcParams['backend']='TkAgg'

to select a backend, or else select an appropriate one in your
matplotlib.rc file (if any).  There are many backends available for
different GUI or non-GUI uses.

$Id$
"""
__version__='$Revision$'

import re
import os
import copy
import errno

try:
    import matplotlib
    import pylab
except ImportError:
    print "Warning: Could not import matplotlib; pylab plots will not work."

import numpy
from numpy.oldnumeric import arange, sqrt, pi, array, floor, transpose, argmax, argmin, cos, sin, log10

import topo
from topo.base.arrayutil import octave_output
from topo.base.sheet import Sheet
from topo.base.arrayutil import wrap
from topo.misc.filepath import normalize_path
from topo.analysis.vision import complexity
import topo.analysis.vision
from topo.plotting.plot import make_template_plot, Plot

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

    Nothing is done if the title is None.
    """
    if title is not None:
        try: 
            manager = pylab.get_current_fig_manager()
            manager.window.title(title)
        except:
            pass


# Default DPI when rendering to a bitmap.  The nominal size * the dpi
# gives the final image size in pixels.  
# E.g.: 4"x4" image * 80 dpi ==> 320x320 pixel image
# The output can be .png, .ps, .pdf, .svg, etc, as supported by MatPlotLib
default_output_dpi=100
default_output_format=".png"

def generate_figure(title=None,filename=None,suffix="",format=None):
    """
    Helper function to display a figure on screen or save to a file.
    
    The title is used for the window when displaying onscreen. 

    The name of the file is constructed from the provided filename
    plus the provided suffix plus the current simulator time plus
    the specified format (defaulting to default_output_format). 

    For bitmap formats, the DPI is determined by default_output_dpi.
    """
    if (format==None):
        format=default_output_format

    pylab.show._needmain=False
    if filename is not None:
        fullname=filename+suffix+str(topo.sim.time())+suffix+format
        pylab.savefig(normalize_path(fullname), dpi=default_output_dpi)
    else:
        windowtitle(title)
        pylab.show()



def vectorplot(vec,xvalues=None,title=None,style='-',label=None,filename=None):
    """
    Simple line plotting for any vector or list of numbers.

    Intended for interactive debugging or analyzing from the command
    prompt.  See MatPlotLib's pylab functions to create more elaborate
    or customized plots; this is just a simple example.

    An optional string can be supplied as a title for the figure, if
    desired.  At present, this is only used for the window, not the
    actual body of the figure (and will thus not appear when the
    figure is saved).

    The style argument allows different line/linespoints style for
    the plot: 'r-' for red solid line, 'bx' for blue x-marks, etc.
    See http://matplotlib.sourceforge.net/matplotlib.pylab.html#-plot
    for more possibilities.

    The label argument can be used to identify the line in a figure legend.

    Ordinarily, the x value for each point on the line is the index of
    that point in the vec array, but a explicit list of xvalues can be
    supplied; it should be the same length as vec.

    Execution of multiple vectorplot() commands with different styles
    will result in all those styles overlaid on a single plot window.
    """
    if xvalues is not None:
        pylab.plot(xvalues, vec, style, label=label)
    else:
        pylab.plot(vec, style, label=label)
    pylab.grid(True)
    generate_figure(title=title,filename=filename)


def matrixplot(mat,title=None,aspect=None,colorbar=True,filename=None):
    """
    Simple plotting for any matrix as a bitmap with axes.

    Like MatLab's imagesc, scales the values to fit in the range 0 to 1.0.
    Intended for interactive debugging or analyzing from the command
    prompt.  See MatPlotLib's pylab functions to create more elaborate
    or customized plots; this is just a simple example.
    """
    pylab.gray()
    pylab.figure(figsize=(5,5))
    pylab.imshow(mat,interpolation='nearest',aspect=aspect)
    if title: windowtitle(title)
    if colorbar and (mat.min()!= mat.max()): pylab.colorbar()
    generate_figure(title=title,filename=filename)


def matrixplot3d(mat,title=None,type="wireframe",filename=None):
    """
    Simple plotting for any matrix as a 3D wireframe with axes.

    Uses Matplotlib's beta-quality features for 3D plotting.  These
    usually work fine for wireframe plots, although they don't always
    format the axis labels properly, and do not support removal of
    hidden lines.  Note that often the plot can be rotated within the
    window to make such problems go away, and then the best result can
    be saved if needed.

    Other than the default "wireframe", the type can be "contour" to
    get a contour plot, or "surface" to get a solid surface plot, but
    surface plots currently fail in many cases, e.g. for small
    matrices.

    If you have trouble, you can try matrixplot3d_gnuplot instead.
    """
    from numpy import outer,arange,ones
    from matplotlib import axes3d
    
    fig = pylab.figure()
    ax = axes3d.Axes3D(fig)

    # Construct matrices for r and c values
    rn,cn = mat.shape
    c = outer(ones(rn),arange(cn*1.0))
    r = outer(arange(rn*1.0),ones(cn))

    if type=="wireframe":
        ax.plot_wireframe(r,c,mat)
    elif type=="surface":
        # Sometimes fails for no obvious reason
        ax.plot_surface(r,c,mat)
    elif type=="contour":
        # Works but not usually very useful
        ax.contour3D(r,c,mat)
    else:
        raise ValueError("Unknown plot type "+str(type))
        
    ax.set_xlabel('R')
    ax.set_ylabel('C')
    ax.set_zlabel('Value')

    generate_figure(title=title,filename=filename)


def matrixplot3d_gnuplot(mat,title=None,outputfilename="tmp.ps"):
    """
    Simple plotting for any matrix as a 3D surface with axes.

    Currently requires the gnuplot-py package to be installed, plus
    the external gnuplot program; likely to be removed once Matplotlib
    supports 3D plots better.

    Unlikely to work on non-UNIX systems.

    Should return when it completes, but for some reason the Topographica
    prompt is not available until this command finishes.
    """
    import Gnuplot
    import Numeric # ERRORALERT
    from os import system
    
    psviewer="gv" # Should be a parameter, or handled better somehow
    g = Gnuplot.Gnuplot(debug=0) #debug=1: output commands to stderr
    r,c = mat.shape
    x = arange(r*1.0)
    y = arange(c*1.0)
    # The .tolist() command is necessary to avoid bug in gnuplot-py,
    # which will otherwise convert a 2D float array into integers (!)
    m = numpy.asarray(mat,dtype="float32").tolist()
    #g("set parametric")
    g("set data style lines")
    g("set hidden3d")
    g("set xlabel 'R'")
    g("set ylabel 'C'")
    g("set zlabel 'Value'")
    if title: g.title(title)
    
    if outputfilename:
        g("set terminal postscript eps color solid 'Times-Roman' 14")
        g("set output '"+outputfilename+"'")
        g.splot(Gnuplot.GridData(m,x,y, binary=1))
        #g.hardcopy(outputfilename, enhanced=1, color=1)
        system(psviewer+" "+outputfilename+" &")

    else:
        g.splot(Gnuplot.GridData(m,x,y, binary=1))
        raw_input('Please press return to continue...\n')


def histogramplot(data,title=None,colors=None,*args,**kw):
    """
    Compute and plot the histogram of the supplied data.
    
    See help(pylab.hist) for help on the histogram function itself.

    If given, colors is an iterable collection of matplotlib.colors
    (see help (matplotlib.colors) ) specifying the bar colors.


    Example use:
     histplot([1,1,1,2,2,3,4,5],title='hist',colors='rgb',bins=3,normed=1)
    """
    pylab.figure(figsize=(4,2))
    pylab.show._needmain=False
    n,bins,bars = pylab.hist(data,*args,**kw)

    # if len(bars)!=len(colors), any extra bars won't have their
    # colors changed, or any extra colors will be ignored.
    if colors: [bar.set_fc(color) for bar,color in zip(bars,colors)]
    
    if title: windowtitle(title)
    pylab.show()


def gradientplot(data,cyclic=True,cyclic_range=1.0,title=None, filename=None):
    """
    Compute and show the gradient plot of the supplied data.
    Translated from Octave code originally written by Yoonsuck Choe.

    If the data is specified to be cyclic, negative differences will
    be wrapped into the range specified (1.0 by default).
    """
    r,c = data.shape
    dx = numpy.diff(data,1,axis=1)[0:r-1,0:c-1]
    dy = numpy.diff(data,1,axis=0)[0:r-1,0:c-1]

    if cyclic: # Wrap into the specified range
        # Convert negative differences to an equivalent positive value
        dx = wrap(0,cyclic_range,dx)
        dy = wrap(0,cyclic_range,dy)
        #
        # Make it increase as gradient reaches the halfway point,
        # and decrease from there
        dx = 0.5*cyclic_range-abs(dx-0.5*cyclic_range)
        dy = 0.5*cyclic_range-abs(dy-0.5*cyclic_range)

    matrixplot(sqrt(dx*dx+dy*dy),title=title,filename=filename)
    

def activityplot(sheet,activity=None,title=None,cmap=None):
    """
    Plots the activity in a sheet.

    Gets plot's extent from sheet.bounds.aarect(). Adds a title and
    allows the selection of a colormap.  If activity is not given,
    the sheet's current activity is used.
    """
    l,b,r,t = sheet.bounds.aarect().lbrt()
    if activity is None:
        activity = sheet.activity
    if cmap is None:
        cmap=pylab.cm.Greys
    pylab.imshow(activity, extent=(l,r,b,t),cmap=cmap)


def topographic_grid(xsheet_view_name='XPreference',ysheet_view_name='YPreference',axis=[-0.5,0.5,-0.5,0.5],filename=None):
    """
    By default, plot the XPreference and YPreference preferences for all
    Sheets for which they are defined, using MatPlotLib.

    If sheet_views other than XPreference and YPreference are desired,
    the names of these can be passed in as arguments.
    """
    for sheet in topo.sim.objects(Sheet).values():
        if ((xsheet_view_name in sheet.sheet_views) and
            (ysheet_view_name in sheet.sheet_views)):

            x = sheet.sheet_views[xsheet_view_name].view()[0]
            y = sheet.sheet_views[ysheet_view_name].view()[0]

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
            title='Topographic mapping to '+sheet.name+' at time '+topo.sim.timestr()

            if isint: pylab.ion()

            generate_figure(title=title,filename=filename,suffix="_"+sheet.name)
            
#########################################################################################
def overlaid_plots(plot_template=[{'Hue':'OrientationPreference'}],overlay=[('contours','OcularPreference',0.5,'black'),('arrows','DirectionPreference','DirectionSelectivity','white')],filename=None,normalize=False):   
    """
    Use matplotlib to make a plot from a bitmap constructed using the
    specified plot_template, plus additional overlaid line contour
    plot(s) specified with ('contours',map-name,contour-value,line-color)
    quadruples and/or overlaid arrows plot(s) specified with ('arrows',map-name for arrows location,
    map-name for arrows scaling,arrow-color) quadruples.
    """
   
    for template in plot_template:
    
        for sheet in topo.sim.objects(Sheet).values():
            name=template.keys().pop(0)
            plot=make_template_plot(template,sheet.sheet_views,sheet.xdensity,sheet.bounds,normalize,name=template[name])        
            if plot:
                bitmap=plot.bitmap
            	
                pylab.figure(figsize=(5,5))
                isint=pylab.isinteractive() # Temporarily make non-interactive for plotting
                pylab.ioff()					 # Turn interactive mode off 
                                    
                pylab.imshow(bitmap.image,origin='lower',interpolation='nearest')				
                pylab.axis('off')

                for (t,pref,sel,c) in overlay:
                    p = pylab.flipud(sheet.sheet_views[pref].view()[0])
                    
                    if (t=='contours'):
                        pylab.contour(p,[sel,sel],colors=c,linewidths=2)
                        
                    if (t=='arrows'):							
                        s = pylab.flipud(sheet.sheet_views[sel].view()[0])
                        scale=int(pylab.ceil(log10(len(p))))
                        X=pylab.array([x for x in xrange(len(p)/scale)])                  
                        p_sc=pylab.zeros((len(p)/scale,len(p)/scale))
                        s_sc=pylab.zeros((len(p)/scale,len(p)/scale))
                        for i in X:
                            for j in X:
                                p_sc[i][j]=p[scale*i][scale*j]
                                s_sc[i][j]=s[scale*i][scale*j]
                        pylab.quiver(scale*X,scale*X,-cos(2*pi*p_sc)*s_sc,-sin(2*pi*p_sc)*s_sc,color=c,edgecolors=c,minshaft=3,linewidths=1) 						
							
                title='%s overlaid with %s at time %s' %(plot.name,pref,topo.sim.timestr())
                if isint: pylab.ion()
                generate_figure(title=title,filename=filename,suffix="_"+sheet.name)
                
######################################################################################

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

    The curve datapoints are collected from the curve_dict for
    the sheet specified by topo.analysis.featureresponses.UnitCurveCommand.sheet
    and the units specified by topo.analysis.featureresponses.UnitCurveCommand.coords
    (which may be set by the GUI or by hand).
    """
    # There may be cases (ie when the lowest contrast curve gives a lot of zero y_values)
    # in which the maximum is not in the centre.
    # Ideally this should be changed so that the preferred orientation is in the centre.
    # This may also be useful for other tuning curve types, not just orientation ie. direction.

    sheet=topo.analysis.featureresponses.UnitCurveCommand.sheet
    coords=topo.analysis.featureresponses.UnitCurveCommand.coords
    for coordinate in coords:
    
        i_value,j_value=sheet.sheet2matrixidx(coordinate[0],coordinate[1])
        
    
        pylab.figure(figsize=(7,7))
        isint=pylab.isinteractive()
        pylab.ioff()
        manager = pylab.get_current_fig_manager()
        
        pylab.ylabel('Response')
        pylab.xlabel(x_axis.capitalize()+' ('+unit+')')
        pylab.title('Sheet '+sheet.name+', coordinate(x,y)='+'('+
                    str(coordinate[0])+','+str(coordinate[1])+')'+' at time '+topo.sim.timestr())
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

    The curve datapoints are collected from the curve_dict for
    the sheet specified by topo.analysis.featureresponses.UnitCurveCommand.sheet
    and the units specified by topo.analysis.featureresponses.UnitCurveCommand.coords
    (which may be set by the GUI or by hand).
    """
    sheet=topo.analysis.featureresponses.UnitCurveCommand.sheet
    coords=topo.analysis.featureresponses.UnitCurveCommand.coords
    for coordinate in coords:
        i_value,j_value=sheet.sheet2matrixidx(coordinate[0],coordinate[1])
        
    
        pylab.figure(figsize=(7,7))
        isint=pylab.isinteractive()
        pylab.ioff()
        manager = pylab.get_current_fig_manager()
        
        pylab.ylabel('Response')
        pylab.xlabel(x_axis.capitalize()+' ('+unit+')')
        pylab.title('Sheet '+sheet.name+', coordinate(x,y)='+'('+
    	 	str(coordinate[0])+','+str(coordinate[1])+')'+' at time '+topo.sim.timestr())
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
    

# RFHACK
### JABHACKALERT: rename & should be called from the 'Receptive
### Fields*' pgts in topo/command/analysis.py & should share the
### implementation of topographic_grid (because that's what is
### intended to be visualized here).
### Should be using generate_figure() as in matrixplot().
def plotrctg():
    
    import matplotlib
    import pylab
    from numpy import fabs
    from topo.base.arrayutil import centroid

    # CEBALERT: make clearer (by doing in a more numpy way)
    # CEBHACKALERT: only last plot hangs around because plots are overwritten
    pylab.show._needmain = False

    # CEBHACKALERT: needs to be better linked!
    from topo.analysis.featureresponses import grid
    
    for g in grid.values():
        xx=[]
        yy=[]
        rows,cols = g.shape
        for iii in range(rows): 
            for jjj in range(cols):
                # The abs() ensures the centroid is taken over both 
                # positive and negative correlations
                xxx,yyy = centroid(fabs(g[iii,jjj]))
                xx.append(xxx)
                yy.append(yyy)

        pylab.scatter(xx,yy)
        pylab.show()


def plot_tracked_attributes(output_fn, init_time, final_time, filename=None, **params):
    """
    Plots parameter values associated with an AttributeTrackingOF.
    Example call:
    VT=AttributeTrackingOF(function=HE, debug_params=['a', 'b',], units=[(0,0),(1,1)], step=1)
    plot_tracked_attributes(VT,0,10000,debug_params=['a'],units=[(0,0)], filename='V1')
    """
    raw = params.get('raw', False)

    for p in params.get('attrib_names',output_fn.attrib_names):
        pylab.figure(figsize=(6,4))
        isint=pylab.isinteractive()
        pylab.ioff()
        pylab.grid(True)
        ylabel=params.get('ylabel', "")
        pylab.ylabel(p+" "+ylabel)
        pylab.xlabel('Iteration Number')
        
        for unit in params.get('units',output_fn.units):
            y_data=[y for (x,y) in output_fn.values[p][unit]]
            x_data=[x for (x,y) in output_fn.values[p][unit]]
            if raw==True:
                plot_data=zip(x_data,y_data)
                pylab.save(normalize_path(filename+p+'(%.2f, %.2f)' %(unit[0], unit[1])),plot_data,fmt='%.6f', delimiter=',')
            
            
            pylab.plot(x_data,y_data, label='Unit (%.2f, %.2f)' %(unit[0], unit[1]))
            (ymin,ymax)=params.get('ybounds',(None,None))
            pylab.axis(xmin=init_time,xmax=final_time, ymin=ymin, ymax=ymax) 
                
        if isint: pylab.ion()
        pylab.legend(loc=0)
        generate_figure(title=topo.sim.name+': '+p,filename=filename,suffix=p)


def matrixplot_hsv(mat,title=None,aspect=None,colorbar=True,filename=None):
    """
    Simple plotting for any matrix as a bitmap with axes.
    As for matrixplot above except values are coloured in
    hsv colorspace rather than greyscale.
    """
    pylab.hsv()
    pylab.figure(figsize=(5,5))
    pylab.imshow(mat,interpolation='nearest',aspect=aspect)
    if title: windowtitle(title)
    if colorbar and (mat.min()!= mat.max()): pylab.colorbar()
    generate_figure(title=title,filename=filename)

def plot_modulation_ratio(fullmatrix):
    """
    This function computes the modulation ratios of neurons in the V1Simple and V1Complex area and
    plots the histogram of them. See analysis.vision.complexity for more info.
    """
    # Should be using generate_figure() as in matrixplot().
    if (topo.sim.objects().has_key("V1Complex") & topo.sim.objects().has_key("V1Simple")):
        bins = [0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,1.1,1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,2.0]
        v1s = complexity(fullmatrix[topo.sim["V1Simple"]])
        v1c = complexity(fullmatrix[topo.sim["V1Complex"]])
        pylab.figure()
        pylab.subplot(311)
        pylab.hist(v1s,bins)
        pylab.axis([0,2.0,0,3500])
        pylab.subplot(312)
        pylab.hist(v1c,bins)
        pylab.axis([0,2.0,0,3500])
        pylab.subplot(313)
        #pylab.hist(numpy.concatenate(array(v1s),array(v1c)),bins)
        pylab.axis([0,2.0,0,3500])
        pylab.savefig(normalize_path(str(topo.sim.timestr()) + 'RM.png'))
        #pylab.show()


# JABALERT: Remove duplication with tuning_curve, above.  
# Should be using generate_figure() as in matrixplot().
def tuning_curve_batch(directory,filename,plot_type,unit,sheet_name,coordinate,x_axis):
    """
    Saves a plot of the tuning curve for the appropriate feature type, such as orientation, contrast or size into a file.

    The curve datapoints are collected from the curve_dict for the specified
    coordinate of the specified sheet.
    """

    sheet=topo.sim[sheet_name]
    i_value,j_value=sheet.sheet2matrixidx(coordinate[0],coordinate[1])
    
    pylab.figure(figsize=(7,7))
    isint=pylab.isinteractive()
    pylab.ioff()
    manager = pylab.get_current_fig_manager()
    
    pylab.ylabel('Response')
    pylab.xlabel(x_axis.capitalize()+' ('+unit+')')
    pylab.title('Sheet '+sheet_name+', coordinate(x,y)='+'('+
	 	str(coordinate[0])+','+str(coordinate[1])+')'+' at time '+topo.sim.timestr())
    manager.window.title(topo.sim.name+': '+x_axis.capitalize()+' Tuning Curve')


    for curve_label in sorted(sheet.curve_dict[x_axis].keys()):
        x_values, y_values = tuning_curve_data(sheet,x_axis, curve_label, i_value, j_value)
        plot_type(x_values, y_values, label=curve_label)
         
    if isint: pylab.ion()
    pylab.legend(loc=4)
    try:
        os.makedirs(directory)
    except os.error, e:
	if e.errno != errno.EEXIST:
	    raise
    pylab.savefig(os.path.join(directory,filename) + '.png')



# JABALERT: Remove duplication with or_tuning_curve, above.  
# Should be using generate_figure() as in matrixplot().
def or_tuning_curve_batch(directory,filename,plot_type,unit,sheet_name,coordinate,x_axis):
    """
    Plots a tuning curve for orientation which rotates the curve 
    values so that minimum y values are at the minimum x value.
    The y_values and labels are rotated by an amount determined by the minmum 
    y_value for the first curve plotted (usually the lowest contrast curve). 

    The curve datapoints are collected from the curve_dict for the specified
    unit of the specified sheet.
    """
    # There may be cases (ie when the lowest contrast curve gives a lot of zero y_values)
    # in which the maximum is not in the centre.
    # Ideally this should be changed so that the preferred orientation is in the centre.
    # This may also be useful for other tuning curve types, not just orientation ie. direction.
    
    sheet=topo.sim[sheet_name]
    i_value,j_value=sheet.sheet2matrixidx(coordinate[0],coordinate[1])
    

    pylab.figure(figsize=(7,7))
    isint=pylab.isinteractive()
    pylab.ioff()
    manager = pylab.get_current_fig_manager()
    
    pylab.ylabel('Response')
    pylab.xlabel(x_axis.capitalize()+' ('+unit+')')
    pylab.title('Sheet '+sheet_name+', coordinate(x,y)='+'('+
	 	str(coordinate[0])+','+str(coordinate[1])+')'+' at time '+topo.sim.timestr())
    #manager.window.title(topo.sim.name+': '+x_axis.capitalize()+' Tuning Curve')

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
    try:
        os.makedirs(directory)
    except os.error, e:
	if e.errno != errno.EEXIST:
	    raise
    pylab.savefig(normalize_path(directory+filename) + '.png')
