"""
Base Plot environment that manipulates SheetViews and has Histogram information

A plot contains information about one or more SheetViews that it combines
to create a single matrix that can be displayed as a bitmap.  Associated with
this single (constructed) box of information are multiple histograms that
are stored within the base plot object.

The plot objects are generally clustered together within a PlotGroup Class
which arranges multiple plots into a single figure on the screen.

$Id$
"""
import sys
import types

from Numeric import zeros, ones

from base import TopoObject, flatten
from sheetview import *
from bitmap import matrix_hsv_to_rgb, WHITE_BACKGROUND, BLACK_BACKGROUND
from histogram import Histogram
from params import Dynamic
import palette

# Types of plots that Plot knows how to create from input matrices.
RGB = 'RGB'
HSV = 'HSV'
COLORMAP = 'COLORMAP'

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

class Plot(TopoObject):
    """
    Class that maintains information on constructing a single matrix
    from one or more SheetViews that has Histogram information, and
    the whole unit can be clustered with PlotGroups to have multiple
    plots within a single window on the screen.
    """
    background = Dynamic(default=BLACK_BACKGROUND)
    palette_ = Dynamic(default=palette.Monochrome)

    def __init__(self, (channel_1, channel_2, channel_3), plot_type, sheet=None, **params):
        """
        channel_1, channel_2, and channel_3 all have one of two types:
        It is either a key that points to a stored SheetView on the
        variable sheet, or
        It is a SheetView object.

        sheet gives the object that the three channels will request
        SheetViews from if a String has been passed in.

        If each of the channels are preconstructed SheetViews, there
        is no reason to pass in the sheet, and therefore it can be
        left blank.

        Named parameter 'name' is being inherited from TopoObject

        WHAT ABOUT BOUNDINGREGIONS?
        """
        super(Plot,self).__init__(**params)
        self.source = sheet
        self.channels = (channel_1, channel_2, channel_3)
        self.plot_type = plot_type
        self.histograms = []
        self.channel_views = []
        self.matrices = []         # Will hold 3 2D matrices.


    def plot(self):
        """
        Get the SheetViews requested from each channel passed in at
        creation, combines them as necessary, and generates the
        Histograms.
        Returns: 2-Tuple, (triple of 2D Matrices mapping to the
        R/G/B channels, List of Histograms)
        """

        self.debug('plot() channels = ' + str(self.channels) + 'self.source = ' + str(self.source) + 'type(self.source) = ' + str(type(self.source)))

        #  Convert what is in the channels into SheetViews if not already
        for each in self.channels:

            # It's possible for Plots to be accidentally passed in a
            # list of SheetViews, but it should be avoided.  A warning
            # will be displayed and the first one in the list will be
            # used.
            if isinstance(each,list) and len(each) > 0:
                if len(each) > 1:
                    self.warning('Plot Channel contains multiple entries, only plotting first: ' + str(each))
                    each = each[0]

            # Case 1: Simple SheetView with the view already embedded.
            #         No need for a Sheet.
            if isinstance(each,SheetView):
                self.channel_views.append(each)

            # Case 2: Entry is a string, or tuple that will be used as a
            #         key in the Sheet dictionary.
            elif isinstance(each,str) or isinstance(each,tuple):
                if self.source is None:
                    self.warning('Plot Channel-type requires a Sheet, but None Sheet passed to Plot() object.')
                    self.warning('channels = ' + str(self.channels) + ' type(self.source) = ' + str(type(self.source)))
                    self.channel_views.append(None)
                else:
                    sv = self.source.sheet_view(each)
                    self.channel_views.append(sv)

            # Case 3: Channel entry is None.  Pass along.
            elif each == None:
                self.channel_views.append(each)

            # Case 4: Undefined.
            else:
                self.warning(each, 'not a String, Tuple, SheetView, or None')

        # NOTE: THIS NEEDS TO BE CHANGED WHEN BOUNDINGBOXES ARE
        # IMPLEMENTED TO TRIM DOWN THE SIZES OF THE MATRICES! 
        # CURRENTLY ASSUMES THAT ALL SUBVIEWS WILL BE OF THE SAME
        # SHAPE.
        shape = (0,0)
        self.debug('self.channel_views = ' + str(self.channel_views))
        for each in self.channel_views:
            if each != None:
                view_matrix = each.view()
                self.matrices.append(view_matrix[0]) # Discards boundingbox
                shape = view_matrix[0].shape
            else:
                self.matrices.append(None)
        # Replace any Nones with a matrix of size 'shape' full of values.
        if self.background == BLACK_BACKGROUND:
            self.matrices = tuple([each or zeros(shape) for each in self.matrices])
        else:
            self.matrices = tuple([each or ones(shape) for each in self.matrices])
            

        # By this point, self.matrices should be a triple of 2D
        # matrices trimmed and ready to go to the caller of this
        # function ... after a possible conversion to a different
        # palette form.
        if self.plot_type == HSV:
            # Do the HSV-->RGB conversion, assume the caller will be
            # displaying the plot as an RGB.
            h,s,v = self.matrices
            self.matrices = matrix_hsv_to_rgb(h,s,v)

        elif self.plot_type == COLORMAP:
            # Don't delete anything, maybe they want position #3, but
            # do warn them if they have more than one channel
            # requested.
            #
            # COLORMAP NOW GENERATES ONLY A GRAYSCALE IMAGE. WORK
            # NEEDS TO BE DONE TO CHANGE THIS TO A SINGLE-CHANNEL
            # MATRIX THAT TRANSLATES THROUGH A PALETTE OF 256 POSSIBLE
            # COLORS THROUGH THE USE OF ColorMap and Palette.  WILL
            # NEED TO PROBABLY WORK WITH PlotEngine SINCE IT CREATES
            # THE FINAL IMAGES.
            single_map = [each for each in self.matrices if each]
            if len(single_map) > 1:
                self.warning('More than one channel requested for single-channel colormap')
            if single_map:
                self.matrices = (single_map[0], single_map[0], single_map[0])

        elif self.plot_type == RGB:
            # Do nothing, we're already in the RGB form.  Possibly
            # change the order to make it match the Lissom order, OR
            # ADD BLACK_BACKGROUND, WHITE_BACKGROUND COLOR SHIFTS.
            None

        else:
            self.warning('Unrecognized plot type')

        # Construct a list of Histogram objects from the matrices that
        # have been created and are waiting to go.  PROBABLY HAVE TO
        # CHANGE ONCE HISTOGRAM DOES SOMETHING.
        self.histograms = [Histogram(each) for each in self.matrices if each]
        
        return (self.matrices, self.histograms)



