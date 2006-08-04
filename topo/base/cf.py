"""
ConnectionField and associated classes.

This module defines some basic classes of objects used to create
simulations of cortical sheets that take input through connection
fields that project from other cortical sheets (or laterally from
themselves).

ConnectionField: Holds a single connection field within a CFProjection.

CFProjection: A set of ConnectionFields mapping from a Sheet into a
ProjectionSheet.

CFSheet: A subclass of ProjectionSheet that provides an interface to
the underlying ConnectionFields in any projection of type CFProjection.

$Id$
"""

__version__ = '$Revision$'


# CEBHACKALERT: some things that need to be cleaned up...
#
# - CFProjection sometimes passes copies of objects to the CFs its
# creating, sometimes it doesn't. Some of ConnectionField's methods
# change their arguments, some don't.  Could lead to confusion and
# some hard-to-track bugs. (Same applies to SharedWeightCFProjection.)
#
# - The Slice object, then what a CF stores as a slice can finally be
# cleaned up.




import Numeric
import copy

import topo

import patterngenerator
from patterngenerator import PatternGeneratorParameter
from parameterizedobject import ParameterizedObject
from functionfamilies import OutputFnParameter,IdentityOF,LearningFnParameter,Hebbian,ResponseFnParameter,DotProduct,IdentityLF
from projection import Projection,ProjectionSheet
from parameterclasses import Parameter,Number,BooleanParameter,ClassSelectorParameter,Integer
from sheet import Sheet,Slice
from sheetview import UnitView, ProjectionView
from boundingregion import BoundingBox,BoundingRegionParameter

# JABALERT: Need to move KeyedList to base if we keep this
from topo.misc.keyedlist import KeyedList

# Specified explicitly when creating weights matrix - required
# for optimized C functions.
weight_type = Numeric.Float32


