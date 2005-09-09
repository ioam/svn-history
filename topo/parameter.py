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
  
  def __init__(self,default=None,doc="Undocumented parameter."):
    """
    Initialize a new parameter.

    Set the name of the parameter to a gensym, and initialize
    the default value.
    """
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


### JABHACKALERT!
###
### I guess this is not a hack per se, but Number and the other
### numeric classes below need to be extended somehow to allow soft
### bounds as well as the current hard ones.  The soft bound would
### specify a typical range, to suggest bounds for e.g. a GUI slider
### for this quantity, but would not enforce those bounds.  E.g. there
### could be an extra tuple parameter ",enforce=(True,True)' (by
### default).  Of course, the bounds would only be enforced if not
### None.
###
### JBD: This is also important for a flexible and dynamic
### InputParamsPanel since the sliders need to have different values
### depending upon the kernel type.
  
class Number(Parameter):
  def __init__(self,default=None,bounds=(None,None)):
    Parameter.__init__(self,default=default)
    self.bounds = bounds
    
  def __set__(self,obj,val):
    if not (isinstance(val,int) or isinstance(val,float)):
      raise "Parameter only takes a numeric value."

    min,max = self.bounds
    if min != None and max != None:
      if not (min <= val <= max):
        raise "Parameter must be between"+`min`+'and'+`max`+', inclusive.'
    elif min != None:
      if not min <= val: 
        raise "Parameter must be at least"+`min`+'.'
    elif max != None:
      if not val <= max:
        raise "Parameter must be at most"+`min`+'.'
        
    super(Number,self).__set__(obj,val)

class Integer(Number):
  def __set__(self,obj,val):
    if not isinstance(val,int):
      raise "Parameter must be an integer."
    super(Integer,self).__set__(obj,val)

class NonNegativeInt(Integer):
  def __init__(self,default=0):
    Integer.__init__(self,default=default,bounds=(0,None))

class PositiveInt(Integer):
  def __init__(self,default=1):
    Integer.__init__(self,default=default,bounds=(1,None))
                    
class Magnitude(Number):
  def __init__(self,default=1):
    Number.__init__(self,default=default,bounds=(0.0,1.0))


class BooleanParameter(Parameter):
  def __init__(self,default=False,bounds=(0,1)):
    Parameter.__init__(self,default=default)
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


