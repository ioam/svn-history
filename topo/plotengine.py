"""
Construct PlotGroups, Plots, and the occasional SheetView, and give it to
the GUI to display or save at it wants.

This class is the connector to Simulation

$Id$
"""
from plot import Plot
from plot import PlotGroup
from topo import base

class PlotEngine(base.TopoObject):
    """
    Stores the main list of plots available to the simulation.  There are
    some default plot types such as Activity.
    """

    def __init__(self, simulation):
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
        self.simulation = simulation_name
        self.figures = []

    
        
