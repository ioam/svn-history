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
from topo.sheets.generatorsheet import GeneratorSheet
from topo.base.cf import CFSheet


class DistributionMatrix(ParameterizedObject):
    """
    Maintains a matrix of Distributions (each of which is a dictionary
    of (feature value: activity) pairs).
    
    The matrix contains one Distribution for each unit in a
    rectangular matrix (given by the matrix_shape constructor
    argument).  The contents of each Distribution can be updated for a
    given bin value all at once by providing a matrix of new values to
    update().

    The results can then be accessed as a matrix of weighted averages
    (which can be used as a preference map) and/or a selectivity
    map (which measures the peakedness of each distribution).
    """

    def __init__(self,matrix_shape,axis_range=(0.0,1.0), cyclic=False):
        self.axis_range=axis_range
        # Initialize the internal data structure: a matrix of Distribution objects.
        # It would be nice to do this using some sort of map() or apply() function...
        self.distribution_matrix = zeros(matrix_shape,'O')
        rows, cols = matrix_shape
        for i in range(rows): 
            for j in range(cols):
                self.distribution_matrix[i,j] = Distribution(axis_range,cyclic,keep_peak=True)
        
  

    def update(self, new_values, bin):
        """Add a new matrix of histogram values for a given bin value."""

        ### JABHACKALERT!  Need to override +=, not +, due to modifying argument,
        ### or else use a different function name altogether (e.g. update(x,y)).
        self.distribution_matrix + self.__make_pairs(new_values,bin)
        
        

    def __make_pairs(self,new_values,bin):
        """For a given bin, transform a matrix of values into a matrix of dictionaries {bin:element}."""
        
        new_matrix=zeros(new_values.shape,'O')
        for i in range(len(new_values)):
            for j in range(len(new_values[i])):
                new_matrix[i,j] = {bin:new_values[i,j]}
        return new_matrix
   
    

    def weighted_average(self):
        """Return the weighted average of each Distribution as a matrix."""

        weighted_average_matrix=zeros(self.distribution_matrix.shape,Float) 

        for i in range(len(weighted_average_matrix)):
            for j in range(len(weighted_average_matrix[i])):
                weighted_average_matrix[i,j]=self.distribution_matrix[i,j].weighted_average()

        return weighted_average_matrix



    def selectivity(self):
        """Return the selectivity of each Distribution as a matrix."""

        selectivity_matrix=zeros(self.distribution_matrix.shape,Float) 

        for i in range(len(selectivity_matrix)):
            for j in range(len(selectivity_matrix[i])):
                selectivity_matrix[i,j]=self.distribution_matrix[i,j].selectivity()

        return selectivity_matrix



class FeatureResponses(ParameterizedObject):
    """
    Systematically vary input pattern feature values and collate the responses.

    Each sheet has a DistributionMatrix for each feature that will be
    tested.  The DistributionMatrix stores the distribution of
    activity values for each unit in the sheet for that feature.  For
    instance, if the features to be tested are orientation and phase,
    we will create a DistributionMatrix for orientation and a
    DistributionMatrix for phase for each sheet.  The orientation and
    phase of the input are then systematically varied (when
    measure_responses is called), and the responses of each unit
    to each pattern are collected into the DistributionMatrix.

    The resulting data can then be used to plot feature maps and
    tuning curves, or for similar types of feature-based analyses.
    """
    
    # CEB: we might want to measure the map on a sheet due
    # to a specific projection, rather than measure the map due
    # to all projections.

    def __init__(self,features):
        self.initialize_featureresponses(features)
        
    def initialize_featureresponses(self,features):
        """Create an empty DistributionMatrix for each feature and each sheet."""
	self._featureresponses = {}
        for sheet in self.sheets_to_measure():
            self._featureresponses[sheet] = {}
            for f in features:
                self._featureresponses[sheet][f.name]=DistributionMatrix(sheet.shape,axis_range=f.range,cyclic=f.cyclic)


    def sheets_to_measure(self):
        """Return a list of the Sheets in the current simulation for which to collect responses."""
        return  [x for x in topo.sim.objects(Sheet).values()
                 if hasattr(x,'measure_maps') and x.measure_maps]
        

    def measure_responses(self,pattern_presenter,param_dict,features,display):
        """Present the given input patterns and collate the responses."""
        save_input_generators()

        feature_names=[f.name for f in features]
        values_lists=[f.values for f in features]
        permutations = cross_product(values_lists)
    
        for p in permutations:
            topo.sim.state_push()

            # Present input patterns
            settings = dict(zip(feature_names, p))
            pattern_presenter(settings,param_dict)

            if display:
                if hasattr(topo,'guimain'):
                    topo.guimain.refresh_activity_windows()
                else:
                    self.warning("No GUI available for display.")

                       
            # Update each DistributionMatrix with (activity,bin)
            for sheet in self.sheets_to_measure():
                for feature,value in zip(feature_names, p):
                    self._featureresponses[sheet][feature].update(sheet.activity, value)
                    
            topo.sim.state_pop()

        restore_input_generators()



