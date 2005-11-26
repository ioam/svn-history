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
from topo.base.keyedlist import KeyedList
from topo.base.sheet import Sheet
import bitmap

import topo
import topo.base.simulator
import topo.base.registry
import MLab
from itertools import chain
from Numeric import transpose, array

from topo.base.parameter import Parameter

from plot import Plot, SHC,HSV,RGB,COLORMAP
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


class PlotGroupTemplate(TopoObject):
    """
    Container class for a PlotGroup object definition.  This is
    separate from a PlotGroup object since it defines how to create a
    PlotGroup object and should contain a series of PlotTemplates.
    The PlotEngine will create the requested plot group type given a
    group template definition.  The templates are used so that
    standard plot types can be redefined at the users convenience.

    The plot_templates member dictionary (KeyedList) can and should be
    accessed directly by outside code.  It is a KeyedList (defined in
    this file) so it can be treated like a dictionary using the []
    notation, but it will preserve ordering.  An example definition:

    pgt = PlotGroupTemplate([('ActivityPref',
                              PlotTemplate({'Strength'   : 'Activity',
                                            'Hue'        : 'Activity',
                                            'Confidence' : 'Activity'}))],
                            name='Activity SHC')

    to change an entry in the above example:

    pgt.plot_templates['ActivityPref'] = newPlotTemplate
    """


    command = Parameter(None)
    def __init__(self, plot_templates=None, **params):
        """
        plot_templates are of the form:
            ( (name_1, PlotTemplate_1), ... , (name_i, PlotTemplate_i) )
        """


        
        super(PlotGroupTemplate,self).__init__(**params)
        if not plot_templates:
            self.plot_templates = KeyedList()
        else:
            self.plot_templates = KeyedList(plot_templates)
        self.description = self.name
        

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

    ### JCALERT: adding the template in the list of parameter to pass. 
    ###     also add a simulator parameter, that will be passed when creating from the plot_engine.
    ### Also plot_list could disappear.
    ### + I left template=None so that the testPlotGroup does not crash anymore,
    ### that will have to be re moved eventually.
    ### re-arranged the order and look at the call in all panel classes (i.e. inputparampanel)

    def __init__(self,template=None,plot_key=None,sheet_filter_lam=None,plot_list=None,shape=FLAT,**params):
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
        self.shape = shape
        self.plot_key = plot_key
        self.bitmaps = []
        self.template = template

        ### JC: Because of that, we might be able to get rid of some line about the filter
        ###      in the plotengine file.        
        if sheet_filter_lam:
            self.sheet_filter_lam = sheet_filter_lam
        else:
            self.sheet_filter_lam = lambda : True

        self.debug('Input type, ', type(self.plot_list))

        ### JCALERT! for the moment we take the active simulator, but later we might want to 
        ### pass the simulator as a parameter of PlotGroup  
	### so directly put this line into PlotGroup rather than BasicPlotGroup
	self.simulator = topo.base.registry.active_sim()

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

    #def create_plots(self):
    # raise("Method not Implemented for the super class")
    #

    ### JABHACKALERT!
    ###
    ### Shouldn't this raise NotImplementedError instead of passing?
    ### If implementing it is required, not optional, then it must.

    ### JC: it is not clear what this function is doing anyway, or the name
    ### should be changed or it should be spared

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
            (r,g,b) = each.matrices

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
                if max(r.flat) > 0: r = MLab.clip(r,0.0,1.0)
                if max(g.flat) > 0: g = MLab.clip(g,0.0,1.0)
                if max(b.flat) > 0: b = MLab.clip(b,0.0,1.0)

                # Indirect test for NaN.  (Since NaN == NaN is False)
                if not (max(r.flat) <= 1 and max(g.flat) <= 1 and max(b.flat) <= 1):
                    self.warning('%s plot contains (%f %f %f)'
                                 % (each.view_info, max(r.flat), max(g.flat), max(b.flat)))

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


    def release_sheetviews(self):
        """
        Call release_sheetviews() on all Plots in plot list, to free
        up Sheet.sheet_view_dict entries and save memory.  Note, not
        all plots use SheetViews stored in a Sheet dictionary.
        """
        for each in self.all_plots:
            each.release_sheetviews()

    def plots(self):
        """
        Generate the bitmap lists.
        """
        bitmap_list = []
	### JC: now it is always a dynamic list, that could be changed for it to
        ### be a static list but it is probably good like that (Ask Jim)
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
        
        generated_bitmap_list = [each.plot() for each in self.all_plots]
        generated_bitmap_list = [each for each in generated_bitmap_list if each is not None]
        
        ### JCALERT! For each plotgroup, we want the plot to be displayed
        ### in the alphabetical order according to their view_info['src_name']
        ### The only PlotGroup that does not have to do that is the projectionplotgroup
        ### and that is why this function is overwritten
        sort_plots(generated_bitmap_list)
        return generated_bitmap_list
    
  

