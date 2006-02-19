"""
ConnectionField and associated classes.

This module defines some basic classes of objects used to create
simulations of cortical sheets that take input through connection
fields that project from other cortical sheets (or laterally from
themselves):

ConnectionField: Holds a single connection field within a CFProjection.

CFProjection: A set of ConnectionFields mapping from a Sheet into a
ProjectionSheet.

CFSheet: A subclass of ProjectionSheet that provides an interface to
the underlying ConnectionFields in any projection of type CFProjection.

$Id$
"""

__version__ = '$Revision$'


import Numeric
import copy

from parameterizedobject import ParameterizedObject
from projection import Projection,ProjectionSheet,Identity,OutputFunctionParameter
from parameterclasses import Parameter, Number, BooleanParameter,ClassSelectorParameter
from arrayutils import Mdot,divisive_normalization
from sheet import Sheet,bounds2slice,sheet2matrixidx,crop_slice_to_sheet_bounds,slice2bounds
from sheetview import UnitView
from itertools import chain
from patterngenerator import PatternGeneratorParameter
import patterngenerator
from boundingregion import BoundingBox


# Specified explicitly when creating weights matrix - required
# for optimized C functions.
weight_type = Numeric.Float32


def hebbian(input_activity, unit_activity, weights, single_connection_learning_rate):
    """Simple Hebbian learning for the weights of one single unit."""
    weights += single_connection_learning_rate * unit_activity * input_activity

# CEBHACKALERT: see docstring
class Hebbian(object):
    """
    This is a temporary wrapper around the hebbian() function so that
    deepcopy can work when a Parameter has this function as its
    default value. (To be removed when ParameterizedObject's support for
    deepcopy is corrected. See connectionfield.py's GenericCFResponseFn
    and projections/basic.py's SharedWeightCFResponseFn)
    """
    def __call__(self,input_activity, unit_activity, weights, single_connection_learning_rate):
        weights += single_connection_learning_rate * unit_activity * input_activity


class ConnectionField(ParameterizedObject):
    """
    A set of weights on one input Sheet.

    Each ConnectionField contributes to the activity of one unit on
    the output sheet, and is normally used as part of a Projection
    including many other ConnectionFields.
    """
    
    x = Parameter(default=0,doc='The x coordinate of the location of the center of this ConnectionField\non the input Sheet, e.g. for use when determining where the weight matrix\nlines up with the input Sheet matrix.')
    y = Parameter(default=0,doc='The y coordinate of the location of the center of this ConnectionField\non the input Sheet, e.g. for use when determining where the weight matrix\nlines up with the input Sheet matrix.')

    # Weights matrix; not yet initialized.
    weights = []

    # Specifies how to get a submatrix from the source sheet that is aligned
    # properly with this weight matrix.  The information is stored as an
    # array for speed of access from optimized C components; use
    # self.slice_tuple() for a nicer Python access method.
    slice_array = []

    # CEBHACKALERT: add some default values
    def __init__(self,x,y,input_sheet,weights_bounds_template,
                 weights_generator,mask_template,
                 output_fn=Identity(),**params):
        """

        weights_bounds_templates is assumed to have been initialized correctly
        already (see e.g. CFProjection.initialize_bounds() ).
        """
        # CEBHACKALERT: maybe an external function is required? We need to
        # have correctly setup bounds here, in change_bounds(), and in other
        # places such as CFProjection (where the mask is made). At the moment,
        # the function is in CFProjection.

        super(ConnectionField,self).__init__(**params)

        self.x = x; self.y = y
        self.input_sheet = input_sheet
        self.offset_bounds(weights_bounds_template)

        # CEBHACKALERT: to change when density is sorted out
        density = (self.input_sheet.xdensity,self.input_sheet.ydensity)


        # CEBHACKALERT: might want to do something about a size that's specified.
        w = weights_generator(x=self.x,y=self.y,bounds=self.bounds,
                              density=density)
        self.weights = w.astype(weight_type)
        # Maintain the original type throughout operations, i.e. do not
        # promote to double.
        self.weights.savespace(1)

        # Now we have to get the right submatrix of the mask (in case it is near an edge)
        r1,r2,c1,c2 =  self.get_slice(weights_bounds_template)
        m = mask_template[r1:r2,c1:c2]
        
        self.mask = m.astype(weight_type)
        self.mask.savespace(1)

        # CEBHACKALERT: this works for now, while the output_fns are all multiplicative.
        self.weights *= self.mask   
        output_fn(self.weights)
        
        # CEBHACKALERT: incorporate such a test into testconnectionfield.
