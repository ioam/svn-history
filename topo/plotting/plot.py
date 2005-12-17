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



### JCALERT! This function has to be better documented
def make_plot(channels,sheet_view_dict,density=None,
              plot_bounding_box=None,normalize=False,situate=False,name=None):
     """
     Factory function called when requesting a Plot Object.
     It is what should always be used when requesting a Plot
     rather than a direct call to one of the Plot sub-classes.
     """
     plot_types=[HSVPlot,RGBPlot,ColormapPlot]
     for pt in plot_types:
         plot = pt(channels,sheet_view_dict,density,plot_bounding_box,normalize,situate,name=name)
         if plot.bitmap != None:
	     return plot
     
     #TopoObject(name="make_plot").verbose('No plot defined')
     return None


class Plot(TopoObject):

    def __init__(self,channels,sheet_view_dict,density,
                 plot_bounding_box,normalize,situate,**params):
	"""
        Get the SheetViews requested from each channel passed in at
        creation, combines them as necessary.
            
	Important features of this object are:

	   self.bitmap: Bitmap object associated with the Plot and 
                        ready to display in the GUI.
        
           self.view_info: Name information that can be used to create
                           labels and filenames.
              
        channels is a dictionary with keys (i.e. 'Strength','Hue','Confidence' ...)
        that point to a stored SheetView in sheet_view_dict, as specified 
	in a PlotTemplate. None is also possible if the Plot is only built 
        from one or two SheetViews. Also the code support the possibility for channels
        to store other objects than SheetViews.   

	sheet_view_dict is a dictionary of SheetViews, generally belonging 
        to a Sheet object but not necessarily.

	density is the density of the sheet that contains the different views
        constituting the plot.

	plot_bounding_box is the outer bounding_box of the plot
        to apply if the plot is situated.  If not situated, the
        bounds of the smallest SheetView are used.

	normalize specified if the Plot is normalized or not.
        
	situate specifies if we want to situate the plot, i.e.,
        whether to plot the entire Sheet (or other area specified by
        the plot_bounding_box), or only the smallest plot (usually a
        Weights plot).
        
        name (inherited from TopoObject) specifies the name to use for
        this plot.
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

	### Note: for supporting other type of plots (e.g vector fields...)
	# def annotated_bitmap(self):  
        # enable other construction....
	

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
	for key in ('Strength','Hue','Confidence'):
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
	Sub-function used by plot: get the shape of the matrix that corresponds 
        to  the smallest sheetview matrix contained in matrices.
        Also get the box corresponding to this same sheetview (slicing_box), and the box
        of the larger one (outer_box). 
     
        e.g. for coloring Weight matrix with a preference sheetview, we need to slice
        the preference matrix region that corresponds to the weight matrix. shape,
        slicing_box and outer_box are used for this purpose.
    	"""
        ### JCALERT! Think about a best way to catch the shape...
        ### also it should raise an Error if the shape is different for 
        ### the three matrices!
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


    def _slice_matrix(self,matrix,shape,slicing_box,outer_box,density):
	"""
        Private plot routine that given a matrix, a shape, a slicing_box,
        an outer_box and a sheet density, return the corresponding submatrix.
        It is assumed that the outer_box contained the slicing_box and that the shape 
        correponds to the slicing_box.
        """
	### JCALERT! Bounding_box for sheetviews
        ### does not have the slight margin that UnitView boxes have; but that could be changed by
        ### inserting this margin to the function bounds2slice....)
	# At this point we assume that if there is matrix of different sizes
        # the outer_box will be a sheet bounding_box.... 
        if matrix !=None and matrix.shape != shape:
	    new_matrix = submatrix(slicing_box,matrix,outer_box,density)
        else:
	    new_matrix = matrix

	return new_matrix

   

    ### JCALERT! In this function, we assume that the slicing box is contained in the 
    ### outer box. Otherwise there will be an error
    def _situate_plot(self,hue,sat,val,outer_box,slicing_box,density):

	shape = bounds2shape(outer_box,density)
	r1,r2,c1,c2 = bounds2slice(slicing_box,outer_box,density)
        ### raise an error when r2-r1 > shape[1] or c2=c1 > shape[0]
	h = zeros(shape,Float)
	h[r1:r2,c1:c2] = hue
	s = zeros(shape,Float)
	s[r1:r2,c1:c2] = sat
	v = zeros(shape,Float)
	v[r1:r2,c1:c2] = val

	return (h,s,v)  



   
class HSVPlot(Plot):

    def __init__(self,channels,sheet_view_dict,density,
                 plot_bounding_box,normalize,situate,**params):

	super(HSVPlot,self).__init__(channels,sheet_view_dict,density, 
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
                    #self.bitmap = self.__situate_plot(self.plot_bounding_box, slicing_box)
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

	if normalize and max(s.flat)>0:
	    s = divide(s,float(max(s.flat)))
        ### JCALERT! I think we need that here (it is not anymore caught from bitmap). Ask Jim
        ### Lead to a bug in testpattern (Disk) but maybe because of a problem in testpattern... 
       #  if not max(s.flat)<=1.0:
#              self.warning('arrayToImage failed to Normalize.  Possible NaN.  Using blank matrix.')
#              self.zeros

	hue,sat,val=h,c,s	
	return (hue,sat,val)
   


    
###  class RGBPlot(Plot):    
###     ... ask for Red, Green, Blue; if enough are there, make a plot.
###        


class RGBPlot(Plot):

  def __init__(self,channels,sheet_view_dict,density,
                 plot_bounding_box,normalize,situate,**params):

      super(RGBPlot,self).__init__(channels,sheet_view_dict,density, 
				   plot_bounding_box,normalize,situate,**params)

###     
###  class PalettePlot(Plot):    
###     ... ask for Strength and Palette; if Strength is present, make a plot.

class ColormapPlot(Plot):

  def __init__(self,channels,sheet_view_dict,density,
                 plot_bounding_box,normalize,situate,**params):

      super(ColormapPlot,self).__init__(channels,sheet_view_dict,density, 
				   plot_bounding_box,normalize,situate,**params)










