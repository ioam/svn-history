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

from base import TopoObject
from utils import flatten
from sheetview import *
from bitmap import matrix_hsv_to_rgb, WHITE_BACKGROUND, BLACK_BACKGROUND
from histogram import Histogram
from params import Dynamic
import palette

# Types of plots that Plot knows how to create from input matrices.
RGB = 'RGB'
HSV = 'HSV'
COLORMAP = 'COLORMAP'


class PlotTemplate(TopoObject):
    """
    Container class for a plot object definition.  This is separate
    from a Plot object since it defines how to create a Plot object
    and should be contained within a PlotGroupTemplate.  The
    PlotEngine will create the requested plot type given the template
    definition.  The templates are used so that standard plot types
    can be redefined at the users convenience.
    """

    def __init__(self, channels=None, **params):
        super(PlotTemplate,self).__init__(**params)
        self.channels = channels
        


class Plot(TopoObject):
    """
    Class that can construct a single bitmap plot from one or more
    SheetViews, optionally including a Histogram.  The bitmap is just
    stored for future use, e.g. as part of a PlotGroup of related
    plots displayed within one GUI window.
    """
    background = Dynamic(default=BLACK_BACKGROUND)
    palette_ = Dynamic(default=palette.Monochrome)

    def __init__(self, (channel_1, channel_2, channel_3), plot_type, sheet=None, **params):
        """
        channel_1, channel_2, and channel_3 all have one of two types:
        It is either a key that points to a stored SheetView on the
        variable sheet, or
        It is a SheetView object.

        plot_type has three options: HSV, COLORMAP, or RGB.  HSV plots
        will be converted to an RGB matrix triple.  COLORMAPs take in
        a single channel, since each pixel should be a single value,
        that should be selected from a palette.  RGB plots are
        three-channel plots that are not mixed together like HSV,
        since it is assumed the GUI display will be in RGB.

        sheet gives the object that the three channels will request
        SheetViews from if a String has been passed in.  Valid options
        are: None, Single Sheet, 3-tuple of Sheets or None.

        TODO: TRIPLE IS CURRENTLY NOT IMPLEMENTED.  THIS REQUIRES
        THAT ALL CHANNELS DERIVE FROM THE SAME SHEET.  SHOULD EXTEND
        self.source SO THAT DIFFERENT SHEET INPUTS ARE POSSIBLE (7/2005)

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
        self.view_info = {}
        self.histograms = []
        self.channel_views = []
        self.matrices = []         # Will hold 3 2D matrices.


    def shape(self):
        """ Return the shape of the first matrix in the Plot """
        return self.matrices[0].shape


    def release_sheetviews(self):
        """
        Delete any Sheet.sheet_view_dict entries used by this plot, under
        the assumption that this Plot is the only object that references
        the SheetView on the Sheet with that dictionary key.
        """
        for each in self.channels:
            # Case 2 is the only time a Sheet holds a SheetView that needs
            # to be deleted.
            if isinstance(each,str) or isinstance(each,tuple):
                if self.source is None:
                    self.warning('Plot Channel-type requires a Sheet, but None Sheet passed to Plot() object.')
                    self.warning('channels = ' + str(self.channels) + ' type(self.source) = ' + str(type(self.source)))
                else:
                    self.source.release_sheet_view(each)


    def plot(self):
        """
        Get the SheetViews requested from each channel passed in at
        creation, combines them as necessary, and generates the
        Histograms.  plot() is here to allow dynamic creation of plots,
        even after the creation of the Plot object.  See the input
        parameters to the Plot object constructor.
        
        Returns: self (Plot)
            Important features of this object are:
                self.matrices: Triple of 2D Matrices mapping to the
                    R/G/B channels.
                self.histograms: List of Histogram objects associated with
                    the matrices is self.matrices.
                self.view_info: Name information that can be used to create
                    labels and filenames.
        """

        self.debug('plot() channels = ' + str(self.channels) + \
                   'self.source = ' + str(self.source) + \
                   'type(self.source) = ' + str(type(self.source)))

        self.channel_views = []
        self.matrices = []
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
                self.view_info = each.view_info

            # Case 2: Entry is a string, or tuple that will be used as a
            #         key in the Sheet dictionary.
            elif isinstance(each,str) or isinstance(each,tuple):
                if self.source is None:
                    self.warning('Plot Channel-type requires a Sheet, '+ \
                                 'but None Sheet passed to Plot() object.')
                    self.warning('channels = ' + str(self.channels) + \
                                 ' type(self.source) = ' + \
                                 str(type(self.source)))
                    self.channel_views.append(None)
                    self.name = 'Undefined'
                else:
                    sv = self.source.sheet_view(each)
                    self.channel_views.append(sv)
                    self.view_info = sv.view_info

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
            self.matrices = tuple([each or zeros(shape)
                                  for each in self.matrices])
        else:
            self.matrices = tuple([each or ones(shape)
                                  for each in self.matrices])
            

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
                self.warning('More than one channel requested for ' + \
                             'single-channel colormap')
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
        
        return self



class SCCPlot(Plot):
    """
    Special type of HSV Plot.

    Color      -> Hue
    Strength   -> Saturation
    Confidence -> Value
    """
    def __init__(self, (channel_1, channel_2, channel_3),
                 sheet=None, **params):
        super(SCCPlot,self).__init__((channel_1, channel_2, channel_3),
                                     HSV, sheet=sheet, **params)






# No Main code.  All testing takes place in the unit testing mechanism
# to be found in ~/topographica/tests/testplot.py
    
    
