from __future__ import generators
"""
General utility functions and classes for Topographica.

$Id$
"""

from Numeric import sqrt,ones,dot,sum

inf = (ones(1)/0.0)[0]

def NxN(tuple):
    """
    Converts a tuple (X1,X2,...,Xn) to a string "X1xX2x...xXn"
    """    
    return 'x'.join([`N` for N in tuple])


def enumerate(seq):
    """
    A copy of the Python 2.3 enumeration generator, for each element Xi
    of a sequence, the enumerator yields the tuple (i,Xi).    
    """
    Generator
    i = 0
    for x in seq:
        yield i,x
        i+=1

enum = enumerate

def norm(v):
    """
    Return the L2 norm of the vector v.
    """    
    return sqrt(dot(v,v))


def msum(m):
    return sum(sum(m))

def mdot(m1,m2):
    return msum(m1*m2)
    
class Struct:
    def __init__(self,**fields):
        for name,value in fields.items():
            setattr(self,name,value)


def flat_indices(shape):
    if len(shape) == 1:
        return [(x,) for x in range(shape[0])]
    else:
        suffix = flat_indices(shape[1:])
        result = []
        for i in range(shape[0]):
            for t in suffix:
                result.append((i,)+t)
        return result
        
    
