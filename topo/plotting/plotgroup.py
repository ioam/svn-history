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
from topo.base.sheet import Sheet
from topo.base.connectionfield import CFSheet

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


    def __init__(self, plot_list, normalize, sheetcoords, integerscaling, **params):
    
        """
	plot_list is a static list specifying the Plot objects belonging to the PlotGroup.

	normalize specified if the Plot in the PlotGroup should be normalized by default.

	sheetcoords is a boolean specifying if the Plots are in sheet coordinates 
	(as opposed to matrix coordinates)

	intergerscaling is a boolean indicating that the Plots are scaled with integer.
        """
        super(PlotGroup,self).__init__(**params)  

	self.plot_list = plot_list	
	self.normalize = normalize
	self.sheetcoords = sheetcoords

	if integerscaling:
            self.sizeconvertfn = int
        else:
            self.sizeconvertfn = identity

	self.bitmaps = []

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

	self.min_master_zoom=3.0
	self.height_of_tallest_plot = 1.0
	self.initial_plot=True


    def _generate_sheet_views(self):
	""" 
	Only implemented for TemplatePlotGroup. 
	Execute the command associated with the template.
	"""
	pass


    def _plot_list(self):
	"""
	function that returns the plot_list.
	Re-implemented by TemplatePlotGroup to construct the plot list as specified by the template.
	"""
	return self.plot_list


    ### JCALERT: gte rid of this function and only keep plots
    def load_images(self):
        """
        Pre: the update command that load the SheetView corresponding to the PlotGroup
             has to be called.
        Post: self.bitmaps contains a list of topo.bitmap objects or None if
              no valid maps were available.

        Returns: List of bitmaps.  self.bitmaps also has been updated.
        """
        self.bitmaps = []
        for each in self.plots():
            win = each.bitmap                      
            win.plot_src_name = each.plot_src_name   
	    win.name = each.name
            self.bitmaps.append(win)
        return self.bitmaps
    

    # Call from load_images() as a dynamic list to regenerate all_plots anytime (allowing refreshing)
    def plots(self):
        """
        Generate the bitmap lists.
        """
        bitmap_list = []
	### JCALERT: here we should generate the sheet_views
	### Need more work to see how to do it.
	self._generate_sheet_views()
        all_plots = [each for each in self._plot_list() if each != None]
	# scaling the Plots
	### JCALERT: momentary hack
	if all_plots!=[]:
	    self.scale_images(all_plots)
	# sorting the Plots.
	self._ordering_plots(all_plots)
        return all_plots
 

    def scale_images(self,plots):
        """
        It is assumed that the PlotGroup code has not scaled the bitmap to the size currently
        desired by the GUI.
        """ 
        ### JCALERT: that cannot be in the constructor for the moment, because when creating the 
 	### panel, there is no PlotGroup assigned to it... It will change when all will be inserted 
 	### in the PlotGroup (i.e scale_image, set_initial_master_zoom, compute_max_height...)
 	if self.initial_plot:
 	    self._set_height_of_tallest_plot(plots)

	### JCALERT: here we should take the plot bounds instead of the sheet one (id in set_height_of..)?
	max_sheet_height = max([(topo.sim.objects(Sheet)[p.plot_src_name].bounds.lbrt()[3]
 			      -topo.sim.objects(Sheet)[p.plot_src_name].bounds.lbrt()[1])
 			     for p in plots if p.resize])
	for plot in plots:
            if not plot.resize:
                scaling_factor = 1
            else:
		if self.sheetcoords:		   
                    s = topo.sim.objects(Sheet).get(plot.plot_src_name,None)
		    scaling_factor=self.sizeconvertfn(self.height_of_tallest_plot/float(s.density)/max_sheet_height)
		else:
		    scaling_factor=self.sizeconvertfn(self.height_of_tallest_plot/float(plot.bitmap.height()))
	    plot.bitmap.image = plot.bitmap.zoom(scaling_factor)

                              
   #          tmp_list = tmp_list + [bitmap.zoom(scaling_factor)]
	
# 	self.zoomed_images = [ImageTk.PhotoImage(im) for im in tmp_list]


    def _set_height_of_tallest_plot(self,plots):
	""" 
	Subfunction that set the initial master zooms for both the sheet
	coordinates and the matrix coordinates case. 
	"""
	### JCALERT! Momentary hack
	max_sheet_height = max([(topo.sim.objects(Sheet)[p.plot_src_name].bounds.lbrt()[3]
 			  -topo.sim.objects(Sheet)[p.plot_src_name].bounds.lbrt()[1])
 			  for p in plots if p.resize])
	max_density = max([topo.sim.objects(Sheet)[p.plot_src_name].density
			   for p in plots if p.resize])
	sheet_max_height = max_density*max_sheet_height
	matrix_max_height = max([p.bitmap.height() for p in plots if p.resize])
	max_height = max(sheet_max_height,matrix_max_height)
	if (max_height >= self.INITIAL_PLOT_HEIGHT):
	    self.height_of_tallest_plot = max_height
	else:	
	    self.height_of_tallest_plot = self.INITIAL_PLOT_HEIGHT
        ### JCALERT: That functionnality will have to be added again to the PlotGroupPanel
# 	if self.height_of_tallest_plot == self.min_master_zoom:
# 	    self.reduce_button.config(state=DISABLED)
	self.initial_plot=False


    def _ordering_plots(self,plot_list):
	"""
	Function called to sort the Plots in order.
	They are ordered according to their precedence number first, and then by alphabetical order.
	"""
	return plot_list.sort(cmp_plot)