#        assert self.weights.shape==(self.slice_array[1]-self.slice_array[0],self.slice_array[3]-self.slice_array[2]),str(self.weights.shape)+" "+str((self.slice_array[1]-self.slice_array[0],self.slice_array[3]-self.slice_array[2])) 


    ### CEBHACKALERT: there is presumably a better way than this.
    def get_slice(self,weights_bounds_template):
        """
        Return the correct slice for a weights/mask matrix at this
        ConnectionField's location on the sheet (i.e. for getting
        the correct submatrix of the weights or mask in case the
        unit is near the edge of the sheet).
        """
        # get size of sheet (=self.input_sheet.activity.shape)
        sr1,sr2,sc1,sc2 = bounds2slice(self.input_sheet.bounds,self.input_sheet.bounds,self.input_sheet.xdensity,self.input_sheet.ydensity)
        sheet_rows = sr2-sr1; sheet_cols = sc2-sc1

        # get size of weights matrix
        r1,r2,c1,c2 = bounds2slice(weights_bounds_template,self.input_sheet.bounds,
                                   self.input_sheet.xdensity,self.input_sheet.ydensity)
        n_rows=r2-r1; n_cols=c2-c1

        # get slice for the submatrix
        center_row,center_col = self.input_sheet.sheet2matrixidx(self.x,self.y)
        
        c1 = -min(0, center_col-n_cols/2)  # assume odd weight matrix so can use n_cols/2 
        r1 = -min(0, center_row-n_rows/2)  # for top and bottom
        c2 = -max(-n_cols, center_col-sheet_cols-n_cols/2)
        r2 = -max(-n_rows, center_row-sheet_rows-n_rows/2)
        return (r1,r2,c1,c2)
        

    def offset_bounds(self,bounds):
        """
        Given bounds centered on the sheet matrix, offset them to this
        cf's location and store the result as self.bounds.

        Also stores the slice_array for access by C.
	"""
        r1,r2,c1,c2 = bounds2slice(bounds,self.input_sheet.bounds,
                                   self.input_sheet.xdensity,self.input_sheet.ydensity)

        # translate to this cf's location
        center_row,center_col = self.input_sheet.sheet2matrixidx(self.x,self.y)
        sheet_center_row,sheet_center_col = self.input_sheet.sheet2matrixidx(0.0,0.0)

        row_offset = center_row-sheet_center_row
        col_offset = center_col-sheet_center_col
        r1+=row_offset; r2+=row_offset
        c1+=col_offset; c2+=col_offset

        # crop to the sheet's bounds
        r1,r2,c1,c2 = crop_slice_to_sheet_bounds((r1,r2,c1,c2),self.input_sheet.bounds,
                                                 self.input_sheet.xdensity,self.input_sheet.ydensity)

        self.bounds = slice2bounds((r1,r2,c1,c2), self.input_sheet.bounds, self.input_sheet.xdensity, self.input_sheet.ydensity)


        # Also, store the array for direct access by C.
        # Numeric.Int32 is specified explicitly here to avoid having it
        # default to Numeric.Int.  Numeric.Int works on 32-bit platforms,
        # but does not work properly with the optimized C activation and
        # learning functions on 64-bit machines.
        self.slice_array = Numeric.array((r1,r2,c1,c2),typecode=Numeric.Int32) 


    def get_input_matrix(self, activity):
        r1,r2,c1,c2 = self.slice_tuple()
        return activity[r1:r2,c1:c2]


    def change_bounds(self, weights_bounds, mask_template, output_fn=Identity()):
        """
        Change the bounding box for this ConnectionField.

        weights_bounds is assumed to have been initialized
        already (made odd, snapped to grid - as in __init__() ).
        
        Discards weights or adds new (zero) weights as necessary,
        preserving existing values where possible.

        Currently only supports reducing the size, not increasing, but
        should be extended to support increasing as well.
        """
        # CEBHACKALERT: re-write to allow arbitrary resizing
        or1,or2,oc1,oc2 = self.slice_tuple()

        self.offset_bounds(weights_bounds)
        r1,r2,c1,c2 = self.slice_tuple()

        if not (r1 == or1 and r2 == or2 and c1 == oc1 and c2 == oc2):
            self.weights = Numeric.array(self.weights[r1-or1:r2-or1,c1-oc1:c2-oc1],copy=1)

            mr1,mr2,mc1,mc2 = self.get_slice(weights_bounds)
            m = mask_template[mr1:mr2,mc1:mc2]
            self.mask = m.astype(weight_type)
            self.mask.savespace(1)

            # CEBHACKALERT: see __init__
            self.weights *= self.mask
            output_fn(self.weights)

    def slice_tuple(self):
        return self.slice_array[0],self.slice_array[1],self.slice_array[2],self.slice_array[3]

    def change_density(self, new_wt_density):
        """Rescale the weight matrix in place, interpolating or decimating as necessary."""
        raise NotImplementedError



