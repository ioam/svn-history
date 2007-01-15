"""
User-level analysis commands, typically for measuring or generating SheetViews.

$Id$
"""
__version__='$Revision$'


from Numeric import array, zeros, Float,size, shape
from math import pi
from copy import deepcopy

import topo
from topo.base.arrayutils import octave_output, centroid
from topo.base.cf import CFSheet, CFProjection, Projection
from topo.base.parameterizedobject import ParameterizedObject
from topo.base.parameterclasses import DynamicNumber
from topo.base.projection import ProjectionSheet
from topo.base.sheet import Sheet
from topo.base.sheetview import SheetView, ProjectionView
from topo.commands.basic import pattern_present
from topo.misc.numbergenerators import UniformRandom
from topo.misc.utils import frange, wrap
from topo.patterns.basic import SineGrating, Gaussian, SineGratingDisk
from topo.sheets.generatorsheet import GeneratorSheet
from topo.base.parameterclasses import Wrapper, Parameter
from topo.analysis.featureresponses import FeatureMaps, FeatureCurves


class Feature(object):
    """
    Stores the parameters requires for generating a map of one input feature.
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
        input_pattern=gen_list.keys()

        inputs = dict().fromkeys(topo.sim.objects(GeneratorSheet),self.gen)

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
        gen_copy1=deepcopy(self.gen)
        gen_copy2=deepcopy(self.gen)

        if features_values.has_key("phasedisparity"):
            if len(input_pattern)!=2:
                self.warning('Disparity is defined only when there are exactly two patterns')
            else:
                temp_phase1=gen_copy1.phase - gen_copy1.phasedisparity/2.0
                temp_phase2=gen_copy2.phase + gen_copy2.phasedisparity/2.0
                gen_copy1.phase=wrap(0,2*pi,temp_phase1)
                gen_copy2.phase=wrap(0,2*pi,temp_phase2)
    
                inputs={}
                inputs[input_pattern[0]]=gen_copy1
                inputs[input_pattern[1]]=gen_copy2

        ## Not yet used; example only
        #if features_values.has_key("xdisparity"):
        #    if len(input_pattern)!=2:
        #        self.warning('Disparity is defined only when there are exactly two patterns')
        #    else:
        #        gen_copy1.x=gen_copy1.x - gen_copy1.xdisparity/2.0
        #        gen_copy2.x=gen_copy2.x + gen_copy2.xdisparity/2.0
        #
        #        inputs={}
        #        inputs[input_pattern[0]]=gen_copy1
        #        inputs[input_pattern[1]]=gen_copy2
        #
        #if features_values.has_key("ydisparity"):
        #    if len(input_pattern)!=2:
        #        self.warning('Disparity is defined only when there are exactly two patterns')
        #    else:
        #        gen_copy1.y=gen_copy1.y - gen_copy1.ydisparity/2.0
        #        gen_copy2.y=gen_copy2.y + gen_copy2.ydisparity/2.0
        #
        #        inputs={}
        #        inputs[input_pattern[0]]=gen_copy1
        #        inputs[input_pattern[1]]=gen_copy2

        if features_values.has_key("ocular"):
            if len(input_pattern)!=2:
                self.warning('Ocularity is defined only when there are exactly two patterns')
            else:
                gen_copy1.scale=2*gen_copy1.ocular
                gen_copy2.scale=2.0-2*gen_copy2.ocular
                
                inputs[input_pattern[0]]=gen_copy1
                inputs[input_pattern[1]]=gen_copy2


        if features_values.has_key("contrast") or param_dict.has_key("contrast"):
            if self.contrast_parameter=='michelson_contrast':
                self.gen.offset=0.5   
                self.gen.scale=2*self.gen.offset*self.gen.contrast/100
            
	
            elif self.contrast_parameter=='weber_contrast':
                # Weber_contrast is currently only well defined for the special case where 
                #the background offset is equal to the target offset in the pattern type SineGratingDisk')
                self.gen.offset=0.5   #In this case this is the offset of both the background and the sine grating
                self.gen.scale=2*self.gen.offset*self.gen.contrast/100
            
                
            elif self.contrast_parameter=='scale':
                self.gen.offset=0.0
                self.gen.scale=self.gen.contrast
            
            
        pattern_present(inputs, self.duration, learning=False,
                        apply_output_fn=self.apply_output_fn)
# Module variables for passing values to the commands.
coordinate = (0,0)
sheet_name = ''
proj_coords=[(0,0)]
proj_name =''

### JABALERT: This mechanism for passing values is a bit awkward, and
### should be changed to something cleaner.  It might also be better
### to access a Sheet instance directly, rather than searching by name.

def measure_position_pref(divisions=6,size=0.5,scale=0.3,offset=0.0,display=False,
                          pattern_presenter=PatternPresenter(Gaussian(aspect_ratio=1.0),False,1.0),
                          x_range=(-0.5,0.5),y_range=(-0.5,0.5)):
    """
    Measure position preference map, using a circular Gaussian by default.

    Measures maps by collating the responses to a set of input
    patterns controlled by some parameters.  The parameter ranges and
    number of input patterns in each range are determined by the
    divisions parameter.  The particular pattern used is determined by the
    size, scale, offset, and pattern_presenter arguments.
    """

    if divisions <= 0:
        raise ValueError("divisions must be greater than 0")

    else:
        # JABALERT: Will probably need some work to support multiple input regions
        feature_values = [Feature(name="x",range=x_range,step=1.0*(x_range[1]-x_range[0])/divisions),
                          Feature(name="y",range=y_range,step=1.0*(y_range[1]-y_range[0])/divisions)]          
                          
        param_dict = {"size":size,"scale":scale,"offset":offset}
        x=FeatureMaps(feature_values)
        x.collect_feature_responses(pattern_presenter,param_dict,display)
       


def measure_or_pref(num_phase=18,num_orientation=4,frequencies=[2.4],
                    scale=0.3,offset=0.0,display=False,
                    pattern_presenter=PatternPresenter(pattern_generator=SineGrating(),
                                                       apply_output_fn=False,duration=0.175)):
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

        feature_values = [Feature(name="phase",range=(0.0,2*pi),step=step_phase,cyclic=True),
                          Feature(name="orientation",range=(0.0,pi),step=step_orientation,cyclic=True),
                          Feature(name="frequency",values=frequencies)]     

        param_dict = {"scale":scale,"offset":offset}
        x=FeatureMaps(feature_values)
        x.collect_feature_responses(pattern_presenter,param_dict,display)



def measure_or_tuning_fullfield(num_phase=18,num_orientation=12,frequencies=[2.4],
                                curve_parameters=[{"contrast":30}, {"contrast":60}, {"contrast":90}],
                                display=True,
                                pattern_presenter=PatternPresenter(pattern_generator=SineGrating(),
                                                                   apply_output_fn=False,duration=1.0,
                                                                   contrast_parameter="michelson_contrast")):
    """
    Measures orientation tuning curve of a particular unit using a full field grating stimulus. 
    michelson_contrast can be replaced by another variable(s) eg. scale, weber_contrast or
    any other contrast definition, provided it is defined in PatternPresenter. 
    """

    f = lambda x: hasattr(x,'measure_maps') and x.measure_maps
    measured_sheets = filter(f,topo.sim.objects(CFSheet).values())
    
    for sheet in measured_sheets:
	sheet_name=str(sheet)
	if num_phase <= 0 or num_orientation <= 0:
	    raise ValueError("num_phase and num_orientation must be greater than 0")
    
	else:
	    step_phase=2*pi/num_phase
	    step_orientation=pi/num_orientation

	    feature_values = [Feature(name="phase",range=(0.0,2*pi),step=step_phase,cyclic=True),
			      Feature(name="orientation",range=(0,5*pi/4),step=step_orientation,cyclic=True),
			      Feature(name="frequency",values=frequencies)]     
        
	    x_axis='orientation'
	    x=FeatureCurves(sheet,x_axis)
    
        for curve in curve_parameters:
	    param_dict={}
            param_dict.update(curve)
	    curve_label='Contrast = '+str(curve["contrast"])+'%'
            x.collect_feature_responses(feature_values,pattern_presenter,param_dict,curve_label,display)
	  


def measure_contrast_response_fullfield(contrasts=[10,20,30,40,50,60,70,80,90],relative_orientations=[-pi/10,0,pi/10],
                                        display=True,frequency=2.4,
                                        pattern_presenter=PatternPresenter(pattern_generator=SineGrating(),
                                                                           apply_output_fn=False,duration=1.0,
                                                                           contrast_parameter="michelson_contrast")):
    """
    Measure the contrast response curve of a particular unit.
    
    Uses a full field grating stimulus at the preferred orientation of the unit.
    Orientation preference must be measured before measuring the contrast response.
    The contrast_parameter is michelson_contrast but can be replaced by another variable
    eg. scale, weber_contrast or any other contrast definition, provided it is defined in PatternPresenter. 
    """
    
    f = lambda x: hasattr(x,'measure_maps') and x.measure_maps
    measured_sheets = filter(f,topo.sim.objects(CFSheet).values())
    
    for sheet in measured_sheets:
	sheet_name=str(sheet)
	matrix_coords = sheet.sheet2matrixidx(coordinate[0],coordinate[1])
	if(('OrientationPreference' in sheet.sheet_view_dict) and
	   ('PhasePreference' in sheet.sheet_view_dict)):
	    or_pref = sheet.sheet_view_dict['OrientationPreference'].view()[0]
	    phase_pref = sheet.sheet_view_dict['PhasePreference'].view()[0]
	    or_value = or_pref[matrix_coords]
	    phase_value = phase_pref[matrix_coords]
	else:
	    raise ValueError("Orientation Preference must be measured before plotting Contrast Response")

        curve_parameters=[{"orientation":or_value+ro} for ro in relative_orientations]
    
	feature_values = [Feature(name="contrast",values=contrasts)]
	x_axis='contrast'
	x=FeatureCurves(sheet,x_axis)

	for curve in curve_parameters:
            param_dict = {"phase":phase_value, "frequency":frequency}
            param_dict.update(curve)
            curve_label='Orientation = %.4f rad' % curve["orientation"] 
	    x.collect_feature_responses(feature_values,pattern_presenter, param_dict,curve_label,display)
    
    
        
def measure_size_response(num_phase=18,frequency=2.4,
                          curve_parameters=[{"contrast":0.2}, {"contrast":0.3}, {"contrast":0.4},{"contrast":0.5}],
                          num_sizes=10,display=True,
                          pattern_presenter=PatternPresenter(pattern_generator=SineGratingDisk(),
                                                             apply_output_fn=False,duration=1.0,
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
    matrix_coords = sheet.sheet2matrixidx(topo.commands.analysis.coordinate[0],topo.commands.analysis.coordinate[1])
    if(('OrientationPreference' in sheet.sheet_view_dict)and
       ('XPreference' in sheet.sheet_view_dict) and
       ('YPreference' in sheet.sheet_view_dict)):
        or_pref = sheet.sheet_view_dict['OrientationPreference'].view()[0]
        x_pref = sheet.sheet_view_dict['XPreference'].view()[0]
        y_pref = sheet.sheet_view_dict['YPreference'].view()[0]
        or_value = or_pref[matrix_coords]
        x_value=x_pref[matrix_coords]
        y_value=y_pref[matrix_coords]
    else:
        raise ValueError("Orientation Preference and Position Preference must be measured before plotting Size Response")

    if num_phase <= 0:
        raise ValueError("num_phase must be greater than 0")

    else:
        step_phase=2*pi/num_phase
        step_size=0.6/num_sizes
        
        feature_values = [Feature(name="phase",range=(0.0,2*pi),step=step_phase,cyclic=True),
                          Feature(name="size",range=(0.1,0.7),step=step_size,cyclic=False)]

        x_axis='size'
        x=FeatureCurves(sheet,x_axis)
          
        for curve in curve_parameters:
            param_dict = {"x":x_value,"y":y_value,"orientation":or_value,"frequency":frequency}
            param_dict.update(curve)
	    curve_label='Contrast = '+str(curve["contrast"])+'%'
            x.collect_feature_responses(feature_values,pattern_presenter, param_dict,curve_label,display)

                  

def measure_contrast_response(contrasts=[0.1,0.2,0.3,0.4,0.5],relative_orientations=[-pi/10,0,pi/10],
                              size=0.5,display=True,frequency=2.4,
                              num_phase=18,pattern_presenter=PatternPresenter(pattern_generator=SineGratingDisk(),
                                                                              apply_output_fn=False,duration=1.0,
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
    if(('OrientationPreference' in sheet.sheet_view_dict) and
       ('XPreference' in sheet.sheet_view_dict) and

       ('YPreference' in sheet.sheet_view_dict)):
        x_pref = sheet.sheet_view_dict['XPreference'].view()[0]
        y_pref = sheet.sheet_view_dict['YPreference'].view()[0]
        or_pref = sheet.sheet_view_dict['OrientationPreference'].view()[0]
        or_value = or_pref[matrix_coords]
        x_value=x_pref[matrix_coords]
        y_value=y_pref[matrix_coords]
    else:
        raise ValueError("Orientation Preference and Position Preference must be measured before plotting Contrast Response")

    curve_parameters=[{"orientation":or_value+ro} for ro in relative_orientations]
    
     
    if num_phase <= 0 :
        raise ValueError("num_phase must be greater than 0")

    else:
        step_phase=2*pi/num_phase
        
        feature_values = [Feature(name="phase",range=(0.0,2*pi),step=step_phase,cyclic=True),
                          Feature(name="contrast",values=contrasts,cyclic=False)]  
        x_axis='contrast'
        x=FeatureCurves(sheet,x_axis)
   
	for curve in curve_parameters:
            param_dict = {"x":x_value,"y":y_value,"frequency":frequency}
            param_dict.update(curve)
            curve_label='Orientation = %.4f rad' % curve["orientation"] 
	    x.collect_feature_responses(feature_values,pattern_presenter, param_dict, curve_label,display)
                        

def measure_or_tuning(num_phase=18,num_orientation=12,frequencies=[2.4],
                      curve_parameters=[{"contrast":0.1}, {"contrast":0.3}, {"contrast":0.4}, {"contrast":0.5}],
                      display=True,size=0.5,
                      pattern_presenter=PatternPresenter(pattern_generator=SineGratingDisk(),
                                                         apply_output_fn=False,duration=1.0,
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
	raise ValueError("Position Preference must be measured before plotting Orientation Response")
        

                 
    if num_phase <= 0 or num_orientation <= 0:
        raise ValueError("num_phase and num_orientation must be greater than 0")
    
    else:
        step_orientation=pi/num_orientation
        step_phase=2*pi/num_phase
        
        feature_values = [Feature(name="phase",range=(0.0,2*pi),step=step_phase,cyclic=True),
                          Feature(name="orientation",range=(0,5*pi/4),step=step_orientation,cyclic=True),
                          Feature(name="frequency",values=frequencies)]     

        x_axis='orientation'
        x=FeatureCurves(sheet,x_axis)
           
    
	for curve in curve_parameters:
            param_dict = {"x":x_value,"y":y_value}
            param_dict.update(curve)
	    curve_label='Contrast = '+str(curve["contrast"])+'%'
            x.collect_feature_responses(feature_values,pattern_presenter, param_dict,curve_label,display)
               


### JABALERT: Shouldn't there be a num_ocularities argument as well, to
### present various combinations of left and right eye activity?        
def measure_od_pref(num_phase=18,num_orientation=4,frequencies=[2.4],
                    scale=0.3,offset=0.0,display=True,
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
        x.collect_feature_responses(pattern_presenter,param_dict,display)
  


def measure_phasedisparity(num_phase=12,num_orientation=4,num_disparity=12,frequencies=[2.4],
                           scale=0.3,offset=0.0,display=True,
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
        x.collect_feature_responses(pattern_presenter,param_dict,display)
     


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
                    
			new_view = SheetView((xpref,sheet.bounds), sheet.name,sheet.precedence)
			sheet.sheet_view_dict['XCoG']=new_view
			new_view = SheetView((ypref,sheet.bounds), sheet.name,sheet.precedence)
			sheet.sheet_view_dict['YCoG']=new_view
    
                

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
                              sheet.name,sheet.precedence)
        sheet.sheet_view_dict['Activity']=new_view
    



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
                    v = p.get_projection_view()
                    key = ('ProjectionActivity',v.projection.dest.name,v.projection.name)
                    v.projection.src.sheet_view_dict[key] = v

