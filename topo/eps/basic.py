"""
Basic scalar EventProcessors

This file contains some EventProcessors that emit and accept scalar
events, e.g. pulses.  These are not currently used in the sample
simulations, but can be useful for testing purposes and for controlling
other types of simulations.

$Id$
"""
__version__='$Revision$'

from topo.base.parameterclasses import Number
from topo.base.simulation import EventProcessor,EPConnectionEvent

class PulseGenerator(EventProcessor):

    """
    A simple pulse generator node.  Produces pulses (scalars) of a
    fixed amplitude at a fixed frequency and phase.

    Period and phase are in units of simulation time. Period must be
    greater than zero.
    """
    amplitude = Number(1.0,doc="The size of the pulse to generate.")
    period    = Number(1.0,bounds=(0,None),doc="The period with which to repeat the pulse. Must be greater than zero.")
    phase     = Number(0.0,doc="The time after starting the simulation to wait before sending the first pulse.")

    def input_event(self,conn,data):
        """
        On input from self, generate output. Ignore all other inputs.
        """
        self.verbose("Time " + str(self.simulation.time()) + ":" +
                     " Received event from ",conn.src,'on port',conn.dest_port,'with data',data)
        self.send_output(data=self.amplitude)

    def start(self):
        assert self.period > 0
        conn=self.simulation.connect(self.name,self.name,delay=self.period)
        e=EPConnectionEvent(self.simulation.time()+self.phase, conn)
        self.simulation.enqueue_event(e)
        EventProcessor.start(self)


class ThresholdUnit(EventProcessor):
    """
    A simple pulse-accumulator threshold node.  Accumulates incoming
    pulses.  When the accumulated value rises above threshold, it
    generates a pulse of a given amplitude and resets the accumulator
    to zero.
    """
    threshold     = Number(default=1.0,doc="The threshold at which to fire.")
    initial_accum = Number(default=0.0,doc="The initial accumulator value.")
    amplitude     = Number(default=1.0,doc="The size of the pulse to generate.")

    def __init__(self,**config):
        EventProcessor.__init__(self,**config)
        self.accum = self.initial_accum

    def input_event(self,conn,data):
        if conn.dest_port == 'input':
            self.accum += data
            self.verbose("Time " + str(self.simulation.time()) + ":" +
                         " Receiving ",data,"; accumulator now",self.accum)
            if self.accum > self.threshold:
                self.send_output(data=self.amplitude)
                self.accum = 0
                print `self` + ' firing, amplitude = ' + `self.amplitude`


class SumUnit(EventProcessor):
    """
    A simple unit that outputs the running sum of input received thus far.
    """
    def __init__(self,**params):
        super(SumUnit,self).__init__(**params)
        self.value = 0.0

    def input_event(self,conn,data):
        self.value += data
        self.debug("received",data,"from",conn.src,"value =",self.value)

    def process_current_time(self):
        self.debug("process_current_time called, time =",self.simulation.time(),"value =",self.value)
        if self.value:
            self.debug("Sending output:",self.value)
            self.send_output(data=self.value)
            self.value = 0.0