class ConnectionField(ParameterizedObject):
    """
    A set of weights on one input Sheet.

    Each ConnectionField contributes to the activity of one unit on
    the output sheet, and is normally used as part of a Projection
    including many other ConnectionFields.
    """
    
    x = Number(default=0.0,softbounds=(-1.0,1.0),
               doc='The x coordinate of the location of the center of this ConnectionField\non the input Sheet, e.g. for use when determining where the weight matrix\nlines up with the input Sheet matrix.')
    y = Number(default=0.0,softbounds=(-1.0,1.0),
               doc='The y coordinate of the location of the center of this ConnectionField\non the input Sheet, e.g. for use when determining where the weight matrix\nlines up with the input Sheet matrix.')


    # Weights matrix; not yet initialized.
    weights = []

    # Specifies how to get a submatrix from the source sheet that is aligned
    # properly with this weight matrix.  The information is stored as an
    # array for speed of access from optimized C components.
    # CEBHACKALERT: can rename this to 'slice_' now.
    slice_array = []

    # JABHACKALERT: The handling of _sum needs to be revisited, because
    # it is unlikely to work for arbitrary combinations of output and
    # learning functions.  E.g. the norm_value is sometimes treated as if
    # it is always the sum, when it may be the length instead.
    def get_sum(self):
        """
        As an optimization, a learning function (or other function
        that alters the cf's weights) may compute the sum
        of the cf's weights and cache it in the sum attribute (which
        really puts the value in _sum).

        If this has been done, the cached value is returned. Otherwise,
        the value is calculated when requested.

        This also allows e.g. joint normalization, because the cf's
        sum attribute can be set explicitly to the joint sum.
        """
        if hasattr(self,'__sum'):
            return self.__sum
        else:
            return Numeric.sum(self.weights.flat)
            
    def set_sum(self,new_sum):
        """
        Once set to a value, that cached value will be used until the
        sum is deleted.  Thus if any object sets this value, any other
        object that changes the value should either delete the cached
        sum or update it to the correct value.  Otherwise, there is a
        possibility that a stale cached value will be returned.
        """        
        self.__sum = new_sum

    def del_sum(self):
        """
        Delete any cached sum that may exist.
        """
        if hasattr(self,'__sum'): delattr(self,'__sum')



    # CEBHACKALERT: Accessing sum as a property from the C code will probably
    # slow it down; this should be checked.
    sum = property(get_sum,set_sum,del_sum,"Please see get_sum() and set_sum().")


    # CEBHACKALERT: add some default values
    def __init__(self,x,y,input_sheet,bounds_template,
                 weights_generator,mask_template,
                 output_fn=IdentityOF(),slice_=None,**params):
        """
        bounds_template is assumed to have been initialized correctly
        already (see e.g. CFProjection.initialize_bounds() ).
        """
        # CEBHACKALERT: maybe an external function is required? We need to
        # have correctly setup bounds here, in change_bounds(), and in other
        # places such as CFProjection (where the mask is made). At the moment,
        # the function is in CFProjection.

        super(ConnectionField,self).__init__(**params)

        self.x = x; self.y = y

        self.input_sheet = input_sheet
        self.offset_bounds(bounds_template,slice_)

        # CEBHACKALERT: might want to do something about a size that's specified.
        w = weights_generator(x=self.x,y=self.y,bounds=self.bounds,
                              xdensity=self.input_sheet.xdensity,
                              ydensity=self.input_sheet.ydensity)
        self.weights = w.astype(weight_type)
        # Maintain the original type throughout operations, i.e. do not
        # promote to double.
        self.weights.savespace(1)

        # Now we have to get the right submatrix of the mask (in case
        # it is near an edge)
        r1,r2,c1,c2 =  self.get_slice(bounds_template,slice_)
        m = mask_template[r1:r2,c1:c2]
        
        self.mask = m.astype(weight_type)
        self.mask.savespace(1)

        # CEBHACKALERT: this works for now, while the output_fns are
        # all multiplicative.  But in the long run we need a better
        # way to apply the mask.  The same applies anywhere the mask
        # is used, including in learningfns/.

        self.weights *= self.mask   
        output_fn(self.weights)        


    ### CEBHACKALERT: there is presumably a better way than this.
    def get_slice(self,bounds_template,slice_=None):
        """
        Return the correct slice for a weights/mask matrix at this
        ConnectionField's location on the sheet (i.e. for getting
        the correct submatrix of the weights or mask in case the
        unit is near the edge of the sheet).
        """
        if not slice_:
            slice_ = Slice(bounds_template,self.input_sheet)
            
        sheet_rows,sheet_cols = self.input_sheet.activity.shape

        # get size of weights matrix
        n_rows,n_cols = slice_.shape

        # get slice for the submatrix
        center_row,center_col = self.input_sheet.sheet2matrixidx(self.x,self.y)
        
        c1 = -min(0, center_col-n_cols/2)  # assume odd weight matrix so can use n_cols/2 
        r1 = -min(0, center_row-n_rows/2)  # for top and bottom
        c2 = -max(-n_cols, center_col-sheet_cols-n_cols/2)
        r2 = -max(-n_rows, center_row-sheet_rows-n_rows/2)
        return (r1,r2,c1,c2)
        

    # CEBHACKALERT: assumes the user wants the bounds to be centered
    # about the unit, which might not be true. Same HACKALERT as for
    # CFProjection.initialize_bounds()
    def offset_bounds(self,bounds,slice_=None):
        """
        Offset the given bounds to this cf's location and store the
        result in the 'bounds' attribute.

        Also stores the slice_array for access by C.
	"""
        if not slice_:
            slice_ = Slice(bounds,self.input_sheet)
        else:
            slice_ = copy.copy(slice_)
               
        # translate to this cf's location
        cf_row,cf_col = self.input_sheet.sheet2matrixidx(self.x,self.y)
        bounds_x,bounds_y=bounds.get_center()
        b_row,b_col=self.input_sheet.sheet2matrixidx(bounds_x,bounds_y)

        row_offset = cf_row-b_row
        col_offset = cf_col-b_col
        slice_.translate(row_offset,col_offset)


        slice_.crop_to_sheet()

        # weights matrix cannot have a zero-sized dimension (could
        # happen at this stage because of cropping)
        nrows,ncols = slice_.shape
        if nrows<1 or ncols<1:
            raise ValueError("ConnectionField at (%s,%s) (input_sheet=%s) has a zero-sized weights matrix (%s,%s); you may need to supply a larger bounds_template or increase the density of the sheet."%(self.x,self.y,self.input_sheet,nrows,ncols))


        self.bounds = slice_.bounds


        # Also, store the array for direct access by C.
        # Numeric.Int32 is specified explicitly here to avoid having it
        # default to Numeric.Int.  Numeric.Int works on 32-bit platforms,
        # but does not work properly with the optimized C activation and
        # learning functions on 64-bit machines.
        self.slice_array = Numeric.array(tuple(slice_),typecode=Numeric.Int32) 


    def get_input_matrix(self, activity):
        r1,r2,c1,c2 = self.slice_array
        return activity[r1:r2,c1:c2]


    def change_bounds(self, bounds_template, mask_template, output_fn=IdentityOF()):
        """
        Change the bounding box for this ConnectionField.

        bounds_template is assumed to have been initialized
        already (its equivalent slice made odd, and
        snapped to grid - as in __init__() ).
        
        Discards weights or adds new (zero) weights as necessary,
        preserving existing values where possible.

        Currently only supports reducing the size, not increasing, but
        should be extended to support increasing as well.
        """
        # CEBHACKALERT: re-write to allow arbitrary resizing
        or1,or2,oc1,oc2 = self.slice_array

        self.offset_bounds(bounds_template)
        r1,r2,c1,c2 = self.slice_array

        if not (r1 == or1 and r2 == or2 and c1 == oc1 and c2 == oc2):
            self.weights = Numeric.array(self.weights[r1-or1:r2-or1,c1-oc1:c2-oc1],copy=1)

            mr1,mr2,mc1,mc2 = self.get_slice(bounds_template)
            m = mask_template[mr1:mr2,mc1:mc2]
            self.mask = m.astype(weight_type)
            self.mask.savespace(1)

            # CEBHACKALERT: see __init__
            self.weights *= self.mask
            output_fn(self.weights)
            del self.sum


    def change_density(self, new_wt_density):
        """Rescale the weight matrix in place, interpolating or decimating as necessary."""
        raise NotImplementedError



