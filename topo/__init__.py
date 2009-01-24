"""
Topographica cortical map simulator package.

Topographica is designed as a collection of packages from which
elements can be selected to model specific systems.  For more
information, see the individual subpackages::

  base           - Core Topographica functions and classes
  plotting       - Visualization functions and classes
  analysis       - Analysis functions and classes (besides plotting)
  tkgui          - Tk-based graphical user interface (GUI)
  command        - High-level user commands
  misc           - Various useful independent modules

The Topographica primitives library consists of a family of classes
that can be used with the above functions and classes::

  sheet          - Sheet classes: 2D arrays of processing units
  projection     - Projection classes: connections between Sheets
  pattern        - PatternGenerator classes: 2D input or weight patterns 
  ep             - EventProcessor classes: other simulation objects
  outputfn       - Output functions, for e.g. normalization or squashing
  responsefn     - Calculate the response of a Projection
  learningfn     - Adjust weights for a Projection
  coordmapper    - CoordinateMapperFn classes: map coords between Sheets

Each of the library directories can be extended with new classes of
the appropriate type, just by adding a new .py file to that directory.
E.g. new PatternGenerator classes can be added to pattern/, and will
then show up in the GUI menus as potential input patterns.

$Id$
"""
__version__ = "$Revision$"

# The tests and the GUI are omitted from this list, and have to be
# imported explicitly if desired.
__all__ = ['analysis',
           'base',
           'command',
           'coordmapper',
           'ep',
           'learningfn',
           'misc',
           'outputfn',
           'param',
           'pattern',
           'plotting',
           'projection',
           'responsefn',
           'sheet']

# get set by the topographica script
release = ''
version = ''



# CEBALERT: can we move these pickle support functions elsewhere?
# In fact, can we just gather all the non-legacy pickle garbage into one
# place? I'd even like to get stuff out of classes, but I guess that
# wouldn't always be desirable.
# (What prompted this note is that, apart from the clutter the pickle
# methods add to classes, I cannot remember all the ways one can
# support pickling; the answer to any new pickle problem is often
# spread throughout all the pickle methods I've ever added...)


# (note that these _pickle_support functions also work for deep copying)
def _numpy_ufunc_pickle_support():
    """
    Allow instances of numpy.ufunc to pickle.
    """
    # Remove this when numpy.ufuncs themselves support pickling.
    # Code from Robert Kern; see:
    #http://news.gmane.org/find-root.php?group=gmane.comp.python.numeric.general&article=13400
    from numpy import ufunc
    import copy_reg

    def ufunc_pickler(ufunc):
        """Return the ufunc's name"""
        return ufunc.__name__

    copy_reg.pickle(ufunc,ufunc_pickler)

_numpy_ufunc_pickle_support()


def _mpq_pickle_support():
    """Allow instances of gmpy.mpq to pickle."""
    from gmpy import mpq
    mpq_type = type(mpq(1,10)) # CEBALERT: any idea how to get this properly?
    import copy_reg
    copy_reg.pickle(mpq_type,lambda q: (mpq,(q.digits(),)))



def _instance_method_pickle_support():
    """Allow instance methods to pickle."""
    # CB: well, it seems to work - maybe there are cases where this
    # wouldn't work?
    def _pickle_instance_method(mthd):
        mthd_name = mthd.im_func.__name__
        obj = mthd.im_self
        return getattr, (obj,mthd_name)

    import copy_reg, types
    copy_reg.pickle(types.MethodType, _pickle_instance_method)

_instance_method_pickle_support()


# Set the default value of Simulation.time_type to gmpy.mpq
# (or the slower fixedpoint.FixedPoint if gmpy is unavailable)
try:
    import gmpy
    time_type = gmpy.mpq
    time_type_args = ()
    _mpq_pickle_support()
except ImportError:
    import fixedpoint
    time_type = fixedpoint.FixedPoint
    time_type_args = (4,)  # gives precision=4

from topo.base.simulation import Simulation
Simulation.time_type = time_type
Simulation.time_type_args = time_type_args

sim = Simulation() 





def about(display=True):
    """Print release and licensing information."""

    ABOUT_TEXT = """
Pre-release version %s (%s) of Topographica; an updated
version may be available from topographica.org.

Copyright 2005-2008 James A. Bednar, Jan Antolik, Christopher Ball,
Yoonsuck Choe, Julien Ciroux, Judah B. De Paula, Foivos Demertzis,
Kateryna Gerasymova, Veldri Kurniawan, Judith Law, Alan Lindsay,
Louise Mathews, Lewis Ng, Christopher Palmer, Ruaidhri Primrose,
Jefferson Provost, Tikesh Ramtohul, Yiu Fai Sit, Stuart Wilson, and
Roger Zhao.


This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License version 2 as
published by the Free Software Foundation. This program is distributed
in the hope that it will be useful, but without any warranty; without
even the implied warranty of merchantability or fitness for a
particular purpose.  See the GNU General Public License for more
details.
"""%(release,version)
    if display:
        print ABOUT_TEXT
    else:        
        return ABOUT_TEXT


# Set most floating-point errors to be fatal for safety; see
# topo/misc/patternfn.py for examples of how to disable
# the exceptions when doing so is safe.  Underflow is always
# considered safe; e.g. input patterns can be very small
# at large distances, and when they are scaled by small
# weights underflows are common and not a problem.
from numpy import seterr
old_seterr_settings=seterr(all="raise",under="ignore")


