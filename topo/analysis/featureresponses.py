"""
FeatureResponses and associated functions and classes.

These classes implement map and tuning curve measurement based
on measuring responses while varying features of an input pattern.

$Id$
"""
__version__='$Revision$'


import time
import copy

from math import fmod,floor,pi
from colorsys import hsv_to_rgb

import numpy
from numpy import zeros, array, empty, object_, size, vectorize, fromfunction
from numpy.oldnumeric import Float

from .. import param
from ..param.parameterized import ParameterizedFunction, ParamOverrides

import topo
import topo.base.sheetcoords
from topo.base.arrayutil import wrap
from topo.base.cf import CFSheet
from topo.base.functionfamily import PatternDrivenAnalysis 
from topo.base.sheet import Sheet, activity_type
from topo.base.sheetcoords import SheetCoordinateSystem
from topo.base.sheetview import SheetView
from topo.command.basic import pattern_present,restore_input_generators, save_input_generators
from topo.command.basic import wipe_out_activity, clear_event_queue
from topo.misc.distribution import Distribution
from topo.misc.util import cross_product, frange
from topo.pattern.basic import SineGrating, Gaussian, Rectangle
from topo.pattern.teststimuli import SineGratingDisk, OrientationContrastPattern, SineGratingRectangle
from topo.plotting.plotgroup import plotgroups,default_input_sheet,default_measureable_sheet
from topo.sheet import GeneratorSheet



# CB: having a class called DistributionMatrix with an attribute
# distribution_matrix to hold the distribution matrix seems silly.
# Either rename distribution_matrix or make DistributionMatrix into
# a matrix.
class DistributionMatrix(param.Parameterized):
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
        """Initialize the internal data structure: a matrix of Distribution objects."""
        self.axis_range=axis_range
        new_distribution = vectorize(lambda x: Distribution(axis_range,cyclic,True),
                                     doc="Return a Distribution instance for each element of x.")
        self.distribution_matrix = new_distribution(empty(matrix_shape))

  

    def update(self, new_values, bin):
        """Add a new matrix of histogram values for a given bin value."""
        ### JABHACKALERT!  The Distribution class should override +=,
        ### rather than + as used here, because this operation
        ### actually modifies the distribution_matrix, but that has
        ### not yet been done.  Alternatively, it could use a different
        ### function name altogether (e.g. update(x,y)).
        self.distribution_matrix + fromfunction(vectorize(lambda i,j: {bin:new_values[i,j]}),
                                                new_values.shape)  
            

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



class FullMatrix(param.Parameterized):
    """
    Records the output of every unit in a sheet, for every combination of feature values.
    Useful for collecting data for later analysis while presenting many input patterns.
    """

    def __init__(self,matrix_shape,features):
        self.matrix_shape = matrix_shape
        self.features = features
        self.dimensions = ()
        for f in features:
            self.dimensions = self.dimensions + (size(f.values),)
        self.full_matrix = empty(self.dimensions,object_)


    def update(self, new_values, feature_value_permutation):
        """Add a new matrix of histogram values for a given bin value."""
        index = ()
        for f in self.features:
            for ff,value in feature_value_permutation:
                if(ff == f.name):
                    index = index + (f.values.index(value),)
        self.full_matrix[index] = new_values




# CB: FeatureResponses and ReverseCorrelation need cleanup; I began but haven't finished.
# JABALERT: At least:
# - Move features out of __init__ and into measure_responses
# - Change measure_responses to __call__, as it's the only thing this
#   class really does
# - Make the other methods private (_) since they are for internal use
# - Possibly -- make the __call__ methods have the same signature?
# - Clean up the inheritance hierarchy?


