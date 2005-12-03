"""

Pattern Generator

Defines a class to return Patterns

CEBHACKALERT: update this when finished reorganizing parametersframe.py

There is a registry dictionary called
registry.pattern_generators that stores the class name as key,
and a reference to the class definition as the value.  This dictionary
is used in the GUI Input Parameter Panel to dynamically generate the
list of valid PatternGenerators that can be presented.  A user can
define a new subclass of PatternGenerator anywhere, and then add an entry
to this dictionary, and the GUI will then add it to the list of
presentation types.

Pattern Matrix Orientations:

These patterns work closely with Sheets and have been written so that
the orientation of the pattern matrices have the same orientation
maintained by the Sheet classes.  Refer to sheet.py for a longer
discussion of the Topographica coordinate system.



    Additionally, this module defines precedences
    SC_PREC, OF_PREC, OR_PREC, X_PREC, Y_PREC
    which can be used by subclasses that override one of the standard Parameters
    (x,y,orientation,scale,offset) and wish to maintain the same order should any changes
    be made to the precedences here.


$Id$
"""
__version__='$Revision$'

from topoobject import TopoObject
from boundingregion import BoundingBox
from sheet import  matrixidx2sheet, bounds2shape
from Numeric import add,subtract,cos,sin,array
from parameter import Parameter,Number
from math import pi

### JABHACKALERT!
### 
### The code from here to the end of ImageGenerator needs to be
### reworked into a proper PatternGenerator for rendering images.

# Judah: The class ImageGenerator was originally written by Jeff, but
# now it should be replaced by a PatternGenerator that will load in an
# input file.  Currently (9/05) only used by cfsom.py and a couple of
# test files.
from Numeric import resize #this class also requires "array" but is about
                           #to be removed, and "array" is imported above
from sheet import Sheet
from simulator import EventProcessor
from utils import NxN
from pprint import *
import Image, ImageOps
class ImageGenerator(Sheet):
    """

    parameters:

      filename = The path to the image file.

    A sheet that reads a pixel map and uses it to generate an activity
    matrix.  The image is converted to grayscale and scaled to match
    the bounds and density of the sheet.

    NOTE: A bare ImageGenerator only sends a single event, containing
    its image when it gets the .start() call, to repeatedly generate
    images, it must have a self-connection.  More elegant, however,
    would be to convert the ImageGenerator from a sheet to a generator
    function suitable for use with the GeneratorSheet class (see
    topo/sheets/generatorsheet.py). 

    """
    filename = Parameter(None)
    
    def __init__(self,**config):

        super(ImageGenerator,self).__init__(**config)

        self.verbose("filename = " + self.filename)

        image = Image.open(self.filename)
        image = ImageOps.grayscale(image)
        image = image.resize(self.activity.shape)
        self.activity = resize(array([x for x in image.getdata()]),
                                 (image.size[1],image.size[0]))

	self.verbose("Initialized %s activity from %s" % (NxN(self.activity.shape),self.filename))
        max_val = float(max(self.activity.flat))
        self.activity = self.activity / max_val


    def start(self):
	assert self.simulator
	self.simulator.enqueue_event_rel(0,self,self,data=self.activity)

    def input_event(self,src,src_port,dest_port,data):
        self.send_output(data=self.activity)


# precedence constants for ordering
# scale,offset,orientation,x,y
SC_PREC = 0.8
OF_PREC = 0.81
OR_PREC = 0.89
X_PREC = 0.9
Y_PREC = 0.91

