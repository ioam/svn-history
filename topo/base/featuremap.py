"""
FeatureMap

** this file doesn't do anything yet **

Id: distribution.py,v 1.4 2005/10/13 15:11:36 ceball Exp $
"""

from Numeric import array 

class FeatureMap(object):
"""
"""

    def __init__(self, activity_matrix, cyclic, axis_range, keep_peak):
        """
        """
        distribution_matrix=[[]]
        for i in activity_matrix:
            distribution_matrix.append([])
            for j in activity_matrix:
                item = distribution(axis_range, cyclic, keep_peak)
                distribution_matrix[i].append


    def update(self, activity_matrix, stimulus_value):
        """
        """
        for i in activity_matrix:
            for j in activity_matrix:
                self.distribution_matrix[].add({stimulus_value:activity_matrix[i,j]})

        

    



        



    
