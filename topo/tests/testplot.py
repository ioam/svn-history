"""
Test for the Plot class.

$Id$
"""
__version__='$Revision$'


import unittest
from pprint import pprint
from topo.plotting import plot
from topo.base.sheet import *
from topo.plotting.bitmap import RGBMap, HSVMap
from topo.base.patterngenerator import ImageGenerator

SHOW_PLOTS = False


### JC: My new imports
from topo.plotting.plot import Plot
from Numeric import zeros, divide, Float, ones
from topo.base.boundingregion import BoundingBox
from topo.base.sheetview import SheetView
from topo.plotting.bitmap import matrix_hsv_to_rgb
import MLab
import RandomArray


from random import random


### JCALERT! there is still some part to be written in this file 
###  when the fundamental changes in plot.py
### plotengine.py and plotgroup.py will be finished.
### for the moment, the tests are commented out...

class TestPlot(unittest.TestCase):

    def setUp(self):

	### Simple case: we only pass a dictionnary to Plot()
        ### that does not belong to a Sheet:
	self.view_dict = {}

	### SheetView1:
	### Find a way to assign randomly the matrix.
	self.matrix1 = zeros((10,10),Float) + RandomArray.random((10,10))
	self.bounds1 = BoundingBox(points=((-0.5,-0.5),(0.5,0.5)))
	self.sheet_view1 = SheetView((self.matrix1,self.bounds1),
				      src_name='TestInputParam',view_type='Pattern')
	self.key1 = 'sv1'
	self.view_dict[self.key1] = self.sheet_view1

        ### SheetView2:
	### Find a way to assign randomly the matrix.
	self.matrix2 = zeros((10,10),Float) + 0.3
	self.bounds2 = BoundingBox(points=((-0.5,-0.5),(0.5,0.5)))
	self.sheet_view2 = SheetView((self.matrix2,self.bounds2),
				      src_name='TestInputParam',view_type='Pattern')
	self.key2 = ('sv2',0,10)
	self.view_dict[self.key2] = self.sheet_view2

        ### SheetView3:
	### Find a way to assign randomly the matrix.
	self.matrix3 = zeros((10,10),Float) + RandomArray.random((10,10))
	self.bounds3 = BoundingBox(points=((-0.5,-0.5),(0.5,0.5)))
	self.sheet_view3 = SheetView((self.matrix3,self.bounds3),
				      src_name='TestInputParam',view_type='Pattern')
	self.key3 = ('sv3',0,'hello',(10,0))
	self.view_dict[self.key3] = self.sheet_view3

        ### SheetView4: for testing clipping + different bounding box
	### Find a way to assign randomly the matrix.
	self.matrix4 = zeros((10,10),Float) + 1.6
	self.bounds4 = BoundingBox(points=((-0.7,-0.7),(0.7,0.7)))
	self.sheet_view4 = SheetView((self.matrix4,self.bounds4),
				      src_name='TestInputParam',view_type='Pattern')
	self.key4 = 'sv4'
	self.view_dict[self.key4] = self.sheet_view4

	### JCALERT! for the moment we can only pass a triple when creating plot
        ### adding more sheetView to test when plot will be fixed for accepting
        ### as much as you want.

	# plot0: empty plot + no sheetviewdict passed: error or empty plot?
        ### JCALERT! It has to be fixed what to do in this case in plot..
        ### disabled test for the moment.
       	#self.plot0 = Plot((None,None,None),None,name='plot0')
	### CATCH EXCEPTION

	# plot1: empty plot 
	self.plot1 = Plot((None,None,None),self.view_dict,name='plot1')
				   
        # plot2: sheetView 1, no normalize, no clipping
	self.plot2 = Plot((self.key1,None,None),self.view_dict,name='plot2')
 
	# plot3: sheetView 1+2, no normalize, no clipping
	self.plot3 = Plot((self.key1,self.key2,None),self.view_dict,name='plot3')

	# plot4: sheetView 1+2+3, no normalize , no clipping 
	self.plot4 = Plot((self.key1,self.key2,self.key3),self.view_dict,name='plot4')

	# plot5: sheetView 1+3, no normalize, no clipping
	self.plot5 = Plot((self.key1,None,self.key3),self.view_dict,name='plot5')

	# plot6: sheetView 2+3, no normalize , no clipping 
	self.plot6 = Plot((None,self.key2,self.key3),self.view_dict,name='plot6')

	# plot7: sheetView 1+2+3, no normalize , clipping 
	self.plot7 = Plot((self.key4,self.key2,self.key3),self.view_dict,name='plot7')

	# plot8: sheetView 1+2+3, normalize , no clipping 
	self.plot8 = Plot((self.key1,self.key2,self.key3),self.view_dict,normalize=True,name='plot8')

	### JCALERT! FOR THE MOMENT I TAKE THE DEFAULT FOR NORMALIZE.
        ### WE WILL SEE IF IT REMAINS IN PLOT FIRST.

	### also makes a sheet to test realease_sheetviews

	self.sheet = Sheet()
	self.sheet.sheet_view_dict[self.key1]=self.sheet_view1
	self.sheet.sheet_view_dict[self.key2]=self.sheet_view2
	self.sheet.sheet_view_dict[self.key3]=self.sheet_view3
	self.sheet.sheet_view_dict[self.key4]=self.sheet_view4

	self.plot9 = Plot((self.key1,self.key2,self.key3),self.sheet.sheet_view_dict,name='plot9')

	
	

    def test_plot(self):

	### JCALERT! make a test for plot0

	# plot 1
	self.plot1.plot()
	test = [None,None,None]
	self.assertEqual(self.plot1.matrices,test)

	# plot 2
	self.plot2.plot()
	sat = zeros((10,10),Float) 
	hue = zeros((10,10),Float)
	val = self.matrix1

	test = matrix_hsv_to_rgb(hue,sat,val)
	for each1,each2 in zip(self.plot2.matrices,test):
	    for each3,each4 in zip(each1.flat,each2.flat):
		self.assertAlmostEqual(each3,each4)

	# plot 3
        self.plot3.plot()
	sat = ones((10,10),Float) 
	hue = zeros((10,10),Float) + 0.3
	val = self.matrix1

	test = matrix_hsv_to_rgb(hue,sat,val)
	for each1,each2 in zip(self.plot3.matrices,test):
	    for each3,each4 in zip(each1.flat,each2.flat):
		self.assertAlmostEqual(each3,each4)  

	# plot 4
	self.plot4.plot()
	sat = self.matrix3 
	hue = zeros((10,10),Float) + 0.3
	val = self.matrix1

	test = matrix_hsv_to_rgb(hue,sat,val)
	for each1,each2 in zip(self.plot4.matrices,test):
	    for each3,each4 in zip(each1.flat,each2.flat):
		self.assertAlmostEqual(each3,each4)  

	# plot 5
	self.plot5.plot()
	sat = zeros((10,10),Float) 
	hue = zeros((10,10),Float) 
	val = self.matrix1

	test = matrix_hsv_to_rgb(hue,sat,val)
	for each1,each2 in zip(self.plot5.matrices,test):
	    for each3,each4 in zip(each1.flat,each2.flat):
		self.assertAlmostEqual(each3,each4)

	# plot 6
	self.plot6.plot()
	sat = self.matrix3 
	hue = zeros((10,10),Float) + 0.3 
	val = ones((10,10),Float) 

	test = matrix_hsv_to_rgb(hue,sat,val)
	for each1,each2 in zip(self.plot6.matrices,test):
	    for each3,each4 in zip(each1.flat,each2.flat):
		self.assertAlmostEqual(each3,each4)  
    
	# plot 7
	self.plot7.plot()
	sat = self.matrix3 
	hue = zeros((10,10),Float) + 0.3 
	val = self.matrix4

        val = MLab.clip(val,0.0,1.0)
	
	test = matrix_hsv_to_rgb(hue,sat,val)
	for each1,each2 in zip(self.plot7.matrices,test):
	    for each3,each4 in zip(each1.flat,each2.flat):
		self.assertAlmostEqual(each3,each4)
	

	# plot 8
	self.plot8.plot()
	sat = self.matrix3 
	hue = zeros((10,10),Float) + 0.3 
	val = self.matrix1

	val = divide(val,float(max(val.flat)))
	
	test = matrix_hsv_to_rgb(hue,sat,val)

	for each1,each2 in zip(self.plot8.matrices,test):
	    for each3,each4 in zip(each1.flat,each2.flat):
		self.assertAlmostEqual(each3,each4)




	# plot 9
	self.plot9.plot()
	sat = self.matrix3 
	hue = zeros((10,10),Float) + 0.3 
	val = self.matrix1
	
	test = matrix_hsv_to_rgb(hue,sat,val)
	for each1,each2 in zip(self.plot9.matrices,test):
	    for each3,each4 in zip(each1.flat,each2.flat):
		self.assertAlmostEqual(each3,each4)  

