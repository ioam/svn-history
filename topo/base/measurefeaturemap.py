"""
MeasureFeatureMap class

$Id$
"""

# CEB,JBFC

# To do:
# - pattern_present_update should be broken up and written in an easier-to-follow way
# e.g. some i,j counting could probably be done better (using zip)
# - when creating SheetViews, pass not just "V1", but also preference, selectivity, etc.
# - namespace __main__, as in later comment 
# - remove temporary testing code
# - will go into featuremap.py
# - give the variables better names!
# - make variables private as appropriate

import topo.base.topoobject
import __main__
import topo.base.registry

from featuremap import FeatureMap
from sheet import Sheet
from topo.sheets.generatorsheet import GeneratorSheet
from topo.base.utils import cross_product, frange
from sheetview import SheetView

# this is deprecated - find new function
from string import capitalize

## temporary ##
from topo.patterns.basic import GaussianGenerator, SineGratingGenerator
from topo.commands.basic import pattern_present, restore_input_generators, save_input_generators
###############

def sinegrating_present(features_values,sim):
    """
    Intermediate user function used by MeasureFeatureMap
    """
    zed = SineGratingGenerator()
    zed.freq=5.0
    zed.scale=0.0606
    zed.offset=0.0        
    inputs = dict().fromkeys(sim.objects(GeneratorSheet),zed)

    # Temporary: kept that in case we neeed it again
    #zed.get_paramobj_dict()['theta'].min_print_level = topo.base.topoobject.DEBUG
    # print zed.phase, zed.theta

    for feature,value in features_values.iteritems():
        update_generator = "zed." + feature + "=" + repr(value)
        exec update_generator

    pattern_present(inputs, 1.0, sim, learning=False)
         


class MeasureFeatureMap(object):
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
        # This dictionary will, for each sheet, contain a dictionary to hold the FeatureMap for each feature
        # {sheet: {feature: FeatureMap()}}
        self.sheet_featuremaps = {}

        # the list of values to be presented for each feature
        self.list_param = []

        # build self.list_param from the input feature_param
        for param in feature_param.values():
            if isinstance(param[1],type([])):               
                self.list_param.append(param[1])
            else:
                low_bound,up_bound=param[0]
                step=param[1]
                self.list_param.append(frange(low_bound,up_bound,step))

        # find all the sheets that will have their feature maps measured (i.e. all Sheets that aren't GeneratorSheets)

        f= lambda x: not isinstance(x,GeneratorSheet)
        self.measured_sheets = filter(f,simulator.objects(Sheet).values())
        
        # now create the featuremaps for each sheet  
        for sheet in self.measured_sheets:
            self.sheet_featuremaps[sheet] = {}
            for feature, value in feature_param.items():
                self.sheet_featuremaps[sheet].update({feature: FeatureMap(sheet,
                                                                          axis_range=value[0],
                                                                          cyclic=value[2])})
        
        self.generator_sheets = simulator.objects(GeneratorSheet)
        self.simulator=simulator

               

    def pattern_present_update(self,user_function):

        """
        Create a list of all permutations of the feature values, then, for each permutation, set the
        feature values in the namespace __main__ and execute the user's code (input_command) there too, updating
        the feature maps.

        Note: allows execution of arbitrary code.
        """
        save_input_generators(self.simulator) 

        input_permutations = cross_product(self.list_param)

      
        # Present the input pattern with various parameter settings,
        # keeping track of the responses
        for permutation in input_permutations:
            sheet=self.measured_sheets[0] # Assumes that there is at least one sheet; needs fixing
            param_dict={}
            k=0
            # SET EACH FEATURE ON THE GENERATOR
            for feature in self.sheet_featuremaps[sheet].keys():                    
             
                param_dict[feature]=permutation[k]
                k=k+1
                
            # DRAW THE PATTERN: call to the user_function
            user_function(param_dict,self.simulator)
            
            # Temporary; refresh the display
            debugmode=True
            console=topo.base.registry.get_console()
            if console and debugmode:
               console.auto_refresh()
            

            # NOW UPDATE EACH FEATUREMAP WITH (ACTIVITY,FEATURE_VALUE)
            for sheet in self.measured_sheets:
                m = 0
                for feature in self.sheet_featuremaps[sheet].keys():
                    # Temporary: debugging print statement
                    # print 'activity for ', sheet,'[0,0], ', feature, '=', permutation[m], ':',  sheet.activity[0,0]
                    self.sheet_featuremaps[sheet][feature].update(sheet.activity, permutation[m])
                    m = m + 1

        # Now that the feature maps have been measured, construct the plots
        for sheet in self.measured_sheets:
            bounding_box = sheet.bounds
            for feature in self.sheet_featuremaps[sheet].keys():
                
                norm_factor = self.sheet_featuremaps[sheet][feature].distribution_matrix[0,0].axis_range
                view_preference = SheetView(((self.sheet_featuremaps[sheet][feature].preference())/norm_factor,bounding_box), sheet.name + "_" + capitalize(feature)+'Preference')
                # note the temporary multiplication by 17 (just because I remember JAB saying it was something like that in LISSOM)
                view_selectivity = SheetView((17*self.sheet_featuremaps[sheet][feature].selectivity(),bounding_box), sheet.name + "_" + capitalize(feature)+'Selectivity')
                sheet.add_sheet_view(capitalize(feature)+'Preference', view_preference)
                sheet.add_sheet_view(capitalize(feature)+'Selectivity', view_selectivity)

        restore_input_generators(self.simulator)



         
