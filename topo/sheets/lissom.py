"""
A Sheet class implementing the LISSOM algorithm
(Sirosh and Miikkulainen, Biological Cybernetics 71:66-78, 1994).

$Id$
"""
__version__='$Revision$'

import Numeric

from itertools import chain

from topo.base.connectionfield import CFSheet
from topo.base.parameterclasses import BooleanParameter, Number, Integer
from topo.base.projection import OutputFunctionParameter
from topo.base.parameterizedobject import ParameterizedObject
from topo.misc.inlinec import optimized
from topo.outputfns.basic import PiecewiseLinear


class LISSOM(CFSheet):


    output_fn = OutputFunctionParameter(default=PiecewiseLinear(lower_bound=0.1,
                                                                upper_bound=0.65))
    # modify weights after each activation?
    continuous_learning = BooleanParameter(default=False)

    activation_count = 0
    new_iteration = True

    precedence = Number(0.6)
    tsettle=Integer(default=8,bounds=(0,None),doc=
                    """
                    Number of times to activate the LISSOM sheet for each external input event.
                    
                    A counter is incremented each time an input is received from any
                    source, and once the counter reaches tsettle, the last activation
                    step is skipped so that there will not be any further recurrent
                    activation.  The next external (i.e., afferent or feedback)
                    event will then start the counter over again.
                    """)


    def input_event(self,src,src_port,dest_port,data):
        # On a new afferent input, clear the activity
        if self.new_iteration:
            self.new_iteration = False
            self.activity *= 0.0
            for name in self.in_projections:
                for proj in self.in_projections[name]:
                    proj.activity *= 0.0

        super(LISSOM,self).input_event(src,src_port,dest_port,data)


    ### JABHACKALERT!  There should be some sort of warning when
    ### tsettle times the input delay is larger than the input period.
    ### Right now it seems to do strange things in that case (settle
    ### at all after the first iteration?), but of course that is
    ### arguably an error condition anyway (and should thus be
    ### flagged).
    def pre_sleep(self):
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
        for proj in chain(*self.in_projections.values()):
            print proj.name, x, y
            print proj.cfs[x][y].weights
