"""
Simple functions operating on a matrix, potentially modifying it.

These are useful for neuron output functions, normalization of
matrices, etc.

All of these function objects (callable objects) should work for
Numpy array arguments of arbitrary shape.  Some may also work for
scalars.

$Id$
"""
__version__='$Revision$'


import numpy, numpy.random
import numpy.oldnumeric as Numeric
import copy
import topo

from numpy import exp,zeros,ones
from numpy.oldnumeric import dot, exp
from math import ceil


from topo.base.sheet import activity_type
from topo.base.arrayutils import clip_lower
from topo.base.arrayutils import L2norm, norm, array_argmax
from topo.base.functionfamilies import OutputFn, OutputFnWithState, OutputFnParameter
from topo.base.parameterclasses import Parameter,Number,ListParameter,BooleanParameter, StringParameter
from topo.base.parameterizedobject import ParameterizedObject
from topo.base.patterngenerator import PatternGeneratorParameter,Constant
from topo.base.boundingregion import BoundingBox
from topo.patterns.basic import Gaussian

# Imported here so that all OutputFns will be in the same package
from topo.base.functionfamilies import IdentityOF,PipelineOF

Pipeline = PipelineOF

# CEBHACKALERT: these need to respect the mask - which will be passed in.


class PiecewiseLinear(OutputFn):
    """ 
    Piecewise-linear OutputFn with lower and upper thresholds.
    
    Values below the lower_threshold are set to zero, those above
    the upper threshold are set to 1.0, and those in between are
    scaled linearly.
    """
    lower_bound = Number(default=0.0,softbounds=(0.0,1.0))
    upper_bound = Number(default=1.0,softbounds=(0.0,1.0))
    
    def __call__(self,x):
        fact = 1.0/(self.upper_bound-self.lower_bound)        
        x -= self.lower_bound
        x *= fact
        x.clip(0.0,1.0,out=x)



class Sigmoid(OutputFn):
    """ 
    Sigmoidal (logistic) output function: 1/(1+exp-(r*x+k)).

    As defined in Jochen Triesch, ICANN 2005, LNCS 3696 pp. 65-70. 
    The parameters control the growth rate (r) and the x position (k)
    of the exponential.
    
    This function is a special case of the GeneralizedLogistic
    function, with parameters r=r, l=0, u=1, m=-k/2r, and b=1.  See
    Richards, F.J. (1959), A flexible growth function for empirical
    use. J. Experimental Botany 10: 290--300, 1959.
    http://en.wikipedia.org/wiki/Generalised_logistic_curve
    """
    
    r = Number(default=1,doc="Parameter controlling the growth rate")
    k = Number(default=0,doc="Parameter controlling the x-postion")
    
    def __call__(self,x):
        x_orig = copy.copy(x)
        x *= 0.0
	x += 1.0 / (1.0 + exp(-(self.r*x_orig+self.k)))


                  
class NakaRushton(OutputFn):
    #JABALERT: Please write the equation into words in the docstring, as in Sigmoid.
    """
    Naka-Rushton curve.

    From Naka, K. and Rushton, W. (1996), S-potentials from luminosity
    units in the retina of fish (Cyprinidae). J. Physiology 185:587-599.

    The Naka-Rushton curve has been shown to be a good approximation
    of constrast gain control in cortical neurons.  The input of the
    curve is usually contrast, but under the assumption that the
    firing rate of a model neuron is directly proportional to the
    contrast, it can be used as an OutputFn for a Sheet.
    
    The parameter c50 corresponds to the contrast at which the half of
    the maximal output is reached.  For a Sheet OutputFn this translates
    to the input for which a neuron will respond with activity 0.5.
    """
    
    c50 = Number(default=0.1, doc="""
        The input of the neuron at which it responds at half of its maximal firing rate (1.0).""")

    e = Number(default=1.0,doc="""The exponent of the input x.""")

    #JABALERT: (pow(x_orig,self.e) should presumably be done only once, using a temporary
    def __call__(self,x):
        #print 'A:', x
        #print 'B:', pow(x,self.e) / (pow(x,self.e) + pow(self.c50,self.e))
        x_orig = copy.copy(x)
        x *= 0
        x += pow(x_orig,self.e) / (pow(x_orig,self.e) + pow(self.c50,self.e))



