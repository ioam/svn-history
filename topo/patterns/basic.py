"""
Simple two-dimensional mathematical or geometrical pattern generators.

$Id$
"""
__version__='$Revision$'

from math import pi, sin, cos
from Numeric import around,bitwise_and,sin,add,Float,bitwise_or

from topo.base.parameterclasses import Number, Parameter, Enumeration, Wrapper
from topo.base.functionfamilies import OutputFnParameter
from topo.base.patterngenerator import PatternGenerator

# Imported here so that all PatternGenerators will be in the same package
from topo.base.patterngenerator import Constant

from topo.misc.patternfns import gaussian,gabor,line,disk,ring
 

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
        precedence=0.31,doc=
        """
        Ratio of the width to the height.
        Specifically, xsigma=ysigma*aspect_ratio (see size).
        """)
    
    size  = Number(default=0.5,bounds=(0.0,None),softbounds=(0.0,2.0),
        precedence=0.30,doc=
        """
        Overall size of the Gaussian, defined by:
        exp(-x^2/(2*xsigma^2) - y^2/(2*ysigma^2)
        where ysigma=size/2.
        """)

    def function(self,**params):
        ysigma = params.get('size',self.size)/2.0
        xsigma = params.get('aspect_ratio',self.aspect_ratio)*ysigma

        return gaussian(self.pattern_x,self.pattern_y,xsigma,ysigma)


class SineGrating(PatternGenerator):
    """2D sine grating pattern generator."""
    
    frequency = Number(default=2.4,bounds=(0.0,None),softbounds=(0.0,10.0),
                       precedence=0.50, doc="Frequency of the sine grating.")
    
    phase     = Number(default=0.0,bounds=(0.0,None),softbounds=(0.0,2*pi),
                       precedence=0.51,doc="Phase of the sine grating.")

    def function(self,**params):
        """Return a sine grating pattern (two-dimensional sine wave)."""
        frequency  = params.get('frequency',self.frequency)
        phase      = params.get('phase',self.phase)
        
        return 0.5 + 0.5*sin(frequency*2*pi*self.pattern_y + phase)        



class Gabor(PatternGenerator):
    """2D Gabor pattern generator."""
    
    frequency = Number(default=2.4,bounds=(0.0,None),softbounds=(0.0,10.0),
        precedence=0.50,doc="Frequency of the sine grating component.")
    
    phase = Number(default=0.0,bounds=(0.0,None),softbounds=(0.0,2*pi),
        precedence=0.51,doc="Phase of the sine grating component.")
    
    aspect_ratio = Number(default=1.0,bounds=(0.0,None),softbounds=(0.0,2.0),
        precedence=0.31,doc=
        """
        Ratio of pattern width to height.
        The width of the Gaussian component is size*aspect_ratio (see Gaussian).
        """)
    
    size = Number(default=0.25,bounds=(0.0,None),softbounds=(0.0,2.0),
        precedence=0.30,doc="Determines the height of the Gaussian component (see Gaussian).")

    def function(self,**params):
        height = params.get('size',self.size)/2.0
        width = (params.get('aspect_ratio',self.aspect_ratio))*height
        
        return gabor( self.pattern_x,self.pattern_y,width,height,
                      params.get('frequency',self.frequency),
                      params.get('phase',self.phase))  


class Line(PatternGenerator):
    """2D line pattern generator."""

    thickness   = Number(default=0.006,bounds=(0.0,None),softbounds=(0.0,1.0),
                         precedence=0.60,
                         doc="Thickness (width) of the solid central part of the line.")
    smoothing = Number(default=0.05,bounds=(0.0,None),softbounds=(0.0,0.5),
                       precedence=0.61,
                       doc="Width of the Gaussian fall-off.")

    def function(self,**params):
        return line(self.pattern_y, 
                    params.get('thickness',self.thickness),
                    params.get('smoothing',self.smoothing))


