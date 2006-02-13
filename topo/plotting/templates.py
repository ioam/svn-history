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
    normalize = Parameter('False')
    
    def __init__(self, plot_templates=[], static_images = [],**params):
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
       
	self.plot_templates = KeyedList(plot_templates)
	self.static_images = KeyedList(static_images)

    ### JCALERT! We might eventually write this function 'Python-like'
    ### by using keyword argument to specify each channel a,d then get the dictionnary 
    ### of all remaining argument....
    def add_plot(self,name,specification_tuple_list):
	dict={}
	for key,value in specification_tuple_list:
	    dict[key]=value
	self.plot_templates.append((name,dict))

    ### JCALERT! We might eventually write this function 'Python-like'
    ### by using keyword argument to specify each channel a,d then get the dictionnary 
    ### of all remaining argument....
    def add_static_image(self,name,file_path):
	self.static_images.append((name,file_path))
        



###############################################################################
# Specific PlotGroupTemplates are stored in this repository,
# to which users can add their own as needed
plotgroup_templates = KeyedList()



###############################################################################
# Sample plots; users can override any of these as necessary
#
# JABALERT: Should eventually remove anything mentioning OrientationPreference
# or OrientationSelectivity from here, and instead set those up in
# measure_or_pref or somewhere like that.  That way, there will be no special
# treatment of any particular input feature.

# JABALERT:
# We should also be able to store things like the Normalize option setting
# (currently ignored?) and a documentation string describing each plot
# (for hovering help text) within each template.
# JC: we should also maybe add the situate option (and auto-refresh?)
### we might want to pass a plotgroup_type to the template
### (see corresponding alert in PlotGroupPanel)

def new_plotgroup_template(name,command,normalize=False):
    pgt = PlotGroupTemplate(name=name,command=command,normalize=normalize)
    plotgroup_templates[pgt.name]=pgt
    return pgt

pgt = new_plotgroup_template(name='Activity',command='update_activity()')
pgt.add_plot('Activity',[('Strength','Activity'),('Hue','OrientationPreference')])

### JCALERT! unitweightpanel could be re-named Connectionfields panel...?
### Also, the situate option could be specified in the template.
### Also implement the test for 'Weights' in PlotGroup.
pgt = new_plotgroup_template(name='Connection Fields',command='update_connectionfields()',normalize='True')
pgt.add_plot('Connection Fields',[('Strength','Weights'),('Hue','OrientationPreference')])


pgt = new_plotgroup_template(name='Projection',command='update_projections()',normalize='True')
pgt.add_plot('Projection',[('Strength','Weights'),('Hue','OrientationPreference')])


pgt = new_plotgroup_template(name='Orientation Preference',command='measure_or_pref()')
pgt.add_plot('Orientation Preference',[('Hue','OrientationPreference')])
pgt.add_plot('Orientation Preference&Selectivity',[('Hue','OrientationPreference'),
						   ('Confidence','OrientationSelectivity')])
pgt.add_plot('Orientation Selectivity',[('Strength','OrientationSelectivity')])
# This line is commented out while the re-sizing is being fixed in plotgrouppanel.py
pgt.add_static_image('Color Key','topo/commands/or_key_white_vert.png')


pgt = new_plotgroup_template(name='Position Preference',command='measure_position_pref() ; topographic_grid()',normalize=True)
pgt.add_plot('X Preference',[('Strength','XPreference')])
pgt.add_plot('Y Preference',[('Strength','YPreference')])
pgt.add_plot('Position Preference',[('Red','XPreference'),('Green','YPreference')])



pgt = new_plotgroup_template(name='Center of Gravity',command='measure_cog() ; topographic_grid(xsheet_view_name="XCoG",ysheet_view_name="YCoG")',normalize=True)
pgt.add_plot('X CoG',[('Strength','XCoG')])
pgt.add_plot('Y CoG',[('Strength','YCoG')])
pgt.add_plot('CoG',[('Red','XCoG'),('Green','YCoG')])



