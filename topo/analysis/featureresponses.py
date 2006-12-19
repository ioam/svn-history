"""
FeatureResponses and associated functions and classes.

$Id$
"""
__version__='$Revision$'


from Numeric import zeros, Float
from Numeric import array

import topo
import topo.base.sheetcoords

from topo.base.sheet import Sheet
from topo.base.sheetview import SheetView
from topo.base.parameterizedobject import ParameterizedObject
from topo.misc.utils import cross_product, frange
from topo.base.sheetcoords import SheetCoordinateSystem
from topo.commands.basic import restore_input_generators, save_input_generators
from topo.misc.distribution import Distribution


class DistributionMatrix(ParameterizedObject):
    """
    Given the required shape, initializes a distribution_matrix
    which is a matrix of Distributions (a dictionary of (feature value: activity) pairs)
    Then stores the Distribution of activity values for each unit in the sheet for
    one stimulus dimension (e.g. Orientation) for one Sheet in the distribution_matrix.

    Can then construct the matrix of weighted averages (preference map)
    and a selectivity map for that parameter from the distribution_matrix.
    """


    def __init__(self,sheet_shape,axis_range=(0.0,1.0), cyclic=False):
        self.axis_range=axis_range
        # Initialize the internal data structure: a matrix of Distribution objects.
        # It would be nice to do this using some sort of map() or apply() function...
        self.distribution_matrix = zeros(sheet_shape,'O')
        rows, cols = sheet_shape
        for i in range(rows): 
            for j in range(cols):
                self.distribution_matrix[i,j] = Distribution(axis_range,cyclic,keep_peak=True)
        
  

    def update(self, new_values, feature_value):
        """Add a new matrix of values for a given stimulus value."""
        
        ### JABHACKALERT!  Need to override +=, not +, due to modifying argument,
        ### or else use a different function name altogether (e.g. update(x,y)).
        self.distribution_matrix + self.__make_pairs(new_values,feature_value)
        
        

    def __make_pairs(self,new_values,feature_value):
        """
        Transform an activity matrix to a matrix of dictionaries {feature_value:element}.
    
        Private method for use with the __add__ method of the Distribution class.
        """
        
        new_matrix=zeros(new_values.shape,'O')
        for i in range(len(new_values)):
            for j in range(len(new_values[i])):
                new_matrix[i,j] = {feature_value:new_values[i,j]}
        return new_matrix
   
    

    def weighted_average(self):
        """Return the weighted average of the distribution matrix as a matrix."""

        weighted_average_matrix=zeros(self.distribution_matrix.shape,Float) 

        for i in range(len(weighted_average_matrix)):
            for j in range(len(weighted_average_matrix[i])):
                weighted_average_matrix[i,j]=self.distribution_matrix[i,j].weighted_average()

        return weighted_average_matrix



    def selectivity(self):
        """Return the selectivity for the distribution matrix as a matrix."""

        selectivity_matrix=zeros(self.distribution_matrix.shape,Float) 

        for i in range(len(selectivity_matrix)):
            for j in range(len(selectivity_matrix[i])):
                selectivity_matrix[i,j]=self.distribution_matrix[i,j].selectivity()

        return selectivity_matrix

