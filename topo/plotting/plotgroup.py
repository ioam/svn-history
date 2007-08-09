"""
Hierarchy of PlotGroup classes, i.e. output-device-independent sets of plots.

Includes PlotGroups for standard plots of anything in a Sheet database,
plus weight plots for one unit, and projections.

$Id$
"""
__version__='$Revision$'

import copy
import Image

import __main__

import topo

from topo.base.parameterizedobject import ParameterizedObject
from topo.base.parameterclasses import Parameter,BooleanParameter,StringParameter,Number
from topo.base.sheet import Sheet
from topo.base.cf import CFSheet,CFProjection
from topo.base.projection import ProjectionSheet

from plot import make_template_plot, Plot


### CEBHACKALERT: make sure error messages are reasonable for trying to do plots
### with e.g. sheet=None or projection=None.


def cmp_plot(plot1,plot2):
    """
    Comparison function for sorting Plots.
    It compares the precedence number first and then the src_name and name attributes.
    """
    if plot1.precedence != plot2.precedence:
	return cmp(plot1.precedence,plot2.precedence)
    else:
	return cmp((plot1.plot_src_name+plot1.name),
		   (plot2.plot_src_name+plot2.name))


def identity(x):
    """No-op function for use as a default."""
    return x


### Temporary
# ObjectSelectorParameter, plus a parent shared with ClassSelectorParameter?
class RangedParameter(Parameter):

    __slots__ = ['range']
    __doc__ = property((lambda self: self.doc))

    def __init__(self, default=None, range=[],instantiate=True,**params):
        Parameter.__init__(self,default=default,instantiate=instantiate,**params)
        self.range = range

    def __set__(self,obj,val):
        #assert not isinstance(val,str),"%s"%val
        super(RangedParameter,self).__set__(obj,val)

        


