"""
Functions for mapping from one 2D cartesion coordinate system to
another.

These are useful for defining projections with magnifications,
reductions, or other transformations on the input coordinate system.

Generally, these function objects should work for an arbitrary (x,y) pair,
returning new, remapped (x,y), although some classes of mappers may
define their range and domain, with undesirable or undefined behavior
outside those regions.

$Id$
"""
__version__='$Revision$'

from numpy import exp,log,sign,sqrt,sin,cos
from math import atan,pi,atan2

from topo.base.parameterizedobject import Parameter
from topo.base.parameterclasses import Number,Enumeration

from topo.base.functionfamilies import CoordinateMapperFn, IdentityMF

##########################################################################
# coordinate mapper functions

class SingleDimensionMapper(CoordinateMapperFn):
    """
    Coordinate Mapper that uses an origin-centered 1-D mapping function.

    An abstract mapping function for coordinate mappers that remap
    based on the radius, x, or y individually. Subclasses should override
    _map_fn(self,z). 
    """
    _abstract_class_name = "SingleDimensionMapper"

    in_range = Number(default=0.5*sqrt(2),bounds=(0,None),doc="""
       The maximum range of the mapping input.""")
    out_range = Number(default=0.5*sqrt(2),bounds=(0,None), doc="""
       The maximum range of the output.""")
    remap_dimension = Enumeration(default='radius',
                                  available=['radius','x','y','xy'],
                                  doc="""
        The dimension to remap. ('xy' remaps x and y independently)""")


    def __call__(self,x,y):

        if self.remap_dimension == 'radius':
            r = sqrt(x**2 + y**2)
            a = atan2(x,y)
            new_r = self._map_fn(r)
            xout = new_r * sin(a)
            yout = new_r * cos(a)
        else:
            if 'x' in self.remap_dimension:
                xout = self._map_fn(x)
            else:
                xout = x

            if 'y' in self.remap_dimension:
                yout = self._map_fn(y)
            else:
                yout = y

        return xout,yout

    def _map_fn(self,z):
        raise NotImplementedError


class MagnifyingMapper(SingleDimensionMapper):
    """
    Exponential (magnifying) mapping function.

    Provides a mapping that magnifies the center of the activity image. 
    Parameter k indicates amount of magnification, k = 0 means no magnification,
    """
    
    k = Number(default=1.0,bounds=(0,None))

    def _map_fn(self,z):
        k = self.k
        if k == 0:
            return z
        else:
            sgn = sign(z)
            z = abs(z)
            return sgn * self.out_range * (exp(z/self.in_range*k)-1)/(exp(k)-1)


class ReducingMapper(SingleDimensionMapper):
    """
    Provides a mapping that reduces the center of the activity.

    Roughly the inverse of Magnifying Mapper.  k indicates amount of reduction.    
    """
    k = Number(default=1.0,bounds=(0,None))
    
    def _map_fn(self,z):
        k = self.k
        sgn = sign(z)
        z = abs(z)
        return sgn * self.out_range * log(z/self.in_range*k+1)/log(k+1)
        

class OttesSCMotorMapper(CoordinateMapperFn):
    """
    Mapping function for mapping motor output from superior colliculus.

    This mapping is taken from Ottes et al. (1986) Vision Research 26:857-873.
    
    Default constant values are from Table 1, ibid.  The mapping allows the creation
    of a single sheet representing both colliculi, one in the x-positive hemisheet and
    the other in the x-negative hemisheet.
    """
    
    A = Number(default=5.3)
    Bu = Number(default=1.8)
    Bv = Number(default=1.8)

    mm_scale = Number(default=8.0,doc="""
       Scale factor to convert constants Bu and Bv from mm to sheet
       units.  Expressed in mm/unit. """)

    decoder_sheet = Parameter(default=None)
    
    def __call__(self,x,y):

        A = self.A 
        Bu = (self.Bu / self.mm_scale)
        Bv = self.Bv / self.mm_scale 

        R = x * self.decoder_sheet.amplitude_scale 
        phi = y * self.decoder_sheet.direction_scale * pi/180

        if R < 0:
            Rsign = -1
        else:
            Rsign = 1
            
        R = abs(R)
        
        u = Rsign * Bu * log(sqrt(R**2 + A**2 + 2*A*R*cos(phi))) - Rsign*Bu*log(A)
        v = Bv * atan((R*sin(phi))/(R*cos(phi)+A))
        
        return u,v
