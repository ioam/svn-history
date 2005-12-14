from __future__ import generators
"""
General utility functions and classes for Topographica.

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


def hebbian(input_activity, unit_activity, weights, learning_rate):
    """Simple Hebbian learning for the weights of one single unit."""
    weights += learning_rate * unit_activity * input_activity



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


# CEBHACKALERT: when a base class for PatternGeneratorParameter etc
# exists, consider making this a method of that class.
from inspect import ismodule
def find_classes_in_package(package,parentclass):
    """
    Return a dictionary containing all items of the type
    specified, owned by modules in the specified package.
    Only currently imported modules are searched, so
    the caller will first need to do 'from package import *'.
    Does not search packages contained within the specified
    package, only the top-level modules.
    """
    result = {}
    for v1 in package.__dict__.itervalues():
        if ismodule(v1):
            for v2 in v1.__dict__.itervalues():
                if (isinstance(v2,type)
                    and issubclass(v2,parentclass)
                    and v2 is not parentclass):
                    result[v2.__name__] = v2
    return result



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


def frange(start, end=None, inc=None):
    """
    A range function that accepts float increments.

    Otherwise, works just as the inbuilt range() function.

    'All thoretic restrictions apply, but in practice this is
    more useful than in theory.'

    From:
    http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/66472
    """
    if end == None:
        end = start + 0.0
        start = 0.0

    if inc == None:
        inc = 1.0

    L = []
    while 1:
        next = start + len(L) * inc
        if inc > 0 and next >= end:
            break
        elif inc < 0 and next <= end:
            break
        L.append(next)
        
    return L


def classlist(class_):
    """
    Return a list of the class hierarchy above (and including) class_.

    The list is ordered from least- to most-specific.  Often useful in
    functions to get and set the full state of an object, e.g. for
    pickling.
    """
    assert isinstance(class_, type)
    q = [class_]
    out = []
    while len(q):
        x = q.pop(0)
        out.append(x)
        for b in x.__bases__:
            if b not in q and b not in out:
                q.append(b)
    return out[::-1]


def descendents(class_):
    """
    Return a list of the class hierarchy below (and including) class_.

    The list is ordered from least- to most-specific.  Can be useful for
    printing the contents of an entire class hierarchy.
    """
    assert isinstance(class_,type)
    q = [class_]
    out = []
    while len(q):
        x = q.pop(0)
        out.insert(0,x)
        for b in x.__subclasses__():
            if b not in q and b not in out:
                q.append(b)
    return out[::-1]


# CEBHACKALERT: I think this function should be renamed to sorted_keys() or sorted_dict_keys() or something
# like that.

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


### JABALERT!
###
### If at all possible should be rewritten to use matrix functions
### that eliminate the explicit for loop.  The savespace() should
### probably also be eliminated. 
### JC: It has been tried to change the function so that to get rid of
### the for loop, but no satisfying matrix function has been found to
### perform it.
###
### Should move to arrayutils.
def clip_in_place(mat,lower_bound,upper_bound):
    """Version of Numeric.clip that changes the argument in place, with no intermediate."""
    mat.savespace(1)
    mflat = mat.flat
    size = len(mflat)
    for i in xrange(size):
        element = mflat[i]
        if element<lower_bound:
            mflat[i] = lower_bound
        elif element>upper_bound:
            mflat[i] = upper_bound



# CEBHACKALERT: should it also take full path to classname?
# e.g. topo.base.patterngenerator.ConstantGenerator rather than ConstantGenerator
# then keep to first "." from the right, or something.
# I also don't know how it works.
import string, re
def classname_repr(class_name, suffix_to_lose=''):
    """
    Return class_name stripped of suffix_to_lose, and with spaces before any capital letters.
    """
    # Cut off 'suffix_to_lose'
    viewable_name = re.sub(suffix_to_lose+'$','',class_name)

    # Add spaces before capital leters
    for c in string.uppercase:
        viewable_name = viewable_name.replace(c,' '+c).strip()

    return viewable_name



