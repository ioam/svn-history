"""
This unit test also requires testbitmap.jpg to run.  The image is used
to import into Sheet Sheetview dictionaries.  The stub simulation is
not functional.

$Id$
"""
__version__='$Revision$'


### JC: My new statements.
import unittest
from topo.base.simulator import Simulator
from topo.plotting.plotengine import PlotEngine
from topo.plotting.plotgroup import BasicPlotGroup, UnitWeightsPlotGroup
from topo.plotting.templates import plotgroup_templates
from topo.sheets.cfsom import CFSOM
import topo.patterns.random
from topo.learningfns.basic import HebbianSOMLF
from topo.base.connectionfield import CFProjection
from topo.responsefns.basic import CFDotProduct
from topo.base.patterngenerator import BoundingBox

### JCALERT! This file has to be re-written when the fundamental changes in plot.py
### plotengine.py and plotgroup.py will be finished.
### for the moment, the tests are commented out...

class TestPlotEngine(unittest.TestCase):

      def setUp(self):

          self.sim = Simulator()

          CFSOM.density = 10
          
          V1 = CFSOM(name='V1')
          V2 = CFSOM(name='V2')
          V3 = CFSOM(name='V3')

          CFProjection.weights_generator = topo.patterns.random.UniformRandom(bounds=BoundingBox(points=((-0.1,-0.1),(0.1,0.1))))
          CFProjection.weights_generator = topo.patterns.random.UniformRandom(bounds=BoundingBox(points=((-0.1,-0.1),(0.1,0.1))))
          CFProjection.response_fn = CFDotProduct()
          CFProjection.learning_fn = HebbianSOMLF()

          self.sim.connect(V1,V2,delay=0.5,connection_type=CFProjection,connection_params={'name':'V1toV2'})
          self.sim.connect(V3,V2,delay=0.5,connection_type=CFProjection,connection_params={'name':'V2toV3'})

          self.pe = PlotEngine(self.sim)

      def test_make_plot_group(self):

          ### Activity PlotGroup
          pgt1 = plotgroup_templates['Activity']

          self.pe.make_plot_group('Activity',pgt1,'BasicPlotGroup',None)
          test_plot_group = BasicPlotGroup(self.sim,pgt1,'Activity',None,None)
          test = self.pe.plot_group_dict.get('Activity',None)

          ### JCALERT! HOW TO TEST THAT TWO PLOTGROUP ARE THE SAME?
          #self.assertEqual(test_plot_group,test)
          
          ### Orientation Preference PlotGroup
          pgt2 = plotgroup_templates['Orientation Preference']

          self.pe.make_plot_group('Orientation Preference',pgt2,'BasicPlotGroup',None)
          test_plot_group = BasicPlotGroup(self.sim,pgt2,'Orientation Preference',None,None)
          test = self.pe.plot_group_dict.get('Orientation Preference',None)
          #self.assertEqual(test_plot_group,test)

          ### UnitWeight PlotGroup
          pgt3 = plotgroup_templates['Unit Weights']

          pg_key1=('Weights','V1',0,0)
          pg_key2=('Weights','V2',0.4,0.4)
          pg_key3=('Weights','V3',0.1,0.1)
          self.pe.make_plot_group(pg_key1,pgt3,'UnitWeightsPlotGroup','V1')
          self.pe.make_plot_group(pg_key2,pgt3,'UnitWeightsPlotGroup','V2')
          self.pe.make_plot_group(pg_key3,pgt3,'UnitWeightsPlotGroup','V3')
          
          test_plot_group1 = UnitWeightsPlotGroup(self.sim,pgt3,pg_key1,'V1',None)
          test_lambda = lambda s: s.name == 'V2'
          test_plot_group2 = UnitWeightsPlotGroup(self.sim,pgt3,pg_key2,test_lambda,None)
          test_plot_group3 = UnitWeightsPlotGroup(self.sim,pgt3,pg_key3,'V3',None)


          test1 = self.pe.plot_group_dict.get(pg_key1,None)
          #self.assertEqual(test_plot_group1,test1)

          test2 = self.pe.plot_group_dict.get(pg_key2,None)
          #self.assertEqual(test_plot_group2,test2)

          test3 = self.pe.plot_group_dict.get(pg_key3,None)
          #self.assertEqual(test_plot_group3,test3)
          
          pgt4 = plotgroup_templates['Projection']



suite = unittest.TestSuite()
suite.addTest(unittest.makeSuite(TestPlotEngine))

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite)
