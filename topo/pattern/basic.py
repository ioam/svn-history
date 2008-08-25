"""
Simple two-dimensional mathematical or geometrical pattern generators.

$Id$
"""
__version__='$Revision$'

import numpy
from math import pi, sin, cos, sqrt
from numpy.oldnumeric import around,bitwise_and,sin,add,Float,bitwise_or
from numpy import alltrue

from .. import param

import topo
# Imported here so that all PatternGenerators will be in the same package
from topo.base.patterngenerator import Constant
from topo.base.patterngenerator import PatternGenerator
from topo.base.arrayutil import wrap
from topo.misc.patternfn import gaussian,gabor,line,disk,ring
from topo.misc.numbergenerator import UniformRandom

# Could add a Gradient class, where the brightness varies as a
# function of an equation for a plane.  This could be useful as a
# background, or to see how sharp a gradient is needed to get a
# response.


class Null(Constant):
    """
    A constant pattern of zero activity.
    """
    scale = param.Number(default=0,constant=True,precedence=-1)


class Gaussian(PatternGenerator):
    """
    2D Gaussian pattern generator.

    The sigmas of the Gaussian are calculated from the size and
    aspect_ratio parameters:

      ysigma=size/2
      xsigma=ysigma*aspect_ratio

    The Gaussian is then computed for the given (x,y) values as::
    
      exp(-x^2/(2*xsigma^2) - y^2/(2*ysigma^2)
    """
    
    aspect_ratio = param.Number(default=0.3,bounds=(0.0,None),softbounds=(0.0,2.0),
        precedence=0.31,doc="""
        Ratio of the width to the height.
        Specifically, xsigma=ysigma*aspect_ratio (see size).""")
    
    size = param.Number(default=0.5,doc="""
        Overall size of the Gaussian, defined by:
        exp(-x^2/(2*xsigma^2) - y^2/(2*ysigma^2)
        where ysigma=size/2 and xsigma=size/2*aspect_ratio.""")

    def function(self,params):
        ysigma = params['size']/2.0
        xsigma = params['aspect_ratio']*ysigma
        
        return gaussian(self.pattern_x,self.pattern_y,xsigma,ysigma)


class SineGrating(PatternGenerator):
    """2D sine grating pattern generator."""
    
    frequency = param.Number(default=2.4,bounds=(0.0,None),softbounds=(0.0,10.0),
                       precedence=0.50, doc="Frequency of the sine grating.")
    
    phase     = param.Number(default=0.0,bounds=(0.0,None),softbounds=(0.0,2*pi),
                       precedence=0.51,doc="Phase of the sine grating.")

    def function(self,params):
        """Return a sine grating pattern (two-dimensional sine wave)."""
        return 0.5 + 0.5*sin(params['frequency']*2*pi*self.pattern_y + params['phase'])        



class Gabor(PatternGenerator):
    """2D Gabor pattern generator."""
    
    frequency = param.Number(default=2.4,bounds=(0.0,None),softbounds=(0.0,10.0),
        precedence=0.50,doc="Frequency of the sine grating component.")
    
    phase = param.Number(default=0.0,bounds=(0.0,None),softbounds=(0.0,2*pi),
        precedence=0.51,doc="Phase of the sine grating component.")
    
    aspect_ratio = param.Number(default=1.0,bounds=(0.0,None),softbounds=(0.0,2.0),
        precedence=0.31,doc=
        """
        Ratio of pattern width to height.
        The width of the Gaussian component is size*aspect_ratio (see Gaussian).
        """)
    
    size = param.Number(default=0.25,doc="""
        Determines the height of the Gaussian component (see Gaussian).""")

    def function(self,params):
        height = params['size']/2.0
        width = params['aspect_ratio']*height
        
        return gabor( self.pattern_x,self.pattern_y,width,height,
                      params['frequency'],params['phase'])


