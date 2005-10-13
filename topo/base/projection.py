"""
The Projection and ProjectionSheet classes.

$Id$
"""

import Numeric

from sheet import Sheet
from parameter import Parameter, Number
from simulator import EPConnection


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
    strength = Number(default=1.0)
    activity = []

    def __init__(self,**params):
        super(Projection,self).__init__(**params)
        self.activity = Numeric.array(self.dest.activity)

    def activate(self,input_activity,rows,cols):
        raise NotImplementedError



class ProjectionSheet(Sheet):
    """
    A Sheet whose activity is computed using projections from other sheets.

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
    transfer_fn() before sending it out on the default output port.
    The activate() method can be overridden to treat sum some of the
    connections, multiply that by the sum of other connections, etc.,
    to model modulatory or other more complicated types of connection
    influences.

    The transfer_fn is a function s(A) that takes an activity matrix
    A and produces and identically shaped output matrix. The default
    is the identity function.

    A ProjectionSheet connection from another sheet takes two parameters:

    projection_type: The type of projection to use for the connection.

    projection_params: A dictionary of keyword arguments for the
    projection constructor (defaulting to the empty dictionary {}).

    For instance, given a simulator sim, an input sheet s1 and a
    ProjectionSheet s2, one might connect them thus:

    sim.connect(s1,s2,projection_type=MyProjectionType,
                      projection_params=dict(a=1,b=2))

    s2 would then construct a new projection of type MyProjectionType
    with the parameters (a=1,b=2).
    """

    transfer_fn  = Parameter(default=lambda x:Numeric.array(x))
                             
    def __init__(self,**params):
        super(ProjectionSheet,self).__init__(**params)
        self.projections = {}
        self.new_input = False

    ### JABHACKALERT!
    ###
    ### What's the projections list for?  Isn't it redundant with
    ### the connections list?  Seems like that's a relic from
    ### back when projections were not a subclass of EPConnection.
    ### This implementation needs to be cleaned up and unified with
    ### the corresponding implementation in EventProcessor.
    def _connect_from(self, proj, **args):
        """
        Accept a connection from src, on src_port, for dest_port.
        Construct a new Projection of type projection_type using the
        parameters in projection_params.
        """
        
        Sheet._connect_from(self,proj,**args)
        if proj.src.name not in self.projections:
            self.projections[proj.src.name] = []
        self.projections[proj.src.name].append(proj)

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
        for name in self.projections:
            for proj in self.projections[name]:
                self.activity+= proj.activity
        self.activity = self.transfer_fn(self.activity)
        self.send_output(data=self.activity)

        if self._learning:
            self.learn()

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
        rows,cols = self.activity.shape

        for proj in self.projections[input_sheet.name]:
            if proj.dest_port == dest_port:
                proj.activate(input_activity,rows,cols)
		break

    def get_projection_by_name(self,tname):
        """
        More often than not, a Projection is requested by name from a
        sheet, rather than by the location in the projections list.
        This code hides the complex reverse addressing necessary.
        Always returns a list in case of multiple name hits, but the
        list may be empty if no projections have a name matching the
        one passed in as t(arget)name.
        """
        
        prjns = [p for name in self.projections
                       for p in self.projections[name]
                           if p.name == tname]
        return prjns




