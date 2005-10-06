"""
Defined Palette types.  Each palette is an object with accessors.

DEVELOPMENT PLANS: Core functionality was written, but there is no
integration into plot.py or plotengine.py and testing was minimal.

THIS CLASS WAS WRITTEN BUT NOT FINISHED SUMMER 2004 DUE TO TIME
CONSTRAINTS.  THE FUTURE PLANS FOR PALETTE DESIGN ARE AS FOLLOWS:

Changes to plot.py need to be made in order to use the Palette class
triples instead of defaulting to just copying the Colormap matrix
three times.  To see where to do this in plot.py search for the line:
'elif self.plot_type == COLORMAP:'

A Palette object has 256 triples of RGB values ranging from 0 ... 255.
The purpose of the class is to maintain an accurate palette
conversion between a number (0..255) and an RGB triple even as the
background of the plots change.  If the background is Black, then
the 0 intensity should often be 0, but if the background of the
Plot should be white, then the 0 intensity should probably be 255.
This automatic updating is possible through the use of Dynamic
Parameters, and lambda functions.

There is a base class called Palette that will store a passed in
variable.  If the variable is a lambda function that gives the 256
triples, then it will evaluate the lambda each time a datarequest is
made.  If it is a static list, then the palette is fixed.  It may be
possible to make Palette a 'pure' Dynamic parameter, with different
types of palettes setting the lambda.  More power to you if you do
that.

Class Monochrome is a sample subclass of Palette that creates a
Monochrome palette ranging from 0=>0 ... 255=>255 when the
background type is BLACK_BACKGROUND and 0=>255 ... 255=>0 when
the background type is WHITE_BACKGROUND.

Other Palette subclasses can be easily added such as Cool, Hot,
etc.

$Id$
"""
from topo.base.object import TopoObject
from topo.base.parameter import Dynamic
from topo.plotting.bitmap import BLACK_BACKGROUND, WHITE_BACKGROUND
import topo.plotting.plot

### JABHACKALERT!
### 
### Not yet properly implemented; all the code in this file needs to
### be either implemented or removed.

class Palette(TopoObject):
    """
    Each palette has 3*256 values that are keyed by an index.
    This base class takes in a list of 256 triples.
    """
    background = Dynamic(default=BLACK_BACKGROUND)
    colors_ = Dynamic(default=(lambda:[(i,i,i) for i in range(256)]))

    def __init__(self,**params):
        """
        Does not fill in the colors, must call with a set
        function call preferably from a subclass of Palette
        """
        super(Palette,self).__init__(**params)

    def set(self, colors):
        """
        Colors is a list of 256 triples, each with a 0..255 RGB value
        or a lambda function that generates the list.  Lambdas will be
        necessary for dynamic shifts in black or white background
        changes.
        """
        self.colors_ = colors

    def flat(self):
        """
        Return the palette in a flat form of 768 numbers.  If the
        colors_ parameter is a callable object, call it for the
        list of values.
        """
        c = self.colors_
        return_list = []
        if callable(c):
            self.warning('Callable Parameter value returned, ', callable(c))
            c = c()
        for each in c:
            return_list.extend(list(each))
        return return_list

    def color(self, pos):
        """
        Return the tuple of RGB color found at pos in color list
        """
        c = self.colors_
        if callable(c):
            self.warning('Callable Parameter value returned, ', callable(c))
            c = c()
        return c[pos]

    def colors(self):
        """
        Return the complete list of palette colors in tuple form
        """
        c = self.colors_
        if callable(c):
            self.warning('Callable Parameter value returned, ', callable(c))
            c = c()
        return c



class Monochrome(Palette):
    """
    Color goes from Black to White if background is Black. It goes
    from White to Black if background is set to White.  By using
    a Dynamic Parameter, it should be able to update the palette
    automatically if the plot background color changes.
    """

    def __init__(self,**params):
        """
        Set a lambda function to the colors list which switches
        if the background switches.  This makes the accessors in
        the parent class rather slow since it has to do a list
        comprehension each time it accesses the list.
        """
        super(Monochrome,self).__init__(**params)
        self.colors = lambda: self.__mono_palette__()

    def __mono_palette__(self):
        """
        Function to be passed as a lambda to the Parameter
        """
        if self.background == BLACK_BACKGROUND:
            set_ = [(i,i,i) for i in range(256)]
        else:                  # Reverse the order 255 ... 0
            set_ = [(i,i,i) for i in range(255,-1,-1)]
        return set_
                

    
