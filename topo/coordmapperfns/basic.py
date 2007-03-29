"""
Functions for mapping from one 2D Cartesian coordinate system to another.

These are useful for defining projections with nonlinear magnifications,
reductions, or other transformations of the input coordinate system.

Generally, these function objects should work for an arbitrary (x,y) pair,
returning new, remapped (x,y), although some classes of mappers may
define their range and domain, with undesirable or undefined behavior
outside those regions.  It is best if such objects raise a suitable
exception in those circumstances.

$Id$
"""
__version__='$Revision$'

from numpy import exp,log,sqrt,sin,cos,zeros
from math import atan,pi,atan2

from topo.base.parameterizedobject import Parameter
from topo.base.parameterclasses import Number,Enumeration
from topo.base.functionfamilies import CoordinateMapperFn, IdentityMF
from topo.misc.utils import signabs

##########################################################################
# coordinate mapper functions


class ConstantMapper(CoordinateMapperFn):
    """
    Coordinate Mapper that uses constant mapping values.

    Outputs constant coordinate (x_cons, y_cons).
    """
    x_cons = Number(default=0.0,bounds=(0,None),doc="""
       The maximum range of the mapping input.""")
    y_cons = Number(default=0.0,bounds=(0,None), doc="""
       The y coordinate of the mapping output.""")

    def __call__(self, x, y):
        """
        Arguments x and y are used to follow the abstraction class
        CoordinateMapperFn only.
        """
        return self.x_cons, self.y_cons


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
            sgn,z = signabs(z)
            return sgn * self.out_range * (exp(z/self.in_range*k)-1)/(exp(k)-1)


class ReducingMapper(SingleDimensionMapper):
    """
    Provides a mapping that reduces the center of the activity.

    Roughly the inverse of Magnifying Mapper.  k indicates amount of reduction.    
    """
    k = Number(default=1.0,bounds=(0,None))
    
    def _map_fn(self,z):
        k = self.k
        sgn,z = signabs(z)
        return sgn * self.out_range * log(z/self.in_range*k+1)/log(k+1)
        

class OttesSCMapper(CoordinateMapperFn):
    """
    Abstract class for superior colliculus mappings.

    Subclasses of this class implement afferent and efferent mappings
    from Ottes et al. (1986) Vision Research 26:857-873.
    
    Default constant values are from Table 1, ibid.  
    """
    __abstract_class = "OttesSCMapper"

    
    A = Number(default=5.3, doc="""
       Shape parameter A, in degrees""")
    Bu = Number(default=1.8, doc="""
       Rostral-caudal scale parameter, in mm""")
    Bv = Number(default=1.8, doc="""
       Orthogonal (medial-lateral?) scale paraemter in mm/deg""")

    mm_scale = Number(default=8.0,doc="""
       Scale factor to convert constants Bu and Bv from mm to sheet
       units.  Expressed in mm/unit. """)

    amplitude_scale = Number(default=1,doc="""
        Scale factor for saccade command amplitude, expressed in
        degrees per unit of sheet.  Indicates how large a
        saccade is represented by the x-component of the command
        input.""")
    
    direction_scale = Number(default=1,doc="""
        Scale factor for saccade command direction, expressed in
        degrees per unit of sheet.  Indicates what direction of saccade
        is represented by the y-component of the command input.""")
    

    def __call__(self,x,y):
        raise NotImplementedError        

class OttesSCMotorMapper(OttesSCMapper):
    """
    Efferent superior colliculus mapping.

    Provides the output/motor mapping from SC as defined by Ottes et al.
    (see superclass docs for reference)

    The mapping allows the creation of a single sheet representing
    both colliculi, one in the x-positive hemisheet and the other in
    the x-negative hemisheet.
    """
    def __call__(self,x,y):

        A = self.A 
        Bu = self.Bu / self.mm_scale
        Bv = self.Bv / self.mm_scale 

        R = x * self.amplitude_scale 
        phi = y * self.direction_scale

        Rsign,R = signabs(R)

        u,v = ottes_mapping(R,phi,A,Bu,Bv)
        return Rsign*u,v

        

class OttesSCSenseMapper(OttesSCMapper):
    """
    Afferent superior colliculus mapping.

    Provides the input/retinal mapping to SC as defined by Ottes et al.
    (see superclass docs for reference)

    The mapping allows the creation of a single sheet representing
    both colliculi, one in the x-positive hemisheet and the other in
    the x-negative hemisheet.

    [NOTE: see warning in docs for ottes_inverse_mapping()]
    """

    def __call__(self,x,y):

        A = self.A 
        Bu = self.Bu 
        Bv = self.Bv 

        u = x * self.mm_scale
        v = y * self.mm_scale

        usgn,u = signabs(u)

        R,phi = ottes_inverse_mapping(u,v,A,Bu,Bv)

        return (usgn*R/self.amplitude_scale,
                phi/self.direction_scale)


def ottes_mapping(R,phi,A,Bu,Bv):
    """
    The efferent mapping function from Ottes et al. (1986)
    Vision Research 26:857-873.

    Takes saccade with amplitude R (in degrees) and direction
    phi (in degrees), and returns a location u,v on the colliculus
    in mm, where the u axis is rostral/caudal, and the v axis  is
    medial/lateral.
    """
    phi *= pi/180
    u = Bu * (log(sqrt(R**2 + A**2 + 2*A*R*cos(phi))) - log(A))
    v = Bv * atan((R*sin(phi))/(R*cos(phi)+A))        
    return u,v

def ottes_inverse_mapping(u,v,A,Bu,Bv):
    """
    The inverse funtion provided in the appendix of Ottes et al. (1986)
    Vision Research 26:857-873

    Supposedly takes a location u,v on the colliculus in mm and maps
    to a retinal eccentricity R and direction phi, in degrees.
    However, this function is not actually the mathematical inverse of
    the forward mapping, nor even close.  
    """
    # JPALERT: As mentioned above, this is not actually the inverse of
    # the efferent mapping. I believe the formula in the paper is
    # in error, though it's possible that there's a bug below that
    # I've missed.
    
    rads = pi/180
    R   = A * sqrt(exp(2*u/Bu) - 2*exp(u/Bu)*cos(rads*v/Bv) + 1)
    phi = atan( (exp(u/Bu)*sin(rads*v/Bv)) / (exp(u/Bu)*cos(rads*v/Bv) -1) )
    return R,phi*180/pi
                 

