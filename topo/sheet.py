# $Id$

from simulator import EventProcessor
from params import Parameter
from Numeric import zeros,sqrt
from boundingregion import BoundingBox

def sheet2matrix(x,y,bounds,density):
    left,bottom,right,top = bounds.aarect().lbrt()
    width = right-left
    height = top-bottom
    linear_density = sqrt(density)
    rows = int(height*linear_density)
    cols = int(width*linear_density)

    col = (x-left) * linear_density
    row = (top-y)  * linear_density

    return int(row),int(col)
    
def matrix2sheet(row,col,bounds,density):
    left,bottom,right,top = bounds.aarect().lbrt()
    width = right-left
    height = top-bottom
    linear_density = sqrt(density)

    x = (col / linear_density) + left
    y = top - (row / linear_density)

    return x,y

def activation_submatrix(slice_bounds,activation,activation_bounds,density):
    """
    Gets a submatrix of an activation matrix defined by bounding rectangle.
    """
    r1,r2,c1,c2 = input_slice(slice_bounds,activation_bounds,density)

    return activation[r1:r2,c1:c2]

def input_slice(slice_bounds, input_bounds, input_density):
    """
    Gets the parameters for slicing an activation matrix given the slice bounds,
    activation bounds, and density of the activation matrix.

    returns a,b,c,d -- such that an activation matrix M
    can be sliced like this: M[a:b,c:d]
    
    """
    left,bottom,right,top = slice_bounds.aarect().lbrt()
    toprow,leftcol = sheet2matrix(left,top,input_bounds,input_density)
    bottomrow,rightcol = sheet2matrix(right,bottom,input_bounds,input_density)

    maxrow,maxcol = sheet2matrix(input_bounds.aarect().right(),
                                 input_bounds.aarect().bottom(),
                                 input_bounds,input_density)

    rstart = max(0,toprow)
    rbound = min(maxrow+1,bottomrow+1)
    cstart = max(0,leftcol)
    cbound = min(maxcol+1,rightcol+1)

    return rstart,rbound,cstart,cbound

    

class Sheet(EventProcessor):
    """
    The generic base class for neural sheets.

    This class handles the sheet's activity matrix, and it's
    coordinate frame.  It manages two sets of coordinates:

    _Sheet_coordinates_ are specified as (x,y) as on a normal
    cartesian graph; the positive y direction is upward, and the scale
    and origin are arbitrary, and specified by parameters.

    _Matrix_coordinates_ are the (row,col) specification for an
    element in the activation matrix.  The usual matrix coordinate
    specs apply.

    Parameters:

    bounds:   A BoundingBox object indicating the bounds of the sheet.
              [default  (-0.5,-0.5) to (0.5,0.5)]
    density:  The areal density of the sheet [default 100]
    
    """

    bounds  = Parameter(BoundingBox(points=((-0.5,-0.5),(0.5,0.5))))
    density = Parameter(100)

    def __init__(self,**params):

        super(Sheet,self).__init__(**params)

        linear_density = sqrt(self.density)

        left,bottom,right,top = self.bounds.aarect().lbrt()
        width,height = right-left,top-bottom
        rows = int(height*linear_density)
        cols = int(width*linear_density)
        self.activation = zeros((rows,cols)) + 0.0 

                
    def sheet2matrix(self,x,y):
        """
        Coordinate transformation: takes a point (x,y) in sheet
        coordinates and returns the (row,col) of the matrix cell it
        cooresponds to.
        """

        return sheet2matrix(x,y,self.bounds,self.density)

    def matrix2sheet(self,row,col):
        """
        Coordinate transformation: Takes the (row,col) of an element
        in the activity matrix and gives its (x,y) in sheet
        coordinates.
        """
        return matrix2sheet(row,col,self.bounds,self.density)

    def sheet_offset(self):
        """
        Returns the offset of the sheet origin from the lower-left
        corner of the sheet.
        """
        return -self.bounds.aarect().left(),-self.bounds.aarect().bottom()

    def sheet_rows(self):
        rows,cols = self.activation.shape
        coords = [self.matrix2sheet(r,0) for r in range(rows,0,-1)]
        return [y for (x,y) in coords]

    def sheet_cols(self):
        rows,cols = self.activation.shape
        coords = [self.matrix2sheet(0,c) for c in range(cols)]
        return [x for (x,y) in coords]