class FeatureResponses(PatternDrivenAnalysis):
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

    def __init__(self,features,**params):
        super(FeatureResponses,self).__init__(**params)
        self.initialize_featureresponses(features)
        self.before_analysis_session.append(save_input_generators)
        self.before_pattern_presentation.append(wipe_out_activity)
        self.before_pattern_presentation.append(clear_event_queue)
        self.after_analysis_session.append(restore_input_generators)
        
    def initialize_featureresponses(self,features):
        """Create an empty DistributionMatrix for each feature and each sheet."""
        self._featureresponses = {}
        self._fullmatrix = {}
        for sheet in self.sheets_to_measure():
            self._featureresponses[sheet] = {}
            for f in features:
                self._featureresponses[sheet][f.name]=DistributionMatrix(sheet.shape,axis_range=f.range,cyclic=f.cyclic)
            self._fullmatrix[sheet] = FullMatrix(sheet.shape,features)

    def sheets_to_measure(self):
        """Return a list of the Sheets in the current simulation for which to collect responses."""
        return  [x for x in topo.sim.objects(Sheet).values()
                 if hasattr(x,'measure_maps') and x.measure_maps]
        
    def measure_responses(self,pattern_presenter,param_dict,features,display):
        """Present the given input patterns and collate the responses."""
        
        # Run hooks before the analysis session
        for f in self.before_analysis_session: f()

        self.param_dict=param_dict
        self.pattern_presenter = pattern_presenter
        
        features_to_permute = [f for f in features if f.compute_fn is None]
        self.features_to_compute = [f for f in features if f.compute_fn is not None]

        self.feature_names=[f.name for f in features_to_permute]
        values_lists=[f.values for f in features_to_permute]
        self.permutations = cross_product(values_lists)
        values_description=' * '.join(["%d %s" % (len(f.values),f.name) for f in features_to_permute])
        
        self.refresh_act_wins=False
        if display:
            if hasattr(topo,'guimain'):
                self.refresh_act_wins=True
            else:
                self.warning("No GUI available for display.")

        # CEBALERT: when there are multiple sheets, this can make it seem
        # like topographica's stuck in a loop (because the counter goes
        # to 100% lots of times...e.g. hierarchical's orientation tuning fullfield.)

        timer = copy.copy(topo.sim.timer)
        timer.func = self.present_permutation

        if hasattr(topo,'guimain'):
            topo.guimain.open_progress_window(timer)
        else:
            self.message("Presenting %d test patterns (%s)." % (len(self.permutations),values_description))

        timer.call_fixed_num_times(self.permutations)
        
        # Run hooks after the analysis session
        for f in self.after_analysis_session: f()

    def present_permutation(self,permutation):
        """Present a pattern with the specified set of feature values."""
        topo.sim.state_push()

        # Calculate complete set of settings
        permuted_settings = zip(self.feature_names, permutation)
        complete_settings = permuted_settings + \
            [(f.name,f.compute_fn(permuted_settings)) for f in self.features_to_compute]
            
        # Run hooks before and after pattern presentation.
        # Could use complete_settings here, to avoid some
        # PatternPresenter special cases, but that might cause
        # conflicts with the existing PatternPresenter code.
        for f in self.before_pattern_presentation: f()
        #valstring = " ".join(["%s=%s" % (n,v) for n,v in complete_settings])
        #self.message("Presenting pattern %s" % valstring)
        self.pattern_presenter(dict(permuted_settings),self.param_dict)
        for f in self.after_pattern_presentation: f()

        if self.refresh_act_wins:topo.guimain.refresh_activity_windows()

        self._update(complete_settings)
        topo.sim.state_pop()

    def _update(self,current_values):
        # Update each DistributionMatrix with (activity,bin)
        for sheet in self.sheets_to_measure():
            for feature,value in current_values:
                self._featureresponses[sheet][feature].update(sheet.activity, value)
            self._fullmatrix[sheet].update(sheet.activity,current_values)



class ReverseCorrelation(FeatureResponses):
    """
    Calculate the receptive fields for all neurons using reverse correlation.
    """
    # CB: Can't we have a better class hierarchy?

    input_sheet = param.Parameter(default=None)

    def initialize_featureresponses(self,features): # CB: doesn't need features!

        self._featureresponses = {}
        assert hasattr(self.input_sheet,'shape')
        
        # surely there's a way to get an array of 0s for each element without
        # looping? (probably had same question for distributionmatrix).
        for sheet in self.sheets_to_measure():
            self._featureresponses[sheet]= numpy.ones(sheet.activity.shape,dtype=object) 
            rows,cols = sheet.activity.shape
            for r in range(rows):
                for c in range(cols):
                    self._featureresponses[sheet][r,c] = numpy.zeros(self.input_sheet.shape) # need to specify dtype?
        

    def collect_feature_responses(self,pattern_presenter,param_dict,display,feature_values):
        self.measure_responses(pattern_presenter,param_dict,feature_values,display)

        for sheet in self.sheets_to_measure():
            rows,cols = sheet.activity.shape
            input_bounds = self.input_sheet.bounds
            input_sheet_views = self.input_sheet.sheet_views

            for ii in range(rows):
                for jj in range(cols):
                    view = SheetView((self._featureresponses[sheet][ii,jj],input_bounds),
                                     sheet.name,sheet.precedence,topo.sim.time())
                    x,y = sheet.matrixidx2sheet(ii,jj)
                    key = ('RFs',sheet.name,x,y)
                    input_sheet_views[key]=view

                    
    

    def measure_responses(self,pattern_presenter,param_dict,features,display):
        """Present the given input patterns and collate the responses."""

        # Since input_sheet's not fixed, we have to call this. Means that there are
        # normally duplicate calls (e.g. gets called by __init__ and then gets called
        # here for no reason except maybe the input_sheet got changed). Would be better
        # to have the input_sheet fixed.
        self.initialize_featureresponses(features) 
        
        super(ReverseCorrelation,self).measure_responses(pattern_presenter,param_dict,
                                                         features,display)
                                                         
    # Ignores current_values; they simply provide distinct patterns on the retina
    def _update(self,current_values):
        for sheet in self.sheets_to_measure():
            rows,cols = sheet.activity.shape
            for ii in range(rows): 
                for jj in range(cols):
                    self._featureresponses[sheet][ii,jj]+=sheet.activity[ii,jj]*self.input_sheet.activity



                          
