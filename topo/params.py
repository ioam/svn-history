"""
Module for handling experiment parameters and defaults.

$Id$


This module defines an attribute descriptor for experiment
parameters.  An experiment parameter is represented in Topographica as
special kind of class attribute.

For example, suppose someone has defined a new kind of sheet, that has
parameters alpha, sigma, and gamma.  He would begin his class
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

2. They can be dynamic.  If a Parameter's value is set to a function
   or other callable object, getting the parameter's value will call
   that function/callable.  E.g.  To cause all FooSheets to draw their
   gammas from a gaussian distribution you'd write something like:

      from random import gauss
      FooSheet.sigma = lambda:gauss(0.5,0.1)

   If a Parameter's valuse is set to a Python generator or iterator,
   then when the Parameter is accessed, the iterator's .next() method
   is called.  So to get a parameter that cycles through a sequence,
   you could write:
      from itertools import cycle
      FooSheet.sigma = cycle([0.1,0.5,0.9])

3. The Parameter descriptor class can be subclassed to provide more
   complex behavior, allowing special types of parameters that, for
   example, require their values to be numbers in certain ranges, or
   read their values from a file or other external source.
"""

class Parameter(object):
  """
  An attribute descriptor file for Topographica parameters.  Setting a
  class attribute to be an instance of this class causes that
  attribute of the class and its instances to be treated as a
  parameter.  This allows special behavior, including dynamically
  generated parameter values (using lambdas or generators), and type
  or range checking at assignment time.
  
  Note: See this HOW-TO document for a good intro to descriptors in
  Python:
          http://users.rcn.com/python/download/Descriptor.htm
  """
  count = 0
  
  def __init__(self,default=None):
    """
    Initialize a new parameter.

    Set the name of the parameter to a gensym, and initialize
    the default value.
    """
    self.name = "_param" + `Parameter.count`
      Parameter.count += 1
      self.default = default

  def __get__(self,obj,objtype):
    """
    Get a parameter value.  If called on the class, produce the
    default value.  If called on an instance, produce the instance's
    value, if one has been set, otherwise produce the default value.
    """
    if not obj:
        result = __produce_value(self.default)
    else:
        result = __produce_value(obj.__dict__.get(self.name,self.default))
    return result



  def __set__(self,obj,val):
    """
    Set a parameter value.  If called on a class parameter,
    set the default value, if on an instance, set the value of the
    parameter in the object, where the value is stored in the
    instance's dictionary under the parameter's name gensym.
    """    
    if not obj:
        print "Setting default to",val
        self.default = val
    else:
        print "Setting value to",val
        obj.__dict__[self.name] = val

  def __del__(self,obj,val):
    """
    Delete a parameter.  Raises an exception.
    """
    raise "Deleting parameters is not allowed."


def __produce_value(value_obj):
  """
  A helper function, produces an actual parameter from a stored
  object.  If the object is callable, call it, else if it's an
  iterator, call its .next(), otherwise return the object
  """
  if callable(value_obj):
      return value()
  if iterable(value_obj):
      return value.next()
  return value_obj


def is_iterator(obj):
  """
  Predicate that returns whether an object is an iterator.
  """
  return '__iter__' in dir(obj) and 'next' in dir(obj)


def setup_params(obj,cls,**args):
  """
  Function to set up parameters in an object.  Takes an object, a
  class and a dictionary of  keyword arguments, as given to a
  constructor. The setup algorithm traverses the class's dictionary looking for attributes
  that are Parameters.  For each parameter it tries to set its value
  to the argument value of the same name, if one exists.
  """
  for name,val in cls.__dict__.items():
    if isinstance(val,Parameter)
      try:
        setattr(obj,name,args[name])
      except KeyError:
        pass


