"""
Simple two-dimensional mathematical or geometrical pattern generators.

$Id$
"""
__version__='$Revision$'

from math import pi
from Numeric import around,bitwise_and,sin,add

from topo.base.parameterclasses import Number, Parameter, ClassSelectorParameter
from topo.misc.patternfns import gaussian,gabor,line,disk,ring
from topo.base.patterngenerator import PatternGenerator

# Imported here so that all PatternGenerators will be in the same package
from topo.base.patterngenerator import Constant

# To go into documentation for the Parameters:
#
# size: (really this is height) 
# aspect_ratio: gives ratio of pattern's width:height; i.e. width/height 
 

class Gaussian(PatternGenerator):
    """
    2D Gaussian pattern generator.

    The sigmas of the Gaussian are calculated from the size and
    aspect_ratio parameters:

      ysigma=size/2
      xsigma=ysigma*aspect_ratio

    The Gaussian is then computed for the given (x,y) values as:
    
      exp(-x^2/(2*xsigma^2) - y^2/(2*ysigma^2)
    """
    
    aspect_ratio   = Number(default=0.3,bounds=(0.0,None),softbounds=(0.0,2.0),
                            precedence=0.31,
                            doc="Ratio of the width to the height.  Specifically, xsigma=ysigma*aspect_ratio (see size).")
    size  = Number(default=0.5,bounds=(0.0,None),softbounds=(0.0,2.0),
                   precedence=0.30,
                   doc="Gaussian is defined by:\n  exp(-x^2/(2*xsigma^2) - y^2/(2*ysigma^2)\nwhere ysigma=size/2.")

    def function(self,**params):
        ysigma = params.get('size',self.size)/2.0
        xsigma = params.get('aspect_ratio',self.aspect_ratio)*ysigma

        return gaussian(self.pattern_x,self.pattern_y,xsigma,ysigma)


class SineGrating(PatternGenerator):
    """2D sine grating pattern generator."""
    
    frequency = Number(default=2.4,bounds=(0.0,None),softbounds=(0.0,10.0),
                       precedence=0.50,
                       doc="Frequency of the sine grating.")
    phase     = Number(default=0.0,bounds=(0.0,None),softbounds=(0.0,2*pi),precedence=0.51,doc="phase of the sine grating")

    def function(self,**params):
        """
        Return a sine grating pattern (two-dimensional sine wave).
        """
        frequency  = params.get('frequency',self.frequency)
        phase      = params.get('phase',self.phase)
        
        return 0.5 + 0.5*sin(frequency*2*pi*self.pattern_y + phase)        



class Gabor(PatternGenerator):
    """2D Gabor pattern generator."""
    
    frequency = Number(default=2.4,bounds=(0.0,None),softbounds=(0.0,10.0),
                       precedence=0.50,
                       doc="Frequency of the sine grating component.")
    phase     = Number(default=0.0,bounds=(0.0,None),softbounds=(0.0,2*pi),
                       precedence=0.51,
                       doc="Phase of the sine grating component.")
    aspect_ratio   = Number(default=1.0,bounds=(0.0,None),softbounds=(0.0,2.0),
                            precedence=0.31,
                            doc="Ratio of width to height; size*aspect_ratio gives the width of Gaussian component (see Gaussian)")
    size  = Number(default=0.25,bounds=(0.0,None),softbounds=(0.0,2.0),
                   precedence=0.30,
                   doc="Determines the height of the Gaussian component (see Gaussian).")

    def function(self,**params):
        height = params.get('size',self.size)/2.0
        width = (params.get('aspect_ratio',self.aspect_ratio))*height
        
        return gabor( self.pattern_x,
                      self.pattern_y,
                      width,
                      height,
                      params.get('frequency',self.frequency),
                      params.get('phase',self.phase))  


class Line(PatternGenerator):
    """2D line pattern generator."""

    # CEBHACKALERT:
    # Set smoothing to zero for the cfsom_example and you can
    # see a problem with lines. The problem is either in
    # the line() function, the generation of the matrices
    # used to draw it, or just in the display; I have to look to
    # see which.

    thickness   = Number(default=0.006,bounds=(0.0,None),softbounds=(0.0,1.0),
                         precedence=0.60,
                         doc="Thickness (width) of the solid central part of the line.")
    smoothing = Number(default=0.05,bounds=(0.0,None),softbounds=(0.0,0.5),
                       precedence=0.61,
                       doc="Width of the Gaussian fall-off.")

    # CEBHACKALERT:
    # scale does not need to be here. For the tutorial, having this scale
    # allows users to see patchy responses to a line without needing to
    # adjust it themselves.
    scale = Number(default=0.7,softbounds=(0.0,2.0))
    
    def function(self,**params):
        return line(self.pattern_y, 
                    params.get('thickness',self.thickness),
                    params.get('smoothing',self.smoothing))


