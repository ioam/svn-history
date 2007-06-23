"""
Tests for the PlotFileSaver classes.

$Id$
"""
__version__='$Revision$'

### CEBALERT: tests don't work properly when file run on its own i.e. like:
###  ./topographica -c 'import topo.tests.testplotfilesaver; topo.tests.run(test_modules=[topo.tests.testplotfilesaver])'
### Tests do work when run as part of 'make tests', though.


import unittest

from topo.base.simulation import Simulation
from topo.base.cf import CFSheet, CFProjection
from topo.sheets.generatorsheet import GeneratorSheet

from topo.plotting.plotfilesaver import PlotGroupSaver,TemplatePlotGroupSaver,ConnectionFieldsPlotGroupSaver,CFProjectionPlotGroupSaver

from topo.plotting.plotgroup import PlotGroup
PlotGroup.cmd_location = locals()

# CEBHACKALERT: seems like I'm testing these commands...i.e. I should have written
# a different test file...
from topo.commands.analysis import update_activity,measure_or_pref,update_projections,update_connectionfields



PlotGroupSaver.filename_prefix="topo/tests/"

class TestPlotGroupSaver(unittest.TestCase):

    plotgroupsaver_class = PlotGroupSaver

    def setUp(self):
        self.sim = Simulation(register=False)
        self.sim['A'] = GeneratorSheet(nominal_density=4)
        self.sim['B'] = CFSheet(nominal_density=4)
        self.sim.connect('A','B',connection_type=CFProjection,name='Afferent')

    def save(self,name,**params):
        p = self.plotgroupsaver_class(name)
        p.plotgroup=p.generate_plotgroup(**params)
        p.plotgroup.draw_plots(update=True)
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

    # CEBHACKALERT: currently not working.
    def test_cfprojection_saving(self):
        pass
        #self.save('Projection',sheet=self.sim['B'],
        #          projection=self.sim['B'].projections('Afferent'))




###########################################################

cases = [TestPlotGroupSaver,TestTemplatePlotGroupSaver,TestConnectionFieldsPlotGroupSaver,TestCFProjectionPlotGroupSaver]

suite = unittest.TestSuite()
suite.addTests([unittest.makeSuite(case) for case in cases])

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite)

