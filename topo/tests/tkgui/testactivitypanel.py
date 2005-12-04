"""
Unit test for activity panel (BasicPlotGroupPanel)
$Id$
"""
__version__='$Revision$'

import unittest
import topo
import Numeric
import Tkinter
import Pmw
from PIL import Image
from topo.sheets.generatorsheet import *
from topo.base.patterngenerator import *
from topo.base.simulator import *
from topo.base.sheetview import *
from topo.plotting.plotengine import *
from topo.tkgui.basicplotgrouppanel import BasicPlotGroupPanel
from topo.patterns.basic import GaussianGenerator

### JCALERT! This test sould be in the testbasicgrouppanel.py.

class TestActivityPanel(unittest.TestCase):

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
        GaussianGenerator.width = 0.02
        GaussianGenerator.height = 0.9
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

        # To change the activity matrix so "Activity" plot_group
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

    def test_activity_plot(self):
        """
        Test the creation the widgets
        """
        topo.base.topoobject.min_print_level = topo.base.topoobject.WARNING
        BasicPlotGroupPanel.print_level = topo.base.topoobject.WARNING

        root = Tkinter.Tk()
        root.resizable(1,1)
        Pmw.initialise(root)
        console = topo.tkgui.topoconsole.TopoConsole(parent=root)
        console.pack(expand=Tkinter.YES,fill=Tkinter.BOTH)
        console.set_active_simulator()
        #console.new_activity_window()
        # console.mainloop()

suite = unittest.TestSuite()
#  Uncomment the following line of code, to not run the test if
#  $DISPLAY is undefined.  Used mainly for GUI testing.
suite.requires_display = True
suite.addTest(unittest.makeSuite(TestActivityPanel))