class PlotGroup(ParameterizedObject):
    """
    Container that has one or more Plots and also knows how to arrange
    the plots and other special parameters.
    """
    ###JCALERT:
    ### - clean up the doc.
    ### - rewrite the test file.

    # listparameter
    #plot_list = Parameter(default=[],instantiate=True)

    cmd_location = Parameter(default=__main__.__dict__)

    update_command = Parameter(default="",doc="""
    Command to execute before updating this plot, e.g. to calculate sheet views.
    
    The command can be any Python code, and will be evaluated in the main namespace
    (as if it were typed into a .ty script).  The initial value is determined by
    the template for this plot, but various arguments can be passed, a modified
    version substituted, etc.""")

    ## CEBHACKALERT
    command = update_command
    
    plot_command = Parameter(default="",doc="""
    Command to execute when updating sheet or coordinate of unit to be plotted
    when the simulator time has not changed.
    In the case of a full-field stimulus, responses do not need to be re-measured
    since the necessary values are already stored. 
    
    The command can be any Python code, and will be evaluated in the main namespace
    (as if it were typed into a .ty script).  The initial value is determined by
    the template for this plot, but various arguments can be passed, a modified
       version substituted, etc.""")
    
    def __init__(self,**params):
        """
        Initialize using a static list of Plots that will make up this PlotGroup.
        """
        super(PlotGroup,self).__init__(**params)

        # CEBALERT
        if 'plot_list' in params:
            self.plot_list = copy.copy(params['plot_list'])
            #del params['plot_list']
        else:
            self.plot_list = []
        
	#self.plot_list = plot_list	
	self.labels = [] # List of plot labels

        # In the future, it might be good to be able to specify the
        # plot rows and columns using tuples.  For instance, if three
        # columns are desired with the plots laid out from left to
        # right, we could use (None, 3).  If three rows are desired
        # then (3, None).  Another method that would work is [3,2,4]
        # would have the first row with 3, the second row with 2, the
        # third row with 4, etc.  The default left-to-right ordering
        # in one row could perhaps be represented as (None, Inf).
        
	self.initial_plot = True  # CB: what's this?
	self.time = None

        ## CB  import __main__; __main__.__dict__['zzz'] = self


    def _plot_command(self):
        exec self.plot_command in self.cmd_location



    def _update_command(self):
        exec self.update_command in self.cmd_location


        
    def _plot_list(self):
	"""
	function that returns the plot_list.
	Re-implemented by TemplatePlotGroup to construct the plot list as specified by the template.
	"""
	return self.plot_list


    # CB: rename
    def draw_plots(self,update=True):
	"""

	If update=True, execute the command associated with the template
	(e.g. generating the Sheetviews necessary to create the PlotGroup's Plots).
	"""
        if update: self._update_command()
        self._plot_command()
        self._make_plots()
        

    # CB: ** replace calls to these two methods **
    def redraw_plots(self):
        self.draw_plots(update=False)
    def update_plots(self):
        self.draw_plots(update=True)



    def _make_plots(self):
        """
        Generate the sorted and scaled list of plots constituting the PlotGroup.
        """

        self.plots = [plot for plot in self._plot_list() if plot != None]

        # Suppress plots in the special case of an initial plot that
        # has no resizable images, to suppress plotgroups that have
        # nothing but a color key
        resizeable_plots = [p for p in self.plots if p.resize]
        if self.initial_plot and not resizeable_plots:
            self.plots=[]

        # Take the timestamps from the underlying Plots
	timestamps = [plot.timestamp for plot in self._plot_list()
                      if plot != None and plot.timestamp >= 0]
        if timestamps != []:
            self.time = max(timestamps)
            if max(timestamps) != min(timestamps):
                self.warning("Combining Plots from different times (%s,%s)" %
                             (min(timestamps),max(timestamps)))

	self._ordering_plots()	
	self.generate_labels()


    def generate_labels(self):
	""" Function used for generating the labels."""
	self.labels = []
	for plot in self.plots:
	    self.labels.append(plot.plot_src_name + '\n' + plot.name)


    def _ordering_plots(self):
	"""
	Function called to sort the Plots in order.
	They are ordered according to their precedence number first, and then by alphabetical order.
	"""
	self.plots.sort(cmp_plot)




### In the rest of the file, whenever we do a loop through all the
### simulation's sheets, seems like we should have set the sheet
### Parameter's range instead. sheet's range is set by the GUI.
### i.e. maybe there should be a sheet parameter here, with its range
### set when the plotgroup is instantiated. Then if sheet=None, the
### sheet's range can be used as the list of sheets.


# rename; represents 3d AND draws plots on itself
class XPlotGroup(PlotGroup):

    sheet_type = Sheet

    sheet = RangedParameter(default=None,doc="""
    The Sheet from which to produce plots.
    If set to None, plots are created for each appropriate Sheet.""") 


    sheet_coords = BooleanParameter(default=False,doc="""
    Whether to scale plots based on their relative sizes in sheet
    coordinates.  If true, plots are scaled so that their sizes are
    proportional to their area in sheet coordinates, so that one can
    compare corresponding areas.  If false, plots are scaled to have
    similar sizes on screen, regardless of their corresponding
    sheet areas, which maximizes the size of each plot.""")

    normalize = BooleanParameter(default=False,doc="""
        Whether to scale plots so that the peak value will be white
        and the minimum value black.  Otherwise, 0.0 will be black
        and 1.0 will be white.  Normalization has the advantage of
        ensuring that any data that is present will be visible, but
        the disadvantage that the absolute scale will be obscured.
        Non-normalized plots are guaranteed to be on a known scale,
        but only values between 0.0 and 1.0 will be visibly
        distinguishable.""")

    integer_scaling = BooleanParameter(default=False,doc="""
        When scaling bitmaps, whether to ensure that the scaled bitmap is an even
        multiple of the original.  If true, every unit will be represented by a
        square of the same size.  Typically false so that the overall area will
        be correct, e.g. when using Sheet coordinates, which is often more
        important.""")




    def sizeconvertfn(self,X):
        if self.integer_scaling:
            return int(X)
        else:
            return identity(X)
        
 
    def __init__(self,**params):
        super(XPlotGroup,self).__init__(**params)

        # Enforce a minimum plot height for the tallest plot of the PlotGroup.
        self.INITIAL_PLOT_HEIGHT = 150
        self.height_of_tallest_plot = 1.0
        self.minimum_height_of_tallest_plot = 1.0




