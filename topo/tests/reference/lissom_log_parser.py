# CEBHACKALERT: filename should change...



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


from Numeric import array
# CEBHACKALERT: this kind of function probably exists somewhere
# already. In any case, needs to print out meaningful errors.
from topo.commands.pylabplots import matrixplot

def get_matrix(matrix_file,dim,center=None):
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
            assert len(values)==dim[1], "Number of cols doesn't match expected value."
            for v in values:
                row.append(float(v))
            n_rows_read+=1
            matrix.append(row)

    assert n_rows_read==dim[0], "Number of rows doesn't match expected value."

    return array(matrix)

from math import ceil

def compare_elements(topo_matrix,lissom_matrix,dp,topo_matrix_name):
    """
    Go through the two matrices element-by-element and check for match
    to the specified number of decimal places (dp).
    """
    assert topo_matrix.shape == lissom_matrix.shape

    
    r,c = topo_matrix.shape

    matches=True
    
    for i in range(r):
        for j in range(c):
            # CEBHACKALERT: I think this is ok for testing the values match to the specified
            # number of dp, given that they are between 0 and 1.
            if abs(topo_matrix[i,j]-lissom_matrix[i][j])>10**-dp:
                matches=False
                print "\n" + topo_matrix_name + " element ("+str(i)+","+str(j)+") didn't match to " + str(dp) + " decimal places.\nTopographica value="+str(topo_matrix[i,j])+", C++ LISSOM value="+str(lissom_matrix[i,j])

    return matches



# CEBHACKALERT: these two functions now work in a really hacky way, because I've just changed them to
# expediate another task.
wt_dp=5
act_dp=5
plots=False

import topo
def compare_weights(c_matrix_filename,c_row_slice,c_col_slice,c_sheet_shape,unit,sheet,conn):

    comparing_what = conn + " " + str(unit) + " t=" + str(topo.sim.time()) 

    topo_weights = topo.sim[sheet].projections()[conn].cf(*unit).weights
    c_weights = get_matrix(c_matrix_filename,c_sheet_shape)[c_row_slice,c_col_slice] # c++ lissom doesn't situate weights  

    match = compare_elements(topo_weights,c_weights,wt_dp,comparing_what)

    if plots and not match:
        matrixplot(topo_weights,title="topo "+comparing_what)
        matrixplot(c_weights,title="c++ "+comparing_what)

    return {comparing_what:match}



def compare_activities(c_matrix_filename,c_sheet_shape,sheet):

    comparing_what = sheet + " activity, t=" + str(topo.sim.time()) 

    topo_act = topo.sim[sheet].activity
    c_act = get_matrix(c_matrix_filename,c_sheet_shape)

    match = compare_elements(topo_act,c_act,act_dp,comparing_what)

    if plots and not match:
        matrixplot(topo_act,title="topo "+comparing_what)
        matrixplot(c_act,title="c++ "+comparing_what)

    return {comparing_what:match}
