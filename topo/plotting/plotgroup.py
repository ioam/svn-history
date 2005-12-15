"""
PlotGroups are containers of Plots that store specific information
about different plot types.  Specifically, a PlotGroup contains the
do_plot_cmd() function that knows how to generate plots.  All
information in these classes must be medium independent.  That is to
say, the bitmaps produced by the groups of plots should be as easily
displayed in a GUI window, as saved to a file.

$Id$
"""
__version__='$Revision$'

### JABHACKALERT!
### 
### The code in this file has not yet been reviewed, and may need
### substantial changes.


import types
from topo.base.topoobject import TopoObject
from topo.base.utils import flatten, dict_sort
from topo.base.sheet import Sheet
import bitmap

import topo
import MLab
from itertools import chain
from Numeric import transpose, array, ravel



from plot import Plot
from topo.base.connectionfield import CFSheet
from topo.base.sheetview import SheetView


# Shape of the plotting display used by PlotGroup.  NOTE: INCOMPLETE,
# THERE SHOULD BE MORE TYPES OF SHAPES SUCH AS SPECIFYING X ROWS, OR Y
# COLUMNS, OR GIVING A LIST OF INTEGERS REPRESENTING NUMBER OF PLOTS
# FOR EACH ROW.  Proposed format: If three columns are desired with
# the plots laid out from left to right, then use (None, 3).  If three
# rows are desired then (3, None).  Another method that would work is
# [3,2,4] would have the first row with 3, the second row with 2, the
# third row with 4, etc.  A key should be used to represent (None, INF)
# or somesuch.
FLAT = 'FLAT'

def sort_plots(plot_list):
    """ This a simple routine to sort a plot list according to their src_name"""
    plot_list.sort(lambda x, y: cmp(x.view_info['src_name'], y.view_info['src_name']))


### JCALERT! This file has been largely modified so that now, each PlotGroup creates
### its plot_list itself, instead of the PlotEngine doing it. The PlotEngine only
### creates and stores the PlotGroup in this new version of the code.It is the first version
### and it still remains job to be done for clarifying and improving it.
### Nevertheless, a lot of the current problem are notified by a JCALERT, and most of the
### remaining job will be to clarify the way Plots are created both in this file and in plot.py
### (also clarifying bitmap.py, plotfilesaver.py and the plotgrouppanel sub-classes at the same time)


