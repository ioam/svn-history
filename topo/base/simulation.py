"""
The Topographica Simulation class.  

The Simulation object is the central object of a Topographica
simulation.  It handles the simulation clock and maintains
communication between the components of the simulation.

A simulation is structured as a directed graph of event-processing nodes
called EventProcessors (EPs).  EventProcessors generate data-carrying
events, which are routed through the graph to other EventProcessors
via delayed connections.

The simulation is modular: EventProcessors should inherit from the root
EventProcessor class.  This class manages the EP's connections to
other EPs, as well as the mechanics of sending events to other EPs
(through the Simulation).  The EventProcessor class defines the basic
EP programming interface.

Formally, a simulation event (EPConnectionEvent) is a class with the following
data:

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
for the current time are processed, the simulation gives each
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


Current Simulation

The current Simulation, which can be accessed through the instance
of the Singleton class SimSingleton(), is the last Simulation to
have been created with register=True (the default).


$Id$
"""
__version__='$Revision$'

from parameterizedobject import ParameterizedObject, Parameter
from parameterclasses import Number, BooleanParameter, CallableParameter
from copy import copy, deepcopy
from fixedpoint import FixedPoint

SLEEP_EXCEPTION = "Sleep Exception"
STOP = "Simulation Stopped"

Forever = FixedPoint(-1)


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
    the current simulation.
    """
    actual_sim = None

    # should both these completely hide that this is
    # SimSingleton, as they do at the moment?
    def __repr__(self):
        """Return the simulation's __repr__()."""
        return self.actual_sim.__repr__()

    def __str__(self):
        """Return the simulation's __str__()."""
        return self.actual_sim.__str__()
    
    def init(self):
        """Create a new simulation."""
        # Simulation will call this object's change_sim()
        Simulation()

    def __getattribute__(self,attribute):
        """
        If the SimSingleton object has the attribute, return it; if the
        actual_sim has the attribute, return it; otherwise, an AttributeError
        relating to Simulation will be raised (as usual).
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
        """Set actual_sim to be new_sim."""
        assert isinstance(new_sim,Simulation), "Can only change to a Simulation instance."
        self.actual_sim=new_sim
            
    def __getitem__(self,item_name):
        """Allow dictionary-style access to the simulation."""
        return self.actual_sim[item_name]

    def __setitem__(self,item_name,item_value):
        """Allow dictionary-style access to the simulation."""
        self.actual_sim[item_name]=item_value


class EventProcessor(ParameterizedObject):
    """
    Base class for EventProcessors, i.e. objects that can accept and
    handle events.  This base class handles the basic mechanics of
    connections and sending events, and stores both incoming and outgoing
    connections. 
    """
    def __init__(self,**config):
        """
        Create an EventProcessor.

        Note that just creating an EventProcessor does not mean it is
        part of the simulation (i.e. it is not in the simulation's list
        of EventProcessors, and it does not have its start() method called).
        To add an EventProcessor e to a simulation s, simply do
        s['name_of_e']=e. At this point, e's name becomes 'name_of_e'.
        """
        super(EventProcessor,self).__init__(**config)

        # The out_connection db is a dictionary indexed by output port.  Each 
        # output port refers to a list of EPConnection objects with that 
        # output port. This optimizes the lookup of the set of outgoing
        # connections from the same port.
        # The in_connection is just a general list. Subclass can use other
        # data stuctures to optimize the operations specific to it
        # by overriding _connect_from().

        # JABHACKALERT: Why are these two not symmetric?  Surely there's no reason.
        self.in_connections = []
        self.out_connections = {None:[]}

        self.simulation = None


    # if extra parameters are required for an EP subclass, a
    # dictionary could be added to Simulation.connect() to hold
    # them, and passed on here
    def _connect_to(self,conn):
        """
        Add a connection to dest/port.
        
        Should only be called from Simulation.connect().
        """

        if not conn.src_port in self.out_connections:
            self.out_connections[conn.src_port] = []
  
        self.out_connections[conn.src_port].append(conn)


    def _connect_from(self,conn):
        """
        Add a connection from src/port.
        
        Should only be called from Simulation.connect().  The extra
        keyword arguments in **args contain arbitrary connection
        parameters that can be interpreted by EP subclasses as
        needed.  
        """

	if conn not in self.in_connections:
            self.in_connections.append(conn)

    def start(self):
        """        
        Called by the simulation when the EventProcessor is added to
        the simulation.

        If an EventProcessor needs to have any code run when it is
        added to the simulation, it should be in this method.
        """
        pass

    def send_output(self,src_port=None,data=None):
        """
        Send some data out to all connections on the given src_port.
        """
        for conn in self.out_connections[src_port]:
            self.simulation.enqueue_event_rel(EPConnectionEvent(conn.delay,conn,data))

    def input_event(self,conn,data):
        """
        Called by the simulation to dispatch an event on the given port
        from src.  (By default, does nothing.)
        """
        pass

    ### JABALERT: Should change the name somehow.
    def pre_sleep(self):
        """
        Called by the simulation before sleeping.  Allows the event processor
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


