"""
The Projection class.

$Id$
"""

import Numeric

from parameter import Parameter, Number, BooleanParameter
from utils import mdot
from learningrules import divisive_normalization
from cfsheet import ConnectionField
from sheetview import UnitView
from simulator import EPConnection

class Projection(EPConnection):
    """
    A projection of ConnectionFields from a Sheet into a CFSheet.

    Projection computes its activity using an activation_fn: A
    function f(X,W) that takes two identically shaped matrices X (the
    input) and W (the ConnectionField weights) and computes a scalar
    stimulation value based on those weights.

    Any subclass of Projection has to implement the interface
    compute_response(self,input_activity,rows,cols) that computes
    the response resulted from the input and store them in the 
    activity[] array.
    """

    activation_fn = Parameter(default=mdot)
    cf_type = Parameter(default=ConnectionField)
    normalize = BooleanParameter(default=False)
    normalize_fn = Parameter(default=divisive_normalization)
    weight_type = Parameter(default=Numeric.Float32)

    strength = Number(default=1.0)
    activity = []

    def __init__(self,**params):
        super(Projection,self).__init__(**params)
        self.cfs = None
        self.input_buffer = None
        self.activity = Numeric.array(self.dest.activity)

    def cf(self,r,c):
        return self.cfs[r][c]

    def set_cfs(self,cf_list):
        self.cfs = cf_list

    def get_shape(self):
        return len(self.cfs),len(self.cfs[0])


    def get_view(self,sheet_x, sheet_y):
        """
        Return a single connection field UnitView, for the unit
        located at sheet coordinate (sheet_x,sheet_y).
        """
        (r,c) = (self.dest).sheet2matrix(sheet_x,sheet_y)
        matrix_data = Numeric.array(self.cf(r,c).weights)

        ### JABHACKALERT!
        ###
        ### The bounds are currently set to a default; what should
        ### they really be set to?
        new_box = self.dest.bounds
        assert matrix_data != None, "Projection Matrix is None"
        return UnitView((matrix_data,new_box),sheet_x,sheet_y,self,view_type='UnitView')

    def compute_response(self,input_activity,rows,cols):
        pass

    def reduce_cfsize(self, new_wt_bounds):
        pass

