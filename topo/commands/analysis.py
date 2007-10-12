"""
User-level analysis commands, typically for measuring or generating SheetViews.

$Id$
"""
__version__='$Revision$'


from numpy.oldnumeric import array, zeros, Float,size, shape
from math import pi
from copy import deepcopy

import topo
from topo.base.arrayutils import octave_output, centroid
from topo.base.cf import CFSheet, CFProjection, Projection
from topo.base.parameterizedobject import ParameterizedObject
from topo.base.parameterclasses import DynamicNumber,ListParameter, BooleanParameter
from topo.base.projection import ProjectionSheet
from topo.base.sheet import Sheet
from topo.base.sheetview import SheetView
from topo.commands.basic import pattern_present
from topo.misc.numbergenerators import UniformRandom
from topo.misc.utils import frange
from topo.base.arrayutils import wrap
from topo.patterns.basic import SineGrating, Gaussian
from topo.patterns.teststimuli import SineGratingDisk
from topo.sheets.generatorsheet import GeneratorSheet
from topo.base.parameterclasses import Parameter
from topo.analysis.featureresponses import ReverseCorrelation, FeatureMaps, FeatureCurves
from topo.plotting.plotgroup import create_plotgroup, plotgroups

from topo.patterns.random import GaussianRandom

class Feature(object):
    """
    Stores the parameters required for generating a map of one input feature.
    """

    def __init__(self, name, range=None, step=0.0, values=None, cyclic=False):
         """
         Users can provide either a range and a step size, or a list of values.
         If a list of values is supplied, the range can be omitted unless the
         default of the min and max in the list of values is not appropriate.
         """ 
         self.name=name
         self.step=step
         self.cyclic=cyclic
                     
         if range:  
             self.range=range
         elif values:
             self.range=(min(values),max(values))
         else:
             raise ValueError('The range or values must be specified')
             
         if values:  
             self.values=values
         else:
             low_bound,up_bound = self.range
             self.values=(frange(low_bound,up_bound,step,not cyclic))


class PatternPresenter(ParameterizedObject):
    """
    Function object for presenting PatternGenerator-created patterns.

    This class helps coordinate a set of patterns to be presented to a
    set of GeneratorSheets.  It provides a standardized way of
    generating a set of linked patterns for testing or analysis, such
    as when measuring preference maps or presenting test patterns.
    Subclasses can provide additional mechanisms for doing this in
    different ways.
    """
    contrast_parameter = Parameter('michelson_contrast')

    def __init__(self,pattern_generator,apply_output_fn=True,duration=1.0,**params):
        self.apply_output_fn=apply_output_fn
        self.duration=duration
        self.gen = pattern_generator
        self.contrast_parameter=params.get('contrast_parameter',self.contrast_parameter)

    def __call__(self,features_values,param_dict):
        
        for param,value in param_dict.iteritems():
           self.gen.__setattr__(param,value)
               
        for feature,value in features_values.iteritems():
           self.gen.__setattr__(feature,value)

        gen_list=topo.sim.objects(GeneratorSheet)
        input_sheet_names=gen_list.keys()
        # Copy the given generator once for every GeneratorSheet
        inputs = dict().fromkeys(gen_list)
        for k in inputs.keys():
            inputs[k]=deepcopy(self.gen)

        ### JABALERT: Should replace these special cases with general
        ### support for having meta-parameters controlling the
        ### generation of different patterns for each GeneratorSheet.
        ### For instance, we will also need to support xdisparity and
        ### ydisparity, plus movement of patterns between two eyes, colors,
        ### etc.  At the very least, it should be simple to control
        ### differences in single parameters easily.  In addition,
        ### these meta-parameters should show up as parameters for
        ### this object, augmenting the parameters for each individual
        ### pattern, e.g. in the Test Pattern window.  In this way we
        ### should be able to provide general support for manipulating
        ### both pattern parameters and parameters controlling
        ### interaction between or differences between patterns.

        if features_values.has_key("phasedisparity"):
            if len(input_sheet_names)!=2:
                self.warning('Disparity is defined only when there are exactly two patterns')
            else:
                temp_phase1=inputs[input_sheet_names[0]].phase - inputs[input_sheet_names[0]].phasedisparity/2.0
                temp_phase2=inputs[input_sheet_names[1]].phase + inputs[input_sheet_names[1]].phasedisparity/2.0
                inputs[input_sheet_names[0]].phase=wrap(0,2*pi,temp_phase1)
                inputs[input_sheet_names[1]].phase=wrap(0,2*pi,temp_phase2)

        ## Not yet used; example only
        #if features_values.has_key("xdisparity"):
        #    if len(input_sheet_names)!=2:
        #        self.warning('Disparity is defined only when there are exactly two patterns')
        #    else:
        #        inputs[input_sheet_names[0]].x=inputs[input_sheet_names[0]].x - inputs[input_sheet_names[0]].xdisparity/2.0
        #        inputs[input_sheet_names[1]].x=inputs[input_sheet_names[1]].x + inputs[input_sheet_names[1]].xdisparity/2.0
        #
        #        inputs={}
        #        inputs[input_sheet_names[0]]=inputs[input_sheet_names[0]]
        #        inputs[input_sheet_names[1]]=inputs[input_sheet_names[1]]
        #
        #if features_values.has_key("ydisparity"):
        #    if len(input_sheet_names)!=2:
        #        self.warning('Disparity is defined only when there are exactly two patterns')
        #    else:
        #        inputs[input_sheet_names[0]].y=inputs[input_sheet_names[0]].y - inputs[input_sheet_names[0]].ydisparity/2.0
        #        inputs[input_sheet_names[1]].y=inputs[input_sheet_names[1]].y + inputs[input_sheet_names[1]].ydisparity/2.0
        #
        #        inputs={}
        #        inputs[input_sheet_names[0]]=inputs[input_sheet_names[0]]
        #        inputs[input_sheet_names[1]]=inputs[input_sheet_names[1]]

        if features_values.has_key("ocular"):
            if len(input_sheet_names)!=2:
                self.warning('Ocularity is defined only when there are exactly two patterns')
            else:
                inputs[input_sheet_names[0]].scale=2*inputs[input_sheet_names[0]].ocular
                inputs[input_sheet_names[1]].scale=2.0-2*inputs[input_sheet_names[1]].ocular


        # For WhiskerArray only; used to set the delay/lag in each input sheet
        if features_values.has_key("deflection"):
            from __main__ import num_lags # Assumed to be defined in .ty file
            if num_lags==1:
                step_offset=1
            else:
                step_offset=0

            for i in xrange(num_lags):
                inputs[input_sheet_names[i]].step=i+step_offset


        if features_values.has_key("contrast") or param_dict.has_key("contrast"):
            if self.contrast_parameter=='michelson_contrast':
                for g in inputs.itervalues():
                    g.offset=0.5
                    g.scale=2*g.offset*g.contrast/100.0

            
	
            elif self.contrast_parameter=='weber_contrast':
                # Weber_contrast is currently only well defined for
                # the special case where the background offset is equal
                # to the target offset in the pattern type
                # SineGratingDisk
                for g in inputs.itervalues():
                    g.offset=0.5   #In this case this is the offset of both the background and the sine grating
                    g.scale=2*g.offset*g.contrast/100.0
            
                
            elif self.contrast_parameter=='scale':
                for g in inputs.itervalues():
                    g.offset=0.0
                    g.scale=g.contrast
            
            
        pattern_present(inputs, self.duration, learning=False,
                        apply_output_fn=self.apply_output_fn)



