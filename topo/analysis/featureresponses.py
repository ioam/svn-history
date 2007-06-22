"""
FeatureResponses and associated functions and classes.

$Id$
"""
__version__='$Revision$'


import time
import copy
from math import fmod,floor

from numpy import zeros, array
from numpy.oldnumeric import Float

import topo
import topo.base.sheetcoords
from topo.base.sheet import Sheet, activity_type
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
#                weighted_average_matrix[i,j]=self.distribution_matrix[i,j].estimated_maximum()               
                           

        return weighted_average_matrix
        
        
    def max_value_bin(self):
        """Return the bin with the max value of each Distribution as a matrix."""

        max_value_bin_matrix=zeros(self.distribution_matrix.shape,Float)
            
        for i in range(len(max_value_bin_matrix)):
            for j in range(len(max_value_bin_matrix[i])):           
                max_value_bin_matrix[i,j]=self.distribution_matrix[i,j].max_value_bin()                             

        return max_value_bin_matrix
        
        

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

        refresh_act_wins=False
        if display:
            if hasattr(topo,'guimain'):
                refresh_act_wins=True
            else:
                self.warning("No GUI available for display.")


        # CEB: currently working here
        
        def m(permutation):
            topo.sim.state_push()

            # Present input patterns
            settings = dict(zip(feature_names, permutation))
            pattern_presenter(settings,param_dict)

            if refresh_act_wins:topo.guimain.refresh_activity_windows()
                    
            # Update each DistributionMatrix with (activity,bin)
            for sheet in self.sheets_to_measure():
                for feature,value in zip(feature_names, permutation):
                    self._featureresponses[sheet][feature].update(sheet.activity, value)

            topo.sim.state_pop()


            
        timer = copy.copy(topo.sim.timer)
        # CEBHACKALERT: hack to work round timer pickling hack
        timer.receive_messages=topo.sim.timer.receive_messages
        timer.receive_progress=topo.sim.timer.receive_progress
        ######################################################
        timer.func = m
        timer.X(permutations)

        restore_input_generators()



### JABALERT: This class needs significant cleanup:
### 1. The timing code should be moved out of here and the other places it appears
### 
### 2. This class should calculate RFs for all units in all sheets for which
###    measure_maps is true, rather than being hardcoded to "V1"
###
### 3. This class should have some sort of parameter for specifying the name
###    of the input region, rather than being hardcoded to "Retina"
###
### 4. The plotting code at the end should mostly be eliminated, and replaced
###    with a separate command (called from the 'Receptive Fields*' pgts in
###    topo/commands/analysis.py instead of from here), sharing the implementation
###    of topographic_grid (because that's what is intended to be visualized here).

grid=[]

class ReverseCorrelation(ParameterizedObject):
    """
    Calculate the receptive fields for all neurons using reverse correlation.
    """
    
    def measure_responses(self,pattern_presenter,param_dict,features,display):
        """Present the given input patterns and collate the responses."""
         
        # JABALERT: The grid data structure should be a matrix of 2D matrices,
        # not a nested list.
        global grid
        rows, cols = topo.sim["V1"].activity.shape
        for iiii in range(rows):
            row = []        
            for jjjj in range(cols):
                row.append(0*topo.sim["Retina"].activity)
            grid.append(row)

     
        save_input_generators()

        feature_names=[f.name for f in features]
        values_lists=[f.values for f in features]
        permutations = cross_product(values_lists)

        ### JABHACKALERT: This timer code should be moved to its own object;
        ### it is much too difficult to follow here (and in tkgui/topoconsole.py).
################## timer part 1        
        
        i=0
        fduration = len(permutations)
        step   = 1.0
        iters  = int(floor(fduration/step))
        remain = fmod(fduration, step)
        starttime=time.time()
        recenttimes=[]

        # Temporary:
 #       self.parent.title(topo.sim.name) ## this changes the title bar to more useful

        ## Duration of most recent times from which to estimate remaining time
        estimate_interval=50.0        

#################### end of timer part 1    
    
        for p in permutations:
            topo.sim.state_push()

            # Present input patterns
            settings = dict(zip(feature_names, p))
            pattern_presenter(settings,param_dict)
                                        
  ##################### timer part 2

      #  for i in xrange(iters):
            i=i+1
            recenttimes.append(time.time())
            length = len(recenttimes)

            if (length>50):
                recenttimes.pop(0)
                length-=1
 #       topo.sim.run(step)
            percent = 100.0*i/iters
