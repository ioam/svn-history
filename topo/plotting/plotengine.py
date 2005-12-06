"""
Construct and stores the PlotGroups used for saving to a file or for a GUI to display.

This class is the connection between the Simulator or GUI, and the
PlotGroup objects in plotting.

When first creating a PlotGroup, PlotEngine stores it in a dictionary,using a plot_group_key as a key.

The PlotGroup can then be retrieved in the dictionnary for later use.

The plot_group_key is the simple name of the PlotGroupTemplate for a BasicPlotGroupPanel PlotGroup
(i.e. A Preference Map panel or an Activity panel)
The plot_group_key is more complicated for UnitWeightsPlotGroup and ProjectionPlotGroup
(see the corresponding UnitWeightsPanel and ProjectionPanel generate_plot_group_key methods)
It is then possible to imagine other type of plot_group_key, as soon as it identified
a single PlotGroup.

$Id$ 
"""


### JABHACKALERT!  The documentation above needs substantial
### clarification -- less detail, more sense.
### JC: I think I improved it a bit, but still need some work.


__version__='$Revision$'

### JCALERT! This file has been clarified a lot.
### Nevertheless, it still remains little alerts that need to be solved
### and the doc still have to be corrested and reviewed

from topo.base.topoobject import TopoObject
### JCALERT! import *: I don't know how to do it otherwise...
### (It has to import any possible PlotGroup...)
from plotgroup import *


class PlotEngine(TopoObject):
    """
    Creates and stores the main list of PlotGroup available to a simulation.
    """

    def __init__(self, simulation, **params):
        """
        Creates a new plot engine that is linked to a particular
        simulation.  The link is necessary since the PlotEngine will
        iterate over all the Sheets  in the simulation, requesting SheetViews
        when necessary.
        """
        super(PlotEngine,self).__init__(**params)
	### JCALERT! maybe change simulation to be simulator 
        ### (carefull to also change the call to it in any other files) 
        self.simulation = simulation
        self.plot_group_dict = {}


    def add_plot_group(self, name, group):
        """
        Add a constructed PlotGroup to the local PlotEngine dictionary for later
        reuse.  User defined plots should be stored here for later use.
        """
        self.plot_group_dict[name] = group

        
    ### JABALERT!  It is strange for this to call make_plot_group;
    ### that call should either be justified or removed.

    ### JC: if the PlotGroup corresponding to the group has already been inserted in
    ### the self.plot_group_dict, it is taken when requested;
    ### otherwise, it seems necessary to create the PlotGroup
    ### also name is generally a plot_group_key for unitweight and projection panel

    ### JCALERT!!! We also might want to get rid of the default value for class_type,
    ### then changed the order and put filter at the end, and changing the call
    ### to any get_plot_group
    ### Also I would change group_type to be template or group_template
    ### (Actually, if we want to just have a PlotGroup that we know has already been created,
    ### it might be useful to call just with the name, In this case, we have to solve the problem
    ### of catching the exception when there is no such PlotGroup in the dict and group_type=None.
    ### Note that for the moment, such a call only happens in the testplotengine.py.)
    ### I would change name to plot_group_key and group_type to template.
        
    def get_plot_group(self, plot_group_key, plot_group_template,
                       class_type='BasicPlotGroup',filter=None):
        """
        Return the PlotGroup registered in self.plot_group_dict with
        the provided key 'name'.  If the name does not exist, then
        creates the requested by calling make_plot_group, and then add it
        to the dictionnary for later reuse. 
	"""
        if filter == None:
            filter = lambda s: True
        elif isinstance(filter,str):     # Allow sheet string name as input.
            target_string = filter
            filter = lambda s: s.name == target_string
        
        if self.plot_group_dict.has_key(plot_group_key):
            self.debug(plot_group_key, "key match in PlotEngine's PlotGroup list")
            requested_plot = self.plot_group_dict[plot_group_key]
        else:
            requested_plot = self.make_plot_group(plot_group_key,plot_group_template,class_type,filter)
        return requested_plot

    
    ### JCALERT!  I would change group_type to be template or group_template
    ### and name to be plot_group_key....
    
    def make_plot_group(self,plot_group_key,plot_group_template,class_type,filter):
        """
        name : The key to look under in the SheetView dictionaries.
        group_type: 2 Valid inputs:
               1. The string name of the PlotGroup subclass to create.
                  The actual name is passed in instead of a class
                  pointer so the function can be used from the
                  command-line, and also so a full list of class names
                  is not required.
               2. If group_type is a PlotGroupTemplate, then the
                  lambda function to handle templates is called.
        filter_lam: Optional lambda function to filter which sheets to
               ask for SheetViews.
        """
       
        ### JCALERT ! This could eventually disappear when ckeaning PlotGroup and not passing any list
        ### when creating it (i.e. got rid of the parameter plot_list in the __init__)
        dynamic_list=[]

        ### JCALERT! I think we can spare the in globals.
        exec 'ptr = ' + class_type  in globals()

        new_group = ptr(self.simulation,plot_group_template,plot_group_key,filter,dynamic_list)

        ### JCALERT! I left this comment but does not understand it...
        # Just copying the pointer.  Not currently sure if we want to
        # promote side-effects by not doing a deepcopy(), but assuming
        # we do for now.  If not, use deepcopy(group_type).

        self.add_plot_group(plot_group_key,new_group)
	    
        self.debug('Type of new_group is', type(new_group))
        return new_group

  
