"""
Functions for getting C++ LISSOM data and comparing them
with Topographica's.

Before using these functions, you should set filename_base to
give the base filename path of the C++ LISSOM files, e.g.
'topo/tests/reference/or_map_topo.'

$Id$
"""
__version__='$Revision$'

# CEBHACKALERT: filename should change

from math import pi, atan2
from numpy import array
import topo
from topo.tests.utils import array_almost_equal


filename_base = ""


def sign(x): return 1 if x>=0 else -1

import re
def get_input_params():
    """

    Return iterators over list of float values for C++ LISSOM's cx,
    cy, and theta for multiple eyes, as well as sign.


    Expects log file with values held in lines like this::
    
      'Iteration: 000000  [Eye0 [Obj0 cx:02.1 cy:11.6 theta:074.0]]\n'

    or this:
    
      'Iteration: 000000  [Eye0 [Obj0 cx:23.4 cy:10.0 theta:059.6]]  [Eye1 [Obj0 cx:22.6 cy:10.5 theta:059.6]]  [Eye2 [Obj0 cx:21.7 cy:11.1 theta:059.6]]  [Eye3 [Obj0 cx:20.8 cy:11.6 theta:059.6]]\n'
      
    """
    f = open(filename_base+'log','r')

    # first iter is test in c++ lissom; use to get num eyes
    n_eyes = len(f.readline().split('Eye')[1::])

    input_params = dict([(i,dict(cx=list(),cy=list(),theta=list(),sign=list()))
                         for i in range(n_eyes)])

    # supposed to match numbers like 02.1, 074.0 etc
    val_match = re.compile(r'([0-9]([0-9]|\.)+)+')

    lines = f.readlines()                 
    for line,lineno in zip(lines,range(len(lines))):
        eyes = line.split('Eye')[1::]
        for eye,i in zip(eyes,range(n_eyes)):
            cx,cy,theta = [float(val[0]) for val in val_match.findall(eye)]
            input_params[i]['cx'].append(cx)
            input_params[i]['cy'].append(cy)
            input_params[i]['theta'].append(theta)

        ### get sign (is there an easier way?)
        if len(eyes)>1: # CeBALERLT: not general (assuming motion just because more than 1 eye)
            realDx = input_params[1]['cx'][lineno]-input_params[0]['cx'][lineno]
            realDy = input_params[1]['cy'][lineno]-input_params[0]['cy'][lineno]
            realtheta = 180*(atan2(realDy,realDx)/pi)
            theta = input_params[0]['theta'][lineno]
            for i in range(n_eyes):
                input_params[i]['sign'].append(sign(theta)/sign(realtheta))
        ###
        
    for i in input_params:
        for val in input_params[i]:
            input_params[i][val] = iter(input_params[i][val])

    return len(lines),input_params



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
    assert topo_matrix.shape == lissom_matrix.shape, "topographica array shape %s, but c++ matrix shape %s"%(topo_matrix.shape,lissom_matrix.shape)
    match_at=-1
    
    for dp in range(1,max_dp+1)[::-1]:
        # CBHACKALERT: aren't lissom_matrix values and topo_matrix values already floats?
        # Seems like whatever I do in get_matrix (e.g. use typecode='f'), unless I do astype(float)
        # here, the comparisons do not work properly. 
        if array_almost_equal(topo_matrix.astype(float),lissom_matrix.astype(float),dp):
            match_at = dp
            break
        
    return match_at
        


def check_weights(sheet_name,proj_name,unit,c_row_slice,c_col_slice,required_dp=6):
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

    if required_dp>0:
        assert match_dp>=required_dp, "Required match to %s d.p. but got %s d.p."%(required_dp,match_dp)


def check_activities(sheet_name,required_dp=5):
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

    if required_dp>0:
        assert match_dp>=required_dp, "Required match to %s d.p. but got %s d.p."%(required_dp,match_dp)
