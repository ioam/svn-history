"""
A Sheet class for composing activation from different sheets into a
single activation matrix.

May not be necessary or useful any longer (as of 8/2005), and could
perhaps be moved to the examples/ directory, or deleted.

$Id$
"""

from topo.sheet import Sheet
from topo.utils import Struct, NxN


class Composer(Sheet):
    """
    A Sheet that combines the activity of 2 or more other sheets into
    a single activity matrix.  When connecting a sheet to a composer,
    you can specify the location at which that sheet's input will be
    mapped into the composer by adding the 'origin' argument to the
    connect() call e.g.:

    sim.connect(input_sheet,composer,delay=1, origin=(0.25,0.25))

    will cause (0,0) on input sheet's activation to map to (0.25,0.25)
    on composer's activation.

    """

    def __init__(self,**config):
        super(Composer,self).__init__(**config)        
        self.inputs = {}
        self.__dirty = False

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

    def _connect_from(self,src,src_port,dest_port,origin=(0,0)):
        self.inputs[(src.name,src_port)] = Struct(origin=origin)
    
    def pre_sleep(self):
        if self.__dirty:        
            self.send_output(data=self.activation) 
            self.activation = zeros(self.activation.shape)+0.0
            self.__dirty=False
           
    def input_event(self,src,src_port,dest_port,data):

        self.verbose("Received %s input from %s." % (NxN(data.shape),src))

        self.__dirty = True

        in_rows, in_cols = data.shape

        # compute the correct position of the input in the buffer
        start_row,start_col = self.sheet2matrix(*self.inputs[(src.name,src_port)].origin)
        row_adj,col_adj = src.sheet2matrix(0,0)

        self.debug("origin (row,col) = "+`(start_row,start_col)`)
        self.debug("adjust (row,col) = "+`(row_adj,col_adj)`)

        start_row -= row_adj
        start_col -= col_adj

        # the maximum bounds
        max_row,max_col = self.activation.shape

        self.debug("max_row = %d, max_col = %d" % (max_row,max_col))
        self.debug("in_rows = %d, in_cols = %d" % (in_rows,in_cols))

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

        self.debug("start_row = %d,start_col = %d" % (start_row,start_col))
        self.debug("end_row = %d,end_col = %d" % (end_row,end_col))
        self.debug("left_clip = %d" % left_clip)
        self.debug("right_clip = %d" % right_clip)
        self.debug("top_clip = %d" % top_clip)
        self.debug("bottom_clip = %d" % bottom_clip)
        self.debug("activation shape = %s" % NxN(self.activation.shape))

        self.activation[start_row:end_row, start_col:end_col] += data[top_clip:in_rows-bottom_clip,
                                                                      left_clip:in_cols-right_clip]


