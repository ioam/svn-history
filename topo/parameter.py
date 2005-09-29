"""
Module for handling experiment parameters and defaults.

$Id$

This module defines an attribute descriptor for experiment parameters.
An experiment parameter is represented in Topographica as a special
kind of class attribute.  See the Parameter class documentation for
more details.
"""

class Parameter(object):
  """
  An attribute descriptor for declaring Topographica parameters.
  
  Simulation parameters are represented in Topographica as a special
  kind of class attribute.  Setting a class attribute to be an
  instance of this class causes that attribute of the class and its
  instances to be treated as a Topographica parameter.  This allows
  special behavior, including dynamically generated parameter values
  (using lambdas or generators), and type or range checking at
  assignment time.
  
  For example, suppose someone has defined a new kind of sheet, that
  has parameters alpha, sigma, and gamma.  He would begin his class
  definition something like this:
  
  class FooSheet(Sheet):
    alpha = Parameter(default=0.1)
    sigma = Parameter(default=0.0)
    gamma = Parameter(default=1.0)
    ...
  
  Parameters have several advantages over plain attributes:
  
  1. They can be set automatically in an instance:  The FooSheet
     __init__ method should call setup_params(self,FooSheet,**args),
     where **args is the dictionary of keyword arguments passed to the
     constructor.  This function will discover all the parameters in
     FooSheet, and set them from the arguments passed in.  E.g., if a
     script does this:
     
        myfoo = FooSheet(alpha=0.5)
  
     myfoo.alpha will return 0.5, without the foosheet constructor
     needing special code to set alpha.
  
  2. They can be dynamic.  If a Parameter is declared as Dynamic, it can
     be set to be a callable object (e.g a function), and getting the
     parameter's value will call that callable.  E.g.  To cause all
     FooSheets to draw their gammas from a gaussian distribution you'd
     write something like:
  
        from random import gauss
        FooSheet.sigma = Dynamic(lambda:gauss(0.5,0.1))
  
     If a Dynamic Parameter's value is set to a Python generator or iterator,
     then when the Parameter is accessed, the iterator's .next() method
     is called.  So to get a parameter that cycles through a sequence,
     you could write:
        from itertools import cycle
        FooSheet.sigma = Dynamic(cycle([0.1,0.5,0.9]))
  
  3. The Parameter descriptor class can be subclassed to provide more
     complex behavior, allowing special types of parameters that, for
     example, require their values to be numbers in certain ranges, or
     read their values from a file or other external source.


  Note: See this HOW-TO document for a good intro to descriptors in
  Python:
          http://users.rcn.com/python/download/Descriptor.htm
  """

  __slots__ = ['name','default','doc']
  count = 0
  
  def __init__(self,default=None,doc=""):
    """
    Initialize a new parameter.


    Set the name of the parameter 
    Set the name of the parameter to a gensym, and initialize
    the default value.
    """
    # CEB:
    # parameter name should probably match the variable name, e.g.
    # x = Parameter()
    # x.name = 'x'
    self.name = "_param" + `Parameter.count`
    self.doc = doc
    Parameter.count += 1
    self.default = default

  def __get__(self,obj,objtype):
    """
    Get a parameter value.  If called on the class, produce the
    default value.  If called on an instance, produce the instance's
    value, if one has been set, otherwise produce the default value.
    """
    if not obj:
        result = self.default
    else:
        result = obj.__dict__.get(self.name,self.default)
    return result


  def __set__(self,obj,val):
    """
    Set a parameter value.  If called on a class parameter,
    set the default value, if on an instance, set the value of the
    parameter in the object, where the value is stored in the
    instance's dictionary under the parameter's name gensym.
    """    
    if not obj:
        self.default = val
    else:
        obj.__dict__[self.name] = val

  def __delete__(self,obj):
    """
    Delete a parameter.  Raises an exception.
    """
    raise "Deleting parameters is not allowed."


  def _get_doc(self):
    return self.doc
  __doc__ = property(_get_doc)


  
