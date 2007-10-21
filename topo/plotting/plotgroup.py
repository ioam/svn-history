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
from topo.base.parameterclasses import Parameter,BooleanParameter, \
     StringParameter,Number,ObjectSelectorParameter, ListParameter, Integer
from topo.base.sheet import Sheet
from topo.base.cf import CFSheet,CFProjection,Projection
from topo.base.projection import ProjectionSheet

from topo.misc.keyedlist import KeyedList
from topo.misc.filepaths import resolve_path

from plot import make_template_plot, Plot
from plotfilesaver import PlotGroupSaver,CFProjectionPlotGroupSaver


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
# * Clean up what's here: names and doc
# * Clean up keyname stuff 
#
# After 0.9.4
# * Improve hierarchy (i.e. making methods as general as possible,
#   and there are also missing classes - currently only CFProjections
#   for CFSheets can be plotted).
# * There are no unit tests


class PlotGroup(ParameterizedObject):
    """
    Container that has one or more Plots and also knows how to arrange
    the plots and other special parameters.
    """
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

    # CB: make clear the distinction between self.plots and self.plot_list
    
    def __init__(self,**params):

        super(PlotGroup,self).__init__(**params)

        self.plot_list = []
	self.labels = [] 

        # In the future, it might be good to be able to specify the
        # plot rows and columns using tuples.  For instance, if three
        # columns are desired with the plots laid out from left to
        # right, we could use (None, 3).  If three rows are desired
        # then (3, None).  Another method that would work is [3,2,4]
        # would have the first row with 3, the second row with 2, the
        # third row with 4, etc.  The default left-to-right ordering
        # in one row could perhaps be represented as (None, Inf).
        
	self.time = None

        self.filesaver = PlotGroupSaver(self)
    

    # CB: (subclasses add more commands)
    def _exec_update_command(self):
        exec self.update_command in __main__.__dict__

    def _exec_plot_command(self):
        exec self.plot_command in __main__.__dict__

        
    def _plot_list(self):
	"""
        Return the list of plots.

	Re-implemented by TemplatePlotGroup to construct a list of plots as specified by the template.
	"""
	return self.plot_list


    def make_plots(self,update=True):
	"""
        Create and scale the plots, after first executing the PlotGroup's update_command
        (if update is True) and plot_command.
	"""
        if update:self._exec_update_command()
        self._exec_plot_command()
        self._create_images(update)
        self.scale_images()


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
	"""Generate labels for the plots."""
	self.labels = []
	for plot in self.plots:
	    self.labels.append(plot.label())


    def _sort_plots(self):
	"""
        Sort plots according to their precedence, then alphabetically.
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
        If this plot is being displayed persistently (e.g. in a GUI),
        whether to regenerate it automatically whenever the simulation
        time advances.  The default is False, because many plots are
        slow to generate (including most preference map plots).""")

    desired_maximum_plot_height = Integer(default=0,bounds=(0,None),doc="""
        User-specified height of the tallest plot in this PlotGroup.
        Other plots will generally be scaled as appropriate, either
        to match this size (when sheet_coords is False), or to
        have the appropriate relative size (when sheet_coords is True).

        If enforce_minimum_plot_height is True, the actual maximum
        plot height may be larger than this parameter's value.  In
        particular, with enforce_minimum_plot_height=True, the default
        value of 0 gives plots that are the size of the underlying
        matrix, which is the most efficient size for saving plots
        directly to disk.  Larger values (e.g. 150) are suitable when
        displaying plots on screen.""")
        
    enforce_minimum_plot_height = BooleanParameter(default=True,doc="""
        If true, ensure that plots are never shown smaller than their
        native size, i.e. with fewer than one pixel per matrix unit.
        This option is normally left on for safety, so that no
        visualization will be missing any units.  However, it may be
        acceptable to turn this check off when working with matrix
        sizes much larger than your screen resolution.""")


    # CEBALERT: SheetPlotGroup works on a list of sheets, and so does
    # TemplatePlotGroup.  (TestPattern uses this to set its own list
    # of sheets.) The classes after TemplatePlotGroup
    # (ProjectionSheetPlotGroup onwards) work on a *single*
    # sheet. Having a sheets attribute is confusing. How do we get
    # round this?
    def __init__(self,sheets=None,**params):
        self.sheets = sheets
        super(SheetPlotGroup,self).__init__(**params)

    def _sheets(self):
        return self.sheets or topo.sim.objects(Sheet).values()

    def make_plots(self,update=True):
        self.height_of_tallest_plot = self.desired_maximum_plot_height
        super(SheetPlotGroup,self).make_plots(update)


    ### CEB: At least some of this scaling would be common to all
    ### plotgroups, if some (e.g. featurecurve) didn't open new
    ### windows.
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
        new_height=self.height_of_tallest_plot

        # No scaling to do if there are no scalable plots, or no desired size
        resizeable_plots = [p for p in self.plots if p.resize]
        if not resizeable_plots or not new_height:
            return False

        ### CEBALERT 'scaling hack': stop plots changing size in GUI ###
        if zoom_factor:
            self._zoom_factor=zoom_factor
        ################################################################


        # Apply optional scaling to the overall size
        if zoom_factor:
            new_height *= zoom_factor
        ### CEBALERT 'scaling hack' ####################################
        elif hasattr(self,'_zoom_factor') and self._zoom_factor:
            new_height *= self._zoom_factor
        ################################################################
            

        # Determine which plot will be the largest, to ensure that
        # no plot is missing any pixels.
        if (self.enforce_minimum_plot_height):
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

            if (new_height < minimum_height_of_tallest_plot):
                new_height = minimum_height_of_tallest_plot
                if zoom_factor:
                    return False
            
        # Scale the images so that each has a size up to the height_of_tallest_plot
	for plot in resizeable_plots:
	    if self.sheet_coords:
                s = topo.sim.objects(Sheet)[plot.plot_src_name]
	        scaling_factor=new_height/float(s.xdensity)/max_sheet_height
	    else:
	        scaling_factor=new_height/float(plot._orig_bitmap.height())
            
            if self.integer_scaling:
                scaling_factor=max(1,int(scaling_factor))
                
            plot.set_scale(scaling_factor)
            
            #print "Scaled %s %s: %d->%d (x %f)" % (plot.plot_src_name, plot.name, plot._orig_bitmap.height(), plot.bitmap.height(), scaling_factor)

        self.height_of_tallest_plot = new_height
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


    The function create_plotgroup provides a convenient way to define plots using
    TemplatePlotGroups; search for create_plotgroup elsewhere in the code to see
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
        image = Image.open(resolve_path(file_path))
        plot = Plot(image,name=name)
        self.plot_list.append(plot)


    def __init__(self,plot_templates=[],static_images=[],**params):
	super(TemplatePlotGroup,self).__init__(**params)

	self.plot_templates = KeyedList(plot_templates)
                
	# Add plots for the static images, if any
        for image_name,file_path in static_images:
            add_static_image(image_name,file_path)

	
    def _plot_list(self):
	plot_list = self.plot_list
        for sheet in self._sheets():
	    for (pt_name,pt) in self.plot_templates:
		plot_list = plot_list + self._create_plots(pt_name,pt,sheet)
    	return plot_list


    def _create_plots(self,pt_name,pt,sheet):
        return [make_template_plot(pt,sheet.sheet_views,sheet.xdensity,
                                   sheet.bounds,self.normalize,name=pt_name)]