class Event(object):
    """
    Hierarchy of classes for storing events.

    When called, must make the event happen.
    """
    def __init__(self,time):
        self.time = time
        
    def __call__(self):
        raise NotImplementedError


class EPConnectionEvent(Event):
    """An Event for delivery to an EPConnection."""
    def __init__(self,time,conn,data=None):
        super(EPConnectionEvent,self).__init__(time)
        self.data = deepcopy(data)
        self.conn = conn

    def __call__(self):
        self.conn.dest.input_event(self.conn,self.data)


class CommandEvent(Event):
    """An Event consisting of a command string to run."""

    def __init__(self,time,command_string):
        super(CommandEvent,self).__init__(time)
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
        # here to avoid importing __main__ into the rest of the file?
        import __main__
        try:
            exec self.command_string in __main__.__dict__
        except SyntaxError:
            raise SyntaxError("CommandEvent at "+`self.time`+" contained a syntax error:'"+self.command_string+"'")

    

            
# Simulation stores its events in a linear-time priority queue (i.e., a
# sorted list.) For efficiency, e.g. for spiking neuron simulations,
# we'll probably need to replace the linear priority queue with a more
# efficient one.  Jeff has an O(log N) minheap implementation, but
# there are likely to be many others to select from.
#
class Simulation(ParameterizedObject):
    """
    A simulation class that uses a simple sorted event list (instead of
    e.g. a sched.scheduler object) to manage events and dispatching.

    The Parameter 'register' indicates whether or not to register the
    Simulation as being part of Topographica; that is, register would
    be false for use of the Simulation outside Topographica. With
    register True, the Simulation is set to be topo.sim, which
    other Topographica commands and classes might look for.
    """
    ### JABALERT! Is step_mode even implemented?
    step_mode = BooleanParameter(default=False)
    register = BooleanParameter(default=True)

    startup_commands = Parameter(
        instantiate=True,
        default=[],
        doc="""
            List of string commands that will be exec'd in
            __main__.__dict__ (i.e. as if they were entered at the command prompt)
            before this simulation is unpickled. Allows e.g. to make sure items
            have been imported before scheduled_commands are run.
            """)
              

    def __init__(self,**config):
        """
        Create the Simulation and register it as topo.sim unless
        register==False.
        
           step_mode = debugging flag, causing the simulation to stop
                       before each tick.
        """
        super(Simulation,self).__init__(**config)

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
        the Simulation. See objects().
        """
        if not isinstance(item_name,str):
            raise TypeError("Expected string (objects in the Simulation are indexed by name).")
        try:
            return self.objects()[item_name]
        except KeyError:
            raise AttributeError("Simulation doesn't contain '"+item_name+"'.")


    def __setitem__(self,ep_name,ep):
        """
        Add ep to the simulation, setting its name to ep_name.
        ep must be an EventProcessor.

        If ep_name already exists in the simulation, ep overwrites
        the original object (as for a dictionary).

        If the ep itself already exists in the simulation, a
        warning is printed and the ep is not added.

        Note: EventProcessors do not necessarily have to be added to
        the simulation to be used, but otherwise they will not receive the
        start() message.  Adding a node to the simulation also sets the
        backlink node.simulation, so that the node can enqueue events
        and read the simulation clock.
        """
        if not isinstance(ep_name,str):
           raise TypeError("Expected string for item name (EPs in the Simulation are indexed by name).")

        if not isinstance(ep,EventProcessor):
           raise TypeError("Expected EventProcessor: objects in the Simulation must be EPs.")

        if ep in self._event_processors.values():
            self.warning("EventProcessor "+str(ep)+" () already exists in the simulation and will not be added.")
        else:
            ep.name=ep_name
            # CEBHACKALERT: if this is overwriting an existing EP,
            # it ought to delete it properly (i.e. remove connections
            # etc). We need a delete() method already anyway.
            self._event_processors[ep_name] = ep
            ep.simulation = self
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
        Run the simulation by starting the event scheduler.

        parameters:
          duration = time to run in simulation time. Default: run indefinitely.
          until    = time to stop in simulation time. Default: run indefinitely.
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
                # then the event is stale, so print a warning and
                # discard it.                

                self.warning('Discarding stale event from',(self.events[0].conn.src,self.events[0].conn.src_port),
                             'to',(self.events[0].conn.dest,self.events[0].conn.dest_port),
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
                # (I kept the try/catch for speed - will usually be EPConnectionEvent -
                #  but I haven't checked the impact. Presumably it's tiny.
                #  Could be simplified to:
                #  if isinstance(event,EPConnectionEvent):
                #      self.verbose...
                #  elif isinstance(event,CommandEvent):
                #      self.verbose...
                #  else:
                #      self.verbose...     )
                try:
                    self.verbose("Delivering event from",event.conn.src.name,
                                 "to",event.conn.dest.name,"at",self._time)
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


    def enqueue_event_abs(self,new_event):
        """
        Enqueue an Event at an absolute simulation clock time.
        """
        assert isinstance(new_event,Event)

        # The new event goes at the end of the event queue if there
        # isn't a queue right now, or if it's later than the last
        # event's time.  Otherwise, it's inserted at the appropriate
        # position somewhere inside the event queue.
        if not self.events or new_event.time >= self.events[-1].time:
            self.events.append(new_event)
            return

        for i,e in enumerate(self.events):
            if new_event.time < e.time:
                self.events.insert(i,new_event)
                break

    def enqueue_event_rel(self,event):
        """
        Enqueue an Event at a time relative to the current simulation clock.

        The incoming event's time is treated as a delay and is added
        to the simulation's current time.
        """
        event.time+=self._time
        self.enqueue_event_abs(event)

        
    def schedule_command(self,time,command_string,absolute_time=True):
        """
        Add a command to execute in __main__.__dict__ at the
        specified time.

        The command should be a string.

        If absolute_time is False, then time is treated as a delay,
        and the command will be executed at the simulator's current time
        plus this delay.
        """
        event = CommandEvent(time=time,command_string=command_string)
        if absolute_time:
            self.enqueue_event_abs(event)
        else:
            self.enqueue_event_rel(event)
        

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
        """Pop a scheduler off the stack."""
        self._time, self.events = self._events_stack.pop()


    def state_len(self):
        """Return number of event queues in _events_stack."""
        return len(self._events_stack)


    def connect(self,
                src,
                dest,
                src_port=None,
                dest_port=None,
                delay=0,connection_type=EPConnection,**connection_params):
        """
        Connect the source to the destination, at the appropriate ports,
        if any are given (src and dest are strings, naming the required
        EPs).

        src and dest should already be part of the simulation.

        Returns the connection that was created.

        If the connection hasn't been given a name, it defaults to
        'srcTodest'
        """
        if 'name' not in connection_params:
            # Might want to have a way of altering the name if this one's
            # already in use. At the moment, an error is raised (correctly).
            connection_params['name'] = src+'To'+dest
        
        conn = connection_type(src=self[src],dest=self[dest],src_port=src_port,dest_port=dest_port,delay=delay,**connection_params)
        self[src]._connect_to(conn)
        self[dest]._connect_from(conn)
        return conn
    

    ### CEBALERT: why not just event_processors()?
    ###
    ### It might be possible to come up with a more expressive name
    ### for this function.  It should mean 'anything that exists in
    ### the simulation universe, i.e. all EventProcessors'.
    ###
    def objects(self,baseclass=EventProcessor):
        """
        Return a list of simulation objects having the specified base
        class.  All simulation objects have a base class of
        EventProcessor, and so the baseclass must be either
        EventProcessor or one of its subclasses.

        To see what EPs are in the simulator, type e.g.
         topo.sim.objects().keys()
        """
        return dict([(ep_name,ep)
                     for (ep_name,ep) in self._event_processors.items()
                     if isinstance(ep,baseclass)])