class CFResponseFunction(ParameterizedObject):
    """
    Map an input activity matrix into an output matrix using CFs.

    Objects in this hierarchy of callable function objects compute a
    response matrix when given an input pattern and a set of
    ConnectionField objects.  Typically used as part of the activation
    function for a neuron, computing activation for one Projection.

    Objects in this class must support being called as a function with
    the arguments specified below, and must return a matrix the same
    size as the activity matrix supplied.
    """
    def __call__(self, cfs, input_activity, activity, strength, **params):
        raise NotImplementedError



class GenericCFResponseFn(CFResponseFunction):
    """
    Generic large-scale response function based on a simple single-CF function.

    Applies the single_cf_fn to each CF in turn.  For the default
    single_cf_fn of mdot, does a basic dot product of each CF with the
    corresponding slice of the input array.  This function is likely
    to be slow to run, but it is easy to extend with any arbitrary
    single-CF response function.

    The single_cf_fn must be a function f(X,W) that takes two
    identically shaped matrices X (the input) and W (the
    ConnectionField weights) and computes a scalar activation value
    based on those weights.
    """
    single_cf_fn = Parameter(default=Mdot())
    
    def __init__(self,**params):
        super(GenericCFResponseFn,self).__init__(**params)

    def __call__(self, cfs, input_activity, activity, strength):
        rows,cols = activity.shape

        single_cf_fn = self.single_cf_fn
        for r in xrange(rows):
            for c in xrange(cols):
                cf = cfs[r][c]
                r1,r2,c1,c2 = cf.slice_tuple()
                X = input_activity[r1:r2,c1:c2]
                activity[r,c] = single_cf_fn(X,cf.weights)
        activity *= strength


# CEBHACKALERT: don't need to pass through stuff like doc because of **params
class ResponseFunctionParameter(ClassSelectorParameter):
    """
    """
    def __init__(self,default=GenericCFResponseFn(),doc='',**params):
        """
        """
        super(ResponseFunctionParameter,self).__init__(CFResponseFunction,default=default,doc=doc,**params)        


