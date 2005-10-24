"""
FeatureMap class.

$Id$
"""

from Numeric import array, zeros, Float 
from distribution import Distribution
from topoobject import TopoObject


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
         




        

    



        



    
