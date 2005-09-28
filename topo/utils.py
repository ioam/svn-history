from __future__ import generators
"""
General utility functions and classes for Topographica.

$Id$
"""

from Numeric import sqrt,ones,dot,sum
import __main__
import weave

inf = (ones(1)/0.0)[0]

def NxN(tuple):
    """
    Converts a tuple (X1,X2,...,Xn) to a string 'X1xX2x...xXn'
    """    
    return 'x'.join([`N` for N in tuple])


def enumerate(seq):
    """
    For each element Xi of the given sequence, produces the tuple (i,Xi).
    
    (A copy of the Python 2.3 enumeration generator.)
    """
    Generator
    i = 0
    for x in seq:
        yield i,x
        i+=1

enum = enumerate

def L2norm(v):
    """
    Return the L2 norm of the vector v.
    """    
    return sqrt(dot(v,v))

def norm(v,L=2):
    """
    Returns the L? norm of v, where L is arbitrary and defaults to 2.
    """
    return sum(v**L)**(1.0/L)

def msum(m):
    """
    Returns the sum of elements in a 2D matrix.  Works in cases where
    sum(a.flat) fails, e.g, with matrix slices or submatrices.
    """
    return sum(sum(m))

### JAB: Could be rewritten using weave.blitz to avoid creating a temporary
def mdot(m1,m2):
    """
    Returns the sum of the element-by-element product of two 2D
    arrays.  Works in cases where dot(a.flat,b.flat) fails, e.g, with
    matrix slices or submatrices.
    """
    a = m1*m2
    return sum(a.flat)

def PLTF01(x):
    """
    Piecewise-linear transfer function.
    A matrix function that applies this function to each element:

           /  0 : x < 0 
    f(x) = |  x : 0 <= x <= 1
           \  1 : x > 1
    """
    return ((x * (x>0)) * (x<1)) + (x>1)

def PLTF(x,lb=0.0,ub=1.0):
    """ 
    Piecewise-linear transfer function with lower and upper thresholds
    as parameters.
    """

    #return PLTF01((x-lb)/(ub-lb))
    fact = 1.0/(ub-lb)
    x = (x-lb)*fact
    return ((x * (x>0)) * (x<1)) + (x>1)


class Struct:
    """
    A simple structure class, takes keyword args and assigns them to
    attributes, e.g:

    s = Struct(foo='a',bar=1)

    >>> s.foo
    'a'
    >>> s.bar
    1
    >>>
    """
    def __init__(self,**fields):
        for name,value in fields.items():
            setattr(self,name,value)


def flat_indices(shape):
    """
    Returns a list of the indices needed to address or loop over all
    the elements of a 1D or 2D matrix with the given shape. E.g.:

    flat_indices((3,)) == [0,1,2]
    """
    if len(shape) == 1:
        return [(x,) for x in range(shape[0])]
    else:
        rows,cols = shape
        return [(r,c) for r in range(rows) for c in range(cols)]
        
    
def add_border(matrix,width=1,value=0.0):
    """
    Returns a new matrix consisting of the given matrix with a border
    or margin of the given width filled with the given value.
    """
    from Numeric import concatenate as join,array
    rows,cols = matrix.shape

    hborder = array([ [value]*(cols+2*width) ]*width)
    vborder = array([ [value]*width ] * rows)

    temp = join( (vborder,matrix,vborder), axis=1)
    return join( (hborder,temp,hborder) )

def flatten(l):
    """
    Flattens a list.
    
    Written by Bearophile as published on the www.python.org newsgroups.
    Pulled into Topographica 3/5/2005.
    """
    if type(l) != list:
        return l
    else:
        result = []
        stack = []
        stack.append((l,0))
        while len(stack) != 0:
            sequence, j = stack.pop(-1)
            while j < len(sequence):
                if type(sequence[j]) != list:
                    k, j, lens = j, j+1, len(sequence)
                    while j < len(sequence) and \
                          (type(sequence[j]) != list):
                        j += 1
                    result.extend(sequence[k:j])
                else:
                    stack.append((sequence, j+1))
                    sequence, j = sequence[j], 0
        return result


def compute_response_mdot_py(input_activity, rows, cols, temp_activity, cfs, strength):
    """
    The original mdot function that the inline C code based on. It is here just
    for reference.
    """

    for r in xrange(rows):
        for c in xrange(cols):
            cf = cfs[r][c]
            r1,r2,c1,c2 = cf.slice
            X = input_activity[r1:r2,c1:c2]

            a = X*cf.weights
            self.temp_activity[r,c] = sum(a.flat)
    self.temp_activity *= self.strength

def compute_response_mdot_c(input_activity, rows, cols, temp_activity, cfs, strength):
    """
    An optmized version that computes the mdot functions for all the conection
    fields with the input_activity. It loops through each unit in the sheet
    and therefore the loop in KernelProjection.compute_response is not needed.
    """

    temp_act = temp_activity
    len, len2 = input_activity.shape
    X = input_activity.flat

    code = """
        double tot;
        float *wi; 
        double *xi, *xj;
        double *tact = temp_act;
        int *slice;
        int rr1, rr2, cc1, cc2;
        int i, j, r, l;
        PyObject *cf, *cfsr;
        PyObject *sarray = PyString_FromString("slice_array");
        PyObject *weights = PyString_FromString("weights");

        for (r=0; r<rows; ++r) {
            cfsr = PyList_GetItem(cfs,r);
            for (l=0; l<cols; ++l) {
                cf = PyList_GetItem(cfsr,l);
                wi = (float *)(((PyArrayObject*)PyObject_GetAttr(cf,weights))->data);
                slice = (int *)(((PyArrayObject*)PyObject_GetAttr(cf,sarray))->data);
                rr1 = *slice++;
                rr2 = *slice++;
                cc1 = *slice++;
                cc2 = *slice;

                tot = 0.0;

                // computes the dot product
                xj = X+len*rr1+cc1;
                for (i=rr1; i<rr2; ++i) {
                    xi = xj;
                    for (j=cc1; j<cc2; ++j) {
                        tot += *wi * *xi;
                        ++wi;
                        ++xi;
                    }
                    xj += len;
                }

                *tact = tot*strength;
                ++tact;
            }
        }
    """

    weave.inline(code, ['X', 'strength', 'len', 'temp_act','cfs','cols','rows'])


def eval_atof(in_string,default_val = 0):
    """
    Create a float from a string by eval'ing it in the __main__
    namespace.  If the string raises an exception, 0 is returned.
    Catch any exceptions and return 0 if this is the case.
    """
    try:
        val = eval(in_string,__main__.__dict__)
    except Exception:
        val = default_val
    return val
