"""
Uses testbitmap.jpg to populate a couple of sheets that the GUI
can then use to display data.

$Id$
"""
import unittest
import topo
from topo.inputsheet import *
from topo.gui import *
from topo.kernelfactory import *
from topo.simulator import *
from PIL import Image
from topo.sheetview import *
from topo.plotengine import *
from topo.bitmap import *

class TestGui(unittest.TestCase):

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


    def test_Gui(self):
        plot_group = self.pe.get_plot_group('Activation')
        plot_list = plot_group.plots()
        self.pe.debug('Type of plot_group', type(plot_group))

        self.s.verbose('Sheets: ', self.pe._sheets())
        for (figure_tuple, hist_tuple) in plot_group.plots():
            plot_group.debug('Plot Tuple', figure_tuple)
            (r,g,b) = figure_tuple
            if r.shape != (0,0) and g.shape != (0,0) and b.shape != (0,0):
                win = RGBMap(r,g,b)
                #win.show()
                # Do not display the images when running in the unit
                # test suite.
                # 
                # It doesn't make a whole lot of sense at this point to
                # test these images against a target, but it may be
                # useful in the future.

        root = start(self.s)
        #root.mainloop()


suite = unittest.TestSuite()
suite.addTest(unittest.makeSuite(TestGui))
