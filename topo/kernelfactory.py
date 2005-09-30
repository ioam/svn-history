"""

Kernel Factory

Defines a class to return Kernels

There is a registry dictionary called
topo.kernelfactory.kernel_factories that stores the class name as key,
and a reference to the class definition as the value.  This dictionary
is used in the GUI Input Parameter Panel to dynamically generate the
list of valid KernelFactories that can be presented.  A user can
define a new subclass of KernelFactory anywhere, and then add an entry
to this dictionary, and the GUI will then add it to the list of
presentation types.

Kernel Matrix Orientations:

These kernels work closely with Sheets and have been written so that
the orientation of the kernel matrices have the same orientation
maintained by the Sheet classes.  Refer to sheet.py for a longer
discussion of the Topographica coordinate system.

For the purposes of this example, assume the goal is a Topographica
matrix that has a 1 at (-0.5,-0.5) a 3 at (0.0,0.0), and a 5 at
(0.5,0.5).  Put a different way,

the area from   -0.5,-0.5   to -0.5/3,-0.5/3 has value 1, 
the area from -0.5/3,-0.5/3 to  0.5/3,0.5/3  has value 3, and 
the area from  0.5/3,0.5/3  to    0.5,0.5    has value 5.

The matrix that would match the sheet coordinates describe above is:

  [[3 4 5]
   [2 3 4]
   [1 2 3]]

This matrix corresponds to a sheet with the value 1 in the Cartesian
plane area -0.5,-0.5 to -0.5/3,-0.5/3, etc.  NOTE: Accessing this
matrix using normal matrix notation will rarely yield reasonable
results.


$Id$
"""
### JABHACKALERT!
###
### Should eliminate all "import *" commands if at all possible.
### Is pprint used for anything?
import types
import base
from boundingregion import BoundingBox
from sheet import sheet2matrix, matrix2sheet, bounds2shape
from Numeric import *
from MLab import flipud,rot90
from parameter import * 
from patternfns import * 
from pprint import pprint,pformat
from math import pi
import topo.registry

### JABALERT!
###
### This class hierarchy (and file) should be renamed so that the
### meaning is more obvious.  What it does is to generate
### two-dimensional radial function patterns.  Convolution kernels are
### one such option, but only one; others are input patterns, initial
### weight patterns, etc.  So perhaps TwoDPattern, TwoDPatternFactory,
### and twodpattern.py might be better names; in any case we need
### something other than Kernel.


### JABHACKALERT!
### 
### The code from here to the end of ImageGenerator needs to be
### reworked into a proper KernelFactory for rendering images.

# Judah: The class ImageGenerator was originally written by Jeff, but
# now it should be replaced by a KernelFactory that will load in an
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
    would be to convert the ImageGenerator from a sheet to a factory
    function suitable for use with the InputSheet class (see
    inputsheet.py). 

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



def produce_kernel_matrices(bounds, density, r, c):
    """
    Get Kernel Matrices

    Sets up two vectors for the x and y values based on a bounds and density.
    The x and y vectors are lists of indexes at which to sample the kernel
    function.
    """       
    #left,bottom,right,top = bounds.aarect().lbrt()
    #bound_width  = right-left
    #bound_height = top-bottom
    linear_density = sqrt(density)

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

    kernel_y = array([matrix2sheet(r,0,bounds,density) for r in range(rows)])
    kernel_x = array([matrix2sheet(0,c,bounds,density) for c in range(cols)])
    assert len(kernel_x) == cols
    assert len(kernel_y) == rows
    return kernel_x[:,0], kernel_y[:,1]



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
### Need to clarify this comment; not clear which matrices are which (data or coordinates)
def produce_rotated_matrices(kernel_x, kernel_y, theta):
    """ Get Rotated matrices

    Takes in two Numeric /arrays/ that specify the x and y coordinates separately
    and a theta value, returns two Numeric matrices that have their coordinates
    rotated by that theta.

    The matrix itself is rotated to match the Topographica Cartesian
    coordinates.
    """

    new_kernel_x = subtract.outer(cos(pi-theta)*kernel_x, sin(pi-theta)*kernel_y)
    new_kernel_y = add.outer(sin(pi-theta)*kernel_x, cos(pi-theta)*kernel_y)

    new_kernel_x = flipud(rot90(new_kernel_x))
    new_kernel_y = flipud(rot90(new_kernel_y))
    return new_kernel_x, new_kernel_y


