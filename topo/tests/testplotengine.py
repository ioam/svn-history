"""
This unit test also requires testbitmap.jpg to run.  The image is used
to import into Sheet Sheetview dictionaries.  The stub simulation is
not functional.

$Id$
"""
__version__='$Revision$'


### JCALERT! got rid of unused import statements!
import unittest
from pprint import pprint
from math import pi
from topo.plotting import plot
from topo.base import topoobject
from topo.base.sheet import Sheet
from topo.base.sheetview import SheetView
from topo.plotting.plotgroup import *
from topo.plotting.templates import PlotGroupTemplate
from topo.plotting.plotengine import *
from topo.sheets.generatorsheet import *
from topo.base.simulator import *
from topo.base import patterngenerator
from topo.patterns.basic import GaussianGenerator
from topo.base.parameter import Dynamic
from topo.sheets.cfsom import CFSOM
from Tkinter import *
from Tkconstants import *
from PIL import Image
import ImageTk
import random
import pdb #debugger


### JC: My new statements.
from topo.base.simulator import Simulator
from topo.plotting.plotengine import PlotEngine
from topo.plotting.plotgroup import BasicPlotGroup
from topo.plotting.templates import plotgroup_templates
from topo.sheets.cfsom import CFSOM
from topo.patterns.random import UniformRandomGenerator
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

          CFProjection.weights_generator = UniformRandomGenerator(bounds=BoundingBox(points=((-0.1,-0.1),(0.1,0.1))))
          CFProjection.weights_generator = UniformRandomGenerator(bounds=BoundingBox(points=((-0.1,-0.1),(0.1,0.1))))
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



          

          
#         self.s = Simulator(step_mode = 1)
#         self.engine = PlotEngine(self.s)
#         self.sheetR = Sheet()
#         self.sheetG = Sheet()
#         self.sheetB = Sheet()
#         self.plot1= plot.Plot(('Activity',None,None),plot.COLORMAP,self.sheetR)
#         self.plot2= plot.Plot(('Activity',None,None),plot.COLORMAP,self.sheetG)
        

#     def test_template_groups(self):
#         pgt = PlotGroupTemplate( 
#             [('HuePref', PlotTemplate({'Strength'   : None,
#                                        'Hue'        : 'Activity',
#                                        'Confidence' : None})),
#              ('HuePrefAndSel', PlotTemplate({'Strength'   : 'Activity',  
#                                              'Hue'        : 'Activity',
#                                              'Confidence' : None})),
#              ('HueSelect', PlotTemplate({'Strength'   : 'Activity',
#                                          'Hue'        : None,
#                                          'Confidence' : None}))])

# 	filter = lambda s: True
#         ag = self.engine.make_plot_group('ActivitySHC',pgt,filter,'BasicPlotGroup')
        

#     def test_get_plot_group(self):
#         pgt = PlotGroupTemplate([('Activity',
#                                   PlotTemplate({'Strength'   : 'Activity',
#                                                 'Hue'        : None,
#                                                 'Confidence' : None}))],
#                                 name='Activity')
#         self.engine.add_plot_group('OldAct',PlotGroup([self.plot1,
#                                                        self.plot2]))
#         group = self.engine.get_plot_group('OldAct')
#         activity_group = self.engine.get_plot_group('Activity',pgt)


#     def test_make_plot_group(self):
#         pgt = PlotGroupTemplate([('Activity',
#                                   PlotTemplate({'Strength'   : 'Activity',
#                                                 'Hue'        : None,
#                                                 'Confidence' : None}))],
#                                 name='Activity')

# 	filter = lambda s: True
#         activity_group = self.engine.make_plot_group('Activity',pgt,filter,'BasicPlotGroup')
#         activity_group2 = self.engine.make_plot_group('Activity',pgt,filter,'BasicPlotGroup')

 
#     def test_plotengine(self):
#         """
#         Cut and paste of current topographica/examples/cfsom_example.py
#         with extensions to interface with the PlotEngine and ImagePoster
#         """
#         # input generation params
#         GeneratorSheet.period = 1.0
#         GeneratorSheet.density = 30
        
