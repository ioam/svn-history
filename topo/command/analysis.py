"""
User-level analysis commands, typically for measuring or generating SheetViews.

Most of this file consists of commands for creating SheetViews, paired
with a template for how to construct plots from these SheetViews.

For instance, the implementation of Activity plots consists of the
update_activity() command plus the Activity PlotGroupTemplate.  The
update_activity() command reads the activity array of each Sheet and
makes a corresponding SheetView to put in the Sheet's sheet_views
dictionary, while the Activity PlotGroupTemplate specifies which
SheetViews should be plotted in which combination.  See the help for
PlotGroupTemplate for more information.

Some of the commands are ordinary Python functions, but the rest are
ParameterizedFunctions, which act like Python functions but support
Parameters with defaults, bounds, inheritance, etc.  These commands
are usually grouped together using inheritance so that they share a
set of parameters and some code, and only the bits that are specific
to that particular plot or analysis appear below.  See the
superclasses for the rest of the parameters and code.

$Id$
"""
__version__='$Revision$'


# JABALERT: Need to go through and eliminate unused imports.
from math import pi
import copy

from colorsys import hsv_to_rgb
from numpy.oldnumeric import array, zeros, Float,size, shape, maximum, add, ones

from .. import param
from ..param.parameterized import PicklableClassAttributes, ParameterizedFunction
from ..param.parameterized import ParamOverrides

import topo
from topo.base.arrayutil import octave_output, centroid, wrap
from topo.base.cf import CFSheet, CFProjection, Projection
from topo.base.projection import ProjectionSheet
from topo.base.simulation import EPConnectionEvent
from topo.base.sheet import Sheet
from topo.base.sheetview import SheetView
from topo.command.basic import pattern_present, wipe_out_activity
from topo.misc.numbergenerator import UniformRandom
from topo.misc.util import frange
from topo.misc.distribution import Distribution
from topo.pattern.basic import SineGrating, Gaussian, Rectangle
from topo.pattern.teststimuli import SineGratingDisk, OrientationContrastPattern, SineGratingRectangle
from topo.pattern.random import GaussianRandom
from topo.sheet.generator import GeneratorSheet
from topo.analysis.featureresponses import ReverseCorrelation, FeatureMaps, FeatureCurves
from topo.plotting.plotgroup import create_plotgroup, plotgroups, ConnectionFieldsPlotGroup


from topo.plotting.plotgroup import UnitMeasurementCommand,ProjectionSheetMeasurementCommand,default_input_sheet
from topo.analysis.featureresponses import Feature, PatternPresenter, Subplotting
from topo.analysis.featureresponses import SinusoidalMeasureResponseCommand, PositionMeasurementCommand, SingleInputResponseCommand, FeatureCurveCommand, UnitCurveCommand


class save_plotgroup(ParameterizedFunction):
    """
    Convenience command for saving a set of plots to disk.  Examples:

      save_plotgroup("Activity")
      save_plotgroup("Orientation Preference")
      save_plotgroup("Projection",projection=topo.sim['V1'].projections('Afferent'))
                                  
    Some plotgroups accept optional parameters, which can be passed
    like projection above.

    (To pass an optional parameter to the PlotFileSaver itself, the
    saver_params dictionary can be used.)
    """

    # Class variables to cache values from previous invocations
    previous_times=[-1]
    previous_commands=[]

    # The use_cached_results option is experimental, and is not
    # typically safe to use (as commands can have different results
    # depending on changes in class defaults, even if the command
    # string is identical).
    def __call__(self,name,saver_params={},use_cached_results=False,**params):
        p=ParamOverrides(self,params,allow_extra_keywords=True)

        plotgroup = copy.deepcopy(plotgroups[name])
    
        # JABALERT: Why does a Projection plot need a Sheet parameter?
        # CB: It shouldn't, of course, since we know the sheet when we have
        # the projection object - it's just leftover from when we passed the
        # names instead. There should be an ALERT already about this somewhere
        # in projectionpanel.py or plotgroup.py (both need to be changed).
        if 'projection' in params:
            params['sheet'] = params['projection'].dest
    
        plotgroup._set_name(name)
        # save_plotgroup's **params are passed to the plotgroup
        for param,val in params.items():
            setattr(plotgroup,param,val)

        # Cache commands to ensure that each is run only once per simulation time
        if (topo.sim.time() != self.previous_times[0]):
            del self.previous_commands[:]
            del self.previous_times[:]
            self.previous_times.append(topo.sim.time())

        if use_cached_results and plotgroup.update_command in self.previous_commands:
            update=False
        else:
            update=True
            self.previous_commands.append(plotgroup.update_command)

        #print "Plotting %s (with update==%s)" % (plotgroup.name,update)
        plotgroup.make_plots(update=update)
        plotgroup.filesaver.save_to_disk(**saver_params)



def decode_feature(sheet, preference_map = "OrientationPreference", axis_bounds=(0.0,1.0), cyclic=True, weighted_average=True):
    """
    Estimate the value of a feature from the current activity pattern on a sheet.
    
    The specified preference_map should be measured before this
    function is called.
    
    If weighted_average is False, the feature value returned is the
    value of the preference_map at the maximally active location.
    
    If weighted_average is True, the feature value is estimated by
    weighting the preference_map by the current activity level, and
    averaging the result across all units in the sheet.  The
    axis_bounds specify the allowable range of the feature values in
    the preference_map.  If cyclic is true, a vector average is used;
    otherwise an arithmetic weighted average is used.
    
    For instance, if preference_map is OrientationPreference (a cyclic
    quantity), then the result will be the vector average of the
    activated orientations.  For an orientation map this value should
    be an estimate of the orientation present on the input.
    """
    d = Distribution(axis_bounds, cyclic)
    
    if not (preference_map in sheet.sheet_views):
        topo.sim.warning(preference_map + " should be measured before calling decode_orientations.")
    else:
        map = sheet.sheet_views[preference_map]
        d.add(dict(zip(map.view()[0].ravel(), sheet.activity.ravel())))
    
    if weighted_average:
        return d.weighted_average()
    else:
        return d.max_value_bin()



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
        sheet.sheet_views['Activity']=new_view


