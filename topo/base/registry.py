"""
Central location for registering and retrieving information needed by
Topographica.  Primarily useful when extending Topographica to provide
new components; once the components are registered here, they will
usually show up automatically in menus, online help, etc.  

$Id$
"""
__version__='$Revision$'
from keyedlist import KeyedList


############################################################
# Global repository of plot templates, which can be augmented
# as necessary.
plot_templates = {}
plotgroup_templates = KeyedList()


############################################################
# Global repository for links between a plot group template name and a
# subclassed Plot Panel to use instead of the default.
#
# An example: plotpanel_classes['Hue Pref Map'] = HuePreferencePanel
plotpanel_classes = {}
