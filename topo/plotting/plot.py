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

import palette


### JCALERT! I will get rid of this function when BitMap is sure and tested
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

    # List comprehensions were not used because they were slower.
    for j in range(shape[0]):
	for i in range(shape[1]):
	    rgb = hsv_to_rgb(rmat[j,i],gmat[j,i],bmat[j,i])
	    rmat[j,i] = rgb[0]
	    gmat[j,i] = rgb[1]
	    bmat[j,i] = rgb[2]
                
    return (rmat, gmat, bmat)




### JCALERT!
### - Re-write the test file, taking the new changes into account.
### - I have to change the order: situate, plot_bb and (normalize)
### - There should be a way to associate the density explicitly
###   with the sheet_view_dict, because it must match all SheetViews
###   in that dictionary.  Maybe as a tuple?
### - Make the subfunction of plot() really private.



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
         resu = pt(channels,sheet_view_dict,density,plot_bounding_box,normalize,situate,name)
         if resu.rgb_matrices != None:
	     return resu
     
     #TopoObject(name="make_plot").verbose('No plot defined')
     return None


class Plot(TopoObject):

    def __init__(self,channels,sheet_view_dict,density=None,
                 plot_bounding_box=None,normalize=False,situate=False,name=None,**params):
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
  
        ### JCALERT! Change the name to bitmap.
        # self.bimapt=None
	self.rgb_matrices = None
	self.channels = channels
	self.view_dict = sheet_view_dict

        ### JCALERT: Fix view_info here, and in SheetView
	self.view_info = {}
        ### JCALERT: it has to be checked if that is ever used at the moment.
	self.cropped = False
        ### JCALERT: This has to stay because of release_sheetviews(). Get rid of both...
	self.channels=channels
     
	# bounds of the situated plotting area 
	self.plot_bounding_box = plot_bounding_box


	### JCALERT! Temporary, can get rid of when it is understood how to pass the name from make_plot
	self.name = name

        ### JCALERT ! This is an hack so that the problem of displaying the right
        ### name under each map in activity and orientation map panel is solved
        ### It has to be changed so that it display what we want for each panel
        ### Also I think the name that is displayed should always be the plot name
        ### (Also see in create_plots for each PlotGroup sub-classes)
        ### This should not be in this function at all
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
	sub-function of plot() that just retrieves the views from the view_dict
	as specified by the channels, and create a dictionnary of matrices and 
        of the corresponding bounding_boxes accordingly .
    
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
	sub-function of plot() that just retrieves the views from the view_dict
	as specified by the channels, and create a dictionnary of matrices and 
        of the corresponding bounding_boxes accordingly .
    
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


   ### JCALERT! This function is probably temporary and will change when fixing the display of Plot Name
    def _set_view_info(self):
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


    ### JCALERT! In this function, we assume that the slicing box is contained in the 
    ### outer box. Otherwise there will be an error
    def _situate_plot(self,outer_box,slicing_box,density):

	### JCALERT! It has to be tested that bounds2shape returns the right answer for this purpose
        ### There seems to have a variation in the size of the plot, study this "bug" to see of
        ### it is linked to that.
	shape = bounds2shape(outer_box,density)
	r1,r2,c1,c2 = bounds2slice(slicing_box,outer_box,density)
        ### raise an error when r2-r1 > shape[1] or c2=c1 > shape[0]
	r = zeros(shape,Float)
	r[r1:r2,c1:c2] = self.rgb_matrices[0]
	g = zeros(shape,Float)
	g[r1:r2,c1:c2] = self.rgb_matrices[1]
	b = zeros(shape,Float)
	b[r1:r2,c1:c2] = self.rgb_matrices[2]

	return (r,g,b)  



   
