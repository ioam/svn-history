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
from utils import inf
import __main__
import topo.gui

SLEEP_EXCEPTION = "Sleep Exception"
STOP = "Simulator Stopped"

# Singleton variable to register which Simulator is currently active in
# the Topographica simulator.  This should not be set directly, but
# through the two accessor functions.  This variable is also used by
# the GUI to know which simulator to drive.
__active_sim = None
def active_sim(): return __active_sim
def set_active_sim(a_sim):
    global __active_sim
    __active_sim = a_sim
    topo.gui.link_to_sim(a_sim)


class Simulator(TopoObject):
    """
    A class to manage a simulation.  A simulator object manages the
    event queue, simulation clock, and list of EventProcessors, dispatching
    events to them in time order, and moving the simulation clock as needed.    
    """

    step_mode = Parameter(default=False)
    register = Parameter(default=True)
    
    def __init__(self,**config):
        """
        The simulator constructor takes one keyword parameter:
        
           step_mode = debugging flag, causing the simulator to stop
                       before each tick.
        """
        super(Simulator,self).__init__(**config)

        self.__time = 0.0
        self.__event_processors = []
        self.__sleep_window = 0.0
        self.__sleep_window_violation = False
        self.__scheduler = sched.scheduler(self.time,self.sleep)
        self.__started = False
        if self.register:
            set_active_sim(self)

        
    def run(self,duration=0,until=0):
        """
        Run the simulator.   Call .start() for each EventProcessor if not
        previously done, and start the event scheduler.
        parameters:
          duration = time to run in simulator time. Default: run indefinitely.
          until    = time to stop in simulator time. Default: run indefinitely.
          (note if both duration and until are used, they both will apply.)
        """
        if not self.__started:
            self.__started = True
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
                delay=0,**extra_args):
        """
        Connect the source to the destination, at the appropriate ports,
        if any are given.  If src and dest have not been added to the
        simulator, they will be added.
        """
        self.add(src,dest)
        src._connect_to(dest,src_port=src_port,dest_port=dest_port,delay=delay,
                        **extra_args)
        dest._connect_from(src,src_port=src_port,dest_port=dest_port,**extra_args)

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
        self.debug("Enqueue relative: from", (src,src_port),"to",(dest,dest_port),
                   "at time",self.time(),"with delay",delay)
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
        self.debug("Enqueue absolute: from", (src,src_port),"to",(dest,dest_port),
                   "at time",self.time(),"with delay",delay)

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


class SimpleSimulator(Simulator):
    """
    A simulator class that uses a simple sorted event list instead of a
    sched.scheduler object to manage events and dispatching.
    """
    class Event:
        def __init__(self,time,src,dest,src_port,dest_port,data):
            self.time = time
            self.src = src
            self.dest = dest
            self.src_port = src_port
            self.dest_port = dest_port
            self.data = data
            
    def __init__(self,**args):
        super(SimpleSimulator,self).__init__(**args)
        self._Simulator__scheduler = None
        self.events = []

    def run(self,duration=inf,until=inf):
        self._Simulator__time = 0.0
        for e in self._Simulator__event_processors:
            e.start()
        self.continue_(duration,until)
        
    def continue_(self,duration=inf,until=inf):

        stop_time = min(self.time()+duration,until)
        while self.events and self.time() < stop_time:
            if self.events[0].time < self.time():
                self.warning('Discarding stale event from',(src,src_port),
                             'to',(dest,dest_port),
                             'for time',etime,
                             '. current time =',self.time())
                self.events.pop(0)
            elif self.events[0].time > self.time():
                self.debug("Time to sleep. current time =",self.time(),"next event time =",self.events[0].time)
                for ep in self._Simulator__event_processors:
                    self.debug("Doing pre_sleep for",e)
                    ep.pre_sleep()
                # so set the time to the frontmost event.
                self._Simulator__time = self.events[0].time
            else:
                e = self.events.pop(0)
                e.dest.input_event(e.src,e.src_port,e.dest_port,e.data)

    def sleep(self,delay):
        self.warning("sleep not supported in class",self.__class__.__name__)

    def enqueue_event_abs(self,time,src,dest,src_port=None,dest_port=None,data=None):
        """
        Like enqueue_event_rel, except it schedules the event for some
        absolute time.
        """
        self.debug("Enqueue absolute: from", (src,src_port),"to",(dest,dest_port),
                   "at time",self.time(),"for time",time)
        new_e = SimpleSimulator.Event(time,src,dest,src_port,dest_port,data)

        if not self.events or time >= self.events[-1].time:
            self.events.append(new_e)
            return

        for i,e in enumerate(self.events):
            if time < e.time:
                self.events.insert(i,new_e)
                break

    def enqueue_event_rel(self,delay,src,dest,src_port=None,dest_port=None,data=None):
        self.enqueue_event_abs(self.time()+float(delay),
                               src,dest,src_port,dest_port,data)

    
        

        

class EventProcessor(TopoObject):
    """
    Base class for EventProcessors.  Handles basic mechanics of connections and
    sending events.
    """
    def __init__(self,**config):
        super(EventProcessor,self).__init__(**config)
        self.connections = {None:[]}
        

    def _connect_to(self,dest,src_port=None,dest_port=None,delay=0,**args):
        """
        Add a connection to dest/port with a delay (default=0).
        """
        if not src_port in self.connections:
            self.connections[src_port] = []

        self.connections[src_port].append((dest,dest_port,delay))

    def _connect_from(self,src,src_port=None,dest_port=None,**args):
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
    


