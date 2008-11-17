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
import sys
import functools
import new
import pickle
import types
import __main__
from StringIO import StringIO

from topo import param



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
    ./topographica examples/hierarchical.ty -c "from topo.misc.util import profile; profile('topo.sim.run(10)')"
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


# CB: note that this has only really been tested for output;
# I've never tried using it to e.g. read multiple files.
class MultiFile(object):
    """
    For all file_like_objs passed on initialization, provides a
    convenient way to call any of file's methods (on all of them).

    E.g. The following would cause 'test' to be written into two
    files, as well as to stdout:

    import sys
    f1 = open('file1','w')
    f2 = open('file2','w')
    m = MultiFile(f1,f2,sys.stdout)
    m.write('test')
    """
    def __init__(self,*file_like_objs):
        self.file_like_objs=file_like_objs
        self.__provide_file_methods()

    def __provide_file_methods(self):
        # Provide a version of all the methods of the type file that
        # don't start with '_'. In each case, the provided version
        # loops over all the file_like_objs, calling the file method
        # on all of them.
        file_methods = [attr for attr in file.__dict__
                        if not attr.startswith('_')
                        and callable(file.__dict__[attr])]

        for method in file_methods:
            def looped_method(method_,*args,**kw):
                all_out = []
                for output in self.file_like_objs:
                    out = getattr(output,method_)(*args,**kw)
                    all_out.append(out)
                return all_out

            setattr(self,method,functools.partial(looped_method,method))
            



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
                

class PickleMain(object):
    """
    Pickle support for types and functions defined in __main__.
    
    When pickled, saves types and functions defined in __main__ by
    value (i.e. as bytecode). When unpickled, loads previously saved
    types and functions back into __main__.
    """
    def _create_pickler(self):
        # Usually we use the cPickle module rather than the pickle
        # module (because cPickle is faster), but here we need control
        # over the pickling process so we use pickle.
        #
        # Additionally, we create a Pickler instance to avoid changing
        # defaults in the pickle module itself, so that there are no side
        # effects for code elsewhere (although we don't use pickle
        # anywhere else ourselves...).

        self.pickled_bytecode = StringIO()
        self.pickler = pickle.Pickler(self.pickled_bytecode,-1)

        self.pickler.dispatch[new.code] = save_code
        self.pickler.dispatch[new.function] = save_function
        self.pickler.dispatch[dict] = save_module_dict
        self.pickler.dispatch[new.classobj] = save_classobj
        self.pickler.dispatch[new.instancemethod] = save_instancemethod
        self.pickler.dispatch[new.module] = save_module
        self.pickler.dispatch[type] = save_type
        # CB: maybe this should be registered from elsewhere
        self.pickler.dispatch[param.parameterized.ParameterizedMetaclass] = save_type


    def __getstate__(self):
        self._create_pickler()
        
        bytecode = {}
        for name,obj in __main__.__dict__.items():
            if isinstance(obj,types.FunctionType) or isinstance(obj,type):
                # (could be extended to other types, I guess
                if obj.__module__ == "__main__":
                    #CB: how do I print out info via Parameterized?
                    print "%s is defined in __main__: saving bytecode."%name
                    bytecode[name] = obj

        self.pickler.dump(bytecode)
        return {'pickled_bytecode':self.pickled_bytecode}


    def __setstate__(self,state):
        bytecode = pickle.load(StringIO(state['pickled_bytecode'].getvalue()))

        for name,obj in bytecode.items():
            print "%s restored from bytecode into __main__"%name
            __main__.__dict__[name] = obj

    
    
# CB: will be moved elsewhere...

### Copied from http://code.activestate.com/recipes/572213/ ###
# (but note that we're not actually using it to pickle __main__,
# and I've removed the lines that change pickle's defaults)
"""
Extend pickle module to allow pickling of interpreter state
including any interactively defined functions and classes.

This module is not required for unpickling such pickle files.

>>> import savestate, pickle, __main__
>>> pickle.dump(__main__, open('savestate.pickle', 'wb'), 2)
"""

import new

def save_code(self, obj):
    """ Save a code object by value """
    args = (
        obj.co_argcount, obj.co_nlocals, obj.co_stacksize, obj.co_flags, obj.co_code,
        obj.co_consts, obj.co_names, obj.co_varnames, obj.co_filename, obj.co_name,
        obj.co_firstlineno, obj.co_lnotab, obj.co_freevars, obj.co_cellvars
    )
    self.save_reduce(new.code, args, obj=obj)

def save_function(self, obj):
    """ Save functions by value if they are defined interactively """
    if obj.__module__ == '__main__' or obj.func_name == '<lambda>':
        args = (obj.func_code, obj.func_globals, obj.func_name, obj.func_defaults, obj.func_closure)
        self.save_reduce(new.function, args, obj=obj)
    else:
        pickle.Pickler.save_global(self, obj)

def save_global_byname(self, obj, modname, objname):
    """ Save obj as a global reference. Used for objects that pickle does not find correctly. """
    self.write('%s%s\n%s\n' % (pickle.GLOBAL, modname, objname))
    self.memoize(obj)

def save_module_dict(self, obj, main_dict=vars(__import__('__main__'))):
    """ Special-case __main__.__dict__. Useful for a function's func_globals member. """
    if obj is main_dict:
        save_global_byname(self, obj, '__main__', '__dict__')
    else:
        return pickle.Pickler.save_dict(self, obj)      # fallback to original 

def save_classobj(self, obj):
    """ Save an interactively defined classic class object by value """
    if obj.__module__ == '__main__':
        args = (obj.__name__, obj.__bases__, obj.__dict__)
        self.save_reduce(new.classobj, args, obj=obj)
    else:
        pickle.Pickler.save_global(self, obj, name)

def save_instancemethod(self, obj):
    """ Save an instancemethod object """
    # Instancemethods are re-created each time they are accessed so this will not be memoized
    args = (obj.im_func, obj.im_self, obj.im_class)
    self.save_reduce(new.instancemethod, args)

def save_module(self, obj):
    """ Save modules by reference, except __main__ which also gets its contents saved by value """
    if obj.__name__ == '__main__':
        self.save_reduce(__import__, (obj.__name__,), obj=obj, state=vars(obj).copy())
    elif obj.__name__.count('.') == 0:
        self.save_reduce(__import__, (obj.__name__,), obj=obj)
    else:
        save_global_byname(self, obj, *obj.__name__.rsplit('.', 1))

def save_type(self, obj):
    if getattr(new, obj.__name__, None) is obj:
        # Types in 'new' module claim their module is '__builtin__' but are not actually there
        save_global_byname(self, obj, 'new', obj.__name__)
    elif obj.__module__ == '__main__':
        # Types in __main__ are saved by value

        # Make sure we have a reference to type.__new__        
        if id(type.__new__) not in self.memo:
            self.save_reduce(getattr, (type, '__new__'), obj=type.__new__)
            self.write(pickle.POP)

        # Copy dictproxy to real dict
        d = dict(obj.__dict__)
        # Clean up unpickleable descriptors added by Python
        d.pop('__dict__', None)
        d.pop('__weakref__', None)
        
        args = (type(obj), obj.__name__, obj.__bases__, d)
        self.save_reduce(type.__new__, args, obj=obj)
    else:
        # Fallback to default behavior: save by reference
        pickle.Pickler.save_global(self, obj)
###############################################################        
