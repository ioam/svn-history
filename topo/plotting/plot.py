"""
Plot class.

$Id$
"""
__version__='$Revision$'


from colorsys import hsv_to_rgb

from Numeric import zeros, ones, Float, divide, ravel,clip,array

from topo.base.topoobject import TopoObject
from topo.base.parameter import Dynamic
from topo.base.sheet import submatrix, bounds2slice, bounds2shape

from bitmap import HSVBitmap, RGBBitmap, PaletteBitmap
import palette


### JCALERT!
### - Re-write the test file, taking the new changes into account.
### - I have to change the order: situate, plot_bb and (normalize)
### - There should be a way to associate the density explicitly
###   with the sheet_view_dict, because it must match all SheetViews
###   in that dictionary.  Maybe as a tuple?
### - Fix the plot name handling along with the view_info sheetview attribute
### - Get rid of release_sheetviews.



def make_plot(channels,sheet_view_dict,density=None,
              plot_bounding_box=None,normalize=False,situate=False,name=None):
     """
     Factory function for constructing a Plot object whose type is not yet known.

     Typically, a Plot will be constructed through this call, because
     it selects the appropriate type automatically, rather than calling
     one of the Plot subclasses automatically.  See Plot.__init__ for
     a description of the arguments.
     """
     plot_types=[SHCPlot,RGBPlot,PalettePlot]
     for pt in plot_types:
         plot = pt(channels,sheet_view_dict,density,plot_bounding_box,normalize,situate,name=name)
         if plot.bitmap != None:
	     return plot
     
     TopoObject(name="make_plot").verbose('No',name,'plot constructed for this Sheet')
     return None


