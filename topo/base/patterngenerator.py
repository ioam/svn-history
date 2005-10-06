"""

Pattern Generator

Defines a class to return Patterns

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

$Id$
"""
### JABHACKALERT!
###
### Should eliminate all "import *" commands if at all possible.
import types
from object import TopoObject
from boundingregion import BoundingBox
from sheet import sheet2matrix, matrix2sheet, bounds2shape
from Numeric import *
from MLab import flipud,rot90
from parameter import Parameter,Number
from math import pi
import registry

### JABHACKALERT!
### 
### The code from here to the end of ImageGenerator needs to be
### reworked into a proper PatternGenerator for rendering images.

# Judah: The class ImageGenerator was originally written by Jeff, but
# now it should be replaced by a PatternGenerator that will load in an
# input file.  Currently (9/05) only used by cfsom.py and a couple of
# test files.
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
        max_val = float(max(max(self.activity)))
        self.activity = self.activity / max_val


    def start(self):
        self.send_output(data=self.activity)

    def input_event(self,src,src_port,dest_port,data):
        self.send_output(data=self.activity)



### JABHACKALERT!
### 
### This should presumably be a private method of PatternGenerator.
def produce_pattern_matrices(bounds, density, r, c):
    """
    Generate vectors representing coordinates at which the pattern will be sampled.

    Sets up two vectors for the x and y values based on a bounds and density.
    The x and y vectors are lists of indexes at which to sample the pattern
    function.
    """       
    if r == 0 and c == 0:
        rows,cols = bounds2shape(bounds,density)
    else:
        rows = r
        cols = c
    
    ### JABHACKALERT!
    ### 
    ### We must fix these things:
    ### 
    # TODO: this can generate output that may be off by one in terms of size,
    # for example most times this generates a 100x100 image, but sometimes
    # it generates a 101x100 
    # TODO: Use sheet operations defined in sheet.py? I think we already
    # do...

    pattern_y = array([matrix2sheet(r,0,bounds,density) for r in range(rows)])
    pattern_x = array([matrix2sheet(0,c,bounds,density) for c in range(cols)])
    assert len(pattern_x) == cols
    assert len(pattern_y) == rows
    return pattern_x[:,0], pattern_y[:,1]



### JABHACKALERT!
### 
### Instead of theta, any user-visible parameter should have a
### readable name like "orientation" or "angle" (which is shorter but
### not precisely correct).
### 
### JBD: This should be implemented in concert with changes to
### inputparamspanel.py to make a dynamic parameter list.  Now (9/05)
### the Python variable name must be the name displayed to the
### InputParamsPanel sliders.

### JABHACKALERT!
### 
### Why do the matrices need to be "rotated to match the Topographica
### Cartesian coordinates"? Is that why a line or grating of zero degrees
### points upwards instead of to the right?  
### 
### This should presumably be a private method of PatternGenerator.
def transform_coordinates(pattern_x, pattern_y, orientation):
    """
    Rotates and translates the given matrix coordinates.

    Accepts Numeric matrices specifing the x and y coordinates
    (separately), along with an orientation value.  Returns two Numeric
    matrices of the same shape, but with the coordinate values translated
    and rotated to have the specified origin and orientation.

    Each matrix is also rotated to match the Topographica Cartesian
    coordinates.
    """

    new_pattern_x = subtract.outer(cos(pi-orientation)*pattern_x, sin(pi-orientation)*pattern_y)
    new_pattern_y = add.outer(sin(pi-orientation)*pattern_x, cos(pi-orientation)*pattern_y)

    new_pattern_x = flipud(rot90(new_pattern_x))
    new_pattern_y = flipud(rot90(new_pattern_y))
    return new_pattern_x, new_pattern_y


class PatternGenerator(TopoObject):

    bounds  = Parameter(default=BoundingBox(points=((-0.5,-0.5), (0.5,0.5))))
    density = Parameter(default=10000)

    theta = Parameter(default=0)

    def __call__(self,**params):
        self.verbose("params = ",params)
        self.setup_xy(params.get('bounds',self.bounds),
                      params.get('density',self.density),
                      params.get('x', self.x),
                      params.get('y',self.y),
                      params.get('theta',self.theta),
                      params.get('rows',0),
                      params.get('cols',0))
        return self.function(**params)

    def setup_xy(self,bounds,density,x,y,theta,rows,cols):
        self.verbose("bounds = ",bounds,"density =",density,"x =",x,"y=",y)
        xm,ym = produce_pattern_matrices(bounds,density,rows,cols)
        self.pattern_x, self.pattern_y = transform_coordinates(xm-x,ym-y,theta)


### JABHACKALERT!
###
### The variables x, y, etc. don't need to be declared in each of the
### Generator subclasses (here and elsewhere), and should be moved to
### PatternGenerator once inputparamspanel.py is fixed.

# Trivial example of a PatternGenerator, provided for when a default is
# needed.  The other specific PatternGenerator classes are stored in
# patterns/, to be imported as needed.
class SolidGenerator(PatternGenerator):
    """
    Solid pattern generator, i.e. a uniform field of the same value.
    """
    x       = Number(default=0.0,softbounds=(-1.0,1.0))
    y       = Number(default=0.0,softbounds=(-1.0,1.0))

    def function(self,**params):
        return ones(self.pattern_x.shape, Float)

# Register this PatternGenerator for public use.
registry.pattern_generators['SolidGenerator']=SolidGenerator