class FeatureResponses(ParameterizedObject):
    """
    Systematically varies input pattern feature values and collates the responses.

    Each sheet has a DistributionMatrix for each feature that will be
    tested.  The DistributionMatrix stores the distribution of
    activity values for each unit in the sheet for that feature.  For
    instance, if the features to be tested are orientation and phase,
    we will create a DistributionMatrix for orientation and a
    DistributionMatrix for phase for each sheet.  The orientation and
    phase of the input are then systematically varied (when
    present_input_patterns is called), and the responses of each unit
    to each pattern are collected into the DistributionMatrix.

    The resulting data can then be used to plot feature maps and
    tuning curves, or for similar types of feature-based analyses.
    """
    
    def __init__(self,features):

        # Sheets that have the attribute measure_maps and have it set True
        # get their maps measured.
        # CEBHACKALERT: we might want to measure the map on a sheet due
        # to a specific projection, rather than measure the map due
        # to all projections.
        # The Sheet 'learning' parameter should be per projection
        # see alert in sheet.py), and we will have a per projection plastic
        # attribute, too.
        f = lambda x: hasattr(x,'measure_maps') and x.measure_maps
        self._sheets_to_measure_maps_for = filter(f,topo.sim.objects(Sheet).values())
	self._featureresponses = {}
        for sheet in self._sheets_to_measure_maps_for:
            self._featureresponses[sheet] = {}
            for f in features:
                self._featureresponses[sheet][f.name]=DistributionMatrix(sheet.shape,axis_range=f.range,cyclic=f.cyclic)
    

    def measure_responses(self,pattern_presenter,param_dict,features,display):
 
        topo.sim.state_push()
        save_input_generators()
        self.__present_input_patterns(pattern_presenter,param_dict, features,display)
        restore_input_generators()
        topo.sim.state_pop()
        
    def __present_input_patterns(self,pattern_presenter,param_dict,features,display):
	
        feature_names=[f.name for f in features]
        values_lists=[f.values for f in features]
        permutations = cross_product(values_lists)
        
        
        # Present the input pattern with various parameter settings,
        # keeping track of the responses
    
        for p in permutations:
            topo.sim.state_push() 

            settings = dict(zip(feature_names, p))

            # DRAW THE PATTERN: call to the pattern_presenter
            pattern_presenter(settings,param_dict)
            self.isfirst=False

            if display:
                if hasattr(topo,'guimain'):
                    topo.guimain.auto_refresh()
                else:
                    self.warning("No GUI available for display.")
            
            # NOW UPDATE EACH FEATUREMAP WITH (ACTIVITY,FEATURE_VALUE)
            for sheet in self._sheets_to_measure_maps_for:
                for feature,value in zip(feature_names, p):
                    self._featureresponses[sheet][feature].update(sheet.activity, value)              
        
                    
            topo.sim.state_pop()


class FeatureMaps(FeatureResponses):
    """
    Measures and collects the responses to the required features and stores the preference matrix 
    and selectivity matrix for each sheet for each feature in the sheet_view_dict. 
    """
    
    def __init__(self,features):
	super(FeatureMaps,self).__init__(features)
        self.features=features
        
    def collect_feature_responses(self,pattern_presenter,param_dict,display):
	self.measure_responses(pattern_presenter,param_dict,self.features,display)    
	
        for sheet in self._sheets_to_measure_maps_for:
            bounding_box = sheet.bounds
            
            for feature in self._featureresponses[sheet].keys():
            ### JCHACKALERT! This is temporary to avoid the positionpref plot to shrink
            ### Nevertheless we should think more about this (see alert in bitmap.py)
            ### When passing a sheet_view that is not croped to 1 in the parameter hue of hsv_to_rgb
            ### it does not work... The normalization seems to be necessary in this case.
            ### I guess it is always cyclic value that we will color with hue in an hsv plot
            ### but still we should catch the error.
            ### Also, what happens in case of negative values?
                if self._featureresponses[sheet][feature].distribution_matrix[0,0].cyclic == True:
                    norm_factor = self._featureresponses[sheet][feature].distribution_matrix[0,0].axis_range
                else:
                    norm_factor = 1.0
                    
                preference_map = SheetView(((self._featureresponses[sheet][feature].weighted_average())/norm_factor,
                                            bounding_box), sheet.name ,sheet.precedence)
                sheet.sheet_view_dict[feature.capitalize()+'Preference']=preference_map
                
                # note the temporary multiplication by 17
                # (just because I remember JAB saying it was something like that in LISSOM)
                selectivity_map = SheetView((17*self._featureresponses[sheet][feature].selectivity(),
                                             bounding_box), sheet.name , sheet.precedence)
                sheet.sheet_view_dict[feature.capitalize()+'Selectivity']=selectivity_map

















































































   