class GeneralizedLogistic(OutputFn):
    """ 
    The generalized logistic curve (Richards' curve): y = l + (u /(1 + b * exp(-r*(x-2*m))^(1/b))).

    The logistic curve is a flexible function for specifying a
    nonlinear growth curve using five parameters:

    * l: the lower asymptote
    * u: the upper asymptote minus l
    * m: the time of maximum growth
    * r: the growth rate
    * b: affects near which asymptote maximum growth occurs

    From Richards, F.J. (1959), A flexible growth function for empirical
    use. J. Experimental Botany 10: 290--300.
    http://en.wikipedia.org/wiki/Generalised_logistic_curve
    """
    
    # JABALERT: Reword these to say what they are, not what they
    # control, if they are anything that can be expressed naturally.
    # E.g. is l a parameter controlling the lower asymptote, or is it
    # simply the lower asymptote?  If it's the lower asymptote, say
    # doc="Lower asymptote.".  Only if the parameter's relationship to
    # what it controls is very indirect should it be worded as below.
    l = Number(default=1,doc="Parameter controlling the lower asymptote.")
    u = Number(default=1,doc="Parameter controlling the upper asymptote (upper asymptote minus lower asymptote.")
    m = Number(default=1,doc="Parameter controlling the time of maximum growth.")
    r = Number(default=1,doc="Parameter controlling the growth rate.")
    b = Number(default=1,doc="Parameter which affects near which asymptote maximum growth occurs.")
    
    def __call__(self,x):
        x_orig = copy.copy(x)
        x *= 0.0
        x += self.l + ( self.u /(1 + self.b*exp(-self.r *(x_orig - 2*self.m))**(1 / self.b)) )    



class DivisiveNormalizeL1(OutputFn):
    """
    OutputFn that divides an array by its L1 norm.

    This operation ensures that the sum of the absolute values of the
    array is equal to the specified norm_value, rescaling each value
    to make this true.  The array is unchanged if the sum of absolute
    values is zero.  For arrays of non-negative values where at least
    one is non-zero, this operation is equivalent to a divisive sum
    normalization.
    """
    norm_value = Number(default=1.0)

    def __call__(self,x):
        """L1-normalize the input array, if it has a nonzero sum."""
        current_sum = 1.0*Numeric.sum(abs(x.ravel()))
        if current_sum != 0:
            factor = (self.norm_value/current_sum)
            x *= factor



class DivisiveNormalizeL2(OutputFn):
    """
    OutputFn to divide an array by its Euclidean length (aka its L2 norm).

    For a given array interpreted as a flattened vector, keeps the
    Euclidean length of the vector at a specified norm_value.
    """
    norm_value = Number(default=1.0)
    
    def __call__(self,x):
        tot = 1.0*L2norm(x.ravel())
        if tot != 0:
            factor = (self.norm_value/tot)
            x *= factor



class DivisiveNormalizeLinf(OutputFn):
    """
    OutputFn to divide an array by its L-infinity norm
    (i.e. the maximum absolute value of its elements).

    For a given array interpreted as a flattened vector, scales the
    elements divisively so that the maximum absolute value is the
    specified norm_value.

    The L-infinity norm is also known as the divisive infinity norm
    and Chebyshev norm.
    """
    norm_value = Number(default=1.0)
    
    def __call__(self,x):
        tot = 1.0*max(abs(x.ravel()))
        if tot != 0:
            factor = (self.norm_value/tot)
            x *= factor


    
class DivisiveNormalizeLp(OutputFn):
    """
    OutputFn to divide an array by its Lp-Norm, where p is specified.

    For a parameter p and a given array interpreted as a flattened
    vector, keeps the Lp-norm of the vector at a specified norm_value.
    Faster versions are provided separately for the typical L1-norm
    and L2-norm cases.  Defaults to be the same as an L2-norm, i.e.,
    DivisiveNormalizeL2.
    """
    p = Number(default=2)
    norm_value = Number(default=1.0)
    
    def __call__(self,x):
        tot = 1.0*norm(x.ravel(),self.p)
        if tot != 0:
            factor = (self.norm_value/tot)
            x *=factor 



class HalfRectifyAndSquare(OutputFn):
    """
    Output function that applies a half-wave rectification (clips at zero)
    and then squares the values.
    """
    lower_bound = Number(default=0.0,softbounds=(0.0,1.0))
    
    def __call__(self,x):
        clip_lower(x,self.lower_bound)
        x *= x



class HalfRectify(OutputFn):
    """
    Output function that applies a half-wave rectification (clips at zero)
    
    """
    lower_bound = Number(default=0.0,softbounds=(0.0,1.0))
    
    def __call__(self,x):
        clip_lower(x,self.lower_bound)



class Square(OutputFn):
    """Output function that applies a squaring nonlinearity."""

    def __call__(self,x):
        x *= x     
        


