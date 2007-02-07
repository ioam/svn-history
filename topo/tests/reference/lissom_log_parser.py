"""
Functions for getting C++ LISSOM data and comparing them
with Topographica's.


$Id$
"""
__version__='$Revision$'

# CEBHACKALERT: filename should change

from Numeric import ones,zeros,where,ravel,sum,array
import topo
from topo.tests.utils import array_almost_equal

# The base part of the C++ lissom files that you are dealing with
# e.g. "topo/tests/reference/or_map_topo."
filename_base = ""


def get_input_params(log_file):
    """
    Return iterators over list of float values for C++ LISSOM's cx, cy, and theta.

    Expects log file with values held in lines like this::
    
      'Iteration: 000000  [Eye0 [Obj0 cx:02.1 cy:11.6 theta:074.0]]\n'  
    """
    f = open(log_file,'r')
    
    x = []
    y = []
    orientation = []

    n_inputs = 0
    for line in f.readlines():    
        if line.startswith('Iteration'):
            bits = line.split()
            assert len(bits)==7, "Messed-up line (is lissom still running?)\n" + line

            cx = float(bits[4].split(':')[1])
            cy = float(bits[5].split(':')[1])
            theta = float(bits[6].split(':')[1].rstrip(']]'))

            x.append(cx)
            y.append(cy)
            orientation.append(theta)
    
            n_inputs+=1

    return n_inputs,iter(x),iter(y),iter(orientation)



# CEBALERT: this kind of function probably exists somewhere already.

def get_matrix(matrix_file):
    """
    Returns an array containing the data in the specified C++ LISSOM .matrix
    file. 

    Ignores lines that start with a hash (#).
    """
    f = open(matrix_file)

    matrix = []
    
    for line in f.readlines():
        row = []
        
        if not line.startswith('#'):
            values = line.split()
            for v in values:
                row.append(float(v))
            matrix.append(row)
            
    # maybe should be setting a typecode of 'f', or maybe they should
    # actually be FixedPoint numbers...
    return array(matrix)



def compare_elements(topo_matrix,lissom_matrix,max_dp=8):
    """
    Return the smallest number of decimal places to which all
    corresponding elements of a C++ lissom and topographica matrix match.

    max_dp specifies the greatest number of decimal places to try.

    Returns -1 if they don't match to at least 1 decimal place.
    """
    # CB: this could be a general function, but I doubt anybody would use it.
    # Plus the hackalert below would have to be fixed.
    assert topo_matrix.shape == lissom_matrix.shape, "topographica and c++ matrices are different shapes"
    match_at=-1
    
    for dp in range(1,max_dp+1)[::-1]:
        # CBHACKALERT: aren't lissom_matrix values and topo_matrix values already floats?
        # Seems like whatever I do in get_matrix (e.g. use typecode='f'), unless I do astype(float)
        # here, the comparisons do not work properly. 
        if array_almost_equal(topo_matrix.astype(float),lissom_matrix.astype(float),dp):
            match_at = dp
            break
        
    return match_at
        


def check_weights(sheet_name,proj_name,unit,c_row_slice,c_col_slice):
    """
    Print the smallest number of decimal places to which all
    corresponding elements of the C++ lissom and Topographica weights
    of unit in proj_name (which projects into sheet_name) match.

    c_row_slice and c_col_slice specifiy where the weights are (C++ lissom
    does not situate weights in its .matrix files).
    """
    cTIME = "%06d"%long(topo.sim.time())
    cREGION = sheet_name
    cCONN = proj_name
    cUNIT = "%03d_%03d"%unit
    
    c_matrix_filename=filename_base+cTIME+'.wts.'+cREGION+'.'+cCONN+'.'+cUNIT+'.matrix'

    comparing_what = proj_name + " " + str(unit) + " t=" + str(topo.sim.time()) 

    topo_weights = topo.sim[sheet_name].projections()[proj_name].cf(*unit).weights
    c_weights = get_matrix(c_matrix_filename)[c_row_slice,c_col_slice]

    match_dp = compare_elements(topo_weights,c_weights)
    print comparing_what+" matched to "+`match_dp`+" d.p."
    # could return comparing_what & dp if that information is to be used for something else


def check_activities(sheet_name):
    """
    Print the smallest number of decimal places to which all
    corresponding elements of the C++ lissom and Topographica
    activities of sheet_name match.
    """
    cTIME = "%06d"%long(topo.sim.time())
    cREGION = sheet_name

    c_matrix_filename=filename_base+cTIME+'p000.'+cREGION+'_Activity.matrix'

    
    comparing_what = sheet_name + " activity t=" + str(topo.sim.time()) 

    topo_act = topo.sim[sheet_name].activity
    c_act = get_matrix(c_matrix_filename)

    match_dp = compare_elements(topo_act,c_act)
    print comparing_what+" matched to "+`match_dp`+" d.p."
    # could return comparing_what & dp if that information is to be used for something else
