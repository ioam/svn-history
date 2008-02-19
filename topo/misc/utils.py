"""
General utility functions and classes.

$Id$
"""
__version__='$Revision$'

import __main__
import math
import re
import string
import random
import numpy
import cProfile
import pstats


def NxN(tuple):
    """
    Converts a tuple (X1,X2,...,Xn) to a string 'X1xX2x...xXn'
    """    
    return 'x'.join([`N` for N in tuple])



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


    From http://www.norvig.com/python-iaq.html
    """
    def __init__(self, **entries): self.__dict__.update(entries)

    def __repr__(self):
        # 
        args = ['%s=%s' % (k, repr(v)) for (k,v) in vars(self).items()]
        return 'Struct(%s)' % ', '.join(args)



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


# CEBNOTE: use this for tkparameterizedobject or delete it
def eval_atof(str):
    """
    Evaluates the given string in __main__, and converts it to a float.

    The string can contain any expression that will evaluate to a
    number.  The expression can use any variables or functions that
    are defined in the main namespace.

    See string.atof() for more details about the conversion from the
    evaluated string into a float.
    """
    return string.atof(eval(str,__main__.__dict__))
    

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



# JABALERT: Should frange be replaced with numpy.arange or numpy.linspace?
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


# CB: this function isn't used, as of 2006/06/22
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


def inverse(dict_):
    """
    Return the inverse of dictionary dict_.
    
    (I.e. return a dictionary with keys that are the values of dict_,
    and values that are the corresponding keys from dict_.)

    The values of dict_ must be unique.
    """
    idict = dict([(value,key) for key,value in dict_.iteritems()])
    if len(idict)!=len(dict_):
        raise ValueError("Dictionary has no inverse (values not unique).")
    return idict


def shortclassname(x):
    """
    Returns the class name of x as a string with the leading package information removed.

    E.g. if x is of type "<class 'topo.base.sheet.Sheet'>", returns
    "Sheet"
    """
    return re.sub("'>","",re.sub(".*[.]","",repr(type(x))))



def profile(command,n=50,sorting=('cumulative','time'),strip_dirs=False):
    """
    Profile the given command (supplied as a string), printing
    statistics about the top n functions when ordered according to
    sorting.

    sorting defaults to ordering by cumulative time and then internal
    time; see http://docs.python.org/lib/profile-stats.html for other
    sorting options.

    By default, the complete paths of files are not shown. If there
    are multiple files with the same name, you might wish to set
    strip_dirs=False to make it easier to follow the output.


    Examples:

    - profile loading a simulation:
    profile('execfile("examples/hierarchical.ty")')

    - profile running an already loaded simulation:
    profile('topo.sim.run(10)')

    - profile running a whole simulation:
    profile('execfile("examples/lissom_oo_or.ty");topo.sim.run(20000)')

    - profile running a simulation, but from the commandline:
    ./topographica examples/hierarchical.ty -c "from topo.misc.utils import profile; profile('topo.sim.run(10)')"
    """
    # This function simply wraps some functions from the cProfile
    # module, making profiling easier.

    # CB: leaves around "filename": should give this a proper name and maybe
    # put in /tmp/ and maybe allow someone to choose where to save it
    prof = cProfile.run(command,'filename')
    prof_stats = pstats.Stats('filename')

    if strip_dirs:prof_stats.strip_dirs()
    
    prof_stats.sort_stats(*sorting).print_callees(n)
    ### the above lets us see which times are due to which calls
    ### unambiguously, while the version below only reports total time
    ### spent in each object, not the time due to that particular
    ### call.
    prof_stats.sort_stats(*sorting).print_stats(n)

    


def weighted_sample(seq,weights=[]):
    """
    Select randomly from the given sequence.
    
    The weights, if given, should be a sequence the same length as
    seq, as would be passed to weighted_sample_idx().
    """
    if not weights:
        return seq[random.randrange(len(seq))]
    else:
        assert len(weights) == len(seq)
        return seq[weighted_sample_idx(weights)]


def weighted_sample_idx(weights):
    """
    Return an integer generated by sampling the discrete distribution
    represented by the sequence of weights.

    The integer will be in the range [0,len(weights)).  The weights
    need not sum to unity, but can contain any non-negative values
    (e.g., [1 1 1 100] is a valid set of weights).

    To use weights from a 2D numpy array w, specify w.ravel() (not the
    w.flat iterator).
    """
    total = sum(weights)
    if total == 0:
        return random.randrange(len(weights))
    index = random.random() * total
    accum = 0
    for i,x in enumerate(weights):
        accum += x
        if index < accum:
            return i


def idx2rowcol(idx,shape):
    """
    Given a flat matrix index and a 2D matrix shape, return the (row,col)
    coordinates of the index.
    """
    assert len(shape) == 2
    rows,cols = shape

    return idx/cols,idx%cols



def rowcol2idx(r,c,shape):
    """
    Given a row, column, and matrix shape, return the corresponding index
    into the flattened (raveled) matrix.
    """
    assert len(shape) == 2
    rows,cols = shape

    return r * cols + c


    
def centroid(pts,weights):
    """
    Return the centroid of a weighted set of points as an array.

    The pts argument should be an array of points, one per row,
    and weights should be a vector of weights.
    """
    # CEBALERT: use numpy.sum? Worthwhile if weights is a numpy.array.
    return numpy.dot(numpy.transpose(pts),weights)/sum(weights)

def signabs(x):
    """
    Split x into its sign and absolute value.

    Returns a tuple (sign(x),abs(x)).  Note: sign(0) = 1, unlike
    numpy.sign.
    """

    if x < 0:
        sgn = -1
    else:
        sgn = 1

    return sgn,abs(x)



# CEBALERT: would it be simpler just to have a dictionary/list
# somewhere of extra things to pickle, and pickle that in
# save_snapshot()? What about supporting things other than
# module-level attributes?


class Singleton(object):
    """
    The singleton pattern.

    To create a singleton class, you subclass from Singleton; each
    subclass will have a single instance, no matter how many times its
    constructor is called. To further initialize the subclass
    instance, subclasses should override 'init' instead of __init__ -
    the __init__ method is called each time the constructor is called.

    From http://www.python.org/2.2.3/descrintro.html#__new__
    """
    def __new__(cls, *args, **kwds):
        it = cls.__dict__.get("__it__")
        if it is not None:
            return it
        cls.__it__ = it = object.__new__(cls)
        it.init(*args, **kwds)
        return it

    def init(self, *args, **kwds):
        """Method to be overridden if the subclass needs initialization."""
        pass

    # CB: our addition
    def __reduce_ex__(self,p):
        """
        Causes __new__ to be called on unpickling; in turn, __new__
        ensures there is only one instance.
        """
        return (type(self),tuple()) 




class ExtraPickler(Singleton):
    """
    Provides a simple means to include arbitrary attributes from
    modules when pickling.

    To include a variable z of module x.y (i.e. x.y.z) in a snapshot (and have
    it put back as x.y.z on loading), do:
        ExtraPickler().add( ('x.y','z') )
    """
    extras = []

    def add(self,item):
        self.extras.append(item)

    def __reduce_ex__(self,p):
        states = {}
        for extra in self.extras:
            d = {}
            exec "from %s import %s"%(extra[0],extra[1]) in d
            states[extra] = d[extra[1]]
        return (type(self),tuple(),{'extras':self.extras,'states':states})
                
    def __setstate__(self,state):
        import __main__
        
        self.extras = state['extras']
        states = state['states']

        for extra in set(self.extras):
            item = states[extra]
            module = extra[0]
            attribute = extra[1]

            # CEBALERT: same alert about setting val in main as for
            # the parameter pickler. surely it's not required? at least
            # prefix __ or something. 
            __main__.__dict__['val']=item

            exec "import %s"%module in __main__.__dict__

            # complication: we're about to set x.y.z=item, but
            # the same thing might also be __main__.__dict__['z']
            # (i.e. main's z might BE x.y.z; when we write over x.y.z,
            # we then also need to write over main's z)
            update_main=False
            if attribute in __main__.__dict__:
                full_path_item = eval("%s.%s"%(module,attribute),__main__.__dict__)
                if __main__.__dict__[attribute] is full_path_item: # can't just check name!
                    update_main=True

            exec "%s.%s=val"%(module,attribute) in __main__.__dict__

            if update_main:
                exec "%s=val"%(attribute) in __main__.__dict__
                



