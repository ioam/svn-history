"""
Topographica bounding regions and boxes.

 $Id$
"""
import debug
import params
from Numeric import *

NYI = "Abstract method not implemented."

class BoundingRegion(debug.Debuggable):
    """
    Abstract bounding region class.  Should be subclassed
    """
    
    def __init__(self,**args):
        debug.Debuggable.__init__(self,**args)
        params.setup_params(self,BoundingRegion,**args)
    def contains(self,x,y):
        raise NYI
    def scale(self,xs,ys):
        raise NYI
    def translate(self,xoff,yoff):
        raise NYI
    def rotate(self,theta):
        raise NYI
    def aarect(self):
        raise NYI


class BoundingBox(BoundingRegion):
    """
    A rectangular bounding box defined by two points forming
    an axis-aligned rectangle.

    parameters:

    points = a sequence of two points that define an axis-aligned rectangle.
    """
    def __init__(self,**args):
        BoundingRegion.__init__(self,**args)
        params.setup_params(self,BoundingRegion,**args)
        
        self._aarect = AARectangle(*args['points'])

    def contains(self,x,y):
        left,bottom,right,top = self.aarect().lbrt()
        return (left <= x <= right) and (bottom <= y <= top)

    def aarect(self):
        return self._aarect


class BoundingEllipse(BoundingBox):
    """
    Similar to BoundingBox, but it the region is the ellipse
    inscribed within the rectangle.
    """
    def __init__(self,**args):
        BoundingBox.__init__(self,**args)
        params.setup_params(self,BoundingEllipse,**args)
        
    def contains(self,x,y):
        left,bottom,right,top = self.aarect().lbrt()
        xr = (right-left)/2.0
        yr = (top-bottom)/2.0
        xc = left + xr
        yc = bottom + yr

        xd = x-xc
        yd = y-yc

        return (xd**2/xr**2 + yd**2/yr**2) <= 1

class BoundingCircle(BoundingRegion):
    """
    A bounding circle.
    parameters:

    center = a single point (x,y)
    radius = a scalar radius
    """
    radius = 0.5
    center = (0.0,0.0)

    def __init__(self,**args):
        BoundingRegion.__init__(self,**args)
        params.setup_params(self,BoundingCircle,**args)    

    def contains(self,x,y):
        xc,yc = self.center
        xd = x-xc
        yd = y-yc
        return xd*xd + yd*yd <= self.radius*self.radius

    def aarect(self):
        xc,yc = self.center
        r = self.radius
        return AARectangle((xc-r,yc-r),(xc+r,yc+r))

inf = array(1)/0.0
class Unbounded(BoundingRegion):
    def __init__(self,**args):
        BoundingRegion.__init__(self,**args)
        params.setup_params(self,Unbounded,**args)
    def contains(self,x,y):
        return True
    def scale(self,xs,ys):
        pass
    def translate(self,xoff,yoff):
        pass
    def rotate(self,theta):
        pass
    def aarect(self):
        return AARectangle((-inf,-inf),(inf,inf))
      
        

class AARectangle:
    """
    Axis-aligned rectangle class.   Defines the smallest
    axis-aligned rectangle that encloses a set of points.

    usage:  aar = AARectangle( (x1,y1),(x2,y2), ... , (xN,yN) )
    """
    def __init__(self,*points):
        self.__top = max([y for x,y in points])
        self.__bottom = min([y for x,y in points])
        self.__left = min([x for x,y in points])
        self.__right = max([x for x,y in points])


    def top(self):
        """
        Return the y-coordinate of the top of the rectangle.
        """
        return self.__top
    def bottom(self):
        """
        Return the y-coordinate of the bottom of the rectangle.
        """
        return self.__bottom
    def left(self):
        """
        Return the x-coordinate of the left side of the rectangle.
        """
        return self.__left
    def right(self):
        """
        Return the x-coordinate of the right side of the rectangle.
        """
        return self.__right
    def lbrt(self):
        """
        Return (left,bottom,right,top) as a tuple
        """
        return (self.left(),
                self.bottom(),
                self.right(),
                self.top())

    def centroid(self):
        """
        Return the centroid of the rectangle.
        """
        left,bottom,right,top = self.lbrt()
        return (right+left)/2.0,(top+bottom)/2.0
    

        
        