class CFPResponseFn(ParameterizedObject):
    """
    Map an input activity matrix into an output matrix using the CFs
    in a CFProjection.

    Objects in this hierarchy of callable function objects compute a
    response matrix when given an input pattern and a set of
    ConnectionField objects.  Typically used as part of the activation
    function for a neuron, computing activation for one Projection.

    Objects in this class must support being called as a function with
    the arguments specified below, and must return a matrix the same
    size as the activity matrix supplied.
    """
    _abstract_class_name = "CFPResponseFn"

    def __call__(self, cfs, input_activity, activity, strength, **params):
        raise NotImplementedError



class CFPRF_Plugin(CFPResponseFn):
    """
    Generic large-scale response function based on a simple single-CF function.

    Applies the single_cf_fn to each CF in turn.  For the default
    single_cf_fn of DotProduct(), does a basic dot product of each CF with the
    corresponding slice of the input array.  This function is likely
    to be slow to run, but it is easy to extend with any arbitrary
    single-CF response function.

    The single_cf_fn must be a function f(X,W) that takes two
    identically shaped matrices X (the input) and W (the
    ConnectionField weights) and computes a scalar activation value
    based on those weights.
    """
    single_cf_fn = ResponseFnParameter(default=DotProduct(),
        doc="Accepts a ResponseFn that will be applied to each CF individually.")
    
    def __call__(self, cfs, input_activity, activity, strength):
        rows,cols = activity.shape

        single_cf_fn = self.single_cf_fn
        for r in xrange(rows):
            for c in xrange(cols):
                cf = cfs[r][c]
                r1,r2,c1,c2 = cf.slice_array
                X = input_activity[r1:r2,c1:c2]
                activity[r,c] = single_cf_fn(X,cf.weights)
        activity *= strength


class CFPResponseFnParameter(ClassSelectorParameter):
    """
    Parameter whose value can be any CFProjectionResponseFunction; i.e., a function
    that uses all the CFs of a CFProjection to transform the input activity
    into an output activity.
    """
    __slots__ = []
    __doc__ = property((lambda self: self.doc))

    def __init__(self,default=CFPRF_Plugin(),**params):
        super(CFPResponseFnParameter,self).__init__(CFPResponseFn,default=default,**params)        