class ProjectionSheetPlotGroup(TemplatePlotGroup):
    """
    Abstract PlotGroup for visualizations of the Projections of one ProjectionSheet.

    Requires self.keyname to be set to the name of a placeholder
    SheetView that will be replaced with a key that is unique to a
    particular Projection of the current Sheet.
    """
    _abstract_class_name = "ProjectionSheetPlotGroup"

    keyname = "ProjectionSheet" # CB: what is this keyname?

    sheet = ObjectSelectorParameter(default=None,doc="""
    The Sheet from which to produce plots.""")

    sheet_type = ProjectionSheet

    # CB: this isn't really necessary for these classes
    # themselves. Right now we have it provide a useful error message
    # to users (which is useful).
    def _check_sheet_type(self):
        if not isinstance(self.sheet,self.sheet_type):
            raise TypeError(
                "%s's sheet Parameter must be set to a %s instance (currently %s, type %s)." \
                %(self,self.sheet_type,self.sheet,type(self.sheet))) 

    def _sheets(self):
        return [self.sheet]

    def _exec_update_command(self):
        self._check_sheet_type()
	topo.commands.analysis.sheet_name = self.sheet.name
        super(ProjectionSheetPlotGroup,self)._exec_update_command()
        



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
        # Note: the UnitView is in the src_sheet view_dict,
        # and the name in the key is the destination sheet.
        return [make_template_plot(self._change_key(pt,sheet,proj),
                                   proj.src.sheet_views,
                                   proj.src.xdensity,
                                   None,
                                   self.normalize,
                                   name=proj.name) for proj in sheet.in_connections]

 
    def generate_labels(self):
	self.labels = []
	for plot in self.plots:
	    self.labels.append(plot.name + '\n(from ' + plot.plot_src_name+')')



