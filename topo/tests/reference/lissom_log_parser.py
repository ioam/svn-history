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
            assert len(bits)==7, "Messed-up line?\n" + line

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

def compare_elements(topo_matrix,lissom_matrix):
    """
    Return a dictionary {dp:frac} where frac is the fraction of elements which match
    at the corresponding number of decimal places (dp).
    """
    assert topo_matrix.shape == lissom_matrix.shape

    diffs = abs(topo_matrix-lissom_matrix)
    n_elements=diffs.shape[0]*diffs.shape[1]
    
    fraction_matching = {}
    for dp in (9,8,7,6,5,4,3):
        # CEBHACKALERT: what's the best way to test for float equality to certain no. of dp?
        # This is unlikely to be correct in general.
        fraction_matching[dp] = sum(ravel(where(diffs<=10**-dp,ones(diffs.shape),zeros(diffs.shape))))/float(n_elements)

    return fraction_matching
        

def compare_weights(c_matrix_filename,c_row_slice,c_col_slice,c_sheet_side,unit,sheet,conn):

    comparing_what = conn + " " + str(unit) + " t=" + str(topo.sim.time()) 

    topo_weights = topo.sim[sheet].projections()[conn].cf(*unit).weights
    c_weights = get_matrix(c_matrix_filename,c_sheet_side)[c_row_slice,c_col_slice] # c++ lissom doesn't situate weights  

    zed = compare_elements(topo_weights,c_weights)

    return {comparing_what:zed}


def compare_activities(c_matrix_filename,c_sheet_side,sheet):

    comparing_what = sheet + " activity, t=" + str(topo.sim.time()) 

    topo_act = topo.sim[sheet].activity
    c_act = get_matrix(c_matrix_filename,c_sheet_side)

    zed = compare_elements(topo_act,c_act)

    return {comparing_what:zed}


