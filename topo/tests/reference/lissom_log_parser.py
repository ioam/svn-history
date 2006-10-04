# CEBHACKALERT: filename should change...

def get_input_params(log_file='or_map_topo.log'):
    """
    Return iterators over list of float values for C++ LISSOM's cx, cy, and theta.

    Expects log file with values held in lines like this:
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
def get_matrix(matrix_file,dim):
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

    return matrix
