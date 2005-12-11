"""
Unit test for PlotGroupPanel
$Id$
"""
__version__='$Revision$'

import unittest, os
import topo
from topo.sheets.generatorsheet import *
from topo.tkgui import *
from topo.base.patterngenerator import *
from topo.base.simulator import *
from PIL import Image
from topo.base.sheetview import *
from topo.plotting.plotengine import *
from topo.plotting.bitmap import *
import topo.tkgui.topoconsole 
import topo.tkgui.plotgrouppanel
import Tkinter
from topo.sheets.cfsom import CFSOM
from math import pi
from topo.base.parameter import Dynamic
import random
import pdb #debugger
from topo.patterns.basic import GaussianGenerator,LineGenerator

class TestPlotGroupPanel(unittest.TestCase):

    def setUp(self):
        """
        Create a Simulator that has a couple of sheets within it that
        have data within them that can then be used by the GUI tests.
        Two objects created after completion:
            self.s   Sample simulation with a couple of sheets
            self.pe  Plot engine watching self.s
        """
        GeneratorSheet.period = 1.0
        GeneratorSheet.density = 30
#        base.print_level = topo.base.topoobject.WARNING
#        GeneratorSheet.print_level = topo.base.topoobject.WARNING
        
        GaussianGenerator.x = Dynamic(lambda : random.uniform(-0.5,0.5))
        GaussianGenerator.y = Dynamic(lambda : random.uniform(-0.5,0.5))
        GaussianGenerator.orientation = Dynamic(lambda :random.uniform(-pi,pi))

        width = 0.02
        height = 0.9
        GaussianGenerator.size = height
        GaussianGenerator.aspect_ratio = width/height
        GaussianGenerator.bounds = BoundingBox(points=((-0.8,-0.8),(0.8,0.8)))

        ###########################################
        # build simulation
        
#        topo.base.topoobject.min_print_level = topo.base.topoobject.WARNING
        
        self.s = Simulator()
        self.s.verbose("Creating simulation objects...")

        # Uses testbitmap.jpg.
        # Converts a JPG to a triple of arrays of [0 <= i <= 1].
        miata = Image.open('topo/tests/testbitmap.jpg')
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
        retina = GeneratorSheet(input_generator=GaussianGenerator())
        retina.print_level = topo.base.topoobject.WARNING

        # For a new sheet_group named Miata:
        sviewR = SheetView((self.ra,BoundingBox(points=((-0.8,-0.8),(0.8,0.8)))))
        sviewG = SheetView((self.ga,BoundingBox(points=((-0.8,-0.8),(0.8,0.8)))))
        sviewB = SheetView((self.ba,BoundingBox(points=((-0.8,-0.8),(0.8,0.8)))))
        sheetR.add_sheet_view("Miata",sviewR)
        sheetG.add_sheet_view("Miata",sviewG)
        sheetB.add_sheet_view("Miata",sviewB)

        # To change the activation matrix so "Activity" plot_group
        # will be different.
        sheetR.activity = self.ra
        sheetG.activity = self.ga
        sheetB.activity = self.ba

        self.s.add(sheetR)
        self.s.add(sheetG)
        self.s.add(sheetB)
        self.s.add(retina)

        self.pe = PlotEngine(self.s)
        # s.run(1)



    def test_weightspanel(self):
        """
        Here, we're not interested in the Activity plots, but we are
        interested in the weights of the receptive fields.
        """
        topo.base.topoobject.min_print_level = topo.base.topoobject.WARNING
        topo.tkgui.plotgrouppanel.PlotGroupPanel.print_level = topo.base.topoobject.WARNING
        # input generation params
        GeneratorSheet.period = 1.0
        GeneratorSheet.density = 30
        
        LineGenerator.x = Dynamic(lambda : random.uniform(-0.5,0.5))
        LineGenerator.y = Dynamic(lambda : random.uniform(-0.5,0.5))
        LineGenerator.orientation = Dynamic(lambda :random.uniform(-pi,pi))
        LineGenerator.thickness = 0.02
        LineGenerator.bounds = BoundingBox(points=((-0.8,-0.8),(0.8,0.8)))
        
        # rf som parameters
        CFSOM.density = 50
        CFSOM.learning_length = 10000
        CFSOM.radius_0 = 0.1
        
        ###########################################
        # build simulation
        s = topo.base.simulator.Simulator()
        
        retina = GeneratorSheet(input_generator=LineGenerator(),name='Retina')
        retina.print_level = topo.base.topoobject.WARNING
        V1 = CFSOM(name='V1')
        V1.print_level = topo.base.topoobject.WARNING
        
        s.connect(retina,V1,delay=1)
        s.print_level = topo.base.topoobject.WARNING
        
        s.run(1)

        root = Tkinter.Tk()
        root.resizable(1,1)
        Pmw.initialise(root)
        console = topo.tkgui.topoconsole.TopoConsole(parent=root)
        console.pack(expand=Tkinter.YES,fill=Tkinter.BOTH)
        #console.new_weights_window()
        # console.mainloop()
        


suite = unittest.TestSuite()
#  Uncomment the following line of code, to not run the test if
#  $DISPLAY is undefined.  Used mainly for GUI testing.
suite.requires_display = True
suite.addTest(unittest.makeSuite(TestPlotGroupPanel))

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite)
