"""
Random-dot stereogram patterns.

$Id$
"""
__version__='$Revision$'


from Numeric import zeros,ones
from RandomArray import random,seed

from topo.base.parameterclasses import Number
from topo.base.patterngenerator import PatternGenerator
from topo.base.sheetcoords import SheetCoordinateSystem
from topo.base.functionfamilies import OutputFnParameter, IdentityOF


# Taken from matplotlib.mlab; can probably be replaced with floor() or ceil().
def fix(x):

    """
    Rounds towards zero.
    x_rounded = fix(x) rounds the elements of x to the nearest integers
    towards zero.
    For negative numbers is equivalent to ceil and for positive to floor.
    """
    from matplotlib import numerix
    from Numeric import floor,ceil,reshape
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


class RandomDotStereogram(PatternGenerator):
    """
    Random dot stereogram based on rectangular black and white patches.
    """

    # Suppress unused parameters
    x = Number(hidden = True)
    y = Number(hidden = True)
    orientation = Number(hidden = True)
    

    # New parameters for this pattern
    xdisparity = Number(default=0.0,bounds=(-1.0,1.0),softbounds=(-0.5,0.5),
                precedence=0.50,doc="Horizontal Disparity.")
    
    ydisparity = Number(default=0.0,bounds=(-1.0,1.0),softbounds=(-0.5,0.5),
                precedence=0.51,doc="Vertical Disparity.")

    dotdensity = Number(default=0.5,bounds=(0.0,1.0),softbounds=(0.1,0.9),
                precedence=0.52,doc="controls number of dots, 0.5=50% coverage.")

    dotsize = Number(default=0.1,bounds=(0.0,1.0),softbounds=(0.05,0.15),
                precedence=0.53,doc="edgelength of square dots.")

    random = Number(default=500,bounds=(0.0,1000.0),softbounds=(0.0,1000.0),
                precedence=0.54,doc="controls the position of the dots")


    def __call__(self,**params):
        
        self._check_params(params)
        
        bounds = params.get('bounds',self.bounds)
        xdensity = params.get('xdensity',self.xdensity)
        ydensity = params.get('ydensity',self.ydensity)
        scale = params.get('scale',self.scale)
        offset = params.get('offset',self.offset)
        output_fn = params.get('output_fn',self.output_fn)

        xsize,ysize = SheetCoordinateSystem(bounds,xdensity,ydensity).shape
        
        xdisparity  = params.get('xdisparity',self.xdisparity*xsize)
        ydisparity  = params.get('ydisparity',self.ydisparity*ysize)
        dotdensity  = params.get('dotdensity',self.dotdensity)
        dotsize     = params.get('dotsize',self.dotsize*xsize)
        random      = params.get('random',self.random)

        result=scale*self.rds(xsize,ysize,xdisparity,ydisparity,dotdensity,dotsize,random)+offset
        
        if output_fn is not IdentityOF: 
            output_fn(result)

        return result
        
        
    def rds(self,xsize,ysize,xdisparity,ydisparity,dotdensity,dotsize,gen_seed):
    
    
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
