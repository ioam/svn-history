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
'Modulation'.  Multiple ports can be grouped by a dest EP by assuming
a convention that the keys are tuples,
e.g. ('JointNormalize','Group1'), ('JointNormalize','Group2').

An example src_port use might be an EP that sends different events to
itself than it sends out to other EPs.  In this case the self
connections might have src_port = 'Recurrent', and probably also a
special dest_port.


CURRENT SIMULATION

The current Simulation, which can be accessed through the instance of
the Singleton class SimSingleton(), is the most recent Simulation to
have been created with register=True (the default).


$Id$
"""
__version__='$Revision$'

from parameterizedobject import ParameterizedObject, Parameter
from parameterclasses import Number, BooleanParameter,wrap_callable
from copy import copy, deepcopy
from fixedpoint import FixedPoint
import bisect

SLEEP_EXCEPTION = "Sleep Exception"
STOP = "Simulation Stopped"

# CEBALERT: Is it dangerous to have 'Forever' implemented
# like this? To start with, min(Forever,1) gives
# FixedPoint('-1.00,2') i.e. Forever.
Forever = FixedPoint(-1)

# Default path to the current simulation, from main
# Only to be used by script_repr(), to allow it to generate
# a runnable script
simulation_path="topo.sim"

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

    def __getattribute__(self,name):
        """
        If the SimSingleton object has the attribute, return it; if the
        actual_sim has the attribute, return it; otherwise, an AttributeError
        relating to Simulation will be raised (as usual).
        """
        try:
            return object.__getattribute__(self,name)
        except AttributeError:
            actual_sim = object.__getattribute__(self,'actual_sim')
            return getattr(actual_sim,name)

    def __setattr__(self,name,value):
        """
        If this object has the attribute name, set it to value.
        Otherwise, set self.actual_sim.name=value.

        (Unless an attribute is inserted directly into this object's
        __dict__, the only attribute it has is 'actual_sim'. So, this
        method really sets attributes on actual_sim.)
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


    ## CEBALERT: syntax like "'V1' in topo.sim" does not work
    def __getitem__(self,item_name):
        """Allow dictionary-style access to the simulation."""
        return self.actual_sim[item_name]

    def __setitem__(self,item_name,item_value):
        """Allow dictionary-style access to the simulation."""
        self.actual_sim[item_name]=item_value

    def __delitem__(self,item_name):
        """Allow dictionary-style deletion of objects from the simulation."""
        del self.actual_sim[item_name]

    def __getstate__(self):
        """Avoid calling actual_sim's __getstate__ directly.""" 
        return {'actual_sim':self.actual_sim}

    def __setstate__(self,state):
        """On unpickling, change to the pickled simulation."""
        self.change_sim(state['actual_sim'])
        
        


