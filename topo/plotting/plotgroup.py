"""
Hierarchy of PlotGroup classes, i.e. output-device-independent sets of plots.

Includes PlotGroups for standard plots of anything in a Sheet database,
plus weight plots for one unit, and projections.

$Id$
"""
__version__='$Revision$'

import types
from itertools import chain

from Numeric import transpose, array, ravel

from topo.base.utils import flatten, dict_sort
from topo.base.topoobject import TopoObject
from topo.base.sheet import Sheet
from topo.base.sheetview import SheetView
from topo.base.connectionfield import CFSheet

from plot import Plot, make_plot
import bitmap

### JABALERT: This constant (and PlotGroup.shape) should be removed
### for now, though it may be reinstated some day.
FLAT = 'FLAT'

def sort_plots(plot_list):
    """Sort a (static) plot list according to the src_names."""
    plot_list.sort(lambda x, y: cmp(x.view_info['src_name'], y.view_info['src_name']))



class PlotGroup(TopoObject):
    """
    Container that has one or more Plots and also knows how to arrange
    the plots and other special parameters.
    """

    ###JCALERT:
    ### - re-arranged the order and look at the call in all panel classes (i.e. inputparampanel)
    ### also review the doc of each functions.
    ### - rewrite the test file.

    def __init__(self,simulator,template,plot_group_key,sheet_name=None,plot_list=[],shape=FLAT,**params):
        """
        plot_list can be of two types: 
        1.  A list of Plot objects that can return bitmaps when requested.
        2.  Can also be a function that returns a list of plots so
        that each time plot() is called, an updated list is created for the
        latest list of sheets in the simulation.
        """
        super(PlotGroup,self).__init__(**params)        
        self.all_plots = []
        self.added_list = []

        # Shape of the plotting display used by PlotGroup.
        #
        # Allowable shapes include:
        ### JABALERT: What shapes are already supported, right now?
        #
        # In the future, it might be good to be able to specify the
        # plot rows and columns using tuples.  For instance, if three
        # columns are desired with the plots laid out from left to
        # right, we could use (None, 3).  If three rows are desired
        # then (3, None).  Another method that would work is [3,2,4]
        # would have the first row with 3, the second row with 2, the
        # third row with 4, etc.  The default left-to-right ordering
        # in one row could perhaps be represented as (None, Inf).
        self.shape = shape
        
        self.plot_group_key = plot_group_key
        self.bitmaps = []

        ### JABALERT: This class hierarchy would be simpler to
        ### understand if all the template, lambda, sheet_name,
        ### etc. stuff moves to BasicPlotGroup, which would be renamed
        ### to TemplatePlotGroup.  That way the base class PlotGroup
        ### would be simple -- just working with a static list of
        ### plots, using a member function like plots() (a merger of
        ### initialize_plot_list() and the current plots()) that for a
        ### PlotGroup returns the static list, but for a
        ### TemplatePlotGroup generates the list anew each time, based
        ### on the template.
        
        self.template = template
        
	# If no sheet_name is defined, the sheet_filter_lam accepts all sheets
        if sheet_name:
	    self.sheet_filter_lam = lambda s: s.name == sheet_name
        else:
            self.sheet_filter_lam = lambda s : True

	self.simulator = simulator

	self.plot_list = lambda: self._initialize_plot_list(plot_list)


    def _initialize_plot_list(self,plot_list):
        """
        Procedure that is called when creating a PlotGroup, that return the plot_list attribute
        i.e. the list of plot that are specified by the PlotGroup template.

        This function calls create_plots, that is implemented in each PlotGroup subclasses.
        (In particular, this needs to be different for UnitWeightsPlotGroup and ProjectionPlotGroup)
        """
	sheet_list = [each for each in dict_sort(self.simulator.objects(Sheet)) if self.sheet_filter_lam(each)]      
        # Loop over all sheets that passed the filter.
        #     Loop over each individual PlotTemplate:
        #         Call the create_plots function to create the according plot
        for each in sheet_list:
	    ### JCALERT! This test can be later removed when improving testpattern.py
            ### (for the moment call to PlotGroup from testpattern lead to self.template=None
	    if self.template != None :
		for (pt_name,pt) in self.template.plot_templates:
		    plot_list= plot_list + self.create_plots(pt_name,pt,each)
    	return plot_list

  
    def create_plots(self):
        """
	This function need to be re-implemented in the subclass.
	As it is implemented here, it leaves the possibility of passing a plot_list
        of already created plots when creating a PlotGroup.
	"""       
	return []
    

    ### JCALERT! do_plot_cmd() should be deleted here and in all sub-classes
    ### and be replaced by the command assigned from the PlotGroupTemplate
    ### (e.g measure_or_pref,measure_activity) and executed from the panel class.
    ### All these function will have to go in a special separate file  
    ### (measure_or_pref and measure_activity being in analysis/featuremap.py for the moment). 
    ### That will also enable to makes the different panel acting more uniformly,
    ### and might allow to delete basicplotgrouppanel.py
    def do_plot_cmd(self):
        """
        Command called when plots need to be generated.
        
        Subclasses of PlotGroup will need to create this function.
        """
        pass
    

    def load_images(self):
        """
        Pre:  do_plot_cmd() has already been called, so plots() will return
              valid plots.
        Post: self.bitmaps contains a list of topo.bitmap objects or None if
              no valid maps were available.

        Returns: List of bitmaps.  self.bitmaps also has been updated.
        """
        self.bitmaps = []
        for each in self.plots():
            win = each.bitmap                      
            win.view_info = each.view_info            
            self.bitmaps.append(win)
        return self.bitmaps
    
    
    def add(self,new_plot):
        """
        new_plot can be a single Plot, or it can be a list of plots.
        Either way, it will be properly added to the end of self.plot_list.
        """     
	self.added_list.extend(new_plot)
      

    # Call from load_images() as a dynamic list to regenerate all_plots anytime (allowing refreshing)
    def plots(self):
        """
        Generate the bitmap lists.
        """
        bitmap_list = []
	self.all_plots = flatten(self.plot_list()) + self.added_list
        generated_bitmap_list = [each for each in self.all_plots if each != None]
        ### JCALERT! For each plotgroup, we want the plot to be displayed
        ### in the alphabetical order according to their view_info['src_name']
        ### The only PlotGroup that does not have to do that is the projectionplotgroup
        ### and that is why this function is overwritten. 
        ### (It has to be fixed, as well as the handling of plot label in general)
        sort_plots(generated_bitmap_list)
        return generated_bitmap_list
    
  

