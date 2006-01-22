"""
User-level analysis commands, typically for measuring or generating SheetViews.

$Id$
"""


import re, os
from Numeric import array
from math import pi

import topo.base.simulator

from topo.analysis.featuremap import MeasureFeatureMap
from topo.base.arrayutils import octave_output
from topo.base.sheet import Sheet
from topo.base.sheetview import SheetView
from topo.commands.basic import pattern_present
from topo.patterns.basic import SineGrating, Gaussian
from topo.sheets.generatorsheet import GeneratorSheet



class PatternPresenter(object):
    """
    Function object for presenting PatternGenerator-created patterns,
    for use with map measurement commands like measure_or_pref.
    """
    
    def __init__(self,patterngenerator,apply_output_fn=True,duration=1.0):
        self.apply_output_fn=apply_output_fn
        self.duration=duration
        self.gen = patterngenerator

    def __call__(self,sim,features_values,param_dict):
        ### JABHACKALERT!  Should be able to do this more cleanly using gen's __dict__,
        # with something like:
        #
        #self.gen.__dict__.update(param_dict)
        #self.gen.__dict__.update(features_values)
        #
        # or
        #
        #for param,value in param_dict.iteritems():
        #    self.gen.__dict__[param]=value
        #
        #for feature,value in features_values.iteritems():
        #    self.gen.__dict__[feature]=value

        for param, value in param_dict.iteritems():
            update_generator = "self.gen." + param + "=" + repr(value)
            exec update_generator

        for feature,value in features_values.iteritems():
            update_generator = "self.gen." + feature + "=" + repr(value)
            exec update_generator

        inputs = dict().fromkeys(sim.objects(GeneratorSheet),self.gen)

        pattern_present(inputs, self.duration, learning=False,
                        apply_output_fn=self.apply_output_fn)



def measure_or_pref(num_phase=18,num_orientation=4,frequencies=[2.4],
                    scale=0.3,offset=0.0,display=False,
                    user_function=PatternPresenter(SineGrating(),False,1.0)):
    """Measure orientation maps, using a sine grating by default."""

    # CEBHACKALERT:
    # Is there some way that lissom_or.ty could set the value of a variable
    # that measure_or_pref reads, so that measure_or_pref could default to
    # duration=1.0, but when LISSOM is loaded switches to 0.06?  Otherwise
    # people playing around with CFSOM will think it doesn't work for
    # orientation maps...

    
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



def measure_cog(divisions=6,size=0.1,scale=0.3,offset=0.0,display=False,
                user_function=PatternPresenter(Gaussian(aspect_ratio=1.0),False,1.0)):
    """Measure center-of-gravity (CoG) map, using a Gaussian by default."""

    if divisions <= 0:
        raise ValueError("divisions must be greater than 0")

    else:
        step=1.0/divisions
        feature_values = {"x": ( (-0.5,0.5), step, False),
                          "y": ( (-0.5,0.5), step, False)}
        x=MeasureFeatureMap(feature_values)
        param_dict = {"size":size,"scale":scale,"offset":offset}
        x.measure_maps(user_function, param_dict, display)


def plot_cog():
    """
    Plot the CoG for all Sheets for which measure_cog returned results,
    using the external command 'topogrid'.
    """
    sim = topo.base.simulator.get_active_sim()    
    for sheet in sim.objects(Sheet).values():
        if (('XPreference' in sheet.sheet_view_dict) and
            ('YPreference' in sheet.sheet_view_dict)):
            octave_output("XPreference.matrix",sheet.sheet_view_dict['XPreference'].view()[0],"XPreference",sheet.name)
            octave_output("YPreference.matrix",sheet.sheet_view_dict['YPreference'].view()[0],"YPreference",sheet.name)
            topogrid=re.sub('::','/external/topogrid',os.getenv('PYTHONPATH'))
            os.system(topogrid+" XPreference.matrix YPreference.matrix")


def update_activity():
    """Measure an activity map. Command called when opening an activity plot group panel.
    To be exact, just add the activity sheet_view for Sheets objects of the simulator
    """
    sim = topo.base.simulator.get_active_sim()
    for sheet in sim.objects(Sheet).values():
        activity_copy = array(sheet.activity)
        new_view = SheetView((activity_copy,sheet.bounds),
                              src_name=sheet.name,view_type='Activity')
        sheet.sheet_view_dict['Activity']=new_view
    


coordinate = (0,0)
sheet_name = ''
### JACALERT! This function, as well as update_projections have to be simplified.
### Particularly, having to retrieve the Sheet object from the sheet_name is an issue:
### It might be better to have access to the Sheet object directly rather then the name 
### in the CFSheetPlotpanels.
def update_weights():
    """
    Lambda function passed in, that will filter out all sheets
    except the one with the name being looked for.
    """
    simulator=topo.base.simulator.get_active_sim()
    sheets = simulator.objects(Sheet).values()
    x = coordinate[0]
    y = coordinate[1]
    for each in sheets:
	if (each.name == sheet_name):
            ### JCALERT! It is confusing that the method unit_view is only defined in the 
            ### CFSheet class, and that we are supposed to manipulate sheets here.
            ### also, it is supposed to return a view, but here it is used as a procedure.
	    each.update_unit_view(x,y)



proj_coords=[(0,0)]
proj_name =''
def update_projections():
    simulator=topo.base.simulator.get_active_sim()
    sheets = simulator.objects(Sheet).values()
    for each in sheets:
	if (each.name == sheet_name):
	    for x,y in proj_coords:
		each.update_unit_view(x,y,proj_name)
