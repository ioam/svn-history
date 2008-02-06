"""
Projection and related classes.

$Id$
"""
__version__='$Revision$'

from numpy import array,asarray,ones,sometrue, logical_and, logical_or

from sheet import Sheet
from parameterclasses import Number, BooleanParameter, Parameter, ListParameter
from parameterizedobject import ParameterizedObject
from simulation import EPConnection
from functionfamilies import OutputFnParameter,IdentityOF
from topo.misc.keyedlist import KeyedList


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

    # JPALERT: Is there anything about this class that assumes its sheet is a
    # ProjectionSheet?


    # JPALERT: Need this double indirection because Python property get/set
    # methods can't be overridden in subclasses(!).
    def __get_data(self): return self.get_data()
    def __set_data(self,data): self.set_data(data)
    data = property(__get_data,__set_data)
    
    def __get_sheet(self): return self.get_sheet()
    def __set_sheet(self,sheet): self.set_sheet(sheet)
    sheet = property(__get_sheet,__set_sheet)
    
    
    def __init__(self,sheet=None,**params):
        super(SheetMask,self).__init__(**params)
        self.sheet = sheet


    # Ensure that whenever somebody accesses the data they are not None
    def get_data(self): 
        assert(self._sheet != None)
        return self._data
    def set_data(self,data): 
        assert(self._sheet != None)
        self._data = data

    def get_sheet(self): 
        assert(self._sheet != None)
        return self._sheet
    def set_sheet(self,sheet): 
        self._sheet = sheet 
        if(self._sheet != None): self.reset()


    def __and__(self,mask):
        return AndMask(self._sheet,submasks=[self,mask])
    def __or__(self,mask):
        return OrMask(self._sheet,submasks=[self,mask])

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

  
class CompositeSheetMask(SheetMask):
    """
    A SheetMask that computes its value from other SheetMasks.    
    """
    __abstract =  True 

    submasks = ListParameter(class_=SheetMask)

    def __init__(self,sheet=None,**params):
        super(CompositeSheetMask,self).__init__(sheet,**params)
        assert self.submasks, "A composite mask must have at least one submask."

    def _combine_submasks(self):
        """
        A method that combines the submasks.

        Subclasses should override this method to do their respective
        composite calculations.  The result should be stored in self.data.
        """
        raise NotImplementedError
    
    def set_sheet(self,sheet):
        for m in self.submasks:
            m.sheet = sheet
        super(CompositeSheetMask,self).set_sheet(sheet)

    def reset(self):
        for m in self.submasks:
            m.reset()
        self._combine_submasks()
        
    def calculate(self):
        for m in self.submasks:
            m.calculate()
        self._combine_submasks()
            
    def update(self):
        for m in self.submasks:
            m.update()
        self._combine_submasks()



class AndMask(CompositeSheetMask):
    """
    A composite SheetMask that computes its value as the logical AND (i.e. intersection) of its sub-masks.
    """
    def _combine_submasks(self):
        self._data = asarray(reduce(logical_and,(m.data for m in self.submasks)),dtype=int)



class OrMask(CompositeSheetMask):
    """
    A composite SheetMask that computes its value as the logical OR (i.e. union) of its sub-masks.
    """
    def _combine_submasks(self):
        self._data = asarray(reduce(logical_or,(m.data for m in self.submasks)),dtype=int)

    
        