# JABALERT: Why does a Projection plot need a Sheet parameter?
def save_plotgroup(name,saver_params={},**params):
    """
    Convenience command for saving a set of plots to disk.  Examples:

      save_plotgroup("Activity")
      save_plotgroup("Orientation Preference")
      save_plotgroup("Projection",sheet=topo.sim['V1'],
                                  projection=topo.sim['V1'].projections('Afferent'))

    Some plotgroups accept optional parameters, which can be passed
    like sheet and projection above.

    (To pass an optional parameter to the PlotFileSaver itself, the
    saver_params dictionary can be used.)
    """
    plotgroup = plotgroups[name]
    if not plotgroup:
        raise ValueError("No plotgroup named %s in plotgroups repository."%name)

    saver_class = plotgroup.filesaver

    # save_plotgroup's **params are passed to the plotgroup
    params['name'] = name
    for param,val in params.items():
        setattr(plotgroup,param,val)

    saver = saver_class(plotgroup,**saver_params)
    saver.plotgroup.make_plots()
    saver.save_to_disk()



class Subplotting(ParameterizedObject):
    """
    Convenience functions for handling subplots (such as colorized Activity plots).
    Only needed for avoiding typing, as plots can be declared with their own
    specific subplots without using these functions.
    """
    
    plotgroups_to_subplot=ListParameter(default=
        ["Activity", "Connection Fields", "Projection", "Projection Activity"],
        doc="List of plotgroups for which to set subplots.")

    subplotting_declared = BooleanParameter(default=False,
        doc="Whether set_subplots has previously been called")
    
    @staticmethod    
    def set_subplots(prefix=None,hue="",confidence="",force=True):
        """
        Define Hue and Confidence subplots for each of the plotgroups_to_subplot.  
        Typically used to make activity or weight plots show a
        preference value as the hue, and a selectivity as the
        confidence.

        The specified hue, if any, should be the name of a SheetView,
        such as OrientationPreference.  The specified confidence, if
        any, should be the name of a (usually) different SheetView,
        such as OrientationSelectivity.

        The prefix option is a shortcut making the usual case easier
        to type; it sets hue to prefix+"Preference" and confidence to
        prefix+"Selectivity".

        If force=False, subplots are changed only if no subplot is
        currently defined.  Force=False is useful for setting up
        subplots automatically when maps are measured, without
        overwriting any subplots set up specifically by the user.

        Currently works only for plotgroups that have a plot
        with the same name as the plotgroup, though this could
        be changed easily.

        Examples::
        
           Subplotting.set_subplots("Orientation")
             - Set the default subplots to OrientationPreference and OrientationSelectivity

           Subplotting.set_subplots(hue="OrientationPreference")
             - Set the default hue subplot to OrientationPreference with no selectivity

           Subplotting.set_subplots()
             - Remove subplots from all the plotgroups_to_subplot.
        """
        
        if Subplotting.subplotting_declared and not force:
            return
        
        if prefix:
            hue=prefix+"Preference"
            confidence=prefix+"Selectivity"
        
        for name in Subplotting.plotgroups_to_subplot:
            if plotgroups.has_key(name):
                pg=plotgroups[name]
                if pg.plot_templates.has_key(name):
                    pt=pg.plot_templates[name]
                    pt["Hue"]=hue
                    pt["Confidence"]=confidence
                else:
                    Subplotting().warning("No template %s defined for plotgroup %s" % (name,name))
            else:
                Subplotting().warning("No plotgroup %s defined" % name)

        Subplotting.subplotting_declared=True



