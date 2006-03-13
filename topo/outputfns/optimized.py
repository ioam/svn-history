"""
Output functions (see basic.py) written in C to optimize performance.

Requires the weave package; without it unoptimized versions are used.
"""
from topo.base.projection import OutputFunction
from topo.base.parameterizedobject import ParameterizedObject
from topo.base.parameterclasses import Number

from topo.misc.inlinec import inline, optimized

from basic import DivisiveSumNormalize as DivisiveSumNormalize_Py


# CB: will be DivisiveL1Normalize (i.e. will use the
# absolute values - see basic.py).
class DivisiveSumNormalize(OutputFunction):
    """
    OutputFunction that divides an array by its sum.

    See the equivalent version in outputfns.basic for a
    description.

    The given array must be of type Numeric.Float32.
    """
    norm_value = Number(default=1.0)    

    def __init__(self,**params):
        super(DivisiveSumNormalize,self).__init__(**params)

    def __call__(self, x, current_norm_value=None):
        """
        Normalize the input array.

        If the array's current norm_value is already equal to the required
        norm_value, the operation is skipped.
        """
        # Doesn't seem any faster to do this bit in C
        if current_norm_value==self.norm_value:
            return
        elif current_norm_value==None:
            current_norm_value=sum(x.flat)

        target_norm_value = self.norm_value

        if current_norm_value != 0:
            rows,cols=x.shape
            
            div_sum_norm_code = """
            float *xi = x;

            double factor = target_norm_value/current_norm_value;

            for (int i=0; i<rows*cols; ++i) {
                *(xi++) *= factor;
            }
            """
            inline(div_sum_norm_code, ['x','current_norm_value','target_norm_value','rows','cols'], local_dict=locals())


if not optimized:
    DivisiveSumNormalize = DivisiveSumNormalize_Py
    ParameterizedObject().message('Inline-optimized components not available; using DivisiveSumNormalize_Py instead of DivisiveSumNormalize.')