class Disk(PatternGenerator):
    """2D disk pattern generator."""

    aspect_ratio  = Number(default=1.0,bounds=(0.0,None),softbounds=(0.0,2.0),
                           precedence=0.31,
                           doc="Ratio of width to height; size*aspect_ratio gives the width of the disk.")
    size  = Number(default=0.5,bounds=(0.0,None),softbounds=(0.0,2.0),
                   precedence=0.30,
                   doc="Height of the disk")
    smoothing = Number(default=0.1,bounds=(0.0,None),softbounds=(0.0,0.5),
                       precedence=0.61,
                       doc="Width of the Gaussian fall-off")
    
    def function(self,**params):
        height = params.get('size',self.size)
        width = (params.get('aspect_ratio',self.aspect_ratio))*height

        return disk( self.pattern_x, 
                     self.pattern_y, 
                     width,
                     height,
                     params.get('smoothing',self.smoothing))  


class Ring(PatternGenerator):
    """2D ring pattern generator."""

    thickness   = Number(default=0.015,bounds=(0.0,None),softbounds=(0.0,0.5),
                         precedence=0.60,
                         doc="Thickness (line width) of the ring.")
    smoothing = Number(default=0.1,bounds=(0.0,None),softbounds=(0.0,0.5),
                       precedence=0.61,
                       doc="Width of the Gaussian fall-off inside and outside the ring.")
    aspect_ratio  = Number(default=1.0,bounds=(0.0,None),softbounds=(0.0,2.0),
                           precedence=0.31,
                           doc="Ratio of width to height; size*aspect_ratio gives the overall width.")
    size  = Number(default=0.5,bounds=(0.0,None),softbounds=(0.0,2.0),precedence=0.30)

    def function(self,**params):
        height = params.get('size',self.size)
        width = (params.get('aspect_ratio',self.aspect_ratio))*height
        
        return ring(self.pattern_x, 
                    self.pattern_y,
                    width,
                    height,
                    params.get('thickness',self.thickness),
                    params.get('smoothing',self.smoothing))  
    

class Rectangle(PatternGenerator):
    """2D rectangle pattern generator."""
    
    aspect_ratio   = Number(default=1.0,bounds=(0.0,None),softbounds=(0.0,2.0),
                            precedence=0.31,
                            doc="Ratio of width to height; size*aspect_ratio gives the width of the rectangle.")
    size  = Number(default=0.5,bounds=(0.0,None),softbounds=(0.0,2.0),
                   precedence=0.30,
                   doc="Height of the rectangle.")

    # We will probably want to add Fuzzy-style anti-aliasing to this.

    def function(self,**params):
        height = params.get('size',self.size)
        width = (params.get('aspect_ratio',self.aspect_ratio))*height
        
        return bitwise_and(abs(self.pattern_x)<=width/2.0,
                           abs(self.pattern_y)<=height/2.0)


class SquareGrating(PatternGenerator):
    """2D squarewave grating pattern generator."""
    
    frequency = Number(default=2.4,bounds=(0.0,None),softbounds=(0.0,10.0),precedence=0.50,doc="Frequency of the square grating.")
    phase     = Number(default=0.0,bounds=(0.0,None),softbounds=(0.0,2*pi),precedence=0.51,doc="Phase of the square grating.")

    # We will probably want to add anti-aliasing to this,
    # and there might be an easier way to do it than by
    # cropping a sine grating.

    def function(self,**params):
        """
        Return a square-wave grating (alternating black and white bars).
        """
        frequency  = params.get('frequency',self.frequency)
        phase      = params.get('phase',self.phase)
        
        return around(0.5 + 0.5*sin(frequency*2*pi*self.pattern_y + phase))




# CEBHACKALERT: I just used methods in Image;
# I'm going to clean up Image and Composite together.

from topo.base.sheet import bounds2slice,sheet2matrix
from Numeric import floor,zeros,Float,where
def sheet2matrixidx_array(x,y,bounds,density):
    """
    Convert a point (x,y) in sheet coordinates to the integer row and
    column index of the matrix cell in which that point falls, given a
    bounds and density.  Returns (row,column).

    Note that if coordinates along the right or bottom boundary are
    passed into this function, the returned matrix coordinate of the
    boundary will be just outside the matrix, because the right and
    bottom boundaries are exclusive.
    """
    # CEBHACKALERT: see Sheet.__init__
    if type(density)!=tuple:
        left,bottom,right,top = bounds.aarect().lbrt()
        xdensity = int(density*(right-left)) / float((right-left))
        ydensity = int(density*(top-bottom)) / float((top-bottom))
    else:
        xdensity,ydensity = density

    r,c = sheet2matrix(x,y,bounds,xdensity,ydensity)
    r = floor(r)
    c = floor(c)
    return r, c