class CFLearningFunction(ParameterizedObject):
    """
    Compute new CFs based on input and output activity values.

    Objects in this hierarchy of callable function objects compute a
    new set of CFs when given input and output patterns and a set of
    ConnectionField objects.  Typically used for updating the weights
    of one CFProjection.

    Objects in this class must support being called as a function with
    the arguments specified below.
    """
 
    def constant_sum_connection_rate(self,cfs,learning_rate):
	""" 
	return the learning rate for a single connection according to the total learning_rate,
        the number of rows and cols of the output_activity matrix and the connection fields
	matrix cfs. Keep the sum of the single connection learning rate constant.
	"""      
        ### JCALERT! To check with Jim: we take the number of unit at the center of the matrix
        ### That would be the best way to go, but it is not possible to acces the 
        ### sheet_density and bounds from here without more important changes
        #center_r,center_c = sheet2matrixidx(0,0,bounds,xdensity,ydensity)
	rows = len(cfs)
	cols = len(cfs[0])
	cf = cfs[cols/2][rows/2]
        # The number of units in the mask 
	nb_unit = len(Numeric.nonzero(Numeric.ravel(cf.mask)))
	constant_sum_connection_rate=learning_rate/(nb_unit)
	return constant_sum_connection_rate

    def __call__(self, cfs, input_activity, output_activity, learning_rate, **params):
        raise NotImplementedError


class IdentityCFLF(CFLearningFunction):
    """CFLearningFunction performing no learning."""

    output_fn = OutputFunctionParameter(default=Identity(),
                 doc='Function applied to the weights after each learning step.')
    def __call__(self, cfs, input_activity, output_activity, learning_rate, **params):
        pass


# CEBHACKALERT: don't need to pass through stuff like doc because of **params
class LearningFunctionParameter(ClassSelectorParameter):
    """
    """
    def __init__(self,default=IdentityCFLF(),doc='',**params):
        """
        """
        super(LearningFunctionParameter,self).__init__(CFLearningFunction,default=default,doc=doc,**params)        


class GenericCFLF(CFLearningFunction):
    """CFLearningFunction applying the specified single_cf_fn to each CF."""
    single_cf_fn = Parameter(default=Hebbian())
    output_fn =  OutputFunctionParameter(default=Identity(),
                 doc='Function applied to the weights after each learning step')
    
    def __init__(self,**params):
        super(GenericCFLF,self).__init__(**params)

   
    def __call__(self, cfs, input_activity, output_activity, learning_rate, **params):
        """Apply the specified single_cf_fn to every CF."""
        rows,cols = output_activity.shape
	single_connection_learning_rate = self.constant_sum_connection_rate(cfs,learning_rate)
        # avoid evaluating these references each time in the loop
        output_fn = self.output_fn
        single_cf_fn = self.single_cf_fn
	for r in xrange(rows):
            for c in xrange(cols):
                cf = cfs[r][c]
                single_cf_fn(cf.get_input_matrix(input_activity),
                             output_activity[r,c], cf.weights, single_connection_learning_rate)
                # CEBHACKALERT: see ConnectionField.__init__()
                cf.weights *= cf.mask
                output_fn(cf.weights)
                