class PlotGroup(TopoObject):
    """
    Container that has one or more Plots and also knows how to arrange
    the plots and other special parameters.
    """

    ### JCALERT: 
    ### - plot_list may disappear. For that we need to work on the special case of inputparampanel.
    ### - re-arranged the order and look at the call in all panel classes (i.e. inputparampanel)
    ### also review the doc of each functions.
    ### - rewrite the test file.

    def __init__(self,simulator,template,plot_group_key,sheet_filter_lam=None,plot_list=None,shape=FLAT,**params):
        """
        plot_list can be of two types: 
        1.  A list of Plot objects that can return bitmaps when requested.
        2.  Can also be a function that returns a list of plots so
        that each time plot() is called, an updated list is created for the
        latest list of sheets in the simulation.
        """
        super(PlotGroup,self).__init__(**params)        
        self.plot_list = plot_list
        self.all_plots = []
        self.added_list = []
        
        ### JCALERT! It has to redefined what self.shape is for. 
        self.shape = shape
        self.plot_group_key = plot_group_key
        self.bitmaps = []
        self.template = template

        ### JCALERT! Because of that, we might be able to get rid of some line about the filter
        ###      in the plotengine file. (To do)  
	### Also: do we leave the possibility here to pass a string. In this case, change it in plot_engine?
        if sheet_filter_lam:
	    if isinstance(sheet_filter_lam,str):
		self.sheet_filter_lam = lambda s: s.name == sheet_filter_lam
	    else:
		self.sheet_filter_lam = sheet_filter_lam
        else:
            self.sheet_filter_lam = lambda s : True

        self.debug('Input type, ', type(self.plot_list))

	self.simulator = simulator

	### JC: We do not call initialize_plot_list from the super class because we want the possibility
        ### to create PlotGroup object from plot_list already built (cf InputParamPanel)

    ### JCALERT! we might want this function to be private.
    def initialize_plot_list(self):
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
        
        plot_list = []

        for each in sheet_list:
	   
            for (pt_name,pt) in self.template.plot_templates:
		plot_list= plot_list+ self.create_plots(pt_name,pt,each)
                
	return plot_list

    ###JCALERT! We may want to implement a create_plots in the PlotGroup class
    ### Ask Jim about that.
    def create_plots(self):
        """This function need to be re-implemented in the subclass."""
        
	raise NotImplementedError
    

    ### JABHACKALERT!
    ###
    ### Shouldn't this raise NotImplementedError instead of passing?
    ### If implementing it is required, not optional, then it must.

    ### JCALERT! it is not clear what this function is doing anyway, or the name
    ### should be changed or it should be spared. (To do)
    ### That would require a re-organization of the way Plot are created in the sub-PlotGroup

    def do_plot_cmd(self):
        """
        Command called when plots need to be generated.
        
        Subclasses of PlotGroup will need to create this function.
        """
        pass
    

    ### JABHACKALERT!  There is no apparent reason why this code
    ### should be constructing any bitmaps here.  The Plot should be
    ### able to return a Bitmap (e.g. using a function bitmap(), and
    ### the type of that Bitmap might be anything (RGBBitmap,
    ### HSVBitmap, etc., rather than RGBBitmap as assumed here).
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
            (r,g,b) = each.rgb_matrices
            
            # CEBHACKALERT:
            # when scale is 0, r is an array of zeros but g and b are None
            if g==None or b==None:
                g=r
                b=r
            
            if r.shape != (0,0) and g.shape != (0,0) and b.shape != (0,0):
                # Crop activity to a maximum of 1.  Will scale brighter
                # or darker, depending.
                #
                # Should report that cropping took place.
                #
                ### JCALERT! It should be 1.0, and anyway, it is already supposed to be done in plot...?
                if max(ravel(r)) > 0: r = MLab.clip(r,0.0,1.0)
                if max(ravel(g)) > 0: g = MLab.clip(g,0.0,1.0)
                if max(ravel(b)) > 0: b = MLab.clip(b,0.0,1.0)

                # Indirect test for NaN.  (Since NaN == NaN is False)
                if not (max(ravel(r)) <= 1 and max(ravel(g)) <= 1 and max(ravel(b)) <= 1):
                    self.warning('%s plot contains (%f %f %f)'
                                 % (each.view_info, max(ravel(r)), max(ravel(g)), max(ravel(b))))

                win = bitmap.RGBMap(r, g, b)
                win.view_info = each.view_info
               
                self.bitmaps.append(win)
        return self.bitmaps
    

    
    def add(self,new_plot):
        """
        new_plot can be a single Plot, or it can be a list of plots.
        Either way, it will be properly added to the end of self.plot_list.
        """
        if isinstance(new_plot,types.ListType):
            if not isinstance(self.plot_list,types.ListType):
                self.warning('Adding to PlotGroup that uses dynamic plotlist')
            self.added_list.extend(new_plot)
        else:
            self.added_list.append(new_plot)


    ### JCALERT ! It has to be redefined how this function release_sheet_view() works
    ### here but also in sheet and connectionfield.

    def release_sheetviews(self):
        """
        Call release_sheetviews() on all Plots in plot list, to free
        up Sheet.sheet_view_dict entries and save memory.  Note, not
        all plots use SheetViews stored in a Sheet dictionary.
        """
        for each in self.all_plots:
            each.release_sheetviews()


    ### JCALERT! The call to this function is done when we want the list.
    ### so there is no need to explicitly call it from outside if not to use this list
    ### (see the do_plot_cmd in most of the PlotGroupPanels).     
    def plots(self):
        """
        Generate the bitmap lists.
        """
        bitmap_list = []

	### JCALERT: now it is (almost) always a dynamic list (except the call from InputParamPanel..., 
        ### that could be changed for it to be a static list ? (Ask Jim)
        ### (It would require an explicit call to initialize_plot_list instead of the use of plot_list(),
        ### in this case, the create_plots for the super-class will just be pass?)
        if isinstance(self.plot_list,types.ListType):
            self.debug('Static plotgroup')
            self.all_plots = flatten(self.plot_list) + self.added_list
        else:       # Assume it's a callable object that returns a list.
            self.debug('Dynamic plotgroup')
            self.all_plots = flatten(self.plot_list()) + self.added_list
            self.debug('all_plots = ' + str(self.all_plots))

	### JCALERT! I don't understand this comment. I think it can go:
        # Eventually a simple list comprehension is not going to be
        # sufficient as outlining and other things will need to be
        # done to each of the matrices that come in from the Plot
        # objects.
        
	### JCALERT! Instead of testing each.rgb_matrices != (None,None,None)
        ### Catch the exeption raised for empty plots...
        generated_bitmap_list = [each for each in self.all_plots if (each.rgb_matrices != (None,None,None))]
        
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

    ### JCALERT! See what to do for the default value (sheet_filter_lam =None, plot_list=None)
    def __init__(self,simulator,template,plot_group_key,sheet_filter_lam,plot_list,**params):
        super(BasicPlotGroup,self).__init__(simulator,template,plot_group_key,sheet_filter_lam,plot_list,
                                            **params)


        ### JC: for basic PlotGroup, no need to create a "dynamic List"
        ### even we could get rid of this dynamic list and systematically call
        ### plots() before load_images (cf plotgrouppanel)?(cf JCALERT in plots() above)
	self.plot_list = self.initialize_plot_list()


    def create_plots(self,pt_name,pt,sheet):
	
	plot_channels = {}
	
	plot_channels['Strength'] = pt.channels.get('Strength',None)
        plot_channels['Hue'] = pt.channels.get('Hue',None)
        plot_channels['Confidence'] = pt.channels.get('Confidence',None)
        n = pt.channels.get('Normalize',False)
	plot_name = '\n'+pt_name
        p = Plot(plot_channels,sheet.sheet_view_dict,sheet.density,sheet.bounds,n,name=plot_name)
	return [p]

	