class CFPLearningFn(ParameterizedObject):
    """
    Compute new CFs for a CFProjection based on input and output activity values.

    Objects in this hierarchy of callable function objects compute a
    new set of CFs when given input and output patterns and a set of
    ConnectionField objects.  Used for updating the weights of one
    CFProjection.

    Objects in this class must support being called as a function with
    the arguments specified below.
    """
    _abstract_class_name = "CFPLearningFn"
        
    def constant_sum_connection_rate(self,cfs,learning_rate):
	""" 
	Return the learning rate for a single connection assuming that
        the total rate is to be divided evenly among all the units in
        the connection field.
	"""      
        ### JCALERT! To check with Jim: right now, we take the number of units
        ### at the center of the matrix.  It would be better to calculate it
        ### directly from the sheet_density and bounds, but it is not currently
        ### possible to access those from here.  Example:
        #center_r,center_c = sheet2matrixidx(0,0,bounds,xdensity,ydensity)
	rows = len(cfs)
	cols = len(cfs[0])
	cf = cfs[rows/2][cols/2]
        # The number of units in the mask 
	nb_unit = len(Numeric.nonzero(Numeric.ravel(cf.mask)))
	constant_sum_connection_rate=learning_rate/float(nb_unit)
	return constant_sum_connection_rate

    def __call__(self, cfs, input_activity, output_activity, learning_rate, **params):
        raise NotImplementedError


class CFPLF_Identity(CFPLearningFn):
    """CFLearningFunction performing no learning."""
    single_cf_fn = LearningFnParameter(default=IdentityLF(),constant=True)
  
    def __call__(self, cfs, input_activity, output_activity, learning_rate, **params):
        pass


class CFPLearningFnParameter(ClassSelectorParameter):
    """
    Parameter whose value can be any CFPLearningFn; i.e., a function
    that uses all the CFs of a CFProjection to transform the input activity
    into an output activity.
    """
    __slots__ = []
    __doc__ = property((lambda self: self.doc))

    def __init__(self,default=CFPLF_Identity(),**params):
        super(CFPLearningFnParameter,self).__init__(CFPLearningFn,default=default,**params)        


class CFPLF_Plugin(CFPLearningFn):
    """CFPLearningFunction applying the specified single_cf_fn to each CF."""
    single_cf_fn = LearningFnParameter(default=Hebbian(),
        doc="Accepts a LearningFn that will be applied to each CF individually.")
       
    def __call__(self, cfs, input_activity, output_activity, learning_rate, **params):
        """Apply the specified single_cf_fn to every CF."""
        rows,cols = output_activity.shape
	single_connection_learning_rate = self.constant_sum_connection_rate(cfs,learning_rate)
        # avoid evaluating these references each time in the loop
        single_cf_fn = self.single_cf_fn
	for r in xrange(rows):
            for c in xrange(cols):
                cf = cfs[r][c]
                single_cf_fn(cf.get_input_matrix(input_activity),
                             output_activity[r,c], cf.weights, single_connection_learning_rate)
                # CEBHACKALERT: see ConnectionField.__init__()
                cf.weights *= cf.mask
                
class CFPOutputFn(ParameterizedObject):
    """
    Map the weight matrix of each CF in a CFProjection into a new one
    of the same shape.
    """
    _abstract_class_name = "CFPOutputFn"
    
    def __call__(self, cfs, output_activity,**params):
        raise NotImplementedError


class CFPOF_Plugin(CFPOutputFn):
    """Applies the specified single_cf_fn to each CF in the CFProjection."""
    single_cf_fn = OutputFnParameter(default=IdentityOF(),
        doc="Accepts an OutputFn that will be applied to each CF individually.")
    
    def __call__(self, cfs, output_activity, **params):
        """
        Apply the single_cf_fn to each CF.

        For each CF, the sum of the weights is passed
        as the current value of the norm. Following
        application of the output function, the cf's
        sum is then set equal to the single_cf_fn's
        norm_value. 
        """
        if type(self.single_cf_fn) is not IdentityOF:
            rows,cols = output_activity.shape
            single_cf_fn = self.single_cf_fn
            norm_value = self.single_cf_fn.norm_value                

            for r in xrange(rows):
                for c in xrange(cols):
                    cf = cfs[r][c]
                    single_cf_fn(cf.weights)
                    del cf.sum


