"""
File containing optimized elements of sheets.
"""
from topo.base.functionfamilies import OutputFn, OutputFnParameter, IdentityOF
from topo.base.parameterclasses import Number
from topo.base.parameterizedobject import ParameterizedObject

from topo.misc.inlinec import inline, provide_unoptimized_equivalent

from topo.sheets.lissom import LISSOM
from topo.base.projection import OutputFnParameter, Projection

class LISSOM_Opt(LISSOM):
    """
    Overrides the function JointNormalizingCFSheet.__compute_joint_norm_totals 
    with C optimized code for LISSOM sheet
    """

    def compute_joint_norm_totals(self,projlist,mask):
            """Compute norm_total for each CF in each projections from a group to be normalized jointly.
               The same assumptions are done as in the original function!
            """
            
            # Assumes that all Projections in the list have the same r,c size
            assert len(projlist)>=1
            rows,cols = projlist[0].cfs_shape
            length = len(projlist)

            code = """
                double *x = mask;
                for (int r=0; r<rows; ++r) {
                    for (int l=0; l<cols; ++l) {
                        double load = *x++;
                        if (load != 0)
                        {
                            double nt = 0;
                            
                            for(int p=0; p<length; p++)
                            {
                                PyObject *proj = PyList_GetItem(projlist,p);
                                PyObject *cfs = PyObject_GetAttrString(proj,"_cfs");
                                PyObject *cf = PyList_GetItem(PyList_GetItem(cfs,r),l);
                                PyObject *o = PyObject_GetAttrString(cf,"norm_total");
                                nt += PyFloat_AsDouble(o);
                                Py_DECREF(cfs);
                                Py_DECREF(o);
                            }
                            
                            for(int p=0; p<length; p++)
                            {
                                PyObject *proj = PyList_GetItem(projlist,p);
                                PyObject *cfs = PyObject_GetAttrString(proj,"_cfs");
                                PyObject *cf = PyList_GetItem(PyList_GetItem(cfs,r),l);
                                PyObject *total_obj = PyFloat_FromDouble(nt);  //(new ref)
                                PyObject_SetAttrString(cf,"norm_total",total_obj);
                                PyObject_SetAttrString(cf,"has_norm_total",Py_True);
                                Py_DECREF(cfs);
                                Py_DECREF(total_obj);
                            }
                        }
                    }
                }
            """    
            inline(code, ['projlist','mask','rows','cols','length'], local_dict=locals())

provide_unoptimized_equivalent("LISSOM_Opt","LISSOM",locals())