class TemplatePlotGroup(PlotGroup):
    """
    PlotGroup that is built as specified by a PlotGroupTemplate.
    """

    def __init__(self,plot_list,normalize,sheetcoords,integerscaling,template,sheet_name,**params):

	super(TemplatePlotGroup,self).__init__(plot_list,normalize,sheetcoords,integerscaling,**params)
	self.template = template
	# If no sheet_name is defined, the sheet_filter_lam accepts all sheets
        # (i.e the PlotGroup will try to build a Plot object for each Sheet in the simulation)
	self.sheet_name=sheet_name
        if sheet_name:
	    self.sheet_filter_lam = lambda s: s.name == sheet_name
        else:
            self.sheet_filter_lam = lambda s : True

	# Command used to refresh the plot, if any
        self.cmdname = self.template.command

	# add static images to the added_plot_list, as specified by the template.
        self._add_static_images()
	

    def _generate_sheet_views(self):
	""" 
	Only implemented for TemplatePlotGroup. 
	Execute the command associated with the template.
	"""
	exec self.cmdname in __main__.__dict__

	
    def _plot_list(self):
        """
        Procedure that is called when creating a PlotGroup, that return the plot_list attribute
        i.e. the list of plot that are specified by the PlotGroup template.

        This function calls create_plots, that is implemented in each TemplatePlotGroup subclasses.
        """
	sheet_list = [each for each in topo.sim.objects(Sheet).values() if self.sheet_filter_lam(each)]      
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
# 	p = make_template_plot(plot_channels,sheet.sheet_view_dict,sheet.density,
#  			       bb,self.normalize,name=plot_name)
        p = make_template_plot(plot_channels,sheet.sheet_view_dict,sheet.density,
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

    def __init__(self,plot_list,normalize,sheetcoords,integerscaling,
		 template,sheet_name,x,y,**params):
        self.x = x
        self.y = y
      	self.situate = False       
	super(ConnectionFieldsPlotGroup,self).__init__(plot_list,normalize,
						       sheetcoords,integerscaling,template,sheet_name,**params)
  
    def _generate_sheet_views(self):
	""" 
	Only implemented for TemplatePlotGroup. 
	Execute the command associated with the template.
	"""
	### JCALERT: commands in analysis have to be re-written so that to avoid
	### setting all these global parameters.
	topo.commands.analysis.coordinate = (self.x,self.y)
	topo.commands.analysis.sheet_name = self.sheet_name

        exec self.cmdname  in __main__.__dict__
		

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
			plot_list.append(make_template_plot(plot_channels,p.src.sheet_view_dict,p.src.density,
							    None,self.normalize,name=p.name))
		    else:
			(r,c) = p.dest.sheet2matrixidx(self.x,self.y)
			plot_list.append(make_template_plot(plot_channels,p.src.sheet_view_dict,p.src.density,
							    p.cf(r,c).bounds,self.normalize,name=p.name))
			
	    else:
		 plot_list.append(make_template_plot(pt,sheet.sheet_view_dict,sheet.density,
						     sheet.bounds,self.normalize,name=pt_name))
        return plot_list




class ProjectionPlotGroup(TemplatePlotGroup):
    """
    PlotGroup for Projection Plots
    """

    def __init__(self,plot_list,normalize,sheetcoords,integerscaling,
		 template,sheet_name,proj_name,density,**params):

	### JCALERT! rename to proj_name
        self.weight_name = proj_name
        self.density = density

        ### JCALERT! shape determined by the plotting density
        ### This is set by self.generate_coords()
        self.proj_plotting_shape = (0,0)
	
	### JCALERT! should become an argument of the constructor (id:for connectionPlotGroup) 
	self.situate = False 
       
        super(ProjectionPlotGroup,self).__init__(plot_list,normalize,sheetcoords,integerscaling,
						 template,sheet_name,**params)

        self.INITIAL_PLOT_HEIGHT = 6
        self.min_master_zoom=1


	### JCALERT! change this name 
        #self._sim_ep_src = self._sim_ep.projections().get(self.weight_name,None)
 

    def _generate_sheet_views(self):
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
        exec self.cmdname  in __main__.__dict__
		
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
		    plot_list.append(make_template_plot(plot_channels,src_sheet.sheet_view_dict,src_sheet.density,
							src_sheet.bounds,self.normalize))
		else:
		    (r,c) = projection.dest.sheet2matrixidx(x,y)
		    plot_list.append(make_template_plot(plot_channels,src_sheet.sheet_view_dict,src_sheet.density,
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
        ### JCALERT! It is a bit confusing, but in the case of the projection
        ### sheet_filter_lam filter to one single sheet...
	### this has to be made simpler...
	for s in topo.sim.objects(Sheet).values():
	    if (self.sheet_filter_lam(s) and isinstance(s,CFSheet)):
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

    ### JCALERT It has to be re-implemented for the projectionpanel,
    ### but this is only a momentary version that requires more work.
    def _set_height_of_tallest_plot(self,plots):
	""" 
	Subfunction that set the initial master zooms for both the sheet
	coordinates and the matrix coordinates case. 
	"""
        self.height_of_tallest_plot = self.INITIAL_PLOT_HEIGHT
	self.initial_plot=False


    def scale_images(self,plots):
	pass


    def _ordering_plots(self,plot_list):
	"""
	Function called to sort the Plots in order.
	It is re-implmented for ProjectionPlotGroup, because we do not want to order the Connection Field
        views composing the projection plot in any order (i.e. we want to preserve the same order).
	"""
	return plot_list
    