class CFPOF_Identity(CFPOutputFn):
    """
    CFPOutputFn that leaves the CFs unchanged.

    Must never be changed or subclassed, because it might never
    be called. (I.e., it could simply be tested for and skipped.)
    """
    single_cf_fn = OutputFnParameter(default=IdentityOF(),constant=True)
    
    def __call__(self, cfs, output_activity, **params):
        pass



class CFPOutputFnParameter(ClassSelectorParameter):
    """
    Parameter whose value can be any CFOutputFn; i.e., a function
    that iterates through all the CFs of a CFProjection and applies
    an output_fn to each.
    """
    __slots__ = []
    __doc__ = property((lambda self: self.doc))

    def __init__(self,default=CFPOF_Plugin(),**params):
        super(CFPOutputFnParameter,self).__init__(CFPOutputFn,default=default,**params)        


                    
class CFProjection(Projection):
    """
    A projection composed of ConnectionFields from a Sheet into a ProjectionSheet.

    CFProjection computes its activity using a response_fn of type
    CFPResponseFn (typically a CF-aware version of mdot) and output_fn 
    (which is typically IdentityOF). Any subclass has to implement the interface
    activate(self,input_activity) that computes the response from the input 
    and stores it in the activity array.
    """
    response_fn = CFPResponseFnParameter(
        default=CFPRF_Plugin(),
        doc='Function for computing the Projection response to an input pattern.')
    
    cf_type = Parameter(default=ConnectionField,constant=True,
        doc="Type of ConnectionField to use when creating individual CFs.")
    
    nominal_bounds_template = BoundingRegionParameter(
        default=BoundingBox(radius=0.1),
        doc="""Bounds defining the Sheet area covered by a prototypical ConnectionField.
The true bounds will differ depending on the density (see initialize_bounds()).""")
    
    weights_generator = PatternGeneratorParameter(
        default=patterngenerator.Constant(),constant=True,
        doc="Generate initial weights values.")

    # JABALERT: Confusing name; change to cf_shape or cf_boundary_shape
    weights_shape = PatternGeneratorParameter(
        default=patterngenerator.Constant(),constant=True,
        doc="Define the shape of the connection fields.")
    
    learning_fn = CFPLearningFnParameter(
        default=CFPLF_Plugin(),
        doc='Function for computing changes to the weights based on one activation step.')

    # JABALERT: Shouldn't learning_rate be owned by the learning_fn?
    learning_rate = Number(default=0.0,softbounds=(0,100),
        doc="Amount of learning at each step for this projection, specified in units that are independent of the density of each Sheet.")
    
    output_fn  = OutputFnParameter(
        default=IdentityOF(),
        doc='Function applied to the Projection activity after it is computed.')

    weights_output_fn = CFPOutputFnParameter(
        default=CFPOF_Plugin(),
        doc='Function applied to each CF after learning.')

    strength = Number(default=1.0,doc="Global multiplicative scaling applied to the Activity of this Sheet.")

    min_matrix_radius = Integer(
        default=1,bounds=(0,None),
        doc="""
        Enforced minimum for radius of weights matrix.
        The default of 1 gives a minimum matrix of 3x3. 0 would
        allow a 1x1 matrix.
        """)

    def __init__(self,initialize_cfs=True,**params):
        """
        Initialize the Projection with a set of cf_type objects
        (typically ConnectionFields), each located at the location
        in the source sheet corresponding to the unit in the target
        sheet.

        The nominal_bounds_template specified may be altered. The bounds must
        be fit to the Sheet's matrix, and the weights matrix must
        have odd dimensions. These altered bounds are passed to the
        individual connection fields.

        A mask for the weights matrix is constructed. The shape is
        specified by weights_shape; the size defaults to the size
        of the nominal_bounds_template.
        """
        super(CFProjection,self).__init__(**params)

        # get the actual bounds_template by adjusting a copy of the
        # nominal_bounds_template to ensure an odd slice, and to be
        # cropped to sheet if necessary
        self.bounds_template = self.initialize_bounds(self.nominal_bounds_template)

        slice_ = Slice(self.bounds_template,self.src)

        self.mask_template = self.create_mask_template()
        

        if initialize_cfs:            
            # set up array of ConnectionFields translated to each x,y in the src sheet
            cflist = []
            for y in self.dest.sheet_rows()[::-1]:
                row = []
                for x in self.dest.sheet_cols():
                    # JABALERT: Currently computes the location of the
                    # ConnectionField as the exact location in the input
                    # sheet corresponding to the unit in the destination
                    # sheet.  Instead, we will need to add the ability to
                    # use some other type of mapping, e.g. to add jitter
                    # in the initial mapping.
                    row.append(self.cf_type(x,y,
                                            self.src,
                                            copy.copy(self.bounds_template),
                                            self.weights_generator,
                                            copy.copy(self.mask_template), 
                                            output_fn=self.weights_output_fn.single_cf_fn,
                                            slice_=slice_))
                cflist.append(row)


            ### JABALERT: Should make cfs semi-private, since it has an
            ### accessor function and isn't always the same format
            ### (e.g. for SharedWeightCFProjection).  Could also make it
            ### be a class attribute; not sure.
            self.cfs = cflist

        ### JCALERT! We might want to change the default value of the
        ### input value to self.src.activity; but it fails, raising a
        ### type error. It probably has to be clarified why this is
        ### happening
        self.input_buffer = None
        self.activity = Numeric.array(self.dest.activity)



    def create_mask_template(self):
        """
        """
        # CEBHACKALERT: allow user to override this.
        # calculate the size & aspect_ratio of the mask if appropriate
        # mask size set to be that of the weights matrix
        if hasattr(self.weights_shape, 'size'):
            l,b,r,t = self.bounds_template.lbrt()
            self.weights_shape.size = t-b
            self.weights_shape.aspect_ratio = (r-l)/self.weights_shape.size

        # Center mask to matrixidx center
        center_r,center_c = self.src.sheet2matrixidx(0,0)
        center_x,center_y = self.src.matrixidx2sheet(center_r,center_c)
        
        mask_template = self.weights_shape(x=center_x,y=center_y,
                                           bounds=self.bounds_template,
                                           xdensity=self.src.xdensity,
                                           ydensity=self.src.ydensity)
        # CEBHACKALERT: threshold should be settable by user
        mask_template = Numeric.where(mask_template>=0.5,mask_template,0.0)

        return mask_template
        

    def initialize_bounds(self,original_bounds):
        """
        Return sheet-coordinate bounds that correspond exactly to the slice
        of the sheet which best approximates the specified sheet-coordinate
        bounds.

        The supplied bounds are translated to have a center at the
        center of one of the sheet's units (we arbitrarily use the
        center unit), and then these bounds are converted to a slice
        in such a way that the slice exactly includes all units whose
        centers are within the bounds (see
        SheetCoordinateSystem.bounds2slice()). However, to ensure that
        the bounds are treated symmetrically, we take the right and
        bottom bounds and reflect these about the center of the slice
        (i.e. we take the 'xradius' to be right_col-center_col and the
        'yradius' to be bottom_col-center_row). Hence, if the bounds
        happen to go through units, if the units are included on the
        right and bottom bounds, they will be included on the left and
        top bounds. This ensures that the slice has odd dimensions.

        This slice is converted back to the exactly corresponding
        bounds, and these are returned.
        """
        # don't alter the original_bounds
        bounds = copy.deepcopy(original_bounds)
        
        bounds_xcenter,bounds_ycenter=bounds.get_center()
        sheet_rows,sheet_cols=self.src.shape
        # arbitrary (e.g. could use 0,0) 
        center_row,center_col = sheet_rows/2,sheet_cols/2
        unit_xcenter,unit_ycenter=self.src.matrixidx2sheet(center_row,
                                                           center_col)

        #CEBHACKALERT: to be cleaned up...
        self.center_unitxcenter,self.center_unitycenter = unit_xcenter,unit_ycenter

        bounds.translate(unit_xcenter-bounds_xcenter,
                         unit_ycenter-bounds_ycenter)

        ### CEBHACKALERT: for now, assumes weights are to be centered
        # about each unit, whatever the user specified. This will be
        # changed. See also CF.offset_bounds().
        #
        # Slice will (optionally) perform a more general version
        # of this, so it will not need to appear here.
        weights_slice =  Slice(bounds,self.src)
        r1,r2,c1,c2 = weights_slice

        # use the calculated radius unless it's smaller than the min
        xrad=max(c2-center_col-1,self.min_matrix_radius)
        yrad=max(r2-center_row-1,self.min_matrix_radius)

        r2=center_row+yrad+1
        c2=center_col+xrad+1
        r1=center_row-yrad
        c1=center_col-xrad

        weights_slice._set_slice((r1,r2,c1,c2))
        ### end CEBHACKALERT

        ### Checks:
        # (1) user-supplied bounds must lead to a weights matrix of at
        # least 1x1
        rows,cols = weights_slice.shape
        if rows==0 or cols==0:
            raise ValueError("nominal_bounds_template results in a zero-sized weights matrix (%s,%s) for %s - you may need to supply a larger nominal_bounds_template or increase the density of the sheet."%(rows,cols,self.name))
        # (2) weights matrix must be odd (otherwise this method has an error)
        # (The second check should move to a test file.)
        if rows%2!=1 or cols%2!=1:
            raise AssertionError("nominal_bounds_template yielded even-height or even-width weights matrix (%s rows, %s columns) for %s - weights matrix must have odd dimensions."%(rows,cols,self.name))



        return weights_slice.bounds

    def cf(self,r,c):
        """Return the specified ConnectionField"""
        return self.cfs[r][c]


    def get_shape(self):
        return len(self.cfs),len(self.cfs[0])


    def get_view(self,sheet_x, sheet_y):
        """
        Return a single connection field UnitView, for the unit
        located at sheet coordinate (sheet_x,sheet_y).
        """
	matrix_data = Numeric.zeros(self.src.activity.shape,Numeric.Float)
        (r,c) = self.dest.sheet2matrixidx(sheet_x,sheet_y)
        r1,r2,c1,c2 = self.cf(r,c).slice_array
	matrix_data[r1:r2,c1:c2] = self.cf(r,c).weights

        return UnitView((matrix_data,self.src.bounds),sheet_x,sheet_y,self)


    def get_projection_view(self):
	"""
	Returns the activity in a single projection
	"""
	matrix_data = Numeric.array(self.activity)
	 
	
	return ProjectionView((matrix_data,self.src.bounds),self)


    def activate(self,input_activity):
        """Activate using the specified response_fn and output_fn."""
        self.input_buffer = input_activity
        self.response_fn(self.cfs, input_activity, self.activity, self.strength)
        self.output_fn(self.activity)


    def learn(self):
        """
        For a CFProjection, learn consist in calling the learning_fn.
        """
        # Learning is performed if the input_buffer has already been set,
        # i.e. there is an input to the Projection.
        if self.input_buffer:
            self.learning_fn(self.cfs,self.input_buffer,self.dest.activity,self.learning_rate)


    ### JABALERT: Is this necessary?
    def apply_output_fn(self):
        """Apply the weights_output_fn to the weights."""
        self.weights_output_fn(self.cfs,self.dest.activity)


    ### JABALERT: This should be changed into a special __set__ method for
    ### bounds_template, instead of being a separate function.
    def change_bounds(self, nominal_bounds_template):
        """
        Change the bounding box for all of the ConnectionFields in this Projection.

        Calls change_bounds() on each ConnectionField.

	Currently only allows reducing the size, but should be
        extended to allow increasing as well.
        """
        bounds_template = self.initialize_bounds(nominal_bounds_template)

        if not self.bounds_template.containsbb_exclusive(bounds_template):
            if self.bounds_template.containsbb_inclusive(bounds_template):
                self.debug('Initial and final bounds are the same.')
            else:
                self.warning('Unable to change_bounds; currently allows reducing only.')
            return

        # it's ok so we can store the bounds and resize the weights
        self.nominal_bounds_template = nominal_bounds_template
        self.bounds_template = bounds_template

        mask_template = self.create_mask_template()
        
        rows,cols = self.get_shape()
        cfs = self.cfs
        output_fn = self.weights_output_fn.single_cf_fn
        for r in xrange(rows):
            for c in xrange(cols):
                cfs[r][c].change_bounds(copy.copy(bounds_template),
                                        copy.copy(mask_template),
                                        output_fn=output_fn)



    def change_density(self, new_wt_density):
        """
        Rescales the weight matrix in place, interpolating or resampling as needed.
	
	Not yet implemented.
	"""
        raise NotImplementedError