class FeatureMaps(FeatureResponses):
    """
    Measures and collects the responses to a set of features for calculating feature maps.

    For each feature and each sheet, the results are stored as a
    preference matrix and selectivity matrix in the sheet's
    sheet_views; these can then be plotted as preference
    or selectivity maps.
    """
    
    selectivity_multiplier = param.Number(default=17,bounds=(0.0,None),doc="""
        Factor by which to multiply the calculated selectivity values
        before plotting them.  Usually set much greater than 1.0 to
        highlight particularly unselective areas, especially when
        combining selectivity with other plots as when using Confidence
        subplots.""")
    
    def __init__(self,features,**params):
        super(FeatureMaps,self).__init__(features,**params)
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
            # CB: (see also ALERT by SheetView's norm_factor.)
                cyclic = self._featureresponses[sheet][feature].distribution_matrix[0,0].cyclic
                if cyclic:
                    norm_factor = self._featureresponses[sheet][feature].distribution_matrix[0,0].axis_range
                else:
                    norm_factor = 1.0

                #JLHACKALERT - normfactor changes depending on the number of squares the retina
                #is divided into during retinotopy measurement.
                if feature=="retinotopy":
                    norm_factor = (pattern_presenter.divisions)*(pattern_presenter.divisions)
                    
                if weighted_average:
                    preference_map = SheetView(
                        ((self._featureresponses[sheet][feature].weighted_average())/norm_factor,
                         bounding_box), sheet.name, sheet.precedence, topo.sim.time())
                else:
                    preference_map = SheetView(
                        ((self._featureresponses[sheet][feature].max_value_bin())/norm_factor,
                         bounding_box), sheet.name, sheet.precedence, topo.sim.time())

                preference_map.cyclic = cyclic
                preference_map.norm_factor = norm_factor
                    
                sheet.sheet_views[feature.capitalize()+'Preference']=preference_map
                
                selectivity_map = SheetView((self.selectivity_multiplier*
                                             self._featureresponses[sheet][feature].selectivity(),
                                             bounding_box), sheet.name , sheet.precedence, topo.sim.time())
                sheet.sheet_views[feature.capitalize()+'Selectivity']=selectivity_map

                
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




###############################################################################
###############################################################################

# Define user-level commands and helper classes for calling the above


class Feature(object):
    """
    Stores the parameters required for generating a map of one input feature.
    """

    def __init__(self, name, range=None, step=0.0, values=None, cyclic=False, compute_fn=None, offset=0):
         """
         Users can provide either a range and a step size, or a list of values.
         If a list of values is supplied, the range can be omitted unless the
         default of the min and max in the list of values is not appropriate.

         If non-None, the compute_fn should be a function that when given a list 
         of other parameter values, computes and returns the value for this feature.

         If supplied, the offset is added to the given or computed values to allow
         the starting value to be specified.
         """
         self.name=name
         self.cyclic=cyclic
         self.compute_fn=compute_fn
         self.range=range
                     
         if values is not None:
             self.values=values if offset == 0 else [v+offset for v in values]
             if not self.range:
                 self.range=(min(self.values),max(self.values))
         else:
             if range is None:
                 raise ValueError('The range or values must be specified.')
             low_bound,up_bound = self.range
             values=(frange(low_bound,up_bound,step,not cyclic))
             self.values = values if offset == 0 else \
                           [(v+offset)%(up_bound-low_bound) if cyclic else (v+offset)
                            for v in values]



