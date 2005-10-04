"""
The topographica simulator module.  

The Simulator object is the central object of a Topographica
simulation.  It handles the simulation clock and maintains
communication between the components of the simulation.

A simulation is structured as a directed graph of event-processing nodes
called EventProcessors (EPs).  EventProcessors generate data-carrying
events, which are routed through the graph to other EventProcessors
via delayed connections.

The simulator is modular: EventProcessors should inherit from the root
EventProcessor class.  This class manages the EP's connections to
other EPs, as well as the mechanics of sending events to other EPs
(through the simulator).  The EventProcessor class defines the basic
EP programming interface.

Formally, a simulation event is a tuple:
(time,src,src_port,dest,dest_port,data), where

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
delivering events to EventProcessors in time order.  After all events
for the current time are processed, the simulator gives each
EventProcessor a chance to do any final computation, after which
simulation time skips to the time of the earliest event remaining in
the queue.

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

An example of input port use might be an EP that receives 'ordinary'
neural activity on the default port, and receives a separate
modulatory signal that influences learning.  The originator of the
modulatory signal might have a connection to the EP with dest_port =
'modulation'.

An example of output port use might be an EP that sends different
events to itself than it sends out to other EPs.  In this case the
self connections might have src_port = 'recurrent'.


=========================

* Simulator *

This module actually contains two simulator classes.  The original
BaseSimulator, and a subclass Simulator.  BaseSimulator uses the
sched.scheduler class from the Python std library to handle event
scheduling.  Because sched.scheduler is a black box, Simulator was
written in order to be able to debug event scheduling issues,
Simulator stores its events in a linear-time priority queue (i.e a
sorted list.)

The BaseSimulator class is more mature, and should be better able to
handle exceptions raised while running without corrupting the event
queue.  The black-box nature of the scheduler, however, means that
fancy footwork with exceptions must be done in order to get
.pre_sleep() to behave correctly.  Simulator, on the other hand, may
not (currently) guarantee that raised exceptions won't corrupt the
event queue, but its implementation is much simpler and clearer and
its performance is easier to inspect and debug.  Simulator is
currently the default, because toggling learning requries copies of
the event queue.  For efficiency, e.g. for spiking neuron simulations,
we'll probably need to replace the linear priority queue with a more
efficient one.  Jeff has an O(log N) minheap implementation.

Note also that even though BaseSimulator may guarantee that the event
queue isn't corrupted by a raised exception, there is no guarantee that
the internal state of the EP that raised the exception is sane, so
it's not clear if the exception-safe aspect of sched.simulator is of
particular value.


$Id$
"""


import sched
from base import TopoObject
from parameter import Parameter
from copy import copy, deepcopy
import __main__
import topo.registry
from fixedpoint import FixedPoint

SLEEP_EXCEPTION = "Sleep Exception"
STOP = "Simulator Stopped"

Forever = -1

