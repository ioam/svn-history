"""
FeatureMap and associated functions and classes.

$Id$
"""
__version__='$Revision$'

# CEB,JBFC

# To do:
# - this file is difficult to understand!
# - remove temporary testing code
# - give the variables better names!
# - get rid of non-used import statement

from Numeric import array, zeros, Float 
from topo.base.distribution import Distribution
from topo.base.topoobject import TopoObject

from topo.base.sheet import Sheet
from topo.sheets.generatorsheet import GeneratorSheet
from topo.base.utils import cross_product, frange
from topo.base.sheetview import SheetView
from math import pi

## temporary ...? ##
from topo.patterns.basic import GaussianGenerator, SineGratingGenerator
from topo.commands.basic import pattern_present, restore_input_generators, save_input_generators

import topo.base.registry
from topo.base import sheetview
from topo.base.registry import get_console

import topo.base.simulator

## Should only import this when using display option
import topo.tkgui.topoconsole 


class SineGratingPresenter(object):
    """Function object for presenting sine gratings, for use with e.g. measure_or_pref."""
    
    def __init__(self,sim=None,apply_output_fn=True,duration=1.0):
        self.sim=sim
        self.apply_output_fn=apply_output_fn
        self.duration=duration

    def __call__(self,features_values,param_dict):
        gen = SineGratingGenerator()

        ### JABHACKALERT!  Should be able to do this more cleanly.
        for param, value in param_dict.iteritems():
            update_generator = "gen." + param + "=" + repr(value)
            exec update_generator

        for feature,value in features_values.iteritems():
            update_generator = "gen." + feature + "=" + repr(value)
            exec update_generator

        inputs = dict().fromkeys(self.sim.objects(GeneratorSheet),gen)

        pattern_present(inputs, self.duration, self.sim, learning=False,
                        apply_output_fn=self.apply_output_fn)



def measure_or_pref(sim=None,num_phase=18,num_orientation=4,frequencies=[2.4],
                    scale=0.3,offset=0.0,display=False,
                    user_function_class=SineGratingPresenter,
                    apply_output_fn=False, duration=1.0):
    """Measure orientation maps, using a sine grating by default."""

    # CEBHACKALERT:
    # Is there some way that lissom_or.ty could set the value of a variable
    # that measure_or_pref reads, so that measure_or_pref could default to
    # duration=1.0, but when LISSOM is loaded switches to 0.06?  Otherwise
    # people playing around with CFSOM will think it doesn't work for
    # orientation maps...

    
    if not sim:
        sim = topo.base.simulator.get_active_sim()

    if sim:

        if num_phase <= 0 or num_orientation <= 0:
            raise ValueError("num_phase and num_orientation must be greater than 0")
            
        else:
            user_function=user_function_class(sim,apply_output_fn, duration)
            step_phase=2*pi/num_phase
            step_orientation=pi/num_orientation
        
            feature_values = {"orientation": ( (0.0,pi), step_orientation, True),
                              "phase": ( (0.0,2*pi),step_phase,True),
                              "frequency": ((min(frequencies),max(frequencies)),frequencies,False)}

            x=MeasureFeatureMap(sim,feature_values)

            param_dict = {"scale":scale,"offset":offset}
            
            x.measure_maps(user_function, param_dict, display)

    else:
        TopoObject().warning('No active Simulator.')


def measure_activity():
    """Measure an activity map. Command called when opening an activity plot group panel.
    To be exact, just add the activity sheet_view for Sheets objects of the simulator
    """
    simulator = topo.base.simulator.get_active_sim()
    for sheet in simulator.objects(Sheet).values():
        activity_copy = array(sheet.activity)
        new_view = sheetview.SheetView((activity_copy,sheet.bounds),
                                        src_name=sheet.name,view_type='Activity')
        sheet.add_sheet_view('Activity',new_view)
    


class FeatureMap(TopoObject):
    """
    A feature map for one stimulus dimension (e.g. Orientation) for one Sheet.

    Given a set of activity matrices and associated parameter values,
    constructs a preference map and a selectivity map for that parameter.
    """

    

    def __init__(self, sheet, axis_range=(0.0,1.0), cyclic=False):
        
        # Initialize the internal data structure: a matrix of Distribution objects.
        # It would be nice to do this using some sort of map() or apply() function...
        rows, cols = sheet.activity.shape
        self.distribution_matrix = zeros(sheet.activity.shape,'O')
        for i in range(rows):
            for j in range(cols):
                self.distribution_matrix[i,j] = Distribution(axis_range,cyclic,keep_peak=True)
       

    def update(self, activity_matrix, feature_value):
        """Add a new matrix of activity values for a given stimulus value."""
        
        ### JABHACKALERT!  Need to override +=, not +, due to modifying argument,
        ### or else use a different function name altogether (e.g. update(x,y)).
        self.distribution_matrix + self.__make_pairs(activity_matrix,feature_value)


    def __make_pairs(self,activity_matrix,feature_value):
        """
        Transform an activity matrix to a matrix of dictionaries {feature_value:element}.
    
        Private method for use with the __add__ method of the Distribution class.
        """
        
        new_matrix=zeros(activity_matrix.shape,'O')
        for i in range(len(activity_matrix)):
            for j in range(len(activity_matrix[i])):
                           new_matrix[i,j] = {feature_value:activity_matrix[i,j]}
        return new_matrix


    def preference(self):
        """Return the preference map for this feature as a matrix."""

        rows, cols = self.distribution_matrix.shape
        preference_matrix=zeros((rows, cols),Float) 

        for i in range(rows):
            for j in range(cols):
                preference_matrix[i,j]=self.distribution_matrix[i,j].weighted_average()

        return preference_matrix
        

    def selectivity(self):
        """Return the selectivity map for this feature as a matrix."""

        rows, cols = self.distribution_matrix.shape
        selectivity_matrix=zeros((rows, cols),Float) 

        for i in range(rows):
            for j in range(cols):
                selectivity_matrix[i,j]=self.distribution_matrix[i,j].selectivity()

        return selectivity_matrix

         

