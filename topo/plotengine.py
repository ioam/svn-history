"""
Construct PlotGroups, Plots, and the occasional SheetView, and give it to
the GUI to display or save at it wants.

This class is the connector to Simulation

$Id$
"""
from base import TopoObject
from plot import Plot
from plot import PlotGroup

class PlotEngine(TopoObject):
    """
    Stores the main list of plots available to the simulation.  There are
    some default plot types such as Activity.
    """

    def __init__(self, simulation, **params):
        """
        Create a new plot engine that is linked to a particular
        simulation.  The link is necessary since the PlotEngine will
        poll all the event processors in the simulation to request
        Plots from the Sheet objects.  This allows new Plot objects to
        automatically appear on previously defined figures.

        Example calling style:
            s = Simulation(step=1)
            new_plot_engine = PlotEngine(s)
        QUESTION: PUT A REFERENCE TO PLOT ENGINE WITHIN SIMULATION?
        """
        super(PlotEngine,self).__init__(**params)
        self.simulation = simulation_name
        self.plot_group_dict = {}


    def _sheets(self):
        """
        Get the list of sheets from the event processor list on the
        local Simulation.
        """
        return self.simulation.get_event_processors()


    def add_plot_group(self, name, group):
        """
        Add a constructed PlotGroup to the local dictionary for later
        reuse.
        """
        self.plot_group_dict[name] = group


    def get_plot_group(self, name):
        """
        Return the PlotGroup registered in self.plot_group_dict with
        the provided 'name'.  If the name does not exist, then generate
        a PlotGroup using the generic dynamic group creator.

        GENERATED PLOTGROUPS WILL POLL ALL SHEETS; NO PARAMETER BASED
        DEFAULT SHEET GROUPS ARE CURRENTLY IMPLEMENTED BUT IT WOULD BE THE
        BEST SOLUTION.
        """
        self.plot_group_dict.setdefault(name,self._get_sheet_view_plot_group(name,self._sheets()))
        

    def _get_sheet_view_plot_group(self, name, filter_lam):
        """
        Default method of creating a plot such as Activity.  Creates
        a new PlotGroup with a lambda function to poll the latest
        and greatest SheetView with 'name' from each sheet in 'sheets',
        using the filter_lambda to choose on inclusion of the sheet.
        """
        None

