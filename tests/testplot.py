import unittest
from pprint import pprint
from topo import plot
from topo.sheet import Sheet

class TestPlot(unittest.TestCase):

    def test_plot(self):
        self.s2 = Sheet()
        x = plot.Plot(('Activity',None,None),plot.COLORMAP,self.s2)
        for o in dir():
            # pprint(o)
            if isinstance(o,plot.Plot):
                o.warning('Found ', o.name)



suite = unittest.TestSuite()
suite.addTest(unittest.makeSuite(TestPlot))