######################################################################
### At least some of this scaling would be common to all plotgroups, if
### some (e.g. featurecurve) didn't open new windows.
    def _make_plots(self):
        super(XPlotGroup,self)._make_plots()
        # scaling the Plots
	### JCALERT: momentary hack        
	if self.plots!=[]:
	    self.scale_images()


    def scale_images(self):
        """
        Enlarge the bitmaps as needed for display.
        """
        ### JABALERT: Should this be done by the GUI instead, without changing the bitmaps?
        
        ### JCALERT: that cannot be in the constructor for the moment, because when creating the 
 	### panel, there is no PlotGroup assigned to it... It will change when all will be inserted 
 	### in the PlotGroup (i.e scale_image, set_initial_master_zoom, compute_max_height...)
        if self.initial_plot:
            self._calculate_minimum_height_of_tallest_plot()
            
        ### JCALERT: here we should take the plot bounds instead of the sheet one (id in set_height_of..)?
        resizeable_plots = [p for p in self.plots if p.resize]
        if resizeable_plots:
            max_sheet_height = max([(topo.sim.objects(Sheet)[p.plot_src_name].bounds.lbrt()[3]
                                     -topo.sim.objects(Sheet)[p.plot_src_name].bounds.lbrt()[1])
                                    for p in resizeable_plots])

	for plot in self.plots:
            if not plot.resize:
                scaling_factor = 1
            else:
		if self.sheet_coords:		   
                    s = topo.sim.objects(Sheet).get(plot.plot_src_name,None)
		    scaling_factor=self.sizeconvertfn(self.height_of_tallest_plot/float(s.xdensity)/max_sheet_height)
		else:
		    scaling_factor=self.sizeconvertfn(self.height_of_tallest_plot/float(plot.bitmap.height()))
                    ### JABHACKALERT: Enforces a minimum scaling factor of 1,
                    ### to avoid divide-by-zero errors.  The actual cause of these
                    ### errors should instead be avoided elsewhere.
                    if (scaling_factor <= 0):
                        scaling_factor=1
                    
	    plot.rescale(scaling_factor)


    def _calculate_minimum_height_of_tallest_plot(self):
	"""
        Calculate the size of the plot that will generate the largest bitmap.

        This value is used to set the initial plot heights, and the
        minimum height to which the plot can be reduced.
	"""
        # JCALERT: Should be rewritten more cleanly.
        # JPALERT: Indeed, since it seems to be wrong.  Plots with
        # large bounds and low desnity are plotted very large and
        # can't be reduced.  (E.g. sheet bounds -60 to +60, density =
        # 1/6)
        # JPHACKALERT: My changes below are hacks to try to get it to
        # do something sensible for simulations with large bounds.  We
        # need to spec out how it _should_ behave first, then rewrite.
        resizeable_plots = [p for p in self.plots if p.resize]
        if resizeable_plots:
##             max_sheet_height = max([(topo.sim.objects(Sheet)[p.plot_src_name].bounds.lbrt()[3]
##                               -topo.sim.objects(Sheet)[p.plot_src_name].bounds.lbrt()[1])
##                               for p in resizeable_plots])
##             max_density = max([topo.sim.objects(Sheet)[p.plot_src_name].xdensity
##                                for p in resizeable_plots])
##             # JPALERT: the max_density and the max_height may come
##             # from different sheets, it doesn't make sense to multiply them
##             sheet_max_height = max_density*max_sheet_height
            matrix_max_height = max([p.bitmap.height() for p in self.plots if p.resize])