class Line(PatternGenerator):
    """2D line pattern generator."""

    thickness   = param.Number(default=0.006,bounds=(0.0,None),softbounds=(0.0,1.0),
                         precedence=0.60,
                         doc="Thickness (width) of the solid central part of the line.")
    smoothing = param.Number(default=0.05,bounds=(0.0,None),softbounds=(0.0,0.5),
                       precedence=0.61,
                       doc="Width of the Gaussian fall-off.")

    def function(self,params):
        return line(self.pattern_y,params['thickness'],params['smoothing'])


class Disk(PatternGenerator):
    """
    2D disk pattern generator.

    An elliptical disk can be obtained by adjusting the aspect_ratio of a circular
    disk; this transforms a circle into an ellipse by stretching the circle in the
    y (vertical) direction.

    The Gaussian fall-off at a point P is an approximation for non-circular disks,
    since the point on the ellipse closest to P is taken to be the same point as
    the point on the circle before stretching that was closest to P.
    """

    aspect_ratio  = param.Number(default=1.0,bounds=(0.0,None),softbounds=(0.0,2.0),
        precedence=0.31,doc=
        "Ratio of width to height; size*aspect_ratio gives the width of the disk.")

    size  = param.Number(default=0.5,doc="Top to bottom height of the disk")
    
    smoothing = param.Number(default=0.1,bounds=(0.0,None),softbounds=(0.0,0.5),
                       precedence=0.61,doc="Width of the Gaussian fall-off")
    
    def function(self,params):
        height = params['size']
        aspect_ratio = params['aspect_ratio']

        # CEBHACKALERT: this division should handle aspect_ratio=0
        return disk(self.pattern_x/aspect_ratio,self.pattern_y,height,
                         params['smoothing'])


class Ring(PatternGenerator):
    """
    2D ring pattern generator.

    See the Disk class for a note about the Gaussian fall-off.
    """

    thickness = param.Number(default=0.015,bounds=(0.0,None),softbounds=(0.0,0.5),
        precedence=0.60,doc="Thickness (line width) of the ring.")
    
    smoothing = param.Number(default=0.1,bounds=(0.0,None),softbounds=(0.0,0.5),
        precedence=0.61,doc="Width of the Gaussian fall-off inside and outside the ring.")
    
    aspect_ratio = param.Number(default=1.0,bounds=(0.0,None),softbounds=(0.0,2.0),
        precedence=0.31,doc=
        "Ratio of width to height; size*aspect_ratio gives the overall width.")
    
    size = param.Number(default=0.5)

    def function(self,params):
        height = params['size']
        aspect_ratio = params['aspect_ratio']

        return ring(self.pattern_x/aspect_ratio,self.pattern_y,height,
                    params['thickness'],params['smoothing'])
    

class Rectangle(PatternGenerator):
    """2D rectangle pattern generator."""
    
    aspect_ratio   = param.Number(default=1.0,bounds=(0.0,None),softbounds=(0.0,2.0),
        precedence=0.31,doc=
        "Ratio of width to height; size*aspect_ratio gives the width of the rectangle.")
    
    size  = param.Number(default=0.5,doc="Height of the rectangle.")

    # We will probably want to add Fuzzy-style anti-aliasing to this.

    def function(self,params):
        height = params['size']
        width = params['aspect_ratio']*height
        
        return bitwise_and(abs(self.pattern_x)<=width/2.0,
                           abs(self.pattern_y)<=height/2.0)