class Projection(EPConnection):
    """
    A projection from a Sheet into a ProjectionSheet.

    Projections are required to support the activate() method, which
    will construct a matrix the same size as the target
    ProjectionSheet, from an input matrix of activity from the source
    Sheet.  Other than that, a Projection may be of any type.
    """
    __abstract=True
    
    strength = Number(default=1.0)

    src_port = Parameter(default='Activity')
    
    dest_port = Parameter(default='Activity')

    output_fn  = OutputFnParameter(
        default=IdentityOF(),
        doc='Function applied to the Projection activity after it is computed.')

       
    def __init__(self,**params):
        super(Projection,self).__init__(**params)
        self.activity = array(self.dest.activity)
        self._updating_state = []
        
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

    def stop_updating(self):
        """
        Save the current state of the updating parameter to an internal stack.
        Calls the stop_updating function for the projection output_fn.
        Will need to be overwritten in subclasses that have a updating parameter,
        or some other potential state change which should be frozen.  
        """
        self.output_fn.stop_updating()
      

    def restore_updating(self):
        """
        Pop the most recently saved updating parameter off the stack.
        Calls the restore_updating function for the projection output_fn.
        Will need to be overwritten in subclasses that have a updating parameter
        or some other potential state change which should be frozen.
        """
        self.output_fn.restore_updating()
           

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
        self.verbose("Received input from " + str(conn.src.name) +
                     " on dest_port " + str(conn.dest_port) +
                     " via connection " + conn.name + ".")
        self.present_input(data,conn)
        self.new_input = True


    def _port_match(self,key,portlist):
        """
        Returns True if the given key matches any port on the given list.

        A port is considered a match if the port is == to the key,
        or if the port is a tuple whose first element is == to the key,
        or if both the key and the port are tuples whose first elements are ==.

        This approach allows connections to be grouped using tuples.
        """
        port=portlist[0]
        return [port for port in portlist
                if (port == key or
                    (isinstance(key,tuple)  and key[0] == port) or
                    (isinstance(port,tuple) and port[0] == key) or
                    (isinstance(key,tuple)  and isinstance(port,tuple) and port[0] == key[0]))]


    def _grouped_in_projections(self,ptype):
        """
        Return a dictionary of lists of incoming Projections, grouped for type.
        Each projection of type <ptype> is grouped according to the name of the port into a single list 
        within the dictionary.

        The entry None will contain those that are not of type <ptype>, while the other entries will contain a list of
        Projections, each of which has type ptype.
        
        Example: to obtain the lists of projection that should be together joint normalised you call
        __grouped_in_projection('JointNormalize')
        """
        in_proj = KeyedList()
        in_proj[None]=[] # Independent (ungrouped) connections
        
        for c in self.in_connections:
            d = c.dest_port
            if not isinstance(c,Projection):
                self.debug("Skipping non-Projection "+c.name)
            elif isinstance(d,tuple) and len(d)>2 and d[1]==ptype:
                if in_proj.get(d[2]):
                    in_proj[d[2]].append(c)
                else:
                    in_proj[d[2]]=[c]
            #elif isinstance(d,tuple):
            #    raise ValueError("Unable to determine appropriate action for dest_port: %s (connection %s)." % (d,c.name))
            else:
                in_proj[None].append(c)
                    
        return in_proj


    def activate(self):
        """
        Collect activity from each projection, combine it to calculate
        the activity for this sheet, and send the result out.  Subclasses
        may override this method to whatever it means to calculate activity
        in that subclass.
        """
        self.activity *= 0.0
        div = self.activity *0.0
        mul = self.activity *0.0

        for proj in self.in_connections:
            d = proj.dest_port
            if not isinstance(proj,Projection):
                self.debug("Skipping non-Projection "+proj.name)
            elif isinstance(d,tuple) and len(d)>1 and d[1]=='Divisive':
                div += proj.activity
            elif isinstance(d,tuple) and len(d)>1 and d[1]=='Multiplicative':
                mul += proj.activity
            else:
                self.activity += proj.activity

        #print div[60,60]
        #print self.activity[60,60]
        self.activity /= (1.0 + div)
        #print self.activity[60,60]
        self.activity *= (1.0 + mul)

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
                self.debug("Skipping non-Projection "+proj.name)
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
        conn.activate(input_activity)


    def projections(self,name=None):
        """
        
        Return either a named input p, or a dictionary
        {projection_name, projection} of all the in_connections for
        this ProjectionSheet.

        A minor convenience function for finding projections by name;
        the sheet's list of in_connections usually provides simpler
        access to the Projections.
        """
        if not name:
            return dict([(p.name,p) for p in self.in_connections])
        else:
            for c in self.in_connections:
                if c.name == name:
                    return c
            raise KeyError(name)


    def stop_updating(self):
        """
        Save the current state of the learning parameter to an internal stack.
        Turns off the updating and calls the stop_updating function for each
        projection and for the sheet output function.
        """

        self._updating_state.append(self.learning)
        self.learning=False
        self.output_fn.stop_updating()
        for proj in self.in_connections:
            if not isinstance(proj,Projection):
                self.debug("Skipping non-Projection "+proj.name)
            else:
                proj.stop_updating()


    def restore_updating(self):
        """
        Pop the most recently saved learning parameter off the stack.
        Calls the restore_updating function for each projection and for
        the sheet output function.
        """

        self.learning = self._updating_state.pop()
        self.output_fn.restore_updating()
        for proj in self.in_connections:
            if not isinstance(proj,Projection):
                self.debug("Skipping non-Projection "+proj.name)
            else:
                proj.restore_updating()
        
    

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