class PlotGroup(TopoObject):
    """
    Container that has one or more Plots and also knows how to arrange
    the plots and other special parameters.
    """

    def __init__(self,plot_list,shape=FLAT,**params):
        """
        plot_list can be of two types: 
        1.  A list of Plot objects that will be polled for their bitmaps.
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


    def plots(self):
        """
        Get the matrix data from each of the Plot objects, do any needed
        plot marking, then pass up the list of bitmaps.

        THE GUI IS GOING TO GLUE THE HISTOGRAMS INTO ONE GLORIOUS WHOLE.
        """
        bitmap_list = []
        if isinstance(self.plot_list,types.ListType):
            self.debug('Static plotgroup')
            all_plots = flatten(self.plot_list) + self.added_list
        else:       # Assume it's a callable object that returns a list.
            self.debug('Dynamic plotgroup')
            all_plots = flatten(self.plot_list()) + self.added_list
            self.debug('all_plots = ' + str(all_plots))

        # Eventually a simple list comprehension is not going to be
        # sufficient as outlining and other things will need to be
        # done to each of the matrices that come in from the Plot
        # objects.
        bitmap_list = [each.plot() for each in all_plots]

        return bitmap_list





# No Main code.  All testing takes place in the unit testing mechanism
# to be found in ~/topographica/tests/testplot.py
    
    