class CFProjection(Projection):
    """
    A projection composed of ConnectionFields from a Sheet into a ProjectionSheet.

    CFProjection computes its activity using a response_fn of type
    CFResponseFunction (typically a CF-aware version of mdot) and output_fn 
    (which is typically Identity). Any subclass has to implement the interface
    activate(self,input_activity) that computes the response from the input 
    and stores it in the activity array.
    """
    response_fn = ResponseFunctionParameter(default=GenericCFResponseFn(),
                                            doc='Function for computing the Projection response to an input pattern.' )
    cf_type = Parameter(default=ConnectionField,constant=True)
    weights_bounds = Parameter(default=BoundingBox(points=((-0.1,-0.1),(0.1,0.1))))
    weights_generator = PatternGeneratorParameter(default=patterngenerator.Constant(),constant=True)
    weights_shape = PatternGeneratorParameter(default=patterngenerator.Constant(),constant=True)
    learning_fn = LearningFunctionParameter(default=GenericCFLF(),
                                            doc='Function for computing changes to the weights based on one activation step.')
    learning_rate = Parameter(default=0.0)
    output_fn  = OutputFunctionParameter(default=Identity(),
                                         doc='Function applied to the Projection activity after it is computed.')
    strength = Number(default=1.0)



    def __init__(self,initialize_cfs=True,**params):
        """
        Initialize the Projection with a set of cf_type objects
        (typically ConnectionFields), each located at the location
        in the source sheet corresponding to the unit in the target
        sheet.

        The weights_bounds specified may be altered. The bounds must
        be fit to the Sheet's matrix, and the weights matrix must
        have odd dimensions. These altered bounds are passed to the
        individual connection fields.

        A mask for the weights matrix is constructed. The shape is
        specified by weights_shape; the size defaults (CEBHACKALERT)
        to the size of the altered weights_bounds.
        """
        super(CFProjection,self).__init__(**params)

        # adjust the weights to fit the sheet, and to be odd.
        self.weights_bounds = self.initialize_bounds(self.weights_bounds)

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
                                            copy.copy(self.weights_bounds),
                                            self.weights_generator,
                                            copy.copy(self.mask_template), 
                                            self.learning_fn.output_fn))
                cflist.append(row)


            ### JABALERT: Should make cfs semi-private, since it has an
            ### accessor function and isn't always the same format
            ### (e.g. for SharedWeightProjection).  Could also make it
            ### be a class attribute; not sure.
            self.cfs = cflist

        ### JCALERT! We might want to change the default value of the input value to self.src.activity;
        ### but it fails, raising a type error. It probably has to be clarified why this is happenning
        self.input_buffer = None
        self.activity = Numeric.array(self.dest.activity)



    def create_mask_template(self):
        """
        """
        # CEBHACKALERT: allow user to override this.
        # calculate the size & aspect_ratio of the mask if appropriate
        if hasattr(self.weights_shape, 'size'):
            l,b,r,t = self.weights_bounds.lbrt()
            self.weights_shape.size = t-b
            self.weights_shape.aspect_ratio = (r-l)/self.weights_shape.size

        # CEBHACKALERT: mask centered to matrixidx center
        center_r,center_c = self.src.sheet2matrixidx(0,0)
        center_x,center_y = self.src.matrixidx2sheet(center_r,center_c)
        
        density = (self.src.xdensity,self.src.ydensity)
        mask_template = self.weights_shape(x=center_x,y=center_y,
                                           bounds=self.weights_bounds,
                                           density=density)
        # CEBHACKALERT: threshold should be settable by user
        mask_template = Numeric.where(mask_template>=0.5,mask_template,0.0)

        return mask_template
        

    def initialize_bounds(self,bounds):
        """
        Return sheet-coordinate bounds corresponding to the odd-dimensions
        slice that best approximates the specified sheet-coordinate bounds.


        Converts the bounds to a slice, but ensuring the slice specifies
        an odd number of rows and an odd number of columns. Then converts this
        slice back to sheet-coordinate bounds.    
        """
        slice_ = bounds2slice(bounds,self.src.bounds,self.src.xdensity,self.src.ydensity)
        n_rows=slice_[1]-slice_[0]; n_cols=slice_[3]-slice_[2]

        sheet_center_row,sheet_center_col = self.src.sheet2matrixidx(0.0,0.0)

        r1 = sheet_center_row - n_rows/2
        c1 = sheet_center_col - n_cols/2
        r2 = sheet_center_row + n_rows/2 +1
        c2 = sheet_center_col + n_cols/2 +1

        return slice2bounds((r1,r2,c1,c2),self.src.bounds,self.src.xdensity,self.src.ydensity)


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
        (r,c) = (self.dest).sheet2matrixidx(sheet_x,sheet_y)

        # CEBHACKALERT: why is this necessary? Isn't cf[r][c].weights
        # already a Numeric array? (Same in SharedWeightProjection.)
        matrix_data = Numeric.array(self.cf(r,c).weights)

        new_box = self.cf(r,c).bounds
	
        assert matrix_data != None, "Projection Matrix is None"
        return UnitView((matrix_data,new_box),sheet_x,sheet_y,self)


    def activate(self,input_activity):
        """Activate using the specified response_fn and output_fn."""
        self.input_buffer = input_activity
        self.response_fn(self.cfs, input_activity, self.activity, self.strength)
        self.activity = self.output_fn(self.activity)


    def learn(self):
        """
        For a CFProjection, learn consist in calling the learning_fn.
        """
        # Learning is performed if the input_buffer has already been set,
        # i.e. there is an input to the Projection.
        if self.input_buffer:
            self.learning_fn(self.cfs,self.input_buffer,self.dest.activity,self.learning_rate)
      

    ### JABALERT: This should be changed into a special __set__ method for
    ### weights_bounds, instead of being a separate function.
    def change_bounds(self, weights_bounds_template):
        """
        Change the bounding box for all of the ConnectionFields in this Projection.

        Calls change_bounds() on each ConnectionField.

	Currently only allows reducing the size, but should be
        extended to allow increasing as well.
        """
        weights_bounds = self.initialize_bounds(weights_bounds_template)

        # CEBHACKALERT: should only warn if new bounds are actually larger - right
        # now it warns if bounds stay the same size.
        if not self.weights_bounds.containsbb_exclusive(weights_bounds):
            self.warning('Unable to change_bounds; currently allows reducing only.')
            return

        self.weights_bounds = weights_bounds

        mask_template = self.create_mask_template()
        
        rows,cols = self.get_shape()
        cfs = self.cfs
        output_fn = self.learning_fn.output_fn
        for r in xrange(rows):
            for c in xrange(cols):
                cfs[r][c].change_bounds(copy.copy(weights_bounds),copy.copy(mask_template),output_fn=output_fn)



    def change_density(self, new_wt_density):
        """
        Rescales the weight matrix in place, interpolating or resampling as needed.
	
	Not yet implemented.
	"""
        raise NotImplementedError