pg = create_plotgroup(name='Activity',category='Basic',
             doc='Plot the activity for all Sheets.', auto_refresh=True,
             update_command=update_activity, plot_immediately=True)
pg.add_plot('Activity',[('Strength','Activity')])



class update_connectionfields(UnitMeasurementCommand):
    """A callable Parameterized command for measuring or plotting a unit from a Projection."""

    # Force plotting of all CFs, not just one Projection
    projection = param.ObjectSelector(default=None,constant=True)


pg= create_plotgroup(name='Connection Fields',category="Basic",
                     doc='Plot the weight strength in each ConnectionField of a specific unit of a Sheet.',
                     update_command=update_connectionfields,
                     plot_immediately=True, normalize=True, situate=True)
pg.add_plot('Connection Fields',[('Strength','Weights')])



class update_projection(UnitMeasurementCommand):
    """A callable Parameterized command for measuring or plotting units from a Projection."""


pg= create_plotgroup(name='Projection',category="Basic",
           doc='Plot the weights of an array of ConnectionFields in a Projection.',
           update_command=update_projection,
           plot_immediately=False, normalize=True,sheet_coords=True)
pg.add_plot('Projection',[('Strength','Weights')])



class update_projectionactivity(ProjectionSheetMeasurementCommand):
    """
    Add SheetViews for all of the Projections of the ProjectionSheet
    specified by the sheet parameter, for use in template-based plots.
    """
    
    def __call__(self,**params):
        p=ParamOverrides(self,params)
        self.params('sheet').compute_default()        
        s = p.sheet
        if s is not None:
            for p in s.in_connections:
                if not isinstance(p,Projection):
                    topo.sim.debug("Skipping non-Projection "+p.name)
                else:
                    v = p.get_projection_view(topo.sim.time())
                    key = ('ProjectionActivity',v.projection.dest.name,v.projection.name)
                    v.projection.dest.sheet_views[key] = v


pg =  create_plotgroup(name='Projection Activity',category="Basic",
             doc='Plot the activity in each Projection that connects to a Sheet.',
             update_command=update_projectionactivity,
             plot_immediately=True, normalize=True,auto_refresh=True)
pg.add_plot('Projection Activity',[('Strength','ProjectionActivity')])




class measure_position_pref(PositionMeasurementCommand):
    """Measure a position preference map by collating the response to patterns."""
    
    scale = param.Number(default=0.3)

    def _feature_list(self,p):
        width =1.0*p.x_range[1]-p.x_range[0]
        height=1.0*p.y_range[1]-p.y_range[0]
        return [Feature(name="x",range=p.x_range,step=width/p.divisions),
                Feature(name="y",range=p.y_range,step=height/p.divisions)]


pg= create_plotgroup(name='Position Preference',category="Preference Maps",
           doc='Measure preference for the X and Y position of a Gaussian.',
           update_command=measure_position_pref,
           plot_command='topographic_grid()',
           normalize=True)

pg.add_plot('X Preference',[('Strength','XPreference')])
pg.add_plot('Y Preference',[('Strength','YPreference')])
pg.add_plot('Position Preference',[('Red','XPreference'),
                                   ('Green','YPreference')])



class measure_rfs(SingleInputResponseCommand):
    """
    Map receptive fields by reverse correlation.

    Presents a large collection of input patterns, typically pixel
    by pixel on and off, keeping track of which units in the specified
    input_sheet were active when each unit in other Sheets in the
    simulation was active.  This data can then be used to plot
    receptive fields for each unit.  Note that the results are true
    receptive fields, not the connection fields usually presented in
    lieu of receptive fields, because they take all circuitry in
    between the input and the target unit into account.

    Note also that it is crucial to set the scale parameter properly when
    using units with a hard activation threshold (as opposed to a
    smooth sigmoid), because the input pattern used here may not be a
    very effective way to drive the unit to activate.  The value
    should be set high enough that the target units activate at least
    some of the time there is a pattern on the input.
    """
    
    static_parameters = param.List(default=["offset","size"])

    __abstract = True


    def __call__(self,**params):
        p=ParamOverrides(self,params)
        self.params('input_sheet').compute_default()
        x=ReverseCorrelation(self._feature_list(p),input_sheet=p.input_sheet) #+change argument
        static_params = dict([(s,p[s]) for s in p.static_parameters])
        if p.duration is not None:
            p.pattern_presenter.duration=p.duration
        if p.apply_output_fn is not None:
            p.pattern_presenter.apply_output_fn=p.apply_output_fn
        x.collect_feature_responses(p.pattern_presenter,static_params,p.display,self._feature_list(p))


    def _feature_list(self,p):
        # Present the pattern at each pixel location by default
        l,b,r,t = p.input_sheet.nominal_bounds.lbrt()
        density=p.input_sheet.nominal_density*1.0 # Should make into a parameter
        divisions = density*(r-l)-1
        size = 1.0/density
        x_range=(r-size/2,l)
        y_range=(t-size,b)
        p['size']=size

        return [Feature(name="x",range=x_range,step=1.0*(x_range[1]-x_range[0])/divisions),
                Feature(name="y",range=y_range,step=1.0*(y_range[1]-y_range[0])/divisions),
                Feature(name="scale",range=(-p.scale,p.scale),step=p.scale*2)]