class Disk(PatternGenerator):
    """2D disk pattern generator."""

    aspect_ratio  = Number(default=1.0,bounds=(0.0,None),softbounds=(0.0,2.0),
        precedence=0.31,doc=
        "Ratio of width to height; size*aspect_ratio gives the width of the disk.")

    size  = Number(default=0.5,bounds=(0.0,None),softbounds=(0.0,2.0),
                   precedence=0.30,doc="Height of the disk")
    
    smoothing = Number(default=0.1,bounds=(0.0,None),softbounds=(0.0,0.5),
                       precedence=0.61,doc="Width of the Gaussian fall-off")
    
    def function(self,**params):
        height = params.get('size',self.size)
        width = (params.get('aspect_ratio',self.aspect_ratio))*height

        return disk( self.pattern_x,self.pattern_y,width,height,
                     params.get('smoothing',self.smoothing))  


class Ring(PatternGenerator):
    """2D ring pattern generator."""

    thickness = Number(default=0.015,bounds=(0.0,None),softbounds=(0.0,0.5),
        precedence=0.60,doc="Thickness (line width) of the ring.")
    
    smoothing = Number(default=0.1,bounds=(0.0,None),softbounds=(0.0,0.5),
        precedence=0.61,doc="Width of the Gaussian fall-off inside and outside the ring.")
    
    aspect_ratio = Number(default=1.0,bounds=(0.0,None),softbounds=(0.0,2.0),
        precedence=0.31,doc=
        "Ratio of width to height; size*aspect_ratio gives the overall width.")
    
    size = Number(default=0.5,bounds=(0.0,None),softbounds=(0.0,2.0),precedence=0.30)

    def function(self,**params):
        height = params.get('size',self.size)
        width = (params.get('aspect_ratio',self.aspect_ratio))*height
        
        return ring(self.pattern_x,self.pattern_y,width,height,
                    params.get('thickness',self.thickness),
                    params.get('smoothing',self.smoothing))  
    

class Rectangle(PatternGenerator):
    """2D rectangle pattern generator."""
    
    aspect_ratio   = Number(default=1.0,bounds=(0.0,None),softbounds=(0.0,2.0),
        precedence=0.31,doc=
        "Ratio of width to height; size*aspect_ratio gives the width of the rectangle.")
    
    size  = Number(default=0.5,bounds=(0.0,None),softbounds=(0.0,2.0),
        precedence=0.30,doc="Height of the rectangle.")

    # We will probably want to add Fuzzy-style anti-aliasing to this.

    def function(self,**params):
        height = params.get('size',self.size)
        width = (params.get('aspect_ratio',self.aspect_ratio))*height
        
        return bitwise_and(abs(self.pattern_x)<=width/2.0,
                           abs(self.pattern_y)<=height/2.0)


class TwoRectangles(Rectangle):
    """Two 2D rectangle pattern generator."""

    x1 = Number(default=-0.15,bounds=(-1.0,1.0),softbounds=(-0.5,0.5),
                doc="X center of rectangle 1.")
    
    y1 = Number(default=-0.15,bounds=(-1.0,1.0),softbounds=(-0.5,0.5),
                doc="Y center of rectangle 1.")
    
    x2 = Number(default=0.15,bounds=(-1.0,1.0),softbounds=(-0.5,0.5),
                doc="X center of rectangle 2.")
    
    y2 = Number(default=0.15,bounds=(-1.0,1.0),softbounds=(-0.5,0.5),
                doc="Y center of rectangle 2.")

    # YC: Maybe this can be implemented much more cleanly by calling
    # the parent's function() twice, but it's hard to see how to 
    # set the (x,y) offset for the parent.
    def function(self,**params):
        height = params.get('size',self.size)
        width = (params.get('aspect_ratio',self.aspect_ratio))*height

        return bitwise_or(
	       bitwise_and(bitwise_and(
			(self.pattern_x-self.x1)<=self.x1+width/4.0,
			(self.pattern_x-self.x1)>=self.x1-width/4.0),
		      bitwise_and(
			(self.pattern_y-self.y1)<=self.y1+width/4.0,
			(self.pattern_y-self.y1)>=self.y1-width/4.0)),
	       bitwise_and(bitwise_and(
			(self.pattern_x-self.x2)<=self.x2+width/4.0,
			(self.pattern_x-self.x2)>=self.x2-width/4.0),
		      bitwise_and(
			(self.pattern_y-self.y2)<=self.y2+width/4.0,
			(self.pattern_y-self.y2)>=self.y2-width/4.0)))


