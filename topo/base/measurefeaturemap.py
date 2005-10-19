"""
MeasureFeatureMap class

$Id$
"""

# CEB,JBF
# To do:
# - add sheetview after each input presentation; this will also
#   allow us to check the input patterns are as expected
# - namespace __main__, as in later comment 
# - remove temporary testing code
# - give the variables better names!
# - make variables private as appropriate
#
# - some i,j counting could probably be done better


from featuremap import FeatureMap
from sheet import Sheet
from topo.sheets.generatorsheet import GeneratorSheet

import __main__

# this is depracated - find new function
from string import capitalize

## temporary ##
from topo.patterns.basic import SineGratingGenerator
from topo.patterns.patternpresent import *
###############



## to go to topo.base.utils ##
"""
Return the cross-product of a variable number of lists (e.g. of a list of lists).

Use to obtain permutations, e.g.
l1=[a,b]
l2=[c,d]
cross_product([l1,l2]) = 
[[a,c], [a,d], [b,c], [b,d]]


From:
http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/159975
"""
# re-write so someone other than Python knows what might happen when this runs
cross_product=lambda ss,row=[],level=0: len(ss)>1 \
   and reduce(lambda x,y:x+y,[cross_product(ss[1:],row+[i],level+1) for i in ss[0]]) \
   or [row+[i] for i in ss[0]]


def frange(start, end=None, inc=None):
    """
    A range function that accepts float increments.

    Otherwise, works just as the inbuilt range() function.

    'All thoretic restrictions apply, but in practice this is
    more useful than in theory.'

    From:
    http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/66472
    """
    if end == None:
        end = start + 0.0
        start = 0.0

    if inc == None:
        inc = 1.0

    L = []
    while 1:
        next = start + len(L) * inc
        if inc > 0 and next >= end:
            break
        elif inc < 0 and next <= end:
            break
        L.append(next)
        
    return L

##############################



class MeasureFeatureMap(object):
    """
    """
    def __init__(self, simulator, feature_param):
        """
        simulator: the variable name holding the simulator from which to get the sheets.

        feature_param: a dictionary with features as keys and their parameters as values.
                       {dimension_name: (range, values, cyclic)}
                       range: the tuple (lower_bound, upper_bound)
                       values: either a list of the values to use for the feature (list), or
                                      a step size (float) to generate the list frange(lower_bound,upper_bound,values)
                       cyclic: whether or not the feature is cyclic (see topo.base.distribution)
                       e.g.    
                       {'theta': (0.0,1.0), 0.10, True}  for cyclic theta in steps of 0.10 from 0.0 to 1.0
                       {'x': (0.0,2.0), [0.0, 0.5, 0.6, 0.7, 1.0], False}  for the non-cyclic x values specified, which may
                                                                           only fall in the range [0.0,1.0].
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
                self.sheet_featuremaps[sheet].update({feature: FeatureMap(activity_matrix_dimensions=sheet.activity.shape,
                                                                          axis_range=value[0],
                                                                          cyclic=value[2])})

        # temp for testing        
        self.generator_sheets = simulator.objects(GeneratorSheet)
        self.simulator=simulator

               
    def pattern_present_update(self,input_command="pattern_present(inputs, 5.0, self.simulator, False)"):
        """
        Create a list of all permutations of the feature values, then, for each permutation, set the
        feature values in the namespace __main__ and execute the user's code (input_command) there too, updating
        the feature maps.

        Note: allows execution of arbitrary code.
        """
        input_permutations = cross_product(self.list_param)
        print input_permutations

        # just for testing
        # exec "from topo.patterns.patternpresent import pattern_present" in __main__.__dict__

        for permutation in input_permutations:
            for sheet in self.measured_sheets:
                k=0
                for feature in self.sheet_featuremaps[sheet].keys():                    
                    set_feature_variables_cmd = feature + "=" + repr(permutation[k])

                    ## temporaray - used for testing default input_command ##
                    inputs = dict().fromkeys(self.generator_sheets,SineGratingGenerator())
                    exec set_feature_variables_cmd #in __main__.__dict__
                    exec input_command #in __main__.__dict__
                 
                    self.sheet_featuremaps[sheet][feature].update(sheet.activity, permutation[k])
                    k=k+1

        for sheet in self.measured_sheets:
            for feature in self.sheet_featuremaps[sheet].keys():
                sheet.add_sheet_view(capitalize(feature)+'Preference', self.sheet_featuremaps[sheet][feature].preference())
                sheet.add_sheet_view(capitalize(feature)+'Selectivity', self.sheet_featuremaps[sheet][feature].selectivity())
            
           

            
            
