"""
A prototype event-based simulator module.

A simulation is structured as directed graph of event-processing nodes
called EventProcessors.  EventProcessors generate data-carrying
events, which are routed through the graph to other EventProcessors
via delayed connections.

The simulator is modular: EventProcessors can be any kind of object
that supports the (still evolving) interface for accepting and
processing events, but in practice should inherit from class
EventProcessor.  EventProcessors are responsible for managing their
own connections.

Formally, an event is a tuple: (time,src,dest,port,data), where

  time = The time at which the event should be delivered, an arbitrary
         floating point value.
  src  = The EventProcessor from which the event originated.
  dest = Destination EventProcessor of the event
  port = The destination port of the event.  Ports are arbitrary
         'addresses' within an EventProcessor.  In principle, they can be any
         kind of Python value, but in practice they are likely to be
         strings, or None.
  data = The event data to be delivered.  Can be anything.


A simulation begins by giving each EventProcessor an opportunity to
send any initial events.  It then proceeds by processing and
delivering events in time order.  After all events for the current
time are processed, simulation time skips to the time of earliest
event remaining in the queue.

$Id$
"""


import sched
from base import TopoObject
from params import Parameter

PAUSE = "Simulator Paused"

class Simulator(TopoObject):
    """
    A class to manage a simulation.  A simulator object manages the
    event queue, simulation clock, and list of EventProcessors, dispatching
    events to them in time order, and moving the simulation clock as needed.    
    """

    step_mode = Parameter(0)
    
    def __init__(self,**config):
        """
        The simulator constructor takes one keyword parameter:
        
           step_mode = debugging flag, causing the simulator to stop
                       before each tick.
        """
        super(Simulator,self).__init__(**config)

        self.__time = 0
        self.__event_processors = []

        self.__scheduler = sched.scheduler(self.time,self.sleep)
        
        
    def run(self,dur=0):
        """
        Run the simulator.   Call .start() for each EventProcessor, and
        start the event scheduler.
        """
        for node in self.__event_processors:
            node.start()
        self.cont(dur)

    def cont(self,dur=0):
        if dur:
            self.__scheduler.enter(dur,0,self.pause,[])
        try:
            self.__scheduler.run()
        except PAUSE:
            print "Paused"
        except EOFError:
            print "Paused"
        except KeyboardInterrupt:
            print "Paused"

    def pause(self):
        raise PAUSE

    def add(self,*EPs):
        """
        Add one or more EventProcessors to the simulator.
        Note, EventProcessors do not necessarily
        have to be added to the simulator to be used in a simulation,
        but they will not receive the start() message.  Adding a node
        to the simulator also sets the backlink node.simulator, so
        that the node can enqueue events and read the simulator clock.
        """
        for ep in EPs:
            if not ep in self.__event_processors:
                self.__event_processors.append(ep)
                ep.simulator = self


    def connect(self,
                src=None,
                dest=None,
                src_port=None,
                dest_port=None,
                delay=0):
        """
        Connect the source to the destination, at the appropriate ports,
        if any are given.  If src and dest have not been added to the
        simulator, they will be added.
        """
        self.add(src,dest)
        src._connect_to(dest,src_port=src_port,dest_port=dest_port, delay=delay)
        dest._connect_from(src,src_port=src_port,dest_port=dest_port)

    def enqueue_event_rel(self,delay,src,dest,src_port=None,dest_port=None,data=None):
        """
        Enqueue an event for a specified delay from the current time.
          delay = event delay
          src   = source EP of event
          dest  = destination EP of event
          src_port   = source port (default None)
          dest_port  = destination port (default None)
          data  = event data (default None)
        """
        self.__scheduler.enter(delay,1,self.__dispatch,(src,src_port,dest,dest_port,data))

    def enqueue_event_abs(self,time,src,dest,src_port=None,dest_port=None,data=None):
        """
        Like enqueue_event_rel, except it schedules the event for some
        absolute time.
        """
        self.__scheduler.enterabs(time,1,self.__dispatch,(src,src_port,dest,dest_port,data))

    def __dispatch(self,src,src_port,dest,dest_port,data):
        """
        Dispatch an event to dest.
        """
        dest.input_event(src,src_port,dest_port,data)
        
    def time(self):
        """
        Return the current simulation time.
        """
        return self.__time
    
    def sleep(self,delay):
        """
        Sleep in simulator time.  Skip the clock ahead by delay
        units.  If self.step_mode, pause and wait for input before continuing.
        """
        if self.step_mode and delay > 0:
            raw_input("\nsimulator time = %f: " % self.time())
        self.__time += delay
        


class EventProcessor(TopoObject):
    """
    Base class for EventProcessors.  Handles basic mechanics of connections and
    sending events.
    """
    def __init__(self,**config):
        super(EventProcessor,self).__init__(**config)
        self.connections = {None:[]}
        

    def _connect_to(self,dest,src_port=None,dest_port=None,delay=0):
        """
        Add a connection to dest/port with a delay (default=0).
        """
        if not src_port in self.connections:
            self.connections[src_port] = []

        self.connections[src_port].append((dest,dest_port,delay))

    def _connect_from(self,src,src_port=None,dest_port=None):
        pass

    def start(self):
        """
        Called by the simulator when a new simulation starts.  By
        default, do nothing. 
        """
        pass

    def send_output(self,src_port=None,data=None):
        """
        Send some data out all connections.
        """
        for dest,dest_port,delay in self.connections[src_port]:
            self.simulator.enqueue_event_rel(delay,self,dest,src_port,dest_port,data)

    def input_event(self,src,src_port,dest_port,data):
        """
        Called by the simulator to dispatch an event on the given port
        from src.  (By default do nothing)
        """
        pass
        


class PulseGenerator(EventProcessor):
    
    """
    
    A simple pulse generator node.

    Parameters:
      amplitude = The size of the pulse to generate. (default 1.0)
      period    = The period with which to repeat the pulse. (defalut 0.0)
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
    
    def __init__(self,**config):
        EventProcessor.__init__(self,**config)
        setup_params(self,PulseGenerator,**config)

        if self.period:
            self.connect_to(self,delay=self.period)
        
    def input_event(self,src,src_port,dest_port,data):
        """
        On input from self, generate output. Ignore all other inputs.
        """
        print '%s received event from %s on port %s with data %s' % (`self`,`src`,`port`,`data`)
        self.send_output(data=self.amplitude)
        
    def start(self):        
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
    threshold = Parameter(1.0)
    accum     = Parameter(0.0)
    amplitude = Parameter(1.0)

    def __init__(self,**config):
        EventProcessor.__init__(self,**config)
        setup_params(self,ThresholdUnit,config)

    def input_event(self,src,src_port,dest_port,data):
        if port == 'input':
            self.accum += data
            print '%s received %d, accumulator now %d' % (`self`,data,self.accum)
            if self.accum > self.threshold:
                self.send_output(data=self.amplitude)
                self.accum = 0
                print `self` + ' firing, amplitude = ' + `self.amplitude`





##################################################################################
if __name__ == '__main__':


    s = Simulator(step_mode = 1)

    pulse = PulseGenerator(period = 0.10, phase = 0.003)
    sum1 = ThresholdUnit(threshold = 5)
    sum2 = ThresholdUnit(threshold = 2)
    
    s.add(pulse,sum1,sum2)
    connect(pulse,sum1,dest_port='input',delay = 0.1)
    connect(sum1,sum2,dest_port='input',delay = 0.1)
    connect(sum2,sum1,dest_port='input',delay = 0.1)

    s.run()
