"""
Family of two-dimensional functions indexed by x and y.

All functions are written to be valid both for scalar x and y, and for
Numeric arrays of x and y (in which case the result is also an array);
the functions therefore have the same mathematical behaviour as Numeric.

$Id$
"""
__version__='$Revision$'



from math import pi

from Numeric import where,maximum,cos,sin,sqrt,less_equal,divide,greater_equal,bitwise_xor

from Numeric import zeros,ones
from RandomArray import random,seed

from topo.base.arrayutils import exp


# CEB: Divide is imported from Numeric so that mathematical
# expressions with scalars (such as exp(-(3.0/0.0)) ) are evaluated
# correctly. Unfortunately this makes such expressions more difficult
# to read. How can Numeric's / operator be made to override Python's /
# operator for scalars?


# Taken from matplotlib.mlab; may be temporary
def fix(x):

    """
    Rounds towards zero.
    x_rounded = fix(x) rounds the elements of x to the nearest integers
    towards zero.
    For negative numbers is equivalent to ceil and for positive to floor.
    """
    
    dim = numerix.shape(x)
    if numerix.mlab.rank(x)==2:
        y = reshape(x,(1,dim[0]*dim[1]))[0]
        y = y.tolist()
    elif numerix.mlab.rank(x)==1:
        y = x
    else:
        y = [x]
    for i in range(len(y)):
	if y[i]>0:
		y[i] = floor(y[i])
	else:
		y[i] = ceil(y[i])
    if numerix.mlab.rank(x)==2:
        x = reshape(y,dim)
    elif numerix.mlab.rank(x)==0:
        x = y[0]
    return x



def gaussian(x, y, xsigma, ysigma):
    """
    Two-dimensional oriented Gaussian pattern (i.e., 2D version of a
    bell curve, like a normal distribution but not necessarily summing
    to 1.0).
    """
    x_w = divide(x,xsigma)
    y_h = divide(y,ysigma)
    return exp(-0.5*x_w*x_w + -0.5*y_h*y_h)


def gabor(x, y, xsigma, ysigma, frequency, phase):
    """
    Gabor pattern (sine grating multiplied by a circular Gaussian).
    """ 
    x_w = divide(x,xsigma)
    y_h = divide(y,ysigma)
    p = exp(-0.5*x_w*x_w + -0.5*y_h*y_h)    
    return p * (0.5 + 0.5*cos(2*pi*frequency*y + phase))


def line(y, thickness, gaussian_width):
    """
    Infinite-length line with a solid central region, then Gaussian fall-off at the edges.
    """
    distance_from_line = abs(y)
    gaussian_y_coord = distance_from_line - thickness/2.0
    sigmasq = gaussian_width*gaussian_width
    falloff = __exp(-gaussian_y_coord*gaussian_y_coord, 2*sigmasq)
    return where(gaussian_y_coord<=0, 1.0, falloff)


def disk(x, y, width, height, gaussian_width):
    """
    Elliptical disk with Gaussian fall-off after the solid central region.
    """
    disk_perimeter = __ellipse_dist(x,y,width/2.0,height/2.0)  
    disk = greater_equal(disk_perimeter,0)

    sigmasq = gaussian_width*gaussian_width
    falloff = __exp(-disk_perimeter*disk_perimeter, 2.0*sigmasq)

    return maximum(disk, falloff)


def ring(x, y, width, height, thickness, gaussian_width):
    """
    Elliptical ring (annulus) with Gaussian fall-off after the solid ring-shaped region.
    """    
    ellipse_dist = __ellipse_dist(x,y,width/2.0,height/2.0)  

    inner_perimeter = ellipse_dist - thickness
    outer_perimeter = ellipse_dist + thickness

    ring = bitwise_xor(greater_equal(inner_perimeter,0.0),greater_equal(outer_perimeter,0.0)) 

    sigmasq = gaussian_width*gaussian_width
    inner_falloff = __exp(-inner_perimeter*inner_perimeter, 2.0*sigmasq)
    outer_falloff = __exp(-outer_perimeter*outer_perimeter, 2.0*sigmasq)

    return maximum(inner_falloff,maximum(outer_falloff,ring))