pg= create_plotgroup(name='RF Projection',category="Other",
    doc='Measure receptive fields.',
    update_command=measure_rfs,
    plot_command='',
    normalize=True)
pg.add_plot('RFs',[('Strength','RFs')])



###############################################################################
# Disabled until investigated further
#class measure_rfs_noise(SingleInputResponseCommand):
#    """Map receptive field on a GeneratorSheet using Gaussian noise inputs."""
#
#    pattern_presenter = param.Callable(
#        default=PatternPresenter(GaussianRandom()))
#
#    scale = param.Number(default=0.5)
#
#    static_parameters = param.List(default=["scale","offset"])
#
#    def __call__(self,**params):
#        p=ParamOverrides(self,params)
#        self.params('input_sheet').compute_default()
#
#        ### JABALERT: What was this function supposed to do?  It steps
#        ### through a range of x and y, yet a GaussianRandom pattern
#        ### ignores x and y, so all it really seems to be doing is
#        ### ending up with about 10000 noise patterns.  Surely there
#        ### is a better way to do that?  For now, divisions, xrange,
#        ### and y_range are no longer parameters, because they are
#        ### nonsensical, but a proper parameter (e.g. number of random
#        ### presentations) should be added and these removed.
#        ### Alternatively, maybe it was supposed to be a GaussianCloud
#        ### pattern, in which case these should be made into
#        ### Parameters (or calculated like in measure_rfs).
#        divisions=99
#        x_range=(-1.0,1.0)
#        y_range=(-1.0,1.0)
#
#        feature_values = [Feature(name="x",range=x_range,step=1.0*(x_range[1]-x_range[0])/divisions),
#                          Feature(name="y",range=y_range,step=1.0*(y_range[1]-y_range[0])/divisions)]   
#                          
#        static_params = dict([(s,p[s]) for s in p.static_parameters])        
#        if p.duration is not None:
#            p.pattern_presenter.duration=p.duration
#        if p.apply_output_fn is not None:
#            p.pattern_presenter.apply_output_fn=p.apply_output_fn
#        x=ReverseCorrelation(feature_values,input_sheet=p.input_sheet)
#        x.collect_feature_responses(p.pattern_presenter,static_params,p.display,feature_values)
#
#
#pg= create_plotgroup(name='RF Projection (noise)',category="Other",
#           doc='Measure receptive fields by reverse correlation using random noise.',
#           update_command=measure_rfs_noise,
#           plot_command='',normalize=True)
#pg.add_plot('RFs',[('Strength','RFs')])



class measure_cog(ParameterizedFunction):
    """
    Calculate center of gravity (CoG) for each CF of each unit in each CFSheet.

    Unlike measure_position_pref and other measure commands, this one
    does not work by collating the responses to a set of input patterns.
    Instead, the CoG is calculated directly from each set of incoming
    weights.  The CoG value thus is an indirect estimate of what
    patterns the neuron will prefer, but is not limited by the finite
    number of test patterns as the other measure commands are.

    Measures only one projection for each sheet, as specified by the
    proj_name parameter.  The default proj_name of '' selects the
    first non-self connection, which is usually useful to examine for
    simple feedforward networks, but will not necessarily be useful in
    other cases.
    """
      
    proj_name = param.String(default='',doc="""
        Name of the projection to measure; the empty string means 'the first
        non-self connection available'.""")

    def __call__(self,**params):
        p=ParamOverrides(self,params)
        
        measured_sheets = [s for s in topo.sim.objects(CFSheet).values()
                           if hasattr(s,'measure_maps') and s.measure_maps]

        # Could easily be extended to measure CoG of all projections
        # and e.g. register them using different names (e.g. "Afferent
        # XCoG"), but then it's not clear how the PlotGroup would be
        # able to find them automatically (as it currently supports
        # only a fixed-named plot).
        requested_proj=p.proj_name
        for sheet in measured_sheets:
            for proj in sheet.in_connections:
                if (proj.name == requested_proj) or \
                   (requested_proj == '' and (proj.src != sheet)):
                    self._update_proj_cog(proj)
                    if requested_proj=='':
                        print "measure_cog: Measured %s projection %s from %s" % \
                              (proj.dest.name,proj.name,proj.src.name)
                        break


    def _update_proj_cog(self,proj):
        """Measure the CoG of the specified projection and register corresponding SheetViews."""
        
        sheet=proj.dest
        rows,cols=sheet.activity.shape
        xpref=zeros((rows,cols),Float)
        ypref=zeros((rows,cols),Float)
        
        for r in xrange(rows):
            for c in xrange(cols):
                cf=proj.cfs[r,c]
                r1,r2,c1,c2 = cf.input_sheet_slice
                row_centroid,col_centroid = centroid(cf.weights)
                xcentroid, ycentroid = proj.src.matrix2sheet(
                        r1+row_centroid+0.5,
                        c1+col_centroid+0.5)
            
                xpref[r][c]= xcentroid
                ypref[r][c]= ycentroid
            
                sheet.sheet_views['XCoG']=SheetView((xpref,sheet.bounds), sheet.name,
                                                    sheet.precedence,topo.sim.time())
                
                sheet.sheet_views['YCoG']=SheetView((ypref,sheet.bounds), sheet.name,
                                                    sheet.precedence,topo.sim.time())


pg= create_plotgroup(name='Center of Gravity',category="Preference Maps",
             doc='Measure the center of gravity of each ConnectionField in a Projection.',
             update_command=measure_cog,
             plot_command='topographic_grid(xsheet_view_name="XCoG",ysheet_view_name="YCoG")',
             normalize=True)
