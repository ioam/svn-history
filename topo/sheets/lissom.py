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
from topo.base.utils import PLTF
from topo.base.learningrules import hebbian_c,hebbian_div_norm_c
from topo.transferfns.basic import PiecewiseLinear

class LISSOM(CFSheet):

    # Should be changed to a TransferFunctionParameter
    transfer_fn = Parameter(default=PiecewiseLinear(lower_bound=0.1,upper_bound=0.65))
    learning_fn = Parameter(default=hebbian_c)

    # modify weights after each activation?
    continuous_learning = Parameter(default=False)

    presleep_count = 0

    tsettle=8

    def input_event(self,src,src_port,dest_port,data):
        # On a new afferent input, clear the activity
        if src.name == 'Retina':
            self.activity *= 0.0
            for name in self.projections:
                for proj in self.projections[name]:
                    proj.activity *= 0.0

        super(LISSOM,self).input_event(src,src_port,dest_port,data)

    def pre_sleep(self):
        """
        Pass the accumulated stimulation through self.transfer_fn and
        send it out on the default output port.
        """

        iteration_done = False
        self.presleep_count += 1

	if self.presleep_count == self.tsettle+1: #end of an iteration
            iteration_done = True

        if self.new_input:
            self.new_input = False
            self.activity *= 0.0
            for name in self.projections:
                for proj in self.projections[name]:
                    self.activity += proj.activity
            self.activity = self.transfer_fn(self.activity)

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
                    

    def learn(self):
        rows,cols = self.activity.shape
        for proj in chain(*self.projections.values()):
            if proj.input_buffer:
                alpha = proj.learning_rate
                if proj.src == self: #lateral connection
                    inp = self.activity
                else:
                    inp = proj.input_buffer

                if self.learning_fn.func_name == "hebbian_c":
                    # hebbian_c is an function for the whole sheet
                    cfs = proj.cfs
                    len, len2 = inp.shape
		    if proj.normalize:
                        # Hebbian learning with divisive normalization per 
                        # projection. It is much faster to do both of them
                        # in one function.
			if proj.normalize_fn.func_name == "divisive_normalization":
                            hebbian_div_norm_c(inp, self.activity, rows, cols, len, cfs, alpha)
                        else:
                            hebbian_c(inp, self.activity, rows, cols, len, cfs, alpha)
			    norm = proj.normalize
                            for r in range(rows):
                                for c in range(cols):
                                    proj.normalize_fn(cfs[r][c].weights)
                    else:
                        hebbian_c(inp, self.activity, rows, cols, len, cfs, alpha)
                else:
                    # apply learning rule and normalization to each unit
                    norm = proj.normalize
                    for r in range(rows):
                        for c in range(cols):
                            cf = proj.cf(r,c)
                            self.learning_fn(cf.get_input_matrix(inp), self.activity[r,c], cf.weights, alpha)
                            if norm:
                                proj.normalize_fn(cf.weights)


    def lateral_projections(self):
        return [p for p in chain(*self.projections.values()) if p.src is self]
    def afferent_projections(self):
        return [p for p in chain(*self.projections.values()) if p.src is not self]

    def reduce_cfsize(self, name, new_wt_bounds):
        for proj in chain(*self.projections.values()):
            if proj.name == name:
                proj.reduce_cfsize(new_wt_bounds)
                return
        self.warning("Can't find ", name)

    def change_learning_rate(self, name, new_alpha):
        for proj in chain(*self.projections.values()):
            if proj.name == name:
                proj.learning_rate = new_alpha
                return
        self.warning("Can't find ", name)


    # print the weights of a unit
    def printwts(self,x,y):
        for proj in chain(*self.projections.values()):
            print proj.name, x, y
            print transpose(proj.cfs[x][y].weights)
