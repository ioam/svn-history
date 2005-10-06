"""
Topographica package; all important files are in subpackages.

$Id$
"""

__all__ = ['base','sheets','projections','patterns','eps','plotting']

# Enable automatic importing of .ty files, treating them just like .py
import topo.base.tyimputil
