# CEBHACKALERT: filename should change...
import topo

from Numeric import ones,zeros,where,ravel,sum,array

from topo.commands.pylabplots import matrixplot



def get_input_params(log_file='or_map_topo.log'):
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



# CEBHACKALERT: this kind of function probably exists somewhere
# already. In any case, needs to print out meaningful errors.

def get_matrix(matrix_file,side_length,center=None):
    """
    Returns an array containing the data in the specified C++ LISSOM .matrix
    file. The dimensions of the array must match those specified in
    dim=(rows,cols)  (to ensure that the matrix is the size you expect).

    Ignores lines that start with a hash (#).
    """
    f = open(matrix_file)

    n_rows_read = 0

    matrix = []
    
    for line in f.readlines():
        row = []
        
        if not line.startswith('#'):
            values = line.split()
            assert len(values)==side_length, "Number of cols doesn't match expected value."
            for v in values:
                row.append(float(v))
            n_rows_read+=1
            matrix.append(row)

    assert n_rows_read==side_length, "Number of rows doesn't match expected value."

    return array(matrix)


# CB: simplify these three functions when it's clear what is useful to know.

from topo.tests.utils import array_almost_equal

def compare_elements(topo_matrix,lissom_matrix,max_dp=8):
    """
    Return the smallest number of decimal places to which all corresponding elements of the two arrays match.

    max_dp specifies the greatest number of decimal places to try.

    Returns -1 if they don't match to at least 1 decimal place. (CB: Because I don't want to
    fix the functions in topo.tests.utils - they probably exist in numpy.)
    """
    assert topo_matrix.shape == lissom_matrix.shape, "topographica and c++ matrices are different shapes; did you take the right slice of the c++ matrix?"

    match_at=-1
    
    for dp in range(1,max_dp+1)[::-1]:
        # CBHACKALERT: aren't lissom_matrix values and topo_matrix values already floats?
        # Seems like whatever I do in get_matrix (e.g. use typecode='f'), unless I do astype(float)
        # here, the comparisons do not work properly. 
        if array_almost_equal(topo_matrix.astype(float),lissom_matrix.astype(float),dp):
            match_at = dp
            break
        
    return match_at
        

def compare_weights(c_matrix_filename,c_row_slice,c_col_slice,c_sheet_side,unit,sheet,conn):
    """

    - slices (not nec. square, lissom doesn't situate)
    """
    comparing_what = conn + " " + str(unit) + " t=" + str(topo.sim.time()) 

    topo_weights = topo.sim[sheet].projections()[conn].cf(*unit).weights
    c_weights = get_matrix(c_matrix_filename,c_sheet_side)[c_row_slice,c_col_slice] # c++ lissom doesn't situate weights  

    match_dp = compare_elements(topo_weights,c_weights)
    print comparing_what+" matched to "+`match_dp`+" d.p."
    # comparing_what & dp if that information is to be used for something else


def compare_activities(c_matrix_filename,c_sheet_side,sheet):

    comparing_what = sheet + " activity, t=" + str(topo.sim.time()) 

    topo_act = topo.sim[sheet].activity
    c_act = get_matrix(c_matrix_filename,c_sheet_side)

    match_dp = compare_elements(topo_act,c_act)
    print comparing_what+" matched to "+`match_dp`+" d.p."
    # comparing_what & dp if that information is to be used for something else


