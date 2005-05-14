"""
PlotGroup and subclasses

$Id$
"""
from base import TopoObject
from plot import *

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


class PlotGroup(TopoObject):
    """
    Container that has one or more Plots and also knows how to arrange
    the plots and other special parameters.
    """

    def __init__(self,plot_list,shape=FLAT,**params):
        """
        plot_list can be of two types: 
        1.  A list of Plot objects that can return bitmaps when requested.
        2.  Can also be a function that returns a list of plots so
        that each time plot() is called, an updated list is created for the
        latest list of sheets in the simulation.

        shape recommends the visual arrangement of the plots within
        the group.  The default is FLAT.  PlotGroup does not do the
        final pasting, instead allowing the GUI to do that, but it
        will hold the shape information as needed.  RECOMMENDED
        IMPLEMENTATION: (None, 5) will have 5 columns of plots, (5,
        None) will have 5 rows of of plots.  An X-tuple will have each
        subsequent row the length of the corresponding value in the
        tuple.
        """
        super(PlotGroup,self).__init__(**params)
        self.plot_list = plot_list
        self.all_plots = []
        self.added_list = []
        self.shape = shape
        self.debug('Input type, ', type(self.plot_list))


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
        Get the matrix data from each of the Plot objects, do any needed
        plot marking, then pass up the list of bitmaps.

        THE GUI IS GOING TO GLUE THE HISTOGRAMS INTO ONE GLORIOUS WHOLE.
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

        return generated_bitmap_list
