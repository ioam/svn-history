"""
Hisogram object that both calculates, and holds information about
a 2D matrix of data.

STUB CLASS ONLY.  GENERIC INPUT AND OUTPUT DATA TO ALLOW DEVELOPMENT
IN OTHER AREAS.

$Id$
"""
from base import *
import types

# For stub calculation
import Numeric

class Histogram(TopoObject):

    def __init__(self, matrix, **params):
        """
        matrix can be a list of matrices, or a single matrix.
        
        This initialization function should take in one or more
        matrices, do the calculation, and store it for when others
        want it.
        """
        super(Histogram,self).__init__(**params)

        # Do some basic constructor definition overloading
        if isinstance(matrix,types.TupleType):
            matrix = list(matrix)
        if not isinstance(matrix,types.ListType):
            matrix = [matrix]
        self.matrices = matrix


    def histogram(self):
        """
        CHANGE THIS FUNCTION WHEN IMPLEMENTING HISTOGRAM
        """
        sum_matrix = self.matrices.pop(0)
        for each in self.matrices:
            sum_matrix = sum_matrix + each
        f_matrix = Numeric.ones(sum_matrix.shape[0])
        result = list(Numeric.matrixmultiply(sum_matrix,f_matrix))
        result.extend([0 for each in range(256 - len(result))])
        return Numeric.array(result)


#  All testing takes place through the Unit Test modules found in the
#  topographica/tests directory.
                       
    
