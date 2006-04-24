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


Current Simulator

The current Simulator, which can be accessed through the instance
of the Singleton class SimSingleton(), is the last Simulator to
have been created with register=True (the default).


$Id$
"""
__version__='$Revision$'

from parameterizedobject import ParameterizedObject, Parameter
from parameterclasses import Number, BooleanParameter, CallableParameter
from copy import copy, deepcopy
from fixedpoint import FixedPoint

SLEEP_EXCEPTION = "Sleep Exception"
STOP = "Simulator Stopped"

Forever = FixedPoint(-1)


# CEBHACKALERT: this is to be removed; calls
# can be replaced by 'topo.sim'

def get_active_sim():
    """
    Return the active simulator.
    """
    return SimSingleton()


class Singleton(object):
    """
    The singleton pattern.

    To create a singleton class, you subclass from Singleton; each
    subclass will have a single instance, no matter how many times its
    constructor is called. To further initialize the subclass
    instance, subclasses should override 'init' instead of __init__ -
    the __init__ method is called each time the constructor is called.

    From http://www.python.org/2.2.3/descrintro.html#__new__
    """
    def __new__(cls, *args, **kwds):
        it = cls.__dict__.get("__it__")
        if it is not None:
            return it
        cls.__it__ = it = object.__new__(cls)
        it.init(*args, **kwds)
        return it
    def init(self, *args, **kwds):
        pass



class SimSingleton(Singleton):
    """
    A singleton class, the instance of which allows access to
    the current simulator.
    """
    actual_sim = None

    # should both these completely hide that this is
    # SimSingleton, as they do at the moment?
    def __repr__(self):
        """
        Return the simulator's __repr__().
        """
        return self.actual_sim.__repr__()

    def __str__(self):
        """
        Return the simulator's __str__().
        """
        return self.actual_sum.__str__()
    
    def init(self):
        """
        Create a new simulator.
        """
        # Simulator will call this object's change_sim()
        Simulator()

    def __getattribute__(self,attribute):
        """
        If the SimSingleton object has the attribute, return it; if the
        actual_sim has the attribute, return it; otherwise, an AttributeError
        relating to Simulator will be raised (as usual).
        """
        try:
            return object.__getattribute__(self,attribute)
        except AttributeError:
            actual_sim = object.__getattribute__(self,'actual_sim')
            return getattr(actual_sim,attribute)

    def __setattr__(self,name,value):
        """
        If this object has the attribute name, set it to value.
        Otherwise, set self.actual_sim.name=value.

        Unless an attribute is inserted into this object's __dict__,
        the only one it is are 'actual_sim'.
        So, this method really sets attributes on the actual_sim.
        """
        # read like:
        #  if hasattr(self,name):
        #      setattr(self,name,value)
        #  else:
        #      setattr(self.actual_sim,name,value)
        try:
            object.__getattribute__(self, name) 
            object.__setattr__(self, name, value)
        except AttributeError:
            object.__setattr__(self.actual_sim, name, value)

    def change_sim(self,new_sim):
        """
        Set actual_sim to be new_sim.
        """
        assert isinstance(new_sim,Simulator), "Can only change to a Simulator instance."
        self.actual_sim=new_sim
            
    def __getitem__(self,item_name):
        """
        Allow dictionary-style access to the simulator.
        """
        return self.actual_sim[item_name]

    def __setitem__(self,item_name,item_value):
        """
        Allow dictionary-style access to the simulator.
        """
        self.actual_sim[item_name]=item_value


class EventProcessor(ParameterizedObject):
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


    # if extra parameters are required for an EP subclass, a
    # dictionary could be added to Simulator.connect() to hold
    # them, and passed on here
    def _connect_to(self,conn):
        """
        Add a connection to dest/port with a delay (default=0).
        Should only be called from Simulator.connect().
        """

        if not conn.src_port in self.out_connections:
            self.out_connections[conn.src_port] = []
  
        self.out_connections[conn.src_port].append(conn)


    def _connect_from(self,conn):
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
        Called by the simulator when the EventProcessor is add()ed to the simulator.

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
    


class EventProcessorParameter(Parameter):
    """
    Parameter whose value can be any EventProcessor instance.
    """
    __slots__ = []
    __doc__ = property((lambda self: self.doc))
    
    def __init__(self,default=EventProcessor(),**params):
        super(EventProcessorParameter,self).__init__(default=default,**params)
        
    def __set__(self,obj,val):
        if not isinstance(val,EventProcessor):
            raise ValueError("Parameter must be an EventProcessor.")
        else:
            super(EventProcessorParameter,self).__set__(obj,val)


class EPConnection(ParameterizedObject):
    """
    EPConnection stores basic information for a connection between
    two EventProcessors.
    """

    src = EventProcessorParameter(default=None,constant=True)
    dest = EventProcessorParameter(default=None,constant=True)
    src_port = Parameter(default=None)
    dest_port = Parameter(default=None)
    delay = Parameter(default=0)

    def __init__(self,**params):
        super(EPConnection,self).__init__(**params)


class Event(object):
    """
    Hierarchy of classes for storing events.

    When called, must make the event happen.
    """
    # CEBHACKALERT: subclasses must implement time attribute
    
    def __call__(self):
        raise NotImplementedError

class EPEvent(Event):
    """An Event for delivery to an EventProcessor."""
    def __init__(self,time,src,dest,src_port,dest_port,data):
        self.time = time
        self.src = src
        self.dest = dest
        self.src_port = src_port
        self.dest_port = dest_port
        self.data = deepcopy(data)

    def __call__(self):
        self.dest.input_event(self.src,self.src_port,self.dest_port,self.data)


class CommandEvent(Event):
    """An Event consisting of a command string to run."""

    def __init__(self,time,command_string):
        self.time = time
        self.command_string = command_string
        
    def __call__(self):
        """
        exec's the command_string in __main__.__dict__.
        
        Be sure that any required items will be present in
        __main__.__dict__; in particular, consider what will be present
        after the network is saved and restored. For instance, results of
        scripts you have run, or imports they make---all currently
        available in __main__.__dict__---will not be saved with the
        network.
        """
        import __main__
        try:
            exec self.command_string in __main__.__dict__
        except SyntaxError:
            raise SyntaxError("CommandEvent at "+`self.time`+" contained a syntax error:'"+self.command_string+"'")


# CEBHACKALERT: class to be removed when all example files changed
# to use schedule_command()!
class SAEvent(Event):
    def __init__(self,time,fn,args):
        self.time = time
        self.fn = fn
        self.args = args

    def __call__(self):
        self.fn(*self.args)
        
    

# CEBHACKALERT: do we need to allow a user to save arbitrary data
# along with the network when pickling? Like specified imports and
# results stored in variables in main?
# 
# For imports, maybe ScheduledAction could be a ParameterizedObject
# (so class attributes get pickled), and it could have a class
# attribute to store anything scheduled actions repeatedly depend on -
# in many cases, scheduled actions require BoundingBox.
#
# Maybe it would be better to handle everything in something like
# a general save functinon, which does save_snapshot() plus allows
# things and their locations to be saved?
# e.g.
# save_state({"__main__.__dict__": [BoundingBox, x]})
# where save_state() also calls save_snapshot to get the simulator.



            
# CEBHACKALERT: need to rename to simulation, etc.

# Simulator stores its events in a linear-time priority queue (i.e., a
# sorted list.) For efficiency, e.g. for spiking neuron simulations,
# we'll probably need to replace the linear priority queue with a more
# efficient one.  Jeff has an O(log N) minheap implementation, but
# there are likely to be many others to select from.
#
class Simulator(ParameterizedObject):
    """
    A simulator class that uses a simple sorted event list (instead of
    e.g. a sched.scheduler object) to manage events and dispatching.

    The Parameter 'register' indicates whether or not to register the
    Simulator as being part of Topographica; that is, register would
    be false for use of the Simulator outside Topographica. With
    register True, the Simulator is set to be the 'active_sim', which
    other Topographica commands and classes might look for or want to
    be informed about.
    """

    ### JABALERT! Is step_mode even implemented?
    step_mode = BooleanParameter(default=False)
    register = BooleanParameter(default=True)

    # CEBHACKALERT: write the doc so a user knows what it means. And,
    # should this be instantiated? I can't think right now.
    startup_commands = Parameter(
        default=[],
        doc="""
            List of string commands that will be exec'd in
            __main__.__dict__ before this simulator is unpickled.
            """)
              

    def __init__(self,**config):
        """
        The simulator constructor takes one keyword parameter:
        
           step_mode = debugging flag, causing the simulator to stop
                       before each tick.
        """
        super(Simulator,self).__init__(**config)

        # time is a fixed-point number
        # JABHACKALERT! Shouldn't this be at least 4 decimal places by default?
        # (Either using ,4 or setting the FixedPoint default precision to 4?)
        self._time = FixedPoint("0.0")
        self._event_processors = {}
        self._sleep_window = 0.0
        self._sleep_window_violation = False

        if self.register:
            SimSingleton().change_sim(self)

        self.events = []
        self._events_stack = []

    def __getitem__(self,item_name):
        """
        Return item_name if it exists as an EventProcessor in
        the Simulator. See objects().
        """
        if not isinstance(item_name,str):
            raise TypeError("Expected string (objects in the Simulator are indexed by name).")
        try:
            return self.objects()[item_name]
        except KeyError:
            raise AttributeError("Simulator doesn't contain '"+item_name+"'.")


    def __setitem__(self,ep_name,ep):
        """
        Add ep to the simulator, setting its name to ep_name.
        ep must be an EventProcessor.

        If ep_name already exists in the simulator, ep overwrites
        the original object (as for a dictionary).

        If the ep itself already exists in the simulator, a
        warning is printed and the ep is not added.

        Note, EventProcessors do not necessarily have to be added to
        the simulator to be used in a simulation, but they will not
        receive the start() message.  Adding a node to the simulator
        also sets the backlink node.simulator, so that the node can
        enqueue events and read the simulator clock.
        """
        if not isinstance(ep_name,str):
           raise TypeError("Expected string for item name (EPs in the Simulator are indexed by name).")

        if not isinstance(ep,EventProcessor):
           raise TypeError("Expected EventProcessor: objects in the Simulator must be EPs.")

        if ep in self._event_processors.values():
            self.warning("EventProcessor "+str(ep)+" () already exists in the simulator and will not be added.")
        else:
            ep.name=ep_name
            # CEBHACKALERT: if this is overwriting an existing EP,
            # it ought to delete it properly (i.e. remove connections
            # etc). We need a delete() method already anyway.
            self._event_processors[ep_name] = ep
            ep.simulator = self
            ep.start()


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
                    for ep in self._event_processors.values():
    #                    self.debug("Doing pre_sleep for",e)
                        ep.pre_sleep()
                    
                # set the time to the frontmost event (Note: the front
                # event may have been changed by the .pre_sleep() calls).
                self._time = self.events[0].time
            else:

                # If it's not too late, and it's not too early, then
                # it's just right!  So pop the event and call it.
                event = self.events.pop(0)

                # ####### INFORMATION PRINTING ONLY ########
                # (I kept the try/catch for speed - will usually be EPEvent -
                #  but I haven't checked the impact. Presumably it's tiny.
                #  Could be simplified to:
                #  if isinstance(event,EPEvent):
                #      self.verbose...
                #  elif isinstance(event,CommandEvent):
                #      self.verbose...
                #  else:
                #      self.verbose...     )
                try:
                    self.verbose("Delivering event from",event.src.name,
                                 "to",event.dest.name,"at",self._time)
                except AttributeError:
                    if isinstance(event,CommandEvent):
                        self.verbose(
                            "Executing command '"+event.command_string+"' at "+`self._time`)
                    else:
                        self.verbose("Delivering event at",self._time)
                # ##########################################
                
                event()
                did_event=True


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
        new_e = EPEvent(time,src,dest,src_port,dest_port,data)

        # The new event goes at the end of the event queue if there
        # isn't a queue right now, or if it's later than the last
        # event's time.  Otherwise, it's inserted at the appropriate
        # position somewhere inside the event queue.
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

    # CEBHACKALERT: can replace schedule_action() if all examples/ code is
    # changed over.
    def schedule_command(self,time,command_string):
        new_event = CommandEvent(time=time,command_string=command_string)

        # CEBHACKALERT: doesn't this duplicate a lot of enqueue_event_abs()
        if not self.events or time >= self.events[-1].time:
            self.events.append(new_event)
            return
        for index,event in enumerate(self.events):
            if time < event.time:
                self.events.insert(index,new_event)
                break
        

    def schedule_action(self,time,fn,*p):
        """
        Enqueue a function call event at an absolute simulator clock time.
        (Same as enqueue_event_abs, except for scheduling a function call and
        not a generic event.) This method should be used for arbitrary
        functions to be called at specific times, e.g. for saving snapshots.

        Usage: schedule_action(time, function name, param 1, param 2, ...)
        """
        self.debug("Enqueue absolute action: ", fn, "at time",self._time,"for time",time)
        new_e = SAEvent(time,fn,p)

        # CEBHACKALERT: doesn't this duplicate a lot of enqueue_event_abs()
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


    # CEBHACKALERT: This method can be deleted when the
    # connect() method is removed and replaced by connect2().
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
            if not ep in self._event_processors.values():
                self._event_processors[ep.name] = ep
                ep.simulator = self
                ep.start()

    def connect2(self,
                src,
                dest,
                src_port=None,
                dest_port=None,
                delay=0,connection_type=EPConnection,**connection_params):
        """
        Connect the source to the destination, at the appropriate ports,
        if any are given.

        src and dest should already be part of the simulator.

        Returns the connection that was created.
        """
        conn = connection_type(src=self[src],dest=self[dest],src_port=src_port,dest_port=dest_port,delay=delay,**connection_params)
        self[src]._connect_to(conn)
        self[dest]._connect_from(conn)
        return conn

    def connect(self,
                src=None,
                dest=None,
                src_port=None,
                dest_port=None,
                delay=0,connection_type=EPConnection,**connection_params):
        """
        Connect the source to the destination, at the appropriate ports,
        if any are given.  If src and dest have not been added to the
        simulator, they will be added.  Returns the connection that
        was created.
        """
        self.add(src,dest)
        conn = connection_type(src=src,dest=dest,src_port=src_port,dest_port=dest_port,delay=delay,**connection_params)
        src._connect_to(conn)
        dest._connect_from(conn)
        return conn
    

    # CEBHACKALERT: why not just event_processors()?
    ### It might be possible to come up with a more expressive name
    ### for this function.  It should mean 'anything that exists in
    ### the simulator universe, i.e. all EventProcessors'.
    ###
    def objects(self,baseclass=EventProcessor):
        """
        Return a list of simulator objects having the specified base
        class.  All simulator objects have a base class of
        EventProcessor, and so the baseclass must be either
        EventProcessor or one of its subclasses.
        """
        return dict([(ep_name,ep)
                     for (ep_name,ep) in self._event_processors.items()
                     if isinstance(ep,baseclass)])
        