class BasicPlotGroup(PlotGroup):
    """
    PlotGroup for Activity SheetViews
    """

    def __init__(self,simulator,template,plot_group_key,sheet_filter_lam,plot_list,**params):
        super(BasicPlotGroup,self).__init__(simulator,template,plot_group_key,sheet_filter_lam,plot_list,
                                            **params)

    def create_plots(self,pt_name,pt,sheet):

	plot_channels = pt
        ### JCALERT! Normalize should be directly get from plot_channels in Plot instead of here
        ### Same thing in UnitWeight and Projection PlotGroup.
        n = pt.get('Normalize',False)
        ### JABALERT: The newline should not be in the plot_name
        ### itself, but somewhere where it's eventually formatted.
	plot_name = '\n'+pt_name
        p = make_plot(plot_channels,sheet.sheet_view_dict,sheet.density,sheet.bounds,n,False,name=plot_name)
	return [p]

	

class UnitWeightsPlotGroup(PlotGroup):
    """
    PlotGroup for Weights UnitViews.  

    Attributes:
      x: x-coordinate of the unit to plot
      y: y-coordinate of the unit to plot
      situate: Whether to situate the plot on the full source sheet, or just show the weights.
    """

    def __init__(self,simulator,template,plot_group_key,sheet_filter_lam,plot_list,**params):
        self.x = float(plot_group_key[2])
        self.y = float(plot_group_key[3])
      	self.situate = False
        
	super(UnitWeightsPlotGroup,self).__init__(simulator,template,plot_group_key,sheet_filter_lam,plot_list,
						  **params)
  
    def create_plots(self,pt_name,pt,sheet):

	plot_list = []
        if not isinstance(sheet,CFSheet):
            self.warning('Requested weights view from other than CFSheet.')
        else:
            for p in set(flatten(sheet.in_projections.values())):	
		### JCALERT! This has to be clarified somewhere: the sheet_view for a 
		### weight belongs to the src_sheet, and the name in the key
                ### is the destination sheet.
	        plot_channels = pt

	        ### JCALERT! do the plot_channels['Strength'] == 'weights' test
                ### here and in projectionplotgroup
                key = ('Weights',sheet.name,p.name,self.x,self.y)
		plot_name = '\n(from ' + p.src.name +')'
		plot_channels['Strength'] = key			       
		plot_list.append(make_plot(plot_channels,p.src.sheet_view_dict,p.src.density,
				      p.src.bounds,pt['Normalize'],self.situate,name=plot_name))

        self.debug('plot_list =' + str(plot_list))
        return plot_list


   