class Plot(TopoObject):
    """
    A bitmap-based plot of one Sheet.

    Once constructed, the Plot contains a bitmap (which is None if no
    plot could be built) that is ready to display, and a view_info
    data structure that can be used to create labels and filenames.
    """
    
    def __init__(self,channels,sheet_view_dict,density,
                 plot_bounding_box,normalize,situate,**params):
	"""
        Build a plot out of a set of SheetViews as determined by a plot_template.
        
        channels is a plot_template, i.e. a dictionary with keys
        (i.e. 'Strength','Hue','Confidence' ...).  Each key typically
        has a string value naming specifies a SheetView in
        sheet_view_dict, though specific channels may contain other
        types of information as required by specific Plot subclasses.
        channels that are not used by a particular Plot subclass will
        silently be ignored.

	sheet_view_dict is a dictionary of SheetViews, generally (but
        not necessarily) belonging to a Sheet object.

	density is the density of the Sheet whose sheet_view_dict was
	passed.

	plot_bounding_box is the outer bounding_box of the plot to
        apply if the plot is situated.  If not situated, the bounds of
        the smallest SheetView are used.

	normalize specifies whether the Plot should be normalized to
	fill the maximum dynamic range, i.e. 0.0 to 1.0.  If not
        normalized, values are clipped at 1.0.
        
	situate specifies if we want to situate the plot, i.e.,
        whether to plot the entire Sheet (or other area specified by
        the plot_bounding_box), or only the smallest plot.  The
        situate parameter is usually useful only for a Weights plot.
        
        name (which is inherited from TopoObject) specifies the name
        to use for this plot.
        """

        super(Plot,self).__init__(**params) 
       
        self.bitmap = None
        
        ### JCALERT: Fix view_info here, and in SheetView
	self.view_info = {}

	self.channels = channels
	self.view_dict = sheet_view_dict
	# bounds of the situated plotting area 
	self.plot_bounding_box = plot_bounding_box

        ### JCALERT ! This is an hack so that the problem of displaying the right
        ### name under each map in activity and orientation map panel is solved
        ### It could be done in a more satisfying way, fixing view_info in SheetViews
        ### and finding a good way to handle sheetview and plot name
	self._set_view_info()

	# # Eventually: support other type of plots (e.g vector fields...) using
        # # something like:
	# def annotated_bitmap(self):  
        # enable other construction....


    def _get_matrix(self,key):
        """
	Private Plot routine that just retrieves the matrix view (if any)
        associated with a given key in the Plot.channels.

	If the key is in channels, the corresponding sheetviews is looked 
        for in the view_dict, and its associated matrix is returned if found.
        None is returned otherwise.
        
	(It just deals with the fact that channels can be None, or that the keys
	specified by channels can potentially refer to no SheetViews in the dict).
        """
        sheet_view_key = self.channels.get(key,None)
	sv = self.view_dict.get(sheet_view_key, None)
        if sv == None:
	    matrix = None
	else:
	    view = sv.view()
	    matrix = view[0]

        return matrix


    def _get_box(self,key):
        """
        Private Plot routine that just retrieves the bounding box (if any)
        associated with a given key in the Plot.channels.

	If the key is in channels, the corresponding sheetviews is looked 
        for in the view_dict, and its associated bounds are returned if found.
        None is returned otherwise.
        
	(It just deals with the fact that channels can be None, or that the keys
	specified by channels can potentially refer to no SheetViews in the dict).
        """ 
        sheet_view_key = self.channels.get(key,None)
	sv = self.view_dict.get(sheet_view_key, None)
        if sv == None:
	    box = None
	else:
	    view = sv.view()
	    box = view[1]

        return box


   ### JCALERT! This function is probably temporary: will change when fixing the display of Plot Name
    def _set_view_info(self):
	""" Set the Plot view_info. Call when Plot is created"""
	for key in self.channels:
	    sheet_view_key = self.channels.get(key,None)
	    sv = self.view_dict.get(sheet_view_key, None)
	    if sv != None :
		if self.name == None:
		    self.view_info['src_name'] = sv.view_info['src_name'] + repr(self.name)
		else:
		    self.view_info['src_name'] = sv.view_info['src_name'] + self.name
		    self.view_info['view_type'] = sv.view_info['view_type']

     
    def _get_shape_and_boxes(self,matrices,boxes):
	"""
	Sub-function used by plot: get the shape of the matrix that
        corresponds to the smallest sheetview matrix contained in
        matrices.  Also get the box corresponding to this same
        sheetview (slicing_box), and the box of the larger one
        (outer_box).
     
        For instance, for coloring Weight matrix with a preference
        sheetview, we need to slice the preference matrix region that
        corresponds to the weight matrix. shape, slicing_box and
        outer_box are used for this purpose.
    	"""
        ### JCALERT! Think about a best way to catch the shape...
        ### also it should raise an Error if the shape is different for 
        ### the three matrices!
        ### JABALERT: Should use BoundingBoxIntersection to compute the intersection.
 	l_shape = []
	l_box = []
	for mat,box in zip(matrices,boxes):
	    if mat != None:
		l_shape.append(mat.shape)
		l_box.append(box)

	shape = l_shape[0]              
	slicing_box = l_box[0]              # this is the smaller box of the plot
        outer_box = l_box[0]
	for sh,b in zip(l_shape,l_box):
	    if (sh[0]+sh[1]) < (shape[0]+shape[1]):
		shape = sh
		slicing_box = b 
            else:
                outer_box=b	   

        return shape,slicing_box,outer_box


    # JABALERT: Is there some reason not to remove this?  If so, document.
    def _slice_matrix(self,matrix,shape,slicing_box,outer_box,density):
	"""
        Private plot routine that given a matrix, a shape, a slicing_box,
        an outer_box and a sheet density, return the corresponding submatrix.
        It is assumed that the outer_box contained the slicing_box and that the shape 
        correponds to the slicing_box.
        """
	# At this point we assume that if there is matrix of different sizes
        # the outer_box will be a sheet bounding_box.... 
        if matrix !=None and matrix.shape != shape:
	    new_matrix = submatrix(slicing_box,matrix,outer_box,density)
        else:
	    new_matrix = matrix

	return new_matrix

   

    ### JCALERT! In this function, we assume that the slicing box is contained in the 
    ### outer box. Otherwise there will be an error.
    def _situate_plot(self,hue,sat,val,outer_box,slicing_box,density):

        left,bottom,right,top = outer_box.aarect().lbrt()
        xdensity = int(density*(right-left)) / float((right-left))
        ydensity = int(density*(top-bottom)) / float((top-bottom))

	shape = bounds2shape(outer_box,xdensity,ydensity)

	r1,r2,c1,c2 = bounds2slice(slicing_box,outer_box,xdensity,ydensity)
        ### raise an error when r2-r1 > shape[1] or c2=c1 > shape[0]
	h = zeros(shape,Float)
	h[r1:r2,c1:c2] = hue
	s = zeros(shape,Float)
	s[r1:r2,c1:c2] = sat
	v = zeros(shape,Float)
	v[r1:r2,c1:c2] = val

	return (h,s,v)  

    def _normalize(self,a):
        a_offset = a-min(a.flat)
        max_a_offset = max(a_offset.flat)
        if max_a_offset>0:
             a = divide(a_offset,float(max_a_offset))
        else:
             if min(a.flat)<=0:
                  a=zeros(a.shape,Float)
             else:
                  a = ones(a.shape,Float)
        return a



