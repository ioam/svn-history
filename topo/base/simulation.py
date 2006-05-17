"""
A general-purpose Simulation class for discrete events.  

The Simulation object is the central object of a simulation.  It
handles the simulation clock time and maintains communication between
the components of the simulation.

A simulation is structured as a directed graph of event-processing
nodes called EventProcessors (EPs).  EventProcessors generate
data-carrying Events, which are routed through the graph to other
EventProcessors via delayed connections.  Most objects in the
simulation will be a subclass of EventProcessor, customized to provide
some specific behavior.

There are different subclasses of Event, each doing different types of
computation, and each can contain any arbitrary Python data.  A
simulation begins by giving each EventProcessor an opportunity to send
any initial events.  It then proceeds by processing and delivering
events to EventProcessors in time order.  After all events for the
current time are processed, the simulation gives each EventProcessor a
chance to do any final computation, after which simulation time skips
to the time of the earliest event remaining in the queue.


PORTS

All connections between EPs are tagged with a source port and a
destination port.  Ports are internal addresses that EPs can use to
distinguish between inputs and outputs.  A port specifier can be any
hashable Python object.  If not specified, the input and output ports
for a connection default to None.

src_ports distinguish different types of output that an EP may
produce. When sending output, the EP must call self.send_output()
separately for each port.  dest_ports distinguish different types of
input an EP may receive and process.  The EP is free to interpret the
input port designation on an incoming event in any way it chooses.

An example dest_port might be for an EP that receives 'ordinary'
neural activity on the default port, and receives a separate
modulatory signal that influences learning.  The originator of the
modulatory signal might have a connection to the EP with dest_port =
'modulation'.  Multiple ports can be grouped by a dest EP by assuming
a convention that the keys are tuples,
e.g. ('jointnormalize','Conn1'), ('jointnormalize','Conn2').

An example src_port use might be an EP that sends different
events to itself than it sends out to other EPs.  In this case the
self connections might have src_port = 'recurrent'.


CURRENT SIMULATION

The current Simulation, which can be accessed through the instance of
the Singleton class SimSingleton(), is the most recent Simulation to
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
        """Method to be overridden if the subclass needs initialization."""
        pass



class SimSingleton(Singleton):
    """Provides access to a single shared instance of Simulation."""
    
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
        """Create a new simulation object when needed."""
        # The Simulation constructor will call SimSingleton's change_sim()
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

    def __delitem__(self,item_name):
        """Allow dictionary-style access to the simulation."""
        del self.actual_sim[item_name]


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

        # A subclass could use another data stucture to optimize operations
        # specific to itself, if it also overrides _connect_from().
        self.in_connections = []
        self.out_connections = []

        self.simulation = None


    # if extra parameters are required for an EP subclass, a
    # dictionary could be added to Simulation.connect() to hold
    # them, and passed on here
    def _connect_to(self,conn):
        """
        Add the specified connection to the list of outgoing connections.
        Should only be called from Simulation.connect().
        """
        for existing_connection in self.out_connections:
            if existing_connection.name==conn.name and existing_connection.dest==conn.dest:
                raise ValueError('A connection out of an EventProcessor must have a unique name; "%s" out of %s already exists'%(conn.name,self.name))
  
        self.out_connections.append(conn)


    def _connect_from(self,conn):
        """
        Add the specified connection to the list of incoming connections.
        Should only be called from Simulation.connect().
        """
        for existing_connection in self.in_connections:
            if existing_connection.name == conn.name:
                raise ValueError('A connection into an EventProcessor must have a unique name; "%s" into %s already exists'%(conn.name,self.name))

        self.in_connections.append(conn)


    def start(self):
        """        
        Called by the simulation when the EventProcessor is added to
        the simulation.

        If an EventProcessor needs to have any code run when it is
        added to the simulation, the code can be put into this method
        in the subclass.
        """
        pass


    def send_output(self,src_port=None,data=None):
        """
        Send some data out to all connections on the given src_port.
        """
        out_conns_on_src_port = [conn for conn in self.out_connections
                                 if conn.src_port==src_port]

        for conn in out_conns_on_src_port:
            e=EPConnectionEvent(conn.delay+self.simulation.time(),conn,data)
            self.simulation.enqueue_event(e)
            

    def input_event(self,conn,data):
        """
        Called by the simulation when an EPConnectionEvent is delivered;
        the EventProcessor should process the data somehow.
        """
        raise NotImplementedError


    def process_current_time(self):
        """
        Called by the simulation before advancing the simulation
        time.  Allows the event processor to do any computation that
        requires that all events for this time have been delivered.
        Computations performed in this method should not generate any
        events with a zero time delay, or else causality could be
        violated. (By default, does nothing.)
        """
        pass
    


class EventProcessorParameter(Parameter):
    """Parameter whose value can be any EventProcessor instance."""
    
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
    src = EventProcessorParameter(default=None,constant=True,precedence=0.10,doc=
       """The EventProcessor from which messages originate.""")
    
    dest = EventProcessorParameter(default=None,constant=True,precedence=0.11,doc=
       """The EventProcessor to which messages are delivered.""")
    
    src_port = Parameter(default=None,precedence=0.20,doc=
       """
       Identifier that can be used to distinguish different types of outgoing connections.

       EventProcessors that generate only a single type of
       outgoing event will typically use a src_port of None.  However,
       if multiple types of communication are meaningful, the
       EventProcessor can accept other values for src_port.  It is up
       to the src EventProcessor to deliver appropriate data to each
       port, and to declare what will be sent over that port.
       """)
    
    dest_port = Parameter(default=None,precedence=0.21,doc=
       """
       Identifier that can be used to distinguish different types of incoming connections.

       EventProcessors that accept only a single type of incoming
       event will typically use a src_port of None.  However, if
       multiple types are of communication are meaningful, the
       EventProcessor can accept other values for dest_port.  It is up
       to the dest EventProcessor to process the data appropriately
       for each port, and to define what is expected to be sent to
       that port.
       """)

    delay = Parameter(default=0,doc=
       """Simulation time between when each Event is generated by the src and when it is delivered to the dest.""")


class Event(object):
    """Hierarchy of classes for storing simulation events of various types."""
    def __init__(self,time):
        self.time = time
        
    def __call__(self):
        """
        Cause some computation to be performed, deliver a message, etc.,
        as appropriate for each subtype of Event.
        """
        raise NotImplementedError


class EPConnectionEvent(Event):
    """
    An Event for delivery to an EPConnection.

    Provides access to a data field, which can be used for anything
    the src wants to provide, and a link to the connection over which
    it has arrived, so that the dest can determine what to do with the
    data.
    """
    def __init__(self,time,conn,data=None):
        super(EPConnectionEvent,self).__init__(time)
        assert isinstance(conn,EPConnection)
        ### JABALERT: Do we always want to deepcopy here?
        ### E.g. the same data sent to a dozen ports should probably have
        ### only one copy.
        self.data = deepcopy(data)
        self.conn = conn

    def __call__(self):
        self.conn.dest.input_event(self.conn,self.data)

    def __repr__(self):
        return "EPConnectionEvent(time="+`self.time`+",conn="+`self.conn`+")"


class CommandEvent(Event):
    """An Event consisting of a command string to execute."""

    def __init__(self,time,command_string):
        super(CommandEvent,self).__init__(time)
        self.command_string = command_string

    def __repr__(self):
        return "CommandEvent(time="+`self.time`+" ,command_string='"+self.command_string+"')"
    
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
        # Presumably here to avoid importing __main__ into the rest of the file
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
    Simulation with SimSingleton, which can be used to provide a
    single point of contact for accessing the Simulation.
    """
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
        Create the Simulation and register it with SimSingleton unless
        register==False.        
        """
        super(Simulation,self).__init__(**config)

        self._time = FixedPoint("0.0",4)
        self._event_processors = {}

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

        Note: EventProcessors do not necessarily have to be added to
        the simulation to be used, but otherwise they will not receive the
        start() message.  Adding a node to the simulation also sets the
        backlink node.simulation, so that the node can enqueue events
        and read the simulation time.
        """
        if not isinstance(ep_name,str):
           raise TypeError("Expected string for item name (EPs in the Simulation are indexed by name).")

        if not isinstance(ep,EventProcessor):
           raise TypeError("Expected EventProcessor: objects in the Simulation must be EPs.")

        if ep in self._event_processors.values():
            self.warning("EventProcessor "+str(ep)+" () already exists in the simulation and will not be added.")
        else:
            ep.name=ep_name
            # deletes and overwrites any existing EP with the same name,
            # silently, as if a dictionary
            if ep.name in self._event_processors: del self[ep.name]
                
            self._event_processors[ep_name] = ep
            ep.simulation = self
            ep.start()


    def __delitem__(self,ep_name):
        """
        Dictionary-style deletion of EPs from the simulation; see __delete_ep().

        Deletes EP from simulation, plus connections that come into it and
        connections that go out of it.
        """
        if not isinstance(ep_name,str):
           raise TypeError("Expected string for item name (EPs in the Simulation are indexed by name).")

        self.__delete_ep(ep_name)


    # CEBHACKALERT: should be reimplemented. Results in unnecessary looping,
    # is difficult to understand, and contains the same code twice. But it
    # does work.
    def __delete_ep(self,ep_name):
        """
        Remove the specified EventProcessor from the simulation, plus
        delete connections that come into it and connections that go from it.

        (Used by 'del topo.sim[ep_name]' (as for a dictionary) to delete
        event processors from the simulation.)
        """
        ep = self[ep_name]
        
        # remove from simulation list of eps
        del self._event_processors[ep_name]

        # remove out_conections that go to this ep
        for conn in ep.in_connections:
            i = 0
            to_del = []
            for out_conn in conn.src.out_connections:
                if out_conn.dest is ep:
                    to_del.append(i)
                i+=1

            for i in to_del:
                del conn.src.out_connections[i]

        # remove in_connections that come from this ep
        for conn in ep.out_connections:
            i = 0
            to_del = []
            for in_conn in conn.dest.in_connections:
                if in_conn.src is ep:
                    to_del.append(i)
                i+=1

            for i in to_del:
                del conn.dest.in_connections[i]


    def time(self):
        """
        Return the current simulation time as a FixedPoint object.
        
	If the time returned will be used in the computation of a
        floating point variable, it should be cast into a floating
        point number by float().
        """
        return self._time

    
    def run(self,duration=Forever,until=Forever):
        """
        Process simulation events for the specified duration or until the specified time.

        Arguments:
          duration = length of simulation time to run. Default: run indefinitely.
          until    = maximum simulation time to simulate. Default: run indefinitely.

        If both duration and until are used, the one that is reached first will apply.
        """
        # Complicated expression for min(time+duration,until)
        if duration == Forever:
            stop_time = until
        elif until == Forever:
            stop_time = self._time + duration
        else:
            stop_time = min(self._time+duration,until)
            
        did_event = False

        while self.events and (stop_time == Forever or self._time <= stop_time):
            # Loop while there are events and it's not time to stop.
            
            if self.events[0].time < self._time:
                # Warn and then discard events scheduled *before* the current time
                self.warning('Discarding event',repr(self.events[0]))
                self.events.pop(0)
                
            elif self.events[0].time > self._time:
                # Before moving on to the next time, do any processing
                # necessary for the current time.  This is necessary only
                # if some event has been delivered at the current time.

                if did_event:
                    did_event = False
                    self.debug("Time to sleep. Current time =",self._time,
                               ".  Next event time =",self.events[0].time)
                    for ep in self._event_processors.values():
                        ep.process_current_time()
                    
                # Set the time to the frontmost event.  Bear in mind
                # that the front event may have been changed by the
                # .process_current_time() calls.
                self._time = self.events[0].time
                
            else:
                # Pop and call the event at the head of the queue.
                event = self.events.pop(0)
                self.verbose("Delivering "+ repr(event))
                event()
                did_event=True


        # The time needs updating if the events have not done it.
        #if self.events and self.events[0].time >= stop_time:
        if stop_time != Forever:
            self._time = stop_time


    def enqueue_event(self,event):
        """
        Enqueue an Event at an absolute simulation clock time.
        """
        assert isinstance(event,Event)

        # The new event goes at the end of the event queue if there
        # isn't a queue right now, or if it's later than the last
        # event's time.  Otherwise, it's inserted at the appropriate
        # position somewhere inside the event queue.
        if not self.events or event.time >= self.events[-1].time:
            self.events.append(event)
            return

        for i,e in enumerate(self.events):
            if event.time < e.time:
                self.events.insert(i,event)
                break

    def schedule_command(self,time,command_string):
        """
        Add a command to execute in __main__.__dict__ at the
        specified time.

        The command should be a string.
        """
        event = CommandEvent(time=time,command_string=command_string)
        self.enqueue_event(event)
        

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


    # Could just process src and dest in conn_params.  
    # Also could accept the connection already created, rather than
    # creating one.
    def connect(self,src,dest,connection_type=EPConnection,**conn_params):
        """
        Connect the src EventProcessor to the dest EventProcessor.

        The src and dest should be string names of existing EPs.
        Returns the connection that was created.  If the connection
        hasn't been given a name, it defaults to 'srcTodest'.
        """
        
        if 'name' not in conn_params:
            # Might want to have a way of altering the name if this one's
            # already in use. At the moment, an error is raised (correctly).
            conn_params['name'] = src+'To'+dest

        # Looks up src and dest in our dictionary of objects
        conn = connection_type(src=self[src],dest=self[dest],**conn_params)
        self[src]._connect_to(conn)
        self[dest]._connect_from(conn)
        return conn
    

    ### Could change the name to event_processors().
    def objects(self,baseclass=EventProcessor):
        """
        Return a list of simulation objects having the specified base
        class.  All simulation objects have a base class of
        EventProcessor, and so the baseclass must be either
        EventProcessor or one of its subclasses.

        If there is a simulator called s, you can type e.g.
        s.objects().keys() to see a list of all objects.
        """
        return dict([(ep_name,ep)
                     for (ep_name,ep) in self._event_processors.items()
                     if isinstance(ep,baseclass)])
