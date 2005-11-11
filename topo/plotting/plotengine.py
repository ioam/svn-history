"""
Construct PlotGroups, Plots, and the occasional SheetView, for saving to a
file or for a GUI to display.

This class should be the connection between the Simulator or GUI, and
any Plot generation routines.

PlotEngine will create the requested plot group type from a plot_key
(dictionary key name for the SheetView dictionaries on each sheet) or
a plot dictionary definition.

A Plot that contains the old LISSOM style plot information, (in a
different displayed form):

Define PlotGroup HuePreference
    Define Plot HuePref
        Channels:
            Strength   = Null
	    Hue        = HueP   (Predefined SheetView)
	    Confidence = Null
    Define Plot HuePrefAndSel
        Channels:
	    Strength   = HueSel (Predefined SheetView)
	    Hue        = HueP   (Predefined SheetView)
	    Confidence = Null 
    Define Plot HueSelect
        Channels:
	    Strength   = HueSel (Predefined SheetView)
	    Hue	       = Null
	    Confidence = Null

in the new syntax would look like:

    hue_template = PlotGroupTemplate( 
        [('HuePref', PlotTemplate({'Strength'   : None,
                                   'Hue'        : 'HueP',
                                   'Confidence' : None})),
         ('HuePrefAndSel', PlotTemplate({'Strength'   : 'HueSel',  
                                         'Hue'        : 'HueP',
                                         'Confidence' : None})),
         ('HueSelect', PlotTemplate({'Strength'   : 'HueSel',
                                     'Hue'        : None,
                                     'Confidence' : None}))])


NOTE: get_plot_group() function interface could be cleaned up, since
the lambda functions are a bit confusing, and the user should probably
be protected as much as possible while remaining flexible.  

$Id$
"""
### JABHACKALERT!  The documentation above needs substantial
### clarification -- less detail, more sense.


__version__='$Revision$'


from copy import deepcopy
from topo.base.topoobject import TopoObject
from topo.base.utils import flatten, dict_sort
from plot import Plot, SHC,HSV,RGB,COLORMAP
from plotgroup import *
from topo.base.sheet import Sheet
from topo.base.connectionfield import CFSheet
from topo.base.sheetview import SheetView
from topo.base.sheet import Sheet

def sheet_filter(sheet):
    """
    Example sheet filter that can be used to limit which sheets are
    displayed through make_plot_group().  Default filter used
    by the built-in get_plot_group(..) when there is no plot of the
    correct key name in the PlotGroup dictionary.

    SHOULD BE EXPANDED OR REPLACED FOR MORE (ANY?) DEFAULT FUNCTIONALITY
    """
    if sheet == sheet:
        return True