### JABHACKALERT!
### 
### KernelFactory should be renamed to PatternGenerator, and all
### the Factory classes should be named Generator instead. (The
### patterns are only sometimes kernels, and in python they are not
### quite like the C++/Java Factory design pattern; instead they are
### like generators.)

class KernelFactory(base.TopoObject):

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
        xm,ym = produce_kernel_matrices(bounds,density,rows,cols)
        self.kernel_x, self.kernel_y = produce_rotated_matrices(xm-x,ym-y,theta)


#########################################################
# Kernel Factory Objects
#
#

### JABHACKALERT!
###
### The variables x, y, etc. don't need to be declared in each of the
### Factory subclasses, and should be moved to KernelFactory once
### inputparamspanel.py is fixed.

class SolidFactory(KernelFactory):
    """
    Solid-color pattern generator.
    """
    x       = Number(default=0.0,softbounds=(-1.0,1.0))
    y       = Number(default=0.0,softbounds=(-1.0,1.0))

    def function(self,**params):
        return self.kernel_x*0+1

class GaussianFactory(KernelFactory):
    """
    Gaussian pattern generator
    """
    x       = Number(default=0.0,softbounds=(-1.0,1.0))
    y       = Number(default=0.0,softbounds=(-1.0,1.0))
    theta   = Number(default=0.0,softbounds=(0.0,2*pi))
    width   = Number(default=0.2,bounds=(0.0,None),softbounds=(0.0,1.0))
    height  = Number(default=0.2,bounds=(0.0,None),softbounds=(0.0,1.0))

    def function(self,**params):
        return gaussian( self.kernel_x, 
                         self.kernel_y, 
                         params.get('width',self.width), 
                         params.get('height',self.height)) 


class SineGratingFactory(KernelFactory):
    """
    Sine grating pattern generator
    """
    x       = Number(default=0.0,softbounds=(-1.0,1.0))
    y       = Number(default=0.0,softbounds=(-1.0,1.0))
    theta   = Number(default=0.0,softbounds=(0.0,2*pi))
    frequency = Number(default=5.0,bounds=(0.0,None),softbounds=(0.0,10.0))
    phase     = Number(default=pi/2,bounds=(0.0,None),softbounds=(0.0,2*pi))

    def function(self,**params):
        return sine_grating( self.kernel_x,
                             self.kernel_y,
                             params.get('frequency',self.frequency), 
                             params.get('phase',self.phase)) 


class SquareGratingFactory(KernelFactory):
    """
    Square grating pattern generator
    """
    x       = Number(default=0.0,softbounds=(-1.0,1.0))
    y       = Number(default=0.0,softbounds=(-1.0,1.0))
    theta   = Number(default=0.0,softbounds=(0.0,2*pi))
    frequency = Number(default=5.0,bounds=(0.0,None),softbounds=(0.0,10.0))
    phase     = Number(default=pi/2,bounds=(0.0,None),softbounds=(0.0,2*pi))

    def function(self,**params):
        return square_grating( self.kernel_x,
                             self.kernel_y,
                             params.get('frequency',self.frequency), 
                             params.get('phase',self.phase)) 


class GaborFactory(KernelFactory):
    """
    Gabor pattern generator
    """
    x       = Number(default=0.0,softbounds=(-1.0,1.0))
    y       = Number(default=0.0,softbounds=(-1.0,1.0))
    theta   = Number(default=0.0,softbounds=(0.0,2*pi))
    frequency = Number(default=5.0,bounds=(0.0,None),softbounds=(0.0,10.0))
    phase     = Number(default=pi/2,bounds=(0.0,None),softbounds=(0.0,2*pi))
    width   = Number(default=0.2,bounds=(0.0,None),softbounds=(0.0,1.0))
    height  = Number(default=0.2,bounds=(0.0,None),softbounds=(0.0,1.0))

    def function(self,**params):
        return gabor( self.kernel_x,
                      self.kernel_y,
                      params.get('width',self.width),
                      params.get('height',self.height),
                      params.get('frequency',self.frequency),
                      params.get('phase',self.phase))  

  
