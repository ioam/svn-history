"""
The LISSOM class.

$Id$
"""
__version__='$Revision$'

import Numeric

from topo.base.cf import CFSheet
from topo.base.parameterclasses import BooleanParameter, Number, Integer
from topo.base.projection import OutputFnParameter
from topo.base.parameterizedobject import ParameterizedObject
from topo.misc.inlinec import optimized
from topo.outputfns.basic import PiecewiseLinear


class LISSOM(CFSheet):
    """
    A Sheet class implementing the LISSOM algorithm
    (Sirosh and Miikkulainen, Biological Cybernetics 71:66-78, 1994).

    A LISSOM sheet is a CFSheet slightly modified to enforce a fixed
    number of settling steps.  Settling is controlled by the tsettle
    parameter; once that number of settling steps has been reached, an
    external input is required before the sheet will activate again.
    """

    tsettle=Integer(default=8,bounds=(0,None),doc="""
       Number of times to activate the LISSOM sheet for each external input event.
       
       A counter is incremented each time an input is received from any
       source, and once the counter reaches tsettle, the last activation
       step is skipped so that there will not be any further recurrent
       activation.  The next external (i.e., afferent or feedback)
       event will then start the counter over again.""")

    continuous_learning = BooleanParameter(default=False, doc="""
       Whether to modify the weights after every settling step.
       If false, waits until settling is completed before doing learning.""")

    output_fn = OutputFnParameter(default=PiecewiseLinear(lower_bound=0.1,upper_bound=0.65))
    precedence = Number(0.6)
    
    activation_count = 0
    new_iteration = True

    def input_event(self,conn,data):
        # On a new afferent input, clear the activity
        if self.new_iteration:
            self.new_iteration = False
            self.activity *= 0.0
            for proj in self.in_connections:
                proj.activity *= 0.0
                    
        super(LISSOM,self).input_event(conn,data)


    ### JABALERT!  There should be some sort of warning when
    ### tsettle times the input delay is larger than the input period.
    ### Right now it seems to do strange things in that case (settle
    ### at all after the first iteration?), but of course that is
    ### arguably an error condition anyway (and should thus be
    ### flagged).
    def process_current_time(self):
        """
        Pass the accumulated stimulation through self.output_fn and
        send it out on the default output port.
        """
        if self.new_input:
            self.new_input = False
    	    if self.activation_count == self.tsettle:
                # Once we have been activated the required number of times
                # (determined by tsettle), reset various counters, learn
                # if appropriate, and avoid further activation until an
                # external event arrives.
                self.activation_count = 0
                self.new_iteration = True # used by input_event when it is called
                if (self.learning and not self.continuous_learning):
                    self.learn()
            else:
                self.activate()
                self.activation_count += 1
                if (self.learning and self.continuous_learning):
                   self.learn()
                   

    # print the weights of a unit
    def printwts(self,x,y):
        for proj in self.in_connections:
            print proj.name, x, y
            print proj.cfs[x][y].weights
