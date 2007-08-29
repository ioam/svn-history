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
from topo.base.parameterclasses import Parameter,BooleanParameter,StringParameter,Number,ObjectSelectorParameter
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

    cmd_location = Parameter(default=__main__.__dict__,doc="""
    Namespace in which to execute the update_command and plot_command.""")

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


    def draw_plots(self,update=True):
	"""

	If update=True, execute the command associated with the template
	(e.g. generating the Sheetviews necessary to create the PlotGroup's Plots).
	"""
        if update: self._update_command()
        self._plot_command()
        self._make_plots(update)
        self.scale_images()
        

    # CB: ** replace calls to these two methods **
    def redraw_plots(self):
        self.draw_plots(update=False)
    def update_plots(self):
        self.draw_plots(update=True)

    # CB/JAB: rename to _create_images()
    def _make_plots(self,update):
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

	self._ordering_plots()	
	self.generate_labels()

    def scale_images(self,zoom_factor=None):
        """Scale the images by the given zoom factor, if appropriate; default is to do nothing."""
        pass
    
    def generate_labels(self):
	""" Function used for generating the labels."""
	self.labels = []
	for plot in self.plots:
	    self.labels.append(plot.plot_src_name + '\n' + plot.name)


    # CB/JAB: rename to _sort_plots
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

    # CB/JAB: Remove sheet_type and sheet from this class
    sheet_type = Sheet

    sheet = ObjectSelectorParameter(default=None,doc="""
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




    def __init__(self,**params):
        super(XPlotGroup,self).__init__(**params)
        self.height_of_tallest_plot = 150.0 # Initial value



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
            sheets=topo.sim.objects(Sheet)
            ### Should take the plot bounds instead of the sheet ones, once that's supported
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
                s = topo.sim.objects(Sheet).get(plot.plot_src_name,None)
	        scaling_factor=self.height_of_tallest_plot/float(s.xdensity)/max_sheet_height
	    else:
	        scaling_factor=self.height_of_tallest_plot/float(plot._orig_bitmap.height())
            
            if self.integer_scaling:
                scaling_factor=max(1,int(scaling_factor))
                
            plot.set_scale(scaling_factor)
            
            #print "Scaled %s %s: %d->%d (x %f)" % (plot.plot_src_name, plot.name, plot._orig_bitmap.height(), plot.bitmap.height(), scaling_factor)

        return True



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
        # CB/JAB: Remove sheet_type and sheet from this class; instead have a mechanism for specifying a list of sheets
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

    keyname = "ProjectionSheet" # CB: Make into a parameter and document what it is

    sheet = ObjectSelectorParameter(default=None,doc="""
    The Sheet from which to produce plots.""")


    def _update_command(self):

        # CEBALERT: rather than various scattered tests like the one below and for projections in later classes,
        # have some method (probabably declared in a super class) like "_check_conditions()".
        if self.sheet is None: raise ValueError("%s must have a sheet (currently None)."%self)
	### JCALERT: commands in analysis.py should be re-written to
	### avoid setting these global parameters.
	topo.commands.analysis.sheet_name = self.sheet.name
        super(ProjectionSheetPlotGroup,self)._update_command()
        
    # CB/JAB: Should replace this custom routine with simply providing
    # a method for constructing a special key name; then maybe nearly
    # all the fancy processing in the various _create_plots functions
    # can be eliminated
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

    # CB/JAB: Remove sheet_type and sheet from superclasses; instead have a mechanism for specifying a list of sheets, and then focus down to one sheet in this class
        
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
    _abstract_class_name = "CFPlotGroup"
    
    situate = BooleanParameter(default=False,doc=
                               """If True, plots the weights on the
entire source sheet, using zeros for all weights outside the
ConnectionField.  If False, plots only the actual weights that are
stored.""")

# CEBALERT: all necessary situate stuff removed from tkgui? See ALERT in CFRelatedPlotGroupPanel.



# CB/JAB: Consider -- is this actually general enough to handle
# anything related to a unit, rather than CF specifically?
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

    projection = ObjectSelectorParameter(default=None,doc="The projection to visualize.")

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
        self.height_of_tallest_plot = 5 # Initial value
        
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


    def _ordering_plots(self):
	"""Skips plot sorting for Projections to keep the units in order."""
	pass



# CB/JAB: Can't it just inherit from ConnectionFieldsPlotGroup
# (renamed to something like UnitPlotGroup)?  Then will simply have
# something about getting the right time.
class FeatureCurvePlotGroup(PlotGroup):


    sheet = ObjectSelectorParameter() 

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

