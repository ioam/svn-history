"""
Hierarchy of PlotGroup classes, i.e. output-device-independent sets of plots.

Includes PlotGroups for standard plots of anything in a Sheet database,
plus weight plots for one unit, and projections.

$Id$
"""
__version__='$Revision$'

import copy
import Image
import numpy

import __main__

import topo

from topo.base.parameterizedobject import ParameterizedObject
from topo.base.parameterclasses import Parameter,BooleanParameter, \
     StringParameter,Number,ObjectSelectorParameter, Filename, ListParameter
from topo.base.sheet import Sheet
from topo.base.cf import CFSheet,CFProjection
from topo.base.projection import ProjectionSheet

from topo.misc.keyedlist import KeyedList

from plot import make_template_plot, Plot


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



# general CEBALERTs for this file:
#
# Before 0.9.4:
# * Clean up keyname stuff 
# * Update documentation
#
# After 0.9.4
# * Clean up hierarchy (i.e. making methods as general as possible,
#   and there are also missing classes - currently only CFProjections
#   for CFSheets can be plotted).
# * There are no unit tests
# * Commands in analysis.py should be re-written to avoid having to
#   set global parameters


class PlotGroup(ParameterizedObject):
    """
    Container that has one or more Plots and also knows how to arrange
    the plots and other special parameters.
    """

    cmd_location = Parameter(default=__main__.__dict__,doc="""
    Namespace in which to execute the update_command and plot_command.""")

    update_command = StringParameter(default="",doc="""
    Command to execute before updating this plot, e.g. to calculate sheet views.
    
    The command can be any Python code, and will be evaluated in the main namespace
    (as if it were typed into a .ty script).  The initial value is determined by
    the template for this plot, but various arguments can be passed, a modified
    version substituted, etc.""")

    plot_command = StringParameter(default="",doc="""
    Command to execute when updating sheet or coordinate of unit to be plotted
    when the simulator time has not changed (i.e. no further measurement of
    responses is required).
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

        self.plot_list = []
	self.labels = [] # List of plot labels

        # In the future, it might be good to be able to specify the
        # plot rows and columns using tuples.  For instance, if three
        # columns are desired with the plots laid out from left to
        # right, we could use (None, 3).  If three rows are desired
        # then (3, None).  Another method that would work is [3,2,4]
        # would have the first row with 3, the second row with 2, the
        # third row with 4, etc.  The default left-to-right ordering
        # in one row could perhaps be represented as (None, Inf).
        
	self.time = None



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


    def make_plots(self,update=True):
	"""

	If update=True, execute the command associated with the template
	(e.g. generating the Sheetviews necessary to create the PlotGroup's Plots).
	"""
        if update: self._update_command()
        self._plot_command()
        self._create_images(update)
        self.scale_images()


    def redraw_plots(self):
        self.make_plots(update=False)


    def _create_images(self,update):
        """
        Generate the sorted and scaled list of plots constituting the PlotGroup.
        """

        self.plots = [plot for plot in self._plot_list() if plot != None]

        # Suppress plots in the special case of plots not being updated 
        # and having no resizable images, to suppress plotgroups that
        # have nothing but a color key
        resizeable_plots = [p for p in self.plots if p.resize]
        if not update and not resizeable_plots:
            self.plots=[]

        # Take the timestamps from the underlying Plots
	timestamps = [plot.timestamp for plot in self._plot_list()
                      if plot != None and plot.timestamp >= 0]
        if timestamps != []:
            self.time = max(timestamps)
            if max(timestamps) != min(timestamps):
                self.warning("Combining Plots from different times (%s,%s)" %
                             (min(timestamps),max(timestamps)))

	self._sort_plots()	
	self.generate_labels()

    def scale_images(self,zoom_factor=None):
        """Scale the images by the given zoom factor, if appropriate; default is to do nothing."""
        pass
    
    def generate_labels(self):
	""" Function used for generating the labels."""
	self.labels = []
	for plot in self.plots:
	    self.labels.append(plot.plot_src_name + '\n' + plot.name)


    def _sort_plots(self):
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


class SheetPlotGroup(PlotGroup):


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

    auto_refresh = BooleanParameter(default=False,doc="""
        If this plot is being displayed regularly (e.g. in a GUI),
        whether to regenerate it automatically whenever the simulation
        time advances.  The default is False, because many plots are
        slow to generate (e.g. most preference map plots).""")


    # CEBALERT: if keeping this, need to add to other contructors.
    def __init__(self,sheets=None,**params):
        self.sheets = sheets
        super(SheetPlotGroup,self).__init__(**params)
        self.height_of_tallest_plot = 150.0 # Initial value

    def _sheets(self):
        return self.sheets or topo.sim.objects(Sheet).values()

    ### CEB: At least some of this scaling would be common to all
    ### plotgroups, if some (e.g. featurecurve) didn't open new
    ### windows.
    ###
    ### JAB: Isn't there some way to have the GUI take care of the
    ### actual scaling, without us having to change the bitmaps
    ### ourselves?
    ###
    ### Could strip out the matrix-coord scaling and put it into
    ### PlotGroup
    def scale_images(self,zoom_factor=None):
        """
        Enlarge or reduce the bitmaps as needed for display.

        The calculated sizes will be multiplied by the given
        zoom_factor, if it is not None.

        A minimum size (and potentially a maximum size) are enforced,
        as described below.

        If the scaled sizes would be outside of the allowed range, no
        scaling is done, and False is returned.  (One might
        conceivably instead want the scaling to reach the actual
        minimum or maximum allowed, but if we did this, then repeated
        enlargements and reductions would not be reversible, unless we
        were very tricky about how we did it.)

        For matrix coordinate plots (sheet_coords=False), the minimum
        size is calculated as the native size of the largest bitmap to
        be plotted.  Other plots are then usually scaled up to (but
        not greater than) this size, so that all plots are
        approximately the same size, and no plot is missing any pixel.

        For Sheet coordinate plots, the minimum plotting density that
        will avoid losing pixels is determined by the maximum density
        from any sheet.  If all plots are then drawn at that density
        (as they must be for them to be in Sheet coordinates), the
        largest plot will then be the one with the largest sheet
        bounds, and the size of that plot will be the maximum density
        times the largest sheet bounds.
        """
        
        resizeable_plots = [p for p in self.plots if p.resize]
        if not resizeable_plots:
            return False

        # Determine which plot will be the largest, to ensure that
        # no plot is missing any pixels.
        if not self.sheet_coords:
            bitmap_heights = [p._orig_bitmap.height() for p in resizeable_plots]
            minimum_height_of_tallest_plot = max(bitmap_heights)
            
        else:           
            ### JABALERT: Should take the plot bounds instead of the sheet bounds
            ### Specifically, a weights plot with situate=False
            ### doesn't use the Sheet bounds, and so the
            ### minimum_height is significantly overstated.
            sheets = topo.sim.objects(Sheet)
            max_sheet_height = max([(sheets[p.plot_src_name].bounds.lbrt()[3]-
                                     sheets[p.plot_src_name].bounds.lbrt()[1])
                                   for p in resizeable_plots])
            max_sheet_density = max([sheets[p.plot_src_name].xdensity
                                     for p in resizeable_plots])
            minimum_height_of_tallest_plot = max_sheet_height*max_sheet_density
            
        if (self.height_of_tallest_plot < minimum_height_of_tallest_plot):
            self.height_of_tallest_plot = minimum_height_of_tallest_plot
            
        # Apply optional scaling to the overall size
        if zoom_factor:
            new_height = self.height_of_tallest_plot * zoom_factor
            # Currently enforces only a minimum, but could enforce maximum height
            if new_height >= minimum_height_of_tallest_plot:
                self.height_of_tallest_plot = new_height
            else:
                return False

        # Scale the images so that each has a size up to the height_of_tallest_plot
	for plot in resizeable_plots:
	    if self.sheet_coords:
                s = topo.sim.objects(Sheet)[p.plot_src_name]
	        scaling_factor=self.height_of_tallest_plot/float(s.xdensity)/max_sheet_height
	    else:
	        scaling_factor=self.height_of_tallest_plot/float(plot._orig_bitmap.height())
            
            if self.integer_scaling:
                scaling_factor=max(1,int(scaling_factor))
                
            plot.set_scale(scaling_factor)
            
            #print "Scaled %s %s: %d->%d (x %f)" % (plot.plot_src_name, plot.name, plot._orig_bitmap.height(), plot.bitmap.height(), scaling_factor)

        return True



class TemplatePlotGroup(SheetPlotGroup):
    """
    Container that allows creation of different types of plots in a
    way that is independent of particular models or Sheets.

    A TemplatePlotGroup is constructed from a plot_templates list, an
    optional command to run to generate the data, and other optional
    parameters.
    
    The plot_templates list should contain tuples (plot_name,
    plot_template).  Each plot_template is a list of (name, value)
    pairs, where each name specifies a plotting channel (such as Hue
    or Confidence), and the value is the name of a SheetView (such as
    Activity or OrientationPreference).
        
    Various types of plots support different channels.  An SHC
    plot supports Strength, Hue, and Confidence channels (with
    Strength usually being visualized as luminance, Hue as a color
    value, and Confidence as the saturation of the color).  An RGB
    plot supports Red, Green, and Blue channels.  Other plot types
    will be added eventually.

    For instance, one could define an Orientation-colored Activity
    plot as::
        
      plotgroups['Activity'] =
          TemplatePlotGroup(name='Activity', category='Basic',
              update_command='measure_activity()',
              plot_templates=[('Activity',
                  {'Strength': 'Activity', 'Hue': 'OrientationPreference', 'Confidence': None})])
    
    This specifies that the final TemplatePlotGroup will contain up to
    one Plot named Activity per Sheet, although there could be no
    plots at all if no Sheet has a SheetView named Activity once
    'measure_activity()' has been run.  The Plot will be colored by
    OrientationPreference if such a SheetView exists for that Sheet,
    and the value (luminance) channel will be determined by the
    SheetView Activity.  This plot will be listed in the category
    'Basic' anywhere such categories are relevant (e.g. in the GUI).

    
    Here's a more complicated example specifying two different plots
    in the same PlotGroup::

      TemplatePlotGroup(name='Orientation Preference', category='Basic'
          update_command='measure_or_pref()',
          plot_templates=
              [('Orientation Preference',
                  {'Strength': None, 'Hue': 'OrientationPreference'}),
               ('Orientation Selectivity',
                  {'Strength': 'OrientationSelectivity'})])

    Here the TemplatePlotGroup will contain up to two Plots per Sheet,
    depending on which Sheets have OrientationPreference and
    OrientationSelectivity SheetViews.


    The function new_pg provides a convenient way to define plots using
    TemplatePlotGroups; search for new_pg elsewhere in the code to see
    examples. 
    """

    doc = StringParameter(default="",
      doc="Documentation string describing this type of plot.")

    plot_immediately=BooleanParameter(False,doc="""
      Whether to call the plot command at once or only when the user asks for a refresh.

      Should be set to true for quick plots, but false for those that take a long time
      to calculate, so that the user can change the update command if necessary.""")
    
    prerequisites=ListParameter([],
      doc="List of preference maps which must exist before this plot can be calculated.")

    category = StringParameter(default="User",
      doc="Category to which this plot belongs, which will be created if necessary.")

    # JCALERT! We might eventually write these two functions
    # 'Python-like' by using keyword argument to specify each
    # channel and then get the dictionnary of all remaining
    # arguments.
    # 
    # JABALERT: We should also be able to store a documentation string
    # describing each plot (for hovering help text) within each
    # plot template.
    #
    # JAB: Maybe add_template would be a better name, to contrast with add_static_image
    def add_plot(self,name,specification_tuple_list):
	dict_={}
	for key,value in specification_tuple_list:
	    dict_[key]=value
	self.plot_templates.append((name,dict_))


    def add_static_image(self,name,file_path):
        """
        Construct a static image Plot (e.g. a color key for an Orientation Preference map).
        """
        image = Image.open(file_path)
        plot = Plot(image,name=name)
        self.plot_list.append(plot)


    def __init__(self,plot_templates=[],static_images=[],**params):
	super(TemplatePlotGroup,self).__init__(**params)

	self.plot_templates = KeyedList(plot_templates)
                
	# Add plots for the static images, if any
        for image_name,file_path in static_images:
            add_static_image(image_name,file_path)

	
    def _plot_list(self):
        """
        Procedure that is called when creating a PlotGroup.

        Returns the plot_list attribute, i.e., the list of plots that
        are specified by the PlotGroup template.

        This function calls create_plots, which is implemented in each
        TemplatePlotGroup subclass.
        """   
	plot_list = self.plot_list
        for each in self._sheets():
	    for (pt_name,pt) in self.plot_templates:
		plot_list = plot_list + self._create_plots(pt_name,pt,each)
    	return plot_list


    def _create_plots(self,pt_name,pt,sheet):
	""" 
	Sub-function of _plot_list().
	Creates a plot corresponding to a plot_template, its name, and a sheet.
	"""
        return [make_template_plot(pt,sheet.sheet_view_dict,sheet.xdensity,
                                   sheet.bounds,self.normalize,name=pt_name)]



class ProjectionSheetPlotGroup(TemplatePlotGroup):
    """
    Abstract PlotGroup for visualizations of the Projections of one ProjectionSheet.

    Requires self.keyname to be set to the name of a placeholder
    SheetView that will be replaced with a key that is unique to a
    particular Projection of the current Sheet.
    """
    _abstract_class_name = "ProjectionSheetPlotGroup"

    keyname = "ProjectionSheet" 

    sheet = ObjectSelectorParameter(default=None,doc="""
    The Sheet from which to produce plots.""")

    sheet_type = ProjectionSheet


    def _check_sheet_type(self):
        if not isinstance(self.sheet,self.sheet_type):
            raise TypeError(
                "%s's sheet Parameter must be set to a %s instance (currently %s, type %s)." \
                %(self,self.sheet_type,self.sheet,type(self.sheet))) 

    def _sheets(self):
        return [self.sheet]

    def _update_command(self):
        self._check_sheet_type()
	topo.commands.analysis.sheet_name = self.sheet.name
        super(ProjectionSheetPlotGroup,self)._update_command()
        



    # Special case: if the Strength is set to self.keyname, we
    # request UnitViews (i.e. by changing the Strength key in
    # the plot_channels). Otherwise, we consider Strength as
    # specifying an arbitrary SheetView.

    # CB/JAB: Should replace this custom routine with simply providing
    # a method for constructing a special key name; then maybe nearly
    # all the fancy processing in the various _create_plots functions
    # can be eliminated

    # (this method isn't the solution to the above, it's just beginning
    # to remove some duplication)
    def _change_key(self,plotgroup_template,sheet,proj):
        plot_channels = copy.deepcopy(plotgroup_template)
        key = (self.keyname,sheet.name,proj.name)
        plot_channels['Strength']=key
        return plot_channels

    def _create_plots(self,pt_name,pt,sheet):
	"""Creates plots as specified by the plot_template."""
        # Note: the UnitView is in the src_sheet view_dict,
        # and the name in the key is the destination sheet.
        return [make_template_plot(self._change_key(pt,sheet,proj),
                                   proj.src.sheet_view_dict,
                                   proj.src.xdensity,
                                   None,
                                   self.normalize,
                                   name=proj.name) for proj in sheet.in_connections]

 
    def generate_labels(self):
	""" Function used for generating the labels."""
	self.labels = []
	for plot in self.plots:
	    self.labels.append(plot.name + '\n(from ' + plot.plot_src_name+')')



class ProjectionActivityPlotGroup(ProjectionSheetPlotGroup):
    """Visualize the activity of all Projections into a ProjectionSheet."""

    keyname='ProjectionActivity' 


    def _create_plots(self,pt_name,pt,sheet):
        return [make_template_plot(self._change_key(pt,sheet,proj),
                                   proj.dest.sheet_view_dict,
                                   proj.dest.xdensity,
                                   proj.dest.bounds,
                                   self.normalize,
                                   name=proj.name) for proj in sheet.in_connections]



class ProjectionPlotGroup(ProjectionSheetPlotGroup):
    projection = ObjectSelectorParameter(default=None,doc="The projection to visualize.")
    
    

class CFProjectionPlotGroup(ProjectionPlotGroup):
    """Visualize one CFProjection."""

    keyname='Weights'

    situate = BooleanParameter(default=False,doc="""
    If True, plots the weights on the entire source sheet, using zeros
    for all weights outside the ConnectionField.  If False, plots only
    the actual weights that are stored.""")


    ### JPALERT: The bounds are meaningless for large sheets anyway.  If a sheet
    ### is specified in, say, visual angle coordinates (e.g., -60 to +60 degrees), then
    ### the soft min of 5.0/unit will still give a 600x600 array of CFs!
    ### Density should probably be specified WRT to sheet bounds,
    ### instead of per-unit-of-sheet.    
    density = Number(default=10.0,
                     softbounds=(5.0,50.0),doc="""
                     Number of units to plot per 1.0 distance in sheet coordinates""")
                     
    sheet_type = CFSheet
    projection_type = CFProjection

    def __init__(self,**params):
        super(CFProjectionPlotGroup,self).__init__(**params)
        self.height_of_tallest_plot = 5 # Initial value
        
        ### JCALERT! shape determined by the plotting density
        ### This is set by self.generate_coords()
        self.proj_plotting_shape = (0,0)
    

    def _check_projection_type(self):
        if not isinstance(self.projection,self.projection_type):
            raise TypeError(
                "%s's projection Parameter must be set to a %s instance (currently %s, type %s)." \
                %(self,self.projection_type,self.projection,type(self.projection))) 


    def _update_command(self):
        self._check_projection_type()
	### JCALERT: commands in analysis have to be re-written so that to avoid
	### setting all these global parameters.
        topo.commands.analysis.proj_coords = self.generate_coords()
        topo.commands.analysis.proj_name = self.projection.name
        super(CFProjectionPlotGroup,self)._update_command()


    def _change_key(self,plotgroup_template,sheet,proj,x,y):
        plot_channels = copy.deepcopy(plotgroup_template)
        key = (self.keyname,sheet.name,proj.name,x,y)
        plot_channels['Strength']=key
        return plot_channels

		
    def _create_plots(self,pt_name,pt,sheet):
	""" 
	Sub-function of _plot_list().
	Creates a plot as specified by a Projection plot_template:
	Built a projection Plot from corresponding UnitViews.
	"""
	projection = self.projection
        plot_list=[]
        src_sheet=projection.src

        for x,y in self.generate_coords():
            
            # JC: we might consider allowing the construction of 'projection type' plots
            # with other things than UnitViews.
            plot_channels = self._change_key(pt,sheet,projection,x,y)
            
            if self.situate:
                bounds = src_sheet.bounds
            else:
                (r,c) = projection.dest.sheet2matrixidx(x,y)
                bounds = projection.cf(r,c).bounds
                                                    
            plot_list.append(make_template_plot(plot_channels,
                                                src_sheet.sheet_view_dict,
                                                src_sheet.xdensity,
                                                bounds,
                                                self.normalize))
        return plot_list


    def generate_coords(self):
        """
        Evenly space out the units within the sheet bounding box, so
        that it doesn't matter which corner the measurements start
        from.  A 4 unit grid needs 5 segments.  List is in left-to-right,
        from top-to-bottom.
        """
        def rev(x): y = x; y.reverse(); return y

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


    def _sort_plots(self):
	"""Skips plot sorting for Projections to keep the units in order."""
	pass



class UnitPlotGroup(ProjectionSheetPlotGroup):
    """
    Visualize anything related to a unit.
    """

    # JABALERT: need to show actual coordinates of unit returned
    x = Number(default=0.0,doc="""x-coordinate of the unit to plot""")
    y = Number(default=0.0,doc="""y-coordinate of the unit to plot""")
## """Sheet coordinate location desired.  The unit nearest this location will be returned.
## It is an error to request a unit outside the area of the Sheet.""")

        
    def _update_command(self):
	topo.commands.analysis.coordinate = (self.x,self.y)
	super(UnitPlotGroup,self)._update_command()



class ConnectionFieldsPlotGroup(UnitPlotGroup):
    """
    Visualize ConnectionField for each of a CFSheet's CFProjections.
    """
    keyname='Weights'

    sheet_type = CFSheet

    situate = BooleanParameter(default=False,doc="""
    If True, plots the weights on the entire source sheet, using zeros
    for all weights outside the ConnectionField.  If False, plots only
    the actual weights that are stored.""")

    def _change_key(self,plotgroup_template,sheet,proj,x,y):
        plot_channels = copy.deepcopy(plotgroup_template)
        key = (self.keyname,sheet.name,proj.name,x,y)
        plot_channels['Strength']=key
        return plot_channels


    def _create_plots(self,pt_name,pt,sheet):
	""" 
	Creates a plot as specified by a Connection Field plot_template:
	"""
        plot_list = []
        for p in sheet.in_connections:
            plot_channels = self._change_key(pt,sheet,p,self.x,self.y)
            if self.situate:
                bounds = None
            else:
                (r,c) = p.dest.sheet2matrixidx(self.x,self.y)
                bounds = p.cf(r,c).bounds
            plot_list.append(make_template_plot(plot_channels,
                                                p.src.sheet_view_dict,
                                                p.src.xdensity,
                                                bounds,
                                                self.normalize,
                                                name=p.name))
        return plot_list


class FeatureCurvePlotGroup(UnitPlotGroup):

    def _update_command(self):
        super(FeatureCurvePlotGroup,self)._update_command()          
        self.get_curve_time()

    def _plot_command(self):
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




plotgroups = KeyedList()
"""
Global repository of PlotGroups, to which users can add
their own as needed.
"""


plotgroup_types = {'Connection Fields': ConnectionFieldsPlotGroup,
                   # CB: and here's where to start with being able to plot any type
                   # of projection
                   'Projection': CFProjectionPlotGroup,
                   'Projection Activity': ProjectionActivityPlotGroup}


def new_pg(template_plot_type='bitmap',**params):
    """
    Create a new PlotGroup and add it to the plotgroups list.

    Convenience function to make it simpler to use the name of the
    PlotGroup as the key in the plotgroups list.

    template_plot_type: Whether the plots are bitmap images or curves ('curve')

    """
    name = params.get('name')

    pg_type = TemplatePlotGroup
    if name:
        if name in plotgroup_types:
            pg_type = plotgroup_types[name]
        elif template_plot_type=='curve':
            pg_type = FeatureCurvePlotGroup
                
    pg = pg_type(**params)
    plotgroups[pg.name]=pg
    return pg
