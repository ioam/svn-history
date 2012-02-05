"""
Topographica plotting subsystem.

Two-dimensional plots are generated by generic classes for visualizing
Sheets in any model.  The plots are often viewed in a GUI, but they
can potentially also be rendered to bitmapped images to save as files,
or to display on other types of interfaces such as web servers.

The usual way that a plot is specified is using a PlotGroupTemplate,
which specifies a group of related plots.  A PlotGroupTemplate is a
list of PlotTemplates.  Each PlotTemplate will normally produce up to
one plot per Sheet in the network, though in special cases it can
produce more.  The definitions for each of these templates can be done
in advance of defining any particular model, and rarely require any
editing for any particular model.

For more information, see the various modules in this package.

$Id$
"""
__version__='$Revision$'
__all__ = ['bitmap','plot','plotgroup','plotfilesaver']
