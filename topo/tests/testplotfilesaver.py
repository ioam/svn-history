"""
Tests for the PlotFileSaver classes.

$Id$
"""
__version__='$Revision$'

import unittest

from topo.base.simulation import Simulation
from topo.base.cf import CFSheet, CFProjection
from topo.sheets.generatorsheet import GeneratorSheet

from topo.plotting.plotfilesaver import PlotGroupSaver,TemplatePlotGroupSaver,ConnectionFieldsPlotGroupSaver,CFProjectionPlotGroupSaver

from topo.plotting.plotgroup import PlotGroup

# CEBHACKALERT: seems like I'm testing analysis commands...i.e. I should have written
# a different test file...

PlotGroupSaver.filename_prefix="topo/tests/testplotfilesaver"

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
        
    def test_orientation_preference_saving(self):
        self.save('Orientation Preference')


class TestConnectionFieldsPlotGroupSaver(TestPlotGroupSaver):
    plotgroupsaver_class = ConnectionFieldsPlotGroupSaver

    def test_cf_saving(self):
        self.save("Connection Fields",sheet=self.sim['B'])

        
class TestCFProjectionPlotGroupSaver(TestPlotGroupSaver):
    plotgroupsaver_class = CFProjectionPlotGroupSaver

    def test_cfprojection_saving(self):
        self.save('Projection',sheet=self.sim['B'],
                  projection=self.sim['B'].projections('Afferent'))




###########################################################

cases = [TestPlotGroupSaver,TestTemplatePlotGroupSaver,TestConnectionFieldsPlotGroupSaver,TestCFProjectionPlotGroupSaver]

suite = unittest.TestSuite()
suite.addTests([unittest.makeSuite(case) for case in cases])

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite)

