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
import __main__

SLEEP_EXCEPTION = "Sleep Exception"
STOP = "Simulator Stopped"

class Simulator(TopoObject):
    """
    A class to manage a simulation.  A simulator object manages the
    event queue, simulation clock, and list of EventProcessors, dispatching
    events to them in time order, and moving the simulation clock as needed.    
    """

    step_mode = Parameter(default=False)
    
    def __init__(self,**config):
        """
        The simulator constructor takes one keyword parameter:
        
           step_mode = debugging flag, causing the simulator to stop
                       before each tick.
        """
        super(Simulator,self).__init__(**config)

        self.__time = 0
        self.__event_processors = []
        self.__sleep_window = 0
        self.__sleep_window_violation = False
        self.__scheduler = sched.scheduler(self.time,self.sleep)
        
        
    def run(self,duration=0,until=0):
        """
        Run the simulator.   Call .start() for each EventProcessor, and
        start the event scheduler.
        parameters:
          duration = time to run in simulator time. Default: run indefinitely.
          until    = time to stop in simulator time. Default: run indefinitely.
          (note if both duration an until are used, they both will apply.)
        """
        for node in self.__event_processors:
            node.start()
        self.continue_(duration,until)

    def continue_(self,duration=0,until=0):
        if duration:
            self.__scheduler.enter(duration,0,self.stop,[])
        if until:
            self.__scheduler.enterabs(until,0,self.stop,[])
        try:
            keep_running = True
            while keep_running:
                keep_running = False
                try:
                    self.__scheduler.run()
                except SLEEP_EXCEPTION:
                    self.debug("SLEEP EXCEPTION")
                    self.__sleep_window_violation = False
                    self.__sleep_window = 0
                    keep_running = True
        except STOP:
            self.message("Simulation stopped at time %f" % self.time())
        except EOFError:
            self.message("Simulation stopped at time %f" % self.time())
        except KeyboardInterrupt:
            self.message("Simulation stopped at time %f" % self.time())

    def stop(self):
        raise STOP

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
        # If this event is scheduled when the simulator is about to sleep,
        # make sure that the event isn't being scheduled during the sleep window,
        # if it is, indicate a violation.
        if self.__sleep_window and delay < self.__sleep_window:
            self.__sleep_window_violation = True
        # now schedule the event
        self.__scheduler.enter(delay,1,self.__dispatch,(self.time()+delay,src,src_port,dest,dest_port,data))

    def enqueue_event_abs(self,time,src,dest,src_port=None,dest_port=None,data=None):
        """
        Like enqueue_event_rel, except it schedules the event for some
        absolute time.
        """
        # If this event is scheduled when the simulator is about to sleep,
        # make sure that the event isn't being scheduled during the sleep window,
        # if it is, indicate a violation.
        if self.__sleep_window and (self.time() <= time < self.time()+self.__sleep_window):
            self.__sleep_window_violation = True
        # now schedule the event
        self.__scheduler.enterabs(time,1,self.__dispatch,(time,src,src_port,dest,dest_port,data))

    def __dispatch(self,time,src,src_port,dest,dest_port,data):
        """
        Dispatch an event to dest.
        """
        if time < self.time():
            self.warning("Ignoring stale event from",src,"to",dest,
                         "scheduled for time",time,"processed at time",self.time())
        else:
            dest.input_event(src,src_port,dest_port,data)

    def get_event_processors(self):
        """Return the list of event processors such as Sheets."""
        return self.__event_processors

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

        if delay > 0:
            # set the sleep window, so the event scheduling methods know
            # that we're about to sleep, and for how long.
            self.__sleep_window = delay
            for ep in self.__event_processors:
                # give each EP a chance to send some events
                ep.pre_sleep()

            # if an event was scheduled to occur during the time we're
            # supposed to be asleep, then raise an exception -- the
            # top level loop will catch it and rerun to make sure the
            # event gets run.
            if self.__sleep_window_violation:
                raise SLEEP_EXCEPTION

            if self.step_mode:
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
    
    def pre_sleep(self):
        """
        Called by the simulator before sleeping.  Allows the event processor
        to send any events that must be sent before time advances.
        (by default, do nothing)
        """
        pass
    


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
                message(`self` + ' firing, amplitude = ' + `self.amplitude`)


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


##################################################################################
if __name__ == '__main__':

    import base
    
    base.min_print_level = base.DEBUG

    s = Simulator(step_mode = 1)

    class Printer(EventProcessor):
        def input_event(self,src,src_port,dest_port,data):
            self.message("Recieved",data,"from",src,".")
        

    pulse1 = PulseGenerator(period = 1)
    pulse2 = PulseGenerator(period = 3)
    sum = SumUnit()
    out = Printer(name="OUTPUT")
    
    s.connect(pulse1,sum,delay=1)
    s.connect(pulse2,sum,delay=1)
    s.connect(sum,out,delay=0)

    
    s.run()
