"""
Plot and PlotTemplate classes. Plot creates the 3 matrices necessary
for plotting, from a three-tuple (channels) and a dictionnary of SheetViews.

The channels specified the key to find the SheetViews that have to be retrieved
for getting the 3 matrices necessary for plotting a RGB images. 

The plot objects are listed within a PlotGroup Class which then arranges
multiple plots into a single figure in a PlotGroupPanel.

Associated with this single (constructed) box of information are multiple histograms that
are stored within the base plot object. (Not yet implemented)

$Id$
"""
__version__='$Revision$'


### JCALERT!
### 
### The code in this file is still being reviewed, and may still need
### substantial changes. Particularly, the doc has to be reviewed.

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
# RGB = 'RGB'
# HSV = 'HSV'
# SHC = 'HSV'  # For now treat as an HSV, but reorder the channels.
# COLORMAP = 'COLORMAP'





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

 
    ### JCALERT! Pass the content of a template instead of channels.

    def __init__(self,(channel_1, channel_2, channel_3),sheet_view_dict,
                 normalize=False, **params):
        """
        channel_1, channel_2, and channel_3 all have one of two types:
        It is either a key that points to a stored SheetView on the
        variable sheet, or
        It is a SheetView object.

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

      	self.view_dict = sheet_view_dict

        self.channels = (channel_1, channel_2, channel_3)

        self.view_info = {}
        self.cropped = False
        self.histograms = []
        self.channel_views = []
        self.matrices = []           # Will finally hold 3 2D matrices.
        self.normalize = normalize

        if self.view_dict == None:
            raise ValueError("A Plot should be passed a sheet_view_dict when created")
  

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

	    #### JCALERT! To fix now that it is a dictionnary that is passed...
            # if isinstance(each,str) or isinstance(each,tuple):
#                     self.view_dict.release_sheet_view(each)
            ### JC: it works like that view_dict is the same pointer than sheet_view_dict!
	    del self.view_dict[each]


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

	### JC: commented out now that we pass a dict instead of a sheet.
      #   self.debug('plot() channels = ' + str(self.channels) + \
#                    'self.view_dict = ' + repr(self.view_dict) + \
#                    'type(self.source) = ' + str(type(self.source)))

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

# 	if isinstance(self.channels[0],SheetView):
# 	    ### Then this function will go away.
# 	    self.get_channels_view_from_sheet_view()
# 	else:

	self.get_channels_view_from_sheet()

        ### JABALERT! Need to document what this code does.

        ### JCALERT! The code below can be made clearer.
        ### Especially, the passing None in channel_views can be changed.
	### Also, this can be put in another function...
            
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


        ### JCALERT! This function ought to be in Plot rather than bitmap.py
        self.matrices = matrix_hsv_to_rgb(hue,sat,val)

        return self


    def get_channels_view_from_sheet(self):
    
        for each in self.channels:
            
            if each == None:
                self.channel_views.append(None)
                
            ### JCALERT! This test has to be re-defined (Why Tuple?)
            elif isinstance(each,str) or isinstance(each,tuple):
		### JCALERT! We could got rid of look_up_dict in sheet.py and use
		### .get(key,None) instead?
                # sv = look_up_dict(self.view_dict,each)
                # that can be turned into: (Ask Jim)
		sv = self.view_dict.get(each, None)
                if sv == None:
		    ### JC: disabled momentarily. Can be spared now I think.
                    #self.debug('No sheet view named ' + repr(each) + ' in Sheet_dict ' + repr(self.view_dict))
                    self.channel_views.append(None)
                else:
		   
		    ### temporary debug
		    #print "sv",sv,sv.view_info

		    self.channel_views.append(sv)

                        ### JCALERT ! That has to be changed.
                        ### JCALERT ! This is an hack so that the problem of displaying the right
                        ### name under each map in activity and orientation map panel is solved
                        ### It has to be changed so that it display what we want for each panel
		        ### Also I think the name that is displayed should always be the plot_name
		    
		    ### JCALERT! To fix now that this is a dictionnary being passed
		    ### But it works fine with the vie_info['src_name'] apparently...
		    # could be:
		    self.view_info = sv.view_info
		  #   self.view_info['src_name']  = sv.view_info['src_name']
#                     self.view_info['view_type'] = sv.view_info['view_type']
                

### JC: if we keep the concept of having list of sheet_view in the sheet_view_dict (for projection, and also, 
### then an idea is to have a special function in the case of a list that return a list of 
### Plots instead of a Plot. But I think it is not good idea anyway to have a list in the sheet_view_dict.              
### JCALERT! The histograms should be implemented and an object histograms assign to a Plot()