pg.add_plot('X CoG',[('Strength','XCoG')])
pg.add_plot('Y CoG',[('Strength','YCoG')])
pg.add_plot('CoG',[('Red','XCoG'),('Green','YCoG')])



class measure_sine_pref(SinusoidalMeasureResponseCommand):
    """
    Measure preferences for sine gratings in various combinations.
    Can measure orientation, spatial frequency, spatial phase,
    ocular dominance, and horizontal phase disparity.
    """

    num_ocularity = param.Integer(default=1,bounds=(1,None),softbounds=(1,3),doc="""
        Number of ocularity values to test; set to 1 to disable or 2 to enable.""")

    num_disparity = param.Integer(default=1,bounds=(1,None),softbounds=(1,48),doc="""
        Number of disparity values to test; set to 1 to disable or e.g. 12 to enable.""")

    num_hue = param.Integer(default=1,bounds=(1,None),softbounds=(1,48),doc="""
        Number of hues to test; set to 1 to disable or e.g. 8 to enable.""")

    subplot = param.String("Orientation")
    
    def _feature_list(self,p):
        features = \
            [Feature(name="frequency",values=p.frequencies),
             Feature(name="orientation",range=(0.0,pi),step=pi/p.num_orientation,cyclic=True),
             Feature(name="phase",range=(0.0,2*pi),step=2*pi/p.num_phase,cyclic=True)]

        if p.num_ocularity>1: features += \
            [Feature(name="ocular",range=(0.0,1.0),step=1.0/p.num_ocularity)]

        if p.num_disparity>1: features += \
            [Feature(name="phasedisparity",range=(0.0,2*pi),step=2*pi/p.num_disparity,cyclic=True)]

        if p.num_hue>1: features += \
            [Feature(name="hue",range=(0.0,1.0),step=1.0/p.num_hue,cyclic=True)]
            
        return features


class measure_or_pref(SinusoidalMeasureResponseCommand):
    """Measure an orientation preference map by collating the response to patterns."""

    subplot = param.String("Orientation")
    
    def _feature_list(self,p):
        return [Feature(name="frequency",values=p.frequencies),
                Feature(name="orientation",range=(0.0,pi),step=pi/p.num_orientation,cyclic=True),
                Feature(name="phase",range=(0.0,2*pi),step=2*pi/p.num_phase,cyclic=True)]


pg= create_plotgroup(name='Orientation Preference',category="Preference Maps",
             doc='Measure preference for sine grating orientation.',
             update_command=measure_sine_pref)
pg.add_plot('Orientation Preference',[('Hue','OrientationPreference')])
pg.add_plot('Orientation Preference&Selectivity',[('Hue','OrientationPreference'),
						   ('Confidence','OrientationSelectivity')])
pg.add_plot('Orientation Selectivity',[('Strength','OrientationSelectivity')])
pg.add_plot('Phase Preference',[('Hue','PhasePreference')])
pg.add_plot('Phase Selectivity',[('Strength','PhaseSelectivity')])
pg.add_static_image('Color Key','topo/command/or_key_white_vert_small.png')


pg= create_plotgroup(name='Spatial Frequency Preference',category="Preference Maps",
             doc='Measure preference for sine grating orientation and frequency.',
             update_command=measure_sine_pref)
pg.add_plot('Spatial Frequency Preference',[('Strength','FrequencyPreference')])
pg.add_plot('Spatial Frequency Selectivity',[('Strength','FrequencySelectivity')])
# Just calls measure_sine_pref to plot different maps.



class measure_od_pref(SinusoidalMeasureResponseCommand):
    """Measure an ocular dominance preference map by collating the response to patterns."""

    ### JABALERT: Shouldn't there be a num_ocularities parameter as
    ### well, to present various combinations of left and right eye
    ### activity?  And shouldn't this just be combined with
    ### measure_or_pref, using num_ocularities=1 by default?
    
    def _feature_list(self,p):
        return [Feature(name="frequency",values=p.frequencies),
                Feature(name="orientation",range=(0.0,pi),step=pi/p.num_orientation,cyclic=True),
                Feature(name="phase",range=(0.0,2*pi),step=2*pi/p.num_phase,cyclic=True),
                Feature(name="ocular",range=(0.0,1.0),values=[0.0,1.0])]
  

pg= create_plotgroup(name='Ocular Preference',category="Preference Maps",
             doc='Measure preference for sine gratings between two eyes.',
             update_command=measure_sine_pref)
pg.add_plot('Ocular Preference',[('Strength','OcularPreference')])
pg.add_plot('Ocular Selectivity',[('Strength','OcularSelectivity')])



class measure_phasedisparity(SinusoidalMeasureResponseCommand):
    """Measure a phase disparity preference map by collating the response to patterns."""

    ### JABALERT: Shouldn't this just be combined with measure_or_pref
    ### and measure_od_pref, using num_disparity=1 by default?

    num_disparity = param.Integer(default=12,bounds=(1,None),softbounds=(1,48),
                                  doc="Number of disparity values to test.")

    def _feature_list(self,p):
        return [Feature(name="frequency",values=p.frequencies),
                Feature(name="orientation",range=(0.0,pi),step=pi/p.num_orientation,cyclic=True),
                Feature(name="phase",range=(0.0,2*pi),step=2*pi/p.num_phase,cyclic=True),
                Feature(name="ocular",range=(0.0,1.0),values=[0.0,1.0]),
                Feature(name="phasedisparity",range=(0.0,2*pi),step=2*pi/p.num_disparity,cyclic=True)]


pg= create_plotgroup(name='PhaseDisparity Preference',category="Preference Maps",
             doc='Measure preference for sine gratings differing in phase between two sheets.',
             update_command=measure_sine_pref,normalize=True)