class SHCPlot(Plot):
    """
    Bitmap plot based on Strength, Hue, and Confidence matrices.

    Constructs an HSV (hue, saturation, and value) plot by choosing
    the appropriate matrix for each channel.
    """

    def __init__(self,channels,sheet_view_dict,density,
                 plot_bounding_box,normalize,situate,**params):
	super(SHCPlot,self).__init__(channels,sheet_view_dict,density, 
				   plot_bounding_box,normalize,situate,**params)
        
	# catching the empty plot exception
	s_mat = self._get_matrix('Strength')
	h_mat = self._get_matrix('Hue')
	c_mat = self._get_matrix('Confidence') 

        # If it is an empty plot: self.bitmap=None
        if (s_mat==None and c_mat==None and h_mat==None):
	    self.debug('Empty plot.')

        # Otherwise, we construct self.bitmap according to what is specified by the channels.
	else:	  
	    s_box = self._get_box('Strength')
	    h_box = self._get_box('Hue')
	    c_box = self._get_box('Confidence')

	    shape,slicing_box,outer_box = self._get_shape_and_boxes((s_mat,h_mat,c_mat),(s_box,h_box,c_box))
	   
            s_mat = self._slice_matrix(s_mat,shape,slicing_box,outer_box,density)
            h_mat = self._slice_matrix(h_mat,shape,slicing_box,outer_box,density)
            c_mat = self._slice_matrix(c_mat,shape,slicing_box,outer_box,density)

	    hue,sat,val = self.__make_hsv_matrices((s_mat,h_mat,c_mat),shape,normalize)
            
            self.bitmap = HSVBitmap(hue,sat,val)
        
            # Situate the plot if required
	    if situate:
		if self.plot_bounding_box == None:
		    raise ValueError("the plot_bounding_box must be specified for situating the plot")
		else:
		    hue,sat,val = self._situate_plot(hue, sat, val, self.plot_bounding_box,
                                                     slicing_box, density)
                    self.bitmap = HSVBitmap(hue,sat,val)


    def __make_hsv_matrices(self, hsc_matrices,shape,normalize):
	""" 
	Sub-function of plot() that return the h,s,v matrices corresponding 
	to the current matrices in sliced_matrices_dict. The shape of the matrices
        in the dict is passed, as well as the normalize boolean parameter.
	The result specified a bitmap in hsv coordinate.
    
        Applies normalizing and cropping if required.
	"""
	zero=zeros(shape,Float)
	one=ones(shape,Float)	

	s,h,c = hsc_matrices
	# Determine appropriate defaults for each matrix
	if s is None: s=one # Treat as full strength by default
	if c is None: c=one # Treat as full confidence by default
	if h is None:       # No color, gray-scale plot.
	    h=zero
	    c=zero


        # If normalizing, offset the matrix so that the minimum
        # value is 0.0 and then scale to make the maximum 1.0
        if normalize:
             s=self._normalize(s)
            

        # This translation from SHC to HSV is valid only for black backgrounds;
        # it will need to be extended also to support white backgrounds.
	hue,sat,val=h,c,s
	return (hue,sat,val)
   

    