class TwoRectangles(Rectangle):
    """Two 2D rectangle pattern generator."""

    x1 = param.Number(default=-0.15,bounds=(-1.0,1.0),softbounds=(-0.5,0.5),
                doc="X center of rectangle 1.")
    
    y1 = param.Number(default=-0.15,bounds=(-1.0,1.0),softbounds=(-0.5,0.5),
                doc="Y center of rectangle 1.")
    
    x2 = param.Number(default=0.15,bounds=(-1.0,1.0),softbounds=(-0.5,0.5),
                doc="X center of rectangle 2.")
    
    y2 = param.Number(default=0.15,bounds=(-1.0,1.0),softbounds=(-0.5,0.5),
                doc="Y center of rectangle 2.")

    # YC: Maybe this can be implemented much more cleanly by calling
    # the parent's function() twice, but it's hard to see how to 
    # set the (x,y) offset for the parent.
    def function(self,params):
        height = params['size']
        width = params['aspect_ratio']*height

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
    
    frequency = param.Number(default=2.4,bounds=(0.0,None),softbounds=(0.0,10.0),
        precedence=0.50,doc="Frequency of the square grating.")
    
    phase     = param.Number(default=0.0,bounds=(0.0,None),softbounds=(0.0,2*pi),
        precedence=0.51,doc="Phase of the square grating.")

    # We will probably want to add anti-aliasing to this,
    # and there might be an easier way to do it than by
    # cropping a sine grating.

    def function(self,params):
        """
        Return a square-wave grating (alternating black and white bars).
        """
        return around(0.5 + 0.5*sin(params['frequency']*2*pi*self.pattern_y + params['phase']))


# CB: I removed motion_sign from this class because I think it is
# unnecessary. But maybe I misunderstood the original author's
# intention?
#
# In any case, the original implementation was incorrect - it was not
# possible to get some motion directions (directions in one whole
# quadrant were missed out).
#
# Note that to get a 2pi range of directions, one must use a 2pi range
# of orientations (there are two directions for any given
# orientation).  Alternatively, we could generate a random sign, and
# use an orientation restricted to a pi range.

class Sweeper(PatternGenerator):
    """
    PatternGenerator that sweeps a supplied PatternGenerator in a direction
    perpendicular to its orientation.
    """

    generator = param.Parameter(default=Gaussian(),precedence=0.97, doc="Pattern to sweep.")

    speed = param.Number(default=0.25,bounds=(0.0,None),doc="""
        Sweep speed: number of sheet coordinate units per unit time.""")

    step = param.Number(default=1,doc="""
        Number of steps at the given speed to move in the sweep direction.
        The distance moved is speed*step.""")

    def function(self,params):
        """Selects and returns one of the patterns in the list."""
        bounds = params['bounds']
        xdensity=params['xdensity']
        ydensity=params['ydensity']
        x=params['x']
        y=params['y']
        scale=params['scale']
        offset=params['offset']
        size=params['size']
        orientation=params['orientation']
        
        pg = self.generator

        motion_orientation=orientation+pi/2.0

        speed=params['speed']
        step=params['step']

        new_x = x+size*pg.x
        new_y = y+size*pg.y
        
        image_array = pg(xdensity=xdensity,ydensity=ydensity,bounds=bounds,
                         x=new_x + speed*step*cos(motion_orientation),
                         y=new_y + speed*step*sin(motion_orientation),
                         orientation=orientation,
                         scale=pg.scale*scale,offset=pg.offset+offset)
        
        return image_array


