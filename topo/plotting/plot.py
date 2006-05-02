"""
Plot class.

$Id$
"""
__version__='$Revision$'


from Numeric import zeros, ones, Float, divide,ravel,clip,array

from topo.base.parameterizedobject import ParameterizedObject
from topo.base.parameterclasses import Dynamic
from topo.base.sheetview import SheetView
from topo.base.sheet import Slice
from topo.base.sheetcoords import SheetCoordinateSystem

from bitmap import HSVBitmap, RGBBitmap, PaletteBitmap, Bitmap
import palette


### JCALERT!
### - Re-write the test file, taking the new changes into account.
### - I have to change the order: situate, plot_bb and (normalize)
### - There should be a way to associate the density explicitly
###   with the sheet_view_dict, because it must match all SheetViews
###   in that dictionary.  Maybe as a tuple?
### - Fix the plot name handling along with the view_info sheetview attribute
### - Get rid of release_sheetviews.


class Plot(ParameterizedObject):
     """
     Simple Plot object constructed from a specified PIL image.
     """
     def __init__(self,image=None,**params):
          
          super(Plot,self).__init__(**params) 
          self.bitmap = Bitmap(image)
          self.plot_src_name = ''
          self.precedence = 0.0
          # indicate if we should re-size as a topographica plot (using integer)
          # or if it is a static image that we can re-size without having to worry 
          # about what a pixel represents.
          self.resize=False
          


def make_template_plot(channels,sheet_view_dict,density=None,
              plot_bounding_box=None,normalize=False,name='None'):
     """
     Factory function for constructing a Plot object whose type is not yet known.

     Typically, a Plot will be constructed through this call, because
     it selects the appropriate type automatically, rather than calling
     one of the Plot subclasses automatically.  See Plot.__init__ for
     a description of the arguments.
     """
     plot_types=[SHCPlot,RGBPlot,PalettePlot]
     for pt in plot_types:
         plot = pt(channels,sheet_view_dict,density,plot_bounding_box,normalize,name=name)
         if plot.bitmap != None:
	     return plot
     
     ParameterizedObject(name="make_template_plot").verbose('No',name,'plot constructed for this Sheet')
     return None



