"""
Module for handling parameters and defaults.

This module is a placeholder for our params/defaults database system
(whatever that ends up being).  Right now it just holds one function.
$Id$
"""

def get_param(param_name,dict,default=None):
  """
  Get the named parameter from a dictionary, else return the default.
  """
  if param_name in dict:
    return dict[param_name]
  elif '__defaults__' in dict:
    return get_param(param_name,dict['__defaults__'],default)
  else:
    return default

def setup_params(obj,cls,**params):

  #print "Setting params for ", obj, " of class ", cls
  for var,val in cls.__dict__.items():
    if var[:2] != '__':
      try:
        #print "Trying to set ", var
        obj.__dict__[var] = params[var]
        #print "Set ", var, " to ", obj.__dict__[var]
      except KeyError:
        pass
