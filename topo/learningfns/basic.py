"""
Basic learning functions.

$Id$
"""
__version__ = "$Revision$"

from Numeric import ones,Float32

from topo.base.functionfamilies import LearningFn,LearningFnParameter
from topo.base.parameterclasses import Number
from topo.base.cf import CFPLearningFn

# Imported here so that all learning functions will be in the same package
from topo.base.functionfamilies import Hebbian



class Oja(LearningFn):
    """
    Oja's rule (Oja, 1982; Dayan and Abbott, 2001, equation 8.16.)

    Hebbian rule with soft multiplicative normalization, tending the
    weights toward a constant sum-squared value over time.
    """
    
    alpha=Number(default=0.1,bounds=(0,None))
    def __call__(self,input_activity, unit_activity, weights, single_connection_learning_rate):
        weights += single_connection_learning_rate * (unit_activity * input_activity -
                                                      self.alpha * (unit_activity**2) * weights)

class Covariance(LearningFn):
    """
    Covariance learning rule supporting either input or unit thresholds.

    As presented by Dayan and Abbott (2001), covariance rules allow
    either potentiation or depression of the same synapse, depending
    on an activity level.  By default, this implementation follows
    Dayan and Abbott equation 8.8, with the unit_threshold determining
    the level of postsynaptic activity (activity of the target unit),
    below which LTD (depression) will occur.

    If you wish to use an input threshold as in Dayan and Abbott
    equation 8.9 instead, set unit_threshold to zero and change
    input_thresold to some positive value instead.  When both
    thresholds are zero this rule degenerates to the standard Hebbian
    rule.
    
    Requires some form of output_fn normalization for stability.
    """
    
    unit_threshold =Number(default=0.5,bounds=(0,None),
        doc="Threshold between LTD and LTP, applied to the activity of this unit.")
    input_threshold=Number(default=0.0,bounds=(0,None),
        doc="Threshold between LTD and LTP, applied to the input activity.")
    def __call__(self,input_activity, unit_activity, weights, single_connection_learning_rate):
        weights += single_connection_learning_rate * (unit_activity - self.unit_threshold) * (input_activity - self.input_threshold)

        
class CPCA(LearningFn):
    """
    CPCA (Conditional Principal Component Analysis rule.

    (See O'Reilly and Munakata, Computational Explorations in 
    Cognitive Neuroscience, 2000, equation 4.12.)

    Increases each weight in proportion to the product of this
    neuron's activity, input activity, and connection weights.
 
    Has built-in normalization, and so does not require output_fn
    normalization for stability.  Intended to be a more biologically
    plausible version of the Oja rule.
    """
   
    def __call__(self,input_activity, unit_activity, weights, single_connection_learning_rate):
	"""
        Update the value of the given weights matrix based on the
        input_activity matrix (of the same size as the weights matrix),
        the response of this unit (the unit_activity), and the previous weights 
   	matrix governed by a per-connection learning rate.
	"""

        weights += single_connection_learning_rate * unit_activity * (input_activity - weights);


class BCMFixed(LearningFn):
    """
    Bienenstock, Cooper, and Munro (1982) learning rule with a fixed threshold.

    (See Dayan and Abbott, 2001, equation 8.12) In the BCM rule,
    activities change only when there is both pre- and post-synaptic
    activity.  The full BCM rule requires a sliding threshold (see
    CFPBCM), but this version is simpler and easier to analyze.

    Requires some form of output_fn normalization for stability.
    """

    unit_threshold=Number(default=0.5,bounds=(0,None),doc="Threshold between LTD and LTP.")
    def __call__(self,input_activity, unit_activity, weights, single_connection_learning_rate):
        weights += single_connection_learning_rate * unit_activity * input_activity * (unit_activity-self.unit_threshold)

##  ## JABHACKALERT: Untested
##  class CFPBCM(CFPLearningFn):
##      """
##      Bienenstock, Cooper, and Munro (1982) learning rule with sliding threshold.
##      
##      (See Dayan and Abbott, 2001, equation 8.12, 8.13).
##  
##      Activities change only when there is both pre- and post-synaptic activity.
##      Threshold is adjusted based on recent firing rates.
##      """
##      single_cf_fn = LearningFnParameter(default=Hebbian())
##      
##      unit_threshold_0=Number(default=0.5,bounds=(0,None),
##          doc="Initial value of threshold between LTD and LTP; actual value computed based on recent history.")
##      unit_threshold_learning_rate=Number(default=0.1,bounds=(0,None),
##          doc="Amount by which the unit_threshold is adjusted for each activity calculation.")
##  
##      def __call__(self, cfs, input_activity, output_activity, learning_rate, **params):
##          # Initialize thresholds the first time we learn the size of the output_activity.
##          if not hasattr(self,'unit_thresholds'):
##              self.unit_thresholds=ones(output_activity.shape,Float32)*self.unit_threshold_0
##              self.unit_thresholds.savespace(1)
##  
##          rows,cols = output_activity.shape
##  
##          # JABALERT: Is this correct?
##  	single_connection_learning_rate = self.constant_sum_connection_rate(cfs,learning_rate)
##  
##          # avoid evaluating these references each time in the loop
##          single_cf_fn = self.single_cf_fn
##  	for r in xrange(rows):
##              for c in xrange(cols):
##                  cf = cfs[r][c]
##                  input_activity = cf.get_input_matrix(input_activity)
##                  unit_activity = output_activity[r,c]
##                  threshold=self.unit_thresholds[r,c]
##                  print cf.weights, type(cf.weights)
##                  print input_activity, type(input_activity)
##                  print single_connection_learning_rate,unit_activity,threshold, (unit_activity-threshold)
##                  cf.weights += (single_connection_learning_rate * unit_activity * (unit_activity-threshold)) * input_activity 
##                  self.unit_thresholds[r,c] += self.unit_threshold_learning_rate*(unit_activity*unit_activity-threshold)
##  
##                  # CEBHACKALERT: see ConnectionField.__init__()
##                  cf.weights *= cf.mask
##      
##  
##  
##  # Inappropriately shares the history between units; needs to be modified to be a CFPTrace learning rule
##  class Trace(LearningFn):
##      """
##      Trace learning rule; Foldiak (1991), Sutton and Barto (1981), Wallis and Rolls (1997).
##  
##      Incorporates a trace of recent activity into the learning
##      function, instead of learning based only on the current activity
##      as in strict Hebbian learning.
##  
##      Requires some form of output_fn normalization for stability.
##      """
##      
##      trace_strength=Number(default=0.5,bounds=(0.0,1.0),doc="How much the learning is dominated by the activity trace, relative to the current value.")
##      
##      def __init__(self,**params):
##          super(Trace,self).__init__(**params)
##          self.trace=0
##      
##      def __call__(self,input_activity, unit_activity, weights, single_connection_learning_rate):
##          trace = (1-self.trace_strength)*unit_activity+self.trace_strength*self.trace
##          weights += single_connection_learning_rate * trace * input_activity




