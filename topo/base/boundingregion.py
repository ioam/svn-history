"""
Bounding regions and bounding boxes.

$Id$
"""

__version__='$Revision$'

from numpy import inf

### JABALERT: The aarect information should probably be rewritten in
### matrix notation, not list notation, so that it can be scaled,
### translated, etc. easily.
###
from parameterizedobject import ParameterizedObject, Parameter
from parameterclasses import Number

class BoundingRegion(ParameterizedObject):
    """
    Abstract bounding region class, for any portion of a 2D plane.

    Only subclasses can be instantiated directly.
    """
    _abstract_class_name = "BoundingRegion"
    
    def __init__(self,**args):
        super(BoundingRegion,self).__init__(**args)
    def contains(self,x,y):
        raise NotImplementedError
    def scale(self,xs,ys):
        raise NotImplementedError
    def translate(self,xoff,yoff):
        l,b,r,t = self.aarect().lbrt()
        self._aarect = AARectangle((l+xoff,b+yoff),(r+xoff,t+yoff))
    def rotate(self,theta):
        raise NotImplementedError
    def aarect(self):
        raise NotImplementedError
    def centroid(self):
        """
        Return the coordinates of the center of this BoundingBox
        """        
        return self.aarect().centroid()

class BoundingBox(BoundingRegion):
    """
    A rectangular bounding box defined either by two points forming
    an axis-aligned rectangle (or simply a radius for a square).
    """
    def __str__(self):
        """
        Return BoundingBox(points=((left,bottom),(right,top)))

        Reimplemented here so that 'print' for a BoundingBox
        will display the bounds.
        """
        l,b,r,t = self._aarect.lbrt()
        if r == -l and t == -b and r == t:
            return 'BoundingBox(radius=%s)'%(r)
        else:
            return 'BoundingBox(points=((%s,%s),(%s,%s)))'%(l,b,r,t)

    def script_repr(self,imports=[],prefix="    "):
        # Generate import statement
        cls = self.__class__.__name__
        mod = self.__module__
        imports.append("from %s import %s" % (mod,cls))
        return self.__str__()

    def __init__(self,**args):
        """
        Create a BoundingBox.

        Either 'radius' or 'points' can be specified for the
        AARectangle.

        If radius is passed in, the BoundingBox will use min_radius
        (which defaults to 0.0) if it's larger than radius - so by
        passing min_radius=1.25/density, a BoundingBox of at least 3x3
        matrix units can be guaranteed.

        If neither radius nor points is passed in, create a default
        AARectangle defined by (-0.5,-0.5),(0.5,0.5).
        """
        # if present, 'radius', 'min_radius', and 'points' are deleted from
        # args before they're passed to the superclass (because they
        # aren't parameters to be set)
        if 'radius' in args:
            radius = args['radius']
            del args['radius']

            if 'min_radius' in args:
                min_radius = args['min_radius']
                del args['min_radius']
            else:
                min_radius = 0.0

            r=max(radius,min_radius)
            self._aarect=AARectangle((-r,-r),(r,r))
                
        elif 'points' in args:
            self._aarect = AARectangle(*args['points'])
            del args['points']
        else:
            self._aarect = AARectangle((-0.5,-0.5),(0.5,0.5))

        super(BoundingBox,self).__init__(**args)        


    def contains(self,x,y):
        """
        Returns true if the given point is contained within the
        bounding box, where all boundaries of the box are
        considered to be inclusive.
        """
        left,bottom,right,top = self.aarect().lbrt()
        return (left <= x <= right) and (bottom <= y <= top)

    def contains_exclusive(self,x,y):
        """
        Return True if the given point is contained within the
        bounding box, where the bottom and right boundaries are
        considered exclusive.
        """
        left,bottom,right,top = self.aarect().lbrt()
        return (left <= x < right) and (bottom < y <= top)



    def containsbb_exclusive(self,x):
        """
        Returns true if the given BoundingBox x is contained within the
        bounding box, where at least one of the boundaries of the box has
        to be exclusive.
        """
        left,bottom,right,top = self.aarect().lbrt()
        leftx,bottomx,rightx,topx = x.aarect().lbrt()
        return (left <= leftx) and (bottom <= bottomx) and (right >= rightx) and (top >= topx) and (not ((left == leftx) and (bottom == bottomx) and (right == rightx) and (top == topx)))

    def containsbb_inclusive(self,x):
        """
        Returns true if the given BoundingBox x is contained within the
        bounding box, including cases of exact match.
        """
        left,bottom,right,top = self.aarect().lbrt()
        leftx,bottomx,rightx,topx = x.aarect().lbrt()
        return (left <= leftx) and (bottom <= bottomx) and (right >= rightx) and (top >= topx)

    def upperexclusive_contains(self,x,y):
        """
        Returns true if the given point is contained within the
        bounding box, where the right and upper boundaries
        are exclusive, and the left and lower boundaries are
        inclusive.  Useful for tiling a plane into non-overlapping
        regions.
        """
        left,bottom,right,top = self.aarect().lbrt()
        return (left <= x < right) and (bottom <= y < top)

    def aarect(self):
        return self._aarect

    def lbrt(self):
        """
        return left,bottom,right,top values for the BoundingBox.
        """
        return self._aarect.lbrt()



class Cartesian2DPoint(Parameter):
    """
    Parameter whose value represents a point in a 2D Cartesian plane.
    """
    ### JABALERT: Should accept and respect a BoundingBox bounds.
    __slots__ = []
    __doc__ = property((lambda self: self.doc))

    def __set__(self,obj,val):
        try: ## Test that it is a 2-tuple
            (x,y) = val 
            super(Cartesian2DPoint,self).__set__(obj,val)
        except:
            raise ValueError("Parameter must be a 2D point (an x,y tuple).")