class BasicPlotGroup(PlotGroup):
    """
    PlotGroup for Activity SheetViews
    """

    def __init__(self,template,plot_key,sheet_filter_lam,plot_list,**params):
        super(BasicPlotGroup,self).__init__(template,plot_key,sheet_filter_lam,plot_list,
                                            **params)

        ### JC for basic PlotGroup, no need to create a "dynamic List"
	self.plot_list = self.initialize_plot_list()

    # default is the basic plot group:
    # should be re-implemented in UnitWeightPlotGroup and ProjectionPlotGroup
    ### JCALERT! maybe simply put that in the above function
    def create_plots(self,pt_name,pt,sheet):
	
	strength = pt.channels.get('Strength',None)
        hue = pt.channels.get('Hue',None)
        confidence = pt.channels.get('Confidence',None)
        n = pt.channels.get('Normalize',False)
        p = Plot((strength,hue,confidence),SHC,sheet,n,name=pt_name)
        return [p]

	

class UnitWeightsPlotGroup(PlotGroup):
    """
    PlotGroup for Weights UnitViews
    """

    def __init__(self,template,plot_key,sheet_filter_lam,plot_list,**params):
        super(UnitWeightsPlotGroup,self).__init__(template,plot_key,sheet_filter_lam,plot_list,
                                              **params)
        self.x = float(plot_key[2])
        self.y = float(plot_key[3])
 
      	
	### JCALERT! I am not sure we need something dynamic here, to check
	self.plot_list = lambda: self.initialize_plot_list()

  
    def create_plots(self,pt_name,pt,sheet):

	### JC: the Sheet_name param ought to be in the plot key and not in the
        ### group template,  as well as the location: 
        ###  Does it has to be changed when working on PlotGroupPanel?
        ### (Passing parameter through the template has to be changed eventually)
        sheet_target = pt.channels['Sheet_name']
        (sheet_x,sheet_y) = pt.channels['Location']

	### JCALERT: here the hue and confidence ought to be taken and used later on
        ### but a first work on plot.py is required to make these changes
        ### hue = pt.channels['Hue']
        ### confidence = pt.channels['Confidence']

        projection_list = []
        if not isinstance(sheet,CFSheet):
            self.warning('Requested weights view from other than CFSheet.')
        else:
            for p in set(flatten(sheet.in_projections.values())):
                key = ('Weights',sheet_target,p.name,sheet_x,sheet_y)
                v = sheet.sheet_view(key)
                if v:
                    projection_list += [(sheet,p,each) for each in v if each.projection.name == p.name]
 
        # HERE IS WHERE WE (NEED TO?) ADD ADDITIONAL SORTING INFORMATION.
	### JCALERT! What does that do?
        projection_list.sort(key=lambda x: x[2].name,reverse=True)

        plot_list = []
        for (a_sheet,projection,views) in projection_list:
            if not isinstance(views,list):
                views = [views]
            for each in views:
                if isinstance(each,SheetView):
		    ### JC: here it needs to be changed: but plot.py also as to be fixed
                    ### e.g. plot_list.append(Plot((each,hue,None),COLORMAP,s,pt.channels['Normalize']))
		    plot_list.append(Plot((each,None,None),COLORMAP,None,pt.channels['Normalize']))
                else:
                    key = ('Weights',a_sheet,projection,sheet_x,sheet_y)
                    plot_list.append(Plot((key,None,None),COLORMAP,p.src,pt.channels['Normalize']))
        self.debug('plot_list =' + str(plot_list))
        return plot_list
	
    ### JCALERT! I am not sure this function is of any use here
    def do_plot_cmd(self):
        """
        Lambda function passed in, that will filter out all sheets
        except the one with the name being looked for.
        """
        sheets = topo.base.registry.active_sim().objects(Sheet).values()
        for each in sheets:
            if self.sheet_filter_lam(each):
		### JCALERT! It is confusing that the method unit_view is defined in the 
                ### class connectionfield that does not inherit from Sheet, and that we are supposed to
                ### manipulate sheets here.
		### also, it is supposed to return a view, but here it is used as a procedure.
                ### (procedure that is applied to a connectionfield and add the unit_view in the 
                ### sheet_view_dict of its source sheet
                each.unit_view(self.x,self.y)

   
