import unittest, os
import topo
from topo.inputsheet import *
from topo.tk import *
from topo.kernelfactory import *
from topo.simulator import *
from PIL import Image
from topo.sheetview import *
from topo.plotengine import *
from topo.bitmap import *
import topo.tk.topoconsole 
import topo.tk.plotpanel
import Tkinter
from topo.cfsom import CFSOM
from topo.image import ImageSaver
from math import pi
from topo.params import Dynamic
import random
import pdb #debugger

class TestPlotPanel(unittest.TestCase):

    def setUp(self):
        """
        Create a Simulator that has a couple of sheets within it that
        have data within them that can then be used by the GUI tests.
        Two objects created after completion:
            self.s   Sample simulation with a couple of sheets
            self.pe  Plot engine watching self.s
        """
        InputSheet.period = 1.0
        InputSheet.density = 900
#        base.print_level = base.WARNING
#        InputSheet.print_level = base.WARNING
        
        GaussianFactory.x = Dynamic(lambda : random.uniform(-0.5,0.5))
        GaussianFactory.y = Dynamic(lambda : random.uniform(-0.5,0.5))
        GaussianFactory.theta = Dynamic(lambda :random.uniform(-pi,pi))
        GaussianFactory.width = 0.02
        GaussianFactory.height = 0.9
        GaussianFactory.bounds = BoundingBox(points=((-0.8,-0.8),(0.8,0.8)))

        ###########################################
        # build simulation
        
#        base.min_print_level = base.WARNING
        
        self.s = Simulator()
        self.s.verbose("Creating simulation objects...")

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
        retina.print_level = base.WARNING

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

        self.s.add(sheetR)
        self.s.add(sheetG)
        self.s.add(sheetB)
        self.s.add(retina)

        self.pe = PlotEngine(self.s)
        # s.run(1)



    def test_weightspanel(self):
        """
        Here, we're not interested in the Activation plots, but we are
        interested in the weights of the receptive fields.
        """
        base.min_print_level = base.WARNING
        topo.tk.plotpanel.PlotPanel.print_level = base.WARNING
        # input generation params
        InputSheet.period = 1.0
        InputSheet.density = 900
        
        FuzzyLineFactory.x = Dynamic(lambda : random.uniform(-0.5,0.5))
        FuzzyLineFactory.y = Dynamic(lambda : random.uniform(-0.5,0.5))
        FuzzyLineFactory.theta = Dynamic(lambda :random.uniform(-pi,pi))
        FuzzyLineFactory.width = 0.02
        FuzzyLineFactory.bounds = BoundingBox(points=((-0.8,-0.8),(0.8,0.8)))
        
        # rf som parameters
        CFSOM.density = 2500
        CFSOM.learning_length = 10000
        CFSOM.radius_0 = 0.1
        
        ###########################################
        # build simulation
        s = topo.simulator.Simulator()
        
        retina = InputSheet(input_generator=FuzzyLineFactory(),name='Retina')
        retina.print_level = base.WARNING
        V1 = CFSOM(name='V1')
        V1.print_level = base.WARNING
        save  = ImageSaver(name='CFSOM')
        
        s.connect(retina,V1,delay=1)
        s.print_level = base.WARNING
        
        s.run(1)

        root = Tkinter.Tk()
        root.resizable(1,1)
        Pmw.initialise(root)
        console = topo.tk.topoconsole.TopoConsole(parent=root)
        console.pack(expand=Tkinter.YES,fill=Tkinter.BOTH)
        console.new_weights_window()
        # console.mainloop()
        


suite = unittest.TestSuite()
#  Uncomment the following line of code, to not run the test if
#  $DISPLAY is undefined.  Used mainly for GUI testing.
suite.requires_display = True
suite.addTest(unittest.makeSuite(TestPlotPanel))