class PatternPresenter(param.Parameterized):
    """
    Function object for presenting PatternGenerator-created patterns.

    This class helps coordinate a set of patterns to be presented to a
    set of GeneratorSheets.  It provides a standardized way of
    generating a set of linked patterns for testing or analysis, such
    as when measuring preference maps or presenting test patterns.
    Subclasses can provide additional mechanisms for doing this in
    different ways.
    """
    
    # JABALERT: Needs documenting, and probably also a clearer name
    contrast_parameter = param.Parameter('michelson_contrast')

    # JABALERT: Needs documenting; apparently only for retinotopy?
    divisions = param.Parameter()

    apply_output_fn = param.Boolean(default=True, doc="""
        When presenting a pattern, whether to apply each sheet's
        output function.  If False, for many networks the response
        will be linear, which requires fewer test patterns to measure
        a meaningful response, but it may not correspond to the actual
        preferences of each neuron under other conditions.  If True,
        callers will need to ensure that the input patterns are in a
        suitable range to drive the neurons to generate meaningful
        output, because e.g. a threshold-based output function might
        result in no activity for inputs that are too weak..""")

    duration = param.Number(default=1.0,doc="""
        Amount of simulation time for which to present each test pattern.
	By convention, most Topographica example files are designed to
        have a suitable activity pattern computed by the
        default time, but the duration will need to be changed for
        other models that do not follow that convention or if a
        linear response is desired.""")


    def __init__(self,pattern_generator,**params):
        super(PatternPresenter,self).__init__(**params)
        self.gen = pattern_generator # Why not a Parameter?
        
        
    def __call__(self,features_values,param_dict):
        for param,value in param_dict.iteritems():
           self.gen.__setattr__(param,value)
               
        for feature,value in features_values.iteritems():
           self.gen.__setattr__(feature,value)

        gen_list=topo.sim.objects(GeneratorSheet)
        input_sheet_names=gen_list.keys()
        # Copy the given generator once for every GeneratorSheet
        inputs = dict().fromkeys(gen_list)
        for k in inputs.keys():
            inputs[k]=copy.deepcopy(self.gen)

        ### JABALERT: Should replace these special cases with general
        ### support for having meta-parameters controlling the
        ### generation of different patterns for each GeneratorSheet.
        ### For instance, we will also need to support xdisparity and
        ### ydisparity, plus movement of patterns between two eyes, colors,
        ### etc.  At the very least, it should be simple to control
        ### differences in single parameters easily.  In addition,
        ### these meta-parameters should show up as parameters for
        ### this object, augmenting the parameters for each individual
        ### pattern, e.g. in the Test Pattern window.  In this way we
        ### should be able to provide general support for manipulating
        ### both pattern parameters and parameters controlling
        ### interaction between or differences between patterns.           

        if features_values.has_key('direction'):
            orientation = features_values['direction']+pi/2
            from topo.pattern.basic import Sweeper            
            for name,i in zip(inputs.keys(),range(len(input_sheet_names))):
                speed=features_values['speed']
                try:
                    step=int(name[-1])
                except:
                    if not hasattr(self,'direction_warned'):
                        self.warning('Assuming step is zero; no input lag number specified at the end of the input sheet name.')
                        self.direction_warned=True
                    step=0
                speed=features_values['speed']
                inputs[name] = Sweeper(generator=inputs[name],step=step,speed=speed)
                setattr(inputs[name],'orientation',orientation)

           

        if features_values.has_key('hue'):
            for name,i in zip(inputs.keys(),range(len(input_sheet_names))):
                r,g,b=hsv_to_rgb(features_values['hue'],1.0,1.0)
                if (name.count('Red')):
                    inputs[name].scale=r
                elif (name.count('Green')):
                    inputs[name].scale=g
                elif (name.count('Blue')):
                    inputs[name].scale=b
                else: 
                    if not hasattr(self,'hue_warned'):
                        self.warning('Unable to measure hue preference, because hue is defined only when there are different input sheets with names with Red, Green or Blue substrings.')
                        self.hue_warned=True


        if features_values.has_key('retinotopy'):
            #Calculates coordinates of the centre of each SineGratingRectangle to be presented 
            coordinate_x=[]
            coordinate_y=[]
            coordinates=[]
            for name,i in zip(inputs.keys(),range(len(input_sheet_names))):
                l,b,r,t = topo.sim[name].nominal_bounds.lbrt()
                x_div=float(r-l)/(self.divisions*2)
                y_div=float(t-b)/(self.divisions*2)
                for i in range(self.divisions):
                    if not bool(self.divisions%2):
                        if bool(i%2):
                            coordinate_x.append(i*x_div)
                            coordinate_y.append(i*y_div)
                            coordinate_x.append(i*-x_div)
                            coordinate_y.append(i*-y_div)
                    else:
                        if not bool(i%2):
                            coordinate_x.append(i*x_div)
                            coordinate_y.append(i*y_div)
                            coordinate_x.append(i*-x_div)
                            coordinate_y.append(i*-y_div)
                for x in coordinate_x:
                    for y in coordinate_y:
                        coordinates.append((x,y))
               
                x_coord=coordinates[features_values['retinotopy']][0]
                y_coord=coordinates[features_values['retinotopy']][1]
                inputs[name].x = x_coord
                inputs[name].y = y_coord
          
                
          
        if features_values.has_key("phasedisparity"):
            temp_phase1=features_values['phase']-features_values['phasedisparity']/2.0
            temp_phase2=features_values['phase']+features_values['phasedisparity']/2.0
            for name,i in zip(inputs.keys(),range(len(input_sheet_names))):
                if (name.count('Right')):
                    inputs[name].phase=wrap(0,2*pi,temp_phase1)
                elif (name.count('Left')):
                    inputs[name].phase=wrap(0,2*pi,temp_phase2)
                else:
                    if not hasattr(self,'disparity_warned'):
                        self.warning('Unable to measure disparity preference, because disparity is defined only when there are inputs for Right and Left retinas.')
                        self.disparity_warned=True
                
          
        ## Not yet used; example only
        #if features_values.has_key("xdisparity"):
        #    if len(input_sheet_names)!=2:
        #        self.warning('Disparity is defined only when there are exactly two patterns')
        #    else:
        #        inputs[input_sheet_names[0]].x=inputs[input_sheet_names[0]].x - inputs[input_sheet_names[0]].xdisparity/2.0
        #        inputs[input_sheet_names[1]].x=inputs[input_sheet_names[1]].x + inputs[input_sheet_names[1]].xdisparity/2.0
        #
        #        inputs={}
        #        inputs[input_sheet_names[0]]=inputs[input_sheet_names[0]]
        #        inputs[input_sheet_names[1]]=inputs[input_sheet_names[1]]
        #
        #if features_values.has_key("ydisparity"):
        #    if len(input_sheet_names)!=2:
        #        self.warning('Disparity is defined only when there are exactly two patterns')
        #    else:
        #        inputs[input_sheet_names[0]].y=inputs[input_sheet_names[0]].y - inputs[input_sheet_names[0]].ydisparity/2.0
        #        inputs[input_sheet_names[1]].y=inputs[input_sheet_names[1]].y + inputs[input_sheet_names[1]].ydisparity/2.0
        #
        #        inputs={}
        #        inputs[input_sheet_names[0]]=inputs[input_sheet_names[0]]
        #        inputs[input_sheet_names[1]]=inputs[input_sheet_names[1]]


        if features_values.has_key("ocular"):
            for name,i in zip(inputs.keys(),range(len(input_sheet_names))):
                if (name.count('Right')):
                    inputs[name].scale=2*features_values['ocular']
                elif (name.count('Left')):
                    inputs[name].scale=2.0-2*features_values['ocular']
                else:
                    self.warning('Skipping input region %s; Ocularity is defined only for Left and Right retinas.' %
                                 name)

        if features_values.has_key("contrastcentre")or param_dict.has_key("contrastcentre"):
            if self.contrast_parameter=='michelson_contrast':
                for g in inputs.itervalues():
                    g.offsetcentre=0.5
                    g.scalecentre=2*g.offsetcentre*g.contrastcentre/100.0

            
	
            elif self.contrast_parameter=='weber_contrast':
                # Weber_contrast is currently only well defined for
                # the special case where the background offset is equal
                # to the target offset in the pattern type
                # SineGratingDisk
                for g in inputs.itervalues():
                    g.offsetcentre=0.5   #In this case this is the offset of both the background and the sine grating
                    g.scalecentre=2*g.offsetcentre*g.contrastcentre/100.0
            
                
            elif self.contrast_parameter=='scale':
                for g in inputs.itervalues():
                    g.offsetcentre=0.0
                    g.scalecentre=g.contrastcentre



        if features_values.has_key("contrastsurround")or param_dict.has_key("contrastsurround"):
            if self.contrast_parameter=='michelson_contrast':
                for g in inputs.itervalues():
                    g.offsetsurround=0.5
                    g.scalesurround=2*g.offsetsurround*g.contrastsurround/100.0

            
	
            elif self.contrast_parameter=='weber_contrast':
                # Weber_contrast is currently only well defined for
                # the special case where the background offset is equal
                # to the target offset in the pattern type
                # SineGratingDisk
                for g in inputs.itervalues():
                    g.offsetsurround=0.5   #In this case this is the offset of both the background and the sine grating
                    g.scalesurround=2*g.offsetsurround*g.contrastsurround/100.0
            
                
            elif self.contrast_parameter=='scale':
                for g in inputs.itervalues():
                    g.offsetsurround=0.0
                    g.scalesurround=g.contrastsurround



        if features_values.has_key("contrast") or param_dict.has_key("contrast"):
            if self.contrast_parameter=='michelson_contrast':
                for g in inputs.itervalues():
                    g.offset=0.5
                    g.scale=2*g.offset*g.contrast/100.0

            
	
            elif self.contrast_parameter=='weber_contrast':
                # Weber_contrast is currently only well defined for
                # the special case where the background offset is equal
                # to the target offset in the pattern type
                # SineGratingDisk
                for g in inputs.itervalues():
                    g.offset=0.5   #In this case this is the offset of both the background and the sine grating
                    g.scale=2*g.offset*g.contrast/100.0
            
                
            elif self.contrast_parameter=='scale':
                for g in inputs.itervalues():
                    g.offset=0.0
                    g.scale=g.contrast
            
        pattern_present(inputs, self.duration, plastic=False,
                     apply_output_fn=self.apply_output_fn)