pg.add_plot('PhaseDisparity Preference',[('Hue','PhasedisparityPreference')])
pg.add_plot('PhaseDisparity Selectivity',[('Strength','PhasedisparitySelectivity')])
pg.add_static_image('Color Key','topo/command/disp_key_white_vert_small.png')



class measure_or_tuning_fullfield(FeatureCurveCommand):
    """
    Measures orientation tuning curve(s) of a particular unit using a
    full-field sine grating stimulus.  

    The curve can be plotted at various different values of the
    contrast (or actually any other parameter) of the stimulus.  If
    using contrast and the network contains an LGN layer, then one
    would usually specify michelson_contrast as the
    contrast_parameter. If there is no explicit LGN, then scale
    (offset=0.0) can be used to define the contrast.  Other relevant
    contrast definitions (or other parameters) can also be used,
    provided they are defined in PatternPresenter and the units
    parameter is changed as appropriate.
    """

    pattern_presenter = param.Callable(
        default=PatternPresenter(pattern_generator=SineGrating(),
                                 contrast_parameter="michelson_contrast"))


create_plotgroup(template_plot_type="curve",name='Orientation Tuning Fullfield',category="Tuning Curves",doc="""
            Plot orientation tuning curves for a specific unit, measured using full-field sine gratings.
            Although the data takes a long time to collect, once it is ready the plots
            are available immediately for any unit.""",
        update_command=measure_or_tuning_fullfield,
        plot_command='cyclic_tuning_curve(x_axis="orientation")')



class measure_or_tuning(UnitCurveCommand):
    """
    Measures orientation tuning curve(s) of a particular unit.

    Uses a circular sine grating patch as the stimulus on the
    retina. 

    The curve can be plotted at various different values of the
    contrast (or actually any other parameter) of the stimulus.  If
    using contrast and the network contains an LGN layer, then one
    would usually specify weber_contrast as the contrast_parameter. If
    there is no explicit LGN, then scale (offset=0.0) can be used to
    define the contrast.  Other relevant contrast definitions (or
    other parameters) can also be used, provided they are defined in
    PatternPresenter and the units parameter is changed as
    appropriate.
    """

    num_orientation = param.Integer(default=12)

    static_parameters = param.List(default=["size","x","y"])

    def __call__(self,**params):
        p=ParamOverrides(self,params)
        self.params('sheet').compute_default()
        sheet=p.sheet
        
        for coord in p.coords:
            self.x=self._sheetview_unit(sheet,coord,'XPreference',default=coord[0])
            self.y=self._sheetview_unit(sheet,coord,'YPreference',default=coord[1])
            self._compute_curves(p,sheet)
               

create_plotgroup(template_plot_type="curve",name='Orientation Tuning',category="Tuning Curves",doc="""
            Measure orientation tuning for a specific unit at different contrasts,
            using a pattern chosen to match the preferences of that unit.""",
        update_command=measure_or_tuning,
        plot_command='cyclic_tuning_curve(x_axis="orientation")',
        prerequisites=['XPreference'])



# JABALERT: Is there some reason not to call it measure_size_tuning?
class measure_size_response(UnitCurveCommand):
    """
    Measure receptive field size of one unit of a sheet.

    Uses an expanding circular sine grating stimulus at the preferred
    orientation and retinal position of the specified unit.
    Orientation and position preference must be calulated before
    measuring size response.

    The curve can be plotted at various different values of the
    contrast (or actually any other parameter) of the stimulus.  If
    using contrast and the network contains an LGN layer, then one
    would usually specify weber_contrast as the contrast_parameter. If
    there is no explicit LGN, then scale (offset=0.0) can be used to
    define the contrast.  Other relevant contrast definitions (or
    other parameters) can also be used, provided they are defined in
    PatternPresenter and the units parameter is changed as
    appropriate.
    """
    size=None # Disabled unused parameter

    static_parameters = param.List(default=["orientation","x","y"])

    num_sizes = param.Integer(default=10,bounds=(1,None),softbounds=(1,50),
                              doc="Number of different sizes to test.")

    x_axis = param.String(default='size',constant=True)


    def __call__(self,**params):
        p=ParamOverrides(self,params)
        self.params('sheet').compute_default()
        sheet=p.sheet

        for coord in p.coords:
            # Orientations are stored as a normalized value beween 0
            # and 1, so we scale them by pi to get the true orientations.
            self.orientation=pi*self._sheetview_unit(sheet,coord,'OrientationPreference')
            self.x=self._sheetview_unit(sheet,coord,'XPreference',default=coord[0])
            self.y=self._sheetview_unit(sheet,coord,'YPreference',default=coord[1])
            self._compute_curves(p,sheet)


    # Why not vary frequency too?  Usually it's just one number, but it could be otherwise.
    def _feature_list(self,p):
        return [Feature(name="phase",range=(0.0,2*pi),step=2*pi/p.num_phase,cyclic=True),
               #Feature(name="frequency",values=p.frequencies),
                Feature(name="size",range=(0.1,1.0),step=1.0/p.num_sizes,cyclic=False)]


create_plotgroup(template_plot_type="curve",name='Size Tuning',category="Tuning Curves",
        doc='Measure the size preference for a specific unit.',
        update_command=measure_size_response,
        plot_command='tuning_curve(x_axis="size",unit="Diameter of stimulus")',
        prerequisites=['OrientationPreference','XPreference'])



