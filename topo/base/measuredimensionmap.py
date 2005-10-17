"""
Distribution class

$Id$
"""




def table_creator(nested_list, list):
    
    """
    """
    
    for list in nested_list:
        for item in list:
            nested_list_resu.append(list.append(item))
    return nested_list_resu


class MeasureDimensionMap():

    """
    """

    def __init__(self, simulator,pattern_generator,generator_sheets,measured_sheet,dimension_list):
        """
        """

        self.featuremaps = dict()
        for dimension in dimension_list:
            self.featuremaps[dimension]=FeatureMap()
            
        
        self.simulator=simulator
        self.pattern_generator=pattern_generator
        self.inputs = dict().fromkeys(generator_sheets,pattern_generator)
        self.measured_sheet = measured_sheet
        



           
        
    def pattern_present_update(self, duration, stim_dim_param):

        """
        """
        
        table = [[]]
        
        for dimension in stim_dim_param.keys():
            low_bound,up_bound = stim_dim_param[dimension][0]
            step = stim_dim_param[dimension][1]
            value_list =  range(low_bound,up_bound,step)
            table = table_creator(table,value_list)
            

        for item in table:
            i=0
            j=0
            for dimension in stim_dim_param.keys():
                eval('self.pattern_generator.' + dimension + '=table[' + i + ']')
                i=i+1
                
            pattern_present(self.inputs, duration, self.simulator, False)

            for dimension in stim_dim_param.keys():
                self.prefmatrix.update(self.measured_sheet.activity,item[j])
                j=j+1

                

