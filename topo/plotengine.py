"""
Construct PlotGroups, Plots, and the occasional SheetView, and give it to
the GUI to display or save at it wants.

This class is the connection between Simulation and the Plot generation
routines.

$Id$
"""
from base import TopoObject
from utils import flatten
from plot import *
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
    else:
        return False


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
        poll all the event processors in the simulation to dynamically
        request Plots from the Sheet objects.  This allows new Plot
        objects to automatically appear in previously defined
        PlotGroups.

        Example calling style:
            s = Simulation(step=1)
            new_plot_engine = PlotEngine(s)
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


    def get_plot_group(self, name, filter=sheet_filter):
        """
        Return the PlotGroup registered in self.plot_group_dict with
        the provided key 'name'.  If the name does not exist, then
        generate a PlotGroup using the generic dynamic group creator.
        This default construction allows for certain types of plots to
        be defined automatically, such as 'Activation'.

        GENERATED PLOTGROUPS WILL POLL ALL SHEETS; NO PARAMETER BASED
        DEFAULT SHEET GROUPS OR FILTERS ARE CURRENTLY IMPLEMENTED BUT
        IT WOULD BE THE BEST SOLUTION.
        """
        if self.plot_group_dict.has_key(name):
            self.debug(name, "key match in PlotEngine's PlotGroup list")
            requested_plot = self.plot_group_dict[name]
        else:
            self.debug(name, "key match failure in PlotEngine's PlotGroup list")
            # Rather than fail, check for SheetViews of the name.
            # Current filter is sheet_filter(..).
            requested_plot = self.make_sheetview_group(name,filter)
        return requested_plot


    def lambda_single_view_per_name(self,name,filter_lam):
        """
        Basic lambda function that assumes a single sheet per name in
        each Sheets SheetView dictionary.
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
                    plot_list.append(Plot((each,None,None),COLORMAP,None,
                                     name = each.name))
                else:
                    plot_list.append(Plot((name,None,None),COLORMAP,sheet,
                                     name = 'Composite'))
        self.debug('plot_list =' + str(plot_list))
        return plot_list


    def make_sheetview_group(self, name, filter_lam=None):
        """
        Default method of creating a dynamic plot such as
        'Activation'.  Makes a new PlotGroup containing a lambda
        function that will poll the latest and greatest list of
        SheetViews with 'name' from each Sheet in the simulation.  It
        uses the filter_lambda to decide if it should include the
        sheet in the Group.  If passed in, filter_lambda must take a
        Sheet, and return True or False.
        """
        if filter_lam is None:
            filter_lam = lambda sheet: True            
        # An alternative is lambda_single_view_per_name(name,filter_lam)
        dynamic_list = lambda : self.lambda_flat_dynamic_list(name,filter_lam)
        new_group = PlotGroup(dynamic_list)
        self.debug('Type of new_group is', type(new_group))
        return new_group

