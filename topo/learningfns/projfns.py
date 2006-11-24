"""
Learning functions for Projections.


For example, CFProjectionLearningFunctions compute a new set of
ConnectionFields when given an input and output pattern and a set of
ConnectionField objects.

$Id$
"""
__version__ = "$Revision$"

import Numeric
from Numeric import ones,Float,Float32,zeros

from topo.base.cf import CFPLearningFn,LearningFnParameter
from topo.base.parameterclasses import Number,BooleanParameter
from basic import BCMFixed
from topo.base.functionfamilies import Hebbian,LearningFn,LearningFnParameter

# Imported here so that all ProjectionLearningFns will be in the same package
from topo.base.cf import CFPLF_Identity,CFPLF_Plugin


#### JABHACKALERT: Untested
##class CFPLF_BCM(CFPLearningFn):
##    """
##    Bienenstock, Cooper, and Munro (1982) learning rule with sliding threshold.
##    
##    (See Dayan and Abbott, 2001, equation 8.12, 8.13).
##
##    Activities change only when there is both pre- and post-synaptic activity.
##    Threshold is adjusted based on recent firing rates.
##    """
##    single_cf_fn = LearningFnParameter(default=BCMFixed())
##    
##    unit_threshold_0=Number(default=0.5,bounds=(0,None),
##        doc="Initial value of threshold between LTD and LTP; actual value computed based on recent history.")
##    unit_threshold_learning_rate=Number(default=0.1,bounds=(0,None),
##        doc="Amount by which the unit_threshold is adjusted for each activity calculation.")
##
##    def __call__(self, cfs, input_activity, output_activity, learning_rate, **params):
##        # Initialize thresholds the first time we learn the size of the output_activity.
##        if not hasattr(self,'unit_thresholds'):
##            self.unit_thresholds=ones(output_activity.shape,Float32)*self.unit_threshold_0
##            self.unit_thresholds.savespace(1)
##
##        rows,cols = output_activity.shape
##
##        # JABALERT: Is this correct?
##	single_connection_learning_rate = self.constant_sum_connection_rate(cfs,learning_rate)
##
##        # avoid evaluating these references each time in the loop
##        single_cf_fn = self.single_cf_fn
##	for r in xrange(rows):
##            for c in xrange(cols):
##                cf = cfs[r][c]
##                input_activity = cf.get_input_matrix(input_activity)
##                unit_activity = output_activity[r,c]
##                threshold=self.unit_thresholds[r,c]
##                print cf.weights, type(cf.weights)
##                print input_activity, type(input_activity)
##                print single_connection_learning_rate,unit_activity,threshold, (unit_activity-threshold)
##                cf.weights += (single_connection_learning_rate * unit_activity * (unit_activity-threshold)) * input_activity 
##                self.unit_thresholds[r,c] += self.unit_threshold_learning_rate*(unit_activity*unit_activity-threshold)
##
##                # CEBHACKALERT: see ConnectionField.__init__()
##                cf.weights *= cf.mask



class CFPLF_Trace(CFPLearningFn):
    """
    Implementation of Trace LearningFn as CFPLF, NOT FULLY TESTED

    Trace learning rule; Foldiak (1991), Sutton and Barto (1981), Wallis and Rolls (1997).
       
    Incorporates a trace of recent activity into the learning
    function, instead of learning based only on the current activity
    as in strict Hebbian learning.
    
    Requires some form of output_fn normalization for stability.

    NOT YET TESTED.
    """

    trace_strength=Number(default=0.5,bounds=(0.0,1.0),
       doc="How much the learning is dominated by the activity trace, relative to the current value.")     
    single_cf_fn = LearningFnParameter(default=BCMFixed())                
    def __call__(self, cfs, input_activity, output_activity, learning_rate, **params):
        rows,cols = output_activity.shape
        single_connection_learning_rate = self.constant_sum_connection_rate(cfs,learning_rate)
        single_cf_fn = self.single_cf_fn
        
        ##Initialise traces to zero if they don't already exist
        if not hasattr(self,'traces'):
            self.traces=zeros(output_activity.shape,Float32)
            self.traces.savespace(1)
            
        for r in xrange(rows):
            for c in xrange(cols):
                cf = cfs[r][c]
                input_activity = cf.get_input_matrix(input_activity)
                unit_activity = output_activity[r,c]
                self.traces[r,c] =(1-self.trace_strength)*unit_activity+self.trace_strength*self.traces[r,c]
                cf.weights += single_connection_learning_rate * self.traces[r,c] * (input_activity - cf.weights)

                # CEBHACKALERT: see ConnectionField.__init__()
                cf.weights *= cf.mask
      