##             max_height = max(sheet_max_height,matrix_max_height)
            max_height = matrix_max_height
            self.minimum_height_of_tallest_plot = max_height
            if (max_height >= self.INITIAL_PLOT_HEIGHT):
                self.height_of_tallest_plot = max_height
            else:   
                self.height_of_tallest_plot = self.INITIAL_PLOT_HEIGHT
            self.initial_plot=False
######################################################################

    


class TemplatePlotGroup(XPlotGroup):
    """
    PlotGroup that is built as specified by a PlotGroupTemplate.
    """

    template = Parameter() 

    def __init__(self,**params):
	super(TemplatePlotGroup,self).__init__(**params)

        ##### CEBHACKALERT: set params from template #####
        assert self.template is not None
        for n in self.template.params().keys():
            if hasattr(self,n):
                setattr(self,n,getattr(self.template,n))
        ##################################################
                
	# Add static images to the added_plot_list, as specified by the template.
        self._add_static_images()

	
    def _plot_list(self):
        """
        Procedure that is called when creating a PlotGroup.

        Returns the plot_list attribute, i.e., the list of plots that
        are specified by the PlotGroup template.

        This function calls create_plots, which is implemented in each
        TemplatePlotGroup subclass.
        """
	if self.sheet:
            sheet_list = [self.sheet]
	else:
	    sheet_list = topo.sim.objects(self.sheet_type).values() #self.params()['sheet'].range()  
   
	plot_list = self.plot_list
        # Loop over all sheets that passed the filter.
        #     Loop over each individual plot template:
        #         Call the create_plots function to create the according plot
        for each in sheet_list:
	    for (pt_name,pt) in self.template.plot_templates:
		plot_list = plot_list + self._create_plots(pt_name,pt,each)
    	return plot_list


    def _create_plots(self,pt_name,pt,sheet):
	""" 
	Sub-function of _plot_list().
	Creates a plot corresponding to a plot_template, its name, and a sheet.
	"""
        p = make_template_plot(pt,sheet.sheet_view_dict,sheet.xdensity,
 			       sheet.bounds,self.normalize,name=pt_name)

	return [p]


    def _add_static_images(self):
        """
        Construct a static image Plot (e.g. a color key for an Orientation Preference map).
        """        
        for image_name,file_path in self.template.static_images :
            image = Image.open(file_path)
	    plot = Plot(image,name=image_name)
            self.plot_list.append(plot)



### CEBALERT: shouldn't contain any CF-related stuff. 
class ProjectionSheetPlotGroup(TemplatePlotGroup):
    """
    Abstract PlotGroup for visualizations of the Projections of one ProjectionSheet.

    Requires self.keyname to be set to the name of a placeholder
    SheetView that will be replaced with a key that is unique to a
    particular Projection of the current Sheet.
    """
    _abstract_class_name = "ProjectionSheetPlotGroup"

    keyname = "ProjectionSheet" # CB: document what these are

    sheet = RangedParameter(default=None,doc="""
    The Sheet from which to produce plots.""")


    def _update_command(self):

        # CEBALERT: rather than various scattered tests like the one below and for projections in later classes,
        # have some method (probabable decalred in a super calss) like "_check_conditions()".
        if self.sheet is None: raise ValueError("%s must have a sheet (currently None)."%self)
	### JCALERT: commands in analysis.py should be re-written to
	### avoid setting these global parameters.
	topo.commands.analysis.sheet_name = self.sheet.name
        super(ProjectionSheetPlotGroup,self)._update_command()
        
		
    def _create_plots(self,pt_name,pt,sheet):
	"""Creates plots as specified by the plot_template."""
        if not isinstance(sheet,CFSheet):
            self.warning('Requested Projection view from a Sheet that is not a CFSheet.')
            return []
        else:
	    # Special case: if the Strength is set to self.keyname, we
	    # request UnitViews (i.e. by changing the Strength key in
	    # the plot_channels). Otherwise, we consider Strength as
	    # specifying an arbitrary SheetView.
	    if ( pt.get('Strength', None) == self.keyname):
                plot_list = []
                for p in sheet.in_connections: 
		    plot_channels = copy.deepcopy(pt)
		    # Note: the UnitView is in the src_sheet view_dict,
		    # and the name in the key is the destination sheet.
		    key = (self.keyname,sheet.name,p.name)
		    plot_channels['Strength'] = key
                    plot_list.append(make_template_plot(plot_channels,p.src.sheet_view_dict,
                                                        p.src.xdensity,
                                                        None,self.normalize,name=p.name))
                return plot_list
                
	    else: # Fall back to normal case
                return super(ProjectionSheetPlotGroup,self)._create_plots(pt_name,pt,sheet)

 
    def generate_labels(self):
	""" Function used for generating the labels."""
	self.labels = []
	for plot in self.plots:
	    self.labels.append(plot.name + '\n(from ' + plot.plot_src_name+')')