class Composite(PatternGenerator):
    """
    PatternGenerator that accepts a list of other PatternGenerators.
    To create a new pattern, asks each of the PatternGenerators in the
    list to create a pattern, then it combines the patterns to create a 
    single pattern that it returns.
    """

    # The Accum_Replace operator from LISSOM is not yet supported,
    # but it should be added once PatternGenerator bounding boxes
    # are respected and/or GenericImage patterns support transparency.
    operator = param.Parameter(numpy.maximum,precedence=0.98,doc="""
        Binary Numpy function used to combine the individual patterns.

        Any binary Numpy array "ufunc" returning the same
        type of array as the operands and supporting the reduce
        operator is allowed here.  Supported ufuncs include::

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

        You can also write your own operators, by making a class that
        has a static method named "reduce" that returns an array of the
        same size and type as the arrays in the list.  For example::
        
          class return_first(object):
              @staticmethod
              def reduce(x):
                  return x[0]
              
        """)
    
    generators = param.List(default=[Constant(scale=0.0)],precedence=0.97,
        class_=PatternGenerator,doc="""
        List of patterns to use in the composite pattern.  The default is
        a blank pattern, and should thus be overridden for any useful work.""")

    size  = param.Number(default=1.0,doc="Scaling factor applied to all sub-patterns.")

    
    def __init__(self,**params):
        super(Composite,self).__init__(**params)
        assert hasattr(self.operator,'reduce'),repr(self.operator)+" does not support 'reduce'."


    def _advance_pattern_generators(self,generators):
        """
        Subclasses can override this method to provide constraints on
        the values of genertators' parameters and/or eliminate
        generators from this list if necessary.
        """
        return generators

        
    # JABALERT: To support large numbers of patterns on a large input region,
    # should be changed to evaluate each pattern in a small box, and then
    # combine them at the full Composite Bounding box size.
    def function(self,params):
        """Constructs combined pattern out of the individual ones."""
        generators = self._advance_pattern_generators(params['generators'])

        # CEBALERT: mask gets applied by all PGs including the Composite itself
        # (leads to redundant calculations in current lissom_oo_or usage, but
        # will lead to problems/limitations in the future).
        orientation=params['orientation']
        size = params['size']
        patterns = [pg(xdensity=params['xdensity'],ydensity=params['ydensity'],bounds=params['bounds'],mask=params['mask'],
                       x=params['x']+size*(pg.x*cos(orientation)-
                                        pg.y*sin(orientation)),
                       y=params['y']+size*(pg.x*sin(orientation)+
                                        pg.y*cos(orientation)),
                       orientation=pg.orientation+orientation,
                       size=pg.size*params['size'],
                       scale=pg.scale*params['scale'],
                       offset=pg.offset+params['offset'])
                    for pg in generators]
        image_array = self.operator.reduce(patterns)
        return image_array



class SeparatedComposite(Composite):
    """
    Generalized version of the Composite PatternGenerator that enforces spacing constraints
    between pattern centers.

    Currently supports minimum spacing, but can be generalized to
    support maximum spacing also (and both at once).
    """

    min_separation = param.Number(default=0.0, bounds = (0,None),
                            softbounds = (0.0,1.0), doc="""
        Minimum distance to enforce between all pairs of pattern centers.

        Useful for ensuring that multiple randomly generated patterns
        do not overlap spatially.  Note that as this this value is
        increased relative to the area in which locations are chosen,
        the likelihood of a pattern appearing near the center of the
        area will decrease.  As this value approaches the available
        area, the corners become far more likely to be chosen, due to
        the distances being greater along the diagonals.
        """)
        ### JABNOTE: Should provide a mechanism for collecting and
        ### plotting the training pattern center distribution, so that
        ### such issues can be checked.

    max_trials = param.Integer(default = 50, bounds = (0,None),
                         softbounds = (0,100), precedence=-1, doc="""
        Number of times to try for a new pattern location that meets the criteria.
        
        This is an essentially arbitrary timeout value that helps
        prevent an endless loop in case the requirements cannot be
        met.""")

        
    def __distance_valid(self, g0, g1):
        """
        Returns true if the distance between the (x,y) locations of two generators
        g0 and g1 is greater than a minimum separation.

        Can be extended easily to support other criteria.
        """
        dist = sqrt((g1.x - g0.x) ** 2 +
                    (g1.y - g0.y) ** 2)
        return dist >= self.min_separation


    def _advance_pattern_generators(self,generators):
        """
        Advance the parameters for each generator for this presentation.

        Picks a position for each generator that is accepted by __distance_valid
        for all combinations.  Returns a new list of the generators, with
        some potentially omitted due to failure to meet the constraints.
        """
        
        valid_generators = []
        for g in generators:
            
            for trial in xrange(self.max_trials):
                # Generate a new position and add generator if it's ok
                
                if alltrue([self.__distance_valid(g,v) for v in valid_generators]):
                    valid_generators.append(g)
                    break
                
                vals = (g.force_new_dynamic_value('x'), g.force_new_dynamic_value('y'))
                
            else:
                self.warning("Unable to place pattern %s subject to given constraints" %
                             g.name)

        return valid_generators