# Module variables for passing values to the commands.
coordinate = (0,0)
sheet_name = ''
proj_coords=[(0,0)]
proj_name =''

### JABALERT: This mechanism for passing values is a bit awkward, and
### should be changed to something cleaner.  It might also be better
### to access a Sheet instance directly, rather than searching by name.




# Most of the rest of this file consists of commands for creating
# SheetViews, paired with a template for how to construct plots from
# these SheetViews.
# 
# For instance, the implementation of Activity plots consists of an
# update_activity() plus the Activity PlotGroupTemplate.  The
# update_activity() command reads the activity array of each Sheet and
# makes a corresponding SheetView to put in the Sheet's
# sheet_view_dict, while the Activity PlotGroupTemplate specifies
# which SheetViews should be plotted in which combination.  See the
# help for PlotGroupTemplate for more information.


###############################################################################
###############################################################################


###############################################################################

pg = create_plotgroup(name='Activity',category='Basic',
             doc='Plot the activity for all Sheets.', auto_refresh=True,
             update_command='update_activity()', plot_immediately=True)
pg.add_plot('Activity',[('Strength','Activity')])



def update_activity():
    """
    Make a map of neural activity available for each sheet, for use in template-based plots.
    
    This command simply asks each sheet for a copy of its activity
    matrix, and then makes it available for plotting.  Of course, for
    some sheets providing this information may be non-trivial, e.g. if
    they need to average over recent spiking activity.
    """
    for sheet in topo.sim.objects(Sheet).values():
        activity_copy = array(sheet.activity)
        new_view = SheetView((activity_copy,sheet.bounds),
                              sheet.name,sheet.precedence,topo.sim.time())
        sheet.sheet_view_dict['Activity']=new_view
    

###############################################################################
from topo.plotting.plotgroup import ConnectionFieldsPlotGroup
pg= create_plotgroup(name='Connection Fields',category="Basic",
                     doc='Plot the weight strength in each ConnectionField of a specific unit of a Sheet.',
                     update_command='update_connectionfields()',
                     plot_immediately=True, normalize=True)
pg.add_plot('Connection Fields',[('Strength','Weights')])


def update_connectionfields():
    """
    Add SheetViews for the weights of one unit in a CFSheet, 
    for use in template-based plots.
    """
    sheets = topo.sim.objects(Sheet).values()
    x = coordinate[0]
    y = coordinate[1]
    for s in sheets:
	if (s.name == sheet_name and isinstance(s,CFSheet)):
	    s.update_unit_view(x,y)



## ###############################################################################
pg= create_plotgroup(name='Projection',category="Basic",
           doc='Plot the weights of an array of ConnectionFields in a Projection.',
           update_command='update_projections()',
           plot_immediately=True, normalize=True)
pg.add_plot('Projection',[('Strength','Weights')])


def update_projections():
    """
    Add SheetViews for the weights in one CFProjection,
    for use in template-based plots.
    """
    sheets = topo.sim.objects(Sheet).values()
    for s in sheets:
	if (s.name == sheet_name and isinstance(s,CFSheet)):
	    for x,y in proj_coords:
		s.update_unit_view(x,y,proj_name)


## ###############################################################################
pg =  create_plotgroup(name='Projection Activity',category="Basic",
             doc='Plot the activity in each Projection that connects to a Sheet.',
             update_command='update_projectionactivity()',
             plot_immediately=True, normalize=True,auto_refresh=True)
pg.add_plot('Projection Activity',[('Strength','ProjectionActivity')])


def update_projectionactivity():
    """
    Add SheetViews for all of the Projections of the ProjectionSheet
    specified by sheet_name, for use in template-based plots.
    """
    
    for s in topo.sim.objects(Sheet).values():
	if (s.name == sheet_name and isinstance(s,ProjectionSheet)):
            for p in s.in_connections:
                if not isinstance(p,Projection):
                    topo.sim.debug("Skipping non-Projection "+p.name)
                else:
                    v = p.get_projection_view(topo.sim.time())
                    key = ('ProjectionActivity',v.projection.dest.name,v.projection.name)
                    v.projection.dest.sheet_view_dict[key] = v



###############################################################################
###############################################################################


###############################################################################
pg= create_plotgroup(name='Position Preference',category="Preference Maps",
           doc='Measure preference for the X and Y position of a Gaussian.',
           update_command='measure_position_pref()',
           plot_command='topographic_grid()',
           normalize=True)

pg.add_plot('X Preference',[('Strength','XPreference')])
pg.add_plot('Y Preference',[('Strength','YPreference')])
pg.add_plot('Position Preference',[('Red','XPreference'),
                                    ('Green','YPreference')])

def measure_position_pref(divisions=6,size=0.5,scale=0.3,offset=0.0,display=False,
                          pattern_presenter=PatternPresenter(Gaussian(aspect_ratio=1.0),False,0.175),
                          x_range=(-0.5,0.5),y_range=(-0.5,0.5),weighted_average=True):
    """
    Measure position preference map, using a circular Gaussian by default.

    Measures maps by collating the responses to a set of input
    patterns controlled by some parameters.  The parameter ranges and
    number of input patterns in each range are determined by the
    divisions parameter.  The particular pattern used is determined by the
    size, scale, offset, and pattern_presenter arguments.
    """

    # JABALERT: Here and everywhere that follows there's really no
    # need for the else: clause; should simplify it by removing that.
    if divisions <= 0:
        raise ValueError("Divisions must be greater than 0")

    else:
        # JABALERT: Will probably need some work to support multiple input regions
        feature_values = [Feature(name="x",range=x_range,step=1.0*(x_range[1]-x_range[0])/divisions),
                          Feature(name="y",range=y_range,step=1.0*(y_range[1]-y_range[0])/divisions)]   
                          
                                      
                              
                          
        param_dict = {"size":size,"scale":scale,"offset":offset}
        x=FeatureMaps(feature_values)
        x.collect_feature_responses(pattern_presenter,param_dict,display,weighted_average)


