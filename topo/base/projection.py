"""
Projection and related classes.

$Id$
"""
__version__='$Revision$'
import Numeric

from itertools import chain

from sheet import Sheet
from parameterclasses import Parameter, Number, BooleanParameter, ClassSelectorParameter
from simulator import EPConnection
from parameterizedobject import ParameterizedObject


class OutputFunction(ParameterizedObject):
    """
    Object to map a numeric item into another of the same size.

    Typically used for transforming an array of intermediate results
    into a final version.  For instance, when computing the output of
    a Sheet, one will often first compute a linear sum, then use a
    sigmoidal OutputFunction to transform that into the final result.

    Objects in this class must support being called as a function with
    one argument, typically a matrix, and return a matrix of the same
    size.  If implemented using Numeric functions, subclasses of this
    class should also work for scalars.  For matrix or other mutable
    objects, the argument x may be modified by the call to this function,
    and is not currently guaranteed to have the same value as the one
    returned by this function.
    """

    # CEBHACKALERT: can we have this here - is there a more appropriate
    # term for it, general to output functions?
    norm_value = Parameter(default=None)
    
    def __call__(self,x):
        raise NotImplementedError


# Trivial example of an OutputFunction, provided for when a default
# is needed.  The other concrete OutputFunction classes are stored
# in outputfns/, to be imported as needed.
class Identity(OutputFunction):
    """
    Identity function, returning its argument as-is.

    For speed, calling this function object is sometimes optimized
    away entirely.  To make this feasible, it is not allowable to
    derive other classes from this object, modify it to have different
    behavior, add side effects, or anything of that nature.
    """

    def __call__(self,x):
        return x


class OutputFunctionParameter(ClassSelectorParameter):
    """
    Parameter whose value can be any OutputFunction, i.e., a function mapping a 2D array
    to a 2D array.
    """
    __slots__ = []
    __doc__ = property((lambda self: self.doc))

    packages = []
    
    def __init__(self,default=Identity(),**params):
        super(OutputFunctionParameter,self).__init__(OutputFunction,default=default,**params)        


### JABALERT
###
### Need to provide a way to visualize the activity of a Projection,
### e.g. by putting it into the destination's SheetView database.
class Projection(EPConnection):
    """
    A projection from a Sheet into a ProjectionSheet.

    Projections are required to support the activate() method, which
    will construct a matrix the same size as the target
    ProjectionSheet, from an input matrix of activity from the source
    Sheet.  Other than that, a Projection may be of any type.
    """
    _abstract_class_name = "Projection"
    
    strength = Number(default=1.0)

    def __init__(self,**params):
        super(Projection,self).__init__(**params)
        self.activity = Numeric.array(self.dest.activity)

    def activate(self,input_activity):
        raise NotImplementedError

    
    def learn(self):
        """
        This function has to be re-implemented by sub-classes, if they wish
        to support learning.
        """
        pass


class ProjectionSheet(Sheet):
    """
    A Sheet whose activity is computed using Projections from other sheets.

    A standard ProjectionSheet expects its input to be generated from
    other Sheets. Upon receiving an input event, the ProjectionSheet
    interprets the event data to be (a copy of) an activity matrix
    from another sheet.  The ProjectionSheet provides a copy of this
    matrix to each Projection from that input Sheet, asking each one
    to compute their own activity in response.  The same occurs for
    any other pending input events.

    After all events have been processed for a given time, the
    ProjectionSheet computes its own activity matrix using its
    activate() method, which by default sums all its Projections'
    activity matrices and passes the result through a user-specified
    output_fn() before sending it out on the default output port.
    The activate() method can be overridden to sum some of the
    projections, multiply that by the sum of other projections, etc.,
    to model modulatory or other more complicated types of connections.

    The output_fn is a function s(A) that takes an activity matrix
    A and produces and identically shaped output matrix. The default
    is the identity function.
    """
    output_fn = OutputFunctionParameter(default=Identity(),
                                        doc='output function applied (optionally) to the ProjectionSheet activity.')
    apply_output_fn=BooleanParameter(default=True)
                             
    def __init__(self,**params):
        super(ProjectionSheet,self).__init__(**params)
	self.in_projections = {}
        self.new_input = False


    def _connect_from(self, conn, **args):
        """
        Accept a connection from src, on src_port, for dest_port.
        Contruct a dictionary of projections indexed by source name.
        Ensure that Projections to this ProjectionSheet are named differently,
        by raising an error if the user try to do so.
        """
        Sheet._connect_from(self, conn, **args)

        ### JCALERT! This could be better re-implemented: the structure of in_projections obliged to
        ### use the chain method in slef.projections. Maybe it would be possible to code it differently.
        if isinstance(conn, Projection):
            if conn.src.name not in self.in_projections:
                self.in_projections[conn.src.name] = []
            if conn.name in self.projections():
                raise ValueError('Two Projections to the same Sheet, have to be named differently')
            else:
                self.in_projections[conn.src.name].append(conn)
        else:
            raise TypeError('ProjectionSheets only accept Projections, not other types of connection.')


    def input_event(self,src,src_port,dest_port,data):
        """
        Accept input from some sheet.  Call .present_input() to
        compute the stimulation from that sheet.
        """
        #self.message("Received input from",src,"at time",self.simulator.time())
        self.present_input(data,src,dest_port)
        self.new_input = True


    def activate(self):
        """
        Collect activity from each projection, combine it to calculate
        the activity for this sheet, and send the result out.
        """
        self.activity *= 0.0
        for name in self.in_projections:
            for proj in self.in_projections[name]:
                self.activity+= proj.activity
        if self.apply_output_fn:
            self.activity = self.output_fn(self.activity)
        self.send_output(data=self.activity)


    def pre_sleep(self):
        """
        Called by the simulator after all the events are processed for the 
        current time but before time advances.  Allows the event processor
        to send any events that must be sent before time advances to drive
        the simulation. 
        """
        if self.new_input:
            self.activate()
            self.new_input = False
            if self.learning:
                self.learn()


    def learn(self):
        """
        Override this method to implement learning/adaptation.  Called
        from self.pre_sleep() _after_ activity has been propagated.
        """
        pass


    def present_input(self,input_activity,input_sheet,dest_port):
        """
        Provide the given input_activity to all projections from the
        given input_sheet, asking each one to compute its activity.
        The sheet's own activity is not calculated until activite()
        is called.
        """
        for proj in self.in_projections[input_sheet.name]:
            if proj.dest_port == dest_port:
                proj.activate(input_activity)


    def projections(self):
        """
        Return a dictionary {projection_name, projection} of all the in_projections
        for this Sheet.
        """
        return dict([(p.name,p) for p in chain(*self.in_projections.values())])




