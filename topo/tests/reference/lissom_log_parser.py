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


from Numeric import array
# CEBHACKALERT: this kind of function probably exists somewhere
# already. In any case, needs to print out meaningful errors.
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
            t_value = round(topo_matrix[i,j],dp)
            l_value = round(lissom_matrix[i][j],dp)
            # CEBHACKALERT: should be an assert statement
            if t_value != l_value:
                matches=False
                print "\n" + topo_matrix_name + " element ("+str(i)+","+str(j)+") didn't match to " + str(dp) + " decimal places.\nTopographica value="+str(t_value)+", C++ LISSOM value="+str(l_value)

    return matches
