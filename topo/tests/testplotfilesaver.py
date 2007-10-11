"""
Tests for the PlotFileSaver classes.

$Id$
"""
__version__='$Revision$'

import unittest
import os

from topo.base.simulation import Simulation
from topo.base.cf import CFSheet, CFProjection
from topo.base.parameterclasses import resolve_filename,normalize_path

from topo.sheets.generatorsheet import GeneratorSheet

from topo.plotting.plotfilesaver import PlotGroupSaver,TemplatePlotGroupSaver,ConnectionFieldsPlotGroupSaver,CFProjectionPlotGroupSaver

from topo.plotting.plotgroup import PlotGroup

# CEBHACKALERT: seems like I'm testing analysis commands...i.e. I should have written
# a different test file...

PlotGroupSaver.filename_prefix="topo/tests/testplotfilesaver"

# remove old test output
tests_dir=normalize_path("topo/tests/")
for f in os.listdir(tests_dir):
    if f.startswith("testplotfilesaverPGS_test") and f.endswith(".png"):
        os.remove(os.path.join(tests_dir,f))



class TestPlotGroupSaver(unittest.TestCase):

    plotgroupsaver_class = PlotGroupSaver

    def setUp(self):
        self.sim = Simulation(register=True,name="PGS_test")
        self.sim['A'] = GeneratorSheet(nominal_density=4)
        self.sim['B'] = CFSheet(nominal_density=4)
        self.sim.connect('A','B',connection_type=CFProjection,name='Afferent')        

    def save(self,name,**params):
        p = self.plotgroupsaver_class(name)
        p.generate_plotgroup(**params)
        p.plotgroup.make_plots(update=True)
        p.save_to_disk()


class TestTemplatePlotGroupSaver(TestPlotGroupSaver):
    plotgroupsaver_class = TemplatePlotGroupSaver

    def test_activity_saving(self):
        self.save('Activity')
        resolve_filename("topo/tests/testplotfilesaverPGS_test_000000.00_A_Activity.png")
        resolve_filename("topo/tests/testplotfilesaverPGS_test_000000.00_B_Activity.png")






        
    def test_orientation_preference_saving(self):
        self.save('Orientation Preference')
        resolve_filename("topo/tests/testplotfilesaverPGS_test_000000.00_B_Orientation_Preference.png")
        resolve_filename("topo/tests/testplotfilesaverPGS_test_000000.00_B_Orientation_PreferenceAndSelectivity.png")
        resolve_filename("topo/tests/testplotfilesaverPGS_test_000000.00_B_Orientation_Selectivity.png")
        resolve_filename("topo/tests/testplotfilesaverPGS_test_000000.00__Color_Key.png")
        



class TestConnectionFieldsPlotGroupSaver(TestPlotGroupSaver):
    plotgroupsaver_class = ConnectionFieldsPlotGroupSaver

    def test_cf_saving(self):
        self.save("Connection Fields",sheet=self.sim['B'])
        resolve_filename("topo/tests/testplotfilesaverPGS_test_000000.00_Afferent_(from_A).png")

        
class TestCFProjectionPlotGroupSaver(TestPlotGroupSaver):
    plotgroupsaver_class = CFProjectionPlotGroupSaver

    def test_cfprojection_saving(self):
        self.save('Projection',sheet=self.sim['B'],
                  projection=self.sim['B'].projections('Afferent'))
        resolve_filename("topo/tests/testplotfilesaverPGS_test_000000.00_B_Afferent.png")




###########################################################

cases = [TestPlotGroupSaver,TestTemplatePlotGroupSaver,TestConnectionFieldsPlotGroupSaver,TestCFProjectionPlotGroupSaver]

suite = unittest.TestSuite()
suite.addTests([unittest.makeSuite(case) for case in cases])

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite)