class CFSheet(ProjectionSheet):
    """
    A ProjectionSheet providing access to the ConnectionFields in its CFProjections.

    CFSheet is a Sheet built from units indexed by Sheet coordinates
    (x,y).  Each unit can have one or more ConnectionFields on another
    Sheet (via this sheet's CFProjections).  Thus CFSheet is a more
    concrete version of a ProjectionSheet; a ProjectionSheet does not
    require that there be units or weights of any kind.  Unless you
    need access to the underlying ConnectionFields for visualization
    or analysis, CFSheet and ProjectionSheet are interchangeable.
    """

    measure_maps = BooleanParameter(True,doc="""
        Whether to include this Sheet when measuring various maps to create SheetViews.""")

    precedence = Number(0.5)

    def _port_match(self,key,portlist):
        """
        Returns True if the given key matches any port on the given list.

        A port is considered a match if the port is == to the key,
        or if the port is a tuple whose first element is == to the key,
        or if both the key and the port are tuples whose first elements are ==.
        """
        port=portlist[0]
        return [port for port in portlist
                if (port == key or
                    (isinstance(key,tuple)  and key[0] == port) or
                    (isinstance(port,tuple) and port[0] == key) or
                    (isinstance(key,tuple)  and isinstance(port,tuple) and port[0] == key[0]))]

    # JABHACKALERT: Need to jointly normalize before the first iteration, somehow.
    # Also, whenever a connection is added to a group, need to check
    # that it has the same no of cfs as the existing connection.

    def __grouped_in_projections(self):
        """
        Return a dictionary of lists of incoming Projections, grouped for normalization..

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

                        
    # should refer to applying output_fn together, not just normalization
    # (here and elsewhere)
    def __normalize_joint_projections(self,projlist):
        """Normalize the specified list of projections together."""

        # Assumes that all Projections in the list have the same r,c size
        assert len(projlist)>=1
        proj  = projlist[0]
        rows,cols = len(proj.cfs),len(proj.cfs[0])

        for r in range(rows):
            for c in range(cols):
                sums = [p.cfs[r][c].sum for p in projlist]
                # CB: *to check, this could be the wrong way round*
                # + document
                joint_sum = Numeric.add.reduce(sums)/float(len(projlist))
                for p in projlist:
                    p.cfs[r][c].sum=joint_sum
                 
        for p in projlist:
            p.apply_output_fn()


    def learn(self):
        """
        Call the learn() method on every Projection to the Sheet.
        """
        # Ask all projections to learn independently
        for proj in self.in_connections:
            if not isinstance(proj,Projection):
                self.debug("Skipping non-Projection "+proj.name)
            else:
                proj.learn()

        # Apply output function in groups determined by dest_port
        for key,projlist in self.__grouped_in_projections():
            if key == None:
                self.debug("Time " + str(self.simulation.time()) + ": " +
                           "Independently normalizing:")
                for p in projlist:
                    p.apply_output_fn()
                    self.debug('  ',p.name)
            else:
                self.debug("Time " + str(self.simulation.time()) + ": " +
                           "Jointly normalizing %s:" % key)
                for p in projlist: self.debug("  ",p.name)
                self.__normalize_joint_projections(projlist)
         

                
    def update_unit_view(self,x,y,proj_name=''):
        """
	Creates the list of UnitView objects for a particular unit in this CFSheet.
	(There is one UnitView for each Projection to this CFSheet).

	Each UnitView is then added to the sheet_view_dict of its source sheet.
	It returns the list of all UnitView for the given unit.
	"""     
        for p in self.in_connections:
            if not isinstance(p,CFProjection):
                self.debug("Skipping non-CFProjection "+p.name)
            elif proj_name == '' or p.name==proj_name:
                v = p.get_view(x,y)
                src = v.projection.src
                key = ('Weights',v.projection.dest.name,v.projection.name,x,y)
                src.sheet_view_dict[key] = v
    

 
    ### JCALERT! This should probably be deleted...
    def release_unit_view(self,x,y):
        self.release_sheet_view(('Weights',x,y))