class Selector(PatternGenerator):
    """
    PatternGenerator that selects from a list of other PatternGenerators.
    """

    generators = param.List(default=[Constant()],precedence=0.97,
                               class_=PatternGenerator,bounds=(1,None),
        doc="List of patterns from which to select.")

    size  = param.Number(default=1.0,doc="Scaling factor applied to all sub-patterns.")

    # CB: needs to have time_fn=None
    index = param.Number(default=UniformRandom(lbound=0,ubound=1.0,seed=76),
        bounds=(-1.0,1.0),precedence=0.20,doc="""
        Index into the list of pattern generators, on a scale from 0
        (start of the list) to 1.0 (end of the list).  Typically a
        random value or other number generator, to allow a different item
        to be selected each time.""")

    def __init__(self,generators=[Disk(x=-0.3,aspect_ratio=0.5),
                                  Rectangle(x=0.3,aspect_ratio=0.5)],**params):
        super(Selector,self).__init__(**params)
        self.generators = generators

    def function(self,params):
        """Selects and returns one of the patterns in the list."""
        bounds = params['bounds']
        xdensity=params['xdensity']
        ydensity=params['ydensity']
        x=params['x']
        y=params['y']
        scale=params['scale']
        offset=params['offset']
        size=params['size']
        orientation=params['orientation']
        index=params['index']
        int_index=int(len(self.generators)*wrap(0,1.0,index))
        pg = self.generators[int_index]
        
        image_array = pg(xdensity=xdensity,ydensity=ydensity,bounds=bounds,
                         x=x+size*(pg.x*cos(orientation)-pg.y*sin(orientation)),
                         y=y+size*(pg.x*sin(orientation)+pg.y*cos(orientation)),
                         orientation=pg.orientation+orientation,size=pg.size*size,
                         scale=pg.scale*scale,offset=pg.offset+offset)
                       
        return image_array




class SineGratingDisk(PatternGenerator):
    """A sine grating masked by a circular disk so that only a round patch is visible."""
    ### JABALERT: This class should not be necessary, if we can provide a way
    ### to control the parameters of subparts of Composite objects
    ### more easily (e.g. in the Test Pattern window, or when
    ### measuring tuning curves).


    aspect_ratio  = param.Number(default=1.0,bounds=(0.0,None),softbounds=(0.0,2.0),
        precedence=0.31,doc=
        "Ratio of width to height; size*aspect_ratio gives the width of the disk.")

    size  = param.Number(default=0.5,doc="Top to bottom height of the disk")
    
    smoothing = param.Number(default=0.0,bounds=(0.0,None),softbounds=(0.0,0.5),
                       precedence=0.61,doc="Width of the Gaussian fall-off")

    phase  = param.Number(default=1.0, doc="phase of the sine grating")

    frequency  = param.Number(default=2.4,doc="frequency of the sine grating")

       
    def __call__(self,**params_to_override):
        params = ParamOverrides(self,params_to_override)

        bounds = params['bounds']
        xdensity=params['xdensity']
        ydensity=params['ydensity']
        x=params['x']
        y=params['y']
        scale=params['scale']
        offset=params['offset']
        size=params['size']
        orientation=params['orientation']
        size=params['size']
        phase=params['phase']
        frequency=params['frequency']
        aspect_ratio=params['aspect_ratio']
        smoothing=params['smoothing']

      
        input_1=SineGrating(phase=phase, frequency=frequency, orientation=orientation, scale=scale, offset=offset)
        input_2=Disk(aspect_ratio=aspect_ratio,smoothing=smoothing,x=x, y=y,size=size,scale=scale, offset=offset)
        
        patterns = [input_1(xdensity=xdensity,ydensity=ydensity,bounds=bounds),
                            input_2(xdensity=xdensity,ydensity=ydensity,bounds=bounds)]
                      
        image_array = numpy.minimum.reduce(patterns)
        return image_array