class CFSheet(ProjectionSheet):
    """
    A ProjectionSheet providing access to the ConnectionFields in its CFProjections.

    ProjectionSheet classes do not assume that the Projections can
    provide a set of weights for individual units, or indeed that
    there are units or weights at all.  In contrast, CFSheet is built
    around the assumption that there are units in this Sheet, indexed
    by Sheet coordinates (x,y), and that these units have one or more
    ConnectionField connections on another Sheet (via CFProjections).
    It then provides an interface for visualizing or analyzing these
    ConnectionFields for each unit.  A ProjectionSheet should work
    just the same as this sheet, except that it will not provide those
    routines.
    """

    measure_maps = BooleanParameter(True)
    precedence = Number(0.5)

        
    def learn(self):
        """
        Call the learn() method on every CFProjection to the Sheet.
        """
        for proj in chain(*self.in_projections.values()):
            proj.learn()

                
    def update_unit_view(self,x,y,projection_name=None):
        """
	Creates the list of UnitView objects for a particular unit in this CFSheet,
	(There is one UnitView for each projection to this CFSheet).

	Each UnitView is then added to the sheet_view_dict of its source sheet.
	It returns the list of all UnitView for the given unit.
	"""     
        ### JCALERT! The use of the chain function (here and in projection.py)
        ### could be deleted after re-organizing the way projections are stored
        ### in self.in_projections. I think there is no need to store a list at all.
        ### (see ProjectionSheet in projection.py)
        from itertools import chain
        in_projections = [p for p in chain(*self.in_projections.values())]

        # We check that all the projections are CFProjection
        for p in in_projections:
            if not isinstance(p,CFProjection):
                ### JCALERT! Choose if we raise an error or if we just delete the
                ### Non-CFProjection from the in_projection list.
                raise ValueError("projection has to be a CFProjection in order to build UnitView.")
            
        if projection_name == None:
            projection_filter = lambda p: True
        else:
            projection_filter = lambda p: p.name==projection_name
            
        views = [p.get_view(x,y) for p in in_projections if projection_filter(p)]

        for v in views:
            src = v.projection.src
            key = ('Weights',v.projection.dest.name,v.projection.name,x,y)
            src.sheet_view_dict[key] = v
       
        
    ### JCALERT! This should probably be deleted...
    def release_unit_view(self,x,y):
        self.release_sheet_view(('Weights',x,y))






   
    

        