class Simulator(TopoObject):
    """
    A simulator class that uses a simple sorted event list instead of a
    sched.scheduler object to manage events and dispatching.
    """
    class Event:
        fn = Parameter(default=None,doc="Function to execute when the event is processed")

        def __init__(self,time,src,dest,src_port,dest_port,data,fn=None):
            self.time = time
            self.src = src
            self.dest = dest
            self.src_port = src_port
            self.dest_port = dest_port
            self.data = data
            self.fn = fn

        def __copy__(self):
            new_copy = Simulator.Event(self.time,self.src,self.dest, \
                       self.src_port,self.dest_port,deepcopy(self.data))
            return new_copy
            
            
    step_mode = Parameter(default=False)
    register = Parameter(default=True)

    def __init__(self,**config):
        """
        The simulator constructor takes one keyword parameter:
        
           step_mode = debugging flag, causing the simulator to stop
                       before each tick.
        """
        super(Simulator,self).__init__(**config)

        # time is a fixed-point number
        self._time = FixedPoint("0.0")
        self._event_processors = []
        self._sleep_window = 0.0
        self._sleep_window_violation = False
        self._scheduler = sched.scheduler(self.time,self.sleep)
        self._started = False
        if self.register:
            topo.registry.set_active_sim(self)

        self.events = []
        self._events_stack = []
        
    def time(self):
        """
        Return the current simulation time as a FixedPoint object.
        
	If the time return is used in the computation of a floating point 
        variable, it should be cast into a floating point number by float().
        """
        return self._time
    
    def run(self,duration=Forever,until=Forever):
        """
        Run the simulator.   Call .start() for each EventProcessor if not
        previously done, and start the event scheduler.
        parameters:
          duration = time to run in simulator time. Default: run indefinitely.
          until    = time to stop in simulator time. Default: run indefinitely.
          (note if both duration and until are used, they both will apply.)
        """
        if not self._started:
            self._started = True
            for node in self._event_processors:
                node.start()
        self.continue_(duration,until)

    def continue_(self,duration=Forever,until=Forever):

        # Complicated expression for min(time+duration,until)
        if duration == Forever:
            stop_time = until
        elif until == Forever:
            stop_time = self.time() + duration
        else:
            stop_time = min(self.time()+duration,until)
            
        did_event = False
        while self.events and (stop_time == Forever or self.time() < stop_time):

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
                # the clock).  Before doing that, give everyone a
                # pre_sleep() call.

                if did_event:
                    did_event = False
                    self.debug("Time to sleep. current time =",self.time(),
                               "next event time =",self.events[0].time)
                    for ep in self._event_processors:
    #                    self.debug("Doing pre_sleep for",e)
                        ep.pre_sleep()
                    
                # set the time to the frontmost event (Note: the front
                # event may have been changed by the .pre_sleep() calls).
                self._time = self.events[0].time
            else:

                # If it's not too late, and it's not too early, then
                # it's just right!  So pop the event and dispatch it to
                # its destination.
                e = self.events.pop(0)
                if e.fn == None:
                    e.dest.input_event(e.src,e.src_port,e.dest_port,e.data)
                    did_event = True
                else:
                    e.fn(*(e.data))

        # The clock needs updating if the events have not done it.
        #if self.events and self.events[0].time >= stop_time:
        if stop_time != Forever:
            self._time = stop_time


    def sleep(self,delay):

        # We don't need the sleep call in this class because the
        # continue_ loop updates the clock directly.

        self.warning("sleep not supported in class",self.__class__.__name__)

    def enqueue_event_abs(self,time,src,dest,src_port=None,dest_port=None,data=None):
        """
        Enqueue an event at an absolute simulator clock time.
        """
        self.debug("Enqueue absolute: from", (src,src_port),"to",(dest,dest_port),
                   "at time",self.time(),"for time",time)
        new_e = Simulator.Event(time,src,dest,src_port,dest_port,data)

        if not self.events or time >= self.events[-1].time:
            self.events.append(new_e)
            return

        for i,e in enumerate(self.events):
            if time < e.time:
                self.events.insert(i,new_e)
                break

    def enqueue_event_rel(self,delay,src,dest,src_port=None,dest_port=None,data=None):
        """
        Enqueue an event at a time relative to the current simulator clock.
        """
        self.enqueue_event_abs(self.time()+float(delay),
                               src,dest,src_port,dest_port,data)


    def schedule_action(self,time,fn,*p):
        """
        Enqueue a function call event at an absolute simulator clock time.
        (Same as enqueue_event_abs, except for scheduling a function call and
        not a generic event.) This method should be used for arbitrary
        functions to be called at specific times, e.g. for saving snapshots.

        Usage: schedule_action(time, function name, param 1, param 2, ...)
        """
        self.debug("Enqueue absolute action: ", fn, "at time",self.time(),"for time",time)
        new_e = Simulator.Event(time,None,None,None,None,p,fn=fn)

        if not self.events or time >= self.events[-1].time:
            self.events.append(new_e)
            return

        for i,e in enumerate(self.events):
            if time < e.time:
                self.events.insert(i,new_e)
                break

    def state_push(self):
        """
        Save the current scheduler to an internal stack, and create a
        copy to continue with.  Useful for testing something while
        being able to roll back to the original state.  The copy
        of the scheduler includes a copy of all of the currently
        scheduled events.
        """
        self._events_stack.append((self._time,self.events))
        self.events = [copy(event) for event in self.events]

    def state_pop(self):
        """
        Pop a scheduler off the stack.  
        """
        self._time, self.events = self._events_stack.pop()


    def state_len(self):
        """Return number of event queues in _events_stack."""
        return len(self._events_stack)


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
            if not ep in self._event_processors:
                self._event_processors.append(ep)
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
        src._connect_to(dest,src_port,dest_port,delay,**extra_args)
        dest._connect_from(src,src_port,dest_port,**extra_args)

    
    def get_event_processors(self):
        """Return the list of event processors such as Sheets."""
        return self._event_processors


        
###   JABALERT!
###   
###   Instead of being tuples, connections should be made into proper
###   objects (i.e., into instances of a new class called EPConnection)
###   so that Projections could be subclasses of EPConnection.  That way
###   Sheets wouldn't need any code to keep track of Projections. 
###   The comments below have more background on this approach.
###   
###     Currently, connections in the simulation's directed graph are not
###     first-class objects in the system.  Rather, they are implemented as
###     (dest,dest_port,delay) tuples stored in dictionaries indexed by
###     src_port inside each individual EP (i.e. within each graph node).
###     With the advent of Projection classes for CFSheets (see topo.cfsheet),
###     it is worth considering whether to replace these tuples with an
###     explicit Connection class, of which Projection would be a subclass.
###     This class would encapsulate all data that parameterizes the
###     connection.  This would simplify data structures somewhat, since
###     Projection classes must also keep track of things like src and dest.
###     It might also make future parallelization efforts easier, since each
###     Connection object could conceivably maintain its own event queue, and
###     since connections may naturally delimit independent and parallelizable
###     computations within a simulation.  (This last point should be
###     considered with care, since it is certainly not universally true,
###     different connections will of course interact with one another within
###     an EP.  The question of how much depends on the nature of the
###     simulation.)
###     
###     Note that the EventProcessor.connections tracks the outgoing
###     connections from an EP, while CFSheet.projections tracks the incoming
###     projections.  If we standardize to use Connection objects, probably
###     the EventProcessor class will have to keep track of both incoming and
###     outgoing connections for each EP.
class EventProcessor(TopoObject):
    """
    Base class for EventProcessors, i.e. objects that can accept and
    handle events.  This base class handles the basic mechanics of
    connections and sending events, and also stores the EP's
    dictionaries of output ports and outgoing connections.
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
        

    def _connect_to(self,dest,src_port,dest_port,delay,**args):
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

    def _connect_from(self,src,src_port,dest_port,**args):
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
        default, does nothing. 
        """
        pass

    def send_output(self,src_port=None,data=None):
        """
        Send some data out to all connections on the given src_port.
        """
        for dest,dest_port,delay in self.connections[src_port]:
            self.simulator.enqueue_event_rel(delay,self,dest,src_port,dest_port,data)

    def input_event(self,src,src_port,dest_port,data):
        """
        Called by the simulator to dispatch an event on the given port
        from src.  (By default, does nothing.)
        """
        pass
    
    def pre_sleep(self):
        """
        Called by the simulator before sleeping.  Allows the event processor
        to send any events that must be sent before time advances.
        (By default, does nothing.)
        """
        pass
    