class Number(Parameter):
  """
  Number is a numeric parameter. Numbers have a default value, and bounds.
  There are two types of bounds: `bounds' and `softbounds'.`bounds' are
  hard bounds: the parameter must have a value within the specified range.
  The default bounds are (None,None), meaning there are actually no hard bounds.
  One or both bounds can be set by specifying a value (e.g. bounds=(None,10) means
  there is no lower bound, and an upper bound of 10).
  Bounds are checked when a Number is created, and whenever its value is set.

  `softbounds' are present to indicate the typical range of the parameter, but are
  not enforced. Setting the soft bounds allows, for instance, a GUI to know what values
  to display on sliders for the Number.

  Example of creating a parameter:
  AB = Number(default=0.5, bounds=(None,10), softbounds=(0,1), doc='Distance from A to B.')
  """
  def __init__(self,default=0.0,bounds=(None,None),softbounds=(None,None),doc=""):
    Parameter.__init__(self,default=default,doc=doc)
    self.bounds = bounds
    self._softbounds = softbounds  
    self._check_bounds(default)

  def __set__(self,obj,val):
    self._check_bounds(val)        
    super(Number,self).__set__(obj,val)

  def _check_bounds(self,val):
    """
    Checks that the value is numeric, and checks the hard bounds
    """

    # CEB: all the following error messages should probably print out the parameter's name
    # ('x', 'theta', or whatever)
    if not (isinstance(val,int) or isinstance(val,float)):
      raise "Parameter " + `self.name` + " (" + `self.__class__` + ") only takes a numeric value."

    min,max = self.bounds
    if min != None and max != None:
      if not (min <= val <= max):
        raise "Parameter must be between " + `min` + ' and ' + `max` + ' (inclusive).'
    elif min != None:
      if not min <= val: 
        raise "Parameter must be at least " + `min` + '.'
    elif max != None:
      if not val <= max:
        raise "Parameter must be at most"+`min`+'.'

  def get_soft_bounds(self):
    """
    For each soft bound (upper and lower), if there is a defined bound (not equal to None)
    then it is returned, otherwise it defaults to the hard bound. The hard bound could still be None.
    """
    if not (self.softbounds[0]==None):
      lower_bound = self.softbounds[0]
    else:
      lower_bound = self.bounds[0]

    if not (self.softbounds[1]==None):
      upper_bound = self.softbounds[1]
    else:
      upper_bound = self.bounds[1]

    return (lower_bound, upper_bound)
        

class Integer(Number):
  def __set__(self,obj,val):
    if not isinstance(val,int):
      raise "Parameter must be an integer."
    super(Integer,self).__set__(obj,val)

class Magnitude(Number):
  def __init__(self,default=1.0,softbounds=(None,None),doc=""):
    Number.__init__(self,default=default,bounds=(0.0,1.0),softbounds=softbounds,doc=doc)

class BooleanParameter(Parameter):
  def __init__(self,default=False,bounds=(0,1),doc=""):
    Parameter.__init__(self,default=default,doc=doc)
    self.bounds = bounds
    
  def __set__(self,obj,val):
    if not isinstance(val,bool):

      raise "BooleanParameter only takes a Boolean value."
    if val != True and val != False:

        raise "BooleanParameter must be True or False"
    super(BooleanParameter,self).__set__(obj,val)


class Dynamic(Parameter):
  def __get__(self,obj,objtype):
    """
    Get a parameter value.  If called on the class, produce the
    default value.  If called on an instance, produce the instance's
    value, if one has been set, otherwise produce the default value.
    """
    if not obj:
        result = produce_value(self.default)
    else:
        result = produce_value(obj.__dict__.get(self.name,self.default))
    return result


def produce_value(value_obj):
  """
  A helper function, produces an actual parameter from a stored
  object.  If the object is callable, call it, else if it's an
  iterator, call its .next(), otherwise return the object
  """
  if callable(value_obj):
      return value_obj()
  if is_iterator(value_obj):
      return value_obj.next()
  return value_obj


def is_iterator(obj):
  """
  Predicate that returns whether an object is an iterator.
  """
  import types
  return type(obj) == types.GeneratorType or ('__iter__' in dir(obj) and 'next' in dir(obj))


