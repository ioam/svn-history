"""
Plot and PlotTemplate classes. 

Plot creates the 3 matrices necessary for plotting a RGB image, 
from a three-tuple (channels) and a dictionnary of SheetViews.

The channels specify the key to find the SheetViews that have to be retrieved
for this purpose. 

The plot objects are listed within a PlotGroup Class which then arranges
multiple plots into a single figure in a PlotGroupPanel.

Associated with this single (constructed) box of information are multiple histograms that
are stored within the base plot object. (Not yet implemented.)

$Id$
"""
__version__='$Revision$'


### JCALERT!
### 
### The code in this file is still being reviewed, and may still need
### substantial changes. Particularly, the doc has to be reviewed.

### JCALERT! Are these 3 import statements really used?
import sys
import types
import MLab

### JC: I think it can go, to check:
from topo.base.sheetview import *

from Numeric import zeros, ones, Float, divide
from topo.base.topoobject import TopoObject
from bitmap import matrix_hsv_to_rgb, WHITE_BACKGROUND, BLACK_BACKGROUND
from topo.base.parameter import Dynamic
import palette as palette 

### JC: I think it can go...
from Numeric import array

### JCALERT! WHAT about histograms? (ask Jim) 
#from histogram import Histogram 

### JCALERT! The histograms should be implemented and an object histograms assign to a Plot() 
### WHAT does bitmap really mean here? (ask Jim and review the doc) 
    
class Plot(TopoObject):
    """
    Class that constructs a bitmap plot from one or more
    SheetViews (optionally including a Histogram).  The bitmap is just
    stored for future use, e.g. as part of a PlotGroup of related
    plots displayed within one GUI window.
    """
    background = Dynamic(default=BLACK_BACKGROUND)
    palette_ = Dynamic(default=palette.Monochrome)

 
    ### JCALERT! - Pass the content of a template instead of channels?
    ### Or pass a list of three tuples? To be fixed with Jim.
    ### Also: - put normalize in PlotGroup?

    def __init__(self,(channel_1, channel_2, channel_3),sheet_view_dict,
                 normalize=False, **params):
        """
        (channel_1, channel_2, channel_3) are keys that point to a stored 
        SheetView in sheet_view_dict, as specified in a PlotTemplate.
        None is also possible if the Plot is only built from one or two
        SheetViews.

	sheet_view_dict is a dictionary of SheetViews, generally belonging 
        to a Sheet object but not necessarily.

	normalize specified is the Plot is normalized or not.
        
        a 'name' parameter is inherited from TopoObject.
           
        TODO: implement the possibility to pass more than three 
        SheetView keys for more complicated plots (12/01/05)
        """   
        ### JCALERT! That was in the doc: WHAT ABOUT BOUNDINGREGIONS?
        ### Is it important? (Ask Jim)

        super(Plot,self).__init__(**params)

      	self.view_dict = sheet_view_dict
        self.channels = (channel_1, channel_2, channel_3)

	### JC: maybe we can use the parameter name instead of having a view_info?
        self.view_info = {}

        self.cropped = False
        self.histograms = []

        self.matrices = []              # Will finally hold 3 matrices (or more?)
        self.normalize = normalize

        if self.view_dict == None:
            raise ValueError("A Plot should be passed a sheet_view_dict when created")

	### JCALERT! maybe also raise something when channels are all None? 

    ### JCALERT! Actually, this function can be used this way.
    ### It is called from release_sheetviews in PlotGroup and enable to
    ### free memory space when we don't need the SheetViews entry anymore.
    def release_sheetviews(self):
        """
        Delete any sheet_view_dict entries used by this plot, under
        the assumption that this Plot is the only object that use the 
        the SheetView in the sheet_view_dict  with that dictionary key.
        """
        for each in self.channels:
	    del self.view_dict[each]



    # JC: This function is called by load_images in PlotGroup and sub-classes.  
    ### Maybe it should just be called from __init__ ?             
    def plot(self):
        """
        Get the SheetViews requested from each channel passed in at
        creation, combines them as necessary, (and generates the
        Histograms, not yet implemented).  plot() is here to allow dynamic creation of plots,
        even after the creation of the Plot object. 
            
        Returns: self (Plot)

        Important features of this object are:

	   self.matrices: Triple of Matrices mapping to the
	                  R/G/B channels.
           self.view_info: Name information that can be used to create
                           labels and filenames.
           (self.histograms: List of Histogram objects associated with
                    the matrices is self.matrices. NOT YET IMPLEMENTED)           
        """

	self._get_matrices_from_view_dict()

	### JCALERT ! The name should be changed...
	hsv_matrices = self._make_hsv_matrices()

	### JCALERT! Think about mae_hsv_matrices beeing a procedure
        ### directly working on self.matrices and change matrix_hsv_to_rgb to
        ### take a list of matrices or tuple of matrices. 
	if hsv_matrices == None:
	    ### JCALERT! Why are there empty plot when doing orientation map?
            ### This should maybe not returned None in this case?
            ### It should come from the PlotGroup that looks into all sheets in the simulator
	    ### even the Retina...
	    #print("Empty Plot")
	    return None
	else:
	    (hue,sat,val)= hsv_matrices

	     ### JCALERT! This function ought to be in Plot rather than bitmap.py
	    self.matrices = matrix_hsv_to_rgb(hue,sat,val)
	    return self


    def _get_matrices_from_view_dict(self):
        """
	sub-function of plot() that just retrieve the views from the view_dict
	as specified by the channels, and create its matrices attribute accordingly 
	(list of view matrices from SheetView.view() ).

	(It just deals with the fact that channels can be None, or that the keys
	specified by channels can potentially refer to no SheetViews in the dict).
        """  
	self.matrices=[]
        for each in self.channels:
	    ### JCALERT! Presumably, if each == None then there is no key equal to None in the 
            ### dict and then sv==None. Ask Jim if it is alright, because it is always possible that
            ### some mad man has done dict[None]=who_knows_what ?
	    sv = self.view_dict.get(each, None)
	    if sv == None:
		self.matrices.append(None)
	    else:
		view_matrix = sv.view()
		self.matrices.append(view_matrix[0]) # discard boudingbox  

	    ### JCALERT ! This is an hack so that the problem of displaying the right
	    ### name under each map in activity and orientation map panel is solved
	    ### It has to be changed so that it display what we want for each panel
	    ### Also I think the name that is displayed should always be the plot name
            ### (Also see in create_plots for each PlotGroup sub-classes)
            ### This should not be in this function at all	
		self.view_info['src_name'] = sv.view_info['src_name'] + self.name
		self.view_info['view_type'] = sv.view_info['view_type']


    ### JCALERT! The doc has to be reviewed (as well as the code by the way...)
    ### The function should be made as a procedure working on self.matrices directly...
    def _make_hsv_matrices(self):
	""" 
	Sub-function that return the h,s,v matrices corresponding to
        self.matrices,
        also applying normalizing of the plot if required.
	"""
	shape=(0,0)
	for mat in self.matrices:
	    if mat != None:
		shape = mat.shape

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

	
	return (hue,sat,val)

	
   
