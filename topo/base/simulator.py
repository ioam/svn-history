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


$Id$
"""
__version__='$Revision$'

from topoobject import TopoObject
from parameter import Parameter
from copy import copy, deepcopy
from fixedpoint import FixedPoint

SLEEP_EXCEPTION = "Sleep Exception"
STOP = "Simulator Stopped"

Forever = FixedPoint(-1)


__active_sim = None

def get_active_sim():
    """
    """
    if __active_sim == None:
        TopoObject().warning('No active Simulator.')
        
    return __active_sim

def set_active_sim(sim):
    """
    """
    global __active_sim
    __active_sim = sim


class EPConnection(TopoObject):
    """
    EPConnection stores basic information for a connection between
    two EventProcessors.
    """

    src = Parameter(default=None)
    dest = Parameter(default=None)
    src_port = Parameter(default=None)
    dest_port = Parameter(default=None)
    delay = Parameter(default=None)

    def __init__(self,**params):
        super(EPConnection,self).__init__(**params)


class SimulatorEvent:
    """Simulator event"""
    fn = Parameter(default=None,doc="Function to execute when the event is processed")

    def __init__(self,time,src,dest,src_port,dest_port,data,fn=None):
        self.time = time
        self.src = src
        self.dest = dest
        self.src_port = src_port
        self.dest_port = dest_port
        self.data = deepcopy(data)
        self.fn = fn


# Simulator stores its events in a linear-time priority queue (i.e a
# sorted list.) For efficiency, e.g. for spiking neuron simulations,
# we'll probably need to replace the linear priority queue with a more
# efficient one.  Jeff has an O(log N) minheap implementation, but
# there are likely to be many others to select from.
#
class Simulator(TopoObject):
    """
    A simulator class that uses a simple sorted event list (instead of
    e.g. a sched.scheduler object) to manage events and dispatching.
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

        # time is a fixed-point number
        self._time = FixedPoint("0.0")
        self._event_processors = []
        self._sleep_window = 0.0
        self._sleep_window_violation = False

        if self.register:
            set_active_sim(self)

        # CEBHACKALERT: this isn't staying.
        # Previously, calling topo.base.registry.set_active_sim()
        # did this.
        import topo.base.registry
        topo.base.registry.link_console_to_active_sim()
        # end HACKALERT

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
        Run the simulator by starting the event scheduler.

        parameters:
          duration = time to run in simulator time. Default: run indefinitely.
          until    = time to stop in simulator time. Default: run indefinitely.
          (note if both duration and until are used, they both will apply.)
        """
        # Complicated expression for min(time+duration,until)
        if duration == Forever:
            stop_time = until
        elif until == Forever:
            stop_time = self._time + duration
        else:
            stop_time = min(self._time+duration,until)
            
        did_event = False
        while self.events and (stop_time == Forever or self._time < stop_time):

            # Loop while there are events and it's not time to stop.
            
            if self.events[0].time < self._time:

                # if the first event's time is less than the current time
                # then the event is stale so print a warning and
                # discard it.                

                self.warning('Discarding stale event from',(self.events[0].src,self.events[0].src_port),
                             'to',(self.events[0].dest,self.events[0].dest_port),
                             'for time',self.events[0].time,
                             '. Current time =',self._time)
                self.events.pop(0)
            elif self.events[0].time > self._time:

                # If the first event's time is greater than the
                # current time then it's time to sleep (i.e. increment
                # the clock).  Before doing that, give everyone a
                # pre_sleep() call.

                if did_event:
                    did_event = False
                    self.debug("Time to sleep. Current time =",self._time,
                               ".  Next event time =",self.events[0].time)
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
                   "at time",self._time,"for time",time)
        new_e = SimulatorEvent(time,src,dest,src_port,dest_port,data)

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
        self.enqueue_event_abs(self._time+delay,
                               src,dest,src_port,dest_port,data)


    def schedule_action(self,time,fn,*p):
        """
        Enqueue a function call event at an absolute simulator clock time.
        (Same as enqueue_event_abs, except for scheduling a function call and
        not a generic event.) This method should be used for arbitrary
        functions to be called at specific times, e.g. for saving snapshots.

        Usage: schedule_action(time, function name, param 1, param 2, ...)
        """
        self.debug("Enqueue absolute action: ", fn, "at time",self._time,"for time",time)
        new_e = SimulatorEvent(time,None,None,None,None,p,fn=fn)

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
        self._events_stack.append((self._time,[copy(event) for event in self.events]))

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
                ep.start()


    def connect(self,
                src=None,
                dest=None,
                src_port=None,
                dest_port=None,
                delay=0,connection_type=EPConnection,connection_params={},**extra_args):
        """
        Connect the source to the destination, at the appropriate ports,
        if any are given.  If src and dest have not been added to the
        simulator, they will be added.
        """
        self.add(src,dest)
        conn = connection_type(src=src,dest=dest,src_port=src_port,dest_port=dest_port,delay=delay,**connection_params)
        src._connect_to(conn,**extra_args)
        dest._connect_from(conn,**extra_args)


    def get_event_processors(self):
        """Return the list of event processors such as Sheets."""
        return self._event_processors


    ### It might be possible to come up with a more expressive name
    ### for this function.  It should mean 'anything that exists in
    ### the simulator universe, i.e. all EventProcessors'.
    ###
    ### JABALERT!
    ###
    ### It would be nice to have baseclass default to EventProcessor,
    ### but that would be a forward reference.  If it can be done,
    ### it may be possible to eliminate get_event_processors.
    def objects(self,baseclass):
        """
        Return a list of simulator objects having the specified base
        class.  All simulator objects have a base class of
        EventProcessor, and so the baseclass must be either
        EventProcessor or one of its subclasses.
        """
        return dict([(i.name,i) for i in self._event_processors \
                     if isinstance(i,baseclass)])


class EventProcessor(TopoObject):
    """
    Base class for EventProcessors, i.e. objects that can accept and
    handle events.  This base class handles the basic mechanics of
    connections and sending events, and store both incoming and outgoing
    connections. 
    """
    def __init__(self,**config):
        super(EventProcessor,self).__init__(**config)

        # The out_connection db is a dictionary indexed by output port.  Each 
        # output port refers to a list of EPConnection objects with that 
        # output port. This optimizes the lookup of the set of outgoing
        # connections from the same port.
        # The in_connection is just a general list. Subclass can use other
        # data stuctures to optimize the operations specific to it
        # by overriding _connect_from().
        
        self.in_connections = []
        self.out_connections = {None:[]}

        # The simulator link is not set until the call to add()
        self.simulator = None
        
    def _connect_to(self,conn,**args):
        """
        Add a connection to dest/port with a delay (default=0).
        Should only be called from Simulator.connect(). The extra
        keyword arguments in **args contain arbitrary connection
        parameters that can be interpreted by EP subclasses as
        needed.  
        """

        if not conn.src_port in self.out_connections:
            self.out_connections[conn.src_port] = []
  
        self.out_connections[conn.src_port].append(conn)


    def _connect_from(self,conn,**args):
        """
        Add a connection from src/port with a delay (default=0).
        Should only be called from Simulator.connect().  The extra
        keyword arguments in **args contain arbitrary connection
        parameters that can be interpreted by EP subclasses as
        needed.  
        """

	if conn not in self.in_connections:
            self.in_connections.append(conn)

    def start(self):
        """        
        Called by the simulator when the EventProcessor is add()ed to the simlulator.

        If an EventProcessor needs to have any code run when it is added to the simulator,
        it should be in this method.
        """
        pass

    def send_output(self,src_port=None,data=None):
        """
        Send some data out to all connections on the given src_port.
        """
        for conn in self.out_connections[src_port]:
            self.simulator.enqueue_event_rel(conn.delay,self,conn.dest,conn.src_port,conn.dest_port,data)


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
    

