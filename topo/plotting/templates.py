"""
PlotGroupTemplate class, and global repository of such objects.

These classes allow users to specify different types of plots in a way
that is independent of particular models or Sheets.

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


    ### JCALERT! We might eventually write these two functions
    ### 'Python-like' by using keyword argument to specify each
    ### channel and then get the dictionnary of all remaining
    ### arguments....
    def add_plot(self,name,specification_tuple_list):
	dict={}
	for key,value in specification_tuple_list:
	    dict[key]=value
	self.plot_templates.append((name,dict))

    def add_static_image(self,name,file_path):
        self.image_location = file_path
	self.static_images.append((name,self.image_location))
        



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
# We should also be able to store a documentation string describing each plot
# (for hovering help text) within each template.
# JC: we should also maybe add the situate option (and auto-refresh?)
### we might want to pass a plotgroup_type to the template
### (see corresponding alert in PlotGroupPanel)


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


pgt= new_pgt(name='Activity',category="Basic",
             doc='Plot the activity for all Sheets.',
             command='update_activity()', plot_immediately=True)
pgt.add_plot('Activity',[('Strength','Activity'),
                         ('Hue','OrientationPreference'),
                         ('Confidence','OrientationSelectivity')])

pgt= new_pgt(name='Connection Fields',category="Basic",
             doc='Plot the weight strength in each ConnectionField of a specific unit of a Sheet.',
             command='update_connectionfields()',
             plot_immediately=True, normalize=True)
pgt.add_plot('Connection Fields',[('Strength','Weights'),
                                  ('Hue','OrientationPreference'),
                                  ('Confidence','OrientationSelectivity')])

pgt= new_pgt(name='Projection',category="Basic",
             doc='Plot the weights of an array of ConnectionFields in a Projection.',
             command='update_projections()',
             plot_immediately=True, normalize=True)
pgt.add_plot('Projection',[('Strength','Weights'),
                           ('Hue','OrientationPreference'),
                           ('Confidence','OrientationSelectivity')])

pgt= new_pgt(name='Projection Activity',category="Basic",
             doc='Plot the activity in each Projection that connects to a Sheet.',
             command='update_projectionactivity()',
             plot_immediately=True, normalize=True)
pgt.add_plot('ProjectionActivity',[('Strength','ProjectionActivity')])



pgt= new_pgt(name='Position Preference',category="Preference Maps",
             doc='Measure preference for the X and Y position of a Gaussian.',
             command='measure_position_pref() ; topographic_grid()',
             normalize=True)

pgt.add_plot('X Preference',[('Strength','XPreference')])
pgt.add_plot('Y Preference',[('Strength','YPreference')])
pgt.add_plot('Position Preference',[('Red','XPreference'),
                                    ('Green','YPreference')])


pgt= new_pgt(name='Center of Gravity',category="Preference Maps",
             doc='Measure the center of gravity of each ConnectionField in a Projection.',
             command='measure_cog(proj_name="Afferent") ; topographic_grid(xsheet_view_name="XCoG",ysheet_view_name="YCoG")',
             normalize=True)
pgt.add_plot('X CoG',[('Strength','XCoG')])
pgt.add_plot('Y CoG',[('Strength','YCoG')])
pgt.add_plot('CoG',[('Red','XCoG'),('Green','YCoG')])



pgt= new_pgt(name='Orientation Preference',category="Preference Maps",
             doc='Measure preference for sine grating orientation.',
             command='measure_or_pref()')
pgt.add_plot('Orientation Preference',[('Hue','OrientationPreference')])
pgt.add_plot('Orientation Preference&Selectivity',[('Hue','OrientationPreference'),
						   ('Confidence','OrientationSelectivity')])
pgt.add_plot('Orientation Selectivity',[('Strength','OrientationSelectivity')])
pgt.add_static_image('Color Key','topo/commands/or_key_white_vert_small.png')


pgt= new_pgt(name='Ocular Preference',category="Preference Maps",
             doc='Measure preference for sine gratings between two eyes.',
             command='measure_od_pref()')
pgt.add_plot('Ocular Preference',[('Strength','OcularPreference')])
pgt.add_plot('Ocular Selectivity',[('Strength','OcularSelectivity')])


pgt= new_pgt(name='Spatial Frequency Preference',category="Preference Maps",
             doc='Measure preference for sine grating frequency.',
             command='measure_sf_pref(frequencies=frange(1.0,6.0,0.2),num_phase=15,num_orientation=4)')
pgt.add_plot('Spatial Frequency Preference',[('Strength','FrequencyPreference')])
pgt.add_plot('Spatial Frequency Selectivity',[('Strength','FrequencySelectivity')]) # confidence??


pgt= new_pgt(name='PhaseDisparity Preference',category="Preference Maps",
             doc='Measure preference for sine gratings differing in phase between two sheets.',
             command='measure_phasedisparity()')
pgt.add_plot('PhaseDisparity Preference',[('Hue','PhasedisparityPreference')])
pgt.add_plot('PhaseDisparity Selectivity',[('Strength','PhasedisparitySelectivity')])
pgt.add_static_image('Color Key','topo/commands/disp_key_white_vert_small.png')



new_pgt(name='Orientation Tuning Fullfield',category="Tuning Curves",doc="""
            Plot orientation tuning curves for a specific unit, measured using full-field sine gratings.
            Although the data takes a long time to collect, once it is ready the plots
            are available immediately for any unit.""",
        command='measure_or_tuning_fullfield()',
        plotcommand='or_tuning_curve(x_axis="orientation", plot_type=pylab.plot, unit="degrees")',
        template_plot_type="curve")

new_pgt(name='Orientation Tuning',category="Tuning Curves",
        doc='Measure orientation tuning for a specific unit, using an appropriate pattern for that unit.',
        command='measure_or_tuning(); or_tuning_curve(x_axis="orientation",plot_type=pylab.plot,unit="degrees")',
        template_plot_type="curve",
        prerequisites=['XPreference'])

new_pgt(name='Contrast Response',category="Tuning Curves",
        doc='Measure the contrast response function for a specific unit.',
        command='measure_contrast_response(); tuning_curve(x_axis="contrast",plot_type=pylab.semilogx,unit="%")',
        template_plot_type="curve",
        prerequisites=['OrientationPreference','XPreference'])

new_pgt(name='Size Tuning',category="Tuning Curves",
        doc='Measure the size preference for a specific unit.',
        command='measure_size_response(); tuning_curve(x_axis="size",plot_type=pylab.plot,unit="Diameter of stimulus")',
        template_plot_type="curve",
        prerequisites=['OrientationPreference','XPreference'])

