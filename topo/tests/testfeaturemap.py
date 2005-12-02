"""
TestFeatureMap

$Id$

"""
__version__='$Revision $'



# CEB:
# This file is still being written

# To do:
# 


import unittest

from topo.base.utils import arg, wrap
from math import pi
from Numeric import array, exp
from topo.base.sheet import Sheet
from topo.base.boundingregion import BoundingBox

# for making a simulator:
from topo.sheets.generatorsheet import GeneratorSheet
from topo.base.connectionfield import CFProjection
from topo.sheets.cfsom import CFSOM
from topo.base.simulator import Simulator
from topo.learningfns.basic import HebbianSOM

from topo.patterns import basic
from topo.analysis.featuremap import FeatureMap, MeasureFeatureMap


class TestFeatureMap(unittest.TestCase):

    def setUp(self):

        # sheet to test. As it is, its activity matrix dimension is (3,2) 
        test_sheet = Sheet(density= 1, bounds= BoundingBox(points=((-1,-2),(1,1))))

        # simple activity arrays use to update the feature maps
        self.a1 = array([[1,1], [1,1], [1,1]])
        self.a2 = array([[3,3], [3,3], [3,3]])
        self.a3 = array([[0,1], [0,1], [0,1]])
        
        # object to test for non-cyclic distributions
        self.fm1 = FeatureMap(sheet=test_sheet, axis_range=(0.0,1.0), cyclic=False)
        self.fm1.update(self.a1,0.5)

        # object to for cyclic distributions
        self.fm2 = FeatureMap(sheet=test_sheet, axis_range=(0.0,1.0), cyclic=True)
        self.fm2.update(self.a1,0.5)


    # need to add a test_update()    


    def test_preference(self):
        
        for i in range(3):
            for j in range(2):
                self.assertAlmostEqual(self.fm1.preference()[i,j], 0.5)
                self.assertAlmostEqual(self.fm2.preference()[i,j], 0.5)


        # To test the update function     
        self.fm1.update(self.a1,0.7)
        self.fm2.update(self.a1,0.7)

        for i in range(3):
            for j in range(2):
                self.assertAlmostEqual(self.fm1.preference()[i,j], 0.6)
                vect_sum = wrap(0,1,arg(exp(0.7*2*pi*1j)+exp(0.5*2*pi*1j))/(2*pi)) 
                self.assertAlmostEqual(self.fm2.preference()[i,j],vect_sum) 
                                      
                                      

        
        # To test the keep_peak=True 
        self.fm1.update(self.a1,0.7)
        self.fm2.update(self.a1,0.7)

        for i in range(3):
            for j in range(2):
                self.assertAlmostEqual(self.fm1.preference()[i,j], 0.6)
                vect_sum =wrap(0,1,arg(exp(0.7*2*pi*1j)+exp(0.5*2*pi*1j))/(2*pi))
                self.assertAlmostEqual(self.fm2.preference()[i,j],vect_sum)
                                      
        self.fm1.update(self.a2,0.7)
        self.fm2.update(self.a2,0.7)

        for i in range(3):
            for j in range(2):
                self.assertAlmostEqual(self.fm1.preference()[i,j], 0.65)
                vect_sum =wrap(0,1,arg(3*exp(0.7*2*pi*1j)+exp(0.5*2*pi*1j))/(2*pi))
                self.assertAlmostEqual(self.fm2.preference()[i,j],vect_sum)

        # to even test more....
        
        self.fm1.update(self.a3,0.9)
        self.fm2.update(self.a3,0.9)
        
        for i in range(3):
            self.assertAlmostEqual(self.fm1.preference()[i,0], 0.65)
            self.assertAlmostEqual(self.fm1.preference()[i,1], 0.7)
            vect_sum = wrap(0,1,arg(3*exp(0.7*2*pi*1j)+exp(0.5*2*pi*1j))/(2*pi))
            self.assertAlmostEqual(self.fm2.preference()[i,0],vect_sum)
            vect_sum = wrap(0,1,arg(3*exp(0.7*2*pi*1j)+exp(0.5*2*pi*1j)+exp(0.9*2*pi*1j))/(2*pi))
            self.assertAlmostEqual(self.fm2.preference()[i,1],vect_sum)
            
                                          
    def test_selectivity(self):
        
        for i in range(3):
            for j in range(2):
                # when only one bin the selectivity is 1 (from C code)
                self.assertAlmostEqual(self.fm1.selectivity()[i,j], 1.0)
                self.assertAlmostEqual(self.fm2.selectivity()[i,j], 1.0)

        # To test the update function     
        self.fm1.update(self.a1,0.7)
        self.fm2.update(self.a1,0.7)

        for i in range(3):
            for j in range(2):
                proportion = 1.0/2.0
                offset = 1.0/2.0
                relative_selectivity = (proportion-offset)/(1.0-offset)  ## gives 0 ..?
                self.assertAlmostEqual(self.fm1.selectivity()[i,j],relative_selectivity)
                vect_sum = abs(exp(0.7*2*pi*1j)+exp(0.5*2*pi*1j))/2.0 
                self.assertAlmostEqual(self.fm2.selectivity()[i,j],vect_sum) 
                                      
                                      

        
        # To test the keep_peak=True 
        self.fm1.update(self.a1,0.7)
        self.fm2.update(self.a1,0.7)

        for i in range(3):
            for j in range(2):
                proportion = 1.0/2.0
                offset = 1.0/2.0
                relative_selectivity = (proportion-offset)/(1.0-offset)
                self.assertAlmostEqual(self.fm1.selectivity()[i,j],relative_selectivity)
                vect_sum = abs(exp(0.7*2*pi*1j)+exp(0.5*2*pi*1j))/2.0 
                self.assertAlmostEqual(self.fm2.selectivity()[i,j],vect_sum) 

                                                           
        self.fm1.update(self.a2,0.7)
        self.fm2.update(self.a2,0.7)

        for i in range(3):
            for j in range(2):
                proportion = 3.0/4.0
                offset = 1.0/2.0
                relative_selectivity = (proportion-offset)/(1.0-offset)
                #self.assertAlmostEqual(self.fm1.selectivity()[i,j],relative_selectivity)
                vect_sum = abs(3*exp(0.7*2*pi*1j)+exp(0.5*2*pi*1j))/4.0 
                self.assertAlmostEqual(self.fm2.selectivity()[i,j],vect_sum) 
                 
        # to even test more....
        
        self.fm1.update(self.a3,0.9)
        self.fm2.update(self.a3,0.9)
        
        for i in range(3):
            proportion = 3.0/4.0
            offset = 1.0/3.0 ### Carefull, do not create bins when it is 0
            ### Check with Bednar what is num_bins in the original C-file and see what he wants
            ### now for the selectivity ....
            relative_selectivity = (proportion-offset)/(1.0-offset)
            self.assertAlmostEqual(self.fm1.selectivity()[i,0], relative_selectivity)
            proportion = 3.0/5.0
            offset = 1.0/3.0
            relative_selectivity = (proportion-offset)/(1.0-offset)
            ### to fix this test as well
            #self.assertAlmostEqual(self.fm1.selectivity()[i,1], relative_selectivity)
            
            vect_sum = abs(3*exp(0.7*2*pi*1j)+exp(0.5*2*pi*1j))/4.0
            self.assertAlmostEqual(self.fm2.selectivity()[i,0],vect_sum)
            vect_sum = abs(3*exp(0.7*2*pi*1j)+exp(0.5*2*pi*1j)+exp(0.9*2*pi*1j))/5.0
            self.assertAlmostEqual(self.fm2.selectivity()[i,1],vect_sum)
             




