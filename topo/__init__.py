"""
Topographica cortical map simulator package.

Topographica is designed as a collection of packages from which
elements can be selected to model specific systems.  For more
information, see the individual subpackages:

base        - Core Topographica functions and classes
plotting    - Visualization functions and classes
tk          - Tk-based graphical user interface (GUI)

The Topographica primitives library consists of a family of classes
that can be used with the above functions and classes:

sheets      - Sheet classes: 2D arrays of processing units
projections - Projection classes: connections between Sheets
patterns    - PatternGenerator classes: 2D input or weight patterns 
eps         - EventProcessor classes: other simulator objects

Each of the library directories can be extended with new classes of
the appropriate type, just by adding a new .py file to that directory.
E.g. new PatternGenerator classes can be added to patterns/, and will
then show up in the GUI menus as potential input patterns.

$Id$
"""

__all__ = ['base','commands','sheets','projections','patterns','eps','plotting']

# Enable automatic importing of .ty files, treating them just like .py
import topo.base.tyimputil


ABOUT_TEXT = """
Pre-release version of Topographica; please do not trust this version
of the code unless you have verified it yourself.  An updated version
may be available from topographica.org.

Copyright 2005 James A. Bednar, Christopher Ball, Yoonsuck Choe,
Julien Ciroux, Judah B.  De Paula, Jefferson Provost, Joseph
Reisinger, and Yiu Fai Sit.

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License version 2 as
published by the Free Software Foundation. This program is distributed
in the hope that it will be useful, but without any warranty; without
even the implied warranty of merchantability or fitness for a
particular purpose.  See the GNU General Public License for more
details.
"""

def about():
    """Print release and licensing information."""
    print ABOUT_TEXT

