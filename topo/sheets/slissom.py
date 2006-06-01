"""
The SLISSOM class.

$Id$
"""
__version__='$Revision$'

import Numeric

from math import exp
from topo.base.parameterclasses import BooleanParameter, Number, Integer
from lissom import LISSOM


class SLISSOM(LISSOM):
    """
    A Sheet class implementing the SLISSOM algorithm
    (Choe and Miikkulainen, Neurocomputing 21:139-157, 1998).

    A SLISSOM sheet is a LISSOM sheet to include spiking neurons
    using dynamic synapses.
    """

    # configurable parameters
    threshold = Number(default=0.3,bounds=(0,None), doc="Baseline threshold")
    decay_rate = Number(default=0.01,bounds=(0,None), \
		doc="Dynamic threshold decay rate")
    absolute_refractory = Number(default=1.0,bounds=(0,None), \
		doc="Absolute refractory period")
    dynamic_threshold_init = Number(default=2.0,bounds=(0,None), \
		doc="Initial value for dynamic threshold when spike occurs")
    spike_amplitude = Number(default=1.0,bounds=(0,None), \
		doc="Amplitude of spike at the moment of spiking")

    # matrices for internal use
    dynamic_threshold = None
    spike = None
    spike_history= None

    def __init__(self,**params):
	"""
	SLISSOM-specific init, where dynamic threshold stuff
	gets initialized. 
	"""
	super(SLISSOM,self).__init__(**params)
	self.dynamic_threshold = Numeric.zeros(self.activity.shape)	
	self.spike = Numeric.zeros(self.activity.shape)	
	self.spike_history = Numeric.zeros(self.activity.shape)	

    def activate(self):
	"""
	For now, this is the same as the parent's activate(), plus
	fixed thresholding. Overloading was necessary to
	avoid self.send_output() being invoked before thresholding.
	"""
	
	# copy from grandparent
        self.activity *= 0.0

        for proj in self.in_connections:
            self.activity+= proj.activity

        if self.apply_output_fn:
            self.output_fn(self.activity)

	# Thresholding: baseline + dynamic threshold + absolute refractory 
	# period
        rows,cols = self.activity.shape

        for r in xrange(rows):
            for c in xrange(cols):

		thresh = self.threshold + self.dynamic_threshold[r,c]

                if (self.activity[r,c] > thresh and self.spike_history[r,c]<=0):
                    self.activity[r,c] = self.spike_amplitude
		    self.dynamic_threshold[r,c] = self.dynamic_threshold_init
		    # set absolute refractory period for "next" timestep
		    # (hence the "-1")
		    self.spike_history[r,c] = self.absolute_refractory-1
                else:
                    self.activity[r,c] = 0.0
		    self.dynamic_threshold[r,c] = \
			self.dynamic_threshold[r,c] * exp(-self.decay_rate)
		    self.spike_history[r,c] -= 1

        self.send_output(data=self.activity)

