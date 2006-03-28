"""
Hierarchy of PlotGroup classes, i.e. output-device-independent sets of plots.

Includes PlotGroups for standard plots of anything in a Sheet database,
plus weight plots for one unit, and projections.

$Id$
"""
__version__='$Revision$'

import types
import copy

from Numeric import transpose, array, ravel

import Image

import topo
from topo.misc.utils import flatten, dict_sort
from topo.base.parameterizedobject import ParameterizedObject
from topo.base.sheet import Sheet
from topo.base.sheetview import SheetView
from topo.base.connectionfield import CFSheet

from plot import make_template_plot, Plot
import bitmap



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


# PlotGroup used by the simulation are stored in this dictionnary
plotgroup_dict = {}



class PlotGroup(ParameterizedObject):
    """
    Container that has one or more Plots and also knows how to arrange
    the plots and other special parameters.
    """

    ###JCALERT:
    ### - renamed plot_group_key to plotgroup_key.
    ### - fix the sorting of the plot for display.
    ### - clean up the doc.
    ### - rewrite the test file.


    def __init__(self, plot_group_key, plot_list, normalize,**params):
    
        """
	plot_group_key is a key for storing the PlotGroup in the plotgroup_dict.
	It is then stored and identified under this key.

	plot_list is a static list specifying the Plot objects belonging to the PlotGroup.

	normalize specified if the Plot in the PlotGroup should be normalized by default.       
        """
        super(PlotGroup,self).__init__(**params)  

	self.plot_group_key = plot_group_key
	### JCALERT:Normalize is no really used by PlotGroup for the moment
        ### But it will be when sorted out what to do with TestPattern.
        ### the problem is that for a PlotGroup the plot_list is static...
        ### so it is hard to re-generate the plot if normalize change...
        ### (it is already used by sub-classes though)
	### This should be fixed by having a normalize method in Plot that transform a plot
        ### bitmap to normalize it. If self.normalize change in the PlotGroup,
        ### the _plot_list function called the Plot.normalize method on the plot_list before
        ### returning it.
	self.normalize = normalize
	self.plot_list = plot_list	
        
	# store the PlotGroup in plot_group_dict
	plotgroup_dict[plot_group_key]=self
	self.bitmaps = []

        # In the future, it might be good to be able to specify the
        # plot rows and columns using tuples.  For instance, if three
        # columns are desired with the plots laid out from left to
        # right, we could use (None, 3).  If three rows are desired
        # then (3, None).  Another method that would work is [3,2,4]
        # would have the first row with 3, the second row with 2, the
        # third row with 4, etc.  The default left-to-right ordering
        # in one row could perhaps be represented as (None, Inf).


    def _plot_list(self):
	"""
	function that returns the plot_list.
	"""
	return self.plot_list


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
	all_plots = flatten(self._plot_list()) 
        generated_bitmap_list = [each for each in all_plots if each != None]
	# sorting the Plots.
	self._ordering_plots(generated_bitmap_list)
        return generated_bitmap_list
   

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

    def __init__(self,plot_group_key,plot_list,normalize,template,sheet_name,**params):

        super(TemplatePlotGroup,self).__init__(plot_group_key,plot_list,normalize,**params)
	
	self.template = template
	# If no sheet_name is defined, the sheet_filter_lam accepts all sheets
        # (i.e the PlotGroup will try to build a Plot object for each Sheet in the simulation)
        if sheet_name:
	    self.sheet_filter_lam = lambda s: s.name == sheet_name
        else:
            self.sheet_filter_lam = lambda s : True

	# add static images to the added_plot_list, as specified by the template.
        self._add_static_images()

	
    def _plot_list(self):
        """
        Procedure that is called when creating a PlotGroup, that return the plot_list attribute
        i.e. the list of plot that are specified by the PlotGroup template.

        This function calls create_plots, that is implemented in each TemplatePlotGroup subclasses.
        """
	sheet_list = [each for each in dict_sort(topo.sim.objects(Sheet)) if self.sheet_filter_lam(each)]      
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
        p = make_template_plot(plot_channels,sheet.sheet_view_dict,sheet.density,
 			       sheet.bounds,self.normalize,False,name=plot_name)
	return [p]


    def _add_static_images(self):
        """
        Construct the static image Plot (e.g. color key for Orientation Preference map.
        """        
        for image_name,file_path in self.template.static_images :
            image = Image.open(file_path)
	    plot = Plot(image,name=image_name)
	    plot.bitmap.resize=False
            self.plot_list.append(plot)
            