###############################################################################
pg= create_plotgroup(name='Receptive Fields',category="Other",
           doc='Measure receptive fields.',
           update_command='measure_rfs(input_sheet=topo.sim["Retina"])',
           plot_command='plotrctg()',
           normalize=True)

# CEB: Could provide a default option for the input_sheet by making it
# accept input_sheet_name instead, defaulting to 'Retina'.  We would
# then look up the sheet with topo.sim[input_sheet_name].
def measure_rfs(input_sheet,divisions=10,scale=30.0,offset=0.5,display=False,
                pattern_presenter=PatternPresenter(Gaussian(aspect_ratio=1.0),True,duration=1.0),
                x_range=(-0.2,0.2),y_range=(-0.2,0.2)):
    """
    Map receptive fields by reverse correlation.

    Presents a large collection of input patterns, typically small
    Gaussians, keeping track of which units in the specified
    input_sheet were active when each unit in other Sheets in the
    simulation was active.  This data can then be used to plot
    receptive fields for each unit.  Note that the results are true
    receptive fields, not the connection fields usually presented in
    lieu of receptive fields, because they take all circuitry in
    between the input and the target unit into account.

    Note that it is crucial to set the scale parameter properly when
    using units with a hard activation threshold (as opposed to a
    smooth sigmoid), because the input pattern used here may not be a
    very effective way to drive the unit to activate.  The value
    should be set high enough that the target units activate at least
    some of the time there is a pattern on the input.
    """

    # CEBALERT: various things in here need to be arguments

    # Presents the pattern at each pixel location
    resolution = 100 # percentage, 100 is max, 0 is min
    l,b,r,t = input_sheet.nominal_bounds.lbrt()
    density=resolution*input_sheet.nominal_density/100.0
    divisions = density*(r-l)-1
    size = 1.0/(density)
    x_range=(r,l)
    y_range=(t,b)
    
    if divisions <= 0:
        raise ValueError("Divisions must be greater than 0")

    else:
        feature_values = [Feature(name="x",range=x_range,step=1.0*(x_range[1]-x_range[0])/divisions),
                          Feature(name="y",range=y_range,step=1.0*(y_range[1]-y_range[0])/divisions),
                          Feature(name="scale",range=(-scale,scale),step=scale*2)]   
                          
        param_dict = {"size":size,"scale":scale,"offset":offset}

        x=ReverseCorrelation(feature_values,input_sheet=input_sheet) #+change argument
        x.measure_responses(pattern_presenter,param_dict,feature_values,display)
     

###############################################################################
pg= create_plotgroup(name='Receptive Fields noise',category="Other",
           doc='Measure receptive fields by reverse correlation using random noise.',
           update_command='measure_rfs_noise(input_sheet=topo.sim["Retina"])',
           plot_command='plotrctg()',normalize=True)


### JABALERT: Why is the scale and offset set twice?                                    
def measure_rfs_noise(input_sheet,divisions=99,scale=0.5,offset=0.5,display=False,
                      pattern_presenter=PatternPresenter(GaussianRandom(scale=0.5,offset=0.5),True,duration=1.0),
                      x_range=(-1.0,1.0),y_range=(-1.0,1.0)):
    """Map receptive field on a GeneratorSheet using Gaussian noise inputs."""


    if divisions <= 0:
        raise ValueError("Divisions must be greater than 0")

    else:
        feature_values = [Feature(name="x",range=x_range,step=1.0*(x_range[1]-x_range[0])/divisions),
                          Feature(name="y",range=y_range,step=1.0*(y_range[1]-y_range[0])/divisions)]   
                          
        param_dict = {"scale":scale,"offset":offset}

        x=ReverseCorrelation(feature_values,input_sheet=input_sheet)
        x.measure_responses(pattern_presenter,param_dict,feature_values,display)





###############################################################################
pg= create_plotgroup(name='Center of Gravity',category="Preference Maps",
             doc='Measure the center of gravity of each ConnectionField in a Projection.',
             update_command='measure_cog(proj_name="Afferent")',
             plot_command='topographic_grid(xsheet_view_name="XCoG",ysheet_view_name="YCoG")',
             normalize=True)
pg.add_plot('X CoG',[('Strength','XCoG')])
pg.add_plot('Y CoG',[('Strength','YCoG')])
pg.add_plot('CoG',[('Red','XCoG'),('Green','YCoG')])