class Subplotting(param.Parameterized):
    """
    Convenience functions for handling subplots (such as colorized Activity plots).
    Only needed for avoiding typing, as plots can be declared with their own
    specific subplots without using these functions.
    """
    
    plotgroups_to_subplot=param.List(default=
        ["Activity", "Connection Fields", "Projection", "Projection Activity"],
        doc="List of plotgroups for which to set subplots.")

    subplotting_declared = param.Boolean(default=False,
        doc="Whether set_subplots has previously been called")
    
    _last_args = param.Parameter(default=())
    
    @staticmethod    
    def set_subplots(prefix=None,hue="",confidence="",force=True):
        """
        Define Hue and Confidence subplots for each of the plotgroups_to_subplot.  
        Typically used to make activity or weight plots show a
        preference value as the hue, and a selectivity as the
        confidence.

        The specified hue, if any, should be the name of a SheetView,
        such as OrientationPreference.  The specified confidence, if
        any, should be the name of a (usually) different SheetView,
        such as OrientationSelectivity.

        The prefix option is a shortcut making the usual case easier
        to type; it sets hue to prefix+"Preference" and confidence to
        prefix+"Selectivity".

        If force=False, subplots are changed only if no subplot is
        currently defined.  Force=False is useful for setting up
        subplots automatically when maps are measured, without
        overwriting any subplots set up specifically by the user.

        Currently works only for plotgroups that have a plot
        with the same name as the plotgroup, though this could
        be changed easily.

        Examples::
        
           Subplotting.set_subplots("Orientation")
             - Set the default subplots to OrientationPreference and OrientationSelectivity

           Subplotting.set_subplots(hue="OrientationPreference")
             - Set the default hue subplot to OrientationPreference with no selectivity

           Subplotting.set_subplots()
             - Remove subplots from all the plotgroups_to_subplot.
        """

        Subplotting._last_args=(prefix,hue,confidence,force)
        
        if Subplotting.subplotting_declared and not force:
            return

        if prefix:
            hue=prefix+"Preference"
            confidence=prefix+"Selectivity"
        
        for name in Subplotting.plotgroups_to_subplot:
            if plotgroups.has_key(name):
                pg=plotgroups[name]
                if pg.plot_templates.has_key(name):
                    pt=pg.plot_templates[name]
                    pt["Hue"]=hue
                    pt["Confidence"]=confidence
                else:
                    Subplotting().warning("No template %s defined for plotgroup %s" % (name,name))
            else:
                Subplotting().warning("No plotgroup %s defined" % name)

        Subplotting.subplotting_declared=True


    @staticmethod    
    def restore_subplots():
        args=Subplotting._last_args
        if args != (): Subplotting.set_subplots(*(Subplotting._last_args))