class measure_contrast_response(UnitCurveCommand):
    """
    Measures contrast response curves for a particular unit.

    Uses a circular sine grating stimulus at the preferred
    orientation and retinal position of the specified unit.
    Orientation and position preference must be calulated before
    measuring contrast response.

    The curve can be plotted at various different values of the
    contrast (or actually any other parameter) of the stimulus.  If
    using contrast and the network contains an LGN layer, then one
    would usually specify weber_contrast as the contrast_parameter. If
    there is no explicit LGN, then scale (offset=0.0) can be used to
    define the contrast.  Other relevant contrast definitions (or
    other parameters) can also be used, provided they are defined in
    PatternPresenter and the units parameter is changed as
    appropriate.
    """

    static_parameters = param.List(default=["size","x","y"])

    contrasts = param.List(class_=int,default=[10,20,30,40,50,60,70,80,90,100])

    relative_orientations = param.List(class_=float,default=[0.0, pi/6, pi/4, pi/2])
    
    x_axis = param.String(default='contrast',constant=True)

    units = param.String(default=" rad")

    def __call__(self,**params):
        p=ParamOverrides(self,params)
        self.params('sheet').compute_default()
        sheet=p.sheet

        for coord in p.coords:
            orientation=pi*self._sheetview_unit(sheet,coord,'OrientationPreference')
            self.curve_parameters=[{"orientation":orientation+ro} for ro in self.relative_orientations]

            self.x=self._sheetview_unit(sheet,coord,'XPreference',default=coord[0])
            self.y=self._sheetview_unit(sheet,coord,'YPreference',default=coord[1])
            
            self._compute_curves(p,sheet,val_format="%.4f")

    def _feature_list(self,p):
        return [Feature(name="phase",range=(0.0,2*pi),step=2*pi/p.num_phase,cyclic=True),
                Feature(name="frequency",values=p.frequencies),
                Feature(name="contrast",values=p.contrasts,cyclic=False)]


create_plotgroup(template_plot_type="curve",name='Contrast Response',category="Tuning Curves",
        doc='Measure the contrast response function for a specific unit.',
        update_command=measure_contrast_response,
        plot_command='tuning_curve(x_axis="contrast",unit="%")',
        prerequisites=['OrientationPreference','XPreference'])



class measure_dr_pref(SinusoidalMeasureResponseCommand):
    """Measure a direction preference map by collating the response to patterns."""

    num_phase = param.Integer(default=12)
    
    num_direction = param.Integer(default=6,bounds=(1,None),softbounds=(1,48),
                                  doc="Number of directions to test.")

    num_speeds = param.Integer(default=4,bounds=(1,None),softbounds=(1,10),
                               doc="Number of speeds to test.")

    max_speed = param.Number(default=2.0/24.0,bounds=(0,None),doc="""
        The maximum speed to measure (with zero always the minimum).""")

    subplot = param.String("Direction")

    def _feature_list(self,p):
        return [Feature(name="speed",range=(0.0,p.max_speed),step=float(p.max_speed)/p.num_speeds,cyclic=False),
                Feature(name="frequency",values=p.frequencies),
                Feature(name="direction",range=(0.0,2*pi),step=2*pi/p.num_direction,cyclic=True),
                Feature(name="phase",range=(0.0,2*pi),step=2*pi/p.num_phase,cyclic=True)]

  
pg= create_plotgroup(name='Direction Preference',category="Preference Maps",
             doc='Measure preference for sine grating movement direction.',
             update_command=measure_dr_pref)
pg.add_plot('Direction Preference',[('Hue','DirectionPreference')])
pg.add_plot('Direction Preference&Selectivity',[('Hue','DirectionPreference'),
                                                ('Confidence','DirectionSelectivity')])
pg.add_plot('Direction Selectivity',[('Strength','DirectionSelectivity')])
pg.add_plot('Speed Preference',[('Strength','SpeedPreference')])
pg.add_plot('Speed Selectivity',[('Strength','SpeedSelectivity')])
pg.add_static_image('Color Key','topo/command/dr_key_white_vert_small.png')



class measure_hue_pref(SinusoidalMeasureResponseCommand):
    """Measure a hue preference map by collating the response to patterns."""

    num_phase = param.Integer(default=12)
    
    num_hue = param.Integer(default=8,bounds=(1,None),softbounds=(1,48),
                            doc="Number of hues to test.")

    subplot = param.String("Hue")

    # For backwards compatibility; not sure why it needs to differ from the default
    static_parameters = param.List(default=[])

    def _feature_list(self,p):
        return [Feature(name="frequency",values=p.frequencies),
                Feature(name="orientation",range=(0,pi),step=pi/p.num_orientation,cyclic=True),
                Feature(name="hue",range=(0.0,1.0),step=1.0/p.num_hue,cyclic=True),
                Feature(name="phase",range=(0.0,2*pi),step=2*pi/p.num_phase,cyclic=True)]


pg= create_plotgroup(name='Hue Preference',category="Preference Maps",
             doc='Measure preference for colors.',
             update_command=measure_hue_pref,normalize=True)
pg.add_plot('Hue Preference',[('Hue','HuePreference')])
pg.add_plot('Hue Preference&Selectivity',[('Hue','HuePreference'), ('Confidence','HueSelectivity')])
pg.add_plot('Hue Selectivity',[('Strength','HueSelectivity')])




gaussian_corner = topo.pattern.basic.Composite(
    operator = maximum, generators = [
        topo.pattern.basic.Gaussian(size = 0.06,orientation=0,aspect_ratio=7,x=0.3),
        topo.pattern.basic.Gaussian(size = 0.06,orientation=pi/2,aspect_ratio=7,y=0.3)])