#            print percent,i
            estimate = (iters-i)*(recenttimes[-1]-recenttimes[0])/length
            # CEBALERT: when there are multiple sheets, this can make it seem
            # like topographica's stuck in a loop (because the counter goes
            # to 100% lots of times...e.g. hierarchical's orientation tuning fullfield.
            message = 'Time ' + str(topo.sim.time()) + ': ' + \
                      str(int(percent)) + '% of '  + str(fduration) + ' patterns completed ' + \
                      ('(%02d' % int(estimate/60))+':' + \
                      ('%02d' % int(estimate%60))+ ' remaining).'
                      
            if hasattr(topo,'guimain'):
                topo.guimain.messageBar.message('state', message)
                topo.guimain.update()
            
######################### end of timer              

            if display:
                if hasattr(topo,'guimain'):
                    topo.guimain.refresh_activity_windows()
                else:
                    self.warning("No GUI available for display.")

            for ii in range(rows): 
                for jj in range(cols):
                    grid[ii][jj]=grid[ii][jj]+topo.sim["V1"].activity[ii,jj]*(topo.sim["Retina"].activity)
  
            topo.sim.state_pop()

        restore_input_generators()

        ### JABALERT: The remaining code should move into a separate command in
        ### topo/commands/pylabplots.py, and it should be changed to
        ### use the code from topographic_grid (because that's what
        ### is intended to be visualized here).
        import matplotlib
        matplotlib.use('TkAgg')
        import pylab
        from numpy import fabs
        from topo.base.arrayutils import centroid

        xx=[]
        yy=[]  
        for iii in range(rows): 
            for jjj in range(cols):
                # The abs() ensures the centroid is taken over both 
                # positive and negative correlations
                xxx,yyy = centroid(fabs(grid[iii][jjj]))
                xx.append(xxx)
                yy.append(yyy)
    
        pylab.scatter(xx,yy)
        pylab.show._needmain = False
        pylab.show()


                          
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
        
    def collect_feature_responses(self,pattern_presenter,param_dict,display,weighted_average=True):
        """
        Present the given input patterns and collate the responses.

        If weighted_average is True, the feature responses are
        calculated from a weighted average of the values of each bin
        in the distribution, rather than simply using the actual value
        of the parameter for which response was maximal (the discrete
        method).  Such a computation will generally produce much more
        precise maps using fewer test stimuli than the discrete
        method.  However, weighted_average methods generally require
        uniform and full-range sampling, as described below, which is
        not always feasible.

        For measurements at evenly-spaced intervals over the full
        range of possible parameter values, weighted_averages are a
        good measure of the underlying continuous-valued parameter
        preference, assuming that neurons are tuned broadly enough
        (and/or sampled finely enough) that they respond to at least
        two of the tested parameter values.  This method will not
        usually give good results when those criteria are not met,
        i.e. if the sampling is too sparse, not at evenly-spaced
        intervals, or does not cover the full range of possible
        values.  In such cases weighted_average should be set to
        False, and the number of test patterns will usually need
        to be increased instead.
        """
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
                    
                if weighted_average==True:
                    preference_map = SheetView(((self._featureresponses[sheet][feature].weighted_average())/norm_factor,
                                                bounding_box), sheet.name, sheet.precedence, topo.sim.time())
                else:
                    preference_map = SheetView(((self._featureresponses[sheet][feature].max_value_bin())/norm_factor,
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
        if hasattr(sheet, "curve_dict")==False:
            sheet.curve_dict={}
        sheet.curve_dict[x_axis]={}

    def sheets_to_measure(self):
        return topo.sim.objects(CFSheet).values()

    def collect_feature_responses(self,features,pattern_presenter,param_dict,curve_label,display):
        self.initialize_featureresponses(features)
        rows,cols=self.sheet.shape
        bounding_box = self.sheet.bounds
        self.measure_responses(pattern_presenter,param_dict,features,display)
        self.sheet.curve_dict[self.x_axis][curve_label]={}
        for key in self._featureresponses[self.sheet][self.x_axis].distribution_matrix[0,0]._data.iterkeys():
            y_axis_values = zeros(self.sheet.shape,activity_type)
            for i in range(rows):
                for j in range(cols):
                    y_axis_values[i,j] = self._featureresponses[self.sheet][self.x_axis].distribution_matrix[i,j].get_value(key)
            Response = SheetView((y_axis_values,bounding_box), self.sheet.name , self.sheet.precedence, topo.sim.time())
            self.sheet.curve_dict[self.x_axis][curve_label].update({key:Response})

