"""
Topographica cortical map simulator package.

Topographica is designed as a collection of packages from which
elements can be selected to model specific systems.  For more
information, see the individual subpackages::

  base           - Core Topographica functions and classes
  plotting       - Visualization functions and classes
  analysis       - Analysis functions and classes (besides plotting)
  tkgui          - Tk-based graphical user interface (GUI)
  commands       - High-level user commands
  misc           - Various useful independent modules

The Topographica primitives library consists of a family of classes
that can be used with the above functions and classes::

  sheets         - Sheet classes: 2D arrays of processing units
  projections    - Projection classes: connections between Sheets
  patterns       - PatternGenerator classes: 2D input or weight patterns 
  eps            - EventProcessor classes: other simulation objects
  outputfns      - Output functions, for e.g. normalization or squashing
  responsefns    - Calculate the response of a Projection
  learningfns    - Adjust weights for a Projection
  coordmapperfns - CoordinateMapperFn classes: map coords between Sheets

Each of the library directories can be extended with new classes of
the appropriate type, just by adding a new .py file to that directory.
E.g. new PatternGenerator classes can be added to patterns/, and will
then show up in the GUI menus as potential input patterns.

$Id$
"""
__version__ = "$Revision$"

# The tests and the GUI are omitted from this list, and have to be
# imported explicitly if desired.
__all__ = ['analysis',
           'base',
           'commands',
           'coordmapperfns',
           'eps',
           'learningfns',
           'misc',
           'outputfns',
           'patterns',
           'plotting',
           'projections',
           'responsefns',
           'sheets']

# get set by the topographica script
release = ''
version = ''



                    


from topo.base.simulation import Simulation
sim = Simulation() 





def about(display=True):
    """Print release and licensing information."""

    ABOUT_TEXT = """
Pre-release version """+release+ \
""" of Topographica; an updated version may be
available from topographica.org.

Copyright 2005-2007 James A. Bednar, Jan Antolik, Christopher Ball,
Yoonsuck Choe, Julien Ciroux, Judah B. De Paula, Foivos Demertzis,
Veldri Kurniawan, Judith Law, Alan Lindsay, Louise Mathews, Lewis Ng,
Christopher Palmer, Ruaidhri Primrose, Jefferson Provost, Tikesh
Ramtohul, Yiu Fai Sit, Stuart Wilson, and Roger Zhao.

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License version 2 as
published by the Free Software Foundation. This program is distributed
in the hope that it will be useful, but without any warranty; without
even the implied warranty of merchantability or fitness for a
particular purpose.  See the GNU General Public License for more
details.
"""
    if display:
        print ABOUT_TEXT
    else:        
        return ABOUT_TEXT


# Set most floating-point errors to be fatal for safety; see
# topo/misc/patternfns.py for examples of how to disable
# the exceptions when doing so is safe.  Underflow is always
# considered safe; e.g. input patterns can be very small
# at large distances, and when they are scaled by small
# weights underflows are common and not a problem.
from numpy import seterr
old_seterr_settings=seterr(all="raise",under="ignore")