def measure_cog(proj_name ="Afferent"):    
    """
    Calculate center of gravity (CoG) for each CF of each unit in each CFSheet.

    Unlike measure_position_pref and other measure commands, this one
    does not work by collate the responses to a set of input patterns.
    Instead, the CoG is calculated directly from each set of afferent
    weights.  The CoG value thus is an indirect estimate of what
    patterns the neuron will prefer, but is not limited by the finite
    number of test patterns as the other measure commands are.

    At present, the name of the projection to use must be specified
    in the argument to this function, and a model using any other
    name must specify that explicitly when this function is called.
    """
    ### JABHACKALERT: Should be updated to support multiple projections
    ### to each sheet, not requiring the name to be specified.
    
    f = lambda x: hasattr(x,'measure_maps') and x.measure_maps
    measured_sheets = filter(f,topo.sim.objects(CFSheet).values())
    
    for sheet in measured_sheets:
	for proj in sheet.in_connections:
	    if proj.name == proj_name:
		rows,cols=sheet.activity.shape
		xpref=zeros((rows,cols),Float)
		ypref=zeros((rows,cols),Float)
		for r in xrange(rows):
		    for c in xrange(cols):
			cf=proj.cf(r,c)
			r1,r2,c1,c2 = cf.slice_array
			row_centroid,col_centroid = centroid(cf.weights)
			xcentroid, ycentroid = proj.src.matrix2sheet(
			        r1+row_centroid+0.5,
				c1+col_centroid+0.5)
                    
			xpref[r][c]= xcentroid
			ypref[r][c]= ycentroid
                    
			new_view = SheetView((xpref,sheet.bounds), sheet.name,sheet.precedence,topo.sim.time())
			sheet.sheet_view_dict['XCoG']=new_view
			new_view = SheetView((ypref,sheet.bounds), sheet.name,sheet.precedence,topo.sim.time())
			sheet.sheet_view_dict['YCoG']=new_view
           

###############################################################################
###############################################################################

###############################################################################
pg= create_plotgroup(name='Orientation Preference',category="Preference Maps",
             doc='Measure preference for sine grating orientation.',
             update_command='measure_or_pref()')
pg.add_plot('Orientation Preference',[('Hue','OrientationPreference')])
pg.add_plot('Orientation Preference&Selectivity',[('Hue','OrientationPreference'),
						   ('Confidence','OrientationSelectivity')])
pg.add_plot('Orientation Selectivity',[('Strength','OrientationSelectivity')])
pg.add_static_image('Color Key','topo/commands/or_key_white_vert_small.png')


def measure_or_pref(num_phase=18,num_orientation=4,frequencies=[2.4],
                    scale=0.3,offset=0.0,display=False,weighted_average=True,
                    pattern_presenter=PatternPresenter(pattern_generator=SineGrating(),apply_output_fn=False,duration=0.175)):
    """
    Measure orientation maps, using a sine grating by default.

    Measures maps by collating the responses to a set of input
    patterns controlled by some parameters.  The parameter ranges and
    number of input patterns in each range are determined by the
    num_phase, num_orientation, and frequencies parameters.  The
    particular pattern used is determined by the pattern_presenter
    argument, which defaults to a sine grating presented for a short
    duration.  By convention, most Topographica example files
    are designed to have a suitable activity pattern computed by
    that time, but the duration will need to be changed for other
    models that do not follow that convention.
    """
    # Could consider having scripts set a variable for the duration,
    # based on their own particular model setup, and to have it read
    # from here.  Instead, assumes a fixed default duration right now...

    if num_phase <= 0 or num_orientation <= 0:
        raise ValueError("num_phase and num_orientation must be greater than 0")

    else:
        step_phase=2*pi/num_phase
        step_orientation=pi/num_orientation

        feature_values = [Feature(name="frequency",values=frequencies),
                          Feature(name="orientation",range=(0.0,pi),step=step_orientation,cyclic=True),
                          Feature(name="phase",range=(0.0,2*pi),step=step_phase,cyclic=True)]

        param_dict = {"scale":scale,"offset":offset}
        x=FeatureMaps(feature_values)
        x.collect_feature_responses(pattern_presenter,param_dict,display,weighted_average)

    Subplotting.set_subplots("Orientation",force=False)

###############################################################################
pg= create_plotgroup(name='Ocular Preference',category="Preference Maps",
             doc='Measure preference for sine gratings between two eyes.',
             update_command='measure_od_pref()')
pg.add_plot('Ocular Preference',[('Strength','OcularPreference')])
pg.add_plot('Ocular Selectivity',[('Strength','OcularSelectivity')])



### JABALERT: Shouldn't there be a num_ocularities argument as well, to
### present various combinations of left and right eye activity?        
def measure_od_pref(num_phase=18,num_orientation=4,frequencies=[2.4],
                    scale=0.3,offset=0.0,display=False,weighted_average=True,
		    pattern_presenter=PatternPresenter(pattern_generator=SineGrating(),
                                                   apply_output_fn=False,duration=0.175)):
    """
    Measure ocular dominance maps, using a sine grating by default.

    Measures maps by collating the responses to a set of input
    patterns controlled by some parameters.  The parameter ranges and
    number of input patterns in each range are determined by the
    num_phase, num_orientation, and frequencies parameters.  The
    particular pattern used is determined by the pattern_presenter
    argument, which defaults to a sine grating presented for a short
    duration.  By convention, most Topographica example files
    are designed to have a suitable activity pattern computed by
    that time, but the duration will need to be changed for other
    models that do not follow that convention.
    """
    
    if num_phase <= 0 or num_orientation <= 0:
        raise ValueError("num_phase and num_orientation must be greater than 0")

    else:
        step_phase=2*pi/num_phase
        step_orientation=pi/num_orientation

        feature_values = [Feature(name="phase",range=(0.0,2*pi),step=step_phase,cyclic=True),
                          Feature(name="orientation",range=(0.0,pi),step=step_orientation,cyclic=True),
                          Feature(name="frequency",values=frequencies),
                          Feature(name="ocular",range=(0.0,1.0),values=[0.0,1.0])]  

        param_dict = {"scale":scale,"offset":offset}
        x=FeatureMaps(feature_values)
        x.collect_feature_responses(pattern_presenter,param_dict,display,weighted_average)
  

