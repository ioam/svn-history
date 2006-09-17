"""
The LISSOM and JointNormalizingCFSheet classes.

$Id$
"""
__version__='$Revision$'

import Numeric

import topo

from topo.base.cf import CFSheet
from topo.base.parameterclasses import BooleanParameter, Number, Integer
from topo.base.projection import OutputFnParameter, Projection
from topo.base.parameterizedobject import ParameterizedObject
from topo.base.sheet import activity_type
from topo.misc.inlinec import optimized
from topo.misc.keyedlist import KeyedList
from topo.outputfns.basic import PiecewiseLinear


class JointNormalizingCFSheet(CFSheet):
    """
    A type of CFSheet extended to support joint sum-based normalization.

    For L1 normalization, joint normalization means normalizing the
    sum of (the absolute values of) all weights in a set of
    corresponding CFs in different Projections, rather than only
    considering weights in the same CF.

    This class makes it possible for a model to use joint
    normalization, by providing a mechanism for grouping Projections
    (see _port_match), plus a learn() function that computes the joint
    sums.  Joint normalization also requires having ConnectionField
    store and return a norm_total for each neuron, and having an
    OutputFn that will respect this norm_total rather than the strict
    total of the ConnectionField's weights.  At present,
    CFPOF_DivisiveNormalizeL1 and CFPOF_DivisiveNormalizeL1_opt do use
    norm_total; others can be extended to do something similar if
    necessary.

    To enable joint normalization, you can declare that all the
    incoming connections that should be normalized together each
    have a dest_port of:

    dest_port=('Activity','JointNormalize', 'AfferentGroup1'),

    Then all those that have this dest_port will be normalized
    together, as long as an appropriate OutputFn is being used.
    """

    # JABALERT: Should check that whenever a connection is added to a
    # group, it has the same no of cfs as the existing connections.


    def start(self):
        # Force the weights to be normalized at the start of the simulation
        # JABALERT: There may be some cleaner way to achieve this.
        assert self.simulation
        self.simulation.schedule_command(topo.sim.time(),
                                         'topo.sim["' + self.name + '"]._normalize_weights()')


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

    def __grouped_in_projections(self):
        """
        Return a dictionary of lists of incoming Projections, grouped for normalization.

        The entry None will contain those to be normalized
        independently, while the other entries will contain a list of
        Projections, each of which should be normalized together.
        """
        in_proj = KeyedList()
        in_proj[None]=[] # Independent (ungrouped) connections
        
        for c in self.in_connections:
            d = c.dest_port
            if not isinstance(c,Projection):
                self.debug("Skipping non-Projection "+c.name)
            elif isinstance(d,tuple) and len(d)>2 and d[1]=='JointNormalize':
                if in_proj.get(d[2]):
                    in_proj[d[2]].append(c)
                else:
                    in_proj[d[2]]=[c]
            elif isinstance(d,tuple):
                raise ValueError("Unable to determine appropriate action for dest_port: %s (connection %s)." % (d,c.name))
            else:
                in_proj[None].append(c)
                    
        return in_proj

                        
    def __compute_joint_norm_totals(self,projlist):
        """Compute norm_total for each CF in each projections from a group to be normalized jointly."""

        # Assumes that all Projections in the list have the same r,c size
        assert len(projlist)>=1
        proj  = projlist[0]
        rows,cols = len(proj.cfs),len(proj.cfs[0])

        for r in range(rows):
            for c in range(cols):
                sums = [p.cfs[r][c].norm_total for p in projlist]
                joint_sum = Numeric.add.reduce(sums)
                for p in projlist:
                    p.cfs[r][c].norm_total=joint_sum


    def _normalize_weights(self):
        """Apply the weights_output_fn for every group of Projections."""
        
        for key,projlist in self.__grouped_in_projections():
            if key == None:
                normtype='Independent'
            else:
                normtype='Joint'
                self.__compute_joint_norm_totals(projlist)

            self.debug("Time " + str(self.simulation.time()) + ": " + normtype +
                       "ly normalizing:")

            for p in projlist:
                p.apply_learn_output_fn(Numeric.ones(self.shape,activity_type))
                self.debug('  ',p.name)


    def learn(self):
        """
        Call the learn() method on every Projection to the Sheet, and
        call the output functions (jointly if necessary).
        """
        # Ask all projections to learn independently
        for proj in self.in_connections:
            if not isinstance(proj,Projection):
                self.debug("Skipping non-Projection "+proj.name)
            else:
                proj.learn()

        # Apply output function in groups determined by dest_port
        self._normalize_weights()

        

class LISSOM(JointNormalizingCFSheet):
    """
    A Sheet class implementing the LISSOM algorithm
    (Sirosh and Miikkulainen, Biological Cybernetics 71:66-78, 1994).

    A LISSOM sheet is a JointNormalizingCFSheet slightly modified to
    enforce a fixed number of settling steps.  Settling is controlled
    by the tsettle parameter; once that number of settling steps has
    been reached, an external input is required before the sheet will
    activate again.
    """

    tsettle=Integer(default=8,bounds=(0,None),doc="""
       Number of times to activate the LISSOM sheet for each external input event.
       
       A counter is incremented each time an input is received from any
       source, and once the counter reaches tsettle, the last activation
       step is skipped so that there will not be any further recurrent
       activation.  The next external (i.e., afferent or feedback)
       event will then start the counter over again.""")

    continuous_learning = BooleanParameter(default=False, doc="""
       Whether to modify the weights after every settling step.
       If false, waits until settling is completed before doing learning.""")

    output_fn = OutputFnParameter(default=PiecewiseLinear(lower_bound=0.1,upper_bound=0.65))
    precedence = Number(0.6)
    
    def __init__(self,**params):
        super(LISSOM,self).__init__(**params)
        self.__counter_stack=[]
        self.activation_count = 0
        self.new_iteration = True

    def input_event(self,conn,data):
        # On a new afferent input, clear the activity
        if self.new_iteration:
            self.new_iteration = False
            self.activity *= 0.0
            for proj in self.in_connections:
                proj.activity *= 0.0
                    
        super(LISSOM,self).input_event(conn,data)


    ### JABALERT!  There should be some sort of warning when
    ### tsettle times the input delay is larger than the input period.
    ### Right now it seems to do strange things in that case (settle
    ### at all after the first iteration?), but of course that is
    ### arguably an error condition anyway (and should thus be
    ### flagged).
    def process_current_time(self):
        """
        Pass the accumulated stimulation through self.output_fn and
        send it out on the default output port.
        """
        if self.new_input:
            self.new_input = False
    	    if self.activation_count == self.tsettle:
                # Once we have been activated the required number of times
                # (determined by tsettle), reset various counters, learn
                # if appropriate, and avoid further activation until an
                # external event arrives.
                self.activation_count = 0
                self.new_iteration = True # used by input_event when it is called
                if (self.learning and not self.continuous_learning):
                    self.learn()
            else:
                self.activate()
                self.activation_count += 1
                if (self.learning and self.continuous_learning):
                   self.learn()
                   

    # print the weights of a unit
    def printwts(self,x,y):
        for proj in self.in_connections:
            print proj.name, x, y
            print proj.cfs[x][y].weights


    def state_push(self,**args):
        super(LISSOM,self).state_push(**args)
        self.__counter_stack.append((self.activation_count,self.new_iteration))


    def state_pop(self,**args):
        super(LISSOM,self).state_pop(**args)
        self.activation_count,self.new_iteration=self.__counter_stack.pop()
  

