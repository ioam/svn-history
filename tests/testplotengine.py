"""
This unit test also requires testbitmap.jpg to run.  The image is used
to import into Sheet Sheetview dictionaries.  The stub simulation is
not functional.

$Id$
"""
import unittest
from pprint import pprint
from topo import plot
from topo import base
from topo.bitmap import *
from topo.sheet import Sheet
from topo.plotengine import *
from topo.inputsheet import *
from topo.simulator import *
from topo.rfsom import RFSOM
from topo.image import ImageSaver
from topo import kernelfactory
from topo.kernelfactory import GaussianFactory
from math import pi
from topo.params import Dynamic
from Tkinter import *
from Tkconstants import *
from PIL import Image
import ImageTk
import random
import pdb #debugger


class TestPlotEngine(unittest.TestCase):

    def setUp(self):
        self.s = Simulator(step_mode = 1)
        self.engine = PlotEngine(self.s)
        self.sheetR = Sheet()
        self.sheetG = Sheet()
        self.sheetB = Sheet()
        self.plot1= plot.Plot(('Activity',None,None),plot.COLORMAP,self.sheetR)
        self.plot2= plot.Plot(('Activity',None,None),plot.COLORMAP,self.sheetG)

        pulse1 = PulseGenerator(period = 1)
        pulse2 = PulseGenerator(period = 3)
        sum = SumUnit()
        self.s.connect(pulse1,sum,delay=1)
        self.s.connect(pulse2,sum,delay=1)
        

    def test_get_plot_group(self):
        self.engine.add_plot_group('OldAct',plot.PlotGroup([self.plot1,
                                                            self.plot2]))
        group = self.engine.get_plot_group('OldAct')
        activity_group = self.engine.get_plot_group('Activity')


    def test_make_sheetview_group(self):
        activity_group = self.engine.make_sheetview_group('Activity',sheet_filter)
        activity_group2 = self.engine.make_sheetview_group('Activity',sheet_filter)


    def test_sheet_filter(self):
        assert(sheet_filter(self.sheetR))


    def test_plotengine(self):
        """
        Cut and paste of current topographica/examples/rfsom_example.py
        with extensions to interface with the PlotEngine and ImagePoster
        """
        # input generation params
        InputSheet.period = 1.0
        InputSheet.density = 900
        
        GaussianFactory.x = Dynamic(lambda : random.uniform(-0.5,0.5))
        GaussianFactory.y = Dynamic(lambda : random.uniform(-0.5,0.5))
        GaussianFactory.theta = Dynamic(lambda :random.uniform(-pi,pi))
        GaussianFactory.width = 0.02
        GaussianFactory.height = 0.9
        GaussianFactory.bounds = BoundingBox(points=((-0.8,-0.8),(0.8,0.8)))

        ###########################################
        # build simulation
        
        base.min_print_level = base.MESSAGE
        
        s = Simulator()
        s.verbose("Creating simulation objects...")

        # Uses testbitmap.jpg.
        # Converts a JPG to a triple of arrays of [0 <= i <= 1].
        miata = Image.open('tests/testbitmap.jpg')
        miata = miata.resize((miata.size[0]/2,miata.size[1]/2))
        self.rIm, self.gIm, self.bIm = miata.split()
        self.rseq = self.rIm.getdata()
        self.gseq = self.gIm.getdata()
        self.bseq = self.bIm.getdata()
        self.rar = Numeric.array(self.rseq)
        self.gar = Numeric.array(self.gseq)
        self.bar = Numeric.array(self.bseq)
        self.ra = Numeric.reshape(self.rar,miata.size) / 255.0
        self.ga = Numeric.reshape(self.gar,miata.size) / 255.0
        self.ba = Numeric.reshape(self.bar,miata.size) / 255.0

        sheetR = Sheet()
        sheetG = Sheet()
        sheetB = Sheet()
        retina = InputSheet(input_generator=GaussianFactory())

        # For a new sheet_group named Miata:
        sviewR = SheetView((self.ra,BoundingBox(points=((-0.8,-0.8),(0.8,0.8)))))
        sviewG = SheetView((self.ga,BoundingBox(points=((-0.8,-0.8),(0.8,0.8)))))
        sviewB = SheetView((self.ba,BoundingBox(points=((-0.8,-0.8),(0.8,0.8)))))
        sheetR.add_sheet_view("Miata",sviewR)
        sheetG.add_sheet_view("Miata",sviewG)
        sheetB.add_sheet_view("Miata",sviewB)

        # To change the activation matrix so "Activation" plot_group
        # will be different.
        sheetR.activation = self.ra
        sheetG.activation = self.ga
        sheetB.activation = self.ba

        s.add(sheetR)
        s.add(sheetG)
        s.add(sheetB)
        s.add(retina)

        pe = PlotEngine(s)
        s.run(1)

        plot_group = pe.get_plot_group('Activation')
        plot_list = plot_group.plots()
        pe.debug('Type of plot_group', type(plot_group))

        s.verbose('Sheets: ', pe._sheets())
        for (figure_tuple, hist_tuple) in plot_group.plots():
            plot_group.debug('Plot Tuple', figure_tuple)
            (r,g,b) = figure_tuple
            if r.shape != (0,0) and g.shape != (0,0) and b.shape != (0,0):
                win = RGBMap(r,g,b)
                # win.show()
                # Do not display the images when running in the unit
                # test suite.
                # 
                # It doesn't make a whole lot of sense at this point to
                # test these images against a target, but it may be
                # useful in the future.


suite = unittest.TestSuite()
suite.addTest(unittest.makeSuite(TestPlotEngine))

