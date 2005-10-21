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

from topo.patterns import basic


#import __main__

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
        self.s.connect(self.retina,self.V1,delay=0.5,connection_type=KernelProjection,connection_params={'name':'RtoV1'})

        self.V2 = CFSOM(name='V2')


        #self.s.connect(self.V1,self.V2,delay=1,connection_type=KernelProjection,connection_params={'name':'V1toV2'})
        self.s.connect(self.retina,self.V2,delay=0.5,connection_type=KernelProjection,connection_params={'name':'RtoV2'})



    def test_measurefeaturemap(self):
        """
        
        """
        self.feature_param = {"theta": ( (0.0,1.0), 0.5, True),
                              "phase": ( (0.0,1.0), [0.2,0.4,0.6], False)}
        
        self.x = MeasureFeatureMap(self.s, self.feature_param)
        print self.V1.activity

        # This calls the default input_command in MeasureFeatureMap.
        # Also should test a user-defined input_command, but this depends
        # on a change to be made in MeasureFeatureMap.
        self.x.pattern_present_update()

        print self.x.list_param
        print self.x.sheet_featuremaps
        
        print self.x.sheet_featuremaps[self.V1]['theta'].distribution_matrix[0,0]
	print self.x.sheet_featuremaps[self.V1]['phase'].distribution_matrix[0,0]
        
	print self.x.sheet_featuremaps[self.V1]['theta'].distribution_matrix[0,0]._data
	print self.x.sheet_featuremaps[self.V1]['phase'].distribution_matrix[0,0]._data	

	print self.x.sheet_featuremaps[self.V1]['theta'].distribution_matrix[1,1]._data       
	print self.x.sheet_featuremaps[self.V1]['phase'].distribution_matrix[1,1]._data       

	
        print self.x.sheet_featuremaps[self.V2]['theta'].distribution_matrix[0,0]
	print self.x.sheet_featuremaps[self.V2]['phase'].distribution_matrix[0,0]
        
	print self.x.sheet_featuremaps[self.V2]['theta'].distribution_matrix[0,0]._data
	print self.x.sheet_featuremaps[self.V2]['phase'].distribution_matrix[0,0]._data	

	print self.x.sheet_featuremaps[self.V2]['theta'].distribution_matrix[1,1]._data       
	print self.x.sheet_featuremaps[self.V2]['phase'].distribution_matrix[1,1]._data       

        print self.V1.sheet_view_dict.keys()
        print self.V2.sheet_view_dict.keys()

	print self.x.sheet_featuremaps[self.V2]['theta'].preference()
        print self.x.sheet_featuremaps[self.V1]['theta'].preference()
        

suite = unittest.TestSuite()
suite.addTest(unittest.makeSuite(TestMeasureFeatureMap))


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite)
