"""
A Sheet class implementing the LISSOM algorithm
(Sirosh and Miikkulainen, Biological Cybernetics 71:66-78, 1994).

$Id$
"""
import weave
import Numeric

from itertools import chain

import topo

from topo.base.connectionfield import CFSheet
from topo.base.parameter import Parameter, BooleanParameter
from topo.outputfns.basic import PiecewiseLinear
from topo.learningfns.basic import DivisiveHebbian,GenericCFLF,DivisiveHebbianP

class LISSOM(CFSheet):

    # Should be changed to a OutputFunctionParameter
    output_fn = Parameter(default=PiecewiseLinear(lower_bound=0.1,upper_bound=0.65))
    learning_fn = Parameter(default=DivisiveHebbian())
    
    # modify weights after each activation?
    continuous_learning = BooleanParameter(default=False)

    presleep_count = 0

    tsettle=8

    def input_event(self,src,src_port,dest_port,data):
        ### JABHACKALERT!  What is this?! We can't have any such
        ### calculation based on the name of the src, because the user
        ### can name the input sheet anything he likes!  What will
        ### happen when there are multiple Retinas, or an LGN, or
        ### hierarchical maps, or anything else like that?!?!  The
        ### resetting needs to be done based on the tsettle value, or
        ### something else that we can actually trust; we can't trust
        ### the name of the input sheet in any way.
        
        # On a new afferent input, clear the activity
        if src.name == 'Retina':
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
                        self.presleep_count = 0
                        self.learn()
                   
    # CEBHACKALERT:
    # this is going to projections.py...
    def projections(self):
        return dict([(p.name,p) for p in chain(*self.in_projections.values())])


    # print the weights of a unit
    def printwts(self,x,y):
        for proj in chain(*self.in_projections.values()):
            print proj.name, x, y
            print proj.cfs[x][y].weights



class LISSOMPointer(LISSOM):
    """
    LISSOMPointer implements the same algorithm as LISSOM, but it uses a
    special learning function (DivisiveHebbianP) for faster execution time.
    This requires all the connections between the sheets are instances of 
    KernelPointerProjection (specified via connect()).
    
    """

    learning_fn = Parameter(default=DivisiveHebbianP())

    def __init__(self,**params):
        super(LISSOMPointer,self).__init__(**params)


    def learn(self):
        rows,cols = self.activity.shape
        for proj in chain(*self.in_projections.values()):
            if proj.input_buffer:
                alpha = proj.learning_rate
                inp = proj.input_buffer

                cfs = proj.cfs
                len, len2 = inp.shape
                self.learning_fn(inp, self.activity, rows, cols, len, cfs, alpha, weight_ptrs=proj.weight_ptrs, slice_ptrs=proj.slice_ptrs)