class measure_corner_or_pref(PositionMeasurementCommand):
    """Measure a corner preference map by collating the response to patterns."""
    
    scale = param.Number(default=1.0)

    divisions=param.Integer(default=10)

    pattern_presenter = param.Callable(PatternPresenter(gaussian_corner,apply_output_fn=False,duration=0.175))

    x_range=param.NumericTuple((-1.2,1.2))

    y_range=param.NumericTuple((-1.2,1.2))

    num_orientation = param.Integer(default=4,bounds=(1,None),softbounds=(1,24),
                                    doc="Number of orientations to test.")

    # JABALERT: Presumably this should be omitted, so that size is included?
    static_parameters = param.List(default=["scale","offset"])

    def _feature_list(self,p):
        width =1.0*p.x_range[1]-p.x_range[0]
        height=1.0*p.y_range[1]-p.y_range[0]
        return [Feature(name="x",range=p.x_range,step=width/p.divisions),
                Feature(name="y",range=p.y_range,step=height/p.divisions),
                Feature(name="orientation",range=(0,2*pi),step=2*pi/p.num_orientation,cyclic=True)]


pg= create_plotgroup(name='Corner OR Preference',category="Preference Maps",
             doc='Measure orientation preference for corner shape (or other complex stimuli that cannot be represented as fullfield patterns).',
             update_command=measure_corner_or_pref,
             plot_command='topographic_grid()',
             normalize=True)
pg.add_plot('Corner Orientation Preference',[('Hue','OrientationPreference')])
pg.add_plot('Corner Orientation Preference&Selectivity',[('Hue','OrientationPreference'),
						   ('Confidence','OrientationSelectivity')])
pg.add_plot('Corner Orientation Selectivity',[('Strength','OrientationSelectivity')])



# Doesn't currently have support in the GUI for controlling the input_sheet
class measure_retinotopy(SinusoidalMeasureResponseCommand):
    """
    Measures peak retinotopy preference (as in Schuett et. al Journal
    of Neuroscience 22(15):6549-6559, 2002). The retina is divided
    into squares (each assigned a color in the color key) which are
    activated by sine gratings of various phases and orientations.
    For each unit, the retinotopic position with the highest response
    at the preferred orientation and phase is recorded and assigned a
    color according to the retinotopy color key.
    """

    divisions=param.Integer(default=4,bounds=(1,None),doc="""
        The number of different positions to measure in X and in Y.""")
    
    pattern_presenter = param.Callable(
        default=PatternPresenter(SineGratingRectangle()),doc="""
        Callable object that will present a parameter-controlled
        pattern to a set of Sheets.  For measuring position, the
        pattern_presenter should be spatially localized, yet also able
        to activate the appropriate neurons reliably.""")

    static_parameters = param.List(default=["size","scale","offset"])
  
    scale = param.Number(default=1.0)

    input_sheet = param.ObjectSelector(
        default=None,compute_default_fn=default_input_sheet,doc="""
        Name of the sheet where input should be drawn.""")

    weighted_average= param.Boolean(default=False)


    def __call__(self,**params):
        p=ParamOverrides(self,params)
        self.params('input_sheet').compute_default()
        result=super(measure_retinotopy,self).__call__(**params)
        self.retinotopy_key(p)


    def _feature_list(self,p):
        l,b,r,t = p.input_sheet.nominal_bounds.lbrt()
        x_range=(r,l)
        y_range=(t,b)
    
        self.size=float((x_range[0]-x_range[1]))/p.divisions
        self.retinotopy=range(p.divisions*p.divisions)

        p.pattern_presenter.divisions=p.divisions
        
        return [Feature(name="retinotopy",values=self.retinotopy),
                Feature(name="orientation",range=(0.0,2*pi),step=2*pi/p.num_orientation,cyclic=True),
                Feature(name="frequency",values=p.frequencies),
                Feature(name="phase",range=(0.0,2*pi),step=2*pi/p.num_phase,cyclic=True)]


    # JABALERT: Can't we move this to the plot_command, not the update_command?
    def retinotopy_key(self,p):
        """Automatic plot of retinotopy color key."""

        l,b,r,t = p.input_sheet.nominal_bounds.lbrt()

        coordinate_x=[]
        coordinate_y=[]
        coordinates=[]
        mat_coords=[]
    
        x_div=float(r-l)/(p.divisions*2)
        y_div=float(t-b)/(p.divisions*2)
        ret_matrix = ones(p.input_sheet.shape, float)
     
        for i in range(p.divisions):
            if not bool(p.divisions%2):
                if bool(i%2):
                    coordinate_x.append(i*x_div)
                    coordinate_y.append(i*y_div)
                    coordinate_x.append(i*-x_div)
                    coordinate_y.append(i*-y_div)
            else:
                if not bool(i%2):
                    coordinate_x.append(i*x_div)
                    coordinate_y.append(i*y_div)
                    coordinate_x.append(i*-x_div)
                    coordinate_y.append(i*-y_div)
      
        for x in coordinate_x:
            for y in coordinate_y:
                coordinates.append((x,y))
                
          
        for r in self.retinotopy:
            x_coord=coordinates[r][0]
            y_coord=coordinates[r][1]
            x_top, y_top = p.input_sheet.sheet2matrixidx(x_coord+x_div,y_coord+y_div)
            x_bot, y_bot = p.input_sheet.sheet2matrixidx(x_coord-x_div,y_coord-y_div)
            norm_ret=float((r+1.0)/(p.divisions*p.divisions))
            
            for x in range(min(x_bot,x_top),max(x_bot,x_top)):
                for y in range(min(y_bot,y_top),max(y_bot,y_top)):
                    ret_matrix[x][y] += norm_ret
                   
        #Plot the color key
        import pylab
        from topo.command.pylabplots import matrixplot
        matrixplot(ret_matrix, plot_type=pylab.hsv, title="Color Key")


pg=create_plotgroup(name='Retinotopy',category="Other",
                    doc='Measure retinotopy',update_command=measure_retinotopy,
                    normalize=True)
