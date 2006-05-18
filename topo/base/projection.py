"""
Projection and related classes.

$Id$
"""
__version__='$Revision$'

import Numeric

from sheet import Sheet
from parameterclasses import Number, BooleanParameter
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
    output_fn = OutputFnParameter(
        default=IdentityOF(),
        doc='Output function applied (optionally) to the ProjectionSheet activity.')
    
    apply_output_fn=BooleanParameter(default=True)

                             
    def __init__(self,**params):
        super(ProjectionSheet,self).__init__(**params)
        self.new_input = False


    def _connect_from(self, conn):
        """
        See EventProcessor's _connect_from(); raises an error if conn is not
        a Projection.  Subclasses of ProjectionSheet that know how to handle
        other types of Connections should override this method.
        """
        if isinstance(conn, Projection):
            super(ProjectionSheet,self)._connect_from(conn)
        else:
            raise TypeError('ProjectionSheets only accept Projections, not other types of connection.')


    def input_event(self,conn,data):
        """
        Accept input from some sheet.  Call .present_input() to
        compute the stimulation from that sheet.
        """
        #self.message("Received input from",src,"at time",self.simulation.time())
        self.present_input(data,conn)
        self.new_input = True


    def activate(self):
        """
        Collect activity from each projection, combine it to calculate
        the activity for this sheet, and send the result out.
        """
        self.activity *= 0.0

        for proj in self.in_connections:
            self.activity+= proj.activity

        if self.apply_output_fn:
            self.activity = self.output_fn(self.activity)

        self.send_output(data=self.activity)


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
        Override this method to implement learning/adaptation.  Called
        from self.process_current_time() _after_ activity has been propagated.
        """
        pass


    def present_input(self,input_activity,conn):
        """
        Provide the given input_activity to each in_projection that has a dest_port
        equal to the specified port, asking each one to compute its activity.
        
        The sheet's own activity is not calculated until activate()
        is called.
        """
        # CEBHACKALERT: can remove assert statement.
        assert isinstance(conn,Projection), type(conn)
        conn.activate(input_activity)
        
    # CEBHACKALERT: check if we still need this now that in_connections
    # is a list. We should be able to delete it.
    def projections(self):
        """
        Return a dictionary {projection_name, projection} of all the in_connections
        for this Sheet.
        """
        return dict([(p.name,p) for p in self.in_connections])