class ProjectionActivityPlotGroup(ProjectionSheetPlotGroup):
    """Visualize the activity of all Projections into a ProjectionSheet."""

    keyname='ProjectionActivity' 

 
    ### CEBALERT: very similar to large part of ProjectionSheetPlotGroup's _create_plots
    def _create_plots(self,pt_name,pt,sheet):
	"""Creates plots as specified by the plot_template."""

        # CEBALERT: should there be isinstance(sheet,ProjectionSheet) here, or
        # has that already been ensured? Same question applies to all the other
        # _create_plots() methods (where the test isn't already made).
        plot_list = []
        for p in sheet.in_connections: 
            plot_channels = copy.deepcopy(pt) 
            key = (self.keyname,sheet.name,p.name)
            plot_channels['Strength'] = key
            plot_list.append(make_template_plot(plot_channels,p.dest.sheet_view_dict,
                                                p.dest.xdensity,
                                                p.dest.bounds,self.normalize,name=p.name))
        return plot_list
                




class CFPlotGroup(ProjectionSheetPlotGroup):

    situate = BooleanParameter(default=False,doc=
                               """If True, plots the weights on the
entire source sheet, using zeros for all weights outside the
ConnectionField.  If False, plots only the actual weights that are
stored.""")

# CEBALERT: all necessary situate stuff removed from tkgui? See ALERT in CFRelatedPlotGroupPanel.



	    
### JABALERT: Should pull out common code from
### ConnectionFieldsPlotGroup, ProjectionActivityPlotGroup, and
### ProjectionPlotGroup into a shared parent class; then those
### three classes should be much shorter.

class ConnectionFieldsPlotGroup(CFPlotGroup):
    """
    Visualize a ConnectionField for each of a CFSheet's CFProjections.
    """
    keyname='Weights'
    situate = BooleanParameter(False)

    # JABALERT: need to show actual coordinates of unit returned
    x = Number(default=0.0,doc="""x-coordinate of the unit to plot""")
    y = Number(default=0.0,doc="""y-coordinate of the unit to plot""")
