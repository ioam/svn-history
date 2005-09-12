import unittest
import topo.simulator
import topo.plotengine
from pprint import pprint
from topo import plot
from topo.sheet import *
from topo.plotgroup import *
from topo.bitmap import RGBMap
from topo.kernelfactory import ImageGenerator
import Numeric
from Numeric import divide

SHOW_PLOTS = False

plotgroup_templates = {}

class TestPlotGroup(unittest.TestCase):

    def setUp(self):
        pgt = PlotGroupTemplate([('Activity',
                                  PlotTemplate({'Strength'   : 'Activity',
                                                'Hue'        : None,
                                                'Confidence' : None}))],
                                name='Activity')
        plotgroup_templates[pgt.name] = pgt
        pgt = PlotGroupTemplate([('Unit Weights',
                                  PlotTemplate({'Location'   : (0.0,0.0),
                                                'Sheet_name' : 'V1'}))],
                                name='Unit Weights')
        plotgroup_templates[pgt.name] = pgt
        pgt = PlotGroupTemplate([('Projection',
                                  PlotTemplate({'Density'         : 25,
                                                'Projection_name' : 'None'}))],
                                name='Projection')
        plotgroup_templates[pgt.name] = pgt
        pgt = PlotGroupTemplate([('Preference',
                                  PlotTemplate({'Strength'   : 'Activity',
                                                'Hue'        : 'Activity',
                                                'Confidence' : 'Activity'}))],
                                name='Preference Map')
        plotgroup_templates[pgt.name] = pgt


    def test_plotgroup_release(self):
        self.s = Sheet()
        self.s.activity = Numeric.array([[1,2],[3,4]])
        # Call s.sheet_view(..) with a parameter
        sv2 = self.s.sheet_view('Activity')
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
        x = plot.Plot((None,None,ig.sheet_view('Activity')),plot.HSV)
        y = plot.Plot(('Activity',None,None),plot.COLORMAP,ig)
        z = plot.Plot(('Activity',None,'Activity'),plot.HSV,ig)
        self.pg1 = PlotGroup(plot_list=[x])
        self.pg1.add(y)
        self.pg1.add(z)
        plot_list = self.pg1.plots()
        for each in plot_list:
            (r,g,b) = each.matrices
            map = RGBMap(r,g,b)
            if SHOW_PLOTS: map.show()

    def test_make_plot_group(self):
        sim = topo.simulator.Simulator()
        pe = topo.plotengine.PlotEngine(sim)
        pg = pe.make_plot_group('Activity',
                                plotgroup_templates['Activity'])

    def test_get_plot_group(self):
        sim = topo.simulator.Simulator()
        pe = topo.plotengine.PlotEngine(sim)
        pg = pe.get_plot_group('Activity',
                               plotgroup_templates['Activity'])
        pg = pe.get_plot_group('Activity',
                               plotgroup_templates['Activity'])



    def test_keyedlist(self):
        kl = KeyedList()
        kl = KeyedList(((2,3),(4,5)))
        self.assertEqual(kl[2],3)
        self.assertEqual(kl[4],5)
        kl.append((6,7))
        self.assertEqual(kl[6],7)
        kl[2] = 8
        self.assertEqual(kl[2],8)
        self.assertEqual(kl.has_key(5),False)
        self.assertTrue(kl.has_key(6))
        self.assertEqual(len(kl),3)
        kl.append((3,8))
        l = list(kl)
        

    def test_plotgrouptemplate(self):
        pgt = PlotGroupTemplate()

        pt1 = plot.PlotTemplate({'Strength'   : None,
                                 'Hue'        : 'HueP',
                                 'Confidence' : None})
        pt2 = plot.PlotTemplate({'Strength'   : 'HueSel',
                                 'Hue'        : 'HueP',
                                 'Confidence' : None})
        pt3 = plot.PlotTemplate({'Strength'   : 'HueSel',
                                 'Hue'        : None,
                                 'Confidence' : None})
        pgt = PlotGroupTemplate([('HuePref', pt1),
                                 ('HuePrefAndSel', pt2),
                                 ('HueSelect', pt3)])

        pgt2 = PlotGroupTemplate( 
            [('HuePref', PlotTemplate({'Strength'   : None,
                                       'Hue'        : 'HueP',
                                       'Confidence' : None})),
             ('HuePrefAndSel', PlotTemplate({'Strength'   : 'HueSel',  
                                             'Hue'        : 'HueP',
                                             'Confidence' : None})),
             ('HueSelect', PlotTemplate({'Strength'   : 'HueSel',
                                         'Hue'        : None,
                                         'Confidence' : None}))])




suite = unittest.TestSuite()
suite.addTest(unittest.makeSuite(TestPlotGroup))