###############################################################################
###############################################################################
###############################################################################
#
# 20081017 JABNOTE: This implementation could be improved.  
#
# It currently requires every subclass to implement the feature_list
# method, which constructs a list of features using various parameters
# to determine how many and which values each feature should have.  It
# would be good to replace the feature_list method with a Parameter or
# set of Parameters, since it is simply a special data structure, and
# this would make more detailed control feasible for users. For
# instance, instead of something like num_orientations being used to
# construct the orientation Feature, the user could specify the
# appropriate Feature directly, so that they could e.g. supply a
# specific list of orientations instead of being limited to a fixed
# spacing.
# 
# However, when we implemented this, we ran into two problems:
#
# 1. It's difficult for users to modify an open-ended list of
#     Features.  E.g., if features is a List:
#
#      features=param.List(doc="List of Features to vary""",default=[
#          Feature(name="frequency",values=[2.4]),
#          Feature(name="orientation",range=(0.0,pi),step=pi/4,cyclic=True),
#          Feature(name="phase",range=(0.0,2*pi),step=2*pi/18,cyclic=True)])
#
#    then it it's easy to replace the entire list, but tough to
#    change just one Feature.  Of course, features could be a
#    dictionary, but that doesn't help, because when the user
#    actually calls the function, they want the arguments to
#    affect only that call, whereas looking up the item in a
#    dictionary would only make permanent changes easy, not
#    single-call changes.
#    
#    Alternatively, one could make each feature into a separate     
#    parameter, and then collect them using a naming convention like:
#
#     def feature_list(self,p):
#         fs=[]
#         for n,v in self.get_param_values():
#             if n in p: v=p[n]
#             if re.match('^[^_].*_feature$',n):
#                 fs+=[v]
#         return fs
#    
#    But that's quite hacky, and doesn't solve problem 2.
# 
# 2. Even if the users can somehow access each Feature, the same
#    problem occurs for the individual parts of each Feature.  E.g.
#    using the separate feature parameters above, Spatial Frequency
#    map measurement would require:
#
#      from topo.command.analysis import Feature
#      from math import pi
#      update_command=[measure_or_pref.instance( \
#         frequency_feature=Feature(name="frequency",values=frange(1.0,6.0,0.2)), \
#         phase_feature=Feature(name="phase",range=(0.0,2*pi),step=2*pi/15,cyclic=True), \
#         orientation_feature=Feature(name="orientation",range=(0.0,pi),step=pi/4,cyclic=True)])
#   
#    rather than the current, much more easily controllable implementation:
#   
#      update_command=[measure_or_pref.instance(frequencies=frange(1.0,6.0,0.2),\
#         num_phase=15,num_orientation=4)]
#
#    I.e., to change anything about a Feature, one has to supply an
#    entirely new Feature, because otherwise the original Feature
#    would be changed for all future calls.  Perhaps there's some way
#    around this by copying objects automatically at the right time,
#    but if so it's not obvious.  Meanwhile, the current
#    implementation is reasonably clean and easy to use, if not as
#    flexible as it could be.



