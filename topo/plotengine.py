"""
Construct PlotGroups, Plots, and the occasional SheetView, for saving to a
file or for a GUI to display.

This class should be the connection between the Simulator or GUI, and
any Plot generation routines.

PlotEngine will create the requeted plot group type from a plot_key
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
from copy import deepcopy
from base import TopoObject
from utils import flatten
from plot import Plot, SHC
from plotgroup import *
from sheet import Sheet
from cfsheet import CFSheet


# Global repository of templates that can be added as necessary.
global plot_templates
global plotgroup_templates
plot_templates = {}
plotgroup_templates = {}


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
    some default plot types such as 'Activation'.  Use this interface when
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
            new_plot_engine = topo.plotengine.PlotEngine(s)
        """
        super(PlotEngine,self).__init__(**params)
        self.simulation = simulation
        self.plot_group_dict = {}


    def _sheets(self):
        """
        Get the list of sheets from the event processor list attached
        to the local Simulation.
        """
        sheet_list = [each for each in self.simulation.get_event_processors()
                      if isinstance(each,Sheet)]
        return sheet_list


    def add_plot_group(self, name, group):
        """
        Add a constructed PlotGroup to the local dictionary for later
        reuse.  User defined plots should be stored here for later use.
        """
        self.plot_group_dict[name] = group


    def get_plot_group(self, name, group_type = 'BasicPlotGroup',filter=sheet_filter):
        """
        Return the PlotGroup registered in self.plot_group_dict with
        the provided key 'name'.  If the name does not exist, then
        generate a PlotGroup using the generic dynamic group creator.
        This default construction allows for certain types of plots to
        be defined automatically, such as 'Activation'.  If a SheetView
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
            self.debug(name, "key match failure in PlotEngine's PlotGroup list")
            # Rather than fail, check for SheetViews of the name.
            # Current filter is sheet_filter(..).
            requested_plot = self.make_plot_group(name,group_type,filter)
        return requested_plot


    def lambda_single_view_per_name(self, name, filter_lam):
        """
        Basic lambda function that assumes a single sheet per name in
        each Sheet's SheetView dictionary.
        """
        dynamic_list = lambda : [Plot((name,None,None),COLORMAP,each)
                                 for each in self._sheets() if filter_lam(each)]
        return dynamic_list


    def lambda_flat_dynamic_list(self, name, filter_lam):
        """
        lambda_single_view_per_name() expanded so that the a
        sheet_view dictionary key entry can have a list of SheetViews,
        and not just one.  Each SheetView in the list will be set with
        a Plot object.
        """
        sheet_list = [each for each in self._sheets() if filter_lam(each)]
        self.debug('sheet_list =' + str(sheet_list) + 'name = ' + str(name))

        view_list = [(each, each.sheet_view(name)) for each in sheet_list
                     if each is not None]
        
        ### A possible list from the Sheet.sheet_view dictionary is
        ### converted into multiple Plot generation requests.
        plot_list = []
        for (sheet,views) in view_list:
            if not isinstance(views,list):
                views = [views]
            for each in views:
                if isinstance(each,SheetView):
                    plot_list.append(Plot((each,None,None),COLORMAP,None))
                else:
                    plot_list.append(Plot((name,None,None),COLORMAP,sheet))
        self.debug('plot_list =' + str(plot_list))
        return plot_list


    def lambda_for_weight_view(self, (w,sheet_target,sheet_x,sheet_y), filter_lam):
        """
        To have the UnitViews stored on the Projection source sheet,
        the weights must be requested from each Projection on the
        target sheets.
        """
        sheet_list = [each for each in self._sheets() if filter_lam(each) and each.name == sheet_target]

        projection_list = []
        for s in sheet_list:
            if not isinstance(s,CFSheet):
                self.warning('Requested weights view from other than CFSheet.')
            else:
                for p in set(flatten(s.projections.values())):
                    key = ('Weights',sheet_target,p.name,sheet_x,sheet_y)
                    v = p.src.sheet_view(key)
                    if v: projection_list += [(s,p,each) for each in v if each.projection.name == p.name]
        projection_list.sort(key=lambda x: x[2].name,reverse=True)

        plot_list = []
        for (sheet,projection,views) in projection_list:
            if not isinstance(views,list):
                views = [views]
            for each in views:
                if isinstance(each,SheetView):
                    plot_list.append(Plot((each,None,None),COLORMAP,None))
                else:
                    key = ('Weights',sheet,projection,sheet_x,sheet_y)
                    plot_list.append(Plot((key,None,None),COLORMAP,p.src))
        self.debug('plot_list =' + str(plot_list))
        return plot_list


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
        sheet_list = [each for each in self._sheets() if filter_lam(each)]
        # Loop over all sheets that passed the filter.
        #     Loop over each individual PlotTemplate:
        #         Loop over each channel in the Plot.  Add needed Nones.
        #         Create new Plot and add to list.
        plot_list = []
        for each in sheet_list:
            for (k,pt) in template.plot_templates:
                c = pt.channels
                if 'Strength' in c or 'Hue' in c or 'Confidence' in c:
                    plot_list.append(self.make_SHC_plot(k,pt,each))
                else:
                    self.warning("Only SHC plots currently implemented.")
        return plot_list


    def make_SHC_plot(self, k, pt, sheet):
        """
        Create and return a single Plot object matching the passed in
        PlotTemplate (parameter 'pt'), using the Sheet (parameter 'sheet').
        """
        strength = pt.channels.get('Strength',None)
        hue = pt.channels.get('Hue',None)
        confidence = pt.channels.get('Confidence',None)
        p = Plot((strength,hue,confidence),SHC,sheet,name=k)
        return p

    def make_plot_group(self, name='Activation', group_type='BasicPlotGroup',
                             filter_lam=sheet_filter):
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
            new_group = BasicPlotGroup('None',filter_lam,dynamic_list)
            # Just copying the pointer.  Not currently sure if we want to
            # promote side-effects by not doing a deepcopy(), but assuming
            # we do for now.  If not, use deepcopy(group_type).
            new_group.template = group_type 
            self.add_plot_group(name,new_group)
        else:
            if isinstance(name,tuple) and name[0] == 'Weights':
                dynamic_list = lambda : self.lambda_for_weight_view(name,filter_lam)
            else:
                dynamic_list = lambda : self.lambda_flat_dynamic_list(name,filter_lam)
            try:
                exec 'ptr = ' + group_type in globals()
            except Exception, e:
                self.warning('Exception:', e)
                self.warning('Invalid PlotGroup subclass: ', group_type)
                return PlotGroup(dynamic_list)
            new_group = ptr(name,filter_lam,dynamic_list)

        self.debug('Type of new_group is', type(new_group))
        return new_group

####################


# Populate the dynamic plot menu list registry:
if __name__ != '__main__':
    pgt = PlotGroupTemplate([('Activity',
                              PlotTemplate({'Strength'   : 'Activation',
                                            'Hue'        : None,
                                            'Confidence' : None}))],
                            name='Activity')
    plotgroup_templates[pgt.name] = pgt
    pgt = PlotGroupTemplate([('ActivationPref',
                              PlotTemplate({'Strength'   : 'Activation',
                                            'Hue'        : 'Activation',
                                            'Confidence' : 'Activation'}))],
                            name='Activity HSV')
    plotgroup_templates[pgt.name] = pgt