class CompositePatternGenerator(PatternGenerator):
    """
    PatternGenerator that accepts a list of other PatternGenerators.
    To create a new pattern, asks each of the PatternGenerators in the
    list to create a pattern, then it combines the patterns to create a 
    single pattern that it returns.
    """
    operator = Parameter(default=add,doc="Numeric function to combine the individual patterns.")
    generators = Parameter(default=[],doc="List of patterns composing the composite.")

    aspect_ratio   = Number(default=1.0,bounds=(0.0,None),softbounds=(0.0,2.0),
                            precedence=0.31,
                            doc="Ratio of width to height; size*aspect_ratio gives the width of the rectangle.")
    size  = Number(default=1.0,bounds=(0.0,None),softbounds=(0.0,2.0),
                   precedence=0.30,
                   doc="Height of the rectangle.")


    def __init__(self,generators=[Disk(x=-0.3,smoothing=0),Disk(x=0.3,smoothing=0)],**params):
        super(CompositePatternGenerator,self).__init__(**params)
        self.generators = generators


    def __sheet_to_image(self,x,y,bounds,density,width,height):
        """
        Transform the given topographica abscissae/ordinates (x) to fit
        an image with num_pixels along that aspect.

        - translate center (Image has (0,0) as top-left corner, whereas Sheet has
        (0,0) in the center).

        An Image consists of discrete pixels, whereas the x values are floating-
        point numbers. The simplistic technique in this function uses floor() to
        map a range to a single number.

        Maybe it would be better to put image into Sheet and use BoundingBocol functions, etc.
        """
        
        n_image_rows,n_image_cols=x.shape

        # CEBHACKALERT: temporary, density will become one again soon...
        if type(density)!=tuple:
            left,bottom,right,top = bounds.lbrt()
            xdensity = int(density*(right-left)) / float((right-left))
            ydensity = int(density*(top-bottom)) / float((top-bottom))
        else:
            xdensity,ydensity = density


        # CEBHACKALERT: just made it work - this needs to be changed now
        # that sheet and patterngenerator are different.
        #n_sheet_rows,n_sheet_cols = bounds2shape(bounds,xdensity,ydensity)
        r1,r2,c1,c2 = bounds2slice(bounds,bounds,xdensity,ydensity)
        n_sheet_rows,n_sheet_cols = r2-r1,c2-c1
        
        x = x/width
        y = y/height

        row, col = sheet2matrixidx_array(x,y,bounds,density)

        # CEBALERT:
        # Instead of doing this kind of thing, could make TopoImage a
        # Sheet and then do this with BoundingBoxes.
        col = col - n_sheet_cols/2.0 + n_image_cols/2.0
        row = row - n_sheet_rows/2.0 + n_image_rows/2.0

        # document what this is...
        col = where(col>=n_image_cols, -col, col)
        row = where(row>=n_image_rows, -row, row)

        # ...and don't do this
        return col.astype(int), row.astype(int)


    def function(self,**params):
        bounds = params.get('bounds',self.bounds)
        density=params.get('density',self.density)
        height = params.get('size',self.size)
        width = (params.get('aspect_ratio',self.aspect_ratio))*height

        
    	patterns = [pg(bounds=bounds,
                       density=density)
                    for pg in self.generators]
        
        self.image_array = self.operator.reduce(patterns)

        return self.resamp(self.pattern_x,self.pattern_y,bounds,density,width,height)


    def resamp(self, x, y,bounds,density,width=1.0, height=1.0):
        """
        Return pixels from the image (size-normalized according to
        scaling) at the given Sheet (x,y) coordinates, with
        width/height multiplied as specified by the given width and
        height factors.
        """
 
        x_scaled, y_scaled = self.__sheet_to_image(x, y, bounds, density, width, height)

        image_sample = zeros(x_scaled.shape, Float) #*self.background_value

        # CEBALERT: Sample image at the scaled (x,y)
        # coordinates. You'd think there'd be a Numeric way to do
        # this.
        for i in xrange(len(image_sample)):
            for j in xrange(len(image_sample[i,:])):
                    if x_scaled[i,j] >= 0 and y_scaled[i,j] >= 0:
                        image_sample[i,j] = self.image_array[ y_scaled[i,j],x_scaled[i,j] ]

        return image_sample






        
