"""
Simple two-dimensional mathematical or geometrical pattern generators.

"""

from topo.base.parameterclasses import Number
from topo.base.patterngenerator import PatternGenerator
from topo.base.sheetcoords import SheetCoordinateSystem
from topo.base.functionfamilies import OutputFnParameter, IdentityOF
from topo.misc.patternfns import rds
 


class RandomDotStereogram(PatternGenerator):
    """random dot stereogram"""

    x = Number(hidden = True)
    y = Number(hidden = True)
    orientation = Number(hidden = True)
    

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

        
        result=scale*rds(xsize,ysize,xdisparity,ydisparity,dotdensity,dotsize,random)+offset

        
        if output_fn is not IdentityOF: 
            output_fn(result)

        return result
        
        
