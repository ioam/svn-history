"""
Scalar EPs

Some EventProcessors that emit and accept scalar events, e.g. pulses.
Mostly useful for testing the simulator.  Also possibly for
constructing single-unit simulations.

$Id$
"""
from topo.params import *
from topo.simulator import *

class PulseGenerator(EventProcessor):

    """

    A simple pulse generator node.

    Parameters:
      amplitude = The size of the pulse to generate. (default 1.0)
      period    = The period with which to repeat the pulse. (default 0.0)
                  If zero, the pulse will be sent exactly once.
      phase     = The time after starting the simulation to wait before
                  sending the first pulse. (default 0.0)

    Produces pulses (scalars) of a fixed amplitude at a fixed
    frequency and phase.  Period and phase simulation time intervals.
    If period is omitted or set to 0, a single pulse is sent, offset
    from the start of the simulation by the phase.

    """

    amplitude = Parameter(1)
    period    = Parameter(0)
    phase     = Parameter(0)

    def input_event(self,src,src_port,dest_port,data):
        """
        On input from self, generate output. Ignore all other inputs.
        """
        self.verbose('received event from',src,'on port',dest_port,'with data',data)
        self.send_output(data=self.amplitude)

    def start(self):
        if self.period:
            self.simulator.connect(self,self,delay=self.period)
        self.simulator.enqueue_event_rel(self.phase,self,self)
        EventProcessor.start(self)


class ThresholdUnit(EventProcessor):
    """

    A simple pulse-accumulator threshold node.

    Parameters:
       threshold = (default 1.0) The threshold at which to fire.
       amplitude = (default 1.0) The size of the pulse to generate.
       accum     = (default 0.0) The initial accumulator value

    Accumulates incoming pulses.  When the accumulated value rises
    above threshold, it generates a pulse of a given amplitude and
    resets the accumulator to zero.

    """
    threshold     = Parameter(default=1.0)
    initial_accum = Parameter(default=0.0)
    amplitude     = Parameter(default=1.0)

    def __init__(self,**config):
        EventProcessor.__init__(self,**config)
        self.accum = self.initial_accum

    def input_event(self,src,src_port,dest_port,data):
        if dest_port == 'input':
            self.accum += data
            self.verbose( 'received',data,'accumulator now',self.accum)
            if self.accum > self.threshold:
                self.send_output(data=self.amplitude)
                self.accum = 0
                print `self` + ' firing, amplitude = ' + `self.amplitude`

class SumUnit(EventProcessor):
    """
    A simple sum unit.
    """
    def __init__(self,**params):
        super(SumUnit,self).__init__(**params)
        self.value = 0.0

    def input_event(self,src,src_port,dest_port,data):
        self.value += data
        self.debug("recieved",data,"from",src,"value =",self.value)

    def pre_sleep(self):
        self.debug("pre_sleep called, time =",self.simulator.time(),"value =",self.value)
        if self.value:
            self.debug("Sending output:",self.value)
            self.send_output(data=self.value)
            self.value = 0.0

