from __future__ import generators
"""
General utility functions and classes.

$Id$
"""
__version__='$Revision$'

import __main__
import math



def wrap(lower, upper, x):
    """
    Circularly alias the numeric value x into the range [lower,upper).

    Valid for cyclic quantities like orientations or hues.
    """
    #I have no idea how I came up with this algorithm; it should be simplified.
    range=upper-lower
    return lower + math.fmod(x-lower + 2*range*(1-math.floor(x/(2*range))), range)


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


class Struct:
    """
    A simple structure class, taking keyword args and assigning them to attributes.

    For instance:
    
    s = Struct(foo='a',bar=1)
    >>> s.foo
    'a'
    >>> s.bar
    1
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


# It might be good to handle some common exceptions specially,
# generating warnings for them rather than suppressing them...
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

def string_int_translator(in_string, default = 0) :
    """
    Attempt to parse the string into an int and return the in. If it
    fails, return a default value.
    """
    try :
        val = int(in_string)
    except Exception :
        val = default
    return val

def string_bb_translator(tuple_str, default = (0,0,0,0)) :
    """
    The string is split at spaces and if there is only one section
    the string is evaluated in the main dict space, if there is 4
    they are converted to numbers and used to define a BoundingBox
    In other cases a default value is returned.
    """
    from topo.base.boundingregion import BoundingBox
    default = BoundingBox(points = 
               ((default[0], default[1]), (default[2], default[3])))
    tup = tuple_str.split(' ')
    if len(tup) == 1 :
        return eval_atof(tup[0], default_val = default)
    elif len(tup) == 4 :
        num = {}
        i = 0
        for i in range(4) :
            num[i] = eval_atof(tup[i], None)
            if num[i] == None :
                num[i] = default[i]
    else :
        return default
    return BoundingBox(points = ((num[0], num[1]), (num[2], num[3])))

def dict_translator(in_string, name = '', translator_dictionary = {}) :
    """
    Looks for an entry for the string in the dictionary. If it can't be
    found the string is evaluated in using the main dictionary.
    """
    if translator_dictionary.has_key(name) :
        if translator_dictionary[name].has_key(in_string) :
            val = translator_dictionary[name][in_string]
            from topo.base.parameterizedobject import ParameterizedObject
            if isinstance(val, ParameterizedObject) :
                return val
            else : 
                try :
                    val = val()
                    return val
                except : pass
    elif translator_dictionary.has_key(in_string) :
        return translator_dictionary[in_string]
    val = eval_atof(in_string, default_val = in_string)
    return val


"""
Return the cross-product of a variable number of lists (e.g. of a list of lists).

Use to obtain permutations, e.g.
l1=[a,b]
l2=[c,d]
cross_product([l1,l2]) = 
[[a,c], [a,d], [b,c], [b,d]]


From:
http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/159975
"""
# Need to re-write so someone other than Python knows what might happen when this runs
cross_product=lambda ss,row=[],level=0: len(ss)>1 \
   and reduce(lambda x,y:x+y,[cross_product(ss[1:],row+[i],level+1) for i in ss[0]]) \
   or [row+[i] for i in ss[0]]

def frange(start, end=None, inc=1.0, inclusive=False):
    """
    A range function that accepts float increments.

    Otherwise, works just as the inbuilt range() function.  If
    inclusive is False, as in the default, the range is exclusive (not
    including the end value), as in the inbuilt range(). If inclusive
    is true, the range may include the end value.
        
    'All theoretic restrictions apply, but in practice this is
    more useful than in theory.'

    From: http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/66472
    """
    if end == None:
        end = start + 0.0
        start = 0.0

    # Increments of zero would lead to an infinite loop, which can happen if
    # this is mistakenly called with a integer-based rational expression like 1/2.
    assert ((inc>0 and start<=end) or (inc<0 and start>=end))
    
    L = []
    while 1:
        next = start + len(L) * inc
        if inclusive:
          if inc > 0 and next > end: break
          elif inc < 0 and next < end: break
        else:
          if inc > 0 and next >= end: break
          elif inc < 0 and next <= end: break
        L.append(next)
        
    return L



# CEBHACKALERT: I think this function should be renamed to values_sorted_by_key() or something
# like that. The name's misleading: it doesn't sort the actual dictionary, it just returns the values sorted by key - right?

def dict_sort(d):
    """ Simple and fast routine to sort a dictonary on key """
    keys = d.keys()
    keys.sort()
    return map(d.get, keys)


def keys_sorted_by_value(d):
    """
    Return the keys of dictionary d sorted by their values.

    By Daniel Schult, 2004/01/23
    Posted at http://aspn.activestate.com/ASPN/Python/Cookbook/Recipe/52306
    """
    items=d.items()
    backitems=[ [v[1],v[0]] for v in items]
    backitems.sort()
    return [ backitems[i][1] for i in range(0,len(backitems))]



