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
from topo.misc.util import frange
from topo.analysis.vision import complexity
import topo.analysis.vision
from topo.plotting.plot import make_template_plot, Plot
from topo import param
from topo.param import ParameterizedFunction
from topo.param.parameterized import ParamOverrides
from topo.plotting.plotgroup import default_measureable_sheet



class PylabPlotCommand(ParameterizedFunction):
    """Parameterized command for plotting using Matplotlib/Pylab."""
      
    file_dpi = param.Number(
        default=100.0,bounds=(0,None),softbounds=(0,1000),doc="""
        Default DPI when rendering to a bitmap.  
        The nominal size * the dpi gives the final image size in pixels.  
        E.g.: 4"x4" image * 80 dpi ==> 320x320 pixel image.""")
                                      
    file_format = param.String(default="png",doc="""
        Which image format to use when saving images.
        The output can be png, ps, pdf, svg, or any other format
        supported by Matplotlib.""")

    # JABALERT: Should replace this with a filename_format and
    # associated parameters, as in PlotGroupSaver.  
    # Also should probably allow interactive display to be controlled
    # separately from the filename, to make things work more similarly
    # with and without a GUI.
    filename = param.String(default=None,doc="""
        Optional base of the filename to use when saving images;
        if None the plot will be displayed interactively.
        
        The actual name is constructed from the filename base plus the
        suffix plus the current simulator time plus the file_format.""")

    filename_suffix = param.String(default="",doc="""
        Optional suffix to be used for disambiguation of the filename.""")

    title = param.String(default=None,doc="""
        Optional title to be used when displaying the plot interactively.""")

    __abstract = True


    def _set_windowtitle(self,title):
        """
        Helper function to set the title (if not None) of this PyLab plot window.
        """
        
        # At the moment, PyLab does not offer a window-manager-independent
        # means for controlling the window title, so what we do is to try
        # what should work with Tkinter, and then suppress all errors.  That
        # way we should be ok when rendering to a file-based backend, but
        # will get nice titles in Tk windows.  If other toolkits are in use,
        # the title can be set here using a similar try/except mechanism, or
        # else there can be a switch based on the backend type.
        if title is not None:
            try: 
                manager = pylab.get_current_fig_manager()
                manager.window.title(title)
            except:
                pass
    
    
    def _generate_figure(self,p):
        """
        Helper function to display a figure on screen or save to a file.
        
        p should be a ParamOverrides instance containing the current
        set of parameters.
        """

        pylab.show._needmain=False
        if p.filename is not None:
            # JABALERT: need to reformat this as for other plots
            fullname=p.filename+p.filename_suffix+str(topo.sim.time())+"."+p.file_format
            pylab.savefig(normalize_path(fullname), dpi=p.file_dpi)
        else:
            self._set_windowtitle(p.title)
            pylab.show()



class vectorplot(PylabPlotCommand):
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

    # JABALERT: All but the first two arguments should probably be Parameters
    def __call__(self,vec,xvalues=None,style='-',label=None,**params):
        p=ParamOverrides(self,params)

        if xvalues is not None:
            pylab.plot(xvalues, vec, style, label=label)
        else:
            pylab.plot(vec, style, label=label)
            
        pylab.grid(True)
        self._generate_figure(p)



class matrixplot(PylabPlotCommand):
    """
    Simple plotting for any matrix as a bitmap with axes.

    Like MatLab's imagesc, scales the values to fit in the range 0 to 1.0.
    Intended for interactive debugging or analyzing from the command
    prompt.  See MatPlotLib's pylab functions to create more elaborate
    or customized plots; this is just a simple example.
    """

    plot_type = param.Parameter(default=pylab.gray,doc="""
        Matplotlib command to generate the plot, e.g. pylab.gray or pylab.hsv.""")
    
    # JABALERT: All but the first two should probably be Parameters
    def __call__(self,mat,aspect=None,colorbar=True,**params):
        p=ParamOverrides(self,params)
        
        p.plot_type()
        pylab.figure(figsize=(5,5))
        pylab.imshow(mat,interpolation='nearest',aspect=aspect)
        if colorbar and (mat.min()!= mat.max()): pylab.colorbar()
        self._generate_figure(p)



# JABALERT: Not sure if there is any reason to keep this command
# now that matrixplot supports any plot type.
class matrixplot_hsv(matrixplot):
    """
    Simple plotting for any matrix as a bitmap with axes.
    Same as matrixplot(plot_type=pylab.hsv), i.e., values are colored
    in hsv colorspace rather than greyscale.
    """
    
    plot_type = param.Parameter(default=pylab.hsv)



class matrixplot3d(PylabPlotCommand):
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
    
    # JABALERT: All but the first two arguments should probably be Parameters
    def __call__(self,mat,type="wireframe",**params):
        p=ParamOverrides(self,params)
    
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
    
        self._generate_figure(p)



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



