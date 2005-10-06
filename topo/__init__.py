"""
Topographica package; all important files are in subpackages.

$Id$
"""

__all__ = ['base','sheets','projections','patterns','eps','plotting']

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

