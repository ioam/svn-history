"""
PlotGroupTemplate class, and global repository of such objects.

These classes allow users to specify different types of plots in a way
that is independent of particular models or Sheets.

$Id$
"""
__version__='$Revision$'


from topo.base.topoobject import TopoObject
from topo.misc.keyedlist import KeyedList
from topo.base.parameter import Parameter


### JABHACKALERT: Should just eliminate this class, and pass the dictionaries
### themselves around for consistency.
class PlotTemplate(TopoObject):
    def __init__(self, channels=None,**params):
        super(PlotTemplate,self).__init__(**params)
        #self.background = Dynamic(default=background)
        self.channels = channels


class PlotGroupTemplate(TopoObject):
    """
    Class specifying how to construct a PlotGroup from the objects in a Simulator.

    A PlotGroupTemplate is a data structure that specifies how to
    construct a set of related plots, when later given a set of Sheets
    in a Simulator.  The template can be modified however the user
    wishes, allowing the user to control what information is shown in
    plots, how the data is displayed, and so on.  A single template is
    sufficient for any model, because the template does not include
    any information about specific Sheets.  Thus the templates can be
    modified whenever the user desires, but do not *usually* need to
    be modified.
    """
    
    command = Parameter(None)
    
    def __init__(self, plot_templates=None, **params):
        """
        A PlotGroupTemplate is constructed from a name, an (optional)
        command that the user specifies should be called before using the
        PlotGroupTemplate, and a plot_templates list.  The plot_templates
        list should contain tuples (plot_name, plot_template).  Each
        plot_template is a dictionary of (name, value) pairs, where each
        name specifies a plotting channel (such as Hue or Confidence), and
        the value is the name of a SheetView (such as Activity or
        OrientationPreference).  Current channels include Strength,
        Hue, and Confidence, but others will be added in the future
        such as Red, Green, Blue, Outline, etc.
    
        For instance, one could define an Orientation-colored Activity
        plot as:
        
        pgt.plot_templates['Activity'] =
          PlotGroupTemplate(name='Activity', command='measure_activity()',
                            plot_templates=[('Activity',
                                             {'Strength'   : 'Activity',
                                              'Hue'        : 'OrientationPreference',
                                              'Confidence' : None})])
    
        This specifies that there will be up to one Plot named Activity in
        the final PlotGroup per Sheet, although there could be no plots at
        all if no Sheet has a SheetView named Activity.  The Plot will be
        colored by OrientationPreference if such a SheetView exists, and
        the value channel will be determined by the SheetView Activity.
    
        Here's a more complicated example specifying two different plots
        in the same PlotGroup:
    
          PlotGroupTemplate(name='Orientation Preference', command = 'measure_or_pref()',
                            plot_templates=[('Orientation Preference',
                                             {'Strength'   : None,
                                              'Hue'        : 'OrientationPreference',
                                              'Confidence' : None}),
                                            ('Orientation Selectivity',
                                             {'Strength'   : 'OrientationSelectivity',
                                              'Hue'        : None,
                                              'Confidence' : None})])
    
        Here the PlotGroup will contain up to two Plots per Sheet,
        depending on which Sheets have OrientationPreference and
        OrientationSelectivity.
        """
        
        super(PlotGroupTemplate,self).__init__(**params)
        ### JABALERT: Why would plot_templates ever be None?
        if not plot_templates:
            self.plot_templates = KeyedList()
        else:
            self.plot_templates = KeyedList(plot_templates)
        ### JABALERT: Why on earth do we copy name to description?
        self.description = self.name
        


###############################################################################
# Specific PlotGroupTemplates are stored in this repository,
# to which users can add their own as needed
plot_templates = {} # JABHACKALERT! What is this for?
plotgroup_templates = KeyedList()



###############################################################################
# Sample plots; users can override any of these as necessary
#
# JABALERT: Should eventually remove anything mentioning OrientationPreference
# or OrientationSelectivity from here, and instead set those up in
# measure_or_pref or somewhere like that.  That way, there will be no special
# treatment of any particular input feature.

# JABALERT: This interface needs some cleanup to make it easier to use.
# For instance, we can implement an add_plot_template function,
# accepting a single plot and adding it to a PlotGroupTemplate (which
# is created the first time it is needed).

pgt = PlotGroupTemplate([('Activity',
                          PlotTemplate({'Strength'   : 'Activity',
                                        'Hue'        : 'OrientationPreference',
                                        'Confidence' : None,
                                        'Normalize'  : False}))],
                        name='Activity',
                        command='measure_activity()')
plotgroup_templates[pgt.name] = pgt


pgt = PlotGroupTemplate([('Unit Weights',
                          PlotTemplate({'Strength'   : 'Weights',
                                        'Hue'        : 'OrientationPreference',
                                        'Confidence' : None,
                                        'Normalize'  : True}))],
                        name='Unit Weights',
                        command='pass')
plotgroup_templates[pgt.name] = pgt

### JCALERT: I will remove Density and Projection_name at some point.
pgt = PlotGroupTemplate([('Projection',
                          PlotTemplate({'Strength'        : 'Weights',
					'Hue'             : 'OrientationPreference',
                                        'Confidence'      : None,
                                        'Normalize'       : True,
                                        'Density'         : 25,
                                        'Projection_name' : 'None'}))],
                        name='Projection',
                        command='pass')
plotgroup_templates[pgt.name] = pgt

pgt = PlotGroupTemplate([('Orientation Preference',
                          PlotTemplate({'Strength'   : None,
                                        'Hue'        : 'OrientationPreference',
                                        'Confidence' : None})),
                         ('Orientation Preference&Selectivity',
                          PlotTemplate({'Strength'   : None,
                                        'Hue'        : 'OrientationPreference',
                                        'Confidence' : 'OrientationSelectivity'})),
                         ('Orientation Selectivity',
                          PlotTemplate({'Strength'   : 'OrientationSelectivity',
                                        'Hue'        : None,
                                        'Confidence' : None}))],
                        name='Orientation Preference',
                        command = 'measure_or_pref()')
plotgroup_templates[pgt.name] = pgt