class histogramplot(PylabPlotCommand):
    """
    Compute and plot the histogram of the supplied data.
    
    See help(pylab.hist) for help on the histogram function itself.

    If given, colors is an iterable collection of matplotlib.colors
    (see help (matplotlib.colors) ) specifying the bar colors.

    Example use:
        histogramplot([1,1,1,2,2,3,4,5],title='hist',colors='rgb',bins=3,normed=1)
    """
    
    # JABALERT: All but the first two arguments should probably be Parameters    
    def __call__(self,data,colors=None,**params):
        p=ParamOverrides(self,params,allow_extra_keywords=True)        
    
        pylab.figure(figsize=(4,2))
        n,bins,bars = pylab.hist(data,**(p.extra_keywords))
    
        # if len(bars)!=len(colors), any extra bars won't have their
        # colors changed, or any extra colors will be ignored.
        if colors: [bar.set_fc(color) for bar,color in zip(bars,colors)]

        self._generate_figure(p)



class gradientplot(matrixplot):
    """
    Compute and show the gradient plot of the supplied data.
    Translated from Octave code originally written by Yoonsuck Choe.

    If the data is specified to be cyclic, negative differences will
    be wrapped into the range specified (1.0 by default).
    """
    
    # JABALERT: All but the first two arguments should probably be Parameters    
    def __call__(self,data,cyclic=True,cyclic_range=1.0,**params):
        p=ParamOverrides(self,params)
    
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

        super(gradientplot,self).__call__(sqrt(dx*dx+dy*dy))



class activityplot(PylabPlotCommand):
    """
    Plots the activity in a sheet.

    Gets plot's extent from sheet.bounds.aarect(). Adds a title and
    allows the selection of a colormap.  If activity is not given,
    the sheet's current activity is used.
    """

    # JABALERT: All but the first two arguments should probably be Parameters    
    # Not sure what this command is for or if anyone is using it.
    def __call__(self,sheet,activity=None,cmap=None,**params):
        p=ParamOverrides(self,params)

        l,b,r,t = sheet.bounds.aarect().lbrt()
        if activity is None:
            activity = sheet.activity
        if cmap is None:
            cmap=pylab.cm.Greys
        pylab.imshow(activity, extent=(l,r,b,t),cmap=cmap)

        self._generate_figure(p)
        


class topographic_grid(PylabPlotCommand):
    """
    By default, plot the XPreference and YPreference preferences for all
    Sheets for which they are defined, using MatPlotLib.

    If sheet_views other than XPreference and YPreference are desired,
    the names of these can be passed in as arguments.
    """
    
    # JABALERT: All the arguments should probably be Parameters        
    def __call__(self,xsheet_view_name='XPreference',ysheet_view_name='YPreference',axis=[-0.5,0.5,-0.5,0.5],**params):
        p=ParamOverrides(self,params)

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
                p.filename_suffix="_"+sheet.name
                self._generate_figure(p)
            

class overlaid_plots(PylabPlotCommand):
    """
    Use matplotlib to make a plot from a bitmap constructed using the
    specified plot_template, plus additional overlaid line contour
    plot(s) specified with ('contours',map-name,contour-value,line-color)
    quadruples and/or overlaid arrows plot(s) specified with ('arrows',map-name for arrows location,
    map-name for arrows scaling,arrow-color) quadruples.
    """
    
    # JABALERT: All but the first two arguments should probably be Parameters    
    def __call__(self,plot_template=[{'Hue':'OrientationPreference'}],overlay=[('contours','OcularPreference',0.5,'black'),('arrows','DirectionPreference','DirectionSelectivity','white')],normalize=False,**params):
        p=ParamOverrides(self,params)

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
                        v = pylab.flipud(sheet.sheet_views[pref].view()[0])
                        
                        if (t=='contours'):
                            pylab.contour(v,[sel,sel],colors=c,linewidths=2)
                            
                        if (t=='arrows'):							
                            s = pylab.flipud(sheet.sheet_views[sel].view()[0])
                            scale=int(pylab.ceil(log10(len(v))))
                            X=pylab.array([x for x in xrange(len(v)/scale)])                  
                            v_sc=pylab.zeros((len(v)/scale,len(v)/scale))
                            s_sc=pylab.zeros((len(v)/scale,len(v)/scale))
                            for i in X:
                                for j in X:
                                    v_sc[i][j]=v[scale*i][scale*j]
                                    s_sc[i][j]=s[scale*i][scale*j]
                            pylab.quiver(scale*X,scale*X,-cos(2*pi*v_sc)*s_sc,-sin(2*pi*v_sc)*s_sc,color=c,edgecolors=c,minshaft=3,linewidths=1) 						
    							
                    title='%s overlaid with %s at time %s' %(plot.name,pref,topo.sim.timestr())
                    if isint: pylab.ion()
                    p.filename_suffix="_"+sheet.name                    
                    self._generate_figure(p)
                