class TemplatePlot(Plot):
    """
    A bitmap-based plot as specified by a plot template (or plot channels).
    """
    
    def __init__(self,channels,sheet_view_dict,density,
                 plot_bounding_box,normalize,**params):
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
        apply if specified.  If not, the bounds of
        the smallest SheetView are used.

	normalize specifies whether the Plot should be normalized to
	fill the maximum dynamic range, i.e. 0.0 to 1.0.  If not
        normalized, values are clipped at 1.0.
    
        
        name (which is inherited from ParameterizedObject) specifies the name
        to use for this plot.
        """

        super(TemplatePlot,self).__init__(**params) 
        # for a template plot, resize is True by default
        self.resize=True
        self.bitmap = None
        

	self.channels = channels
	self.view_dict = sheet_view_dict
	# bounds of the situated plotting area 
	self.plot_bounding_box = plot_bounding_box


        ### JCALERT ! The problem of displaying the right plot name is still reviewed
        ### at the moment we have the plot_src_name and name attribute that are used for the label.
        ### generally the name is set to the plot_template name, except for connection
        # set the name of the sheet that provides the SheetViews
        # combined with the self.name parameter when creating the plot (which is generally
        # the name of the plot_template), it provides the necessary information for displaying plot label
	self._set_plot_src_name()

        
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


    def _set_plot_src_name(self):
	""" Set the Plot plot_src_name. Called when Plot is created"""
	for key in self.channels:
	    sheet_view_key = self.channels.get(key,None)
	    sv = self.view_dict.get(sheet_view_key, None)
	    if sv != None:
                 self.plot_src_name = sv.src_name
                 self.precedence = sv.precedence
        

    ### JCALERT: This could be inserted in teh code of get_matrix
    def _get_shape_and_box(self):
	"""
	Sub-function used by plot: get the matrix shape and the bounding box
        of the SheetViews that constitue the TemplatePlot.
    	"""
	for name in self.channels.values():
                sv = self.view_dict.get(name,None)
                if sv != None:
                     shape = sv.view()[0].shape
                     box = sv.view()[1]    
    
        return shape,box


    def _normalize(self,a):
        """ 
        Normalize an array s.
        In case of a constant array, ones is returned for value greater than zero,
        and zeros in case of value inferior or equal to zero.
        """
        a_offset = a-min(a.flat)
        max_a_offset = max(a_offset.flat)
        if max_a_offset>0:
             a = divide(a_offset,float(max_a_offset))
        else:
             if min(a.flat)<=0:
                  a=zeros(a.shape,Float)
             else:
                  a=ones(a.shape,Float)
        return a

    ### JC: maybe density can become an attribute of the TemplatePlot?
    def _re_bound(self,plot_bounding_box,mat,box,density):

        # CEBHACKALERT: for Julien...
        # If plot_bounding_box is that of a Sheet, it will already have been
        # setup so that the density in the x direction and the density in the
        # y direction are equal.
        # If plot_bounding_box comes from elsewhere (i.e. you create it from
        # arbitrary bounds), it might need to be adjusted to ensure the density
        # in both directions is the same (see Sheet.__init__()). I don't know where
        # you want to do that; presumably the code should be common to Sheet and
        # where it's used in the plotting?
        #
        # It's possible we can move some of the functionality
        # into SheetCoordinateSystem.
        if plot_bounding_box.containsbb_exclusive(box):

             ct = SheetCoordinateSystem(plot_bounding_box,density,density)
             new_mat = zeros(ct.shape,Float)

             ct2 = SheetCoordinateSystem(plot_bounding_box,density,density)
             r1,r2,c1,c2 = Slice(box,ct2)
             new_mat[r1:r2,c1:c2] = mat
        else:
             s=Slice(plot_bounding_box,SheetCoordinateSystem(box,density,density))
             s.crop_to_sheet()
             new_mat = s.submatrix(mat)

        return new_mat
  
             
             


class SHCPlot(TemplatePlot):
    """
    Bitmap plot based on Strength, Hue, and Confidence matrices.

    Constructs an HSV (hue, saturation, and value) plot by choosing
    the appropriate matrix for each channel.
    """

    def __init__(self,channels,sheet_view_dict,density,
                 plot_bounding_box,normalize,**params):
	super(SHCPlot,self).__init__(channels,sheet_view_dict,density, 
				   plot_bounding_box,normalize,**params)
        
	# catching the empty plot exception
	s_mat = self._get_matrix('Strength')
	h_mat = self._get_matrix('Hue')
	c_mat = self._get_matrix('Confidence') 

        # If it is an empty plot: self.bitmap=None
        if (s_mat==None and c_mat==None and h_mat==None):
	    self.debug('Empty plot.')

        # Otherwise, we construct self.bitmap according to what is specified by the channels.
	else:

            shape,box = self._get_shape_and_box()                                 

            hue,sat,val = self.__make_hsv_matrices((s_mat,h_mat,c_mat),shape,normalize)

            if self.plot_bounding_box == None:
               self.plot_bounding_box = box
                            
            hue = self._re_bound(self.plot_bounding_box,hue,box,density)
            sat = self._re_bound(self.plot_bounding_box,sat,box,density)
            val = self._re_bound(self.plot_bounding_box,val,box,density)
            
            self.bitmap = HSVBitmap(hue,sat,val)


    def __make_hsv_matrices(self,hsc_matrices,shape,normalize):
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




    
class RGBPlot(TemplatePlot):
  """
  Bitmap plot based on Red, Green, and Blue matrices.
  
  Construct an RGB (red, green, and blue) plot from the Red, Green,
  and Blue channels.
  """
  def __init__(self,channels,sheet_view_dict,density,
                 plot_bounding_box,normalize,**params):

       super(RGBPlot,self).__init__(channels,sheet_view_dict,density, 
				   plot_bounding_box,normalize,**params)


       # catching the empty plot exception
       r_mat = self._get_matrix('Red')
       g_mat = self._get_matrix('Green')
       b_mat = self._get_matrix('Blue') 

       # If it is an empty plot: self.bitmap=None
       if (r_mat==None and g_mat==None and b_mat==None):
            self.debug('Empty plot.')

            # Otherwise, we construct self.bitmap according to what is specified by the channels.
       else:

            shape,box = self._get_shape_and_box()                                 

            red,green,blue = self.__make_rgb_matrices((r_mat,g_mat,b_mat),shape,normalize)

            if self.plot_bounding_box == None:
               self.plot_bounding_box = box
                            
            red = self._re_bound(self.plot_bounding_box,red,box,density)
            green = self._re_bound(self.plot_bounding_box,green,box,density)
            blue = self._re_bound(self.plot_bounding_box,blue,box,density)
         
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
   




class PalettePlot(TemplatePlot):
     """
     Bitmap plot based on a Strength matrices, with optional colorization.  

     Not yet implemented.

     When implemented, construct an RGB plot from a Strength channel,
     optionally colorized using a specified Palette.
     """
  
     def __init__(self,channels,sheet_view_dict,density,
                  plot_bounding_box,normalize,**params):

          super(PalettePlot,self).__init__(channels,sheet_view_dict,density, 
                                           plot_bounding_box,normalize,**params)

          ### JABHACKALERT: To implement the class: If Strength is present,
          ### ask for Palette if it's there, and make a PaletteBitmap.