class BinaryThreshold(OutputFn):
    """
    Forces all values below a threshold to zero, and above it to 1.0.
    """
    threshold = Number(default=0.25, doc="Decision point for determining binary value.")

    def __call__(self,x):
        above_threshold = x>=self.threshold
        x *= 0.0
        x += above_threshold



### JABALERT: Is this the right location for this class?  It brings in
### dependencies on PatternGenerator, which is not something that many
### OutputFns will need.
class PatternCombine(OutputFn):
    """
    Combine the supplied pattern with one generated using a
    PatternGenerator.

    Useful for operations like adding noise or masking out lesioned
    items or around the edges of non-rectangular shapes.
    """
    generator = PatternGeneratorParameter(default=Constant(), doc="""
        Pattern to combine with the supplied matrix.""")

    operator = Parameter(numpy.multiply,precedence=0.98,doc="""
        Binary Numeric function used to combine the two patterns.

        Any binary Numeric array "ufunc" returning the same type of
        array as the operands and supporting the reduce operator is
        allowed here.  See topo.patterns.basic.Composite.operator for
        more details.              
        """)
    
    def __call__(self,x):
        ###JABHACKALERT: Need to set it up to be independent of
        #density; right now only things like random numbers work
        #reasonably
        rows,cols = x.shape
        bb = BoundingBox(points=((0,0), (rows,cols)))
        new_pattern = self.operator(x, self.generator(bounds=bb,xdensity=1,ydensity=1))
        x *= 0.0
        x += new_pattern



### JABALERT: Is this the right location for this class?  It brings in
### dependencies on PatternGeneratorParameter and Gaussian, which are
### not things that many OutputFns will need.  Perhaps move to som.py?
class KernelMax(OutputFn):
    """
    Replaces the given matrix with a kernel function centered around the maximum value.

    This operation is usually part of the Kohonen SOM algorithm, and
    approximates a series of lateral interactions resulting in a
    single activity bubble.

    The radius of the kernel (i.e. the surround) is specified by the
    parameter 'radius', which should be set before using __call__.
    The shape of the surround is determined by the
    neighborhood_kernel_generator, and can be any PatternGenerator
    instance, or any function accepting bounds, density, radius, and
    height to return a kernel matrix.
    """
    kernel_radius = Number(default=0.0,bounds=(0,None),doc="""
        Kernel radius in Sheet coordinates.""")
    
    neighborhood_kernel_generator = PatternGeneratorParameter(
        default=Gaussian(x=0.0,y=0.0,aspect_ratio=1.0),
        doc="Neighborhood function")

    crop_radius_multiplier = Number(default=3.0,doc="""        
        Factor by which the radius should be multiplied, when deciding
        how far from the winner to keep evaluating the kernel.""")
    
    density=Number(1.0,bounds=(0,None),doc="""
        Density of the Sheet whose matrix we act on, for use
        in converting from matrix to Sheet coordinates.""")
    
    def __call__(self,x):
        rows,cols = x.shape
        radius = self.density*self.kernel_radius
        crop_radius = int(max(1.25,radius*self.crop_radius_multiplier))
        
        # find out the matrix coordinates of the winner
        wr,wc = array_argmax(x)
        
        # convert to sheet coordinates
        wy = rows-wr-1
        
        # Optimization: Calculate the bounding box around the winner
        # in which weights will be changed
        cmin = max(wc-crop_radius,  0)
        cmax = min(wc+crop_radius+1,cols)
        rmin = max(wr-crop_radius,  0)
        rmax = min(wr+crop_radius+1,rows)
        ymin = max(wy-crop_radius,  0)
        ymax = min(wy+crop_radius+1,rows)
        bb = BoundingBox(points=((cmin,ymin), (cmax,ymax)))
        
        # generate the kernel matrix and insert it into the correct
        # part of the output array
        kernel = self.neighborhood_kernel_generator(bounds=bb,xdensity=1,ydensity=1,
                                                    size=2*radius,x=wc+0.5,y=wy+0.5)
        x *= 0.0
        x[rmin:rmax,cmin:cmax] = kernel