class tuning_curve(PylabPlotCommand):
    """
    Plot a tuning curve for a feature, such as orientation, contrast, or size.

    The curve datapoints are collected from the curve_dict for
    the units at the specified coordinates in the specified sheet
    (where the units and sheet may be set by a GUI, using 
    topo.analysis.featureresponses.UnitCurveCommand.sheet and 
    topo.analysis.featureresponses.UnitCurveCommand.coords, 
    or by hand).
    """
      
    coords = param.List(default=[(0,0)],doc="""
        List of coordinates of units to measure.""")

    sheet = param.ObjectSelector(
        default=None,compute_default_fn=default_measureable_sheet,doc="""
        Name of the sheet to use in measurements.""")

    x_axis = param.String(default="",doc="""
        Feature to plot on the x axis of the tuning curve""")

    # Can we list some alternatives here, if there are any
    # useful ones?
    plot_type = param.Parameter(default=pylab.plot,doc="""
        Matplotlib command to generate the plot.""")

    unit = param.String(default="",doc="""
        String to use in labels to specify the units in which curves are plotted.""")

    __abstract = True


    def _format_x_tick_label(self,x):
        return "%3.1f" % x

    def _rotate(self, seq, n=1):
        n = n % len(seq) # n=hop interval
        return seq[n:] + seq[:n]

    def _curve_values(self, i_value, j_value, curve):
        """Return the x, y, and x ticks values for the specified curve from the curve_dict"""
        x_values=sorted(curve.keys())
        y_values=[curve[key].view()[0][i_value,j_value] for key in x_values]
        return x_values,y_values,x_values
                    

    def __call__(self,**params):
        p=ParamOverrides(self,params)
        sheet = p.sheet if p.sheet is not None else \
                topo.analysis.featureresponses.UnitCurveCommand.sheet

        coords = p.coords if p.coords is not None else \
                 topo.analysis.featureresponses.UnitCurveCommand.coords
        
        for coordinate in coords:
            i_value,j_value=sheet.sheet2matrixidx(coordinate[0],coordinate[1])
        
            pylab.figure(figsize=(7,7))
            isint=pylab.isinteractive()
            pylab.ioff()
    
            pylab.ylabel('Response')
            pylab.xlabel('%s (%s)' % (p.x_axis.capitalize(),p.unit))
            pylab.title('Sheet %s, coordinate(x,y)=(%d,%d) at time %s' % 
                        (sheet.name,coordinate[0],coordinate[1],topo.sim.timestr()))
            title='%s: %s Tuning Curve' % (topo.sim.name,p.x_axis.capitalize())
        
            self.first_curve=True
            for curve_label in sorted(sheet.curve_dict[p.x_axis].keys()):
                x_values,y_values,ticks=self._curve_values(i_value,j_value,sheet.curve_dict[p.x_axis][curve_label])
                labels = [self._format_x_tick_label(x) for x in ticks]
                pylab.xticks(x_values, labels)

                p.plot_type(x_values, y_values, label=curve_label)
                self.first_curve=False
                 
            if isint: pylab.ion()
            pylab.legend(loc=4)
    
            self._generate_figure(p)



class cyclic_tuning_curve(tuning_curve):
    """
    Same as tuning_curve, but rotates the curve so that minimum y
    values are at the minimum x value to make the plots easier to
    interpret.  Such rotation is valid only for periodic quantities
    like orientation or direction, and only if the correct period
    is set.
    
    At present, the y_values and labels are rotated by an amount
    determined by the minmum y_value for the first curve plotted
    (usually the lowest contrast curve).
    """

    cyclic_range = param.Number(default=pi,bounds=(0,None),softbounds=(0,10),doc="""
        Range of the cyclic quantity (e.g. pi for the orientation of
        a symmetric stimulus, or 2*pi for motion direction or the
        orientation of a non-symmetric stimulus).""")
    
    unit = param.String(default="degrees",doc="""
        String to use in labels to specify the units in which curves are plotted.""")


    # This implementation should work for quantities periodic with
    # some multiple of pi that we want to express in degrees, but it
    # will need to be reimplemented in a subclass to work with other
    # cyclic quantities.
    def _format_x_tick_label(self,x):
        return str(int(180*x/pi))


    def _curve_values(self, i_value, j_value, curve):
        """
        Return the x, y, and x ticks values for the specified curve from the curve_dict.

        With the current implementation, there may be cases (i.e.,
        when the lowest contrast curve gives a lot of zero y_values)
        in which the maximum is not in the center.  This may
        eventually be changed so that the preferred orientation is in
        the center.
        """
        if self.first_curve==True:
            x_values= sorted(curve.keys())
            y_values=[curve[key].view()[0][i_value,j_value] for key in x_values]
            
            min_arg=argmin(y_values)
            x_min=x_values[min_arg] 
            y_min=y_values[min_arg]
            y_values=self._rotate(y_values, n=min_arg)
            self.ticks=self._rotate(x_values, n=min_arg)
            self.ticks+=[x_min]
            x_max=min(x_values)+self.cyclic_range
            x_values.append(x_max)
            y_values.append(y_min)

            self.x_values=x_values
        else:
            y_values=[curve[key].view()[0][i_value,j_value] for key in self.ticks]

        return self.x_values,y_values,self.ticks

            

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