class SquareGrating(PatternGenerator):
    """2D squarewave grating pattern generator."""
    
    frequency = Number(default=2.4,bounds=(0.0,None),softbounds=(0.0,10.0),
        precedence=0.50,doc="Frequency of the square grating.")
    
    phase     = Number(default=0.0,bounds=(0.0,None),softbounds=(0.0,2*pi),
        precedence=0.51,doc="Phase of the square grating.")

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


class Composite(PatternGenerator):
    """
    PatternGenerator that accepts a list of other PatternGenerators.
    To create a new pattern, asks each of the PatternGenerators in the
    list to create a pattern, then it combines the patterns to create a 
    single pattern that it returns.
    """

    # The Accum_Replace operator from LISSOM is not yet supported,
    # but it should be added once PatternGenerator bounding boxes
    # are respected and/or Image patterns support transparency.
    operator = Parameter(default=Wrapper("Numeric.maximum"),precedence=0.98,doc="""
        Binary Numeric function used to combine the individual patterns.

        Any binary Numeric array "ufunc" returning the same
        type of array as the operands and supporting the reduce
        operator is allowed here.  Supported ufuncs include:

          add
          subtract
          multiply
          divide
          maximum
          minimum
          remainder
          power
          logical_and
          logical_or
          logical_xor

        The most useful ones are probably add and maximum, but there
        are uses for at least some of the others as well (e.g. to
        remove pieces of other patterns).

        The function is specified as a string with the complete
        pathname to the ufunc (e.g. "Numeric.add"); when that string
        is evaluated in the main namespace an appropriate ufunc should
        be returned.  (This approach is required to allow these
        objects to be pickled; Numeric ufuncs themselves are not
        picklable.

        You can also write your own operators, by making a class that
        has a static method named reduce that returns an array of the
        same size and type as the objects in the list.  For example:
        
        class return_first(object):
            @staticmethod
            def reduce(x):
                return x[0]

        At the moment, this must be put into a top-level module, such as
        topo.return_first=return_first, for the Wrapper class to be able
        to locate it.
        """)
    
    generators = Parameter(default=[],precedence=0.97,
        doc="List of patterns to use in the composite pattern.")

    size  = Number(default=1.0,bounds=(0.0,None),softbounds=(0.0,2.0),
        precedence=0.30,doc="Height of the composite pattern.")

    def __init__(self,generators=[Disk(x=-0.3,aspect_ratio=0.5),
                                  Disk(x= 0.3,aspect_ratio=0.5)],**params):
        super(Composite,self).__init__(**params)
        self.generators = generators
        
        assert hasattr(self.operator,'reduce'),repr(self.operator)+" does not support 'reduce'."

        for pg in self.generators:
            assert isinstance(pg,PatternGenerator),repr(pg)+" is not a PatternGenerator."

    # JABALERT: To support large numbers of patterns on a large input region,
    # should be changed to evaluate each pattern in a small box, and then
    # combine them at the full Composite Bounding box size.
    def function(self,**params):
        """Constructs combined pattern out of the individual ones."""
        bounds = params.get('bounds',self.bounds)
        xdensity=params.get('xdensity',self.xdensity)
        ydensity=params.get('ydensity',self.ydensity)
        x=params.get('x',self.x)
        y=params.get('y',self.y)
        orientation=params.get('orientation',self.orientation)
        size=params.get('size',self.size)

        patterns = [pg(xdensity=xdensity,ydensity=ydensity,bounds=bounds,
                       x=x+size*pg.x*cos(orientation)+pg.y*sin(orientation),
                       y=y+size*pg.x*sin(orientation)+pg.y*cos(orientation),
                       orientation=pg.orientation+orientation,size=pg.size*size)
                    for pg in self.generators]
        image_array = self.operator.reduce(patterns)
        return image_array
