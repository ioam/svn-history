"""
Plot class.

$Id$
"""
__version__='$Revision$'

from Numeric import zeros, ones, Float, divide, ravel,clip,array

from topo.base.topoobject import TopoObject
from topo.base.parameter import Dynamic
from topo.base.sheet import submatrix, bounds2slice, bounds2shape


### JCALERT! Maybe instead of importing that from bitmap, just define it here...
from bitmap import WHITE_BACKGROUND, BLACK_BACKGROUND
import palette as palette
from colorsys import hsv_to_rgb


def matrix_hsv_to_rgb(hMapArray,sMapArray,vMapArray):
    """
    First matrix sets the Hue (Color).
    Second marix sets the Sauration (How much color)
    Third matrix sets the Value (How bright the pixel will be)

    The three input matrices should all be the same size, and have
    been normalized to 1.  There should be no side-effects on the
    original input matrices.
    """
    
    shape = hMapArray.shape
    rmat = array(hMapArray,Float)
    gmat = array(sMapArray,Float)
    bmat = array(vMapArray,Float)
    
## This code should never be seen.  It means that calling code did
          ## not take the precaution of clipping the input matrices.
    if max(rmat.flat) > 1 or max(gmat.flat) > 1 or max(bmat.flat) > 1:
	topo.base.topoobject.TopoObject().warning('HSVMap inputs exceed 1. Clipping to 1.0')
	if max(rmat.flat) > 0: rmat = clip(rmat,0.0,1.0)
	if max(gmat.flat) > 0: gmat = clip(gmat,0.0,1.0)
	if max(bmat.flat) > 0: bmat = clip(bmat,0.0,1.0)

    ### JABHACKALERT!
    ###
    ### The PreferenceMap panel currently prints the message above,
    ### but this should really be handled some other way.  The messages
    ### fill the console with information that may not be relevant to
    ### anyone, because it can be entirely legal to plot something with
    ### a range higher than 1.0.  E.g. very often we deliberately plot
    ### selectivity with the brightness turned up so high that many of
    ### the brighter pixels get cropped off, to accentuate the shape
    ### of the few remaining areas that are poorly selective.  We should 
    ### have some way of printing a message once, saying where to check
    ### to see if further cropping has occurred.  E.g. there could be 
    ### a variable associated with each plot that says what the maximum
    ### value before cropping was, and a message could be printed the 
    ### first time any plot reaches that maximum, listing the variable
    ### that can be checked to find out the cropping on any particular 
    ### plot.
    ### 
    ### In any case, we should never be using "print" directly; we need
    ### all messages to be handled by the sharedfacility in TopoObject
    ### so that the user can turn them on and off, etc.  If the facilities
    ### in TopoObject are not sufficient, e.g. if there needs to be some
    ### way to use them outside of a TopoObject, then such an interface 
    ### to those shared messaging routines should be provided and then
    ### used consistently.

    # List comprehensions were not used because they were slower.
    for j in range(shape[0]):
	for i in range(shape[1]):
	    rgb = hsv_to_rgb(rmat[j,i],gmat[j,i],bmat[j,i])
	    rmat[j,i] = rgb[0]
	    gmat[j,i] = rgb[1]
	    bmat[j,i] = rgb[2]
                
    return (rmat, gmat, bmat)
    


