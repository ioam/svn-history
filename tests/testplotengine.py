"""
See test_rfsom(self) and ImagePoster for an example of how to use and call
the PlotEngine system from a simulation.

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
from math import pi
from topo.params import Dynamic
from Tkinter import *
from Tkconstants import *
import ImageTk
import random
import pdb #debugger


class ImagePoster(EventProcessor):
    """
    Sample class of what it would take to display plots to the screen every
    self.step steps.  This pulls all 'Activation' plots.
    """

    def __init__(self, plotengine, **params):
        super(EventProcessor,self).__init__(**params)
        self.plotengine = plotengine
        self.c = 0
        self.step = 1


    def input_event(self,src,src_port,dest_port,data):
        if self.c >= self.step:
            self.c = 0
            #Post the image
            self.verbose('Sheets: ', self.plotengine._sheets())
            plot_group = self.plotengine.get_plot_group('Activation')
            plot_list = plot_group.plots()
            self.plotengine.debug('Type of plot_group', type(plot_group))

            # PIL will start displaying the images to a TK window once
            # a Tk environment is started.  This is fine, but in order
            # to display the window, mainloop() has to be called, and
            # control is lost.  Until a workaround is written, I'll
            # stick to XView
            # root = Tk()       

            for (figure_tuple, hist_tuple) in plot_group.plots():
                plot_group.debug('Plot Tuple', figure_tuple)
                (r,g,b) = figure_tuple
                win = RGBMap(r,g,b)
                win.show()

            # The start loop for displaying the static Tk windows.
            # root.mainloop()
        else:
            self.c = self.c + 1
        


class TestPlotEngine(unittest.TestCase):

    def setUp(self):
        self.s = Simulator(step_mode = 1)
        self.engine = PlotEngine(self.s)
        self.sheet1 = Sheet()
        self.sheet2 = Sheet()
        self.plot1= plot.Plot(('Activity',None,None),plot.COLORMAP,self.sheet1)
        self.plot2= plot.Plot(('Activity',None,None),plot.COLORMAP,self.sheet2)

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
        assert(sheet_filter(self.sheet1))


    def test_rfsom(self):
        """
        Cut and paste of current topographica/examples/rfsom_example.py
        with extensions to interface with the PlotEngine and ImagePoster
        """
        # input generation params
        InputSheet.period = 1.0
        InputSheet.density = 900
        
        GaussianSheet.x = Dynamic(lambda : random.uniform(-0.5,0.5))
        GaussianSheet.y = Dynamic(lambda : random.uniform(-0.5,0.5))
        
        GaussianSheet.theta = Dynamic(lambda :random.uniform(-pi,pi))
        GaussianSheet.width = 0.02
        GaussianSheet.height = 0.9
        GaussianSheet.bounds = BoundingBox(points=((-0.8,-0.8),(0.8,0.8)))
        
        # rf som parameters
        RFSOM.density = 900
        RFSOM.rf_width = 0.2
        RFSOM.training_length = 10000
        RFSOM.radius_0 = 0.1

        ###########################################
        # build simulation
        
        base.min_print_level = base.MESSAGE
        
        print "Creating simulation objects..."
        s = Simulator()
        pe = PlotEngine(s)
        
        retina = GaussianSheet(name='Retina')
        V1 = RFSOM(name='V1')

        poster = ImagePoster(pe)
        
        s.connect(retina,V1,delay=1)
        s.connect(retina,poster,dest_port='retina',delay=1)

        s.run(30)


        


suite = unittest.TestSuite()
suite.addTest(unittest.makeSuite(TestPlotEngine))