# JABALERT: not sure whether this is currently used
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
### Should also be rewritten using PylabPlotCommand.
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



# JABALERT: Untested as of Mon Nov 10 12:59:54 GMT 2008
class plot_tracked_attributes(PylabPlotCommand):
    """
    Plots parameter values associated with an AttributeTrackingOF.
    Example call:
    VT=AttributeTrackingOF(function=HE, debug_params=['a', 'b',], units=[(0,0),(1,1)], step=1)
    plot_tracked_attributes(VT,0,10000,attrib_names=['a'],units=[(0,0)], filename='V1')
    """

    # JABALERT: These parameters need to be documented.
    raw = param.Boolean(default=False)

    attrib_names = param.List(default=[])
    
    ylabel = param.String(default="")

    # Should be renamed to coords to match other commands
    units = param.List(default=[])

    ybounds = param.Parameter(default=(None,None))
   

    # JABALERT: All but the first two arguments should probably be Parameters
    def __call__(self,output_fn,init_time,final_time,**params):
        p=ParamOverrides(self,params)

        attrs = p.attrib_names if len(p.attrib_names)>0 else output_fn.attrib_names
        for a in attrs:
            pylab.figure(figsize=(6,4))
            isint=pylab.isinteractive()
            pylab.ioff()
            pylab.grid(True)
            ylabel=p.ylabel
            pylab.ylabel(a+" "+ylabel)
            pylab.xlabel('Iteration Number')
            
            coords = p.units if len(p.units)>0 else output_fn.units
            for coord in coords:
                y_data=[y for (x,y) in output_fn.values[a][coord]]
                x_data=[x for (x,y) in output_fn.values[a][coord]]
                if p.raw==True:
                    plot_data=zip(x_data,y_data)
                    pylab.save(normalize_path(filename+a+'(%.2f, %.2f)' %(coord[0], coord[1])),plot_data,fmt='%.6f', delimiter=',')
                
                
                pylab.plot(x_data,y_data, label='Unit (%.2f, %.2f)' %(coord[0], coord[1]))
                (ymin,ymax)=p.ybounds
                pylab.axis(xmin=init_time,xmax=final_time,ymin=ymin,ymax=ymax)
                    
            if isint: pylab.ion()
            pylab.legend(loc=0)
            p.title=topo.sim.name+': '+a
            p.filename_suffix=a
            self._generate_figure(p)



# JABALERT: Should be updated to plot for a specified list of sheets,
# and then the combination of all of them, so that it will work for
# any network.  Will need to remove the simple_sheet_name and
# complex_sheet_name parameters once that works.
class plot_modulation_ratio(PylabPlotCommand):
    """
    This function computes the modulation ratios of neurons in the
    specified sheets and plots their histograms. See
    analysis.vision.complexity for more info.
    """

    # JABALERT: All but the first argument should probably be Parameters
    def __call__(self,fullmatrix,title=None,filename=None,simple_sheet_name=None,complex_sheet_name=None,bins=frange(0,2.0,0.1,inclusive=True),**params):
        p=ParamOverrides(self,params,allow_extra_keywords=True)

        if (topo.sim.objects().has_key(simple_sheet_name)):
            v1s = complexity(fullmatrix[topo.sim[simple_sheet_name]])
            pylab.figure()
            pylab.subplot(311)
            pylab.hist(v1s,bins)
            pylab.axis([0,2.0,0,3500])
            
        if (topo.sim.objects().has_key(complex_sheet_name)):
            v1c = complexity(fullmatrix[topo.sim[complex_sheet_name]])
            pylab.subplot(312)
            pylab.hist(v1c,bins)
            pylab.axis([0,2.0,0,3500])
            pylab.subplot(313)
            
            if (topo.sim.objects().has_key(simple_sheet_name)):
                # JABALERT: Jan needs to reenable this
                #pylab.hist(numpy.concatenate(array(v1s),array(v1c)),bins)
                pylab.axis([0,2.0,0,3500])
    
        self._generate_figure(p)

