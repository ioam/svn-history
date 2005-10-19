"""
TestMeasureFeatureMap

$Id$
"""

import unittest

# for making a simulator:
from topo.sheets.generatorsheet import GeneratorSheet
from topo.projections.kernelprojection import KernelProjection
from topo.sheets.cfsom import CFSOM
from topo.base.simulator import Simulator

# for measurefeaturemap itself:
from topo.base.measurefeaturemap import *



class TestMeasureFeatureMap(unittest.TestCase):

    def setUp(self):
        """
        Create a CFSOM sheet ('V1') connected to a GeneratorSheet ('Retina').
        """
        self.s = Simulator()
        self.retina = GeneratorSheet(name='Retina')
        self.V1 = CFSOM(name='V1')
        self.s.connect(self.retina,self.V1,delay=1,connection_type=KernelProjection,connection_params={'name':'RtoV1'})
        #self.s.run(1)


    def test_measurefeaturemap(self):
        """
        
        """
        feature_param = {"theta": ( (0.0,1.0), 0.5, True, True )}
        self.x = MeasureFeatureMap(self.s, feature_param)

        self.x.pattern_present_update()

#        print self.x.sheet_featuremaps[self.V1]['theta'].map()
        #... big matrix...we haven't checked it properly

#        print self.x.sheet_featuremaps[self.V1]['theta'].selectivity()
        #... big matrix...we haven't checked it properly

#        print self.x.sheet_featuremaps[self.V1]['theta'].distribution_matrix
        #... don't type that in over ssh!

        print self.x.sheet_featuremaps[self.V1]['theta'].distribution_matrix[0,0]

        print self.x.sheet_featuremaps[self.V1]['theta'].distribution_matrix[0,0]._data
        #{0.0: 0.71912158384770508, 0.5: 1.0}
        

suite = unittest.TestSuite()
suite.addTest(unittest.makeSuite(TestMeasureFeatureMap))