class Plot(TopoObject):
    """
    Constructs and stores a bitmap from one or more SheetViews.

    The bitmap is then available for future use, e.g. as part of a
    PlotGroup of related plots displayed within one GUI window.

    Plot creates the 3 matrices necessary for plotting a RGB image,
    from a channel dictionary and a dictionary of SheetViews.
    Eventually, plots more complex than simple bitmaps will be
    supported, including overlaid outlines, contours, vector fields,
    histograms, etc., and the overall architecture should be designed
    to make this feasible.
    """
    background = Dynamic(default=BLACK_BACKGROUND)
    palette_ = Dynamic(default=palette.Monochrome)
 
    ### JCALERT!
    ### - Re-write the test file, taking the new changes into account.
    ### - I have to change the order: situate, plot_bb and (normalize)
    ### - There should be a way to associate the density explicitly
    ###   with the sheet_view_dict, because it must match all SheetViews
    ###   in that dictionary.  Maybe as a tuple?
    ### - Make the subfunction of plot() really private.

    def __init__(self,channels,sheet_view_dict,density=None,
                 plot_bounding_box=None,normalize=False,situate=False, **params):
        """
        Get the SheetViews requested from each channel passed in at
        creation, combines them as necessary, (and generates the
        Histograms, not yet implemented). 
            
	Important features of this object are:

	   self.matrices: Triple of Matrices mapping to the
	                  R/G/B channels.
           self.view_info: Name information that can be used to create
                           labels and filenames.
           (self.histograms: List of Histogram objects associated with
                    the matrices is self.matrices. NOT YET IMPLEMENTED) 
          
        channels is a dictionary with keys (i.e. 'Strength','Hue','Confidence' ...)
        that point to a stored SheetView in sheet_view_dict, as specified 
	in a PlotTemplate. None is also possible if the Plot is only built 
        from one or two SheetViews.   

	sheet_view_dict is a dictionary of SheetViews, generally belonging 
        to a Sheet object but not necessarily.

	normalize specified is the Plot is normalized or not.

	density is the density of the sheet that contains the different views
        constituting the plot.

	plot_bounding_box is the outer bounding_box of the plot
        to apply if the plot is situated.  If not situated, the
        bounds of the smallest SheetView are used.
        
	situate specifies if we want to situate the plot, i.e.,
        whether to plot the entire Sheet (or other area specified by
        the plot_bounding_box), or only the smallest plot (usually a
        Weights plot).
        
        name (inherited from TopoObject) specifies the name to use for
        this plot.
        """   
        super(Plot,self).__init__(**params)

      	self.view_dict = sheet_view_dict
        self.density = density

	### JCALERT: Fix view_info here, and in SheetView
        self.view_info = {}
	### JCALERT: it has to be checked if that is ever used at the moment.
        self.cropped = False
        ### JCALERT: This has to stay because of release_sheetviews. Get rid of both...
        self.channels=channels
     
	# bounds of the situated plotting area 
	self.plot_bounding_box = plot_bounding_box

	# Remaining of the code are the steps to construct the plot bitmap (self.matrices)

        ### JABALERT: make self.matrices a Tuple. Rename it rgb_matrices
        self.matrices = [None,None,None]

	# return a dictionary of view matrices and a dictionary of bounding_boxes,
        # as specified by channels
	matrices_dict, boxes_dict = self.__extract_view_dict_info(channels)

	# catching the empty plot exception
	s = matrices_dict['Strength']
	h = matrices_dict['Hue']
	c = matrices_dict['Confidence'] 

        ### JABALERT
        ### raise an exception to be caught by the instantiator
        ### instead. Which exception?
        if (s==None and c==None and h==None):
            self.debug('Skipping empty plot.')
	else:
	    # If the plot is not empty: get the submatrix of each sheetview,
            # that corresponds to the smallest one and return them in a new matrix dictionary
            # along with their corresponding shape and bounding_box. 
	    shape, slicing_box, sliced_matrices_dict = self.__slice_matrices(matrices_dict,boxes_dict)

	    # Construct the hsv bitmap corresponding to the dictionary of matrices
	    (hue,sat,val) = self.__make_hsv_matrices(sliced_matrices_dict,shape,normalize)
	    
	    # Convert the hsv bitmap in rgb
	    self.matrices = matrix_hsv_to_rgb(hue,sat,val)

	    # Situate the plot if required
	    if situate:
		if self.plot_bounding_box == None:
		    raise ValueError("the plot_bounding_box must be specified for situating the plot")
		else:
		    self.matrices = self.__situate_plot(self.plot_bounding_box, slicing_box)
	


    ### JABALERT: This does not seem appropriate -- Plot should not delete
    ### any SheetViews that it did not put there itself.
    def release_sheetviews(self):
        """
        Delete any sheet_view_dict entries used by this plot, under
        the assumption that this Plot is the only object that use the 
        the SheetView in the sheet_view_dict  with that dictionary key.
        """
        for each in self.channels.values():
	    del self.view_dict[each]



    def __extract_view_dict_info(self,channels):
        """
	sub-function of plot() that just retrieves the views from the view_dict
	as specified by the channels, and create a dictionnary of matrices and 
        of the corresponding bounding_boxes accordingly .
    
	(It just deals with the fact that channels can be None, or that the keys
	specified by channels can potentially refer to no SheetViews in the dict).
        """  
	matrices_dict = {}
	boxes_dict = {}
	for key,value in channels.items():
	    sv = self.view_dict.get(value, None)
	    if sv == None:
		matrices_dict[key] = None
		boxes_dict[key] = None
	    else:
		view_matrix = sv.view()
 		matrices_dict[key] = view_matrix[0]
	        boxes_dict[key] = view_matrix[1]

	    ### JCALERT ! This is an hack so that the problem of displaying the right
	    ### name under each map in activity and orientation map panel is solved
	    ### It has to be changed so that it display what we want for each panel
	    ### Also I think the name that is displayed should always be the plot name
            ### (Also see in create_plots for each PlotGroup sub-classes)
            ### This should not be in this function at all	
		self.view_info['src_name'] = sv.view_info['src_name'] + self.name
		self.view_info['view_type'] = sv.view_info['view_type']

	return matrices_dict, boxes_dict
	    

    def __slice_matrices(self,matrices_dict,boxes_dict):
	"""
	Sub-function used by plot: get the submatrix of the matrices in matrices_dict 
        corresponding to the slice of the smallest sheetview matrix belonging to the plot.
        e.g. for coloring Weight matrix with a preference sheetview, we need to slice
        the preference matrix region that corresponds to the weight matrix. 

	It returns the new matrices dictionnary that contains the submatrices,
        and the corresponding shape and bounds of the sliced matrices.
    	"""
        ### JCALERT! Think about a best way to catch the shape...
        ### also it should raise an Error if the shape is different for 
        ### the three matrices!
 	l_shape = []
	l_box = []
	for mat,box in zip(matrices_dict.values(),boxes_dict.values()):
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
	new_matrices_dict = {} 
	for key,mat in matrices_dict.items():
	    if mat != None and mat.shape != shape:
		sub_mat = submatrix(slicing_box,mat,outer_box,self.density)
		new_matrices_dict[key] = sub_mat
	    else:
		new_matrices_dict[key] = mat

	return shape,slicing_box,new_matrices_dict


    def __make_hsv_matrices(self, sliced_matrices_dict,shape,normalize):
	""" 
	Sub-function of plot() that return the h,s,v matrices corresponding 
	to the current self.matrices. 
	The result specified a bitmap in hsv coordinate.
    
        Also applying normalizing and cropping if required.
	"""
	zero=zeros(shape,Float)
	one=ones(shape,Float)	

	s = sliced_matrices_dict['Strength']
	h = sliced_matrices_dict['Hue']
	c = sliced_matrices_dict['Confidence'] 

        ### JC: The code below may be improved.
	# Determine appropriate defaults for each matrix
	if s is None: s=one # Treat as full strength by default
	if c is None: c=one # Treat as full confidence by default
	if h is None: # No color -- should be changed to drop down to COLORMAP plot.
	    h=zero
	    c=zero

	if normalize and max(s.flat)>0:
	    s = divide(s,float(max(s.flat)))

	hue,sat,val=h,c,s
       
	### JCALERT! This re-done in matrix_hsv_to_rgb...so we could get rid of one of these tests?
        ### Furthermore self.cropped does not seem to be used....
	if max(ravel(hue)) > 1.0 or max(ravel(sat)) > 1.0 or max(ravel(val)) > 1.0:
	    self.cropped = True
	    ### JCALERT! In which case is this occuring? Because it may not need a warning...
	    #self.warning('Plot: HSVMap inputs exceed 1. Clipping to 1.0')
	    if max(ravel(hue)) > 1.0: hue = clip(hue,0.0,1.0)
	    if max(ravel(sat)) > 1.0: sat = clip(sat,0.0,1.0)
	    if max(ravel(val)) > 1.0: val = clip(val,0.0,1.0)
	else:
	    self.cropped = False

	
	return (hue,sat,val)


    ### JCALERT! In this function, we assume that the slicing box is contained in the 
    ### outer box. Otherwise there will be an error
    def __situate_plot(self,outer_box,slicing_box):

	### JCALERT! It has to be tested that bounds2shape returns the right answer for this purpose
        ### There seems to have a variation in the size of the plot, study this "bug" to see of
        ### it is linked to that.
	shape = bounds2shape(outer_box,self.density)
	r1,r2,c1,c2 = bounds2slice(slicing_box,outer_box,self.density)
        ### raise an error when r2-r1 > shape[1] or c2=c1 > shape[0]
	new_matrices = []
	for mat in self.matrices:
	    new_mat = zeros(shape,Float)
	    new_mat[r1:r2,c1:c2] = mat
	    new_matrices.append(new_mat) 

	return new_matrices    
	    
	
	
   
