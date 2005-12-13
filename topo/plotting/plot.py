"""
Plot class.

$Id$
"""
__version__='$Revision$'


### JABALERT: Should this be replaced with Numeric.clip()?
import MLab # Used for MLab.clip()
from Numeric import zeros, ones, Float, divide, ravel

from topo.base.topoobject import TopoObject
from topo.base.parameter import Dynamic
from topo.base.sheet import submatrix, bounds2slice, bounds2shape

from bitmap import matrix_hsv_to_rgb, WHITE_BACKGROUND, BLACK_BACKGROUND
import palette as palette


class Plot(TopoObject):
    """
    Constructs and stores a bitmap from one or more SheetViews.

    The bitmap is then available for future use, e.g. as part of a
    PlotGroup of related plots displayed within one GUI window.

    Plot creates the 3 matrices necessary for plotting a RGB image,
    from a three-tuple (channels) and a dictionary of SheetViews.
    Eventually, plots more complex than simple bitmaps will be
    supported, including overlaid outlines, contours, vector fields,
    histograms, etc., and the overall architecture should be designed
    to make this feasible.
    """
    background = Dynamic(default=BLACK_BACKGROUND)
    palette_ = Dynamic(default=palette.Monochrome)
 
    ### JCALERT!
    ### - Pass the content of a template, as a dictionary, instead of 3 fixed channels.
    ### - Re-write the test file, taking the new changes into account.
    ### - I have to change the order: situated, plot_bb and (normalize)
    ### - There should be a way to associate the density explicitly
    ###   with the sheet_view_dict, because it must match all SheetViews
    ###   in that dictionary.  Maybe as a tuple?
    def __init__(self,(channel_1, channel_2, channel_3),sheet_view_dict,density=None,
                 plot_bounding_box=None,normalize=False,situated=False, **params):
        """
        (channel_1, channel_2, channel_3) are keys that point to a stored 
        SheetView in sheet_view_dict, as specified in a PlotTemplate.
        None is also possible if the Plot is only built from one or two
        SheetViews.

	sheet_view_dict is a dictionary of SheetViews, generally belonging 
        to a Sheet object but not necessarily.

	normalize specified is the Plot is normalized or not.

	density is the density of the sheet that contains the different views
        constituting the plot.

	plot_bounding_box is the outer bounding_box of the plot
        to apply if the plot is situated.  If not situated, the
        bounds of the smallest SheetView are used.
        
	situated specifies if we want to situate the plot, i.e.,
        whether to plot the entire Sheet (or other area specified by
        the plot_bounding_box), or only the smallest plot (usually a
        Weights plot).
        
        name (inherited from TopoObject) specifies the name to use for
        this plot.
        """   
        super(Plot,self).__init__(**params)

      	self.view_dict = sheet_view_dict
        self.channels = (channel_1, channel_2, channel_3)
        self.density = density

	### JCALERT: Fix view_info here, and in SheetView
        self.view_info = {}

        self.cropped = False

        ### JABALERT: Should probably be a dictionary (or, more likely, KeyedList).
	# The list of matrices that constitutes the plot.
        self.matrices = []

        ### JABALERT: Please explain this better, or clean it up.
	# The list of the bounding box of the SheetViews associated with this plot.
        self.box=[]

	# shape (dimension) of the plotting area
        self.shape = (0,0)
	# bounds of the situated plotting area 
	self.plot_bounding_box = plot_bounding_box

        ### JABALERT: Please explain this better.
	# bounds of the sliced area
        self.slicing_box = None

	self.situated = situated
        self.normalize = normalize


    ### JABALERT: This does not seem appropriate -- Plot should not delete
    ### any SheetViews that it did not put there itself.
    def release_sheetviews(self):
        """
        Delete any sheet_view_dict entries used by this plot, under
        the assumption that this Plot is the only object that use the 
        the SheetView in the sheet_view_dict  with that dictionary key.
        """
        for each in self.channels:
	    del self.view_dict[each]


    ### JCALERT: This should just be moved to __init__.
    # JC: This function is called by load_images in PlotGroup and sub-classes.  
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

	### JC: It might be clearer to call:
        ### self.matrices = self._get_matrices_from_view_dict()
	self._get_matrices_from_view_dict()

        ### JCALERT! What if the order is not the same?
        ### Maybe passing a dictionary instead of a triple in the first place?
	s,h,c = self.matrices
        ### JABALERT: When moving this to __init__, may be better to
        ### raise an exception to be caught by the instantiator
        ### instead.
        if (s==None and c==None and h==None):
            self.debug('Skipping empty plot.')
            return None
	else:
	    self._slice_matrices()
	    (hue,sat,val) = self._make_hsv_matrices()	    
            ### JCALERT! This function ought to be in Plot rather than bitmap.py
	    self.matrices = matrix_hsv_to_rgb(hue,sat,val)
	    if self.situated:
		if self.plot_bounding_box == None:
		    raise ValueError("the plot_bounding_box must be specified for situating the plot")
		else:
		    self._situating_plot(self.plot_bounding_box)
		    
	    return self


    def _get_matrices_from_view_dict(self):
        """
	sub-function of plot() that just retrieves the views from the view_dict
	as specified by the channels, and create its matrices attribute accordingly 
	(list of view matrices from SheetView.view() ).

	(It just deals with the fact that channels can be None, or that the keys
	specified by channels can potentially refer to no SheetViews in the dict).
        """  
	self.matrices=[]
        self.box=[]
        for each in self.channels:
            ### Note that this logic will fail if someone happens to
            ### have put an item with the key None into the
            ### dictionary, but that should be unlikely.
	    sv = self.view_dict.get(each, None)
	    if sv == None:
		self.matrices.append(None)
                self.box.append(None)
	    else:
		view_matrix = sv.view()
		self.matrices.append(view_matrix[0])
                self.box.append(view_matrix[1])

	    ### JCALERT ! This is an hack so that the problem of displaying the right
	    ### name under each map in activity and orientation map panel is solved
	    ### It has to be changed so that it display what we want for each panel
	    ### Also I think the name that is displayed should always be the plot name
            ### (Also see in create_plots for each PlotGroup sub-classes)
            ### This should not be in this function at all	
		self.view_info['src_name'] = sv.view_info['src_name'] + self.name
		self.view_info['view_type'] = sv.view_info['view_type']

    def _slice_matrices(self):
	"""
	Sub-function used by plot: get the submatrix of the matrices in self.matrices 
        corresponding to the slice of the smallest sheetview matrix belonging to the plot.
        e.g. for coloring Weight matrix with a preference sheetview, we need to slice
        the preference matrix region that corresponds to the weight matrix. 
	Also set the attribute self.shape and self.bounds accordingly.
	"""
        ### JCALERT! Think about a best way to catch the shape...
        ### also it should raise an Error if the shape is different for 
        ### the three matrices!
 	l_shape = []
	l_box = []
	for mat,box in zip(self.matrices,self.box):
	    if mat != None:
		l_shape.append(mat.shape)
		l_box.append(box)

	shape = l_shape[0]
	outer_box = l_box[0]               # this is the outer box of the plot
	slicing_box = l_box[0]               # this is the smaller box of the plot
	for sh,b in zip(l_shape,l_box):
	    if (sh[0]+sh[1]) < (shape[0]+shape[1]):
		shape = sh
		slicing_box = b    
	    else:
		outer_box = b

	### JCALERT! Ask Jim about that: is it reasonnable to assume so?
        ### (what it means is that if we have to slice it will be sheetviews,
        ### and so the slicing_box will be from a UnitView and the outer box from
        ### a SheetView, which is required when calling submatrix. Bounding_box for sheetviews
        ### does not have the slight margin that UnitView boxes have; but that could be changed by
        ### inserting this margin to the function bounds2slice....)
	# At this point we assume that if there is matrix of different sizes
        # the outer_box will be a sheet bounding_box....
	new_matrices =[]
	for mat in self.matrices:
	    if mat != None and mat.shape != shape:
		sub_mat = submatrix(slicing_box,mat,outer_box,self.density)
		new_matrices.append(sub_mat)
	    else:
		new_matrices.append(mat)

        ### JCALERT shape and slicing_box should be added to the doc.
	self.shape = shape
	self.slicing_box=slicing_box
	self.matrices = new_matrices

    ### JCALERT! The doc has to be reviewed (as well as the code by the way...)
    ### The function should be made as a procedure working on self.matrices directly..
    ### The code inside has still to be made clearer.

    def _make_hsv_matrices(self):
	""" 
	Sub-function of plot() that return the h,s,v matrices corresponding 
	to the current self.matrices. 
	The result specified a bitmap in hsv coordinate.
    
        Also applying normalizing and croping if required.
	"""
	zero=zeros(self.shape,Float)
	one=ones(self.shape,Float)	

	s,h,c = self.matrices
        ### JC: The code below may be improved.
	# Determine appropriate defaults for each matrix
	if s is None: s=one # Treat as full strength by default
	if c is None: c=one # Treat as full confidence by default
	if h is None: # No color -- should be changed to drop down to COLORMAP plot.
	    h=zero
	    c=zero

	if self.normalize and max(s.flat)>0:
	    s = divide(s,float(max(s.flat)))

	hue,sat,val=h,c,s
       
	if max(ravel(hue)) > 1.0 or max(ravel(sat)) > 1.0 or max(ravel(val)) > 1.0:
	    self.cropped = True
	    ### JCALERT! In which case is this occuring? Because it may not need a warning...
	    #self.warning('Plot: HSVMap inputs exceed 1. Clipping to 1.0')
	    if max(ravel(hue)) > 1.0: hue = MLab.clip(hue,0.0,1.0)
	    if max(ravel(sat)) > 1.0: sat = MLab.clip(sat,0.0,1.0)
	    if max(ravel(val)) > 1.0: val = MLab.clip(val,0.0,1.0)
	else:
	    self.cropped = False

	
	return (hue,sat,val)

    ### JCALERT! In this function, we assume that the slicing box is contained in the 
    ### outer box. Otherwise there will be an error
    def _situating_plot(self,outer_box):

	### JCALERT! It has to be tested that bounds2shape returns the right answer for this purpose
        ### There seems to have a variation in the size of the plot, study this "bug" to see of
        ### it is linked to that.
	shape = bounds2shape(outer_box,self.density)
	r1,r2,c1,c2 = bounds2slice(self.slicing_box,outer_box,self.density)
	new_matrices = []
	for mat in self.matrices:
	    new_mat = zeros(shape,Float)
	    new_mat[r1:r2,c1:c2] = mat
	    new_matrices.append(new_mat)

	self.matrices = new_matrices    
	    
	
	
   