#         GaussianGenerator.x = Dynamic(lambda : random.uniform(-0.5,0.5))
#         GaussianGenerator.y = Dynamic(lambda : random.uniform(-0.5,0.5))
#         GaussianGenerator.orientation = Dynamic(lambda :random.uniform(-pi,pi))
#         GaussianGenerator.width = 0.02
#         GaussianGenerator.height = 0.9
#         GaussianGenerator.bounds = BoundingBox(points=((-0.8,-0.8),(0.8,0.8)))

#         ###########################################
#         # build simulation
        
#         topo.base.topoobject.min_print_level = topo.base.topoobject.WARNING
        
#         s = Simulator()
#         s.print_level = topo.base.topoobject.WARNING
#         s.verbose("Creating simulation objects...")

#         # Uses testbitmap.jpg.
#         # Converts a JPG to a triple of arrays of [0 <= i <= 1].
#         miata = Image.open('topo/tests/testbitmap.jpg')
#         miata = miata.resize((miata.size[0]/2,miata.size[1]/2))
#         self.rIm, self.gIm, self.bIm = miata.split()
#         self.rseq = self.rIm.getdata()
#         self.gseq = self.gIm.getdata()
#         self.bseq = self.bIm.getdata()
#         self.rar = Numeric.array(self.rseq)
#         self.gar = Numeric.array(self.gseq)
#         self.bar = Numeric.array(self.bseq)
#         self.ra = Numeric.reshape(self.rar,miata.size) / 255.0
#         self.ga = Numeric.reshape(self.gar,miata.size) / 255.0
#         self.ba = Numeric.reshape(self.bar,miata.size) / 255.0

#         sheetR = Sheet()
#         sheetG = Sheet()
#         sheetB = Sheet()
#         retina = GeneratorSheet(input_generator=GaussianGenerator())
#         retina.print_level = topo.base.topoobject.WARNING


#         # For a new sheet_group named Miata:
#         sviewR = SheetView((self.ra,BoundingBox(points=((-0.8,-0.8),(0.8,0.8)))))
#         sviewG = SheetView((self.ga,BoundingBox(points=((-0.8,-0.8),(0.8,0.8)))))
#         sviewB = SheetView((self.ba,BoundingBox(points=((-0.8,-0.8),(0.8,0.8)))))
#         sheetR.add_sheet_view("Miata",sviewR)
#         sheetG.add_sheet_view("Miata",sviewG)
#         sheetB.add_sheet_view("Miata",sviewB)

#         # To change the activity matrix so "Activity" plot_group
#         # will be different.
#         sheetR.activity = self.ra
#         sheetG.activity = self.ga
#         sheetB.activity = self.ba

#         s.add(sheetR)
#         s.add(sheetG)
#         s.add(sheetB)
#         s.add(retina)

#         pe = PlotEngine(s)
#         s.run(1)

#         pgt = PlotGroupTemplate([('Activity',
#                                   PlotTemplate({'Strength'   : 'Activity',
#                                                 'Hue'        : None,
#                                                 'Confidence' : None}))],
#                                 name='Activity')
#         plot_group = pe.get_plot_group('Activity',pgt)
#         plot_list = plot_group.plots()
#         pe.debug('Type of plot_group', type(plot_group))

#         s.verbose('Sheets: ', pe.simulation.objects(Sheet).values())
#         for each in plot_group.plots():
#             figure_tuple = each.matrices
#             hist_tuple = each.histograms
#             plot_group.debug('Plot Tuple', figure_tuple)
#             (r,g,b) = figure_tuple
#             if r.shape != (0,0) and g.shape != (0,0) and b.shape != (0,0):
#                 win = RGBMap(r,g,b)
#                 # win.show()
#                 # Do not display the images when running in the unit
#                 # test suite.
#                 # 
#                 # It doesn't make a whole lot of sense at this point to
#                 # test these images against a target, but it may be
#                 # useful in the future.


suite = unittest.TestSuite()
suite.addTest(unittest.makeSuite(TestPlotEngine))

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite)
