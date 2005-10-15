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
from topo.base.parameter import Parameter
from topo.outputfns.basic import PiecewiseLinear
from topo.learningfns.basic import DivisiveHebbian,GenericCFLF

class LISSOM(CFSheet):

    # Should be changed to a OutputFunctionParameter
    output_fn = Parameter(default=PiecewiseLinear(lower_bound=0.1,upper_bound=0.65))
    learning_fn = Parameter(default=DivisiveHebbian())

    # modify weights after each activation?
    continuous_learning = Parameter(default=False)

    presleep_count = 0

    tsettle=8


    def input_event(self,src,src_port,dest_port,data):
        # On a new afferent input, clear the activity
        if src.name == 'Retina':
            self.activity *= 0.0
            for proj in self.connections:
                if proj.dest is self:
                    proj.activity *= 0.0

        super(LISSOM,self).input_event(src,src_port,dest_port,data)


    ### JABALERT: Should change to activate() instead
    def pre_sleep(self):
        """
        Pass the accumulated stimulation through self.output_fn and
        send it out on the default output port.
        """

        iteration_done = False
        self.presleep_count += 1

	if self.presleep_count == self.tsettle+1: #end of an iteration
            iteration_done = True

        if self.new_input:
            self.new_input = False
            self.activity *= 0.0
            for proj in self.connections:
                if proj.dest is self:
                    self.activity += proj.activity
            self.activity = self.output_fn(self.activity)

            # don't send output when an iteration has ended
            if not iteration_done: 
                self.send_output(data=self.activity)

        if self.learning:
            if self.continuous_learning:
                self.learn()
            else:
                if iteration_done:
                    self.presleep_count = 0
                    self.learn()
                    

    ### JABHACKALERT! Can this function now be moved to the base class?
    ### I.e., is there anything LISSOM-specific about it now?
    def learn(self):
        rows,cols = self.activity.shape
        for proj in self.connections:
            if proj.input_buffer and proj.dest is self:
                alpha = proj.learning_rate
                ### JABHACKALERT!  Why is this test necessary?
                if proj.src == self: #lateral connection
                    inp = self.activity
                else:
                    inp = proj.input_buffer

                cfs = proj.cfs
                len, len2 = inp.shape
                self.learning_fn(inp, self.activity, rows, cols, len, cfs, alpha)


    def lateral_connections(self):
        return [p for p in self.connections if p.src is self]
    def afferent_connections(self):
        return [p for p in self.connections if p.src is not self]

    def reduce_cfsize(self, name, new_wt_bounds):
        for proj in self.connections:
            if proj.name == name:
                proj.reduce_cfsize(new_wt_bounds)
                return
        self.warning("Can't find ", name)

    ### JABALERT: Should be able to eliminate this by just providing a 
    ### convenient way for callers to access projections.
    def change_learning_rate(self, name, new_alpha):
        for proj in self.connections:
            if proj.name == name:
                proj.learning_rate = new_alpha
                return
        self.warning("Can't find ", name)


    # print the weights of a unit
    def printwts(self,x,y):
        for proj in self.connections:
            print proj.name, x, y
            print transpose(proj.cfs[x][y].weights)
