"""
2-dimensional convolution

Defines a function and Sheet to do 2D convolution

$Id$
"""
from simulator import EventProcessor
from sheet import Sheet
from utils import NxN


from Numeric import *
from pprint import pprint,pformat
from params import Parameter


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


class Convolver(Sheet):
    """
    
    A sheet that porforms 2D convolutions.

    Parameters:
      kernel = A matrix containing the convolution kernel.
               (default 2x2 uniform blur).


    Sheet convolves any input matrix it receives with the kernel, and
    immediately sends the result out.
    
    """

    kernel = Parameter(array([[1.0]]))

    def __init__(self,**config):
        super(Convolver,self).__init__(**config)

    def input_event(self,src,src_port,dest_port,data):
            
        self.verbose("Received %s input from %s." % (NxN(data.shape),src))
        self.verbose("Convolving...")        
        self.activation = convolve2d(self.kernel,data)
        self.matrix_shape = self.activation.shape
        
        self.send_output(data=self.activation)
        self.message("Sending %s output." % NxN(self.activation.shape))


if __name__ == '__main__':
    k = array([[0,1,0],
               [0,1,0],
               [0,1,0]])

    i = identity(10)

    r = convolve2d(k,i)

    pprint(r)
    
