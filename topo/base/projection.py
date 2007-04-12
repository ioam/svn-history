"""
Projection and related classes.

$Id$
"""
__version__='$Revision$'

import numpy.oldnumeric as Numeric

from sheet import Sheet
from parameterclasses import Number, BooleanParameter, Parameter
from parameterizedobject import ParameterizedObject
from simulation import EPConnection
from functionfamilies import OutputFnParameter,IdentityOF
from numpy import ones,sometrue


class SheetMask(ParameterizedObject):
    """
    An abstract class that defines a mask over a ProjectionSheet object.
    
    This class is typically used for optimization, where mask
    indicates which neurons are active and should be processed
    further. A mask can also be used for lesion experiments, to
    specify which units should be kept inactive.

    See the code for CFProjection and CFResponseFn to see how this
    class can be used to restrict the computation to only those
    neurons that the Mask lists as active.
    """
    # Ensure that whenever somebody accesses the data they are not None
    def get_data(self): 
        assert(self._sheet != None)
        return self._data
    def set_data(self,data): 
        assert(self._sheet != None)
        self._data = data
    data = property(get_data,set_data)
    
    
    def get_sheet(self): 
        assert(self._sheet != None)
        return self._sheet
    def set_sheet(self,sheet): 
        self._sheet = sheet 
        if(self._sheet != None): self.reset()
    sheet = property(get_sheet,set_sheet)
    
    
    def __init__(self,sheet=None,**params):
        super(SheetMask,self).__init__(**params)
        self.sheet = sheet
        

    # JABALERT: Shouldn't this just keep one matrix around and zero it out,
    # instead of allocating a new one each time?
    def reset(self):
      """Initialize mask to default value (with no neurons masked out)."""
      self.data = ones(self.sheet.shape)


    def calculate(self):
      """
      Calculate a new mask based on the activity of the sheet.

      For instance, in an algorithm like LISSOM that is based on a
      process of feedforward activation followed by lateral settling,
      the calculation is done at the beginning of each iteration after
      the feedforward activity has been calculated.

      Subclasses should override this method to compute some non-default
      mask.
      """
      pass
      

    # JABALERT: Not clear what the user should do with this.
    def update(self):
      """
      Update the current mask based on the current activity and a previous mask.

      Should be called only if calculate() has already been called since the last
      reset(); potentially faster to compute than redoing the entire calculate().
      
      Subclasses should override this method to compute some non-default
      mask.
      """
      pass



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

    # Should be a MaskParameter for safety
    #mask = ClassSelectorParameter(SheetMask,default=SheetMask(),instantiate=True,doc="""
    mask = Parameter(default=SheetMask(),instantiate=True,doc="""
        SheetMask object for computing which units need to be computed further.
        The object should be an instance of SheetMask, and will
        compute which neurons will be considered active for the
        purposes of further processing.  The default mask effectively
        disables all masking, but subclasses can use this mask to
        implement optimizations, non-rectangular Sheet shapes,
        lesions, etc.""")
                             
    def __init__(self,**params):
        super(ProjectionSheet,self).__init__(**params)
        self.new_input = False
        self.mask.sheet = self

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


  
    
    
class NeighborhoodMask(SheetMask):
    """
    A SheetMask where the mask includes a neighborhood around active neurons.

    Given a radius and a threshold, considers a neuron active if at
    least one neuron in the radius is over the threshold.
    """

    threshold = Number(default=0.00001,bounds=(0,None),doc="""
       Threshold for considering a neuron active.
       This value should be small to avoid discarding significantly active
       neurons.""")

    radius = Number(default=0.05,bounds=(0,None),doc="""
       Radius in Sheet coordinates around active neurons to consider
       neighbors active as well.  Using a larger radius ensures that
       the calculation will be unaffected by the mask, but it will
       reduce any computational benefit from the mask.""")

    
    def __init__(self,sheet,**params):
        super(NeighborhoodMask,self).__init__(sheet,**params)


    def calculate(self):
        rows,cols = self.data.shape
        
        # JAHACKALERT: Not sure whether this is OK. Another way to do
        # this would be to ask for the sheet coordinates of each unit
        # inside the loop.

        # transforms the sheet bounds with bounds2slice() and then
        # uses this to cut out the activity window
        ignore1,matradius = self.sheet.sheet2matrixidx(self.radius,0)
        ignore2,x = self.sheet.sheet2matrixidx(0,0)
        matradius = abs(matradius-x)
        for r in xrange(rows):
            for c in xrange(cols):
                rr = max(0,r-matradius)
                cc = max(0,c-matradius)
                neighbourhood = self.sheet.activity[rr:r+matradius+1,cc:c+matradius+1].ravel()
                self.data[r][c] = sometrue(neighbourhood>self.threshold)