class FeatureMaps(FeatureResponses):
    """
    Measures and collects the responses to a set of features for calculating feature maps.

    For each feature and each sheet, the results are stored as a
    preference matrix and selectivity matrix in the sheet's
    sheet_view_dict; these can then be plotted as preference
    or selectivity maps.
    """
    
    def __init__(self,features):
	super(FeatureMaps,self).__init__(features)
        self.features=features
        
    def collect_feature_responses(self,pattern_presenter,param_dict,display):
	self.measure_responses(pattern_presenter,param_dict,self.features,display)    
	
        for sheet in self.sheets_to_measure():
            bounding_box = sheet.bounds
            
            for feature in self._featureresponses[sheet].keys():
            ### JCHACKALERT! This is temporary to avoid the positionpref plot to shrink
            ### Nevertheless we should think more about this (see alert in bitmap.py)
            ### When passing a sheet_view that is not cropped to 1 in the parameter hue of hsv_to_rgb
            ### it does not work... The normalization seems to be necessary in this case.
            ### I guess it is always cyclic value that we will color with hue in an hsv plot
            ### but still we should catch the error.
            ### Also, what happens in case of negative values?
                if self._featureresponses[sheet][feature].distribution_matrix[0,0].cyclic == True:
                    norm_factor = self._featureresponses[sheet][feature].distribution_matrix[0,0].axis_range
                else:
                    norm_factor = 1.0
                    
                preference_map = SheetView(((self._featureresponses[sheet][feature].weighted_average())/norm_factor,
                                            bounding_box), sheet.name, sheet.precedence, topo.sim.time())
                sheet.sheet_view_dict[feature.capitalize()+'Preference']=preference_map
                
                # note the temporary multiplication by 17
                # (just because I remember JAB saying it was something like that in LISSOM)
                selectivity_map = SheetView((17*self._featureresponses[sheet][feature].selectivity(),
                                             bounding_box), sheet.name , sheet.precedence, topo.sim.time())
                sheet.sheet_view_dict[feature.capitalize()+'Selectivity']=selectivity_map


class FeatureCurves(FeatureResponses):
    """
    Measures and collects the responses to a set of features, for calculating tuning and similar curves.    

    These curves represent the response of a Sheet to patterns that
    are controlled by a set of features.  This class can collect data
    for multiple curves, each with the same x axis.  The x axis
    represents the main feature value that is being varied, such as
    orientation.  Other feature values can also be varied, such as
    contrast, which will result in multiple curves (one per unique
    combination of other feature values).

    The sheet responses used to construct the curves will be stored in
    a dictionary curve_dict kept in the Sheet of interest.  A
    particular set of patterns is then constructed using a
    user-specified PatternPresenter by adding the parameters
    determining the curve (curve_param_dict) to a static list of
    parameters (param_dict), and then varying the specified set of
    features.  The results can be accessed in the curve_dict,
    indexed by the curve_label and feature value.
    """

    def __init__(self,features,sheet,x_axis):
	super(FeatureCurves, self).__init__(features)
        self.sheet=sheet
        self.x_axis=x_axis
        sheet.curve_dict={}
        sheet.curve_dict[x_axis]={}

    def sheets_to_measure(self):
        return topo.sim.objects(CFSheet).values()

    def collect_feature_responses(self,features,pattern_presenter,param_dict,curve_label,display):
        self.initialize_featureresponses(features)
        rows,cols=self.sheet.shape
        self.measure_responses(pattern_presenter,param_dict,features,display)
        self.sheet.curve_dict[self.x_axis][curve_label]={}
        for key in self._featureresponses[self.sheet][self.x_axis].distribution_matrix[0,0]._data.iterkeys():
            y_axis_values = zeros(self.sheet.shape,'O')
            for i in range(rows):
                for j in range(cols):
                    y_axis_values[i,j] = self._featureresponses[self.sheet][self.x_axis].distribution_matrix[i,j].get_value(key)
            self.sheet.curve_dict[self.x_axis][curve_label].update({key:y_axis_values})














































































   