class EventProcessor(ParameterizedObject):
    """
    Base class for EventProcessors, i.e. objects that can accept and
    handle events.  This base class handles the basic mechanics of
    connections and sending events, and stores both incoming and outgoing
    connections.

    The dest_ports attribute specifies which dest_ports are supported
    by this class; subclasses can augment or change this list if they
    wish.  The special value dest_ports=None means to accept
    connections to any dest_port, while dest_ports=[None,'Trigger']
    means that only connections to port None or port 'Trigger' are
    accepted.

    Similarly, the src_ports attribute specifies which src_ports will
    be given output by this class.
    """
    _abstract_class_name = "EventProcessor"

    src_ports=[None]
    
    dest_ports=[None]

    name = Parameter(constant=True)

    def __init__(self,**params):
        """
        Create an EventProcessor.

        Note that just creating an EventProcessor does not mean it is
        part of the simulation (i.e. it is not in the simulation's list
        of EventProcessors, and it will not have its start() method called).
        To add an EventProcessor e to a simulation s, simply do
        s['name_of_e']=e. At this point, e's 'name' attribute will be set
        to 'name_of_e'.
        """
        super(EventProcessor,self).__init__(**params)

        # A subclass could use another data stucture to optimize operations
        # specific to itself, if it also overrides _dest_connect().
        self.in_connections = []
        self.out_connections = []

        self.simulation = None

    def _port_match(self,key,portlist):
        """
        Returns True if the given key matches any port on the given list.

        In the default implementation, a port is considered a match if
        the port is == to the key, but subclasses of EventProcessor can
        override this to provide weaker forms of matching.
        """
        return key in portlist

    # if extra parameters are required for an EP subclass, a
    # dictionary could be added to Simulation.connect() to hold
    # them, and passed on here
    def _src_connect(self,conn):
        """
        Add the specified connection to the list of outgoing connections.
        Should only be called from Simulation.connect().
        """

        if self.src_ports and not self._port_match(conn.src_port,self.src_ports):
            raise ValueError("%s is not on the list of ports provided for outgoing connections for %s: %s." %
                             (str(conn.src_port), self.__class__, str(self.src_ports)))

        # CB: outgoing connection must be uniquely named among others
        # going to the same destination.
        for existing_connection in self.out_connections:
            if existing_connection.name==conn.name and existing_connection.dest==conn.dest:
                raise ValueError('A connection out of an EventProcessor must have a unique name among connections to a particular destination; "%s" out of %s into %s already exists'%(conn.name,conn.dest,self.name))

        # CB: alternative: outgoing connection must have a unique name
##         for existing_connection in self.out_connections:
##             if existing_connection.name==conn.name:
##                 raise ValueError('A connection out of an EventProcessor must have a unique name; "%s" out of %s already exists'%(conn.name,self.name))
  
        self.out_connections.append(conn)


    def _dest_connect(self,conn):
        """
        Add the specified connection to the list of incoming connections.
        Should only be called from Simulation.connect().
        """

        if self.dest_ports and not self._port_match(conn.dest_port,self.dest_ports):
            raise ValueError("%s is not on the list of ports allowed for incoming connections for %s: %s." %
                             (str(conn.dest_port), self.__class__, str(self.dest_ports)))

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

    ### JABALERT: Should change send_output to accept a list of src_ports, not a single src_port.
    def send_output(self,src_port=None,data=None):
        """Send some data out to all connections on the given src_port."""
        out_conns_on_src_port = [conn for conn in self.out_connections
                                 if self._port_match(conn.src_port,[src_port])]

        for conn in out_conns_on_src_port:
            self.verbose("Time " + str(self.simulation.time()) + ":" +
                         " Sending output on src_port " + str(src_port) +
                         " via connection " + conn.name +
                         " to " + conn.dest.name + ".")
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
    
    def state_push(self):
        """
        Save the current state of this EventProcessor to an internal stack.

        This method is used by operations that need to test the
        response of the EventProcessor without permanently altering
        its state.  All EventProcessors that maintain short-term state
        should save and restore it using these commands.
        """
        pass

    def state_pop(self):
        """
        Pop the most recently saved state off the stack.

        See state_push() for more details.
        """
        pass

    def script_repr(self,imports=[],prefix="    "):
        """Generate a runnable command for creating this EventProcessor."""
        return simulation_path+"['"+self.name+"']="+\
        super(EventProcessor,self).script_repr(imports=imports,prefix=prefix)



        
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

## JPALERT: This type-checking is redundant, since
##     Simulation.connect() only allows the user to create connections
##     between existing simulation objects, which must be EPs.  Type
##     checking here means that it is impossible to ever instantiate
##     an EPConnection in any situation (including debugging) w/o
##     making src and dest be EPs.  However, there is nothing I can
##     find that requires that the src or dest be EPs.  While some
##     *subclasses* of EPConnection (such as Projection) do require
##     that their src and dest support the interfaces of some
##     *subclasses* of EventProcessor (e.g. Sheet.activity), there is
##     no reason that those objects have to be EPs, per se.  IMO,
##     excessive type checking removes much of the power of using a
##     dynamic language like Python.
    