## """Sheet coordinate location desired.  The unit nearest this location will be returned.
## It is an error to request a unit outside the area of the Sheet.""")

        
    def _update_command(self):
	topo.commands.analysis.coordinate = (self.x,self.y)
	super(ConnectionFieldsPlotGroup,self)._update_command()

    def _create_plots(self,pt_name,pt,sheet):
	""" 
	Sub-function of _plot_list().
	Creates a plot as specified by a Connection Field plot_template:
	allows creating a connection field plot or a normal plot.
	"""
        if not isinstance(sheet,CFSheet):
            self.warning('Requested Projection view from a Sheet that is not a CFSheet.')
            return []
        else:
	    if ( pt.get('Strength', None) == self.keyname):
                plot_list = []
                for p in sheet.in_connections:
		    plot_channels = copy.deepcopy(pt)
		    key = (self.keyname,sheet.name,p.name,self.x,self.y)
		    plot_channels['Strength'] = key
		    if self.situate:
			plot_list.append(make_template_plot(plot_channels,p.src.sheet_view_dict,p.src.xdensity,
							    None,self.normalize,name=p.name))
		    else:
			(r,c) = p.dest.sheet2matrixidx(self.x,self.y)
			plot_list.append(make_template_plot(plot_channels,p.src.sheet_view_dict,p.src.xdensity,
							    p.cf(r,c).bounds,self.normalize,name=p.name))
                return plot_list
			
	    else: # Fall back to normal case
                return super(ConnectionFieldsPlotGroup,self)._create_plots(pt_name,pt,sheet)



### Someday will need an abstract ProjectionPlotGroup


class CFProjectionPlotGroup(CFPlotGroup):
    """Visualize one CFProjection."""

    keyname='Weights'

    projection = RangedParameter(default=None)

    ### CEBHACKALERT: tkpo gui not setup to read softbounds
    ### JPALERT: The bounds are meaningless for large sheets anyway.  If a sheet
    ### is specified in, say, visual angle coordinates (e.g., -60 to +60 degrees), then
    ### the soft min of 5.0/unit will still give a 600x600 array of CFs!
    ### Density should probably be specified WRT to sheet bounds,
    ### instead of per-unit-of-sheet.
    
    density = Number(default=10.0,doc='Number of units to plot per 1.0 distance in sheet coordinates',
                     softbounds=(5.0,50.0))
    
    situate = BooleanParameter(False) # override default 

    def __init__(self,**params):
        super(CFProjectionPlotGroup,self).__init__(**params)
        self.INITIAL_PLOT_HEIGHT = 5
        
        ### JCALERT! shape determined by the plotting density
        ### This is set by self.generate_coords()
        self.proj_plotting_shape = (0,0)
    

    def _update_command(self):
        if self.projection is None: raise ValueError("%s must have a projection (currently None)."%self)
	### JCALERT: commands in analysis have to be re-written so that to avoid
	### setting all these global parameters.
        topo.commands.analysis.proj_coords = self.generate_coords()
        topo.commands.analysis.proj_name = self.projection.name
        super(CFProjectionPlotGroup,self)._update_command()

		
    def _create_plots(self,pt_name,pt,sheet):
	""" 
	Sub-function of _plot_list().
	Creates a plot as specified by a Projection plot_template:
	Built a projection Plot from corresponding UnitViews.
	"""
        if self.projection is None: raise ValueError("%s must have a projection (currently None)."%self)
        
	projection = self.projection
        plot_list=[]
        src_sheet=projection.src

        for x,y in self.generate_coords():
            plot_channels = copy.deepcopy(pt)
            # JC: we might consider allowing the construction of 'projection type' plots
            # with other things than UnitViews.
            key = (self.keyname,sheet.name,projection.name,x,y)
            plot_channels['Strength'] = key
            if self.situate:
                plot_list.append(make_template_plot(plot_channels,src_sheet.sheet_view_dict,src_sheet.xdensity,
                                                    src_sheet.bounds,self.normalize))
            else:
                (r,c) = projection.dest.sheet2matrixidx(x,y)
                plot_list.append(make_template_plot(plot_channels,src_sheet.sheet_view_dict,src_sheet.xdensity,
							projection.cf(r,c).bounds,self.normalize))
        return plot_list


    def generate_coords(self):
        """
        Evenly space out the units within the sheet bounding box, so
        that it doesn't matter which corner the measurements start
        from.  A 4 unit grid needs 5 segments.  List is in left-to-right,
        from top-to-bottom.
        """
        def rev(x): y = x; y.reverse(); return y
        ### JCALERT! Here, we assume that for a ProjectionPlotGroup,
	### sheet_name is not None.

        # why was this here?
	#for s in topo.sim.objects(Sheet).values():
	#    if (s.name==self.sheet_name and isinstance(s,CFSheet)):
	#	self._sim_ep = s
        (l,b,r,t) = self.sheet.bounds.lbrt()
        x = float(r - l) 
        y = float(t - b)
        x_step = x / (int(x * self.density) + 1)
        y_step = y / (int(y * self.density) + 1)
        l = l + x_step
        b = b + y_step
        coords = []
        self.proj_plotting_shape = (int(x * self.density), int(y * self.density))
        for j in rev(range(self.proj_plotting_shape[1])):
            for i in range(self.proj_plotting_shape[0]):
                coords.append((x_step*i + l, y_step*j + b))

        return coords


    ## CEBALERT: very similar to XPlotGroup's (marked by "diff"s)
    def scale_images(self):
        if self.initial_plot:
            self._calculate_minimum_height_of_tallest_plot()
            
	    ### JCALERT: here we should take the plot bounds instead of the sheet one (id in set_height_of..)?

        resizeable_plots = [p for p in self.plots if p.resize]
        if resizeable_plots:
            max_sheet_height = max([(topo.sim.objects(Sheet)[p.plot_src_name].bounds.lbrt()[3]
                                     -topo.sim.objects(Sheet)[p.plot_src_name].bounds.lbrt()[1])
                                    for p in resizeable_plots])
            matrix_max_height = max([p.bitmap.height() for p in resizeable_plots]) # diff 1 (addition)

	for plot in self.plots:
            if not plot.resize:
                scaling_factor = 1
            else:
		if self.sheet_coords:		   
                    s = topo.sim.objects(Sheet).get(plot.plot_src_name,None)
		    scaling_factor=self.sizeconvertfn(self.height_of_tallest_plot/float(s.xdensity)/max_sheet_height)
		else:
		    scaling_factor=self.sizeconvertfn(self.height_of_tallest_plot/float(matrix_max_height))
                    # diff 2 (missing enforced min scaling_factor)

	    plot.bitmap.image = plot.bitmap.zoom(scaling_factor) # diff 3 [plot.rescale(scaling_factor)]


    def _ordering_plots(self):
	"""Skips plot sorting for Projections to keep the units in order."""
	pass