#### Think about doing a plot test using sheet_dict and a sheet?
### Ask Jim if it is really necessary...

def test_release_sheetviews(self):

    self.plot9.release_sheetviews()

    test=self.sheet.sheet_view_dict.get(self.key1,None)
    self.assertEqual(test,None)
    test=self.sheet.sheet_view_dict.get(self.key2,None)
    self.assertEqual(test,None)
    test=self.sheet.sheet_view_dict.get(self.key3,None)
    self.assertEqual(test,None)
    test=self.sheet.sheet_view_dict.get(self.key4,None)
    self.assertEqual(test,self.sv4)


### JC: THIS CODE IS LEFT TEMPORARY IN CASE IT IS OF ANY USE IN NEAR FUTURE
    
#         x = plot.Plot(('Activity',None,None),plot.COLORMAP,self.s2)
#         for o in dir():
#             # pprint(o)
#             if isinstance(o,plot.Plot):
#                 o.warning('Found ', o.name)

#         input = ImageGenerator(filename='topo/tests/testsheetview.ppm',
#                          density=100,
#                          bounds=BoundingBox(points=((-0.8,-0.8),(0.8,0.8))))
#         sv = input.sheet_view('Activity')

#         # Defined sheetview in the R channel
#         plot1 = plot.Plot((None,None,sv),plot.COLORMAP)
#         p_tuple = plot1.plot()
#         (r, g, b) = p_tuple.matrices
#         map = RGBMap(r,g,b)
#         if SHOW_PLOTS: map.show()


#     def test_HSV_plot(self):
#         input = ImageGenerator(filename='topo/tests/testsheetview.ppm',
#                          density=100,
#                          bounds=BoundingBox(points=((-0.8,-0.8),(0.8,0.8))))
#         sv = input.sheet_view('Activity')

#         # Defined sheetview in the R channel
#         plot1 = plot.Plot((sv,sv,sv),plot.HSV)
#         p_tuple = plot1.plot()
#         (r, g, b) = p_tuple.matrices
#         map = HSVMap(r,g,b)
#         if SHOW_PLOTS: map.show()

#     def test_plottemplate(self):
#         pt = plot.PlotTemplate()
#         pt = plot.PlotTemplate({'Strength'   : None,
#                                 'Hue'        : 'HueP',
#                                 'Confidence' : None})
#         pt = plot.PlotTemplate(channels={'Strength'   : None,
#                                          'Hue'        : 'HueP',
#                                          'Confidence' : None})



suite = unittest.TestSuite()
suite.addTest(unittest.makeSuite(TestPlot))
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite)
