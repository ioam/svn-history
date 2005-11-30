"""
PlotTemplate and PlotGroupTemplate classes.

It is also the file where the different PlotGroupTemplate currently
in used are defined and registered in the topo.base.registry.

The user is then supposed to define new PlotGroupTemplate in this place.

$Id$
"""
__version__='$Revision$'


from topo.base.topoobject import TopoObject
from topo.base.keyedlist import KeyedList
from topo.base.parameter import Parameter

### JCALERT! Fill the doc when the PlotTemplates for UnitWeight and Projection
### will be definitly set.

class PlotTemplate(TopoObject):
    """
    Container class for a Plot object, i.e. template that
    contains the indications required for creating the Plot.
    It should be used as part of a PlotGroupTemplate that defines
    templates for a PlotGroup.

    A PlotTemplate is essentially a dictionary that stores reference to
    potentially existing SheetView for a given heet.
    
    The templates are used so that standard plot types
    can be redefined at the users convenience.

    For example the template for an activity Plot can be:

    activity_template = PlotTemplate({'Strength'   : 'Activity',
                                      'Hue'        : None,
                                      'Confidence' : None})
                                      
    Where 'Activity' is the key to a (potential) sheet_view 
    
    Kinds of current PlotTemplates:
    SHC Plots:
             Keys:
           
    Unit Weights Plots:
             Keys:
            
    """


    def __init__(self, channels=None,**params):
        super(PlotTemplate,self).__init__(**params)
        #self.background = Dynamic(default=background)
        self.channels = channels
        

### JCALERT! review the code when we know where the command for PlotGroupTemplate
### are defined.
        
class PlotGroupTemplate(TopoObject):
    """
    Container class for a PlotGroup object definition,i.e. template that
    contains the indications required for creating the PlotGroup.
    
    A PlotGroupTemplate essentially stores a KeyedList (dictionnary that is sorted)
    that contains tuples (PlotTemplate_name, PlotTemplate).
    Then, a parameter name define the PlotGroupTemplate name,
    and a parameter command define a string that refers to the command
    executed when requiring the corresponding PlotGroup.
    

    The plot_templates member dictionary (KeyedList) can and should be
    accessed directly by outside code.  It is a KeyedList (defined in
    this file) so it can be treated like a dictionary using the []
    notation, but it will preserve ordering.  An example definition:

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

    pgt.plot_templates['ActivityPref'] = newPlotTemplate
    """


    command = Parameter(None)
    def __init__(self, plot_templates=None, **params):
        """
        plot_templates are of the form:
            ( (name_1, PlotTemplate_1), ... , (name_i, PlotTemplate_i) )
        """
        
        super(PlotGroupTemplate,self).__init__(**params)
        if not plot_templates:
            self.plot_templates = KeyedList()
        else:
            self.plot_templates = KeyedList(plot_templates)
        self.description = self.name
        

### JCALERT! Review the doc here or at the top of the file...
### maybe put the import at the top
### make a nice place for user to find easily.
        
### Populate the dynamic plot menu list registry.
        
import topo.base.registry

pgt = PlotGroupTemplate([('Activity',
                          PlotTemplate({'Strength'   : 'Activity',
                                        'Hue'        : 'OrientationPreference',
                                        'Confidence' : None,
                                        'Normalize'  : False}))],
                        name='Activity',
                        command='measure_activity()')


# CEBHACKALERT: putting OrientationPreference in Hue is ok while we are only
# talking about orientation maps.

topo.base.registry.plotgroup_templates[pgt.name] = pgt
pgt = PlotGroupTemplate([('Unit Weights',
                          PlotTemplate({'Location'   : (0.0,0.0),
                                        'Normalize'  : True,
					'Sheet_name' : 'V1'}))],
                        name='Unit Weights',
                        command='pass')
topo.base.registry.plotgroup_templates[pgt.name] = pgt
pgt = PlotGroupTemplate([('Projection',
                          PlotTemplate({'Density'         : 25,
                                        'Projection_name' : 'None',
                                        'Normalize'       : True}))],
                        name='Projection',
                        command='pass')
topo.base.registry.plotgroup_templates[pgt.name] = pgt
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
topo.base.registry.plotgroup_templates[pgt.name] = pgt