def rds(xsize,ysize,xdisparity,ydisparity,dotdensity,dotsize,gen_seed):


    xsize=int(round(xsize))
    ysize=int(round(ysize))
    xdisparity=int(round(xdisparity))
    ydisparity=int(round(ydisparity))
    dotsize=int(round(dotsize))
    gen_seed=int(round(gen_seed))
    
    bigxsize = 2*xsize
    bigysize = 2*ysize
    ndots=int(round(dotdensity * (bigxsize+2*dotsize) * (bigysize+2*dotsize) / min(dotsize,xsize) / min(dotsize,ysize)))
    halfdot = fix(dotsize/2)

    ###TRALERT:
    
    ###TRALERT:For Test Pattern Window
    bigimage = 0.5*ones((bigysize,bigxsize))

    ###TRALERT:For Energy models
    '''
    bigimage = zeros((bigysize,bigxsize))
    '''
    
    xpos=zeros((1,ndots))
    ypos=zeros((1,ndots))
    x1=zeros((1,ndots))
    y1=zeros((1,ndots))
    x2=zeros((1,ndots))
    y2=zeros((1,ndots))
    col=zeros((1,ndots))

    
    seed(gen_seed*12,gen_seed*99)
    col=random((1,ndots))

    seed(gen_seed*122,gen_seed*799)
    xpos=fix(random((1,ndots))*(bigxsize+2*dotsize)) - halfdot

    seed(gen_seed*1243,gen_seed*9349)
    ypos=fix(random((1,ndots))*(bigysize+2*dotsize)) - halfdot
  
    
    for i in range(ndots):

        ###TRALERT:For Test Pattern Window,white is represented as 1 and black as 0. background is 0.5
        ###alternatively, offset parameter can be set properly
        
        if col[0][i] >= 0.5:
            col[0][i]= 1
        else:
            col[0][i]= 0
        
        
        ###TRALERT:For testing energy models, white==1, black==-1,background=0 (similar to Read's code)
        '''
        if col[0][i] >= 0.5:
            col[0][i]= 1
        else:
            col[0][i]= -1
        '''
        
        x1[0][i]= max(xpos[0][i],0)
        x2[0][i]= min(xpos[0][i] + dotsize-1,bigxsize)
        y1[0][i] = max(ypos[0][i],0)
        y2[0][i] = min(ypos[0][i] + dotsize-1,bigysize)
        bigimage[y1[0][i]:y2[0][i]+1,x1[0][i]:x2[0][i]+1] = col[0][i]
        
    image = bigimage[ (ysize/2)+ydisparity:(3*ysize/2)+ydisparity , (xsize/2)+xdisparity:(3*xsize/2)+xdisparity ]
    
    return image

    





# JABHACKALERT:  The __ellipse_dist function needs to be reimplemented
# with a function that actually computes the distance from point (x,y)
# to the nearest point on the ellipse; this one does not.  The result
# is that the falloffs for ring() and disk() are not correct; try 
# comparing them with those for line().

def __ellipse_dist(x,y,a,b):
    """
    For an ellipse consisting of all points (x1,y1) where 
    (x1/a)^2 + (y1/b)^2 = 1, should return the distance from (x,y) to the
    nearest point on the ellipse.  Negative distance represents points
    outside of the ellipse.
    
    Bug: the value returned is currently related to the distance, but is
    not the same quantity; it needs to be corrected.
    """
    x_a = divide(x,float(a))
    y_b = divide(y,float(b))
    
    return 1.0 - (x_a*x_a + y_b*y_b)  


def __exp(x,denom):
    """
    Special-case exp() function for some functions in this file:

    Return  0.0             if x==0.0 and denom==0
            exp(x/denom)    otherwise

    Functions in this file that calculate an exp(x/denom) need
    to have well-defined behaviour when x is 0, whatever the value
    of denom.
    """
    # x/denom==nan if x==denom==0; 0 is returned in that case
    return where(x!=0.0, exp(divide(x,float(denom))),0.0)


                
           