class BoundingEllipse(BoundingBox):
    """
    Similar to BoundingBox, but the region is the ellipse
    inscribed within the rectangle.
    """
    def __init__(self,**args):
        super(BoundingEllipse,self).__init__(**args)
        
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
    A circular BoundingRegion.

    Takes parameters center (a single 2D point (x,y)) and radius (a
    scalar radius).
    """
    radius = Number(0.5,bounds=(0.0,None))
    center = Cartesian2DPoint((0.0,0.0))

    def __init__(self,**args):
        super(BoundingCircle,self).__init__(**args)

    def contains(self,x,y):
        xc,yc = self.center
        xd = x-xc
        yd = y-yc
        return xd*xd + yd*yd <= self.radius*self.radius

    def aarect(self):
        xc,yc = self.center
        r = self.radius
        return AARectangle((xc-r,yc-r),(xc+r,yc+r))

class Unbounded(BoundingRegion):
    def __init__(self,**args):
        super(Unbounded,self).__init__(**args)
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
    def centroid(self):
        return 0.0,0.0


### This class is valid only for BoundingBoxes, because it
### only deals with the aarect(), ignoring arbitrarily shaped
### BoundingRegions.  To be a real Intersection(BoundingRegion) class,
### it would need to have a contains() function that computes a
### logical AND of the contains() for each of the regions supplied.
### Scale, rotate, and translate would also need to be applied to the
### individual regions each time.
### Could be simpler to write this as a function, because it just
### ends up with a simple BoundingBox after construction.
class BoundingBoxIntersection(BoundingBox):
    """A BoundingBox initialized as the intersection of the supplied list of BoundingBoxes."""
    
    def __init__(self,*boxes,**params):
        """
        Given a list of BoundingBoxes, computes a new BoundingBox that is
        the intersection of all of the supplied boxes.
        """
        super(BoundingBoxIntersection,self).__init__(**params)

        bounds = [r.aarect().lbrt() for r in boxes]
        left = max([l for (l,b,r,t) in bounds])
        bottom = max([b for (l,b,r,t) in bounds])
        right = min([r for (l,b,r,t) in bounds])
        top = min([t for (l,b,r,t) in bounds])

        # JABALERT: Why is this one __aarect, and BoundingBox
        # _aarect?  Probably should change this one to _aarect and
        # eliminate aarect(self).
        self.__aarect = AARectangle((left,bottom),(right,top))

    def aarect(self):
        return self.__aarect


# JABALERT: Should probably remove top, bottom, etc. accessor functions,
# and use the slot itself instead.
###################################################
class AARectangle(object):
    """
    Axis-aligned rectangle class.

    Defines the smallest axis-aligned rectangle that encloses a set of
    points.

    Usage:  aar = AARectangle( (x1,y1),(x2,y2), ... , (xN,yN) )
    """
    __slots__ = ['_left','_bottom','_right','_top']
    def __init__(self,*points):
        self._top = max([y for x,y in points])
        self._bottom = min([y for x,y in points])
        self._left = min([x for x,y in points])
        self._right = max([x for x,y in points])

    # Basic support for pickling
    def __getstate__(self):
        state={}
        try: 
            for k in self.__slots__:
                state[k] = getattr(self,k)
        except AttributeError:
            pass
        return state

    def __setstate__(self,state):
        for k,v in state.items():
            setattr(self,k,v)
        self.unpickle()

    def unpickle(self):
        pass

    def top(self):
        """
        Return the y-coordinate of the top of the rectangle.
        """
        return self._top
    def bottom(self):
        """
        Return the y-coordinate of the bottom of the rectangle.
        """
        return self._bottom
    def left(self):
        """
        Return the x-coordinate of the left side of the rectangle.
        """
        return self._left
    def right(self):
        """
        Return the x-coordinate of the right side of the rectangle.
        """
        return self._right
    def lbrt(self):
        """
        Return (left,bottom,right,top) as a tuple
        """
        return (self._left,
                self._bottom,
                self._right,
                self._top)

    def centroid(self):
        """
        Return the centroid of the rectangle.
        """
        left,bottom,right,top = self.lbrt()
        return (right+left)/2.0,(top+bottom)/2.0
    

    def intersect(self,other):

        l1,b1,r1,t1 = self.lbrt()
        l2,b2,r2,t2 = other.lbrt()

        l = max(l1,l2)
        b = max(b1,b2)
        r = min(r1,r2)
        t = min(t1,t2)

        return AARectangle(points=((l,b),(r,t)))

    def width(self):
        return self._right - self._left
    def height(self):
        return self._top - self._bottom

    def empty(self):
        l,b,r,t = self.lbrt()
        return (r <= l) or (t <= b)


### JABALERT: Should classes like this inherit from something like
### ClassInstanceParameter, which takes a class name and verifies that
### the value is in that class?
###
### Do we also need a BoundingBoxParameter?
class BoundingRegionParameter(Parameter):
    """
    Parameter whose value can be any BoundingRegion instance, enclosing a region in a 2D plane.
    """
    __slots__ = []
    __doc__ = property((lambda self: self.doc))

    def __init__(self,default=BoundingBox(radius=0.5),**params):
        super(BoundingRegionParameter,self).__init__(default=default,instantiate=True,**params)
        
    def __set__(self,obj,val):
        if not isinstance(val,BoundingRegion):
            raise ValueError("Parameter must be a BoundingRegion.")
        else:
            super(BoundingRegionParameter,self).__set__(obj,val)
            
