"""
Simple two-dimensional mathematical or geometrical pattern generators.


Additionally, this module defines precedences
W_PREC, H_PREC, FR_PREC, PH_PREC, TH_PREC, SM_PREC
which can be used by subclasses that use one of the typical Parameters
(frequency, phase, width, height, thickness, smoothing) and wish to maintain the same order
width > height > frequency > phase > thickness > smoothing
should any changes be made to that ordering here.

$Id$
"""
__version__='$Revision$'

from math import pi
from Numeric import around,bitwise_and,sin,add

from topo.base.parameter import Number, Parameter, ClassSelectorParameter
from topo.misc.patternfns import gaussian,gabor,line,disk,ring
from topo.base.patterngenerator import PatternGenerator

# Imported here so that all PatternGenerators will be in the same package
from topo.base.patterngenerator import Constant

# CEBHACKALERT: need size, aspect ratio, frequency, etc. to be defined
# somewhere that all the uses here can inherit from. Otherwise, doc,
# precedence etc. have to be written out several times or some system
# of constants as below for precedence has to be used (which is really
# not an ideal solution).

# precedence constants for ordering
SI_PREC = 0.30
AR_PREC = 0.31
FR_PREC = 0.50
PH_PREC = 0.51
TH_PREC = 0.60
SM_PREC = 0.61

# To go into documentation for the Parameters:
#
# size: (really this is height) 
# aspect_ratio: gives ratio of pattern's width:height; i.e. width/height 
# 


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
    
    aspect_ratio   = Number(default=0.3,bounds=(0.0,None),softbounds=(0.0,2.0),precedence=AR_PREC)
    size  = Number(default=0.5,bounds=(0.0,None),softbounds=(0.0,2.0),precedence=SI_PREC)

    def function(self,**params):
        ysigma = params.get('size',self.size)/2.0
        xsigma = params.get('aspect_ratio',self.aspect_ratio)*ysigma

        return gaussian(self.pattern_x,self.pattern_y,xsigma,ysigma)


class SineGrating(PatternGenerator):
    """2D sine grating pattern generator."""
    
    frequency = Number(default=2.4,bounds=(0.0,None),softbounds=(0.0,10.0),precedence=FR_PREC)
    phase     = Number(default=0.0,bounds=(0.0,None),softbounds=(0.0,2*pi),precedence=PH_PREC)

    def function(self,**params):
        """
        Return a sine grating pattern (two-dimensional sine wave).
        """
        frequency  = params.get('frequency',self.frequency)
        phase      = params.get('phase',self.phase)
        
        return 0.5 + 0.5*sin(frequency*2*pi*self.pattern_y + phase)        



class Gabor(PatternGenerator):
    """2D Gabor pattern generator."""
    
    frequency = Number(default=2.4,bounds=(0.0,None),softbounds=(0.0,10.0),precedence=FR_PREC)
    phase     = Number(default=0.0,bounds=(0.0,None),softbounds=(0.0,2*pi),precedence=PH_PREC)
    aspect_ratio   = Number(default=1.0,bounds=(0.0,None),softbounds=(0.0,2.0),precedence=AR_PREC)
    size  = Number(default=0.25,bounds=(0.0,None),softbounds=(0.0,2.0),precedence=SI_PREC)

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

    thickness   = Number(default=0.006,bounds=(0.0,None),softbounds=(0.0,1.0),precedence=TH_PREC)
    smoothing = Number(default=0.05,bounds=(0.0,None),softbounds=(0.0,0.5),precedence=SM_PREC)

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

    aspect_ratio  = Number(default=1.0,bounds=(0.0,None),softbounds=(0.0,2.0),precedence=AR_PREC)
    size  = Number(default=0.5,bounds=(0.0,None),softbounds=(0.0,2.0),precedence=SI_PREC)
    smoothing = Number(default=0.1,bounds=(0.0,None),softbounds=(0.0,0.5),precedence=SM_PREC)
    
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

    thickness   = Number(default=0.015,bounds=(0.0,None),softbounds=(0.0,0.5),precedence=TH_PREC)
    smoothing = Number(default=0.1,bounds=(0.0,None),softbounds=(0.0,0.5),precedence=SM_PREC)
    aspect_ratio  = Number(default=1.0,bounds=(0.0,None),softbounds=(0.0,2.0),precedence=AR_PREC)
    size  = Number(default=0.5,bounds=(0.0,None),softbounds=(0.0,2.0),precedence=SI_PREC)

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
    
    aspect_ratio   = Number(default=1.0,bounds=(0.0,None),softbounds=(0.0,2.0),precedence=AR_PREC)
    size  = Number(default=0.5,bounds=(0.0,None),softbounds=(0.0,2.0),precedence=SI_PREC)

    # We will probably want to add Fuzzy-style anti-aliasing to this.

    def function(self,**params):
        height = params.get('size',self.size)
        width = (params.get('aspect_ratio',self.aspect_ratio))*height
        
        return bitwise_and(abs(self.pattern_x)<=width/2.0,
                           abs(self.pattern_y)<=height/2.0)


class SquareGrating(PatternGenerator):
    """2D squarewave grating pattern generator."""
    
    frequency = Number(default=2.4,bounds=(0.0,None),softbounds=(0.0,10.0),precedence=FR_PREC)
    phase     = Number(default=0.0,bounds=(0.0,None),softbounds=(0.0,2*pi),precedence=PH_PREC)

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



class CompositePatternGenerator(PatternGenerator):
    """
    PatternGenerator that accepts a list of other PatternGenerators.
    To create a new pattern, asks each of the PatternGenerators in the
    list to create a pattern, then it combines the patterns to create a 
    single pattern that it returns.
    """
	# CPHACKALERT: these should be a Parameters
    operator = add
    generatorlist = []

    def __init__(self,generatorlist=[Disk(x=-0.3),Disk(x=0.3)],**params):
        super(CompositePatternGenerator,self).__init__(**params)
        self.generatorlist = generatorlist

    # Or should it be: def __call__(self,**params): ?
    def function(self,**params):
    	patterns = [pg(bounds=params.get('bounds',self.bounds),density=params.get('density',self.density))
                    for pg in self.generatorlist]
        return self.operator.reduce(patterns)