class MeasureResponseCommand(ParameterizedFunction):
    """Parameterized command for presenting input patterns and measuring responses."""
      
    scale = param.Number(default=1.0,softbounds=(0.0,2.0),doc="""
        Multiplicative strength of input pattern.""")
    
    offset = param.Number(default=0.0,softbounds=(-1.0,1.0),doc="""
        Additive offset to input pattern.""")

    display = param.Boolean(default=False,doc="""
        Whether to update a GUI display (if any) during the map measurement.""")

    weighted_average= param.Boolean(default=True, doc="""
        Whether to compute results using a weighted average, or just
        discrete values.  A weighted average can give more precise
        results, without being limited to a set of discrete values,
        but the results can have systematic biases due to the
        averaging, especially for non-cyclic parameters.""")

    pattern_presenter = param.Callable(default=None,doc="""
        Callable object that will present a parameter-controlled pattern to a
        set of Sheets.  Needs to be supplied by a subclass or in the call.
        The attributes duration and apply_output_fn (if non-None) will
        be set on this object, and it should respect those if possible.""")
    
    static_parameters = param.List(class_=str,default=["scale","offset"],doc="""
        List of names of parameters of this class to pass to the
        pattern_presenter as static parameters, i.e. values that
        will be fixed to a single value during measurement.""")

    subplot = param.String("",doc="""Name of map to register as a subplot, if any.""")

    apply_output_fn = param.Boolean(default=None, doc="""
        If non-None, pattern_presenter.apply_output_fn will be
        set to this value.  Provides a simple way to set
        this commonly changed option of PatternPresenter.""")

    duration = param.Number(default=None,doc="""
        If non-None, pattern_presenter.duration will be
        set to this value.  Provides a simple way to set
        this commonly changed option of PatternPresenter.""")

    __abstract = True


    def __call__(self,**params):
        """Measure the response to the specified pattern and store the data in each sheet."""
        
        p=ParamOverrides(self,params)
        x=FeatureMaps(self._feature_list(p),name="FeatureMaps_for_"+self.name)
        static_params = dict([(s,p[s]) for s in p.static_parameters])
        if p.duration is not None:
            p.pattern_presenter.duration=p.duration
        if p.apply_output_fn is not None:
            p.pattern_presenter.apply_output_fn=p.apply_output_fn
        x.collect_feature_responses(p.pattern_presenter,static_params,
                                    p.display,p.weighted_average)

        if p.subplot != "":
            Subplotting.set_subplots(p.subplot,force=True)

        return x._fullmatrix


    def _feature_list(self,p):
        """Return the list of features to vary; must be implemented by each subclass."""
        raise NotImplementedError

    

class SinusoidalMeasureResponseCommand(MeasureResponseCommand):
    """Parameterized command for presenting sine gratings and measuring responses."""
    
    pattern_presenter = param.Callable(
        default=PatternPresenter(pattern_generator=SineGrating()),doc="""
        Callable object that will present a parameter-controlled pattern to a
        set of Sheets.  By default, uses a SineGrating presented for a short
	duration.  By convention, most Topographica example files
        are designed to have a suitable activity pattern computed by
        that time, but the duration will need to be changed for other
        models that do not follow that convention.""")

    frequencies = param.List(class_=float,default=[2.4],doc="Sine grating frequencies to test.")
    
    num_phase = param.Integer(default=18,bounds=(1,None),softbounds=(1,48),
                              doc="Number of phases to test.")

    num_orientation = param.Integer(default=4,bounds=(1,None),softbounds=(1,24),
                                    doc="Number of orientations to test.")

    scale = param.Number(default=0.3)

    __abstract = True
    


class PositionMeasurementCommand(MeasureResponseCommand):
    """Parameterized command for measuring topographic position."""

    divisions=param.Integer(default=6,bounds=(1,None),doc="""
        The number of different positions to measure in X and in Y.""")
    
    x_range=param.NumericTuple((-0.5,0.5),doc="""
        The range of X values to test.""")

    y_range=param.NumericTuple((-0.5,0.5),doc="""
        The range of Y values to test.""")

    size=param.Number(default=0.5,bounds=(0,None),doc="""
        The size of the pattern to present.""")
    
    pattern_presenter = param.Callable(
        default=PatternPresenter(Gaussian(aspect_ratio=1.0)),doc="""
        Callable object that will present a parameter-controlled
        pattern to a set of Sheets.  For measuring position, the
        pattern_presenter should be spatially localized, yet also able
        to activate the appropriate neurons reliably.""")

    static_parameters = param.List(default=["scale","offset","size"])
  
    __abstract = True

        