class UniformRandomFactory(KernelFactory):
    """
    Uniform random noise pattern generator
    """
    x       = Number(default=0.0,softbounds=(-1.0,1.0))
    y       = Number(default=0.0,softbounds=(-1.0,1.0))
    min     = Number(default=0.0,bounds=(0.0,1.0),softbounds=(0.0,1.0))
    max     = Number(default=1.0,bounds=(0.0,1.0),softbounds=(0.0,1.0))
    
    def function(self,**params):
        return uniform_random( self.kernel_x, self.kernel_y,
                               params.get('min',self.min),
                               params.get('max',self.max)) 


class RectangleFactory(KernelFactory):
    """
    Rectangle pattern generator
    """
    x       = Number(default=0.0,softbounds=(-1.0,1.0))
    y       = Number(default=0.0,softbounds=(-1.0,1.0))
    theta   = Number(default=0.0,softbounds=(0.0,2*pi))
    width   = Number(default=0.2,bounds=(0.0,None),softbounds=(0.0,1.0))
    height  = Number(default=0.2,bounds=(0.0,None),softbounds=(0.0,1.0))

    def function(self,**params):
        return rectangle( self.kernel_x, 
                          self.kernel_y, 
                          params.get('width',self.width),
                          params.get('height',self.height))  


class FuzzyLineFactory(KernelFactory):

    """
    Fuzzy Line Generating Factory
    """
    x       = Number(default=0.0,softbounds=(-1.0,1.0))
    y       = Number(default=0.0,softbounds=(-1.0,1.0))
    theta   = Number(default=0.0,softbounds=(0.0,2*pi))
    width   = Number(default=0.5,bounds=(0.0,None),softbounds=(0.0,1.0))
    height  = Number(default=0.2,bounds=(0.0,None),softbounds=(0.0,1.0))
    gaussian_width = Number(default=0.2,bounds=(0.0,None),softbounds=(0.0,1.0))
    
    def function(self,**params):
        return fuzzy_line( self.kernel_x, 
                           self.kernel_y,
                           params.get('width',self.width),
                           params.get('gaussian_width',self.gaussian_width))  


class FuzzyDiskFactory(KernelFactory):

    """
    Fuzzy disk pattern generator
    """
    x       = Number(default=0.0,softbounds=(-1.0,1.0))
    y       = Number(default=0.0,softbounds=(-1.0,1.0))
    theta   = Number(default=0.0,softbounds=(0.0,2*pi))
    width   = Number(default=0.5,bounds=(0.0,None),softbounds=(0.0,1.0))
    disk_radius  = Number(default=0.2,bounds=(0.0,None),softbounds=(0.0,1.0))
    gaussian_width = Number(default=0.2,bounds=(0.0,None),softbounds=(0.0,1.0))
    
    def function(self,**params):
        return fuzzy_disk( self.kernel_x, 
                           self.kernel_y, 
                           params.get('disk_radius',self.disk_radius), 
                           params.get('gaussian_width',self.gaussian_width))  
    


class FuzzyRingFactory(KernelFactory):
    """
    Fuzzy ring pattern generator
    """
    x       = Number(default=0.0,softbounds=(-1.0,1.0))
    y       = Number(default=0.0,softbounds=(-1.0,1.0))
    theta   = Number(default=0.0,softbounds=(0.0,2*pi))
    width   = Number(default=0.5,bounds=(0.0,None),softbounds=(0.0,1.0))
    disk_radius  = Number(default=0.2,bounds=(0.0,None),softbounds=(0.0,1.0))
    gaussian_width = Number(default=0.2,bounds=(0.0,None),softbounds=(0.0,1.0))


    def function(self,**params):
        return fuzzy_ring(self.kernel_x, 
                          self.kernel_y,
                          params.get('disk_radius',self.disk_radius),
                          params.get('width',self.width),
                          params.get('gaussian_width',self.gaussian_width))  
    

# Populate the KernelFactory registry:
if __name__ != '__main__':
    l = locals()
    for i in l.keys():
        if (type(l[i]) is type(KernelFactory)) \
               and issubclass(l[i],KernelFactory) \
               and i != 'KernelFactory':
            topo.registry.kernel_factories[i] = l[i]
