"""
Random-dot stereogram patterns.

$Id$
"""
__version__='$Revision$'

from Numeric import zeros,ones,floor,where,choose,less,greater,Int
from RandomArray import random,seed

from topo.base.parameterclasses import Number,Integer
from topo.base.patterngenerator import PatternGenerator
from topo.base.sheetcoords import SheetCoordinateSystem
from topo.base.functionfamilies import IdentityOF

from topo.base.arrayutils import clip_lower


### JABHACKALERT: This code seems to work fine when the input regions
### are all the same size and shape, but for
### e.g. examples/hierarchical.ty the resulting images in the Test
### Pattern preview window are square (instead of the actual
### rectangular shapes), matching between the eyes (instead of the
### actual two different rectangles), and with dot sizes that don't
### match between the eyes.  It's not clear why this happens.

class RandomDotStereogram(PatternGenerator):
    """
    Random dot stereogram using rectangular black and white patches.

    Based on Matlab code originally from Jenny Read, implemented in
    Topographica by Tikesh Ramtohul (2006).
    """

    # Suppress unused parameters
    x = Number(hidden=True)
    y = Number(hidden=True)
    size = Number(hidden=True)
    orientation = Number(hidden=True)

    # Override defaults to make them appropriate
    scale  = Number(default=0.5)
    offset = Number(default=0.5)

    # New parameters for this pattern

    #JABALERT: Should rename xdisparity and ydisparity to x and y, and simply
    #set them to different values for each pattern to get disparity
    xdisparity = Number(default=0.0,bounds=(-1.0,1.0),softbounds=(-0.5,0.5),
                        precedence=0.50,doc="Disparity in the horizontal direction.")
    
    ydisparity = Number(default=0.0,bounds=(-1.0,1.0),softbounds=(-0.5,0.5),
                        precedence=0.51,doc="Disparity in the vertical direction.")
    
    dotdensity = Number(default=0.5,bounds=(0.0,None),softbounds=(0.1,0.9),
                        precedence=0.52,doc="Number of dots per unit area; 0.5=50% coverage.")

    dotsize    = Number(default=0.1,bounds=(0.0,None),softbounds=(0.05,0.15),
                        precedence=0.53,doc="Edge length of each square dot.")

    random_seed=Integer(default=500,bounds=(0,1000),
                        precedence=0.54,doc="Seed value for the random position of the dots.")


    def __call__(self,**params):

        # Gather parameters
        self._check_params(params)
        
        bounds      = params.get('bounds',self.bounds)
        xdensity    = params.get('xdensity',self.xdensity)
        ydensity    = params.get('ydensity',self.ydensity)
        scale       = params.get('scale',self.scale)
        offset      = params.get('offset',self.offset)
        output_fn   = params.get('output_fn',self.output_fn)
        dotdensity  = params.get('dotdensity',self.dotdensity)
        random_seed = params.get('random_seed',self.random_seed)

        xsize,ysize = SheetCoordinateSystem(bounds,xdensity,ydensity).shape
        xsize,ysize = int(round(xsize)),int(round(ysize))
        
        xdisparity  = int(round(xsize*params.get('xdisparity',self.xdisparity)))
        ydisparity  = int(round(xsize*params.get('ydisparity',self.ydisparity)))
        dotsize     = int(round(xsize*params.get('dotsize',self.dotsize)))
        
        bigxsize = 2*xsize
        bigysize = 2*ysize
        ndots=int(round(dotdensity * (bigxsize+2*dotsize) * (bigysize+2*dotsize) /
                        min(dotsize,xsize) / min(dotsize,ysize)))
        halfdot = floor(dotsize/2)
    
        # Choose random colors and locations of square dots
        seed(random_seed*12,random_seed*99)
        col=where(random((ndots))>=0.5, 1.0, -1.0)

        seed(random_seed*122,random_seed*799)
        xpos=floor(random((ndots))*(bigxsize+2*dotsize)) - halfdot
    
        seed(random_seed*1243,random_seed*9349)
        ypos=floor(random((ndots))*(bigysize+2*dotsize)) - halfdot
      
        # Construct arrays of points specifying the boundaries of each
        # dot, cropping them by the big image size (0,0) to (bigxsize,bigysize)
        x1=xpos.astype(Int) ; x1=choose(less(x1,0),(x1,0))
        y1=ypos.astype(Int) ; y1=choose(less(y1,0),(y1,0))
        x2=(xpos+(dotsize-1)).astype(Int) ; x2=choose(greater(x2,bigxsize),(x2,bigxsize))
        y2=(ypos+(dotsize-1)).astype(Int) ; y2=choose(greater(y2,bigysize),(y2,bigysize))

        # Draw each dot in the big image, on a blank background
        bigimage = zeros((bigysize,bigxsize))
        for i in range(ndots):
            bigimage[y1[i]:y2[i]+1,x1[i]:x2[i]+1] = col[i]
            
        result = offset + scale*bigimage[ (ysize/2)+ydisparity:(3*ysize/2)+ydisparity ,
                                          (xsize/2)+xdisparity:(3*xsize/2)+xdisparity ]

        if output_fn is not IdentityOF:
            output_fn(result)

        return result