###############################################################################
pg= create_plotgroup(name='Spatial Frequency Preference',category="Preference Maps",
             doc='Measure preference for sine grating frequency.',
             update_command='measure_sf_pref(frequencies=frange(1.0,6.0,0.2),num_phase=15,num_orientation=4)')
pg.add_plot('Spatial Frequency Preference',[('Strength','FrequencyPreference')])
pg.add_plot('Spatial Frequency Selectivity',[('Strength','FrequencySelectivity')]) # confidence??


def measure_sf_pref(num_phase=18,num_orientation=4,frequencies=[2.4],
                    scale=0.3,offset=0.0,display=False,weighted_average=True,
                    pattern_presenter=PatternPresenter(pattern_generator=SineGrating(),apply_output_fn=False,duration=0.175)):

    """
    Measure spatial frequency maps, using a sine grating by default.

    Measures maps by collating the responses to a set of input
    patterns controlled by some parameters.  The parameter ranges and
    number of input patterns in each range are determined by the
    num_phase, num_orientation, and frequencies parameters.  The
    particular pattern used is determined by the pattern_presenter
    argument, which defaults to a sine grating presented for a short
    duration.  By convention, most Topographica example files
    are designed to have a suitable activity pattern computed by
    that time, but the duration will need to be changed for other
    models that do not follow that convention.
    """
    # Could consider having scripts set a variable for the duration,
    # based on their own particular model setup, and to have it read
    # from here.  Instead, assumes a fixed default duration right now...

    if num_phase <= 0 or num_orientation <= 0:
        raise ValueError("num_phase and num_orientation must be greater than 0")

    else:
        step_phase=2*pi/num_phase
        step_orientation=pi/num_orientation

        feature_values = [Feature(name="frequency",values=frequencies),
                          Feature(name="orientation",range=(0.0,pi),step=step_orientation,cyclic=True),
                          Feature(name="phase",range=(0.0,2*pi),step=step_phase,cyclic=True)]

        param_dict = {"scale":scale,"offset":offset}
        x=FeatureMaps(feature_values)
        x.collect_feature_responses(pattern_presenter,param_dict,display,weighted_average)

    Subplotting.set_subplots("Orientation",force=False)
    
###############################################################################
pg= create_plotgroup(name='PhaseDisparity Preference',category="Preference Maps",
             doc='Measure preference for sine gratings differing in phase between two sheets.',
             update_command='measure_phasedisparity()')
pg.add_plot('PhaseDisparity Preference',[('Hue','PhasedisparityPreference')])
pg.add_plot('PhaseDisparity Selectivity',[('Strength','PhasedisparitySelectivity')])
pg.add_static_image('Color Key','topo/commands/disp_key_white_vert_small.png')


def measure_phasedisparity(num_phase=12,num_orientation=4,num_disparity=12,frequencies=[2.4],
                           scale=0.3,offset=0.0,display=False,weighted_average=True,
                           pattern_presenter=PatternPresenter(pattern_generator=SineGrating(),
                                                              apply_output_fn=False,duration=0.175)):
    """
    Measure disparity maps, using sine gratings by default.

    Measures maps by collating the responses to a set of input
    patterns controlled by some parameters.  The parameter ranges and
    number of input patterns in each range are determined by the
    num_phase, num_orientation, num_disparity, and frequencies
    parameters.  The particular pattern used is determined by the

    pattern_presenter argument, which defaults to a sine grating presented
    for a short duration.  By convention, most Topographica example
    files are designed to have a suitable activity pattern computed by
    that time, but the duration will need to be changed for other
    models that do not follow that convention.
    """

    if num_phase <= 0 or num_orientation <= 0 or num_disparity <= 0:
        raise ValueError("num_phase, num_disparity and num_orientation must be greater than 0")

    else:
        step_phase=2*pi/num_phase
        step_orientation=pi/num_orientation
        step_disparity=2*pi/num_disparity

        feature_values = [Feature(name="phase",range=(0.0,2*pi),step=step_phase,cyclic=True),
                          Feature(name="orientation",range=(0.0,pi),step=step_orientation,cyclic=True),
                          Feature(name="frequency",values=frequencies),
                          Feature(name="phasedisparity",range=(0.0,2*pi),step=step_disparity,cyclic=True)]    

        param_dict = {"scale":scale,"offset":offset}
        x=FeatureMaps(feature_values)
        x.collect_feature_responses(pattern_presenter,param_dict,display,weighted_average)


###############################################################################
create_plotgroup(template_plot_type="curve",name='Orientation Tuning Fullfield',category="Tuning Curves",doc="""
            Plot orientation tuning curves for a specific unit, measured using full-field sine gratings.
            Although the data takes a long time to collect, once it is ready the plots
            are available immediately for any unit.""",
        update_command='measure_or_tuning_fullfield()',
        plot_command='or_tuning_curve(x_axis="orientation", plot_type=pylab.plot, unit="degrees")')


