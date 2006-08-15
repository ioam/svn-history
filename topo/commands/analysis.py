"""
User-level analysis commands, typically for measuring or generating SheetViews.

$Id$
"""


from Numeric import array, zeros, Float,size, shape
from math import pi


import topo
import random
import copy

from topo.analysis.featuremap import MeasureFeatureMap
from topo.base.arrayutils import octave_output, centroid
from topo.base.cf import CFSheet, CFProjection, Projection
from topo.base.sheet import Sheet
from topo.sheets.lissom import LISSOM
from topo.base.sheetview import SheetView, ProjectionView
import topo.base.patterngenerator
from topo.commands.basic import pattern_present
from topo.patterns.basic import SineGrating, Gaussian
from topo.sheets.generatorsheet import GeneratorSheet
from topo.base.projection import ProjectionSheet
from topo.misc.numbergenerators import UniformRandom
from topo.base.parameterclasses import DynamicNumber
from topo.base.sheet import Sheet
from topo.base.sheetview import SheetView


class PatternPresenter(object):
    """
    Function object for presenting PatternGenerator-created patterns,
    for use with map measurement commands like measure_or_pref.
    """
    
    def __init__(self,pattern_generator,apply_output_fn=True,duration=1.0):
        self.apply_output_fn=apply_output_fn
        self.duration=duration
        self.gen = pattern_generator

    def __call__(self,features_values,param_dict):

        #Original call method
        """
        for param,value in param_dict.iteritems():
           self.gen.__setattr__(param,value)
        
        for feature,value in features_values.iteritems():
           self.gen.__setattr__(feature,value)
 
        inputs = dict().fromkeys(topo.sim.objects(GeneratorSheet),self.gen)
 
        pattern_present(inputs, self.duration, learning=False,
                        apply_output_fn=self.apply_output_fn)

        """
        
        for param,value in param_dict.iteritems():
           self.gen.__setattr__(param,value)
        
        for feature,value in features_values.iteritems():
           self.gen.__setattr__(feature,value)

        gen_list=topo.sim.objects(GeneratorSheet)
        eye=gen_list.keys()

        ###TRHACKALERT: This is not a generic implementation for presenting patterns. Certain
        ###validations should be done(on GUI level as well).

        if len(eye)==2:
            gen_copy1=copy.deepcopy(self.gen)
            gen_copy2=copy.deepcopy(self.gen)
            inputs={}
            
            if features_values.has_key("positiondisparity"):
                inputs[eye[0]]=gen_copy1
                gen_copy2.x=gen_copy2.x + gen_copy2.positiondisparity
                inputs[eye[1]]=gen_copy2

            elif features_values.has_key("phasedisparity"):
                
                phase_first=random.uniform(0,2*pi)
                phase_first_copy=copy.deepcopy(phase_first)
                phase_second=phase_first_copy + features_values['phasedisparity']
                proj_sheets=topo.sim.objects(CFSheet)
                sheets_name=proj_sheets.keys()
                lissom=topo.sim.objects(LISSOM).keys()

                for sheet in sheets_name:
                    if sheet != lissom[0]:
                        conn_field=proj_sheets[sheet].out_connections
                        if proj_sheets[sheet].in_connections[0].src.name == eye[0]:
                            conn_field[0].weights_generator.__setattr__('phase',phase_first)
                        else:
                            conn_field[0].weights_generator.__setattr__('phase',phase_second)
                            
                inputs = dict().fromkeys(topo.sim.objects(GeneratorSheet),self.gen)

            elif features_values.has_key("ocular"):
                gen_copy1.scale=2*gen_copy1.ocular
                inputs[eye[0]]=gen_copy1
                gen_copy2.scale=2.0-2*gen_copy2.ocular
                inputs[eye[1]]=gen_copy2
        else:
            inputs = dict().fromkeys(topo.sim.objects(GeneratorSheet),self.gen)

        pattern_present(inputs, self.duration, learning=False,
                        apply_output_fn=self.apply_output_fn)

                    

