import unittest
from pprint import pprint
from topo import plot
from topo.sheet import *
from topo.bitmap import RGBMap, HSVMap
from topo.image import ImageGenerator
import Numeric
from Numeric import divide

SHOW_PLOTS = False

class TestPlot(unittest.TestCase):

    def test_plot(self):
        self.s2 = Sheet()
        x = plot.Plot(('Activity',None,None),plot.COLORMAP,self.s2)
        for o in dir():
            # pprint(o)
            if isinstance(o,plot.Plot):
                o.warning('Found ', o.name)

        input = ImageGenerator(filename='tests/testsheetview.ppm',
                         density=10000,
                         bounds=BoundingBox(points=((-0.8,-0.8),(0.8,0.8))))
        sv = input.sheet_view('Activity')

        # Defined sheetview in the R channel
        plot1 = plot.Plot((None,None,sv),plot.COLORMAP)
        p_tuple = plot1.plot()
        (r, g, b) = p_tuple.matrices
        map = RGBMap(r,g,b)
        if SHOW_PLOTS: map.show()


    def test_HSV_plot(self):
        input = ImageGenerator(filename='tests/testsheetview.ppm',
                         density=10000,
                         bounds=BoundingBox(points=((-0.8,-0.8),(0.8,0.8))))
        sv = input.sheet_view('Activity')

        # Defined sheetview in the R channel
        plot1 = plot.Plot((sv,sv,sv),plot.HSV)
        p_tuple = plot1.plot()
        (r, g, b) = p_tuple.matrices
        map = HSVMap(r,g,b)
        if SHOW_PLOTS: map.show()

    def test_plottemplate(self):
        pt = plot.PlotTemplate()
        pt = plot.PlotTemplate({'Strength'   : None,
                                'Hue'        : 'HueP',
                                'Confidence' : None})
        pt = plot.PlotTemplate(channels={'Strength'   : None,
                                         'Hue'        : 'HueP',
                                         'Confidence' : None})



suite = unittest.TestSuite()
suite.addTest(unittest.makeSuite(TestPlot))
