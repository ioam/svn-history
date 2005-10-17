"""
FeatureMap

** this file doesn't do anything yet **

$Id$
"""

from Numeric import array, zeros, add, Float
from distribution import Distribution



def fm_add(activity_matrix,stimulus_value):
    """
    Procedure that transforms a matrix of activity to a matrix of dictionnaries
    with a single key equal to stimulus_value

    This is used by the update FeatureMap method,and enables to simply use the __add__
    method of the Distribution class
    """
    
    new_matrix=zeros(activity_matrix.shape,'O')
    for i in range(len(activity_matrix)):
        for j in range(len(activity_matrix[i])):
                       new_matrix[i,j] = {stimulus_value:activity_matrix[i,j]}
    return new_matrix



class FeatureMap(object):
    """
    """

    def __init__(self, axis_range, cyclic, keep_peak, dim_activity_matrix):
        """
        The only attribute pf a FeatureMap is the matrix that stores the Distribution
        object associating with the activity matrix that relates to this FeatureMap

        
        """
        # get same Distribution object every time        
        # self.distribution_matrix = array([[Distribution(axis_range, cyclic, keep_peak)]*cols]*rows)

        rows, cols = dim_activity_matrix
        self.distribution_matrix = zeros(dim_activity_matrix,'O')
        for i in range(rows):
            for j in range(cols):
                self.distribution_matrix[i,j] = Distribution(axis_range,cyclic,keep_peak)
       

    def update(self, activity_matrix, stimulus_value):
        """
        """
        
        self.distribution_matrix + fm_add(activity_matrix,stimulus_value)

    def map(self):
        """
        """

        rows, cols = self.distribution_matrix.shape
        preference_matrix=zeros((rows, cols),Float) 

        # preference_matrix = self.distribution_matrix
        
        for i in range(rows):
            for j in range(cols):
                preference_matrix[i,j]=self.distribution_matrix[i,j].weighted_average()

        return preference_matrix
        
    def selectivity(self):
        """
        """

        rows, cols = self.distribution_matrix.shape
        selectivity_matrix=zeros((rows, cols),Float) 

        # preference_matrix = self.distribution_matrix
        
        for i in range(rows):
            for j in range(cols):
                selectivity_matrix[i,j]=self.distribution_matrix[i,j].selectivity()

        return selectivity_matrix
         


        

    



        



    