def measure_or_tuning_fullfield(num_phase=18,num_orientation=12,frequencies=[2.4],
                                curve_parameters=[{"contrast":30},{"contrast":60},{"contrast":80},{"contrast":90}],
                                display=False,
                                pattern_presenter=PatternPresenter(pattern_generator=SineGrating(),
                                                                   apply_output_fn=True,duration=1.0,
                                                                   contrast_parameter="michelson_contrast")):
    """
    Measures orientation tuning curve of a particular unit using a full field grating stimulus. 
    michelson_contrast can be replaced by another variable(s) eg. scale, weber_contrast or
    any other contrast definition, provided it is defined in PatternPresenter. 
    """

    sheets_to_measure=topo.sim.objects(CFSheet).values()

    for sheet in sheets_to_measure:
        if num_phase <= 0 or num_orientation <= 0:
            raise ValueError("num_phase and num_orientation must be greater than 0")
        
        else:
            step_phase=2*pi/num_phase
            step_orientation=pi/num_orientation
            
            feature_values = [Feature(name="phase",range=(0.0,2*pi),step=step_phase,cyclic=True),
                              Feature(name="orientation",range=(0,pi),step=step_orientation,cyclic=True),
                              Feature(name="frequency",values=frequencies)]     
            
            x_axis='orientation'
            x=FeatureCurves(feature_values,sheet,x_axis)
            
            for curve in curve_parameters:
                param_dict={}
                param_dict.update(curve)
                curve_label='Contrast = '+str(curve["contrast"])+'%'
                x.collect_feature_responses(feature_values,pattern_presenter,param_dict,curve_label,display)
	  

###############################################################################
create_plotgroup(template_plot_type="curve",name='Orientation Tuning',category="Tuning Curves",doc="""
            Measure orientation tuning for a specific unit at different contrasts,
            using a pattern chosen to match the preferences of that unit.""",
        update_command='measure_or_tuning()',
        plot_command='or_tuning_curve(x_axis="orientation",plot_type=pylab.plot,unit="degrees")',
        prerequisites=['XPreference'])


def measure_or_tuning(num_phase=18,num_orientation=12,frequencies=[2.4],
                      curve_parameters=[{"contrast":30},{"contrast":60},{"contrast":80}, {"contrast":90}],
                      display=False,size=0.5,
                      pattern_presenter=PatternPresenter(pattern_generator=SineGratingDisk(),
                                                         apply_output_fn=True,duration=1.0,
                                                         contrast_parameter="weber_contrast")):
    """
    Measures orientation tuning curve of a particular unit.
    Uses a circular sine grating patch as the stimulus on the retina. If the network contains an LGN layer
    then weber_contrast can be used as the contrast_parameter. If there is no LGN then scale (offset=0.0)
    can be used to define the contrast. Other relevant contrast definitions can also be used provided
    they are defined in PatternPresenter.(The curve_label should also be changed to reflect new units)
    """

    sheet=topo.sim[sheet_name]
    sheet_x,sheet_y = coordinate
    matrix_coords = sheet.sheet2matrixidx(sheet_x,sheet_y)
    if(('XPreference' in sheet.sheet_view_dict) and
       ('YPreference' in sheet.sheet_view_dict)):
	x_pref = sheet.sheet_view_dict['XPreference'].view()[0]
	y_pref = sheet.sheet_view_dict['YPreference'].view()[0]
	x_value=x_pref[matrix_coords]
	y_value=y_pref[matrix_coords]
    else:
        topo.sim.warning("Position Preference should be measured before plotting Orientation Tuning -- using default values for "+sheet_name)
        x_value=coordinate[0]
        y_value=coordinate[1]
      
	
                 
    if num_phase <= 0 or num_orientation <= 0:
        raise ValueError("num_phase and num_orientation must be greater than 0")
    
    else:
        step_orientation=pi/num_orientation
        step_phase=2*pi/num_phase
        
        feature_values = [Feature(name="phase",range=(0.0,2*pi),step=step_phase,cyclic=True),
                          Feature(name="orientation",range=(0,pi),step=step_orientation,cyclic=True),
                          Feature(name="frequency",values=frequencies)]     

        x_axis='orientation'
        x=FeatureCurves(feature_values,sheet,x_axis)
           
    
	for curve in curve_parameters:
            param_dict = {"x":x_value,"y":y_value}
            param_dict.update(curve)
	    curve_label='Contrast = '+str(curve["contrast"])+'%'
            x.collect_feature_responses(feature_values,pattern_presenter, param_dict,curve_label,display)
               

###############################################################################
create_plotgroup(template_plot_type="curve",name='Size Tuning',category="Tuning Curves",
        doc='Measure the size preference for a specific unit.',
        update_command='measure_size_response()',
        plot_command='tuning_curve(x_axis="size",plot_type=pylab.plot,unit="Diameter of stimulus")',
        prerequisites=['OrientationPreference','XPreference'])


