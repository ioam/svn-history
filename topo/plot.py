"""
Base Plot environment that manipulates SheetViews and has Histogram information

A plot contains information about one or more SheetViews that it combines
to create a single matrix that can be displayed as a bitmap.  Associated with
this single (costructed) box of information are multiple histograms that
are stored within the base plot object.

The plot objects are generally clustered together within a PlotGroup Class
which arranges multiple plots into a single figure on the screen.

$Id$
"""
import sys

from base import TopoObject
from sheetview import *

ADD      = 0
SUBTRACT = 1
MULTIPLY = 2
DIVIDE   = 3
AVERAGE  = 4
RGB      = 5
HSV      = 7
MASK     = 8

class Plot(TopoObject):
    """
    Class that maintains information on constructing a single matrix
    from one or more SheetViews that has Histogram information, and
    the whole unit can be clustered with PlotGroups to have multiple
    plots within a single bitmap on the screen.
    """

    def __init__(self, sheet_tuple_list=None, operation=ADD, cache=True, **params):
        """
        sheet_tuple_list has tuples of the sheet and the name of the
        sheet to be retrieved.  Ex: [(Eye0,Activity),(Eye1,Activity)]
        The default is None, which means all existing sheets in the known
        universe that has a View filed under the key entered with
        generate_plot(key_name).

        operation, by default, will ADD multiple SheetViews together if
        sheet_tuple_list has more than one entry.

        When the plot has caching enabled subsequent calls to plot() will
        return the same data with no new calculations taking place.  If
        set to false, every call to plot will get new SheetViews which
        may change the simulation state depending on the type of views
        being requested.  Default is True.

        Named parameter name is being inherited from TopoObject

        __init__ does not generate the plot instead you must also call
        generate_plot.  This is done in case the measurement causes a
        change in the Sheet providing the View.
        """
        super(Plot,self).__init__(**params)
        self.sheet_tuples = sheet_tuple_list
        self.op = operation
        self.histograms = []
        self.do_caching = cache
        self.plot_pending = False
        self.matrix = None


    def plot(self):
        """
        Uses the cached plot, or regenerate if needed.
        Return: 2-Tuple, (Calculated Matrix, List of Histograms)
        """
        if not self.plot_pending:
            generate_plot()
        if not self.do_caching:
            self.plot_pending = False
        return (self.matrix, self.histograms)


    def clear_cache(self):
        """Flush the cache so the next plot will be fresh."""
        self.plot_pending = False
        

    def generate_plot(self,key_name='Activity'):
        """
        Poll each Sheet in the tuple list and get the Views requested,
        then combine as specified by self.op.  Generates Histograms
        and caches the data for the next plot() request.

        If sheet_tuple_list is empty at object creation, all Sheets
        are checked for the View filed under key_name (default is
        Activity).
        """
        if self.sheet_tuples:
            for (sheet, view_name) in self.sheet_tuples:
                sheet_view = None  #TBC
        else:
            #  Do the global name check against the key_name
            sheet_view = None  # TBC


# No Main code.  All testing takes place in the unit testing mechanism
# in ~/topographica/tests/testplot.py
    
    
