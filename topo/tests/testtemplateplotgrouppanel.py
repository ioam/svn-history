"""
Test for TemplatePlotGroupPanel

$Id$
"""
__version__='$Revision$'


import unittest,random

import topo
import numpy.oldnumeric as Numeric
import Tkinter
import Pmw
from PIL import Image
from topo.sheets.generatorsheet import *
from topo.base.patterngenerator import *
from topo.base.simulation import *
from topo.base.sheetview import *
from topo.tkgui.templateplotgrouppanel import *
import topo.patterns.basic

from topo.base.parameterclasses import DynamicNumber
from topo.misc.numbergenerators import UniformRandom

### JCALERT: This test has to be written in order to test the new change in
### the TemplatePlotGroupPanel file



class TestActivityPanel(unittest.TestCase):

    def setUp(self):
        """
        Create a Simulation self.s that has a couple of sheets within
        it that have data within them that can then be used by the GUI
        tests.
        """
        GeneratorSheet.period = 1.0
        GeneratorSheet.nominal_density = 30
#        base.print_level = topo.base.parameterizedobject.WARNING
#        GeneratorSheet.print_level = topo.base.parameterizedobject.WARNING

        gaussian_width = 0.02
        gaussian_height = 0.9

        input_pattern = topo.patterns.basic.Gaussian(
            bounds=BoundingBox(points=((-0.8,-0.8),(0.8,0.8))),
            scale=gaussian_height,
            aspect_ratio=gaussian_width/gaussian_height,
            x=DynamicNumber(UniformRandom(lbound=-0.5,ubound=0.5,seed=100)),
            y=DynamicNumber(UniformRandom(lbound=-0.5,ubound=0.5,seed=200)),
            orientation=DynamicNumber(UniformRandom(lbound=-pi,ubound=pi,seed=300)))


        ###########################################
        # build simulation
        
#        topo.base.parameterizedobject.min_print_level = topo.base.parameterizedobject.WARNING
        
        self.s = Simulation()
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
        retina = GeneratorSheet(input_generator=input_pattern)
        retina.print_level = topo.base.parameterizedobject.WARNING

        # For a new sheet_group named Miata:
        sviewR = SheetView((self.ra,BoundingBox(points=((-0.8,-0.8),(0.8,0.8)))))
        sviewG = SheetView((self.ga,BoundingBox(points=((-0.8,-0.8),(0.8,0.8)))))
        sviewB = SheetView((self.ba,BoundingBox(points=((-0.8,-0.8),(0.8,0.8)))))
        sheetR.sheet_views["Miata"]=sviewR
        sheetG.sheet_views["Miata"]=sviewG
        sheetB.sheet_views["Miata"]=sviewB

        # To change the activity matrix so "Activity" plot_group
        # will be different.
        sheetR.activity = self.ra
        sheetG.activity = self.ga
        sheetB.activity = self.ba

        # CEBALERT: I don't understand what this is testing; it's not
        # used later.
##         self.s.add(sheetR)
##         self.s.add(sheetG)
##         self.s.add(sheetB)
##         self.s.add(retina)
	
        # s.run(1)

##     def test_activity_plot(self):
##         """
##         Test the creation the widgets
##         """
##         topo.base.parameterizedobject.min_print_level = topo.base.parameterizedobject.WARNING
##         TemplatePlotGroupPanel.print_level = topo.base.parameterizedobject.WARNING

        
##         console = topo.tkgui.topoconsole.TopoConsole()
##         Pmw.initialise(console)
        
##         # CEBALERT: what was this testing?
##         #console.set_active_simulator()

##         #console.new_activity_window()
##         # console.mainloop()


class TestTemplatePlotGroupPanel(unittest.TestCase):


    def test_preference_plot(self):
        pass


suite = unittest.TestSuite()
#  Uncomment the following line of code, to not run the test if
#  $DISPLAY is undefined.  Used mainly for GUI testing.
suite.requires_display = True
suite.addTest(unittest.makeSuite(TestActivityPanel))
suite.addTest(unittest.makeSuite(TestTemplatePlotGroupPanel))


### JCALERT! I don't know why but this does not work...?
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=1).run(suite)