##     src = EventProcessorParameter(default=None,constant=True,precedence=0.10,doc=
##        """The EventProcessor from which messages originate.""")
    
##     dest = EventProcessorParameter(default=None,constant=True,precedence=0.11,doc=
##        """The EventProcessor to which messages are delivered.""")

    src = Parameter(default=None,constant=True,precedence=0.10,doc=
       """The EventProcessor from which messages originate.""")
    
    dest = Parameter(default=None,constant=True,precedence=0.11,doc=
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

    delay = Number(default=0,doc=
       """Simulation time between when each Event is generated by the src and when it is delivered to the dest.""")

    private = BooleanParameter(default=False,doc=
       """Set to true if this connection is for internal use only, not to be manipulated by a user.""")


    # CEBALERT: should be reimplemented. It's difficult to understand,
    # and contains the same code twice. But it does work.
    def remove(self):
        """
        Remove this connection from its src's list of out_connections and its
        dest's list of in_connections.
        """
        # remove from EPs that have this as in_connection
        i = 0
        to_del = []
        for in_conn in self.dest.in_connections:
            if in_conn is self:
                to_del.append(i)
            i+=1

        for i in to_del:
            del self.dest.in_connections[i]

        # remove from EPs that have this as out_connection
        i = 0
        to_del = []
        for out_conn in self.src.out_connections:
            if out_conn is self:
                to_del.append(i)
            i+=1

        for i in to_del:
            del self.src.out_connections[i]


    def script_repr(self,imports=[],prefix="    "):
        """Generate a runnable command for creating this connection."""

        if self.private:
            return ""
        
        settings=[]
        for name,val in self.get_param_values():
            try: # There may be a better way to figure out which parameters specify classes
                if issubclass(val,object):
                    rep=val.__name__
                    # Generate import statement
                    cls = val.__name__
                    mod = val.__module__
                    imports.append("from %s import %s" % (mod,cls))
            except TypeError:
                if name=="src" or name=="dest":
                    rep=None
                elif isinstance(val,ParameterizedObject):
                    rep=val.script_repr(imports=imports,prefix=prefix+"    ")
                else:
                    rep=repr(val)

            if rep is not None:
                settings.append('%s=%s' % (name,rep))

        # add import statement
        cls = self.__class__.__name__
        mod = self.__module__
        imports.append("from %s import %s" % (mod,cls))

        return simulation_path+".connect('"+self.src.name+"','"+self.dest.name+ \
               "',connection_type="+self.__class__.__name__+ \
               ",\n"+prefix+(",\n"+prefix).join(settings) + ")"


class Event(object):
    """Hierarchy of classes for storing simulation events of various types."""
    _abstract_class_name = "Event"

    def __init__(self,time):
        self.time = time
        
    def __call__(self,sim):
        """
        Cause some computation to be performed, deliver a message, etc.,
        as appropriate for each subtype of Event.  Should be passed the
        simulation object, to allow access to .time() etc.        
        """
        raise NotImplementedError

    def __cmp__(self,ev):
        """
        Implements event comparison by time, allowing sorting,
        and queue maintenance  using bisect module or minheap
        implementations, if needed.

        NOTE: identity comparisons should always be done using the
        'is' operator, not '=='.
        """
        if self.time > ev.time:
            return 1
        elif self.time < ev.time:
            return -1
        else:
            return 0


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

    def __call__(self,sim):
        self.conn.dest.input_event(self.conn,self.data)

    def __repr__(self):
        return "EPConnectionEvent(time="+`self.time`+",conn="+`self.conn`+")"


class CommandEvent(Event):
    """An Event consisting of a command string to execute."""

    def __init__(self,time,command_string):
        """
        Add the event to the simulation.

        Prints a warning if the syntax is incorrect.
        """
        self.command_string = command_string
        self.__test()
        super(CommandEvent,self).__init__(time)
        
    def __repr__(self):
        return "CommandEvent(time="+`self.time`+", command_string='"+self.command_string+"')"


    def script_repr(self,imports=[],prefix="    "):
        """Generate a runnable command for creating this CommandEvent."""
        return simulation_path+".schedule_command("+`self.time`+",'"+ self.command_string+"')"


    # CEBALERT: should we stop execution after detecting errors
    # (rather than just printing a warning) in __call__() and
    # __test()? After deciding, make docstrings match behavior.
    def __call__(self,sim):
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

        ParameterizedObject(name='CommandEvent').message("Time %08.2f: Running command %s" \
                                                         % (self.time,self.command_string))
        
        try:
            exec self.command_string in __main__.__dict__
            
        except Exception, err:
            ParameterizedObject(name='CommandEvent').warning(`self`+' was not executed because it would cause an error - '+`err`+': "' +err[0]+'".')
        
    def __test(self):
        """
        Check for SyntaxErrors in the command.
        
        All other errors are ignored since __main__ could be in any state at the scheduled time.
        """
        # This method doesn't affect an object the user has, because it executes the command in a new
        # dictionary. So for instance, an iterator will not be advanced because it won't exist in the
        # new dictionary. But the syntax of the command will be checked.
        #
        # CB: we could check for more errors, e.g. by checking for NameError and ignoring *only*
        # that error. Then we would catch things like attempting to schedule 5/0.
        # But I don't think we should actually do that (e.g. someone could be catching
        # divide-by-zero errors later in their simulation).

        try:
            exec self.command_string in {}
        except SyntaxError, err :
            # CEBALERT: why don't the offset and text attributes contain anything?
            # print err.filename,err.lineno,err.offset,err.text
            # (same above in __call__() - why don't some of the attributes contain anything?)
            ParameterizedObject(name='CommandEvent').warning('The scheduled command "'+self.command_string+'" will not be executed because it contains a syntax error: "'+err[0]+'".')
        except:
            pass
        

class FunctionEvent(Event):
    """
    Event that executes a given function function(*args,**kw).
    """
    def __init__(self,time,fn,*args,**kw):
        super(FunctionEvent,self).__init__(time)
        self.fn = wrap_callable(fn)
        self.args = args
        self.kw = kw

    def __call__(self,sim):
        self.fn(*self.args,**self.kw)

    def __repr__(self):
        return 'FunctionEvent(%s,%s,*%s,**%s)' % (`self.time`,`self.fn`,`self.args`,`self.kw`)

class EventSequence(Event):
    """
    Event that contains a sequence of other events to be scheduled and
    executed.

    The .time attributes of the events in the sequence are interpreted
    as offsets relative to the start time of the sequence itself.
    """
    def __init__(self,time,sequence):
        super(EventSequence,self).__init__(time)
        self.sequence = sequence

    def __call__(self,sim):

        # Enqueue all the events in the sequence, offsetting their
        # times from the current time
        sched_time = sim.time()
        for ev in self.sequence:
            new_ev = copy(ev)
            sched_time += ev.time
            new_ev.time = sched_time
            sim.enqueue_event(new_ev)

    def __repr__(self):
        return 'EventSequence(%s,%s)' % (`self.time`,`self.sequence`)



class PeriodicEventSequence(EventSequence):
    """
    An EventSequence that reschedules itself periodically

    Takes a period argument that determines how often the sequence
    will be scheduled.   If the length of the sequence is longer than
    the period, then the length of the sequence will be used as the period.
    """
    ## JPHACKALERT: This should really be refactored into a
    ## PeriodicEvent class that periodically executes a single event,
    ## then the user can construct a periodic sequence using a
    ## combination of PeriodicEvent and EventSequence.  This would
    ## change the behavior if the sequence length is longer than the
    ## period, but I'm not sure how important that is, and it might
    ## actually be useful the other way.
    

    def __init__(self,time,period,sequence):
        super(PeriodicEventSequence,self).__init__(time,sequence)
        self.period = period
        
    def __call__(self,sim):        
        super(PeriodicEventSequence,self).__call__(sim)

        # Find the timed length of the sequence
        seq_length = sum(e.time for e in self.sequence)

        if seq_length < self.period:
            # If the sequence is shorter than the period, then reschedule
            # the sequence to occur again after the period
            self.time += self.period
        else:
            # If the sequence is longer than the period, then
            # reschedule to start after the sequence ends.
            self.time += seq_length
        sim.enqueue_event(self)

    def __repr__(self):
        return 'PeriodicEventSequence(%s,%s,%s)' % (`self.time`,`self.period`,`self.sequence`)


############ Timer code ############
#
# CB: code that previously existed in various places now collected
# together. The original timing code was not properly tested, and the
# current code has not been tested either: needs writing cleanly and
# testing.
#  
### JP: Is it possible that some or all of this can be more cleanly
### implemented using PeriodicEvents?

import time
from math import fmod,floor
class SomeTimer(ParameterizedObject):
    """
    Provides a countdown timer for functions that run repeatedly.
    
    There are two distinct ways to use the timer.

    The first, via call_and_time(), is for calling some function every
    specified number of steps for a specified duration. Currently
    call_and_time() is used for timing calls to simulation.run() every
    1.0 steps for 100 iterations. See the Simulation class for an
    example of using the timer in this way.

    The second, via X(), is for calling some function repeatedly a
    specified number of times. A case to use X() would be timing
    pattern presentations, where the number of times the
    pattern_presenter will be called is known in
    advance. Additionally, this method allows a list of arguments to
    be passed to the function (in this case, the permutation for each
    call).
    """
    # * parameters to control formatting?
    # * the parameter types for some of the following could be more specific
    # * tried to use one message format whether X or call_and_time is being used;
    #   could test for which (via if fixed_num_calls) if we do need two formats
    step = Parameter(default=None,doc=
        """Only relevant with call_fixed_duration(), not call_fixed_num_times(). 
        
           Each iteration, func is called as func(step).
    
           For example, step=1 with func set to topo.sim.time would cause
           the simulation time to advance once per iteration.

           The default value (None) gives 50 iterations for any value of simulation_duration
           passed to call_fixed_duration(simulation_duration).""")
    
    estimate_interval = Number(default=50,doc=
        """Interval in simulation time between estimates.""") 

    func = Parameter(default=None,instantiate=True,doc=
        """Function to be timed.""")

##     func_args = Parameter(default=None,instantiate=True,doc=
##         """Arguments passed to func at time of calling.""")

    simulation_time_fn = Parameter(default=None,instantiate=True,doc=
        """Function that returns the simulation time.""")

    real_time_fn = Parameter(default=time.time,instantiate=True,doc=
        """Function that returns the wallclock time.""")

    receive_messages = Parameter(default=[],instantiate=True,doc=
        """List of objects that will receive timing messages.
        Each must have a timing_message() method.""")

    receive_progress = Parameter(default=[],instantiate=True,doc=
        """List of objects that will receive the current 'percentage complete'
        value. Each must have a timing_value() method.""")

    stop = BooleanParameter(default=False,doc=
        """If set to True, execution of func (and timing) will cease at the end of
        the current iteration.""")


    def __pass_out_progress(self,val):
        [thing(val) for thing in self.receive_progress]
    
    def __pass_out_message(self,message):
        [thing(message) for thing in self.receive_messages]


    def __measure(self,fduration,step,arg_list=None):

        if not arg_list:
            # no list of arguments means not being called set number of times
            fixed_num_calls = False
        else:
            fixed_num_calls = True
            
        iters  = int(floor(fduration/step))
        remain = fmod(fduration, step)
        recenttimes=[]

        if not fixed_num_calls: arg_list=[step]*iters
        
        starttime=self.real_time_fn()
        simulation_starttime = self.simulation_time_fn()

        self.stop = False
        for i in xrange(iters):
            recenttimes.append(self.real_time_fn())
            length = len(recenttimes)

            if (length>self.estimate_interval):
                recenttimes.pop(0)
                length-=1

            self.func(arg_list[i])

            percent = 100.0*i/iters
            estimate = (iters-i)*(recenttimes[-1]-recenttimes[0])/length
            self.__pass_out_progress(percent)

            # Should say 'at current rate', since the calculation assumes linearity
            message = 'Time ' + str(self.simulation_time_fn()) + ': ' + \
                      str(int(percent)) + '% of ' + self.func.__name__ + ' ' + str(fduration) +\
                      (' [%02d' % int(estimate/60))+':' + \
                      ('%02d' % int(estimate%60))+ ' remaining]'
                
            self.__pass_out_message(message)

            if self.stop: break


        if not self.stop:
            if not fixed_num_calls:
                # ensure specified duration has been respected, since code above might not
                # complete specified duration (integer number of iterations)
                leftover = fduration+simulation_starttime-self.simulation_time_fn()
                if leftover>0: self.func(leftover)
            percent = 100   
            self.__pass_out_progress(percent)


            message = ('OK: %s (%0.2f) to time %0.2f  [%0.1f s]' %
                       (self.func.__name__,
                        max(self.simulation_time_fn()-simulation_starttime,fduration),
                        self.simulation_time_fn(),
                        self.real_time_fn()-starttime))
        else:
            message = "Interrupted %s at time %0.2f  [after %0.1f s]"%(self.func.__name__,
                                                                       self.simulation_time_fn(),
                                                                       self.real_time_fn()-starttime)

        self.__pass_out_message(message)

              
    def call_fixed_num_times(self,args_for_iterations):
        """
        Call self.func(args_for_iterations[i]) for all i in args_for_iterations.
        """
        self.__measure(len(args_for_iterations),1.0,arg_list=args_for_iterations)
    X=call_fixed_num_times
        
    
    def call_fixed_duration(self,fduration):
        """
        Call self.func(self.step or fduration/50.0) for fduration.
        """
        # default to 50 steps unless someone set otherwise
        step = self.step or fduration/50.0
        self.__measure(fduration,step)
    call_and_time=call_fixed_duration
        
        
# CB: use to get timing messages at the commandline:
# from topo.base.simulation import MessagePrinter
# topo.sim.timer.receive_messages.append(MessagePrinter().printm)
class MessagePrinter(object):
    def printm(self,x): print x

############ End of timer code ############





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
            __main__.__dict__ (i.e. as if they were entered at the
            command prompt) every time this simulation is unpickled
            (and will be executed before the simulation is itself
            unpickled).

            For example, allows items to be imported before
            scheduled_commands are run.
            """)

    # CB: Is this the simplest way to do this?
    # If we want this to be 'initial_commands' or something similar,
    # then check _time==0 in run() or something like that.
    execute_next = Parameter(
        instantiate=True,
        default=[],
        doc="""
        List of string commands that will be exec'd in __main__.__dict__
        (i.e. as if they were entered at the command prompt) when the
        simulation is next run(). These commands will run before any others,
        and are guaranteed only to run once (before being destroyed).
        """)

    def __init__(self,**params):
        """
        Create the Simulation and register it with SimSingleton unless
        register==False.        
        """
        super(Simulation,self).__init__(**params)

        self._time = FixedPoint("0.0",4)
        self._event_processors = {}

        if self.register:
            SimSingleton().change_sim(self)

        self.events = []
        self._events_stack = []

        # CB: make this a parameter for documentation? Otherwise nobody will know
        # about being able to adjust step.
        from topo.base.parameterclasses import wrap_callable # CEBALERT: remove with python 2.5
        # we set step to 2 so that by default timing doesn't slow simulation too much. but
        # e.g. leaving it as None would result in info at 2% increments of requested run duration,
        # no matter what duration (0.005 or 5, etc).
        self.timer = SomeTimer(func=wrap_callable(self.run),
                               simulation_time_fn=wrap_callable(self.time),step=2)

        

    def __getitem__(self,item_name):
        """
        Return item_name if it exists as an EventProcessor in
        the Simulation. See objects().
        """
        if not isinstance(item_name,str):
            raise TypeError("Expected string (objects in the Simulation are indexed by name); %s is a %s"%(item_name,type(item_name)))
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
            ep.initialized=False
            ep.name=ep_name
            ep.initialized=True
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


    def __delete_ep(self,ep_name):
        """
        Remove the specified EventProcessor from the simulation, plus
        delete connections that come into it and connections that go from it.

        (Used by 'del sim[ep_name]' (as for a dictionary) to delete
        an event processor from the simulation.)
        """
        ep = self[ep_name]
        
        # remove from simulation list of eps
        del self._event_processors[ep_name]

        # remove out_conections that go to this ep
        for conn in ep.in_connections:
            conn.remove()

        # remove in_connections that come from this ep
        for conn in ep.out_connections:
            conn.remove()


    def time(self):
        """
        Return the current simulation time as a FixedPoint object.
        
	If the time returned will be used in the computation of a
        floating point variable, it should be cast into a floating
        point number by float().
        """
        return self._time


    # Change current run() to _run(), and current run_and_time() to run()?

    # CEBALERT: need to simplify duration/until code. Hiding 'until' option
    # until it's fixed (presumably nobody's using it).
    def run_and_time(self,duration=Forever): # ,until=Forever):

        if duration==Forever:
            # CEBALERT: timing code not setup to handle indefinite durations
            # (e.g. 'Forever')
            self.run(duration)
            return
        else:
            self.timer.call_and_time(duration)


    def run(self,duration=Forever,until=Forever):
        """
        Process simulation events for the specified duration or until the specified time.

        Arguments:
          duration = length of simulation time to run. Default: run indefinitely.
          until    = maximum simulation time to simulate. Default: run indefinitely.

        If both duration and until are used, the one that is reached first will apply.
        """
        # CEBHACKALERT: If I do topo.sim.run(10), then topo.sim.run(until=3),
        # topo.sim._time returns to 3 (i.e. the simulation time can jump backwards).
        # JP: This because of the weird sim._time = stop_time line at the end of this method.
        # see my HACKALERT below.
        
        # Execute any commands in execute_next, and then remove them.
        [CommandEvent(time=self._time,command_string=cmd)(self) for cmd in self.execute_next]
        self.execute_next=[]
        
        # Complicated expression for min(time+duration,until)
        if duration == Forever:
            stop_time = FixedPoint(until)
        elif until == Forever:
            stop_time = self._time + duration
        else:
            stop_time = min(self._time+duration,FixedPoint(until))
            
        did_event = False

        while self.events and (stop_time == Forever or self._time <= stop_time):
            # Loop while there are events and it's not time to stop.
            
            if self.events[0].time < self._time:
                # Warn and then discard events scheduled *before* the current time
                self.warning('Discarding stale (unprocessed) event',repr(self.events[0]))
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
                #self.debug("Delivering "+ repr(event))
                event(self)
                did_event=True


        # The time needs updating if the events have not done it.
        #if self.events and self.events[0].time >= stop_time:

        # JPHACKALERT: This is weird.  It can cause time to go backwards,
        # (see CEBHACKALERT above).  Also, if the simulation runs out of
        # events before stop_time is reached, shouldn't that be reflected in
        # Simulation.time()?
        if stop_time != Forever :
            self._time = stop_time



    def enqueue_event(self,event):
        """
        Enqueue an Event at an absolute simulation clock time.
        """
        assert isinstance(event,Event)

        if not self.events or event >= self.events[-1]:
            # The new event goes at the end of the event queue if there
            # isn't a queue right now, or if it's later than the last
            # event's time. 
            self.events.append(event)
        elif event < self.events[0]:
            # If it's earlier than the first item it goes at the beginning.
            self.events.insert(0,event)
        else:
            # Otherwise, it's inserted at the appropriate
            # position somewhere inside the event queue.
            # New events are enqueued after (right of) existing
            # events with the same time, i.e. 'simultaneous' events
            # are executed FIFO.
            bisect.insort_right(self.events,event)

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
        Save a copy of the current state of the simulation for later restoration.

        The saved copy includes all the events on the simulator stack
        (saved using event_push()).  Each EventProcessor is also asked
        to save its own state.  This operation is useful for testing
        something while being able to roll back to the original state.
        """
        self.event_push()
        for ep in self._event_processors.values():
            ep.state_push()


    def state_pop(self):
        """
        Pop the most recently saved state off the stack.

        See state_push() for more details.
        """
        self.event_pop()
	for ep in self._event_processors.values():
            ep.state_pop()


    def event_push(self):
        """
        Save a copy of the events queue for later restoration.

        Same as state_push(), but does not ask EventProcessors to save
        their state.
        """
        self._events_stack.append((self._time,[copy(event) for event in self.events]))


    def event_pop(self):
        """
        Pop the most recently saved events queue off the stack.

        Same as state_pop(), but does not restore EventProcessors' state.
        """
        self._time, self.events = self._events_stack.pop()        


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
        self[src]._src_connect(conn)
        self[dest]._dest_connect(conn)
        return conn
    

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


    def connections(self):
        """Return a list of all unique connections to or from any object."""
        # The return value cannot be a dictionary like objects(),
        # because connection names are not guaranteed to be unique
        connlists =[o.in_connections + o.out_connections
                    for o in self.objects().values()]
        # Flatten one level
        conns=[]
        for cl in connlists:
            for c in cl:
                conns.append(c)
        return [c for c in set(conns)]


    def script_repr(self,imports=[],prefix="    "):
        """
        Return a nearly runnable script recreating this simulation.

        Needs some work to make the result truly runnable.

        Only scheduled commands that have not yet been executed are
        included, because executed commands are not kept around.
        """
        objs  = [o.script_repr(imports=imports) for o in
                 sorted(self.objects().values(), cmp=lambda x, y: cmp(x.name,y.name))]

        conns = [o.script_repr(imports=imports) for o in
                 sorted(self.connections(),      cmp=lambda x, y: cmp(x.name,y.name))]

        cmds  = [o.script_repr(imports=imports) for o in
                 sorted(sorted([e for e in self.events if isinstance(e,CommandEvent)],
                               cmp=lambda x, y: cmp(x.command_string,y.command_string)),
                        cmp=lambda x, y: cmp(x.time,y.time))]

        imps  = sorted(set(imports))

        vals  = [simulation_path + "." + p + "=" + repr(getattr(self,p)) for p in
                 ["name","startup_commands","execute_next"]
                 if getattr(self,p)]

        return "\n\n# Imports:\n\n"                +     '\n'.join(imps)  + \
               "\n\n\n"                            +   '\n\n'.join(vals)  + \
               '\n\n\n\n# Objects:\n\n'            + '\n\n\n'.join(objs)  + \
               '\n\n\n\n# Connections:\n\n'        + '\n\n\n'.join(conns) + \
               '\n\n\n\n# Scheduled commands:\n\n' +     '\n'.join(cmds)
    

    # Convenience function for use in graphical editors of the simulation
    def grid_layout(self,objgrid,xstart=100,xstep=150,ystart=100,ystep=150):
        """
        Set the layout_location of simulation objects in a grid pattern.
    
        Takes a list of lists of simulation objects, or names of
        simulation objects, and positions them with layout_locations
        left-to-right, top-to-bottom, starting at (xstart,ystart) and
        advancing by xstep and ystep.
    
        The object None can be placed in the grid to skip a grid space.
        """
        y = ystart
        for row in objgrid:
            x = xstart
            for obj in row:
                if obj:
                    if isinstance(obj,str):
                        self[obj].layout_location = x,y
                    else:
                        obj.layout_location = x,y
                x += xstep
            y += ystep