def measure_or_pref(num_phase=18,num_orientation=4,frequencies=[2.4],
                    scale=0.3,offset=0.0,display=False,
		    user_function=PatternPresenter(pattern_generator=SineGrating(),
                                                   apply_output_fn=False,duration=0.175)):


    """
    Measure orientation maps, using a sine grating by default.

    Measures maps by collating the responses to a set of input
    patterns controlled by some parameters.  The parameter ranges and
    number of input patterns in each range are determined by the
    num_phase, num_orientation, and frequencies parameters.  The
    particular pattern used is determined by the user_function
    argument, which defaults to a sine grating presented for a short
    duration.  By convention, the Topographica example files
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

        feature_values = {"orientation": ( (0.0,pi), step_orientation, True),
                          "phase": ( (0.0,2*pi),step_phase,True),
                          "frequency": ((min(frequencies),max(frequencies)),frequencies,False)}

        x=MeasureFeatureMap(feature_values)

        param_dict = {"scale":scale,"offset":offset}

        x.measure_maps(user_function, param_dict, display)


def measure_od_pref(num_phase=18,num_orientation=4,frequencies=[2.4],
                    scale=0.3,offset=0.0,display=True,
		    user_function=PatternPresenter(pattern_generator=SineGrating(),
                                                   apply_output_fn=False,duration=0.175)):
    
    if num_phase <= 0 or num_orientation <= 0:
        raise ValueError("num_phase and num_orientation must be greater than 0")

    else:
        step_phase=2*pi/num_phase
        step_orientation=pi/num_orientation

        feature_values = {"orientation": ( (0.0,pi), step_orientation, True),
                          "phase": ( (0.0,2*pi),step_phase,True),
                          "frequency": ((min(frequencies),max(frequencies)),frequencies,False),
                          "ocular":((0.0,1.0),[0.0,1.0],False)}

        x=MeasureFeatureMap(feature_values)

        param_dict = {"scale":scale,"offset":offset}

        x.measure_maps(user_function, param_dict, display)


###TRHACKALERT :Might be preferable to present multiple oriented Gaussians as input
### instead of Sine Grating. Any change in the x and y parameters would cause a change in
### phase, as Jim mentioned.

def measure_position_disparity(num_phase=18,num_orientation=4,frequencies=[2.4],
                    scale=0.3,offset=0.0,display=True,
		    user_function=PatternPresenter(pattern_generator=SineGrating(),
                                                   apply_output_fn=False,duration=0.175)):

    
    if num_phase <= 0 or num_orientation <= 0:
        raise ValueError("num_phase and num_orientation must be greater than 0")

    else:
        step_phase=2*pi/num_phase
        step_orientation=pi/num_orientation

        ###HACKALERT: If I name the feature_value position_disparity and do the necessary chnages in
        ###topo.plotting.templates, I don't get any plot. Same applies for phase_disparity

        feature_values = {"orientation": ( (0.0,pi), step_orientation, True),
                          "phase": ( (0.0,2*pi),step_phase,True),
                          "frequency": ((min(frequencies),max(frequencies)),frequencies,False),
                          "positiondisparity":((-0.2,0.2),[-0.2,0.0,0.2],False)}

        x=MeasureFeatureMap(feature_values)

        param_dict = {"scale":scale,"offset":offset}

        x.measure_maps(user_function, param_dict, display)


def measure_phase_disparity(num_phase=18,num_orientation=4,num_disparity=4,frequencies=[2.4],
                    scale=0.3,offset=0.0,display=True,
		    user_function=PatternPresenter(pattern_generator=SineGrating(),
                                                   apply_output_fn=False,duration=0.175)):


    if num_phase <= 0 or num_orientation <= 0 or num_disparity <= 0:
        raise ValueError("num_phase, num_disparity and num_orientation must be greater than 0")

    else:
        step_phase=2*pi/num_phase
        step_orientation=pi/num_orientation
        step_disparity=2*pi/num_disparity

        feature_values = {"orientation": ( (0.0,pi), step_orientation, True),
                          "phase": ( (0.0,2*pi),step_phase,True),
                          "frequency": ((min(frequencies),max(frequencies)),frequencies,False),
                          "phasedisparity":((0.0,2*pi),step_disparity,True)}

        x=MeasureFeatureMap(feature_values)

        param_dict = {"scale":scale,"offset":offset}

        x.measure_maps(user_function, param_dict, display)
    

def measure_position_pref(divisions=6,size=0.5,scale=0.3,offset=0.0,display=False,
                          user_function=PatternPresenter(Gaussian(aspect_ratio=1.0),False,1.0),
                          x_range=(-0.5,0.5),y_range=(-0.5,0.5)):
    """Measure position preference map, using Gaussian patterns by default."""

    if divisions <= 0:
        raise ValueError("divisions must be greater than 0")

    else:
        # JABALERT: Will probably need some work to support multiple input regions
        feature_values = {"x": ( x_range, 1.0*(x_range[1]-x_range[0])/divisions, False),
                          "y": ( y_range, 1.0*(y_range[1]-y_range[0])/divisions, False)}
        x=MeasureFeatureMap(feature_values)
        param_dict = {"size":size,"scale":scale,"offset":offset}
        x.measure_maps(user_function, param_dict, display)



def measure_cog():
    """Calculate center of gravity for each CF of each unit in each CFSheet."""

    f = lambda x: hasattr(x,'measure_maps') and x.measure_maps
    measured_sheets = filter(f,topo.sim.objects(CFSheet).values())

    for sheet in measured_sheets:
        for proj in sheet.in_connections:
	    if proj.src.name == 'Retina':
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
                    
                    ### JLHACKALERT: This currently only works if there is a 
                    ### projection from a sheet called 'Retina' (presumed to be the afferent) - will not work for a 
                    ### more general case. There is probably a better way.
                    
			new_view = SheetView((xpref,sheet.bounds), sheet.name,sheet.precedence)
			sheet.sheet_view_dict['XCoG']=new_view
			new_view = SheetView((ypref,sheet.bounds), sheet.name,sheet.precedence)
			sheet.sheet_view_dict['YCoG']=new_view
    
                

def update_activity():
    """
    Measure an activity map. Command called when opening an activity plot group panel.

    To be precise, just add the activity sheet_view for Sheets objects of the simulation.
    """
    for sheet in topo.sim.objects(Sheet).values():
        activity_copy = array(sheet.activity)
        new_view = SheetView((activity_copy,sheet.bounds),
                              sheet.name,sheet.precedence)
        sheet.sheet_view_dict['Activity']=new_view
    

# JABALERT: Module variables for passing values to the commands; should be
# changed to a cleaner mechanism.
coordinate = (0,0)
sheet_name = ''
proj_coords=[(0,0)]
proj_name =''


### JACALERT! This function, as well as update_projections have to be simplified.
### Particularly, having to retrieve the Sheet object from the sheet_name is an issue:
### It might be better to have access to the Sheet object directly rather then the name 
### in the CFSheetPlotpanels.
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
                elif proj_name == '' or p.name==proj_name:
                    v = p.get_projection_view()
                    key = ('ProjectionActivity',v.projection.dest.name,v.projection.name)
                    v.projection.src.sheet_view_dict[key] = v