class MeasureFeatureMap(TopoObject):
    """
    """
    def __init__(self, simulator, feature_param):
        """
        simulator: the variable name holding the simulator from which to get the sheets.

        feature_param: a dictionary with sheets as keys and a dictionnary: 
                       {feature_name: (range, values, cyclic)} as values
                       
                       range: the tuple (lower_bound, upper_bound)
                       values: either a list of the values to use for the feature (list), or
                                      a step size (float) to generate the list
                                      (i.e. frange(lower_bound,upper_bound,values))
                       cyclic: whether or not the feature is cyclic (see topo.base.distribution)

                       e.g.    
                       {'theta': (0.0,1.0), 0.10, True}
                       for cyclic theta in steps of 0.10 from 0.0 to 1.0
                       {'x': (0.0,2.0), [0.0, 0.5, 0.6, 0.7, 1.0], False}
                       for the non-cyclic x values specified, which may only fall in the range [0.0,1.0].
        """
        self.simulator=simulator

        # This dictionary will contains (for each sheet) a dictionary to hold the FeatureMap for each feature
        # {sheet: {feature: FeatureMap()}}
        self.__featuremaps = {}

        # the list of (list of) values to be presented for each feature
        self.__featurevalues = []
        
        for param in feature_param.values():
            # param can be either list or float (a step size)
            if isinstance(param[1],type([])):               
                self.__featurevalues.append(param[1])
            else:
                low_bound,up_bound = param[0]
                step=param[1]
                self.__featurevalues.append(frange(low_bound,up_bound,step))

        # all the sheets that will have their feature maps measured
        # (i.e. all Sheets that aren't GeneratorSheets)
        f = lambda x: not isinstance(x,GeneratorSheet)
        self.__measured_sheets = filter(f,simulator.objects(Sheet).values())
        
        # now create the featuremaps for each sheet    
        for sheet in self.__measured_sheets:
            self.__featuremaps[sheet] = {}
            for feature, value in feature_param.items():
                self.__featuremaps[sheet].update({feature: FeatureMap(sheet,
                                                                          axis_range=value[0],
                                                                          cyclic=value[2])})

                
    def measure_maps(self,user_function,param_dict,display=False):

        """
        Create a list of all permutations of the feature values, then, for each permutation, set the
        feature values in the namespace __main__ and execute the user's code (input_command) there too, updating
        the feature maps.

        Note: allows execution of arbitrary code.
        """
        save_input_generators(self.simulator)
        
        self.__present_input_patterns(user_function,param_dict,display)
        self.__construct_sheet_views()

        restore_input_generators(self.simulator)


    def __present_input_patterns(self,user_function,param_dict,display=False):
        input_permutations = cross_product(self.__featurevalues)

        # Present the input pattern with various parameter settings,
        # keeping track of the responses
        for permutation in input_permutations:
            sheet=self.__measured_sheets[0] # Assumes that there is at least one sheet; needs fixing
            feature_points={}

            # set each feature's value
            for feature,value in zip(self.__featuremaps[sheet].keys(), permutation):
                feature_points[feature] = value

            # DRAW THE PATTERN: call to the user_function
            user_function(feature_points,param_dict)


            #### Debugging     ####
            if display:
                temp=topo.base.registry.plotgroup_templates['Activity']
                x = topo.tkgui.topoconsole.PlotsMenuEntry(get_console(),temp)
                panel = x.command()
                panel.toggle_auto_refresh()
            
            #### Debugging end ####


            
            # NOW UPDATE EACH FEATUREMAP WITH (ACTIVITY,FEATURE_VALUE)
            for sheet in self.__measured_sheets:
                for feature,value in zip(self.__featuremaps[sheet].keys(), permutation):
                    self.__featuremaps[sheet][feature].update(sheet.activity, value)
        

    def __construct_sheet_views(self):
        for sheet in self.__measured_sheets:
            bounding_box = sheet.bounds
            
            for feature in self.__featuremaps[sheet].keys():

                norm_factor = self.__featuremaps[sheet][feature].distribution_matrix[0,0].axis_range
		### JCALERT! There is an hack in the for the view_name (which is only the name of the sheet)
                ### it enables the proper display in plot.py (see corresponding alert)
                ### It might have to be changed when the name display is fixed in plot.py (ask Jim)
                preference_map = SheetView(((self.__featuremaps[sheet][feature].preference())/norm_factor,
                                             bounding_box), sheet.name )
                sheet.add_sheet_view(feature.capitalize()+'Preference', preference_map)

                # note the temporary multiplication by 17
                # (just because I remember JAB saying it was something like that in LISSOM)
                selectivity_map = SheetView((17*self.__featuremaps[sheet][feature].selectivity(),
                                              bounding_box), sheet.name )
                sheet.add_sheet_view(feature.capitalize()+'Selectivity', selectivity_map)









        

    



        



    