class TestMeasureFeatureMap(unittest.TestCase):

    def setUp(self):
        """
        Create a CFSOM sheet ('V1') connected to a GeneratorSheet ('Retina').
        """
        self.s = Simulator()
        self.retina = GeneratorSheet(name='Retina')
        self.V1 = CFSOM(name='V1')
        self.s.connect(self.retina,self.V1,delay=0.5,connection_type=CFProjection,connection_params={'name':'RtoV1','learning_fn':HebbianSOM()})

        self.V2 = CFSOM(name='V2')


        #self.s.connect(self.V1,self.V2,delay=1,connection_type=CFProjection,connection_params={'name':'V1toV2'})
        self.s.connect(self.retina,self.V2,delay=0.5,connection_type=CFProjection,connection_params={'name':'RtoV2','learning_fn':HebbianSOM()})



    def test_measurefeaturemap(self):
        """
        
        """
        self.feature_param = {"orientation": ( (0.0,1.0), 0.5, True),
                              "phase": ( (0.0,1.0), [0.2,0.4,0.6], False)}
        
        self.x = MeasureFeatureMap(self.s, self.feature_param)
        #print self.V1.activity

        #### test has to be written!!!
        
cases = [TestFeatureMap,
         TestMeasureFeatureMap]

suite = unittest.TestSuite()
suite.addTests(unittest.makeSuite(case) for case in cases)
              
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=1).run(suite)


        


        
        

                
        

   