def measure_size_response(num_phase=18,
                          curve_parameters=[{"contrast":30}, {"contrast":60},{"contrast":80},{"contrast":90}],
                          num_sizes=10,display=False,
                          pattern_presenter=PatternPresenter(pattern_generator=SineGratingDisk(),
                                                             apply_output_fn=True,duration=1.0,
                                                             contrast_parameter="weber_contrast")):
    """
    Measure receptive field size of one unit of a sheet.

    Uses an expanding circular sine grating stimulus at the preferred
    orientation and retinal position of the specified unit.
    Orientation and position preference must be calulated before
    measuring size response.

    The curve can be plotted at various different values of the
    contrast of the stimulus. If the network contains an LGN layer
    then weber_contrast can be used as the contrast_parameter.
    If there is no LGN then scale (offset=0.0) can be used to define
    the contrast. Other relevant contrast definitions can also be used
    provided they are defined in PatternPresenter.
    (The curve_label should also be changed to reflect new units)
    """
    
    sheet=topo.sim[sheet_name]

    matrix_coords = sheet.sheet2matrixidx(coordinate[0],coordinate[1])
    if('OrientationPreference' in sheet.sheet_view_dict):
        or_pref = sheet.sheet_view_dict['OrientationPreference'].view()[0]
        or_value = or_pref[matrix_coords]*pi # Orientations are stored as a normalized value beween 0 and 1.
                                             # The factor of pi is the norm_factor and is the range of orientation in measure_or_pref.
    else:
        topo.sim.warning("Orientation Preference should be measured before plotting Size Response -- using default values for "+sheet_name)
        or_value = 0.0

  

    if(('XPreference' in sheet.sheet_view_dict) and
       ('YPreference' in sheet.sheet_view_dict)):
        x_pref = sheet.sheet_view_dict['XPreference'].view()[0]
        y_pref = sheet.sheet_view_dict['YPreference'].view()[0]
        x_value=x_pref[matrix_coords]
        y_value=y_pref[matrix_coords]
    else:
        topo.sim.warning("Position Preference should be measured before plotting Size Response -- using default values for "+sheet_name)
        x_value=coordinate[0]
        y_value=coordinate[1]

  

    if num_phase <= 0:
        raise ValueError("num_phase must be greater than 0")

    else:
        step_phase=2*pi/num_phase
        step_size=1.0/num_sizes
        
        feature_values = [Feature(name="phase",range=(0.0,2*pi),step=step_phase,cyclic=True),
                          Feature(name="size",range=(0.1,1.0),step=step_size,cyclic=False)]

        x_axis='size'
        x=FeatureCurves(feature_values,sheet,x_axis)
          
        for curve in curve_parameters:
            param_dict = {"x":x_value,"y":y_value,"orientation":or_value}
            param_dict.update(curve)
	    curve_label='Contrast = '+str(curve["contrast"])+'%'
            x.collect_feature_responses(feature_values,pattern_presenter, param_dict,curve_label,display)


###############################################################################
create_plotgroup(template_plot_type="curve",name='Contrast Response',category="Tuning Curves",
        doc='Measure the contrast response function for a specific unit.',
        update_command='measure_contrast_response()',
        plot_command='tuning_curve(x_axis="contrast",plot_type=pylab.semilogx,unit="%")',
        prerequisites=['OrientationPreference','XPreference'])


def measure_contrast_response(contrasts=[10,20,30,40,50,60,70,80,90,100],relative_orientations=[0.0, pi/6, pi/4, pi/2],
                              size=0.5,display=False,frequency=2.4,
                              num_phase=18,pattern_presenter=PatternPresenter(pattern_generator=SineGratingDisk(),
                                                                              apply_output_fn=True,duration=1.0,
                                                                              contrast_parameter="weber_contrast")):
    """
    Measures contrast response curves for a particular unit.

    Uses a circular sine grating patch as the stimulus on the retina.
    If the network contains an LGN layer then weber_contrast can be
    used as the contrast_parameter. If there is no LGN then scale (offset=0.0)
    can be used to define the contrast. Other relevant contrast
    definitions can also be used provided they are defined in PatternPresenter
    (The curve_label should also be changed to reflect new units)

    The stimulus is presented at the preferred orientation and
    retinal position of the unit.Orientation preference and position
    preference must be measured before measuring the contrast response.
    """

    sheet=topo.sim[sheet_name]
    matrix_coords = sheet.sheet2matrixidx(coordinate[0],coordinate[1])

    if('OrientationPreference' in sheet.sheet_view_dict):
        or_pref = sheet.sheet_view_dict['OrientationPreference'].view()[0]
        or_value = or_pref[matrix_coords]*pi # Orientations are stored as a normalized value beween 0 and 1.
                                             # The factor of pi is the norm_factor and is the range of orientation in measure_or_pref.
    else:
        topo.sim.warning("Orientation Preference should be measured before plotting Contrast Response -- using default values for "+sheet_name)
        or_value = 0.0
   

    if(('XPreference' in sheet.sheet_view_dict) and
       ('YPreference' in sheet.sheet_view_dict)):
        x_pref = sheet.sheet_view_dict['XPreference'].view()[0]
        y_pref = sheet.sheet_view_dict['YPreference'].view()[0]
        x_value=x_pref[matrix_coords]
        y_value=y_pref[matrix_coords]
    else:
        topo.sim.warning("Position Preference should be measured before plotting Contrast Response -- using default values for "+sheet_name)
        x_value=coordinate[0]
        y_value=coordinate[1]
 
    curve_parameters=[{"orientation":or_value+ro} for ro in relative_orientations]
    
     
    if num_phase <= 0 :
        raise ValueError("num_phase must be greater than 0")

    else:
        step_phase=2*pi/num_phase
        
        feature_values = [Feature(name="phase",range=(0.0,2*pi),step=step_phase,cyclic=True),
                          Feature(name="contrast",values=contrasts,cyclic=False)]  
        x_axis='contrast'
        x=FeatureCurves(feature_values,sheet,x_axis)
   
	for curve in curve_parameters:
            param_dict = {"x":x_value,"y":y_value,"frequency":frequency, "size":size}
            param_dict.update(curve)
            curve_label='Orientation = %.4f rad' % curve["orientation"] 
	    x.collect_feature_responses(feature_values,pattern_presenter, param_dict, curve_label,display)

            

