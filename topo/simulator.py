"""
The topographica simulator module.  

The Simulator object is the central object of a Topographica
simulation.  It handles the simulation clock and maintains
communication between the components of the simulation.

A simulation is structured as directed graph of event-processing nodes
called EventProcessors (EPs).  EventProcessors generate data-carrying
events, which are routed through the graph to other EventProcessors
via delayed connections.

The simulator is modular: EventProcessors should inherit from the root
EventProcessor class.  This class manages the EP's connections to
other EPs, as well as the mechanics of sending events to other EPs
(through the simulator).  The EventProcessor class defines the basic
EP programming interface.

Formally, an simulation event is a tuple: (time,src,dest,port,data), where

  time      = The time at which the event should be delivered, an arbitrary
              floating point value.
  src       = The EventProcessor from which the event originated.
  src_port  = The output port from which the event originated
              in the source EP. (see PORTS, below)
  dest      = Destination EventProcessor of the event
  dest_port = The input port to which the event is destined in dest.
              (see PORTS) below.
  data      = The event data to be delivered.  Can be anything.


A simulation begins by giving each EventProcessor an opportunity to
send any initial events.  It then proceeds by processing and
delivering events in time order.  After all events for the current
time are processed, simulation time skips to the time of earliest
event remaining in the queue.

PORTS

All connections between EPs are tagged with a source port and a
destination port.  Ports are internal addresses that EPs can use to
distinguish between inputs and outputs.  A port specifier can be any
hashable Python object.  If not specified, the input and output ports
for a connection default to None.

Output ports distinguish different types of output that an EP may
produce. When sending output, the EP must call self.send_output()
separately for each port.  Input ports distinguish different types of
input an EP may receive and process.  The EP is free to interpret the
input port designation on an incoming event in any way it chooses.

An example of input port use might be an EP that receives neural
'ordinary' neural activity on the default port, and receives a
separate modulatory signal that influences learning.  The originator
of the modulatory signal might have a connection to the EP with
dest_port = 'modulation'.

An example of output port use might be an EP that sends different
events to itself than it sends out to other EPs.  In this case the
self connections might have src_port = 'recurrent'.


=========================

Jeff's implementation notes:

* SimpleSimulator *

This module actually contains two simulator classes.  The original
Simulator, and a subclass SimpleSimulator.  Simulator uses the
sched.scheduler class from the Python std library to handle event
scheduling.  Because sched.scheduler is a black box, I wrote
SimpleScheduler in order to be able to debug event scheduling issues,
SimpleScheduler stores its events in a linear-time priority queue (i.e
a sorted list.)

The Simulator class is more mature, and should be better able to
handle exceptions raised while running without corrupting the event
queue.  The black-box nature of the scheduler, however, means that I
had to do some fancy footwork with exceptions in order to get
.pre_sleep() to behave correctly.  SimpleSimulator, on the other hand,
may not (currently) guarantee that raised exceptions won't corrupt the
event queue, but its implementation is much simpler and clearer and
its performance is easier to inspect and debug.  It may be worth
making SimpleSimulator the default (i.e. renaming it as Simulator and
making it the superclass rather than the subclass).  For efficiency,
e.g. for spiking neuron simulations, we'll probably need to replace
the linear priority queue with a more efficient one.  I have an O(log
N) minheap implementation in python somewhere.  It might even be in
the CVS repository as a dead file.

Note also that even though Simulator may guarantee that the event
queue isn't corrupted by a raise exception, there is no guarantee that
the internal state of the EP that raised the exception is sane, so
it's not clear if the exception-save aspect if sched.simulator is of
particular value.


* Connection classes *

Currently, connections in the simulation's directed graph are not
first-class objects in the system.  Rather, they are implemented as
(dest,dest_port,delay) tuples stored in dictionaries indexed by
src_port inside each individual EP (i.e. within each graph node).
With the advent of Projection classes for RFSheets (see rfsheet.py),
it is worth considering whether to replace these tuples with an
explicit Connection class, of which Projection would be a subclass.
This class would encapsulate all data that parameterizes the
connection.  This would simplify data structures somewhat, since
Projection classes must also keep track of things like src and dest.
It might also make future parallelization efforts easier, since each
Connection object could conceivably maintain its own event queue, and
since connections may naturally delimit independent and parallelizable
computations within a simulation.  (This last point should be
considered with care, since it is certainly not universally true,
different connections will of course interact with one another within
an EP.  The question of how much depends on the nature of the
simulation.)

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
                # By default we should stop running if there's an exception
                keep_running = False
                try:
                    self.__scheduler.run()
                except SLEEP_EXCEPTION:

                    # SLEEP_EXCEPTION is raised when an EP's
                    # .pre_sleep() method enqueued an event to occur
                    # during the time when the scheduler was supposed
                    # to be asleep.  By raising an exception we are
                    # able to stop the scheduler before it sleeps and
                    # restart it to process the newly scheduled event(s).
                    
                    self.debug("SLEEP EXCEPTION")
                    self.__sleep_window_violation = False
                    self.__sleep_window = 0
                    # since the exception was a SLEEP_EXCEPTION
                    # we want to keep running.
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
        self._Simulator__time = 0.0
        
    def run(self,duration=inf,until=inf):
        if self._Simulator__time = 0.0:
            # if the time is 0.0 start all the EPs
            # FIXME: this is probably not right, .run(until=0) will
            # cause EPs to be started more than once.
            for e in self._Simulator__event_processors:
                e.start()
        self.continue_(duration,until)
        
    def continue_(self,duration=inf,until=inf):

        stop_time = min(self.time()+duration,until)
        while self.events and self.time() < stop_time:

            # Loop while there are events and it's not time to stop.
            
            if self.events[0].time < self.time():

                # if the first event's time is less than the current time
                # then the event is stale so print a warning and
                # discard it.                

                self.warning('Discarding stale event from',(src,src_port),
                             'to',(dest,dest_port),
                             'for time',etime,
                             '. current time =',self.time())
                self.events.pop(0)
            elif self.events[0].time > self.time():

                # If the first event's time is greater than the
                # current time then it's time to sleep (i.e. increment
                # the clock) before doing that, give everyone a
                # pre_sleep() call.

                self.debug("Time to sleep. current time =",self.time(),"next event time =",self.events[0].time)
                for ep in self._Simulator__event_processors:
                    self.debug("Doing pre_sleep for",e)
                    ep.pre_sleep()
                    
                # set the time to the frontmost event (Note: the front
                # event may have been changed by the .pre_sleep() calls.

                self._Simulator__time = self.events[0].time
            else:

                # If it's not too late, and it's not too early, then
                # it's just right, so pop the event and dispatch it to
                # its destination.

                e = self.events.pop(0)
                e.dest.input_event(e.src,e.src_port,e.dest_port,e.data)

    def sleep(self,delay):

        # We don't need the sleep call in this class because the
        # continue_ loop updates the clock directly.

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
    sending events.  Also handles the EP's dictionary of output ports
    and outgoing connections.
    """
    def __init__(self,**config):
        super(EventProcessor,self).__init__(**config)

        # Connections are maintained within each EP.  The connection db
        # is a dictionary indexed by output port.  Each output port
        # refers to a list of connections represented as tuples:
        # (dest,dest_port,delay) where:
        #
        #  dest      = destination EP
        #  dest_port = destination port in the EP
        #  delay     = connection propagation delay in simulator time units.
        
        self.connections = {None:[]}
        

    def _connect_to(self,dest,src_port=None,dest_port=None,delay=0,**args):
        """
        Add a connection to dest/port with a delay (default=0).
        Should only be called from Simulator.connect(). The extra
        keyword arguments in **args contain arbitrary connection
        parameters that can be interpreted by EP subclasses as
        needed.  
        """
        if not src_port in self.connections:
            self.connections[src_port] = []

        self.connections[src_port].append((dest,dest_port,delay))

    def _connect_from(self,src,src_port=None,dest_port=None,**args):
        """
        Add a connection from src/port with a delay (default=0).
        Should only be called from Simulator.connect().  The extra
        keyword arguments in **args contain arbitrary connection
        parameters that can be interpreted by EP subclasses as
        needed.  
        """
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
    


