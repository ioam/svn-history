"""
sheet for randomly generating gaussian inputs

$Id$
"""

import debug
from kernelfactory import *
import random
from simulator import EventProcessor
from sheet import Sheet
from utils import NxN


from Numeric import *
from pprint import pprint,pformat
from params import setup_params


def convolve2d(kernel,image):
    """
    Convolve kernel with image.  The resulting matrix will be the
    dimensions of image, less the respective dimensions of kernel.
    """
    
    krows,kcols = kernel.shape
    result = zeros((image.shape[0]-krows,
                    image.shape[1]-kcols)) * 1.0
    result[0,0] = 0.33
    
    for r in range(result.shape[0]):
        for c in range(result.shape[1]):
            submatrix = image[r:r+krows,c:c+kcols]            
            result[r,c] = sum(sum(kernel * submatrix))

    return result


class GaussianSheet(Sheet):

    def __init__(self,**config):
        kernel =  KernelFactory(kernel_bounds=BoundingBox(points=((0,0), (10,10)), kernel_density=1))

        EventProcessor.__init__(self,**config)
        setup_params(self,GaussianSheet,**config)

    def input_event(self,src,src_port,dest_port,data):
        self.db_print("Received %s input from %s." % (NxN(data.shape),src),
                      debug.VERBOSE)

        self.db_print("Generating a new kernel...",debug.VERBOSE)
        self.activation = kernel.get_kernel(x=random.uniform(-1,1), y=random.uniform(-1,1), theta=random.uniform(-3.14159,3.14159)) 
  
        self.matrix_shape = self.activation.shape
        
        self.send_output(data=self.activation)
        self.db_print("Sending %s output." % NxN(self.activation.shape))


if __name__ == '__main__':
        print "nothing here yet"
