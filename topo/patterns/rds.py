"""
Random-dot stereogram patterns.

$Id$
"""
__version__='$Revision$'


from Numeric import zeros,ones,floor
from RandomArray import random,seed

from topo.base.parameterclasses import Number
from topo.base.patterngenerator import PatternGenerator
from topo.base.sheetcoords import SheetCoordinateSystem
from topo.base.functionfamilies import OutputFnParameter, IdentityOF


class RandomDotStereogram(PatternGenerator):
    """
    Random dot stereogram using rectangular black and white patches.

    Based on Matlab code originally from Jenny Read, implemented in
    Topographica by Tikesh Ramtohul (2006).
    """

    # Suppress unused parameters
    x = Number(hidden=True)
    y = Number(hidden=True)
    orientation = Number(hidden=True)
    

    # New parameters for this pattern
    xdisparity = Number(default=0.0,bounds=(-1.0,1.0),softbounds=(-0.5,0.5),
                        precedence=0.50,doc="Disparity in the horizontal direction.")
    
    ydisparity = Number(default=0.0,bounds=(-1.0,1.0),softbounds=(-0.5,0.5),
                        precedence=0.51,doc="Disparity in the vertical direction.")
    
    dotdensity = Number(default=0.5,bounds=(0.0,None),softbounds=(0.1,0.9),
                        precedence=0.52,doc="Number of dots per unit area; 0.5=50% coverage.")

    dotsize    = Number(default=0.1,bounds=(0.0,None),softbounds=(0.05,0.15),
                        precedence=0.53,doc="Edge length of each square dot.")

    random_seed = Number(default=500,bounds=(0.0,1000),softbounds=(0.0,1000.0),
                        precedence=0.54,doc="Seed value for the random position of the dots.")


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
        random_seed = params.get('random_seed',self.random_seed)

        xsize=int(round(xsize))
        ysize=int(round(ysize))
        xdisparity=int(round(xdisparity))
        ydisparity=int(round(ydisparity))
        dotsize=int(round(dotsize))
        random_seed=int(round(random_seed))
        
        bigxsize = 2*xsize
        bigysize = 2*ysize
        ndots=int(round(dotdensity * (bigxsize+2*dotsize) * (bigysize+2*dotsize) / min(dotsize,xsize) / min(dotsize,ysize)))
        halfdot = floor(dotsize/2)
    
        ### TRALERT:
        
        ### TRALERT:For Test Pattern Window
        bigimage = 0.5*ones((bigysize,bigxsize))
    
        ### TRALERT:For Energy models
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
    
        
        seed(random_seed*12,random_seed*99)
        col=random((1,ndots))
    
        seed(random_seed*122,random_seed*799)
        xpos=floor(random((1,ndots))*(bigxsize+2*dotsize)) - halfdot
    
        seed(random_seed*1243,random_seed*9349)
        ypos=floor(random((1,ndots))*(bigysize+2*dotsize)) - halfdot
      
        
        for i in range(ndots):
    
            ### TRALERT:For Test Pattern Window,white is represented as 1 and black as 0. background is 0.5
            ### alternatively, offset parameter can be set properly
            
            if col[0][i] >= 0.5:
                col[0][i]= 1
            else:
                col[0][i]= 0
            
            
            ### TRALERT:For testing energy models, white==1, black==-1,background=0 (similar to Read's code)
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
            
        result = offset + scale*bigimage[ (ysize/2)+ydisparity:(3*ysize/2)+ydisparity , (xsize/2)+xdisparity:(3*xsize/2)+xdisparity ]

        if output_fn is not IdentityOF:
            output_fn(result)

        return result
