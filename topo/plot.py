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

# Types of plots that Plot knows how to piece together from the input
# matrices.
RGB = 'RGB'
HSV = 'HSV'
CMAP = 'COLORMAP'

# Shape of the plotting display used by PlotGroup.  NOTE: INCOMPLETE,
# THERE SHOULD BE MORE TYPES OF SHAPES SUCH AS SPECIFYING X ROWS, OR Y
# COLUMNS, OR GIVING A LIST OF INTEGERS REPRESENTING NUMBER OF PLOTS
# FOR EACH ROW.
FLAT = 'FLAT'

class Plot(TopoObject):
    """
    Class that maintains information on constructing a single matrix
    from one or more SheetViews that has Histogram information, and
    the whole unit can be clustered with PlotGroups to have multiple
    plots within a single bitmap on the screen.
    """

    def __init__(self, sheet_tuple_list=None, **params):
        """
        sheet_tuple_list has tuples of the sheet and the name of the
        sheet to be retrieved.  Ex: [(Eye0,Activity),(Eye1,Activity)]
        The default is None, which means all existing sheets in the known
        universe that has a View filed under the key entered with
        generate_plot(key_name).

        Named parameter name is being inherited from TopoObject

        __init__ does not generate the plot instead you must also call
        generate_plot.  This is done in case the measurement causes a
        change in the Sheet providing the View.

        What about BoundingRegions?
        """
        super(Plot,self).__init__(**params)
        self.sheet_tuples = sheet_tuple_list
        self.op = operation
        self.histograms = []
        self.plot_pending = False
        self.matrix = None


    def plot(self):
        """
        Uses the cached plot, or regenerate if needed.
        Return: 2-Tuple, (Calculated Matrix, List of Histograms)
        """
        if not self.plot_pending:
            generate_plot()
        return (self.matrix, self.histograms)


    def generate(self,key_name='Activity'):
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
                sheet_view = None
                #NYI
        else:
            #  Do the global name check against the key_name
            sheet_view = None
            #NYI



class PlotGroup(TopoObject):
    """
    Container that has one or more Plots and also knows how to arrange
    the plots and other special parameters.  Works with the bitmap
    display mechanisms.
    """

    def __init__(self, sheet_tuple_list=None, shape=FLAT, **params):
        """
        sheet_tuple_list has tuples of the sheet and the name of the
        sheet to be retrieved.  Ex: [(Eye0,Activity),(Eye1,Activity)]
        The default is None, which means all existing sheets in the
        known universe that have a View filed under the key entered
        with generate_plot(key_name).

        Shape gives the visual arrangement of the plots within the group.
        The default is FLAT (None) with each subsequent plot to the right
        of the last.
        TO BE IMPLEMENTED:  (None, 5) will have 5 columns of plots,
        (5, None) will have 5 rows of of plots.  An X-tuple will have
        each subsequent row the length of the corresponding value in
        the tuple.

        __init__ does not generate the plot instead you must also call
        generate_plot.  This is done in case the measurement causes a
        change in the Sheet providing the View.

        What about BoundingRegions?
        """
        super(PlotGroup,self).__init__(**params)
        self.sheet_tuples = sheet_tuple_list
        self.shape = shape
        self.plot_pending = False
        self.plot_list = []


    def plot(self):
        """
        Uses the cached plot, or regenerate if needed.
        Return: 2-Tuple, (Calculated Matrix, List of Histograms)
        """
        if not self.plot_pending:
            generate_plot()
        return (self.matrix, self.histograms)


    def generate_plot(self,key_name='Activity'):
        """
        If sheet_tuple_list is empty at object creation, all Sheets
        are checked for the View filed under key_name (default is
        Activity).
        """
        if self.sheet_tuples:
            for (sheet, view_name) in self.sheet_tuples:
                # Do something with the Plot objects.
                x = 1
                #NYI
        else:
            x = 1
            #  Do the global name check against the key_name
            #NYI




# No Main code.  All testing takes place in the unit testing mechanism
# to be found in ~/topographica/tests/testplot.py
    
    