class RGBPlot(Plot):
  """
  Bitmap plot based on Red, Green, and Blue matrices.
  
  Construct an RGB (red, green, and blue) plot from the Red, Green,
  and Blue channels.
  """
  def __init__(self,channels,sheet_view_dict,density,
                 plot_bounding_box,normalize,situate,**params):

       super(RGBPlot,self).__init__(channels,sheet_view_dict,density, 
				   plot_bounding_box,normalize,situate,**params)


       # catching the empty plot exception
       r_mat = self._get_matrix('Red')
       g_mat = self._get_matrix('Green')
       b_mat = self._get_matrix('Blue') 

       # If it is an empty plot: self.bitmap=None
       if (r_mat==None and g_mat==None and b_mat==None):
            self.debug('Empty plot.')

            # Otherwise, we construct self.bitmap according to what is specified by the channels.
       else:
            r_box = self._get_box('Red')
	    g_box = self._get_box('Green')
	    b_box = self._get_box('Blue')

	    shape,slicing_box,outer_box = self._get_shape_and_boxes((r_mat,g_mat,b_mat),(r_box,g_box,b_box))
	   
            r_mat = self._slice_matrix(r_mat,shape,slicing_box,outer_box,density)
            g_mat = self._slice_matrix(g_mat,shape,slicing_box,outer_box,density)
            b_mat = self._slice_matrix(b_mat,shape,slicing_box,outer_box,density)

	    red,green,blue = self.__make_rgb_matrices((r_mat,g_mat,b_mat),shape,normalize)
            
            self.bitmap = RGBBitmap(red,green,blue)
        
            # Situate the plot if required
	    if situate:
		if self.plot_bounding_box == None:
		    raise ValueError("the plot_bounding_box must be specified for situating the plot")
		else:
		    red,green,blue = self._situate_plot(red, green, blue, self.plot_bounding_box,
                                                     slicing_box, density)
                    self.bitmap = RGBBitmap(red,green,blue)


  def __make_rgb_matrices(self, rgb_matrices,shape,normalize):
	""" 
	Sub-function of plot() that return the h,s,v matrices
	corresponding to the current matrices in
	sliced_matrices_dict. The shape of the matrices in the dict is
	passed, as well as the normalize boolean parameter.  The
	result specified a bitmap in hsv coordinate.
    
        Applies normalizing and cropping if required.
	"""
	zero=zeros(shape,Float)
	one=ones(shape,Float)	

	r,g,b = rgb_matrices
	# Determine appropriate defaults for each matrix
	if r is None: r=zero 
	if g is None: g=zero 
	if b is None: b=zero 

        if normalize:
             r = self._normalize(r)
             g = self._normalize(g)
             b = self._normalize(b)

	return (r,g,b)
   




class PalettePlot(Plot):
  """
  Bitmap plot based on a Strength matrices, with optional colorization.  

  Not yet implemented.

  When implemented, construct an RGB plot from a Strength channel,
  optionally colorized using a specified Palette.
  """
  
  def __init__(self,channels,sheet_view_dict,density,
                 plot_bounding_box,normalize,situate,**params):

      super(PalettePlot,self).__init__(channels,sheet_view_dict,density, 
				   plot_bounding_box,normalize,situate,**params)

      ### JABHACKALERT: To implement the class: If Strength is present,
      ### ask for Palette if it's there, and make a PaletteBitmap.

