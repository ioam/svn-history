"""
FeatureMap and associated functions and classes.

$Id$
"""
__version__='$Revision$'


# CEBHACKALERT: every time I have to change something in this file
# it is very painful. There are always multiple copies of the same
# thing! 
# e.g. a Simulator was being passed around but then found
# from somewhere else anyway. It was (and maybe still is?) possible
# to pass feature parameters in at too many stages.
# I have to clean it up!
# - remove temporary testing code
# - get rid of unused import statements
# - a Simulator should be passed in; this code shouldn't look for
#   active_sim

from math import pi

from Numeric import array, zeros, Float 

from topo.base import sheetview
from topo.base.sheet import Sheet
from topo.base.sheetview import SheetView
from topo.base.topoobject import TopoObject
from topo.base.utils import cross_product, frange
from topo.commands.basic import pattern_present, restore_input_generators, save_input_generators
from topo.misc.distribution import Distribution
from topo.sheets.generatorsheet import GeneratorSheet

import topo.base.simulator


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
    def __init__(self, feature_param):
        ### JABALERT: The feature_param structure is pretty
        ### complicated; surely it should be an object or something
        ### less fragile than a list assumed to have three elements as
        ### it is here.
        """
        feature_param: a dictionary with sheets as keys and a dictionary: 
                       {feature_name: (range, values, cyclic)} as values
                       
                       range: the tuple (lower_bound, upper_bound)
                       values: either a list of the values to use for the feature (list), or
                                      a step size (float) to generate the list
                                      (i.e. frange(lower_bound,upper_bound,values))
                       cyclic: whether or not the feature is cyclic (see topo.misc.distribution)

                       e.g.    
                       {'theta': (0.0,1.0), 0.10, True}
                       for cyclic theta in steps of 0.10 from 0.0 to 1.0
                       {'x': (0.0,2.0), [0.0, 0.5, 0.6, 0.7, 1.0], False}
                       for the non-cyclic x values specified, which may only fall in the range [0.0,1.0].
        """
        # CEBHACKALERT: see alert in topo/commands/basic.py about testing there is an active_sim
        self.simulator=topo.base.simulator.get_active_sim()
        
        # This dictionary will contain (for each sheet) a dictionary to hold the FeatureMap for each feature
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
                cyclic=param[2]
                self.__featurevalues.append(frange(low_bound,up_bound,step,not cyclic))

        # Sheets that have the attribure measure_maps and have it set True
        # get their maps measured.
        # CEBHACKALERT: we might want to measure the map on a sheet due
        # to a specific projection, rather than measure the map due
        # to all projections.
        # The Sheet 'learning' parameter should be per projection
        # (see alert in sheet.py), and we will have a per projection plastic
        # attribure, too.
        f = lambda x: hasattr(x,'measure_maps') and x.measure_maps
        self.__measured_sheets = filter(f,self.simulator.objects(Sheet).values())
        
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
        save_input_generators()
        
        self.__present_input_patterns(user_function,param_dict,display)
        self.__construct_sheet_views()

        restore_input_generators()


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
            user_function(self.simulator,feature_points,param_dict)


            # CEBHACKALERT: I've temporarily removed this feature,
            # i.e. plotting each pattern. There must be a better way
            # than this!
            #
            # JC: For it to work, uncomment this and pass in display=True
            # (or change display to 1 below)
            #### Debugging     ####
           #  import topo.tkgui.topoconsole 
#             from topo.plotting.templates import plotgroup_templates
#             if display:
#                temp=plotgroup_templates['Activity']
#                console = topo.tkgui.topoconsole.dict_console['console']
#                x = topo.tkgui.topoconsole.PlotsMenuEntry(console,temp)
#                panel = x.command()
#                panel.toggle_auto_refresh()
            #### Debugging end ####

            
            # NOW UPDATE EACH FEATUREMAP WITH (ACTIVITY,FEATURE_VALUE)
            for sheet in self.__measured_sheets:
                for feature,value in zip(self.__featuremaps[sheet].keys(), permutation):
                    self.__featuremaps[sheet][feature].update(sheet.activity, value)
        

    def __construct_sheet_views(self):
        for sheet in self.__measured_sheets:
            bounding_box = sheet.bounds
            
            for feature in self.__featuremaps[sheet].keys():

		### JCHACKALERT! This is temporary to avoid the positionpref plot to shrink
                ### Nevertheless we should think more about this (see alert in bitmap.py)
                ### When passing a sheet_view that is not croped to 1 in the parameter hue of hsv_to_rgb
                ### it does not work... The normalization seems to be necessary in this case.
                ### I guess it is always cyclic value that we will color with hue in an hsv plot
                ### but still we should catch the error.
                ### Also, what happens in case of negative values?
		if self.__featuremaps[sheet][feature].distribution_matrix[0,0].cyclic == True:
		    norm_factor = self.__featuremaps[sheet][feature].distribution_matrix[0,0].axis_range
		else:
		    norm_factor = 1.0

		### JCALERT! There is an hack in the for the view_name (which is only the name of the sheet)
                ### it enables the proper display in plot.py (see corresponding alert)
                ### It might have to be changed when the name display is fixed in plot.py (ask Jim)
                preference_map = SheetView(((self.__featuremaps[sheet][feature].preference())/norm_factor,
                                             bounding_box), sheet.name ,sheet.precedence)
                sheet.sheet_view_dict[feature.capitalize()+'Preference']=preference_map

                # note the temporary multiplication by 17
                # (just because I remember JAB saying it was something like that in LISSOM)
                selectivity_map = SheetView((17*self.__featuremaps[sheet][feature].selectivity(),
                                              bounding_box), sheet.name , sheet.precedence)
                sheet.sheet_view_dict[feature.capitalize()+'Selectivity']=selectivity_map









        

    



        



    
