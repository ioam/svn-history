"""
Base Plot environment that manipulates SheetViews and has Histogram information

A plot contains information about one or more SheetViews that it combines
to create a single matrix that can be displayed as a bitmap.  Associated with
this single (constructed) box of information are multiple histograms that
are stored within the base plot object.

The plot objects are clustered together within a PlotGroup Class which
arranges multiple plots into a single figure on the screen.

The PlotEngine class uses PlotTemplate objects, embedded within
PlotGroupTemplate objects to create the Plots that will generate the
bitmaps that will be displayed on screen or saved to disk.  A
PlotTemplate is essentially a dictionary of keyed information,
containing sheet names, or channel settings.

Kinds of PlotTemplates:
    SHC Plots:
        Keys:
            Strength   - SheetView dictionary key
            Hue        - SheetView dictionary key
            Confidence - SheetView dictionary key
    Unit Weights Plots:
        Keys:
            Location   - (x,y) tuple
            Sheet_name - Name of sheet to pull unit weights
    Projection Plots:
        Keys:
            Density    - Density to plot projection weights
            Projection_name - Name of projection to plot.  Looks at
                .src sheet_view_dict
            


$Id$
"""
__version__='$Revision$'
### JABHACKALERT!
### 
### The code in this file has not yet been reviewed, and may need
### substantial changes.

import sys
import types

from Numeric import zeros, ones, Float, divide

from topo.base.topoobject import TopoObject
from topo.base.utils import flatten
from topo.base.sheetview import *
from bitmap import matrix_hsv_to_rgb, WHITE_BACKGROUND, BLACK_BACKGROUND
from histogram import Histogram
from topo.base.parameter import Dynamic
from Numeric import array
import palette as palette 
import MLab

### JCALERT: that could go.

# Types of plots that Plot knows how to create from input matrices.
RGB = 'RGB'
HSV = 'HSV'
SHC = 'HSV'  # For now treat as an HSV, but reorder the channels.
COLORMAP = 'COLORMAP'

class PlotTemplate(TopoObject):
    """
    Container class for a plot object definition.  This is separate
    from a Plot object since it defines how to create a Plot object
    and should be contained within a PlotGroupTemplate.  The
    PlotEngine will create the requested plot type given the template
    definition.  The templates are used so that standard plot types
    can be redefined at the users convenience.

    For example, 'Activity' maps are defined as:
    activity_template = PlotTemplate({'Strength'   : 'Activity',
                                      'Hue'        : None,
                                      'Confidence' : None})
    """

    def __init__(self, channels=None,**params):
        super(PlotTemplate,self).__init__(**params)
        #self.background = Dynamic(default=background)
        self.channels = channels
        