class PatternGenerator(TopoObject):
    """

    A PatternGenerator's Parameters can make use of Parameter's precedence attribute
    to specify the order in which they should appear e.g. on a GUI. The precedence
    attribute is based on the range 0.0 to 1.0, with ordering going from 0.0 (first)
    to 1.0 (last).    
    """

    bounds  = Parameter(default=BoundingBox(points=((-0.5,-0.5), (0.5,0.5))),hidden=True)
    density = Parameter(default=10000,hidden=True)

    x       = Number(default=0.0,softbounds=(-1.0,1.0),precedence=X_PREC)
    y       = Number(default=0.0,softbounds=(-1.0,1.0),precedence=Y_PREC)
    orientation = Number(default=0,softbounds=(0.0,2*pi),precedence=OR_PREC)
    scale = Number(default=1.0,softbounds=(0.0,2.0),precedence=SC_PREC)
    offset = Number(default=0.0,softbounds=(-1.0,1.0),precedence=OF_PREC)

    def __call__(self,**params):
        """
        # CEBHACKALERT: I still have documentation to write, including explaining
        params.get().

        Sometimes rows and cols are already known before the PatternGenerator is called, so
        we can just provide this information without having them recomputed. And sometimes
        rows and cols are not found by simply calling bound2shape() so we need to pass them in
	(e.g. see ConnectionField.init()).
        """
        self.verbose("params = ",params)
        self.__setup_xy(params.get('bounds',self.bounds),
                        params.get('density',self.density),
                        params.get('x', self.x),
                        params.get('y',self.y),
                        params.get('orientation',self.orientation),
                        params.get('rows',0),
                        params.get('cols',0))
        return self.scale*self.function(**params)+self.offset

    def __setup_xy(self,bounds,density,x,y,orientation,rows,cols):
        """
        Produce the pattern matrices from the bounds and density (or rows and cols), and transform according
        to x,y, and orientation.
        """
        self.verbose("bounds = ",bounds,"density =",density,"x =",x,"y=",y)
        x_points,y_points = self.__produce_sampling_vectors(bounds,density,rows,cols)
        self.pattern_x, self.pattern_y = self.__create_and_rotate_coordinates(x_points-x,y_points-y,orientation)

    def function(self,**params):
        """
        Subclasses will typically implement this function to draw a pattern.

        The pattern will then be scaled and rotated automatically by __call__.
        Alternatively, this function may be omitted and __call__ reimplemented,
        e.g. if the automatic scaling and rotating is not appropriate.
        """
        raise NotImplementedError


    def __produce_sampling_vectors(self, bounds, density, r, c):
        """
        Generate vectors representing coordinates at which the pattern will be sampled.

        x is a 1d-array of x-axis values at which to sample the pattern;
        y contains the y-axis values.

        Both contain smaller to larger values from left to right, i.e. they follow Cartesian convention.
        """       
        if r == 0 and c == 0:
            rows,cols = bounds2shape(bounds,density)
        else:
            rows = r
            cols = c

        y = array([matrixidx2sheet(r,0,bounds,density) for r in range(rows)])
        x = array([matrixidx2sheet(0,c,bounds,density) for c in range(cols)])

        y = y[::-1,1]
        x = x[:,0]

        assert len(x) == cols
        assert len(y) == rows

        return x, y

    def __create_and_rotate_coordinates(self, x, y, orientation):
        """
        Creates pattern matrices from x and y vectors, and rotates them to the specified orientation.
        """
        pattern_y = subtract.outer(-cos(orientation)*y, sin(orientation)*x)
        pattern_x = add.outer(-sin(orientation)*y, cos(orientation)*x)

        return pattern_x, pattern_y


# Trivial example of a PatternGenerator, provided for when a default is
# needed.  The other concrete PatternGenerator classes are stored in
# patterns/, to be imported as needed.
from Numeric import ones, Float

class ConstantGenerator(PatternGenerator):
    """Constant pattern generator, i.e. a solid, uniform field of the same value."""

    # The standard x, y, and orientation variables are currently ignored,
    # so they aren't shown in auto-generated lists of parameters (e.g. in the GUI)
    x       = Number(hidden = True)
    y       = Number(hidden = True)
    orientation   = Number(hidden = True)

    # Optimization: We use a simpler __call__ method here to skip the
    # coordinate transformations (which would have no effect anyway)
    def __call__(self,**params):
        r = params.get('rows',0)
	c = params.get('cols',0)

        if r == 0 and c == 0:
            r,c = bounds2shape(params.get('bounds',self.bounds),
                               params.get('density',self.density))
        return self.scale*ones((r,c), Float)+self.offset




