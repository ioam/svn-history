import unittest
from pprint import pprint
from topo import plot
from topo.sheet import *
from topo.bitmap import RGBMap
from topo.image import ImageGenerator
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
        sv = input.sheet_view('Activation')

        # Defined sheetview in the R channel
        plot1 = plot.Plot((None,None,sv),plot.COLORMAP)
        p_tuple = plot1.plot()
        (r, g, b) = p_tuple[0]
        map = RGBMap(r,g,b)
        if SHOW_PLOTS: map.show()



    def test_plotgroup(self):
        self.s2 = Sheet()
        ig = ImageGenerator(filename='tests/testsheetview.ppm',
                         density=10000,
                         bounds=BoundingBox(points=((-0.8,-0.8),(0.8,0.8))))
        x = plot.Plot((None,None,ig.sheet_view('Activation')),plot.HSV)
        y = plot.Plot(('Activation',None,None),plot.COLORMAP,ig)
        z = plot.Plot(('Activation',None,'Activation'),plot.HSV,ig)
        self.pg1 = plot.PlotGroup([x])
        self.pg1.add(y)
        self.pg1.add(z)
        plot_list = self.pg1.plots()
        for each in plot_list:
            (r,g,b) = each[0]
            map = RGBMap(r,g,b)
            if SHOW_PLOTS: map.show()
        





suite = unittest.TestSuite()
suite.addTest(unittest.makeSuite(TestPlot))