class CFPLF_OutstarHebbian(CFPLearningFn):
    """
    CFPLearningFunction applying the specified (default is Hebbian) 
    single_cf_fn to each CF, where normalization is done in an outstar-manner.

    Presumably does not need a separate output_fn for normalization.
    
    NOT YET TESTED.
    """
    single_cf_fn = LearningFnParameter(default=Hebbian(),
        doc="LearningFn that will be applied to each CF individually.")

    outstar_wsum = None

    def __call__(self, cfs, input_activity, output_activity, learning_rate, **params):
        """Apply the specified single_cf_fn to every CF."""
        rows,cols = output_activity.shape
	single_connection_learning_rate = self.constant_sum_connection_rate(cfs,learning_rate)
        # avoid evaluating these references each time in the loop
        single_cf_fn = self.single_cf_fn
	outstar_wsum = zeros(input_activity.shape)
	for r in xrange(rows):
            for c in xrange(cols):
                cf = cfs[r][c]
                single_cf_fn(cf.get_input_matrix(input_activity),
                             output_activity[r,c], cf.weights, single_connection_learning_rate)

		# Outstar normalization
		wrows,wcols = cf.weights.shape
		for wr in xrange(wrows):
		   for wc in xrange(wcols):
			outstar_wsum[wr][wc] += cf.weights[wr][wc]

                # CEBHACKALERT: see ConnectionField.__init__()
                cf.weights *= cf.mask




class HomeoSynaptic(CFPLearningFn):
    """
    Learning function using homeostatic synaptic scaling from 
    Sullivan & de Sa, "Homeostatic Synaptic Scaling in Self-Organizing Maps",
    Neural Networks (2006), 19(6-7):734-43.

    Does not necessarily require output_fn normalization for stability.
    """
    single_cf_fn = LearningFnParameter(default=Hebbian(),
       doc="LearningFn that will be applied to each CF individually")

    beta_n = Number(default=0.01,bounds=(0,None),
       doc="homeostatic learning rate")

    beta_c = Number(default=0.005,bounds=(0,None),
       doc="time window over which the neuron's firing rate is averaged")

    activity_target = Number(default=0.1,bounds=(0,None),
         doc="Target average activity")

    #debug = BooleanParameter(default=False,doc="Print average activity values")
    #beta_n = Number(default=0.00033,bounds=(0,None),doc="Homeostatic learning rate") #Too small?
    #beta_c = Number(default=0.000033,bounds=(0,None),doc="Time window over which the neuron's firing rate is averaged")
    
    def __init__(self,**params):
        super(HomeoSynaptic,self).__init__(**params)
	self.temp_hist = []
        self.ave_hist = []
        
    def __call__(self, cfs, input_activity, output_activity, learning_rate, **params):
	"""
        Update the value of the given weights matrix based on the
        input_activity matrix (of the same size as the weights matrix)
        and the response of this unit (the unit_activity), governed by
        a per-connection learning rate.
	"""
        
        if not hasattr(self,'averages'):
            self.averages = ones(output_activity.shape,Float) * 0.1
	    
                       	    
	    # normalize initial weights to 1.0
            rows,cols = output_activity.shape
            for r in xrange(rows):
                for c in xrange(cols):
                    cf = cfs[r][c]

	            current_norm_value = 1.0*Numeric.sum(abs(cf.weights.flat))
		    if current_norm_value != 0:
            	    	factor = (1.0/current_norm_value)
            	    	cf.weights *= factor
    
        # compute recent average of output activity
        self.averages = self.beta_c * output_activity + (1.0-self.beta_c) * self.averages
        activity_norm = 1.0 + self.beta_n * \
           ((self.averages - self.activity_target)/self.activity_target)
        rows,cols = output_activity.shape
	single_connection_learning_rate = self.constant_sum_connection_rate(cfs,learning_rate)

        # avoid evaluating these references each time in the loop
        single_cf_fn = self.single_cf_fn
	for r in xrange(rows):
            for c in xrange(cols):
                cf = cfs[r][c]
                single_cf_fn(cf.get_input_matrix(input_activity),
                             output_activity[r,c], cf.weights, single_connection_learning_rate)

		# homeostatic normalization
                cf.weights /= activity_norm[r][c]

                # CEBHACKALERT: see ConnectionField.__init__()
                cf.weights *= cf.mask
         
	# For analysis only; can be removed (in which case also remove the initializations above)
        self.ave_hist.append(self.averages[0][7])
        self.temp_hist.append (Numeric.sum(abs(cfs[0][7].weights.flat)))
