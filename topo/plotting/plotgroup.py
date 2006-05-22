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
from topo.base.parameterclasses import Parameter,BooleanParameter
from topo.base.sheet import Sheet
from topo.base.cf import CFSheet

from plot import make_template_plot, Plot


def cmp_plot(plot1,plot2):
    """
    Comparison function for Plots.
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


class PlotGroup(ParameterizedObject):
    """
    Container that has one or more Plots and also knows how to arrange
    the plots and other special parameters.
    """

    ###JCALERT:
    ### - clean up the doc.
    ### - rewrite the test file.

    normalize = BooleanParameter(default=False,doc=
"""Whether to scale plots so that the peak value will be white
and the minimum value black.""")

    sheetcoords = BooleanParameter(default=False,doc=
"""Whether to scale plots based on their relative sizes in sheet
coordinates.  If true, plots are scaled so that their sizes are
proportional to their area in sheet coordinates, so that one can
compare corresponding areas.  If false, plots are scaled to have
similar sizes on screen, regardless of their corresponding
sheet areas.""")

    integerscaling = BooleanParameter(default=False,doc=
"""When scaling bitmaps, whether to ensure that the scaled bitmap is an even
multiple of the original.  If true, every unit will be represented by a
square of the same size.  Typically false so that the overall area will
be correct, e.g. when using Sheet coordinates, which is often more
important.""")
    
    def __init__(self, plot_list, **params):
        """
	plot_list is a static list specifying the Plot objects belonging to the PlotGroup.
        """
        super(PlotGroup,self).__init__(**params)  

	self.plot_list = plot_list	
	if self.integerscaling:
            self.sizeconvertfn = int
        else:
            self.sizeconvertfn = identity

	# List of plot labels
	self.labels = []

        # In the future, it might be good to be able to specify the
        # plot rows and columns using tuples.  For instance, if three
        # columns are desired with the plots laid out from left to
        # right, we could use (None, 3).  If three rows are desired
        # then (3, None).  Another method that would work is [3,2,4]
        # would have the first row with 3, the second row with 2, the
        # third row with 4, etc.  The default left-to-right ordering
        # in one row could perhaps be represented as (None, Inf).

	# Enforce a minimum plot height for the tallest plot of the PlotGroup.
	self.INITIAL_PLOT_HEIGHT = 150

	self.height_of_tallest_plot = 1.0
	self.initial_plot = True
	self.minimum_height_of_tallest_plot = 1.0

	# Time attribute.
	self.time = topo.sim.time()


    ### JCALERT: ASK JIM if we should rename that.
    def update_environment(self):
	""" 
	Only implemented for TemplatePlotGroup. 
	Execute the command associated with the template
	(e.g. generating the Sheetviews necessary to create the PlotGroup's Plots).
	"""
	pass


    def _plot_list(self):
	"""
	function that returns the plot_list.
	Re-implemented by TemplatePlotGroup to construct the plot list as specified by the template.
	"""
	return self.plot_list

    
    def update_plots(self,update=True):
        """
        Generate the sorted and scaled list of plots constituting the PlotGroup.
        """
	### JCALERT! See if we keep this test
	if update:
	    self.update_environment()
	    self.time = topo.sim.time()
	self.plots = [plot for plot in self._plot_list() if plot != None]
	# scaling the Plots
	### JCALERT: momentary hack
	if self.plots!=[]:
	    self.scale_images()
	# sorting the Plots.
	self._ordering_plots()	
	self.generate_labels()

     ### Need to be re-implemented for connectionfieldplotgroup.
    def generate_labels(self):
	""" Function used for generating the labels."""
	self.labels = []
	for plot in self.plots:
	    self.labels.append(plot.plot_src_name + '\n' + plot.name)


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
	max_sheet_height = max([(topo.sim.objects(Sheet)[p.plot_src_name].bounds.lbrt()[3]
 			      -topo.sim.objects(Sheet)[p.plot_src_name].bounds.lbrt()[1])
 			     for p in self.plots if p.resize])

	for plot in self.plots:
            if not plot.resize:
                scaling_factor = 1
            else:
		if self.sheetcoords:		   
                    s = topo.sim.objects(Sheet).get(plot.plot_src_name,None)
		    scaling_factor=self.sizeconvertfn(self.height_of_tallest_plot/float(s.xdensity)/max_sheet_height)
		else:
		    scaling_factor=self.sizeconvertfn(self.height_of_tallest_plot/float(plot.bitmap.height()))
                    ### JABHACKALERT: Enforces a minimum scaling factor of 1,
                    ### to avoid divide-by-zero errors.  The actual cause of these
                    ### errors should instead be avoided elsewhere.
                    if (scaling_factor <= 0):
                        scaling_factor=1
                    
	    plot.bitmap.image = plot.bitmap.zoom(scaling_factor)


    def _calculate_minimum_height_of_tallest_plot(self):
	"""
        Calculate the size of the plot that will generate the largest bitmap.

        This value is used to set the initial plot heights, and the
        minimum height to which the plot can be reduced.
	"""
        # JCALERT: Should be rewritten more cleanly.
	max_sheet_height = max([(topo.sim.objects(Sheet)[p.plot_src_name].bounds.lbrt()[3]
 			  -topo.sim.objects(Sheet)[p.plot_src_name].bounds.lbrt()[1])
 			  for p in self.plots if p.resize])
	max_density = max([topo.sim.objects(Sheet)[p.plot_src_name].xdensity
			   for p in self.plots if p.resize])
	sheet_max_height = max_density*max_sheet_height
	matrix_max_height = max([p.bitmap.height() for p in self.plots if p.resize])
	max_height = max(sheet_max_height,matrix_max_height)
        self.minimum_height_of_tallest_plot = max_height
	if (max_height >= self.INITIAL_PLOT_HEIGHT):
	    self.height_of_tallest_plot = max_height
	else:	
	    self.height_of_tallest_plot = self.INITIAL_PLOT_HEIGHT
	self.initial_plot=False


    def _ordering_plots(self):
	"""
	Function called to sort the Plots in order.
	They are ordered according to their precedence number first, and then by alphabetical order.
	"""
	self.plots.sort(cmp_plot)




class TemplatePlotGroup(PlotGroup):
    """
    PlotGroup that is built as specified by a PlotGroupTemplate.
    """

    # JABALERT: Should be a StringParameter
    updatecommand = Parameter(default="",doc=
"""Command to execute before updating this plot, e.g. to calculate sheet views.

The command can be any Python code, and will be evaluated in the main namespace
(as if it were typed into a .ty script).  The initial value is determined by
the template for this plot, but various arguments can be passed, a modified
version substituted, etc.""")


    def __init__(self,plot_list,template,sheet_name,**params):

	super(TemplatePlotGroup,self).__init__(plot_list,**params)
	self.template = template

	# Sheet_name can be none, in which case the PlotGroup build Plots for each Sheet.
	self.sheet_name=sheet_name

	# Command used to refresh the plot, if any.  Overwrites any keyword parameter above.
        self.updatecommand = self.template.command

	# Add static images to the added_plot_list, as specified by the template.
        self._add_static_images()
	

    def update_environment(self):
	""" 
	Only implemented for TemplatePlotGroup. 
	Execute the command associated with the template.
	"""
	exec self.updatecommand in __main__.__dict__

	
    def _plot_list(self):
        """
        Procedure that is called when creating a PlotGroup, that return the plot_list attribute
        i.e. the list of plot that are specified by the PlotGroup template.

        This function calls create_plots, that is implemented in each TemplatePlotGroup subclasses.
        """
	# If no sheet_name is defined, the sheet_filter_lam accepts all sheets
        # (i.e the PlotGroup will try to build a Plot object for each Sheet in the simulation)
	if self.sheet_name:
	    sheet_list = [each for each in topo.sim.objects(Sheet).values() if each.name == self.sheet_name]   
	else:
	    sheet_list = [each for each in topo.sim.objects(Sheet).values()]
   
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
	Creates a plot corresponding to a plot_template and its name, and a sheet.
	"""
	plot_channels = pt
	plot_name = pt_name
### temporary: will have to be deleted when implementing the Plot BB in the right way.
#	from topo.base.boundingregion import BoundingBox
#       bb=BoundingBox(points=((-1.0,-1.0),(1.0,1.0)))
# 	bb1=BoundingBox(points=((-0.25,-0.25),(0.25,0.25)))
# 	bb2=BoundingBox(points=((-0.75,-0.5),(0.75,0.5)))
# 	p = make_template_plot(plot_channels,sheet.sheet_view_dict,sheet.xdensity,
#  			       bb,self.normalize,name=plot_name)
        p = make_template_plot(plot_channels,sheet.sheet_view_dict,sheet.xdensity,
 			       sheet.bounds,self.normalize,name=plot_name)
	return [p]


    def _add_static_images(self):
        """
        Construct a static image Plot (e.g. a color key for an Orientation Preference map).
        """        
        for image_name,file_path in self.template.static_images :
            image = Image.open(file_path)
	    plot = Plot(image,name=image_name)
            self.plot_list.append(plot)
            


class ConnectionFieldsPlotGroup(TemplatePlotGroup):
    """
    PlotGroup for Connection Fields UnitViews.  

    Attributes:
      x: x-coordinate of the unit to plot
      y: y-coordinate of the unit to plot
      situate: Whether to situate the plot on the full source sheet, or just show the weights.
    """

    def __init__(self,plot_list,template,sheet_name,x,y,**params):
        self.x = x
        self.y = y
      	self.situate = False       
	super(ConnectionFieldsPlotGroup,self).__init__(plot_list,template,sheet_name,**params)
  
    def update_environment(self):
	""" 
	Only implemented for TemplatePlotGroup. 
	Execute the command associated with the template.
	"""
	### JCALERT: commands in analysis have to be re-written so that to avoid
	### setting all these global parameters.
	topo.commands.analysis.coordinate = (self.x,self.y)
	topo.commands.analysis.sheet_name = self.sheet_name

        exec self.updatecommand  in __main__.__dict__
		

    def _create_plots(self,pt_name,pt,sheet):
	""" 
	Sub-function of _plot_list().
	Creates a plot as specified by a Connection Field plot_template:
	allows creating a connection field plot or a normal plot.
	"""
	plot_list = []
        if not isinstance(sheet,CFSheet):
            self.warning('Requested weights view from other than CFSheet.')
        else:
	    # If the Strength is set to Weights, we request UnitViews 
	    # (i.e. by changing the Strength key in the plot_channels)
	    # Otherwise, we consider Strength as specifying a SheetView.
	    if ( pt.get('Strength', None) == 'Weights'):
		for p in sheet.projections().values():			    
		    plot_channels = copy.deepcopy(pt)
		    # Note: the UnitView is in the src_sheet view_dict,
		    # and the name in the key is the destination sheet.
		    key = ('Weights',sheet.name,p.name,self.x,self.y)
		    plot_channels['Strength'] = key
		    if self.situate:
			plot_list.append(make_template_plot(plot_channels,p.src.sheet_view_dict,p.src.xdensity,
							    None,self.normalize,name=p.name))
		    else:
			(r,c) = p.dest.sheet2matrixidx(self.x,self.y)
			plot_list.append(make_template_plot(plot_channels,p.src.sheet_view_dict,p.src.xdensity,
							    p.cf(r,c).bounds,self.normalize,name=p.name))
			
	    else:
		 plot_list.append(make_template_plot(pt,sheet.sheet_view_dict,sheet.xdensity,
						     sheet.bounds,self.normalize,name=pt_name))
        return plot_list


    ### Need to be re-implemented for connectionfieldplotgroup.
    def generate_labels(self):
	""" Function used for generating the labels."""
	self.labels = []
	for plot in self.plots:
	    self.labels.append(plot.name + '\n(from ' + plot.plot_src_name+')')



class ProjectionPlotGroup(TemplatePlotGroup):
    """
    PlotGroup for Projection Plots
    """

    def __init__(self,plot_list,template,sheet_name,proj_name,density,**params):

	### JCALERT! rename to proj_name
        self.weight_name = proj_name
        self.density = density

        ### JCALERT! shape determined by the plotting density
        ### This is set by self.generate_coords()
        self.proj_plotting_shape = (0,0)
	
	### JCALERT! should become an argument of the constructor (id:for connectionPlotGroup) 
	self.situate = False 
       
        super(ProjectionPlotGroup,self).__init__(plot_list,template,sheet_name,**params)

        self.INITIAL_PLOT_HEIGHT = 5


	### JCALERT! change this name 
        #self._sim_ep_src = self._sim_ep.projections().get(self.weight_name,None)
 

    def update_environment(self):
	""" 
	Only implemented for TemplatePlotGroup. 
	Execute the command associated with the template.
	"""
	### JCALERT: commands in analysis have to be re-written so that to avoid
	### setting all these global parameters.
	coords = self.generate_coords()
        topo.commands.analysis.proj_coords = coords
	topo.commands.analysis.sheet_name = self.sheet_name
        topo.commands.analysis.proj_name = self.weight_name
        exec self.updatecommand  in __main__.__dict__
		
    def _create_plots(self,pt_name,pt,sheet):
	""" 
	Sub-function of _plot_list().
	Creates a plot as specified by a Projection plot_template:
	Built a projection Plot from corresponding UnitViews.
	"""
	projection = sheet.projections().get(self.weight_name,None)
        plot_list=[]
        if projection:
	    src_sheet=projection.src
	    for x,y in self.generate_coords():
		plot_channels = copy.deepcopy(pt)
		# JC: we might consider allowing the construction of 'projection type' plots
		# with other things than UnitViews.
		key = ('Weights',sheet.name,projection.name,x,y)
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
	for s in topo.sim.objects(Sheet).values():
	    if (s.name==self.sheet_name and isinstance(s,CFSheet)):
		self._sim_ep = s
        (l,b,r,t) = self._sim_ep.bounds.lbrt()
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


    def scale_images(self):
	if self.initial_plot:
 	    self._calculate_minimum_height_of_tallest_plot()

	### JCALERT: here we should take the plot bounds instead of the sheet one (id in set_height_of..)?
	max_sheet_height = max([(topo.sim.objects(Sheet)[p.plot_src_name].bounds.lbrt()[3]
 			      -topo.sim.objects(Sheet)[p.plot_src_name].bounds.lbrt()[1])
 			     for p in self.plots if p.resize])
        matrix_max_height = max([p.bitmap.height() for p in self.plots if p.resize])

	for plot in self.plots:
            if not plot.resize:
                scaling_factor = 1
            else:
		if self.sheetcoords:		   
                    s = topo.sim.objects(Sheet).get(plot.plot_src_name,None)
		    scaling_factor=self.sizeconvertfn(self.height_of_tallest_plot/float(s.xdensity)/max_sheet_height)
		else:
		    scaling_factor=self.sizeconvertfn(self.height_of_tallest_plot/float(matrix_max_height))
	    plot.bitmap.image = plot.bitmap.zoom(scaling_factor)


    def _ordering_plots(self):
	"""Skips plot sorting for Projections to keep the units in order."""
	pass
    

