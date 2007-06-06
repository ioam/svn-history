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

from numpy import exp,log,sqrt,sin,cos,zeros,ones,dot,array
from numpy.matlib import matrix, zeros as mzeros
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


class AffineTransform(CoordinateMapperFn):
    """
    Remaps the input with an affine transform.

    This mapper allows the specification of an arbitrary combination
    of translation, rotation and scaling via a transform
    matrix. Single translations, etc, can be specified more simply
    with the subclasses Translate2d, Rotate2d, and Scale2d.

    """
    
    matrix = Parameter(default=ones((3,3)),

       doc="""The affine transformation matrix.  The functions
       Translate2dMat, Rotate2dMat, and Scale2dMat generate affine
       transform matrices that can be multiplied together to create
       combination transforms.  E.g. the matrix

       Translate2dMat(3,0)*Rotate2d(pi/2)

       will shift points to the right by 3 units and rotate them around
       the origin by 90 degrees.""")

    def __init__(self, **kw):
        super(AffineTransform,self).__init__(**kw)

        # This buffer prevents having to allocate memory for each point.
        self._op_buf = matrix([[0.0],
                               [0.0],
                               [1.0]])
                               
        
    def __call__(self, x, y):


        ## JPHACKALERT: If the coordmapper interface took a matrix of
        ## x/y column vectors, instead of x and y separately, affine
        ## transforms could be applied to all the points in a single
        ## matrix operation.  This would probably require revision of
        ## some of the other coordmapper functions, but it might allow
        ## some optimization in, e.g., CFProjection intialization by
        ## allowing all the CF positions to be computed at once.

        ## JPALERT: This is the easy way, but it allocates a matrix
        ## for the result.  It might be faster to unroll the
        ## computation.

        self._op_buf[0] = x
        self._op_buf[1] = y
        result = dot(self.matrix,self._op_buf)
               
        return result[0,0],result[1,0]

def Translate2dMat(xoff,yoff):
    """
    Return an affine transformation matrix that translates points by
    the offset (xoff,yoff).
    """
    return matrix([[1, 0, xoff],
                   [0, 1, yoff],
                   [0, 0,   1 ]])

def Rotate2dMat(t):
    """
    Return an affine transformation matrix that rotates the points
    around the origin by t radians.
    """
    return matrix([[cos(t), -sin(t), 0],
                   [sin(t),  cos(t), 0],
                   [  0   ,    0   , 1]])

def Scale2dMat(sx,sy):
    """
    Return an affine translation matrix that scales the points
    toward/away from the origin by a factor of sx on x-axis and sy on
    the y-axis.
    """
    return matrix([[sx,  0, 0],
                   [ 0, sy, 0],
                   [ 0,  0, 1]])


def Translate2d(AffineTransform):
    """
    Translate the input by xoff,yoff.
    """
    xoff = Number(default=0.0)
    yoff = Number(default=0.0)

    def __init__(self,**kw):
        super(Translate2d,self).__init__(**kw)
        self.matrix = Translate2dMat(self.xoff,self.yoff)

def Rotate2d(AffineTransform):
    """
    Rotate the input around the origin by an angle in radians.
    """
    angle = Number(default=0.0)

    def __init__(self,**kw):
        super(Rotate2d,self).__init__(**kw)
        self.matrix = Rotate2dMat(self.angle)

def Scale2d(AffineTransform):
    """
    Scale the input along the x and y axes by sx an sy, respectively.
    """
    sx = Number(default=1.0)
    sy = Number(default=1.0)

    def __init__(self,**kw):
        super(Scale2d2dMat,self).__init__(**kw)
        self.matrix = Scale2d2dMat(self.sx,self.sy)



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
                 

