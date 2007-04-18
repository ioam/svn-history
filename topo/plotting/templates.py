"""
PlotGroupTemplate class and global repository of such objects.

This code allows users to specify different types of plots in a way
that is independent of particular models or Sheets.  Search for
new_pgt elsewhere in the code to see examples of specific templates.

$Id$
"""
__version__='$Revision$'


from topo.base.parameterizedobject import ParameterizedObject
from topo.misc.keyedlist import KeyedList
from topo.base.parameterclasses import Parameter, BooleanParameter, Filename
from topo.base.parameterclasses import ListParameter, StringParameter


class PlotGroupTemplate(ParameterizedObject):
    """
    Class specifying how to construct a PlotGroup from the objects in a Simulation.

    A PlotGroupTemplate is a data structure that specifies how to
    construct a set of related plots, when later given a set of Sheets
    in a Simulation.  The template can be modified however the user
    wishes, allowing the user to control what information is shown in
    plots, how the data is displayed, and so on.

    A single template is sufficient for any model, because the
    template does not include any information about specific Sheets.
    Thus the templates can be modified whenever the user desires, but
    do not *usually* need to be modified.
    """
    
    command = Parameter("pass",
      doc="Command string to run before plotting, if any.")

    plotcommand=Parameter("pass",
      doc="Command string to run before plotting when no further measurement of responses is required")

    template_plot_type=Parameter('bitmap',
      doc="Whether the plots are bitmap images or curves, to determine which GUI components are needed")

    plot_immediately=BooleanParameter(False,doc="""
      Whether to call the plot command at once or only when the user asks for a refresh.

      Should be set to true for quick plots, but false for those that take a long time
      to calculate, so that the user can change the update command if necessary.""")
    
    normalize = BooleanParameter(False,
      doc="If true, enables bitmap plot value normalization by default.")

    image_location = Filename(doc='Path to search for a user-specified image.')

    prerequisites=ListParameter([],
      doc="List of preference maps which must exist before this plot can be calculated.")

    category = StringParameter(default="User",
      doc="Category to which this plot belongs, which will be created if necessary.")

    doc = StringParameter(default="",
      doc="Documentation string describing this type of plot.")

    def __init__(self, plot_templates=[], static_images = [],**params):
        """
        A PlotGroupTemplate is constructed from a name, a plot_templates
        list, an optional command to run to generate the data, and other
        optional parameters.

        The plot_templates list should contain tuples (plot_name,
        plot_template).  Each plot_template is a list of (name,
        value) pairs, where each name specifies a plotting channel
        (such as Hue or Confidence), and the value is the name of a
        SheetView (such as Activity or OrientationPreference).

        Various types of plots support different channels.  An SHC
        plot supports Strength, Hue, and Confidence channels (with
        Strength usually being visualized as luminance, Hue as a color
        value, and Confidence as the saturation of the color).  An RGB
        plot supports Red, Green, and Blue channels.  Other plot types
        will be added eventually.

        For instance, one could define an Orientation-colored Activity
        plot as::
        
          plotgroup_templates['Activity'] =
              PlotGroupTemplate(name='Activity', category='Basic',
                  command='measure_activity()',
                  plot_templates=[('Activity',
                      {'Strength': 'Activity', 'Hue': 'OrientationPreference', 'Confidence': None})])
    
        This specifies that the final PlotGroup will contain up to one
        Plot named Activity per Sheet, although there could be no
        plots at all if no Sheet has a SheetView named Activity once
        'measure_activity()' has been run.  The Plot will be colored
        by OrientationPreference if such a SheetView exists for that
        Sheet, and the value (luminance) channel will be determined by
        the SheetView Activity.  This plot will be listed in the
        category 'Basic'.
    
        Here's a more complicated example specifying two different plots
        in the same PlotGroup::
    
          PlotGroupTemplate(name='Orientation Preference', category='Basic'
              command = 'measure_or_pref()',
              plot_templates=
                  [('Orientation Preference',
                      {'Strength': None, 'Hue': 'OrientationPreference'}),
                   ('Orientation Selectivity',
                      {'Strength': 'OrientationSelectivity'})])
    
        Here the PlotGroup will contain up to two Plots per Sheet,
        depending on which Sheets have OrientationPreference and
        OrientationSelectivity SheetViews.
        """
        
        super(PlotGroupTemplate,self).__init__(**params)
       
	self.plot_templates = KeyedList(plot_templates)
	self.static_images = KeyedList(static_images)


    # JCALERT! We might eventually write these two functions
    # 'Python-like' by using keyword argument to specify each
    # channel and then get the dictionnary of all remaining
    # arguments.
    # 
    # JABALERT: We should also be able to store a documentation string
    # describing each plot (for hovering help text) within each
    # plot template.
    def add_plot(self,name,specification_tuple_list):
	dict={}
	for key,value in specification_tuple_list:
	    dict[key]=value
	self.plot_templates.append((name,dict))

    def add_static_image(self,name,file_path):
        self.image_location = file_path
	self.static_images.append((name,self.image_location))
        


plotgroup_templates = KeyedList()
"""
Global repository of PlotGroupTemplates, to which users can add
their own as needed.
"""


def new_pgt(**params):
    """
    Create a new PlotGroupTemplate and add it to the plotgroup_templates list.

    Convenience function to make it simpler to use the name of the
    PlotGroupTemplate as the key in the plotgroup_templates list.
    See the PlotGroupTemplate __init__ function for more details.
    """
    pgt = PlotGroupTemplate(**params)
    plotgroup_templates[pgt.name]=pgt
    return pgt

pgt = new_pgt(name='Caricaturization Preference',command='measure_caricaturization(display=True,weighted_average=False,pattern_presenter=PatternPresenter(pattern_generator=FaceSpace2Dfromfile(),apply_output_fn=True,duration=1.0))')
pgt.add_plot('Caricaturization Preference',[('Strength','CaricaturizationPreference')])
pgt.add_plot('Caricaturization Preference',[('Hue','CaricaturizationPreference')])
pgt.add_plot('Caricaturization Selectivity',[('Strength','CaricaturizationSelectivity')])
pgt.add_plot('Identity Preference',[('Strength','IdentityPreference')])
pgt.add_plot('Identity Preference',[('Hue','IdentityPreference')])
pgt.add_plot('Identity Selectivity',[('Strength','IdentitySelectivity')])

pgt = new_pgt(name='Face Preference',command='measure_face_pref(display=True,weighted_average=False,pattern_presenter=PatternPresenter(pattern_generator=FaceSpace2Dfromfile(),apply_output_fn=True,duration=1.0))')
pgt.add_plot('Face Preference',[('Strength','CiPreference')])
pgt.add_plot('Face Preference',[('Hue','CiPreference')])
pgt.add_plot('Face Selectivity',[('Strength','CiSelectivity')])
