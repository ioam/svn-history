"""
Unit test for PlotGroupPanel.

$Id$
"""
__version__='$Revision$'

import unittest
import Tkinter
import Image

import topo

from topo.plotting.plot import Plot
from topo.plotting.plotgroup import PlotGroup
from topo.tkgui.plotgrouppanel import PlotGroupPanel

from topo.tkgui.tkguiwindow import ScrolledTkguiWindow

# need to clean up stuff like this: do it all in one
# place (start() modification as suggested by JAB).
if not hasattr(topo,'guimain'):
    from topo.tkgui.topoconsole import TopoConsole
    TopoConsole()


class TestPlotGroupPanel(unittest.TestCase):

    def setUp(self):

        window = Tkinter.Toplevel()
        
        image = Image.open('examples/ellen_arthur.pgm')
        self.plot = Plot(image,name='Ellen Arthur')
        
        self.plotgroup = PlotGroup()
        self.plotgroup.plot_list.append(self.plot)
        
        self.pgpanel = PlotGroupPanel(topo.guimain,window,self.plotgroup)
        self.pgpanel.pack()

        #import __main__; __main__.__dict__['p']=self.pgpanel

    def test_refresh(self):
        """
        Check a plot gets created and displayed
        """
        assert not(hasattr(self.pgpanel.plotgroup,'plots'))
        self.pgpanel.Refresh()
        self.assertEqual(self.pgpanel.plotgroup.plots[0],self.plot)
        # CEBALERT: now should check the plot's actually on the canvas
        # but plotgrouppanel doesn't store canvas item ids, so we
        # can't check.


    # CEBALERT: still need to test the other panel functions...


class TestSheetPGPanel(unittest.TestCase):

    def setUp(self):
        return

##         window = Tkinter.Toplevel()

##         self.plotgroup = SheetPlotGroup( ...
                
##         self.pgpanel = SheetPGPanel(topo.guimain,window,self.plotgroup)
##         self.pgpanel.pack()




cases = [TestPlotGroupPanel,TestSheetPGPanel]

suite = unittest.TestSuite()
suite.requires_display = True
suite.addTests([unittest.makeSuite(case) for case in cases])


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite)