#####################################
from utils import NxN

class Composer(Sheet):
    """
    A Sheet that combines the activity of 2 or more other sheets into
    a single activity matrix.  When an activity matrix is received on
    an input port, it is added to the the sheet's input buffer
    according to the parameters of that port (see port_configure()
    below).  Then after a specified delay, the contents of the buffer
    are sent the sheet's outputs, and the buffer is cleared.

    Parameters:
      delay = (default 1.0) the time delay after receiving an input to
              send output.
    """

    delay = Parameter(1.0)

    def __init__(self,**config):
        super(Composer,self).__init__(**config)
        
        self.ports = {}
        self.timestamp = None

        if self.delay:
            self._connect_to(self,src_port='trigger_out',dest_port='trigger_in',delay=self.delay)

    def port_configure(self,port,**config):
        """
        Configure a specific input port.
        Port parameters:
           origin = (default (0,0)) The offset in the output matrix
                    where this port's input should be placed.
        """
        if not port in self.ports:
            self.ports[port] = {}

        for k,v in config.items():
            self.ports[port][k] = v
            

    def input_event(self,src,src_port,dest_port,data):
        if dest_port == 'trigger_in':
            self.send_output(data=self.activation)
            self.activation = zeros(self.activation.shape)+0.0
            return

        if self.simulator.time != self.timestamp:
            self.timestamp = self.simulator.time
            self.send_output(src_port='trigger_out')

        self.verbose("Received %s input from %s." % (NxN(data.shape),src))

        in_rows, in_cols = data.shape

        # compute the correct position of the input in the buffer
        start_row,start_col = self.sheet2matrix(*self.ports[dest_port]['origin'])
        row_adj,col_adj = src.sheet2matrix(0,0)

        self.verbose("origin (row,col) = "+`(start_row,start_col)`)
        self.verbose("adjust (row,col) = "+`(row_adj,col_adj)`)

        start_row -= row_adj
        start_col -= col_adj

        # the maximum bounds
        max_row,max_col = self.activation.shape

        self.verbose("max_row = %d, max_col = %d" % (max_row,max_col))
        self.verbose("in_rows = %d, in_cols = %d" % (in_rows,in_cols))

        end_row = start_row+in_rows
        end_col = start_col+in_cols

        # if the input goes outside the activation, clip it
        left_clip = -min(start_col,0)
        top_clip  = -min(start_row,0)
        right_clip = max(end_col,max_col) - max_col
        bottom_clip = max(end_row,max_row) - max_row

        start_col += left_clip
        start_row += top_clip
        end_col -= right_clip
        end_row -= bottom_clip

        self.verbose("start_row = %d,start_col = %d" % (start_row,start_col))
        self.verbose("end_row = %d,end_col = %d" % (end_row,end_col))
        self.verbose("left_clip = %d" % left_clip)
        self.verbose("right_clip = %d" % right_clip)
        self.verbose("top_clip = %d" % top_clip)
        self.verbose("bottom_clip = %d" % bottom_clip)
        self.message("activation shape = %s" % NxN(self.activation.shape))

        self.activation[start_row:end_row, start_col:end_col] += data[top_clip:in_rows-bottom_clip,
                                                                      left_clip:in_cols-right_clip]


if __name__ == '__main__':

    # test sheet2matrix
    s = Sheet()

    print 'sheet -> matrix'
    print (0,0), ' -> ', s.sheet2matrix(0,0)
    print (0,0.5), ' -> ', s.sheet2matrix(0,0.5)
    print (0.5,0), ' ->', s.sheet2matrix(0.5,0)
    print (0.5,0.5), ' -> ', s.sheet2matrix(0.5,0.5)


    print 'matrix -> sheet'
    print (0,0), ' -> ', s.matrix2sheet(0,0)
    print (0,100), ' -> ', s.matrix2sheet(0,100)
    print (100,0), ' ->', s.matrix2sheet(100,0)
    print (100,100), ' -> ', s.matrix2sheet(100,100)