class FeatureCurvePlotGroup(PlotGroup):


    sheet = RangedParameter() 

    template = Parameter() # doesn't this make it a templateplotgroup?

    x = Number(default=0.0,doc="something")
    y = Number(default=0.0,doc="somethingelse")


    

    def __init__(self,**params):
        super(FeatureCurvePlotGroup,self).__init__(**params)

        ##### CEBHACKALERT: set params from template #####
        assert self.template is not None
        for n in self.template.params().keys():
            if hasattr(self,n):
                setattr(self,n,getattr(self.template,n))
        ##################################################


    def CEBALERT(self):
        topo.commands.analysis.coordinate = (self.x,self.y)
        topo.commands.analysis.sheet_name = self.sheet.name

    def _update_command(self):
        self.CEBALERT()
        super(FeatureCurvePlotGroup,self)._update_command()          
        self.get_curve_time()

    def _plot_command(self):
        self.CEBALERT()
        super(FeatureCurvePlotGroup,self)._plot_command()
        self.get_curve_time()


    def get_curve_time(self):
        """
        Get timestamps from the current SheetViews in the curve_dict and
        use the max timestamp as the plot label
        Displays a warning if not all curves have been measured at the same time.
        """
        for x_axis in self.sheet.curve_dict.itervalues():
            for curve_label in x_axis.itervalues():
                timestamps = [SheetView.timestamp for SheetView in curve_label.itervalues()]

        if timestamps != []:
            self.time = max(timestamps)
            if max(timestamps) != min(timestamps):
                self.warning("Displaying curves from different times (%s,%s)" %
                             (min(timestamps),max(timestamps)))

