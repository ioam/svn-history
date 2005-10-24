"""
MeasureFeatureMap class

$Id$
"""

# CEB,JBFC

# To do:
# - pattern_present_update should be broken up and written in an easier-to-follow way
# e.g. some i,j counting could probably be done better (using zip)
# - when creating SheetViews, pass not just "V1", but also preference, selectivity, etc.
# - namespace __main__, as in later comment 
# - remove temporary testing code
# - will go into featuremap.py
# - give the variables better names!
# - make variables private as appropriate



from featuremap import FeatureMap
from sheet import Sheet
from topo.sheets.generatorsheet import GeneratorSheet
import topo.base.topoobject
import __main__
import topo.base.registry

# this is deprecated - find new function
from string import capitalize


from sheetview import SheetView
from topo.commands.basic import pattern_present, restore_input_generators, save_input_generators

from topo.patterns.basic import GaussianGenerator, SineGratingGenerator


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

               
    def pattern_present_update(self,input_command="pattern_present(inputs, 1.0, self.simulator, learning=False)"):
        """
        Create a list of all permutations of the feature values, then, for each permutation, set the
        feature values in the namespace __main__ and execute the user's code (input_command) there too, updating
        the feature maps.

        Note: allows execution of arbitrary code.
        """
        save_input_generators(self.simulator) 

        input_permutations = cross_product(self.list_param)

        # ### for testing ###
        # this will be user's code

        # Create the input pattern
        #zed = GaussianGenerator()
        #zed.height = 0.19
        #zed.width = 0.075
        zed = SineGratingGenerator()
        zed.freq=5.0
        zed.scale=0.0606
        zed.offset=0.0        
        zed.offset=0.0
        zed.get_paramobj_dict()['theta'].min_print_level = topo.base.topoobject.DEBUG
        inputs = dict().fromkeys(self.generator_sheets,zed)

        #####################
        # Present the input pattern with various parameter settings,
        # keeping track of the responses
        for permutation in input_permutations:
            sheet=self.measured_sheets[0] # Assumes that there is at least one sheet; needs fixing
            k=0
            # SET EACH FEATURE ON THE GENERATOR
            for feature in self.sheet_featuremaps[sheet].keys():                    
                ## temporary (to change) - used for mock user's code ##
                update_generator_cmd = "zed." + feature + "=" + repr(permutation[k])
                exec update_generator_cmd                    
                k=k+1
                ## will be more like this...
                #set_feature_variables_cmd = feature + "=" + repr(permutation[k])
                #exec set_feature_variables_cmd in __main__.__dict__

            # DRAW THE PATTERN
            exec input_command #in __main__.__dict__


            # Temporary; refresh the display
            debugmode=True
            console=topo.base.registry.get_console()
            if console and debugmode:
               console.auto_refresh()
            print permutation,zed.phase,zed.theta,sum(sum(self.measured_sheets[0].activity))

            # NOW UPDATE EACH FEATUREMAP WITH (ACTIVITY,FEATURE_VALUE)
            # is this right?
            for sheet in self.measured_sheets:
                m = 0
                for feature in self.sheet_featuremaps[sheet].keys():
                    # debugging print statement
                    print 'activity for ', sheet,'[0,0], ', feature, '=', permutation[m], ':',  sheet.activity[0,0]
                    self.sheet_featuremaps[sheet][feature].update(sheet.activity, permutation[m])
                    m = m + 1

        #####################
        # Now that the feature maps have been measured, construct the plots
        for sheet in self.measured_sheets:
            bounding_box = sheet.bounds
            for feature in self.sheet_featuremaps[sheet].keys():
                
                norm_factor = self.sheet_featuremaps[sheet][feature].distribution_matrix[0,0].axis_range
                view_preference = SheetView(((self.sheet_featuremaps[sheet][feature].preference())/norm_factor,bounding_box), sheet.name)
                # note the temporary multiplication by 17 (just because I remember JAB saying it was something like that in LISSOM)
                view_selectivity = SheetView((17*self.sheet_featuremaps[sheet][feature].selectivity(),bounding_box), sheet.name)
                sheet.add_sheet_view(capitalize(feature)+'Preference', view_preference)
                sheet.add_sheet_view(capitalize(feature)+'Selectivity', view_selectivity)

        restore_input_generators(self.simulator)

         
 