### JABHACKALERT!  This class should accept SheetViews, with no
### reference to anything of type Sheet, and no plotting of anything
### else.  It is ridiculously too difficult to understand and maintain
### in its current form.  Any operation that depends on Sheet, such as
### looking up SheetViews by name, or releasing SheetViews, should be
### moved out of it.  PlotTemplate might be able to do such lookup,
### because it's called for every Sheet, but if so it should always
### map consisently from a name string to a SheetView, without trying
### to handle all these special cases.  These classes are trying to be
### way too smart; they should simply plot whatever they are given.
class Plot(TopoObject):
    """
    Class that can construct a single bitmap plot from one or more
    SheetViews, optionally including a Histogram.  The bitmap is just
    stored for future use, e.g. as part of a PlotGroup of related
    plots displayed within one GUI window.
    """
    background = Dynamic(default=BLACK_BACKGROUND)
    palette_ = Dynamic(default=palette.Monochrome)

 
    ### JCALERT! Instead of passing the sheet, we want to pass the dictionnary
    ### it will solve the problem with inputparampanel
    ### but before, I have to solve the problem of the projection that stores
    ### lists of SheetView. (as well as for weights)

    def __init__(self,(channel_1, channel_2, channel_3),sheet,
                 normalize=False, **params):
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
        are: None, Single Sheet, or None.
        TODO: TRIPLE OF SHEETS, ONE FOR EACH CHANNEL, IS CURRENTLY NOT
        IMPLEMENTED.  CURRENT IMPLEMENTATION REQUIRES THAT ALL
        CHANNELS DERIVE FROM THE SAME SHEET.  SHOULD EXTEND
        self.source SO THAT DIFFERENT SHEET INPUTS ARE POSSIBLE
        (7/2005)

        If each of the channels are preconstructed SheetViews, there
        is no reason to pass in the sheet, and therefore it can be
        left blank.

        Named parameter 'name' is being inherited from TopoObject

        WHAT ABOUT BOUNDINGREGIONS?
        """
        super(Plot,self).__init__(**params)

      	self.source = sheet

        self.channels = (channel_1, channel_2, channel_3)

        self.view_info = {}
        self.cropped = False
        self.histograms = []
        self.channel_views = []
        self.matrices = []         # Will hold 3 2D matrices.
        self.normalize = normalize

        if self.source == None:
            raise ValueError("A Plot should be passed a sheet when created")
  

    ### JCALERT! Is it really a useful and meaningful function?
    def shape(self):
        """ Return the shape of the first matrix in the Plot """
        return self.matrices[0].shape


    ### JCALERT! This function should go in another place but not in plot. (I think)
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


    ### JCALERT! This function is called by load_images in PlotGroup
                    
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

        ### JCALERT! I think that can go (already defined above!)
        ### but I do not know why, it lead to a bug with the testpattern window
        ### This has to be fixed.
	self.channel_views = []
        self.matrices = []


	### JCALERT! For the moment, we still need to pass SheetViews directly when plotting
        ### the projection. It is because the plot_key correspond to a list of SheetViews rather than
        ### SheetViews. We might want to change that and only gather all the UnitViews just when
        ### plotting the projection.
        ### (Note: it is also the case for unitweights: the UnitView comes back as a list
        ### which lead to the bad code in the hack below )

	if isinstance(self.channels[0],SheetView):
	    ### Then this function will go away.
	    self.get_channels_view_from_sheet_view()
	else:
	    self.get_channels_view_from_sheet()

        ### JABALERT! Need to document what this code does.

        ### JCALERT! The code below can be made clearer.
        ### Especially, the passing None in channel_views can be changed.
            
        shape = (0,0)
        self.debug('self.channel_views = ' + str(self.channel_views))
               
        for each in self.channel_views:

	    if each != None:
		view_matrix = each.view()
		self.matrices.append(view_matrix[0]) # Discards boundingbox
		shape = view_matrix[0].shape
	    else:
		self.matrices.append(None)


        ### JC: For clarity, this could be another function.
	    
	    # By this point, self.matrices should be a triple of 2D
        # matrices trimmed and ready to go to the caller of this
        # function ... after a possible conversion to a different
        # palette form.
        
	s,h,c = self.matrices

        zero=zeros(shape,Float)
        one=ones(shape,Float)

        ### JABHACKALERT Need to extend for white background; assumes black

        ### JCALERT! This part of the code could go. To see.
        # No plot; in the future should probably not be a warning
        if (s==None and c==None and h==None):
            self.debug('Skipping empty plot.')
            return None

            # Determine appropriate defaults for each matrix
        if s is None: s=one # Treat as full strength by default
        if c is None: c=one # Treat as full confidence by default
        if h is None: # No color -- should be changed to drop down to COLORMAP plot.
            h=zero
            c=zero

        if self.normalize and max(s.flat) > 0:
            s = divide(s,float(max(s.flat)))

        hue=h
        sat=c
        val=s
            
        if max(hue.flat) > 1 or max(sat.flat) > 1 or max(val.flat) > 1:
            self.cropped = True
        #self.warning('Plot: HSVMap inputs exceed 1. Clipping to 1.0')
        if max(hue.flat) > 0: hue = MLab.clip(hue,0.0,1.0)
        if max(sat.flat) > 0: sat = MLab.clip(sat,0.0,1.0)
        if max(val.flat) > 0: val = MLab.clip(val,0.0,1.0)
        else:
            self.cropped = False

        self.matrices = matrix_hsv_to_rgb(hue,sat,val)

        return self


    def get_channels_view_from_sheet(self):
    
        for each in self.channels:
            
            if each == None:
                self.channel_views.append(None)
                
            ### JCALERT! This test has to be re-defined (Why Tuple?)
            elif isinstance(each,str) or isinstance(each,tuple):
                sv = self.source.sheet_view(each)
                if sv == None:
                    self.debug('No sheet view named ' + repr(each) + ' in Sheet ' + self.source.name)
                    self.channel_views.append(None)
                else:
		    ### JCALERT! Hack to deal with the fact that UnitWeights comes in a list:
                    ### It has to be changed in unit_view from connectionfield.py
		    if isinstance(sv,list):
		    	sv=sv[0]
		    ###
		    
		    ### temporary debug
		    #print "sv",sv.view_info
		    self.channel_views.append(sv)

                        ### JCALERT ! That has to be changed.
                        ### JCALERT ! This is an hack so that the problem of displaying the right
                        ### name under each map in activity and orientation map panel is solved
                        ### It has to be changed so that it display what we want for each panel
		        ### Also I think the name that is displayed should always be the plot_name
		    
                    self.view_info['src_name']  = self.source.name +"\n" + sv.view_info['src_name']
                    self.view_info['view_type'] = sv.view_info['view_type']
                
    ### JC: this function will go when the problem of the projection plot will be solved.
    def get_channels_view_from_sheet_view(self):

	for each in self.channels:
	    self.channel_views.append(each)
	    if each != None:
		self.view_info = each.view_info

### JC: if we keep the concept of having list of sheet_view in the sheet_view_dict (for projection, and also, 
### then an idea is to have a special function in the case of a list that return a list of 
### Plots instead of a Plot. But I think it is not good idea anyway to have a list in the sheet_view_dict.              
