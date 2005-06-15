"""
Construct PlotGroups, Plots, and the occasional SheetView, for saving to a
file or for a GUI to display.

This class should be the connection between the Simulator or GUI, and
any Plot generation routines.

Note: get_plot_group() function interface could be cleaned up, since
the lambda functions are a bit confusing, and the user should probably
be protected as much as possible while remaining flexible.  

$Id$
"""
from base import TopoObject
from utils import flatten
from plot import *
from plotgroup import *
from sheet import Sheet


def sheet_filter(sheet):
    """
    Example sheet filter that can be used to limit which sheets are
    displayed through _make_sheetview_group.  Default filter used
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


    def get_plot_group(self, name, group_type = 'BasicPlotGroup',filter=None):
        """
        Return the PlotGroup registered in self.plot_group_dict with
        the provided key 'name'.  If the name does not exist, then
        generate a PlotGroup using the generic dynamic group creator.
        This default construction allows for certain types of plots to
        be defined automatically, such as 'Activation'.
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
            requested_plot = self.make_sheetview_group(name,group_type,filter)
        return requested_plot


    def lambda_single_view_per_name(self,name,filter_lam):
        """
        Basic lambda function that assumes a single sheet per name in
        each Sheet's SheetView dictionary.
        """
        dynamic_list = lambda : [Plot((name,None,None),COLORMAP,each)
                                 for each in self._sheets() if filter_lam(each)]
        return dynamic_list


    def lambda_flat_dynamic_list(self, name, filter_lam):
        """
        Expanded so that the a sheet_view dictionary key entry can
        have a list of sheetviews, and not just one.  Each SheetView
        in the list will be set with a Plot object.
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


    def make_sheetview_group(self, name, group_type='BasicPlotGroup',
                             filter_lam=None):
        """
        name : The key to look under in the SheetView dictionaries.
        group_type: The string name of the PlotGroup subclass to create.
               The actual name is passed in instead of a class pointer
               so the function can be used from the command-line, and
               also so a full list of class names is not required.
        filter_lam: Optional lambda function to filter which sheets to
               ask for SheetViews
        """
        if filter_lam is None:
            filter_lam = lambda sheet: True            
        dynamic_list = lambda : self.lambda_flat_dynamic_list(name,filter_lam)

        # try:
        exec 'ptr = ' + group_type in globals()
        # except Exception, e:
        #     self.warning('Exception:', e)
        #     self.warning('Invalid PlotGroup subclass: ', group_type)
        #     return PlotGroup(dynamic_list)
        new_group = ptr(name,filter_lam,dynamic_list)
        self.debug('Type of new_group is', type(new_group))
        return new_group