class ProjectionActivityPlotGroup(ProjectionSheetPlotGroup):
    """Visualize the activity of all Projections into a ProjectionSheet."""

    keyname='ProjectionActivity' 

    def _create_plots(self,pt_name,pt,sheet):
        return [make_template_plot(self._change_key(pt,sheet,proj),
                                   proj.dest.sheet_views,
                                   proj.dest.xdensity,
                                   proj.dest.bounds,
                                   self.normalize,
                                   name=proj.name) for proj in sheet.in_connections]



class TwoDThingPlotGroup(ProjectionSheetPlotGroup):
    """
    A ProjectionSheetPlotGroup capable of generating coordinates on a 2D grid.
    """
    ### JPALERT: The bounds are meaningless for large sheets anyway.  If a sheet
    ### is specified in, say, visual angle coordinates (e.g., -60 to +60 degrees), then
    ### the soft min of 5.0/unit will still give a 600x600 array of CFs!
    ### Density should probably be specified WRT to sheet bounds,
    ### instead of per-unit-of-sheet.    
    density = Number(default=10.0,
                     softbounds=(5.0,50.0),doc="""
                     Number of units to plot per 1.0 distance in sheet coordinates""")


    def __init__(self,**params):
        super(TwoDThingPlotGroup,self).__init__(**params)

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


    def _change_key(self,plotgroup_template,sheet,x,y):
        plot_channels = copy.deepcopy(plotgroup_template)
        key = (self.keyname,sheet.name,x,y)
        plot_channels['Strength']=key
        return plot_channels


    def _create_plots(self,pt_name,pt,sheet):
        plot_list=[]
        for x,y in self.generate_coords():
            x_center,y_center = sheet.closest_cell_center(x,y)
            plot_channels = self._change_key(pt,sheet,x_center,y_center)
            plot_list.append(make_template_plot(plot_channels,
                                                self.input_sheet.sheet_views,
                                                self.input_sheet.xdensity,
                                                self.input_sheet.bounds,
                                                self.normalize))
        return plot_list


    def _sort_plots(self):
	"""Skips plot sorting for to keep the generated order."""
	pass



class RFProjectionPlotGroup(TwoDThingPlotGroup):

    keyname='RFs'
    input_sheet = ObjectSelectorParameter(default=None,doc="The sheet on which to measure the RFs.")

    def _exec_update_command(self): # RFHACK
	topo.commands.analysis.input_sheet_name = self.input_sheet.name
        super(RFProjectionPlotGroup,self)._exec_update_command()



class ProjectionPlotGroup(TwoDThingPlotGroup):

    projection = ObjectSelectorParameter(default=None,doc="The projection to visualize.")
    keyname='Weights'                     

    def _change_key(self,plotgroup_template,sheet,proj,x,y):
        plot_channels = copy.deepcopy(plotgroup_template)
        key = (self.keyname,sheet.name,proj.name,x,y)
        plot_channels['Strength']=key
        return plot_channels

    def _exec_update_command(self):
        topo.commands.analysis.proj_coords = self.generate_coords()
        topo.commands.analysis.proj_name = self.projection.name
        super(ProjectionPlotGroup,self)._exec_update_command()