class ProjectionPlotGroup(PlotGroup):
    """
    PlotGroup for Projection Plots
    """

    def __init__(self,simulator,template,plot_group_key,sheet_filter_lam,plot_list,**params):
       
        self.weight_name = plot_group_key[1]
        self.density = float(plot_group_key[2])

        # JABALERT: Should probably rename this because there is a shape in PlotGroup also.
        self.shape = (0,0)
	self.situate = False

        super(ProjectionPlotGroup,self).__init__(simulator,template,plot_group_key,sheet_filter_lam,
                                                   plot_list,**params)

	### JCALERT! It is a bit confusing, but in the case of the projection
        ### sheet_filter_lam filter to one single sheet...
	for s in self.simulator.objects(Sheet).values():
	    if self.sheet_filter_lam(s):
		self._sim_ep = s

        self._sim_ep_src = self._sim_ep.get_in_projection_by_name(self.weight_name)[0].src

 
    def create_plots(self,pt_name,pt,sheet):

	### JCALERT This has to be solved: projection is a list here!
        ### for the moment the hack below deal with that.
        ### Also, why do we pass the template here?	
        projection = sheet.get_in_projection_by_name(pt['Projection_name'])
        plot_list=[]
        if projection:
	    src_sheet=projection[0].src
	    projection=projection[0]

	    coords = self._generate_coords()
	    for x,y in coords:
		plot_channels = pt
		### JCALERT! Do the test pt['Strength']='Weights' here
		key = ('Weights',sheet.name,projection.name,x,y)
		plot_channels['Strength'] = key
		plot_list.append(make_plot(plot_channels,src_sheet.sheet_view_dict,
                                      src_sheet.density,src_sheet.bounds,pt['Normalize'],self.situate))
		
        return plot_list

    ### JCALERT! Try to move that in projectionpanel...?
    def _generate_coords(self):
        """
        Evenly space out the units within the sheet bounding box, so
        that it doesn't matter which corner the measurements start
        from.  A 4 unit grid needs 5 segments.  List is in left-to-right,
        from top-to-bottom.
        """
        def rev(x): y = x; y.reverse(); return y
        
        aarect = self._sim_ep.bounds.aarect()
        (l,b,r,t) = aarect.lbrt()
        x = float(r - l) 
        y = float(t - b)
        x_step = x / (int(x * self.density) + 1)
        y_step = y / (int(y * self.density) + 1)
        l = l + x_step
        b = b + y_step
        coords = []
        self.shape = (int(x * self.density), int(y * self.density))
        for j in rev(range(self.shape[1])):
            for i in range(self.shape[0]):
                coords.append((x_step*i + l, y_step*j + b))

        return coords

    ### JCALERT! Should disappear (see alert in PlotGroup)
    def do_plot_cmd(self):
        coords = self._generate_coords()
	for x,y in coords:
	    self._sim_ep.unit_view(x,y)
        

    ### JCALERT ! for the moment this function is re-implemented only for ProjectionGroup
    ### because we do not want the plots to be sorted according to their src_name in this case
    def plots(self):
        """
        Generate the bitmap lists.
        """            
        bitmap_list = []
      
	self.debug('Dynamic plotgroup')
	self.all_plots = flatten(self.plot_list()) + self.added_list
	self.debug('all_plots = ' + str(self.all_plots))

        generated_bitmap_list = [each for each in self.all_plots if each !=None]
        return generated_bitmap_list