class SingleInputResponseCommand(MeasureResponseCommand):
    """
    A callable Parameterized command for measuring the response to input on a specified Sheet.

    Note that at present the input is actually presented to all input sheets; the
    specified Sheet is simply used to determine various parameters.  In the future,
    it may be modified to draw the pattern on one input sheet only.
    """
    # CBERRORALERT: Need to alter PatternPresenter to accept an input sheet,
    # to allow it to be presented on only one sheet.
    
    input_sheet = param.ObjectSelector(
        default=None,compute_default_fn=default_input_sheet,doc="""
        Name of the sheet where input should be drawn.""")

    scale = param.Number(default=30.0)

    offset = param.Number(default=0.5)

    # JABALERT: Presumably the size is overridden in the call, right?
    pattern_presenter = param.Callable(
        default=PatternPresenter(Rectangle(size=0.1,aspect_ratio=1.0)))

    static_parameters = param.List(default=["scale","offset","size"])

    weighted_average = None # Disabled unused parameter

    __abstract = True



class FeatureCurveCommand(SinusoidalMeasureResponseCommand):
    """A callable Parameterized command for measuring tuning curves."""

    num_orientation = param.Integer(default=12)

    sheet = param.ObjectSelector(
        default=None,compute_default_fn=default_measureable_sheet,doc="""
        Name of the sheet to use in measurements.""")

    units = param.String(default='%',doc="""
        Units for labeling the curve_parameters in figure legends.
        The default is %, for use with contrast, but could be any 
        units (or the empty string).""")

    # Make constant in subclasses?
    x_axis = param.String(default='orientation',doc="""
        Parameter to use for the x axis of tuning curves.""")

    static_parameters = param.List(default=[])

    # JABALERT: Might want to accept a list of values for a given
    # parameter to make the simple case easier; then maybe could do
    # the crossproduct of them?
    curve_parameters=param.Parameter([{"contrast":30},{"contrast":60},{"contrast":80},{"contrast":90}],doc="""
        List of parameter values for which to measure a curve.""")

    __abstract = True

    def __call__(self,**params):
        """Measure the response to the specified pattern and store the data in each sheet."""
        p=ParamOverrides(self,params)
        self.params('sheet').compute_default()
        self._compute_curves(p,p.sheet)


    def _compute_curves(self,p,sheet,val_format='%s'):
        """
        Compute a set of curves for the specified sheet, using the
        specified val_format to print a label for each value of a
        curve_parameter.
        """

        x=FeatureCurves(self._feature_list(p),sheet=sheet,x_axis=self.x_axis)
        for curve in p.curve_parameters:
            static_params = dict([(s,p[s]) for s in p.static_parameters])
            static_params.update(curve)
            curve_label="; ".join([('%s = '+val_format+'%s') % (n.capitalize(),v,p.units) for n,v in curve.items()])
            # JABALERT: Why is the feature list duplicated here?
            x.collect_feature_responses(self._feature_list(p),p.pattern_presenter,static_params,curve_label,p.display)


    def _feature_list(self,p):
        return [Feature(name="phase",range=(0.0,2*pi),step=2*pi/p.num_phase,cyclic=True),
                Feature(name="orientation",range=(0,pi),step=pi/p.num_orientation,cyclic=True),
                Feature(name="frequency",values=p.frequencies)]
        

    def _sheetview_unit(self,sheet,sheet_coord,map_name,default=0.0):
        """Look up and return the value of a SheetView for a specified unit."""
        matrix_coords = sheet.sheet2matrixidx(*sheet_coord)

        if(map_name in sheet.sheet_views):
            pref = sheet.sheet_views[map_name].view()[0]
            val = pref[matrix_coords]
        else:
            self.warning(("%s should be measured before plotting this tuning curve -- " + 
                          "using default value of %s for %s unit (%d,%d).") % \
                         (map_name,default,sheet.name,sheet_coord[0],sheet_coord[1]))
            val = default

        return val


class UnitCurveCommand(FeatureCurveCommand):
    """
    Measures tuning curve(s) of particular unit(s).
    """

    pattern_presenter = param.Callable(
        default=PatternPresenter(pattern_generator=SineGratingDisk(),
                                 contrast_parameter="weber_contrast"))

    size=param.Number(default=0.5,bounds=(0,None),doc="""
        The size of the pattern to present.""")
    
    coords = param.List(default=[(0,0)],doc="""
        List of coordinates of units to measure.""")

    __abstract = True
