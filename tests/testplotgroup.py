import unittest
import topo.simulator
import topo.plotengine
from pprint import pprint
from topo import plot
from topo.sheet import *
from topo.plotgroup import *
from topo.bitmap import RGBMap
from topo.image import ImageGenerator
import Numeric
from Numeric import divide

SHOW_PLOTS = False

class TestPlotGroup(unittest.TestCase):


    def test_plotgroup_release(self):
        self.s = Sheet()
        self.s.activity = Numeric.array([[1,2],[3,4]])
        # Call s.sheet_view(..) with a parameter
        sv2 = self.s.sheet_view('Activation')
        self.s.add_sheet_view('key',sv2)
        self.assertEqual(len(self.s.sheet_view_dict.keys()),1)
        y = plot.Plot(('key',None,None),plot.HSV,self.s)
        z = plot.Plot(('key',None,None),plot.HSV,self.s)
        self.pg1 = PlotGroup(plot_list=[y,z])
        tuples = self.pg1.plots()
        self.pg1.release_sheetviews()
        self.assertEqual(len(self.s.sheet_view_dict.keys()),0)
        


    def test_plotgroup(self):
        self.s2 = Sheet()
        ig = ImageGenerator(filename='tests/testsheetview.ppm',
                         density=10000,
                         bounds=BoundingBox(points=((-0.8,-0.8),(0.8,0.8))))
        x = plot.Plot((None,None,ig.sheet_view('Activation')),plot.HSV)
        y = plot.Plot(('Activation',None,None),plot.COLORMAP,ig)
        z = plot.Plot(('Activation',None,'Activation'),plot.HSV,ig)
        self.pg1 = PlotGroup(plot_list=[x])
        self.pg1.add(y)
        self.pg1.add(z)
        plot_list = self.pg1.plots()
        for each in plot_list:
            (r,g,b) = each.matrices
            map = RGBMap(r,g,b)
            if SHOW_PLOTS: map.show()

    def test_make_sheetview_group(self):
        sim = topo.simulator.Simulator()
        pe = topo.plotengine.PlotEngine(sim)
        pg = pe.make_sheetview_group('Activation')

    def test_get_plot_group(self):
        sim = topo.simulator.Simulator()
        pe = topo.plotengine.PlotEngine(sim)
        pg = pe.get_plot_group('Activation')
        pg = pe.get_plot_group('Activation',group_type='ActivationPlotGroup')



suite = unittest.TestSuite()
suite.addTest(unittest.makeSuite(TestPlotGroup))