class UnitWeightsPlotGroup(PlotGroup):
    """
    PlotGroup for Weights UnitViews
    """

    def __init__(self,simulator,template,plot_group_key,sheet_filter_lam,plot_list,**params):
        super(UnitWeightsPlotGroup,self).__init__(simulator,template,plot_group_key,sheet_filter_lam,plot_list,
                                              **params)
        self.x = float(plot_group_key[2])
        self.y = float(plot_group_key[3])

        # Decides wether the plots of the UnitWeightPlotGroup are situated or not
        # Its value is depending on the Situate button defined in CFSheetPlotPanel.
      	self.situate = False
        
	### JCALERT! I am not sure we need something dynamic here.
        ### (cf similar alert in BasicPlotGroup.
	self.plot_list = lambda: self.initialize_plot_list()

  
    def create_plots(self,pt_name,pt,sheet):

	plot_list = []
        if not isinstance(sheet,CFSheet):
            self.warning('Requested weights view from other than CFSheet.')
        else:
            for p in set(flatten(sheet.in_projections.values())):	
		### JCALERT! This has to be clarified somewhere: the sheet_view for a 
		### weight belongs to the src_sheet, and the name in the key
                ### is the destination sheet.
	        plot_channels = {}
	        plot_channels['Strength'] = pt.channels.get('Strength',None)
                plot_channels['Hue'] = pt.channels.get('Hue',None)
                plot_channels['Confidence'] = pt.channels.get('Confidence',None)

	        ### JCALERT! do the plot_channels['Strength'] == 'weights' test
                ### here and in projectionplotgroup
                key = ('Weights',sheet.name,p.name,self.x,self.y)
		plot_name = '\n(from ' + p.src.name +')'
		plot_channels['Strength'] = key			       
		plot_list.append(Plot(plot_channels,p.src.sheet_view_dict,p.src.density,
				      p.src.bounds,pt.channels['Normalize'],self.situate,name=plot_name))

        self.debug('plot_list =' + str(plot_list))
        return plot_list

	
    ### JCALERT! I am not sure this function is of any use here, it should be put in another place...
    ### or, change the name of it so that it is clearer when called for the PlotGroupPanels
    def do_plot_cmd(self):
        """
        Lambda function passed in, that will filter out all sheets
        except the one with the name being looked for.
        """
        sheets = self.simulator.objects(Sheet).values()
        for each in sheets:
            if self.sheet_filter_lam(each):
		### JCALERT! It is confusing that the method unit_view is only defined in the 
                ### CFSheet class, and that we are supposed to manipulate sheets here.
		### also, it is supposed to return a view, but here it is used as a procedure.
                each.unit_view(self.x,self.y)


   