class HSVPlot(Plot):

    def __init__(self,channels,sheet_view_dict,density,
                 plot_bounding_box,normalize,situate,name,**params):

	super(HSVPlot,self).__init__(channels,sheet_view_dict,density, 
				   plot_bounding_box,normalize,situate,name,**params)

	# catching the empty plot exception
	s_mat = self._get_matrix('Strength')
	h_mat = self._get_matrix('Hue')
	c_mat = self._get_matrix('Confidence') 

        ### JABALERT
        ### raise an exception to be caught by the instantiator
        ### instead. Which exception?
        if (s_mat==None and c_mat==None and h_mat==None):
	    self.debug('Empty plot.')

	else:
	  
	    s_box = self._get_box('Strength')
	    h_box = self._get_box('Hue')
	    c_box = self._get_box('Confidence')
	    shc_boxes = (s_box,h_box,c_box)
	    shc_matrices = (s_mat,h_mat,c_mat)

	    shape, slicing_box, outer_box = self._get_shape_and_boxes(shc_matrices,shc_boxes)
	    shc_matrices = self.__slice_matrices(shc_matrices,shape,slicing_box,outer_box,density)
	    hue,sat,val = self.__make_hsv_matrices(shc_matrices,shape,normalize)
        
            ### JCALERT! Use hsv_to_rgb first, and then fix bitmap and use HSVMap directly
            #self.bitmap = HSVMap(hsv_matrices)
            #self.bitmap = matrix_hsv_to_rgb(hue,sat,val)
            ### JCALERT! change the name to bitmap later (here and later and in Plot...)
	    self.rgb_matrices = matrix_hsv_to_rgb(hue,sat,val)
        

            #    Situate the plot if required
	    if situate:
		if self.plot_bounding_box == None:
		    raise ValueError("the plot_bounding_box must be specified for situating the plot")
		else:
                    #self.bitmap = self.__situate_plot(self.plot_bounding_box, slicing_box)
		    self.rgb_matrices = self._situate_plot(self.plot_bounding_box, slicing_box,density)

	    

### JCALERT! DOCUMENTATION, and make into a simple function called 3 times from RGB and 3 from HSV
    def __slice_matrices(self,shc_matrices,shape,slicing_box,outer_box,density):
	"""
        Get the submatrices.
        """
	### JCALERT! Ask Jim about that: is it reasonnable to assume so?
        ### (what it means is that if we have to slice it will be sheetviews,
        ### and so the slicing_box will be from a UnitView and the outer box from
        ### a SheetView, which is required when calling submatrix. Bounding_box for sheetviews
        ### does not have the slight margin that UnitView boxes have; but that could be changed by
        ### inserting this margin to the function bounds2slice....)
	# At this point we assume that if there is matrix of different sizes
        # the outer_box will be a sheet bounding_box.... 
        s = shc_matrices[0]
        if s!=None and s.shape != shape:
	    new_s = submatrix(slicing_box,s,outer_box,density)
        else:
	    new_s = s

        h = shc_matrices[1]
        if h!=None and h.shape != shape:
	    new_h = submatrix(slicing_box,h,outer_box,density)
        else:
	    new_h = h

        c = shc_matrices[2]
        if c!=None and c.shape != shape:
	    new_c = submatrix(slicing_box,c,outer_box,density)
        else:
	    new_c=c

	return (new_s,new_h,new_c)


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
   
       


class RGBPlot(Plot):

  def __init__(self,channels,sheet_view_dict,density=None,
                 plot_bounding_box=None,normalize=False,situate=False,name=None,**params):

      super(RGBPlot,self).__init__(channels,sheet_view_dict,density, 
				   plot_bounding_box,normalize,situate,name, **params)


class ColormapPlot(Plot):

  def __init__(self,channels,sheet_view_dict,density=None,
                 plot_bounding_box=None,normalize=False,situate=False,name=None,**params):

      super(ColormapPlot,self).__init__(channels,sheet_view_dict,density, 
				   plot_bounding_box,normalize,situate,name, **params)




### JC: I kept that as an indication of what remains to do
### JABHACKALERT: Making Plots of various types from a template would
### probably work much more cleanly like:
###  
###  def make_plot(channels,sheet_view_dict,density=None,
###                plot_bounding_box=None,normalize=False,situate=False, **params):
###      plot_types=[HSVPlot,RGBPlot,ColormapPlot]
###      for pt in plot_types:
###          plot=pt(...arguments...)
###          if plot.bitmap != None
###             return plot
###      print "Warning: No plot defined"
###  
###  
###  
###  class Plot(TopoObject):
###     bitmap=None
###     #def annotated_bitmap(self):  .... using bitmap ... construct annotated version
###     ...
###     
###  class HSVPlot(Plot):
###     ... ask for Hue, Strength, Confidence; if enough are there, make a plot.
###  
###  class RGBPlot(Plot):    
###     ... ask for Red, Green, Blue; if enough are there, make a plot.
###  
###     
###  class ColormapPlot(Plot):    
###     ... ask for Strength and Colormap; if Strength is present, make a plot.
