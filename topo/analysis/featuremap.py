"""
FeatureMap and associated functions and classes.

$Id$
"""
__version__='$Revision$'


from Numeric import zeros, Float
from Numeric import array

import topo

from topo.base.sheet import Sheet
from topo.base.sheetview import SheetView
from topo.base.parameterizedobject import ParameterizedObject
from topo.misc.utils import cross_product, frange
from topo.commands.basic import restore_input_generators, save_input_generators
from topo.misc.distribution import Distribution


class FeatureMap(ParameterizedObject):
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

         

class MeasureFeatureMap(ParameterizedObject):
    """
    """
    def __init__(self, features):

        # Sheets that have the attribute measure_maps and have it set True
        # get their maps measured.
        # CEBHACKALERT: we might want to measure the map on a sheet due
        # to a specific projection, rather than measure the map due
        # to all projections.
        # The Sheet 'learning' parameter should be per projection
        # see alert in sheet.py), and we will have a per projection plastic
        # attribute, too.
	
        f = lambda x: hasattr(x,'measure_maps') and x.measure_maps
        self.__sheets_to_measure_maps_for = filter(f,topo.sim.objects(Sheet).values())
        # Add a (blank) FeatureMap for each Feature for each Sheet 
        self.__featuremaps = {}                                          
        for sheet in self.__sheets_to_measure_maps_for:
            self.__featuremaps[sheet] = {}
            for f in features:
                self.__featuremaps[sheet][f.name]=FeatureMap(sheet,axis_range=f.range,cyclic=f.cyclic)

                                                                                                                                
        
    def measure_maps(self,pattern_presenter,param_dict,features,display=False):

        """
        Create a list of all permutations of the feature values, then,
        for each permutation, set the feature values in the namespace
        __main__ and execute the user's code (input_command) there
        too, updating the feature maps.

        To make debugging easier, if display is true and there is a
        GUI open and registered in topo.guimain, asks the GUI to
        update its windows; e.g. any activity window with Auto-Refresh
        enabled will then be updated to show the activity pattern
        being tested.  This might cause problems if a preference map
        window has auto-refresh enabled. :-/
        """
	
 	topo.sim.state_push()
        save_input_generators()

        self.__present_input_patterns(pattern_presenter,param_dict,display,features)
        self.__construct_sheet_views()

        restore_input_generators()
 	topo.sim.state_pop()
	

    def __present_input_patterns(self,pattern_presenter,param_dict,features,display=False):
	
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

            if display:
                if hasattr(topo,'guimain'):
                    topo.guimain.auto_refresh()
                else:
                    self.warning("No GUI available for display.")
            
            # NOW UPDATE EACH FEATUREMAP WITH (ACTIVITY,FEATURE_VALUE)
            for sheet in self.__sheets_to_measure_maps_for:
                for feature,value in zip(feature_names, p):
                    self.__featuremaps[sheet][feature].update(sheet.activity, value)
            
            topo.sim.state_pop()

    def __construct_sheet_views(self):
	
        for sheet in self.__sheets_to_measure_maps_for:
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

                preference_map = SheetView(((self.__featuremaps[sheet][feature].preference())/norm_factor,
                                             bounding_box), sheet.name ,sheet.precedence)
                sheet.sheet_view_dict[feature.capitalize()+'Preference']=preference_map

                # note the temporary multiplication by 17
                # (just because I remember JAB saying it was something like that in LISSOM)
                selectivity_map = SheetView((17*self.__featuremaps[sheet][feature].selectivity(),
                                              bounding_box), sheet.name , sheet.precedence)
                sheet.sheet_view_dict[feature.capitalize()+'Selectivity']=selectivity_map


    ##TRALERT: The following methods were used for analysis purposes in the disparity project
    '''
    def measure_maps_modified(self,pattern_presenter,param_dict,display=False):

        save_input_generators()
        
        self.__present_input_patterns(pattern_presenter,param_dict,display)
        disp_pref,orient_pref=self.get_disp_preference()
        disp_select,orient_select=self.get_disp_selectivity()

        restore_input_generators()
        
        return disp_pref,orient_pref,disp_select,orient_select
    
    def get_disp_preference(self):

        disp=zeros([48,48],Float)
        orient=zeros([48,48],Float)
        
        for sheet in self.__measured_sheets:

            for feature in self.__featuremaps[sheet].keys():
                if feature=='disparity':

                    if self.__featuremaps[sheet][feature].distribution_matrix[0,0].cyclic == True:
                        norm_factor = self.__featuremaps[sheet][feature].distribution_matrix[0,0].axis_range
                        print 'norm_factor : ',norm_factor
                    else:
                        norm_factor = 1.0
               
                    disp=self.__featuremaps[sheet][feature].preference()*180/pi

                if feature=='orientation':

                    if self.__featuremaps[sheet][feature].distribution_matrix[0,0].cyclic == True:
                        norm_factor = self.__featuremaps[sheet][feature].distribution_matrix[0,0].axis_range
                        print 'norm_factor : ',norm_factor
                    else:
                        norm_factor = 1.0
               
                    orient=self.__featuremaps[sheet][feature].preference()*180/pi

        return disp,orient           

    def get_disp_selectivity(self):
        disp_sel=zeros([48,48],Float)
        orient_sel=zeros([48,48],Float)
        
        for sheet in self.__measured_sheets:
            for feature in self.__featuremaps[sheet].keys():
            
                if feature=='disparity':
               
                    disp_sel = self.__featuremaps[sheet][feature].selectivity()

                if feature=='orientation':
               
                    orient_sel = self.__featuremaps[sheet][feature].selectivity()
                
        return disp_sel,orient_sel 

    '''
