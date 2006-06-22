from __future__ import generators
"""
General utility functions and classes.

$Id$
"""
__version__='$Revision$'

import __main__
import math
import re


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
### JABALERT! This will actually return any type, not just float; what's going on?
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
    

# CEBALERT: I think this can probably be simplified.
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


def values_sorted_by_key(d):
    """
    Return the values of dictionary d sorted by key.
    """
    # By Alex Martelli, 2001/04/08
    # http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/52306
    keys = d.keys()
    keys.sort()
    return map(d.get, keys)


def keys_sorted_by_value(d):
    """
    Return the keys of dictionary d sorted by value.
    """
    # By Daniel Schult, 2004/01/23
    # http://aspn.activestate.com/ASPN/Python/Cookbook/Recipe/52306
    items=d.items()
    backitems=[ [v[1],v[0]] for v in items]
    backitems.sort()
    return [ backitems[i][1] for i in range(0,len(backitems))]


# CEBHACKALERT: this could be improved!
import inspect
from topo.base.parameterizedobject import Parameter, ParameterizedObject
def get_states_of_classes_from_module(module,states_of_classes,processed_modules,exclude=None):
    """
    Recursively search module and get states of classes within it.

    states_of_classes is a dictionary {module.path.and.Classname: state}

    Something is considered a module for our purposes if inspect says it's a module,
    and it defines __all__. We only search through modules listed in __all__.

    Keeps a list of processed modules to avoid looking at the same one
    more than once (since e.g. __main__ contains __main__ contains
    __main__...)

    Packages can be specifically excluded if listed in exclude.
    """
    if not exclude:
        exclude = []

#    print "process",module
    
    dict_ = module.__dict__
    for (k,v) in dict_.items():
        if '__all__' in dict_ and inspect.ismodule(v) and k not in exclude:
            if k in dict_['__all__'] and v not in processed_modules:
                #print "pickling classes in",k
                get_states_of_classes_from_module(v,states_of_classes,processed_modules,exclude)
            processed_modules.append(v)

        else:
            if isinstance(v,type) and issubclass(v,ParameterizedObject):

                # Note: we take the class name as v.__name__, not k, because
                # k might be just a label for the true class. For example,
                # if Topographica falls back to the unoptimized components,
                # k could be "CFPRF_DotProduct_opt", but v.__name__
                # - and the actual class - is "CFPRF_DotProduct". It
                # is correct to set the attributes on the true class.
                full_class_path = v.__module__+'.'+v.__name__
                states_of_classes[full_class_path] = {}
                # class ALWAYS has __dict__, right? And no P.O. has slots.
                for (name,obj) in v.__dict__.items():
                    if isinstance(obj,Parameter):
                        states_of_classes[full_class_path][name] = obj

def shortclassname(x):
    """
    Returns the class name of x as a string with the leading package information removed.

    E.g. if x is of type "<class 'topo.base.sheet.Sheet'>", returns
    "Sheet"
    """
    return re.sub("'>","",re.sub(".*[.]","",repr(type(x))))


# CEBHACKALERT: temporary solution for saving savespace state of arrays.
### Python's pickle.Pickler and Numeric's Pickler do not save the
### savespace attribute of arrays, so we implement our own Pickler and
### Unpickler to do this.  These are subclasses of pickle.Pickler and
### pickle.Unpickler, but we override the save_array and load_array
### methods.
###
### These methods are modified ones taken from Numeric's Pickler and
### Unpickler for the moment, but really they should just call
### pickle.Pickler/pickle.Unpickler's own load_array and save_array
### methods, but also save the savespace attribute.
                        

from Numeric import array,multiply,ArrayType,LittleEndian,fromstring,reshape
import string

### CB: code between marks is lifted from Numeric.py with modifications noted ###

# These two functions are used in my modified pickle.py so that
# matrices can be pickled.  Notice that matrices are written in
# binary format for efficiency, but that they pay attention to
# byte-order issues for  portability.

def DumpArray(m, fp):
    if m.typecode() == 'O':
        raise TypeError, "Numeric Pickler can't pickle arrays of Objects"
    s = m.shape
    if LittleEndian: endian = "L"
    else: endian = "B"
    # CB: as well as writing typecode, write savespace
    fp.write("A%s%s%d%d " % (m.typecode(), endian, m.spacesaver(), m.itemsize()))
    for d in s:
        fp.write("%d "% d)
    fp.write('\n')
    fp.write(m.tostring())

def LoadArray(fp):
    ln = string.split(fp.readline())
    if ln[0][0] == 'A': ln[0] = ln[0][1:] # Nasty hack showing my ignorance of pickle
    typecode = ln[0][0]
    endian = ln[0][1]
    # CB: read back savespace
    savespace = int(ln[0][2])
    
    shape = map(lambda x: string.atoi(x), ln[1:])
    itemsize = string.atoi(ln[0][3:])

    sz = reduce(multiply, shape)*itemsize
    data = fp.read(sz)

    m = fromstring(data, typecode)
    m = reshape(m, shape)
    # CB: set savespace
    m.savespace(savespace)

    if (LittleEndian and endian == 'B') or (not LittleEndian and endian == 'L'):
        return m.byteswapped()
    else:
        return m

import pickle, copy
class ExtraUnpickler(pickle.Unpickler):
    def load_array(self):
        self.stack.append(LoadArray(self))

    dispatch = copy.copy(pickle.Unpickler.dispatch)
    dispatch['A'] = load_array

class ExtraPickler(pickle.Pickler):
    def save_array(self, object):
        DumpArray(object, self)

    dispatch = copy.copy(pickle.Pickler.dispatch)
    dispatch[ArrayType] = save_array

### CB: end code from Numeric.py ###