class CFProjectionPlotGroup(ProjectionPlotGroup):
    """Visualize one CFProjection."""

    situate = BooleanParameter(default=False,doc="""
    If True, plots the weights on the entire source sheet, using zeros
    for all weights outside the ConnectionField.  If False, plots only
    the actual weights that are stored.""")
                     
    sheet_type = CFSheet

    def __init__(self,**params):
        super(CFProjectionPlotGroup,self).__init__(**params)    
        self.filesaver = CFProjectionPlotGroupSaver(self)

    def _exec_update_command(self): 
        self._check_projection_type()
        super(CFProjectionPlotGroup,self)._exec_update_command()

    # CB: same comment for ProjectionSheetPlotGroup's _check_sheet_type.
    def _check_projection_type(self):
        if not isinstance(self.projection,CFProjection):
            raise TypeError(
                "%s's projection Parameter must be set to a %s instance (currently %s, type %s)." \
                %(self,self.projection_type,self.projection,type(self.projection))) 

		
    def _create_plots(self,pt_name,pt,sheet):
	projection = self.projection
        plot_list=[]
        src_sheet=projection.src

        for x,y in self.generate_coords():
            
            plot_channels = self._change_key(pt,sheet,projection,x,y)
            
            if self.situate:
                bounds = src_sheet.bounds
            else:
                (r,c) = projection.dest.sheet2matrixidx(x,y)
                bounds = projection.cf(r,c).bounds
                                                    
            plot_list.append(make_template_plot(plot_channels,
                                                src_sheet.sheet_views,
                                                src_sheet.xdensity,
                                                bounds,
                                                self.normalize))
        return plot_list




class UnitPlotGroup(ProjectionSheetPlotGroup):
    """
    Visualize anything related to a unit.
    """

    # JABALERT: need to show actual coordinates of unit returned
    x = Number(default=0.0,doc="""x-coordinate of the unit to plot""")
    y = Number(default=0.0,doc="""y-coordinate of the unit to plot""")
## """Sheet coordinate location desired.  The unit nearest this location will be returned.
## It is an error to request a unit outside the area of the Sheet.""")

    def _change_key(self,plotgroup_template,sheet,x,y):
        plot_channels = copy.deepcopy(plotgroup_template)
        key = (self.keyname,sheet.name,x,y)
        plot_channels['Strength']=key
        return plot_channels

        
    def _exec_update_command(self):
	topo.commands.analysis.coordinate = (self.x,self.y)
	super(UnitPlotGroup,self)._exec_update_command()



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
        plot_list = []
        for p in sheet.in_connections:
            plot_channels = self._change_key(pt,sheet,p,self.x,self.y)
            if self.situate:
                bounds = None
            else:
                (r,c) = p.dest.sheet2matrixidx(self.x,self.y)
                bounds = p.cf(r,c).bounds
            plot_list.append(make_template_plot(plot_channels,
                                                p.src.sheet_views,
                                                p.src.xdensity,
                                                bounds,
                                                self.normalize,
                                                name=p.name))
        return plot_list



class FeatureCurvePlotGroup(UnitPlotGroup):

    def _exec_update_command(self):
        super(FeatureCurvePlotGroup,self)._exec_update_command()          
        self.get_curve_time()

    def _exec_plot_command(self):
        super(FeatureCurvePlotGroup,self)._exec_plot_command()
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




# CEBALERT: most uses of an entry (PlotGroup) from plotgroups mean to
# take a *copy* of that entry. Should we provide access methods to do
# this?
# E.g. save_plotgroup() ought to be taking copies of plotgroups
# from here.
plotgroups = KeyedList()
"""
Global repository of PlotGroups, to which users can add their own as
needed.
"""

from topo.misc.utils import ExtraPickler
ExtraPickler().add(('topo.plotting.plotgroup','plotgroups'))

plotgroup_types = {'Connection Fields': ConnectionFieldsPlotGroup,
                   'Projection': CFProjectionPlotGroup,
                   'RF Projection':RFProjectionPlotGroup,
                   'RF Projection (noise)':RFProjectionPlotGroup,                   
                   'Projection Activity': ProjectionActivityPlotGroup}


def create_plotgroup(template_plot_type='bitmap',**params):
    """
    Create a new PlotGroup and add it to the plotgroups list.

    Convenience function to make it simpler to use the name of the
    PlotGroup as the key in the plotgroups list.

    template_plot_type: Whether the plots are bitmap images or curves
    ('curve').
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
