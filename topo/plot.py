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
import types

from base import TopoObject
from sheetview import *
from bitmap import matrix_rgb_to_hsv

# Types of plots that Plot knows how to piece together from the input
# matrices.
RGB = 'RGB'
HSV = 'HSV'
COLORMAP = 'COLORMAP'

# Shape of the plotting display used by PlotGroup.  NOTE: INCOMPLETE,
# THERE SHOULD BE MORE TYPES OF SHAPES SUCH AS SPECIFYING X ROWS, OR Y
# COLUMNS, OR GIVING A LIST OF INTEGERS REPRESENTING NUMBER OF PLOTS
# FOR EACH ROW.  Proposed format:  If three columns are desired with the
# plots laid out from left to right, then use (None, 3).  If three rows
# are desired then (3, None).  Or more interesting, [3,2,4] would have
# the first row with 3, the second row with 2, the third row with 4, etc.
FLAT = 'FLAT'

class Plot(TopoObject):
    """
    Class that maintains information on constructing a single matrix
    from one or more SheetViews that has Histogram information, and
    the whole unit can be clustered with PlotGroups to have multiple
    plots within a single bitmap on the screen.
    """

    def __init__(self, (channel_1, channel_2, channel_3), plot_type, sheet=None, **params):
        """
        sheet gives the object that the three channels will come from
        in generation of the bitmap.

        channel_1, channel_2, and channel_3 all have one of two types:
        It is either a string that points to a stored SheetView on the
        variable sheet, or
        It is a SheetView object that has already been constructed.

        If each of the channels are preconstructed SheetViews, there
        is no reason to pass in the sheet, and therefore it can be
        left blank.

        Named parameter name is being inherited from TopoObject

        WHAT ABOUT BOUNDINGREGIONS?
        """
        super(Plot,self).__init__(**params)
        self.source = sheet
        self.channels = (channel_1, channel_2, channel_3)
        self.plot_type = plot_type
        self.histograms = []
        self.plot_pending = False
        self.channel_views = []
        self.matrices = None         # Will hold 3 2D matrices.


    def plot(self):
        """
        Get the Views requested from each Channel, Generates
        Histograms
        Returns: 2-Tuple, (tri-tuple of 2D Matrix mapping to
        R/G/B channels, List of Histograms)
        """

        #  Convert what is in the channels into SheetViews if not already
        for each in self.channels:
            if isinstance(each,str):
                sv = self.source.sheet_view(each)
                if sv:
                    self.channel_views.append(sv)
            elif isinstance(each,SheetView):
                self.channel_views.append(each)
            elif each == None:
                self.channel_views.append(each)
            else:
                self.warning(each, 'not a valid string, SheetView, or None')

        # NOTE:  THIS NEEDS TO BE CHANGED WHEN BOUNDINGBOXES ARE
        # IMPLEMENTED TO TRIM DOWN THE SIZES OF THE MATRICES!
        shape = [each.shape for each in self.channel_views if not None]
        for each in self.channel_views:
            if each == None:
                self.matrices.append(Numeric.array(shape[0]))
            else:
                self.matrices.append(each[0])

        # By this point, self.matrices should have a triple of 2D
        # matrices trimmed and ready to go to the caller of this
        # function ... after a possible conversion to a different
        # palette form.

        if self.plot_type == HSV:
            # Do the RGB-->HSV conversion, assume the caller will be
            # displaying the plot as an RGB.
            self.matrices = bitmap.matrix_rgb_to_hsv(self.matrices)
        elif self.plot_type == COLORMAP:
            # Don't delete anything, maybe they want position #3, but
            # do warn them if they have more than one channel requested.
            single_map = [each for each in self.channels if each]
            if len(single_map) > 1:
                self.warning('More than one channel requested for single-channel colormap')
        elif self.plot_type == RGB:
            #  Do nothing, we're already in the RGB form.
            #  Possibly change the order to make it match the Lissom order.
            None
        else:
            self.warning('Unrecognized plot type')

        # Construct a list of Histogram objects from the matrices that have
        # been created and are waiting to go.
        self.histograms = [Hisogram(each) for each in self.matrices if each]
        
        return (self.matrices, self.histograms)



class PlotGroup(TopoObject):
    """
    Container that has one or more Plots and also knows how to arrange
    the plots and other special parameters.  Works with the bitmap
    display mechanisms to create a matrix that the caller can dump to
    a topo.Bitmap object 
    """

    def __init__(self,plot_list,shape=FLAT,**params):
        """
        plot_list has the plots to add to this group. 

        Shape gives the visual arrangement of the plots within the group.
        The default is FLAT (None) with each subsequent plot to the right
        of the last.
        TO BE IMPLEMENTED:  (None, 5) will have 5 columns of plots,
        (5, None) will have 5 rows of of plots.  An X-tuple will have
        each subsequent row the length of the corresponding value in
        the tuple.
        """
        super(PlotGroup,self).__init__(**params)
        self.plot_list = plot_list
        self.shape = shape
        self.plot_list = []


    def add(self,new_plot):
        """
        new_plot can be a single Plot, or it can be a list of plots.
        Either way, it will be properly appended to the end of self's
        plot_list.
        """
        if isinstance(new_plot,types.ListType):
            self.plot_list.extend(new_plot)
        else:
            new_plot = self.plot_list.append(new_plot)


    def plot(self):
        """
        Get the matrix data from each of the Plot objects and paste
        the data into a larger matrix.
        """
        big_matrix = None
        # TBI
        # TBI
        return big_matrix





# No Main code.  All testing takes place in the unit testing mechanism
# to be found in ~/topographica/tests/testplot.py
    
    
