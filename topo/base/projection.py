"""
Projection and related classes.

$Id$
"""
__version__='$Revision$'

import numpy.oldnumeric as Numeric

from sheet import Sheet
from parameterclasses import Number, BooleanParameter, Parameter
from simulation import EPConnection
from functionfamilies import OutputFnParameter,IdentityOF

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

    src_port = Parameter(default='Activity')
    
    dest_port = Parameter(default='Activity')


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

    def apply_learn_output_fn(self,mask):
        """
        Sub-classes can implement this function if they wish to
        perform an operation after learning has completed, such as
        normalizing weight values across different projections.

        The mask argument determines which units should have their
        output_fn applied; units that are nonzero in the mask must
        have the function applied, while those that are zero may or
        may not have the function applied (depending on various
        optimizations).
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
    A and produces an identically shaped output matrix. The default
    is the identity function.
    """

    src_ports=['Activity']
    
    dest_ports=['Activity']
    
    output_fn = OutputFnParameter(
        default=IdentityOF(),
        doc="Output function to apply (if apply_output_fn is true) to this Sheet's activity.")
    
    apply_output_fn=BooleanParameter(default=True,
        doc="Whether to apply the output_fn after computing an Activity matrix.")

                             
    def __init__(self,**params):
        super(ProjectionSheet,self).__init__(**params)
        self.new_input = False


    def _dest_connect(self, conn):
        """
        See EventProcessor's _dest_connect(); raises an error if conn is not
        a Projection.  Subclasses of ProjectionSheet that know how to handle
        other types of Connections should override this method.
        """
        if isinstance(conn, Projection):
            super(ProjectionSheet,self)._dest_connect(conn)
        else:
            raise TypeError('ProjectionSheets only accept Projections, not other types of connection.')


    def input_event(self,conn,data):
        """
        Accept input from some sheet.  Call .present_input() to
        compute the stimulation from that sheet.
        """
        self.verbose("Time " + str(self.simulation.time()) + ":" +
                     " Received input from " + str(conn.src.name) +
                     " on dest_port " + str(conn.dest_port) +
                     " via connection " + conn.name + ".")
        self.present_input(data,conn)
        self.new_input = True


    def activate(self):
        """
        Collect activity from each projection, combine it to calculate
        the activity for this sheet, and send the result out.  Subclasses
        may override this method to whatever it means to calculate activity
        in that subclass.
        """
        self.activity *= 0.0

        for proj in self.in_connections:
            self.activity += proj.activity

        if self.apply_output_fn:
            self.output_fn(self.activity)

        self.send_output(src_port='Activity',data=self.activity)


    def process_current_time(self):
        """
        Called by the simulation after all the events are processed for the 
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
        By default, call the learn() and apply_learn_output_fn()
        methods on every Projection to this Sheet.
        
        Any other type of learning can be implemented by overriding this method.
        Called from self.process_current_time() _after_ activity has
        been propagated.
        """
        for proj in self.in_connections:
            if not isinstance(proj,Projection):
                topo.sim.debug("Skipping non-Projection "+proj.name)
            else:
                proj.learn()
                proj.apply_learn_output_fn(self.activity)


    def present_input(self,input_activity,conn):
        """
        Provide the given input_activity to each in_projection that has a dest_port
        equal to the specified port, asking each one to compute its activity.
        
        The sheet's own activity is not calculated until activate()
        is called.
        """
        # CEBALERT: can remove assert statement.
        assert isinstance(conn,Projection), type(conn)
        conn.activate(input_activity)
        
    # CEBALERT: check if we still need this now that in_connections
    # is a list. We should be able to delete it.
    def projections(self):
        """
        Return a dictionary {projection_name, projection} of all the in_connections
        for this Sheet.
        """
        return dict([(p.name,p) for p in self.in_connections])