class PlotEngine(TopoObject):
    """
    Stores the main list of plots available to the simulation.  There are
    some default plot types such as 'Activity'.  Use this interface when
    generating plots.
    """

    def __init__(self, simulation, **params):
        """
        Create a new plot engine that is linked to a particular
        simulation.  The link is necessary since the PlotEngine will
        iterate over all the event processors in the simulation,
        requesting Plots from all EPs that are also Sheets.  This
        approach ensures that new Plot objects will show up
        automatically even in previously defined PlotGroups.

        Example calling style:
            s = topo.simulation.Simulation()
            new_plot_engine = plotengine.PlotEngine(s)
        """
        super(PlotEngine,self).__init__(**params)
        self.simulation = simulation
        self.plot_group_dict = {}


    def add_plot_group(self, name, group):
        """
        Add a constructed PlotGroup to the local dictionary for later
        reuse.  User defined plots should be stored here for later use.
        """
        self.plot_group_dict[name] = group

        
    ### JABALERT!  It is strange for this to call make_plot_group;
    ### that call should either be justified or removed.
    def get_plot_group(self, name, group_type = 'BasicPlotGroup',
                       filter=sheet_filter, class_type='BasicPlotGroup'):
        """
        Return the PlotGroup registered in self.plot_group_dict with
        the provided key 'name'.  If the name does not exist, then
        generate a PlotGroup using the generic dynamic group creator.
        This default construction allows for certain types of plots to
        be defined automatically, such as 'Activity'.  If a SheetView
        dictionary entry has a key entry with 'name' then it will be part
        of the new plot.
        """
        if filter == None:
            filter = sheet_filter
        elif isinstance(filter,str):     # Allow sheet string name as input.
            target_string = filter
            filter = lambda s: s.name == target_string
        
        if self.plot_group_dict.has_key(name):
            self.debug(name, "key match in PlotEngine's PlotGroup list")
            requested_plot = self.plot_group_dict[name]
        else:
            # Current filter is sheet_filter(..).
            requested_plot = self.make_plot_group(name,group_type,filter,class_type)
        return requested_plot


    ### JABHACKALERT! This function needs a new name describing what
    ### it actually does, i.e. why anyone would want to use it.  The
    ### documentation needs to be clarified; it doesn't make much sense.
    def lambda_for_templates(self, template, filter_lam):
        """
        This assumes that a PlotGroupTemplate named 'template' has
        been passed in that describes a list of plots.  An example is
        given at the top of plotengine.py.

        It is possible for a requested SheetView to in fact have a
        list of Views under that dictionary key instead of a single
        SheetView.  The default behavior will be to only look at the
        first one and dispose of any others if they exist.
        """
        ### JCHACKALERT! It was necessary here to sort the sheet (with
        ### the function sort_dict so that (and by chance that our
        ### display is currently following the alphabetical order) the
        ### plot are placed in a logical way from left to right
        ### (i.e. LeftRetina, RightRetina, V1, V2 but also Orientation
        ### Preference, Orientation Preference&Selectivity,
        ### Orientation Selectivity).  This has to be changed so that
        ### each classes has a number that roughly determine where we
        ### wants it on the plot (i.e. GeneratorSheet: 5, CFSheet: 50)
        ### Note that the same problem has to be solved for
        ### PatternGenerator in order to determine in which order to
        ### display scale, offset...  
        sheet_list = [each for each in dict_sort(self.simulation.objects(Sheet)) if filter_lam(each)]
        
        # Loop over all sheets that passed the filter.
        #     Loop over each individual PlotTemplate:
        #         Loop over each channel in the Plot.  Add needed Nones.
        #         Create new Plot and add to list.
        plot_list = []
        for each in sheet_list:
            for (k,pt) in template.plot_templates:
                c = pt.channels
                if 'Strength' in c or 'Hue' in c or 'Confidence' in c:     # SHC
                    plot_list.append(self.make_SHC_plot(k,pt,each))
                elif 'Location' in c and 'Sheet_name' in c:                # Unit Weights 
                    if c['Sheet_name'] == each.name:
                        # Multiple Plots can be generated from one Sheet.
                        plot_list = plot_list + self.make_unitweights_plot(k,pt,each)
                elif 'Density' in c and 'Projection_name' in c:            # Projections
                    projection = each.get_in_projection_by_name(c['Projection_name'])
                    if projection:
                        plot_list = plot_list + self.make_projection_plot(k,pt,projection[0].src)
                else:
                    self.warning("Only SHC, Unit Weights, and Projection plots currently implemented.")
        return plot_list

    ### JABALERT! What does this function do?  Needs some documentation.
    def make_projection_plot(self, k, pt, s):
        """
        k is the name of the plot template passed in.
        pt is the PlotTemplate being constructed.
        s is the sheet to request the sheet views from.
            It should be the source of the Projection connection.
        """
        c = pt.channels
        key = (k,c['Projection_name'],c['Density'])
        view_list = s.sheet_view(key)
        if not isinstance(view_list,list):
            view_list = [view_list]
        
        ### A list from the Sheet.sheet_view dictionary is
        ### converted into multiple Plot generation requests.
        plot_list = []
        for each in view_list:
            if isinstance(each,SheetView):
                plot_list.append(Plot((each,None,None),COLORMAP,None,pt.channels['Normalize']))
            else:
                plot_list.append(Plot((name,None,None),COLORMAP,s,pt.channels['Normalize']))
        return plot_list


    ### JABALERT! What does this function do?  Needs some documentation.
    def make_unitweights_plot(self, k, pt, s):
        sheet_target = pt.channels['Sheet_name']
        (sheet_x,sheet_y) = pt.channels['Location']

        projection_list = []
        if not isinstance(s,CFSheet):
            self.warning('Requested weights view from other than CFSheet.')
        else:
            for p in set(flatten(s.in_projections.values())):
                key = ('Weights',sheet_target,p.name,sheet_x,sheet_y)
                v = s.sheet_view(key)
                if v:
                    projection_list += [(s,p,each) for each in v if each.projection.name == p.name]
 
        # HERE IS WHERE WE (NEED TO?) ADD ADDITIONAL SORTING INFORMATION.
        projection_list.sort(key=lambda x: x[2].name,reverse=True)

        plot_list = []
        for (sheet,projection,views) in projection_list:
            if not isinstance(views,list):
                views = [views]
            for each in views:
                if isinstance(each,SheetView):
                    plot_list.append(Plot((each,None,None),COLORMAP,None,pt.channels['Normalize']))
                else:
                    key = ('Weights',sheet,projection,sheet_x,sheet_y)
                    plot_list.append(Plot((key,None,None),COLORMAP,p.src,pt.channels['Normalize']))
        self.debug('plot_list =' + str(plot_list))
        
        ### JCHACKALERT! This is an Hack so that the plot are
        ### appearing in alphabetical order which, luckily,
        ### corresponds to the order we want them to be displayed in
        ### This is something that needs more fixing (also see
        ### PatternGenerators and the JCHACKALERT!  alert above in the
        ### file for similar problem)
        plot_list.sort(reverse=True)
        return plot_list



    ### JABALERT! What does this function do?  Needs some documentation.
    def make_SHC_plot(self, k, pt, sheet):
        """
        Create and return a single Plot object matching the passed in
        PlotTemplate (parameter 'pt'), using the Sheet (parameter 'sheet').
        """
        strength = pt.channels.get('Strength',None)
        hue = pt.channels.get('Hue',None)
        confidence = pt.channels.get('Confidence',None)
        n = pt.channels.get('Normalize',False)
        p = Plot((strength,hue,confidence),SHC,sheet,n,name=k)
        return p


    ### JABALERT! What does this function do?  Needs some documentation.
    def make_plot_group(self, name='None', group_type='BasicPlotGroup',
                             filter_lam=sheet_filter, class_type='BasicPlotGroup'):
        """
        name : The key to look under in the SheetView dictionaries.
        group_type: 2 Valid inputs:
               1. The string name of the PlotGroup subclass to create.
                  The actual name is passed in instead of a class
                  pointer so the function can be used from the
                  command-line, and also so a full list of class names
                  is not required.
               2. If group_type is a PlotGroupTemplate, then the
                  lambda function to handle templates is called.
        filter_lam: Optional lambda function to filter which sheets to
               ask for SheetViews.  
        """
        if isinstance(group_type,PlotGroupTemplate):
            dynamic_list = lambda: self.lambda_for_templates(group_type,filter_lam)
            try:
                exec 'ptr = ' + class_type in globals()
            except Exception, e:
                self.warning('Exception raised:', e)
                self.warning('Invalid PlotGroup subclass: ', group_type)
                return PlotGroup(dynamic_list)
            new_group = ptr(name,filter_lam,dynamic_list)

            # Just copying the pointer.  Not currently sure if we want to
            # promote side-effects by not doing a deepcopy(), but assuming
            # we do for now.  If not, use deepcopy(group_type).
            new_group.template = group_type 
            self.add_plot_group(name,new_group)
        else:
            print 'Template was not passed in.  This code deprecated and disabled.'
            import inspect
            print inspect.stack(), '\n'

        self.debug('Type of new_group is', type(new_group))
        return new_group