class ProjectionPlotGroup(PlotGroup):
    """
    PlotGroup for Projection Plots
    """

    def __init__(self,simulator,template,plot_group_key,sheet_filter_lam,plot_list,**params):
        super(ProjectionPlotGroup,self).__init__(simulator,template,plot_group_key,sheet_filter_lam,
                                                   plot_list,**params)
        self.weight_name = plot_group_key[1]
        self.density = float(plot_group_key[2])
        self.shape = (0,0)
        self._sim_ep = [s for s in self.simulator.objects(Sheet).values()
                        if self.sheet_filter_lam(s)][0]
        self._sim_ep_src = self._sim_ep.get_in_projection_by_name(self.weight_name)[0].src

        # Decides wether the plots of the ProjectionPlotGroup are situated or not
        # Its value is depending on the Situate button defined in CFSheetPlotPanel.
        self.situate = False
        
	self.plot_list = lambda: self.initialize_plot_list()
      
 
    def create_plots(self,pt_name,pt,sheet):

	### JCALERT This has to be solved: projection is a list here!
        ### for the moment the hack below deal with that.
        ### Also, why do we pass the template here?
	
        projection = sheet.get_in_projection_by_name(pt.channels['Projection_name'])
        plot_list=[]
        if projection:
	    src_sheet=projection[0].src
	    projection=projection[0]
	         
	    ### JCALERT! for the moment, the sheet_view for a projection is a list of UnitView
            ### This has to be changed, and so it is a temporary hack.
            ### Finally, it won't be possible to pass a sheet_view directly when creating a Plot

            #views = src_sheet.sheet_view_dict.get(key,None)
	    ### JCALERT! replace that by an attribute view_list in ProjectionPlotGroup
            ### no need to create a sheet_view that contains a list...!!
	    for view in self.view_list:
		plot_channels = {}
		plot_channels['Strength'] = pt.channels.get('Strength',None)
		plot_channels['Hue'] = pt.channels.get('Hue',None)
	        plot_channels['Confidence'] = pt.channels.get('Confidence',None)     
		key = ('Weights',sheet.name,projection.name,view.view_info['x'],view.view_info['y'])
		plot_channels['Strength'] = key
		plot_list.append(Plot(plot_channels,src_sheet.sheet_view_dict,
                                      src_sheet.density,src_sheet.bounds,pt.channels['Normalize'],self.situate))
		
        return plot_list


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


    def do_plot_cmd(self):
        coords = self._generate_coords()
        
        full_unitview_list = [self._sim_ep.unit_view(x,y) for (x,y) in coords]

	### JCALERT! The use of chain and nested list here and in 
        ### connectionfield.py (unit_view) can be spared or made simpler.

        self.view_list = [view for view in chain(*full_unitview_list)
                         if view.projection.name == self.weight_name]


    ### JCALERT ! for the moment this function is re-implemented only for ProjectionGroup
    ### because we do not want the plots to be sorted according to their src_name in this case
    def plots(self):
        """
        Generate the bitmap lists.
        """            
        bitmap_list = []
        if isinstance(self.plot_list,types.ListType):
            self.debug('Static plotgroup')
            self.all_plots = flatten(self.plot_list) + self.added_list
        else:       # Assume it's a callable object that returns a list.
            self.debug('Dynamic plotgroup')
            self.all_plots = flatten(self.plot_list()) + self.added_list
            self.debug('all_plots = ' + str(self.all_plots))

        # Eventually a simple list comprehension is not going to be
        # sufficient as outlining and other things will need to be
        # done to each of the matrices that come in from the Plot
        # objects.
	### JCALERT! Instead of testing each.rgb_matrices != (None,None,None)
        ### Catch the exeption risen for empty plots...
        generated_bitmap_list = [each for each in self.all_plots if (each.rgb_matrices != (None,None,None))]
        return [each for each in generated_bitmap_list if each is not None]