pg.add_plot('Retinotopy',[('Hue','RetinotopyPreference')])
pg.add_plot('Retinotopy Selectivity',[('Hue','RetinotopyPreference'),('Confidence','RetinotopySelectivity')])



class measure_orientation_contrast(UnitCurveCommand):
    """
    Measures the response to a center sine grating disk and a surround
    sine grating ring at different contrasts of the central disk. 

    The central disk is set to the preferred orientation of the unit
    to be measured. The surround disk orientation (relative to the
    central grating) and contrast can be varied, as can the size of
    both disks.
    """

    pattern_presenter = param.Callable(
        default=PatternPresenter(pattern_generator=OrientationContrastPattern(),
                                 contrast_parameter="weber_contrast"))

    size=None # Disabled unused parameter
    # Maybe instead of the below, use size and some relative parameter, to allow easy scaling?

    # ALERT: Rename to center.
    size_centre=param.Number(default=0.5,bounds=(0,None),doc="""
        The size of the central pattern to present.""")

    size_surround=param.Number(default=1.0,bounds=(0,None),doc="""
        The size of the surround pattern to present.""")

    contrasts = param.List(class_=int,default=[10,20,30,40,50,60,70,80,90,100])

    relative_orientations = param.List(class_=float,default=[0.0, pi/2])

    thickness=param.Number(default=0.5,bounds=(0,None),softbounds=(0,1.5),doc=""" """)
    
    contrastsurround=param.Number(default=80,bounds=(0,100),doc=""" """)
    
    x_axis = param.String(default='contrastcentre',constant=True)

    units = param.String(default=" rad")

    static_parameters = param.List(default=["x","y","size_centre","size_surround","orientationcentre","contrastsurround","thickness"])

    def __call__(self,**params):
        p=ParamOverrides(self,params)
        self.params('sheet').compute_default()
        sheet=p.sheet

        for coord in p.coords:
            orientation=pi*self._sheetview_unit(sheet,coord,'OrientationPreference')
            self.orientationcentre=orientation
            self.curve_parameters=[{"orientationsurround":orientation+ro} for ro in self.relative_orientations]
            
            self.x=self._sheetview_unit(sheet,coord,'XPreference',default=coord[0])
            self.y=self._sheetview_unit(sheet,coord,'YPreference',default=coord[1])
            
            self._compute_curves(p,sheet,val_format="%.4f")

    def _feature_list(self,p):
        return [Feature(name="phase",range=(0.0,2*pi),step=2*pi/p.num_phase,cyclic=True),
                Feature(name="frequency",values=p.frequencies),
                Feature(name="contrastcentre",values=p.contrasts,cyclic=False)]


create_plotgroup(template_plot_type="curve",name='Orientation Contrast',category="Tuning Curves",
                 doc='Measure the response of one unit to a centre and surround sine grating disk.',
                 update_command=measure_orientation_contrast,
                 plot_command='tuning_curve(x_axis="contrastcentre",unit="%")',
                 prerequisites=['OrientationPreference','XPreference'])        



# JABALERT: Should eliminate the combined preference maps and do something in lissom.ty instead.

pg= create_plotgroup(name='Orientation and Ocular Preference',category="Combined Preference Maps",
             doc='Plot the orientation preference overlaid with ocular dominance boundaries.',
             update_command='',
             plot_command='overlaid_plots(plot_template=[{"Hue":"OrientationPreference"},{"Strength":"OrientationSelectivity"}],overlay=[("contours","OcularPreference",0.5,"black")])',            
             normalize=False)



pg= create_plotgroup(name='Orientation and Direction Preference',category="Combined Preference Maps",
             doc='Plot the orientation preference overlaid with direction preference arrows.',
             update_command='',
             plot_command='overlaid_plots(plot_template=[{"Hue":"OrientationPreference"}],overlay=[("arrows","DirectionPreference","DirectionSelectivity","white")])',            
             normalize=False)



pg= create_plotgroup(name='Orientation and PhaseDisparity Preference',category="Combined Preference Maps",
             doc='Plot the orientation preference overlaid with phase disparity preference boundaries.',
             update_command='',
             plot_command='overlaid_plots(plot_template=[{"Hue":"OrientationPreference","Confidence":"OrientationSelectivity"},{"Strength":"OrientationSelectivity"}],overlay=[("contours","PhasedisparityPreference",0.83,"magenta"),("contours","PhasedisparityPreference",0.08,"yellow")])',            
             normalize=False)



pg= create_plotgroup(name='Orientation and Hue Preference',category="Combined Preference Maps",
             doc='Plot the orientation preference overlaid with hue preference boundaries.',
             update_command='',
             plot_command='overlaid_plots(plot_template=[{"Hue":"OrientationPreference","Confidence":"OrientationSelectivity"},{"Strength":"OrientationSelectivity"}],overlay=[("contours","HuePreference",0.9,"red"),("contours","HuePreference",0.4,"green")],normalize=True)',            
             normalize=True)



pg= create_plotgroup(name='Orientation, Ocular and Direction Preference',category="Combined Preference Maps",
             doc='Plot the orientation preference overlaid with ocular dominance boundaries and direction preference arrows.',
             update_command='',
             plot_command='overlaid_plots(plot_template=[{"Hue":"OrientationPreference"},{"Strength":"OrientationSelectivity"}],overlay=[("contours","OcularPreference",0.5,"black"),("arrows","DirectionPreference","DirectionSelectivity","white")])',            
             normalize=False)




import types
__all__ = list(set([k for k,v in locals().items()
                    if isinstance(v,types.FunctionType) or 
                    (isinstance(v,type) and issubclass(v,ParameterizedFunction))
                    and not v.__name__.startswith('_')]))