class ConnectionFieldsPlotGroup(TemplatePlotGroup):
    """
    PlotGroup for Connection Fields UnitViews.  

    Attributes:
      x: x-coordinate of the unit to plot
      y: y-coordinate of the unit to plot
      situate: Whether to situate the plot on the full source sheet, or just show the weights.
    """

    def __init__(self,plot_group_key,plot_list,normalize,template,sheet_name,**params):
        self.x = float(plot_group_key[2])
        self.y = float(plot_group_key[3])
      	self.situate = False       
	super(ConnectionFieldsPlotGroup,self).__init__(plot_group_key,plot_list,normalize,
						       template,sheet_name,**params)
  
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
		for p in set(flatten(sheet.in_projections.values())):			    
		    plot_channels = copy.deepcopy(pt)
		    # Note: the UnitView is in the src_sheet view_dict,
		    # and the name in the key is the destination sheet.
		    key = ('Weights',sheet.name,p.name,self.x,self.y)
		    plot_channels['Strength'] = key
		    if self.situate:
			plot_list.append(make_template_plot(plot_channels,p.src.sheet_view_dict,p.src.density,
							    None,self.normalize,self.situate,name=p.src.name))
		    else:
			(r,c) = p.dest.sheet2matrixidx(self.x,self.y)
			plot_list.append(make_template_plot(plot_channels,p.src.sheet_view_dict,p.src.density,
							    p.cf(r,c).bounds,self.normalize,self.situate,name=p.src.name))
			
	    else:
		 plot_list.append(make_template_plot(pt,sheet.sheet_view_dict,sheet.density,
						     sheet.bounds,self.normalize,self.situate,name=pt_name))
        return plot_list




class ProjectionPlotGroup(TemplatePlotGroup):
    """
    PlotGroup for Projection Plots
    """

    def __init__(self,plot_group_key,plot_list,normalize,template,sheet_name,**params):
       
        self.weight_name = plot_group_key[1]
        self.density = float(plot_group_key[2])

        ### JCALERT! shape determined by the plotting density
        ### This is set by self.generate_coords()
        self.proj_plotting_shape = (0,0)

	self.situate = False
        
        super(ProjectionPlotGroup,self).__init__(plot_group_key,plot_list,normalize,
                                                 template,sheet_name,**params)

	### JCALERT! It is a bit confusing, but in the case of the projection
        ### sheet_filter_lam filter to one single sheet...
	### this has to be made simpler...
	for s in topo.sim.objects(Sheet).values():
	    if self.sheet_filter_lam(s):
		self._sim_ep = s

        self._sim_ep_src = self._sim_ep.projections().get(self.weight_name,None)
 
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
							src_sheet.bounds,self.normalize,self.situate))
		else:
		    (r,c) = projection.dest.sheet2matrixidx(x,y)
		    plot_list.append(make_template_plot(plot_channels,src_sheet.sheet_view_dict,src_sheet.density,
							projection.cf(r,c).bounds,self.normalize,self.situate))
        return plot_list


    def generate_coords(self):
        """
        Evenly space out the units within the sheet bounding box, so
        that it doesn't matter which corner the measurements start
        from.  A 4 unit grid needs 5 segments.  List is in left-to-right,
        from top-to-bottom.
        """
        def rev(x): y = x; y.reverse(); return y
        
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

  
  
    def _ordering_plots(self,plot_list):
	"""
	Function called to sort the Plots in order.
	It is re-implmented for ProjectionPlotGroup, because we do not want to order the Connection Field
        views composing the projection plot in any order (i.e. we want to preserve the same order).
	"""
	return plot_list
    