### JABALERT: This class should be eliminated if at all possible; it
### is just a specialized version of Composite, and should be
### implementable directly using what is already in Composite.    
class GaussiansCorner(PatternGenerator):
    """Two Gaussian pattern generators arranged into a corner shape."""
    
    x = param.Number(default=-0.15,bounds=(-1.0,1.0),softbounds=(-0.5,0.5),
                doc="X center of the corner")
    
    y = param.Number(default=-0.15,bounds=(-1.0,1.0),softbounds=(-0.5,0.5),
                doc="Y center of the corner")
		
    size = param.Number(default=0.5,doc="The size of the corner")
    
    angle = param.Number(default=pi/2,doc="The angle of the corner")
    
    
    def __call__(self,**params_to_override):
        params = ParamOverrides(self,params_to_override)

        bounds = params['bounds']
        xdensity=params['xdensity']
        ydensity=params['ydensity']
        x=params['x']
        y=params['y']
        scale=params['scale']
        offset=params['offset']
        size=params['size']
        orientation=params['orientation']
        size=params['size']
	
	input_1=Gaussian()
        input_2=Gaussian()
	patterns = [input_1(orientation = orientation, bounds = bounds, xdensity = xdensity, ydensity = ydensity, offset = offset, size = size, x = self.x + cos(orientation) * size*0.9, y = self.y + sin(orientation)*size*0.9),input_2(orientation = orientation+pi/2, bounds = bounds, xdensity = xdensity, ydensity = ydensity, offset = offset, size = size,x = self.x + cos(orientation+pi/2) * size*0.9, y = self.y + sin(orientation+pi/2)*size*0.9)]
	
	return numpy.maximum(patterns[0],patterns[1])



class OneDPowerSpectrum(PatternGenerator):
    """
    ** This class has not been tested, and is still being written **
    
    Returns the spectral density of a rolling window of the input signal
    each time it is called. Over time, outputs a spectrogram.
    """
    window_length = param.Integer(constant=True,default=2,doc="""
    The interval of the signal on which to perform the Fourier transform.
    
    The Fourier transform algorithm is most efficient if this is a power of 2
    (or can be decomposed into small prime factors - see numpy.fft).""")

    
    # CEBALERT: this should be constant, but setting it so gives an error
    windowing_function = param.Parameter(default=numpy.hanning,doc="""
    This function is multiplied with the interval of signal before performing the
    Fourier transform (i.e. it is used to shape the interval). 

    The function chosen here dictates the tradeoff between resolving comparable
    signal strengths with similar frequencies, and resolving disparate signal
    strengths with dissimilar frequencies.

    See  http://en.wikipedia.org/wiki/Window_function
    """)

    window_overlap = param.Integer(default=0,doc="""Amount of overlap between each window of
    the signal.""")
    
    sample_spacing = param.Number(constant=True,default=1.0,doc="""
    ...1/samplerate,relate to time, etc...""")
    
    
    def __init__(self,signal=[1,1,1,1],start_location=0,**params):
        """
        Reads the given signal into a float32 array.

        The current position of the 'read pointer' in the signal array
        is given by self.location. start_location allows the starting
        point to be set.

        self.frequencies gives the DFT's sample frequencies, matching
        the order returned by __call__().
        """
        super(OneDPowerSpectrum,self).__init__(**params)
        
        # CB: add pre-processing options (e.g. remove DC) here?
        # Or should users do them first, if they want them?

        self.signal = numpy.asarray(signal,dtype=numpy.float32)
        self.location = start_location
        self.frequencies = numpy.fft.fftfreq(self.window_length,d=self.sample_spacing)

        self.smoothing_window = self.windowing_function(self.window_length)  


    def __call__(self):
        """
        Perform a DFT (FFT) of the current sample from the signal multiplied
        by the smoothing window.

        See numpy.fft for information about the Fourier transform.
        """
        start = max(self.location-self.window_overlap,0)
        end = start+self.window_length
        signal_sample = self.signal[start:end]

        self.location+=self.window_length

        return numpy.fft.fft(signal_sample*self.smoothing_window) #,n=n_samples)

__all__ = list(set([k for k,v in locals().items() if isinstance(v,type) and issubclass(v,PatternGenerator)]))