class PoissonSample(OutputFn):
    """
    Simulate Poisson-distributed activity with specified mean values.
    
    This output function interprets each matrix value as the
    (potentially scaled) rate of a Poisson process and replaces it
    with a sample from the appropriate Poisson distribution.

    To allow the matrix to contain values in a suitable range (such as
    [0.0,1.0]), the input matrix is scaled by the parameter in_scale,
    and the baseline_rate is added before sampling.  After sampling,
    the output value is then scaled by out_scale.  The function thus
    performs this transformation::

      x <- P(in_scale * x + baseline_rate) * out_scale

    where x is a matrix value and P(r) samples from a Poisson
    distribution with rate r.
    """
    
    in_scale = Number(default=1.0,doc="""
       Amount by which to scale the input.""")
    
    baseline_rate = Number(default=0.0,doc="""
       Constant to add to the input after scaling, resulting in a baseline
       Poisson process rate.""")
    
    out_scale = Number(default=1.0,doc="""
       Amount by which to scale the output (e.g. 1.0/in_scale).""")

    def __call__(self,x):
        
        x *= self.in_scale
        x += self.baseline_rate
        sample = numpy.random.poisson(x,x.shape)
        x *= 0.0
        x += sample
        x *= self.out_scale



class AttributeTrackingOF(OutputFnWithState):
    """
    Keeps track of attributes of a specified ParameterizedObject over time, for analysis or plotting.

    Useful objects to track include sheets (e.g. "topo.sim['V1']"),
    projections ("topo.sim['V1'].projections['LateralInhibitory']"),
    or an output_function.  

    Any attribute whose value is a matrix the same size as the
    activity matrix can be tracked.  Only specified units within this
    matrix will be tracked.
    
    If no object is specified, this function will keep track of the
    incoming activity over time.

    The results are stored in a dictionary named 'values', as (time,
    value) pairs indexed by the parameter name and unit.  For
    instance, if the value of attribute 'x' is v for unit (0,0)
    at time t, values['x'][(0,0)]=(t,v).

    Updating of the tracked values can be disabled temporarily using
    the updating parameter.
    """
    
    object = Parameter(default=None, doc="""
        ParameterizedObject instance whose parameters will be tracked.

        If this parameter's value is a string, it will be evaluated first
        (by calling Python's eval() function).  This feature is designed to
        allow circular references, so that the OF can track the object that
        owns it, without causing problems for recursive traversal (as for
        script_repr()).""")
    # There may be some way to achieve the above without using eval(), which would be better.
    
    attrib_names = ListParameter(default=[], doc="""
        List of names of the function object's parameters that should be stored.""")
    
    units = ListParameter(default=[(0,0)], doc="""
        Matrix coordinates of the unit(s) for which parameter values will be stored.""")
    
    step = Number(default=1, doc="""
        How often to update the tracked values.

        For instance, step=1 means to update them every time this OF is
        called; step=2 means to update them every other time.""")


    def __init__(self,**params):
        super(AttributeTrackingOF,self).__init__(**params)
        self.values={}
        self.n_step = 0
        self._object=None
        for p in self.attrib_names:
            self.values[p]={}
            for u in self.units:
                self.values[p][u]=[]
         
        
    def __call__(self,x):
        if self.updating:
            if self._object==None:
                if isinstance(self.object,str):
                    self._object=eval(self.object)
                else:
                    self._object=self.object
            
            #collect values on each appropriate step
            self.n_step += 1
        
            if self.n_step == self.step:
                self.n_step = 0
                for p in self.attrib_names:
                    if p=="x":
                        value_matrix=x
                    else:
                        value_matrix= getattr(self._object, p)
                        
                    for u in self.units:
                        self.values[p][u].append((topo.sim.time(),value_matrix[u]))
          


class ActivityAveragingOF(OutputFnWithState):
    """
    Calculates the average of the input activity.

    The average is calculated as an exponential moving average, where
    the weighting for each older data point decreases exponentially.
    The degree of weighing for the previous values is expressed as a
    constant smoothing factor.

    The updating parameter allows the updating of the average values
    to be disabled temporarily, e.g. while presenting test patterns.
    """

    step = Number(default=1, doc="""
        How often to update the average.

        For instance, step=1 means to update it every time this OF is
        called; step=2 means to update it every other time.""")
    
    smoothing = Number(default=0.9997, doc="""
        The degree of weighting for the previous average, when calculating the new average.""")
   
    initial_average=Number(default=0, doc="Starting value for the average activity.")

    
    def __init__(self,**params):
        super(ActivityAveragingOF,self).__init__(**params)
        self.n_step = 0
        self.x_avg=None


    def __call__(self,x):
        if self.x_avg is None:
            self.x_avg=self.initial_average*ones(x.shape, activity_type)         

        # Collect values on each appropriate step
        if self.updating:
            self.n_step += 1
            if self.n_step == self.step:
                self.n_step = 0
                self.x_avg = (1.0-self.smoothing)*x + self.smoothing*self.x_avg



__all__ = list(set([k for k,v in locals().items() if isinstance(v,type) and issubclass(v,OutputFn)]))
