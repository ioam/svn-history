"""
MeasureFeatureMap class

$Id$
"""

from featuremap import FeatureMap
from sheet import Sheet
from topo.sheets.generatorsheet import GeneratorSheet

import __main__


# to get rid of it
from topo.patterns.basic import SineGratingGenerator
from topo.patterns.patternpresent import *


# 'If you need to generate the cross product of a variable number of lists, here is how to do it with an obscure one-liner instead of a nice and clean recursive function.' The function works on list of lists as well.
#  http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/159975
cross_product=lambda ss,row=[],level=0: len(ss)>1 \
   and reduce(lambda x,y:x+y,[cross_product(ss[1:],row+[i],level+1) for i in ss[0]]) \
   or [row+[i] for i in ss[0]]


def frange(start, end=None, inc=None):
    """A range function, that does accept float increments...


Sadly missing in the Python standard library, this function
allows to use ranges, just as the built-in function range(),
but with float arguments.

All thoretic restrictions apply, but in practice this is
more useful than in theory.

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




#def permutation_creator(permutation_list, list_param):
#    
#    """
#    """
#    if len(list_param)==0:
#        return permutation_list
#    else:
#        resu_list=[]
#        for list in permutation_list:
#            for item in list_param[0]:
#                copy_list=copy.deep_copy(list)
#                resu_list.append(copy_list.append(item))
#                list_param.pop(0)
#                print resu_list
#                permutation_creator(resu_list,list_param)
                




# "orientation": (range, feature_values, cyclic, keep_peak) 


class MeasureFeatureMap(object):

    """
    """

    def __init__(self, simulator,feature_param):
        """
    
        pattern_generator: the pattern to be presented during measurement (e.g. SineGratingGenerator)
        generator_sheets:  a list of the GeneratorSheets on which to draw the input patterns (e.g. Retina)
        measured_sheet:    the sheet that will have its feature map(s) measured (e.g. V1)
        feature_param:     {dimension_name: (range, step, cyclic)} where range is a tuple of the bounds


        featuremaps: {dimension_name: FeatureMap}
                     You can e.g. ask the FeatureMap for its map() or selectivity()

        
        
        """


        
        self.sheet_featuremaps = {}

        # the list of values to be presented for each feature
        # (e.g. for 3 values of phase and 2 of orientation, [ [0.0, 0.5, 1.0], [0.0, 1.0] ]
        self.list_param = []

        
        for param in feature_param.values():
            if isinstance(param[1],type([])):               
                self.list_param.append(param[1])
            else:
                low_bound,up_bound=param[0]
                step=param[1]
                self.list_param.append(frange(low_bound,up_bound,step))

        f= lambda x: not isinstance(x,GeneratorSheet)
        self.measured_sheets = filter(f,simulator.objects(Sheet).values())
                
        for sheet in self.measured_sheets:
            self.sheet_featuremaps[sheet] = {}
            for feature, value in feature_param.items():
                self.sheet_featuremaps[sheet].update({feature: FeatureMap(value[0], value[2], value[3],sheet.activity.shape)})


        self.simulator=simulator
        
        

        
        generator_sheets=simulator.objects(GeneratorSheet)
        
        # create the inputs dictionnary used by the pattern_present method
        # only used for testing with the default command
        self.inputs = dict().fromkeys(generator_sheets,SineGratingGenerator())

       
       
        



           
        
    def pattern_present_update(self,input_command="pattern_present(self.inputs, 5.0, self.simulator, False)"):

        """
        First create a list of all permutations of the feature values, then
        present patterns with those specified values, and finally update the
        feature maps.
        
        """

        # 
#        input_permutations = permutation_creator([[]],self.list_param)

        input_permutations = cross_product(self.list_param)
       
        for permutation in input_permutations:
            i=0
            for sheet in self.measured_sheets:
                j=0
                for feature in self.sheet_featuremaps[sheet].keys():
                    the = feature + "=" + repr(permutation[i])
                    exec the in __main__.__dict__
                    exec input_command # in __main__.__dict__
                 
           
                    self.sheet_featuremaps[sheet][feature].update(self.measured_sheets[j].activity, permutation[i])
                    j=j+1

            i=i+1

                

