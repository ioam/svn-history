"""
Tests for the PlotFileSaver classes. Also tests analysis commands.

$Id$
"""
__version__='$Revision$'

import unittest
import os
import tempfile
import shutil

from topo.base.simulation import Simulation
from topo.base.cf import CFSheet, CFProjection
from topo.misc.filepath import resolve_path,normalize_path

from topo.sheet import GeneratorSheet

from topo.plotting.plotfilesaver import PlotGroupSaver

from topo.plotting.plotgroup import PlotGroup

from topo.command.analysis import save_plotgroup




import __main__
exec "from topo.command.analysis import *" in __main__.__dict__


class TestPlotGroupSaverBase(unittest.TestCase):

    def exists(self,name):
        self.assert_(os.path.exists(os.path.join(self.tests_dir,name)))

    def setUp(self):
        self.tests_dir=tempfile.mkdtemp()
        self.sim = Simulation(register=True,name="testplotfilesaver")
        self.sim['A'] = GeneratorSheet(nominal_density=2)
        self.sim['B'] = CFSheet(nominal_density=2)
        self.sim.connect('A','B',connection_type=CFProjection,name='Afferent')        

    def tearDown(self):
        shutil.rmtree(self.tests_dir)

    def save(self,name,**params):
        save_plotgroup(name,
                       # CEBALERT: rather than setting filename_prefix
                       # here, shouldn't I be setting
                       # filepath.output_path to a temporary path?
                       # That should be done before any tests are run,
                       # thus giving all tests access to a temporary
                       # directory that will be removed after all
                       # tests have run.
                       saver_params={"filename_prefix":self.tests_dir+'/'},
                       **params)        



class TestPlotGroupSaver(TestPlotGroupSaverBase):

    def test_activity_saving(self):
        self.save('Activity')
        self.exists("testplotfilesaver_000000.00_A_Activity.png")
        self.exists("testplotfilesaver_000000.00_B_Activity.png")

    def test_orientation_preference_saving(self):
        self.save('Orientation Preference')
        self.exists("testplotfilesaver_000000.00_B_Orientation_Preference.png")
        self.exists("testplotfilesaver_000000.00_B_Orientation_PreferenceAndSelectivity.png")
        self.exists("testplotfilesaver_000000.00_B_Orientation_Selectivity.png")
        self.exists("testplotfilesaver_000000.00__Color_Key.png")

    def test_cf_saving(self):
        self.save("Connection Fields",sheet=self.sim['B'])
        self.exists("testplotfilesaver_000000.00_Afferent_(from_A).png")

        
class TestCFProjectionPlotGroupSaver(TestPlotGroupSaverBase):

    def test_cfprojection_saving(self):
        self.save('Projection',
                  projection=self.sim['B'].projections('Afferent'))
        self.exists("testplotfilesaver_000000.00_B_Afferent.png")


###########################################################

cases = [TestPlotGroupSaver,TestCFProjectionPlotGroupSaver]

suite = unittest.TestSuite()
suite.addTests([unittest.makeSuite(case) for case in cases])

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite)

