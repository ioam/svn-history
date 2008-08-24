"""
Tests for the PlotFileSaver classes. Also tests analysis commands.

$Id$
"""
__version__='$Revision$'

import unittest
import os

from topo.base.simulation import Simulation
from topo.base.cf import CFSheet, CFProjection
from topo.misc.filepath import resolve_path,normalize_path

from topo.sheet.generator import GeneratorSheet

from topo.plotting.plotfilesaver import PlotGroupSaver

from topo.plotting.plotgroup import PlotGroup

from topo.command.analysis import save_plotgroup


# remove old test output
tests_dir=normalize_path("topo/tests/")
for f in os.listdir(tests_dir):
    if f.startswith("testplotfilesaverPGS_test") and f.endswith(".png"):
        os.remove(os.path.join(tests_dir,f))

import __main__
exec "from topo.command.analysis import *" in __main__.__dict__


class TestPlotGroupSaverBase(unittest.TestCase):

    def setUp(self):
        self.sim = Simulation(register=True,name="PGS_test")
        self.sim['A'] = GeneratorSheet(nominal_density=2)
        self.sim['B'] = CFSheet(nominal_density=2)
        self.sim.connect('A','B',connection_type=CFProjection,name='Afferent')        

    def save(self,name,**params):
        save_plotgroup(name,
                       saver_params={"filename_prefix":"topo/tests/testplotfilesaver"},
                       **params)        



class TestPlotGroupSaver(TestPlotGroupSaverBase):

    def test_activity_saving(self):
        self.save('Activity')
        resolve_path("topo/tests/testplotfilesaverPGS_test_000000.00_A_Activity.png")
        resolve_path("topo/tests/testplotfilesaverPGS_test_000000.00_B_Activity.png")

    def test_orientation_preference_saving(self):
        self.save('Orientation Preference')
        resolve_path("topo/tests/testplotfilesaverPGS_test_000000.00_B_Orientation_Preference.png")
        resolve_path("topo/tests/testplotfilesaverPGS_test_000000.00_B_Orientation_PreferenceAndSelectivity.png")
        resolve_path("topo/tests/testplotfilesaverPGS_test_000000.00_B_Orientation_Selectivity.png")
        resolve_path("topo/tests/testplotfilesaverPGS_test_000000.00__Color_Key.png")

    def test_cf_saving(self):
        self.save("Connection Fields",sheet=self.sim['B'])
        resolve_path("topo/tests/testplotfilesaverPGS_test_000000.00_Afferent_(from_A).png")

        
class TestCFProjectionPlotGroupSaver(TestPlotGroupSaverBase):

    def test_cfprojection_saving(self):
        self.save('Projection',
                  projection=self.sim['B'].projections('Afferent'))
        resolve_path("topo/tests/testplotfilesaverPGS_test_000000.00_B_Afferent.png")


###########################################################

cases = [TestPlotGroupSaver,TestCFProjectionPlotGroupSaver]

suite = unittest.TestSuite()
suite.addTests([unittest.makeSuite(case) for case in cases])

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite)

