"""
A Sheet class implementing the LISSOM algorithm
(Sirosh and Miikkulainen, Biological Cybernetics 71:66-78, 1994).

$Id$
"""
__version__='$Revision$'

import Numeric

from itertools import chain

from topo.base.connectionfield import CFSheet
from topo.base.parameter import Parameter, BooleanParameter
from topo.base.topoobject import TopoObject
from topo.misc.inlinec import optimized
from topo.outputfns.basic import PiecewiseLinear


class LISSOM(CFSheet):

    # Should be changed to a OutputFunctionParameter
    output_fn = Parameter(default=PiecewiseLinear(lower_bound=0.1,upper_bound=0.65))
    
    # modify weights after each activation?
    continuous_learning = BooleanParameter(default=False)

    presleep_count = 0
    new_iteration = True

    tsettle=8

    def input_event(self,src,src_port,dest_port,data):
        # On a new afferent input, clear the activity
        if self.new_iteration:
            self.new_iteration = False
            self.activity *= 0.0
            for name in self.in_projections:
                for proj in self.in_projections[name]:
                    proj.activity *= 0.0

        super(LISSOM,self).input_event(src,src_port,dest_port,data)


    def pre_sleep(self):
        """
        Pass the accumulated stimulation through self.output_fn and
        send it out on the default output port.
        """

        iteration_done = False
        self.presleep_count += 1

	if self.presleep_count == self.tsettle+2: #end of an iteration
            iteration_done = True
            self.presleep_count = 0
            self.new_iteration = True # used by input_event when it is called

        if self.new_input: 
            self.new_input = False
            # The last iteration is for learning and does not need to compute
	    # the activity.
	    if not iteration_done:
                self.activate()

            if self.learning:
                if self.continuous_learning:
                    self.learn()
                else:
                    if iteration_done:
                        self.learn()
                   

    # print the weights of a unit
    def printwts(self,x,y):
        for proj in chain(*self.in_projections.values()):
            print proj.name, x, y
            print proj.cfs[x][y].weights



class LISSOM_CPointer(LISSOM):
    """
    LISSOMPointer implements the same algorithm as LISSOM, but it uses a
    special learning function (DivisiveHebbian_CPointer) for faster execution 
    time. This requires all the connections between the sheets are instances of 
    CFProjection_CPointer (specified via connect()).
    """

    def __init__(self,**params):
        super(LISSOM_CPointer,self).__init__(**params)


    def learn(self):
        rows,cols = self.activity.shape
        for proj in chain(*self.in_projections.values()):
            if proj.input_buffer:
                learning_rate = proj.learning_rate
                inp = proj.input_buffer

                cfs = proj.cfs
                len, len2 = inp.shape
                proj.learning_fn(cfs, inp, self.activity, learning_rate, weight_ptrs=proj.weight_ptrs, slice_ptrs=proj.slice_ptrs)

# Optimized version overwrites the unoptimized version name if the
# code is in the optimized state.
if not optimized:
    LISSOM_CPointer = LISSOM
    TopoObject().message('Optimized LISSOM_CPointer not being used.')