class ProjectionPlotGroup(PlotGroup):
    """
    PlotGroup for Projection Plots
    """

    def __init__(self,template,plot_key,sheet_filter_lam,plot_list,**params):
        super(ProjectionPlotGroup,self).__init__(template,plot_key,sheet_filter_lam,
                                                   plot_list,**params)
        self.weight_name = plot_key[1]
        self.density = float(plot_key[2])
        self.shape = (0,0)
        self._sim_ep = [s for s in topo.base.registry.active_sim().objects(Sheet).values()
                        if self.sheet_filter_lam(s)][0]
        self._sim_ep_src = self._sim_ep.get_in_projection_by_name(self.weight_name)[0].src

  
	self.plot_list = lambda: self.initialize_plot_list()
      
 
    def create_plots(self,pt_name,pt,sheet):

        c = pt.channels
        projection = sheet.get_in_projection_by_name(c['Projection_name'])
        if projection:
	    src_sheet=projection[0].src
                   
        ### JC: here the hue and confidence ought to be taken and used later on
        ### but a first work on plot.py is required to make these changes
        ### hue = pt.channels['Hue']
        ### confidence = pt.channels['Confidence']

        ### JC apparently, the template carries the information for building
        ### the plot_key. It might be difficult to change now. (also see make_unit_weights_plot)
	    key = (pt_name,c['Projection_name'],c['Density'],sheet.name)
	    view_list = src_sheet.sheet_view(key)
	    if not isinstance(view_list,list):
		view_list = [view_list]
            
	    plot_list=[]
        ### A list from the Sheet.sheet_view dictionary is
        ### converted into multiple Plot generation requests.

        ### JCALERT! This was and still is boggus: what is name?
        ### It is not worse than before because the bug was already here
        ### Need to be fixed in some way.
	    for each in view_list:
		if isinstance(each,SheetView):
		    plot_list.append(Plot((each,None,None),COLORMAP,None,pt.channels['Normalize']))
		else:
                ### JCALERT! bug from plotengine: name is not defined here.(I think he meant key)
		    plot_list.append(Plot((name,None,None),COLORMAP,sheet,pt.channels['Normalize']))

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
        filtered_list = [view for view in chain(*full_unitview_list)
                         if view.projection.name == self.weight_name]

        self._sim_ep_src.add_sheet_view(self.plot_key,filtered_list)

        ### JCALERT! I do not understand this comment.
        ### We might want to get rid of it

        # This is no longer correct now that the UnitViews are no
        # longer on the Projection target sheet.
        # for (x,y) in coords: self._sim_ep.release_unit_view(x,y)

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
        
        generated_bitmap_list = [each.plot() for each in self.all_plots]
        return [each for each in generated_bitmap_list if each is not None]


### JCALERT! What about putting that in a special file for defining PlotGroupTemplate?
 
# Populate the dynamic plot menu list registry
import topo.base.registry
from plot import PlotTemplate
pgt = PlotGroupTemplate([('Activity',
                          PlotTemplate({'Strength'   : 'Activity',
                                        'Hue'        : 'OrientationPreference',
                                        'Confidence' : None,
                                        'Normalize'  : False}))],
                        name='Activity',
                        command='pass')

# CEBHACKALERT: putting OrientationPreference in Hue is ok while we are only
# talking about orientation maps.

topo.base.registry.plotgroup_templates[pgt.name] = pgt
pgt = PlotGroupTemplate([('Unit Weights',
                          PlotTemplate({'Location'   : (0.0,0.0),
                                        'Normalize'  : True,
                                        'Sheet_name' : 'V1'}))],
                        name='Unit Weights',
                        command='pass')
topo.base.registry.plotgroup_templates[pgt.name] = pgt
pgt = PlotGroupTemplate([('Projection',
                          PlotTemplate({'Density'         : 25,
                                        'Projection_name' : 'None',
                                        'Normalize'       : True}))],
                        name='Projection',
                        command='pass')
topo.base.registry.plotgroup_templates[pgt.name] = pgt
pgt = PlotGroupTemplate([('Orientation Preference',
                          PlotTemplate({'Strength'   : None,
                                        'Hue'        : 'OrientationPreference',
                                        'Confidence' : None})),
                         ('Orientation Preference&Selectivity',
                          PlotTemplate({'Strength'   : None,
                                        'Hue'        : 'OrientationPreference',
                                        'Confidence' : 'OrientationSelectivity'})),
                         ('Orientation Selectivity',
                          PlotTemplate({'Strength'   : 'OrientationSelectivity',
                                        'Hue'        : None,
                                        'Confidence' : None}))],
                        name='Orientation Preference',
                        command = 'measure_or_pref()')
topo.base.registry.plotgroup_templates[pgt.name] = pgt

