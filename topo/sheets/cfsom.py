"""
Defines CFSOM, a sheet class that works like a Kohonen SOM extended to
support topographically restricted receptive fields.

$Id$
"""
__version__='$Revision$'

from numpy.oldnumeric import argmax,exp,floor

from topo.base.arrayutils import L2norm
from topo.base.parameterclasses import Number
from topo.base.cf import CFSheet
from topo.learningfns.som import CFPLF_SOM

### JABHACKALERT: The SOM support needs complete reworking to fit with
### the rest of Topographica.  Here is the current plan, as of 3/2007:
# 
# 1. Remove alpha(), radius(), decay(), and learning_length from the
#    CFSOM class, and make new Dynamic parameters instead.  One such
#    class can handle both alpha() and radius() right now.  We'll have
#    to figure out where to put these new classes, because unlike
#    existing Parameter classes, these depend on topo.sim.time(), so
#    they can't go into topo/base/parameterclasses.py.
# 
#    It may be best for these types to take an arbitrary function as
#    their timebase.  That way SOM users could implement batch training
#    by having a special "batch generator" that produces its own
#    timebase for parameter annealing. (i.e. the batch number)  
# 
#    Also remove the special learn() function, which exists only because
#    the current handling of these parameters is at the wrong level (the
#    Sheet, while the values are used at the Projection level).  The
#    CFSOM class will then become empty, and an ordinary CFSheet can be
#    used for SOMs instead.
# 
# 2. Do the same for the variants of these functions in RetinotopicSOM
#    in examples/som_retinotopy.ty and ObermayerSOM in
#    examples/obermayer_pnas90.ty, and then eliminate both of these
#    classes as well.
# 
# 3. Change the output_fn for SOM models to be KernelMax.
# 
# 4. Remove the neighborhood function handling from CFPLF_HebbianSOM,
#    and instead learn based on the already-placed version in the
#    Sheet's activity matrix.  This should be much simpler, but it will
#    slow things down relative to the current implementation, because it
#    will mean that all units will learn, rather than just those within
#    a fixed distance from the winner.  So we will need to implement
#    some sort of optimization so that we ignore units whose activation
#    is zero.  (Which is an optimization that should be useful for
#    nearly all algorithms, right?  Of course, it should still be off by
#    default, just for safety.)
# 
# 5. Although it is not needed for any current model, we can add a new
#    SOM Sheet class that provides output in a form needed as input for
#    another SOM.  The activity matrix described above is one obvious
#    choice, but others include the coordinates of the winning unit (in
#    Sheet coordinates, or in the range 0.0,1.0), or the weight vector
#    of the winning unit, or a copy of the Activity matrix with all
#    units set to zero except the winner (one-hot).  All but one-hot can
#    probably be implemented most naturally as a Sheet class that sends
#    messages out on different ports than Activity, although that might
#    make things more difficult for subsequent sheets to process.  I'm
#    not sure how to handle a one-hot approach -- in that case the
#    output is indeed interpretable as an activity pattern, yet it's not
#    the right one for driving learning, so it's not clear how to
#    implement it.  In any case, none of these options need to be done
#    soon, but I do want to have them sketched out somewhere, so that
#    anyone who needs to do something like this will see the right way
#    to do it.  





class CFSOM(CFSheet):
    """
    Kohonen Self-Organizing Map algorithm extended to support ConnectionFields.

    This is an implementation of the Kohonen SOM algorithm extended to
    support ConnectionFields, i.e., different spatially restricted
    input regions for different units.  With fully connected input
    regions, it should be usable as a regular SOM as well.

    Most of the real work is done by the Projection, and specifically
    by the Projection's learning_fn.  The learning_fn will typically
    be a subclass of CFPLF_SOM, and will typically select a winning unit
    and modify weights according to a neighborhood function around the
    winner.  Other Projection types can also be used.
    """
    alpha_0 = Number(0.5, doc="Initial value of the learning rate.")
    radius_0 = Number(1.0, doc="Initial value of the neighborhood radius.")
    precedence = Number(0.6)
    learning_length = Number(1000, doc="Number of input presentations to use, by default.")
    
    def __init__(self,**params):
        super(CFSOM,self).__init__(**params)
        self.half_life = self.learning_length/8

    def decay(self, time, half_life):
        """Exponential decay."""
        return 0.5**(time/float(half_life))

    ### JCALERT! For the moment, som_retinotopy uses a super-class of
    ### CFSOM in order to override the decay (and alpha) functions. It
    ### would be good to make them Parameters here, so that we can
    ### delete that there and in obermayer, yet still override the
    ### decay and alpha function.
    def alpha(self):
        """Return the learning rate at a specified simulation time, using exponential falloff."""
        return self.alpha_0 * self.decay(float(self.simulation.time()),self.half_life)

    def radius(self):
        """Return the radius at a specified simulation time, using exponential falloff."""
        return self.radius_0 * self.decay(float(self.simulation.time()),self.half_life)

    def learn(self):
        """
        Call the learn() method on every CFProjection to the Sheet.
        """
        rows,cols = self.activity.shape
        radius = self.radius() * self.xdensity
        for proj in self.in_connections:
            proj.learning_rate = self.alpha()
            if isinstance(proj.learning_fn, CFPLF_SOM):
                proj.learning_fn.learning_radius = radius
            proj.learn()


