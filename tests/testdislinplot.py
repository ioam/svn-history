"""
Tests dislinplot.py by creating two test files using sample inputs.
This file depends on four input files in a test directory:

testdislin_od_noselect_bw.bmp
testdislin_or_Eye1_noselect.bmp
testdislin_or_od_select.bmp
testdislin_wts.056_085_s.bmp
testdislin_target.bmp

Two output files are created:

testdislinplot.eps
testdislinplot.tiff

The EPS file is left alone, but the generated tiff file is
compared to a target file to assert that the output is the
same as expected.

$Id$
"""
import unittest
import math, Image, ImageOps, os
import topo
import Image
from topo.dislinplot import *
from topo.dislindriver import *

TESTS_DIR = 'tests/testdislinplot/'

def compare_files(target_file, fresh_file):
    """
    Use a simple string compare between two image files.  Returns
    True if they have identical bitmap representations, and False
    otherwise.
    """
    target = Image.open(target_file).tostring()
    fresh = Image.open(fresh_file).tostring()
    if fresh == target:
        return True
    else:
        return False


class TestDislinPlot(unittest.TestCase):
    def test_dislinplot_1(self):
        "Template example for creating a tiff file from DislinPlot"
        # Set plot options for a tiff output file
        plot2 = dislinplot.DislinPlot()
        plot2.set_dislin_scale(False)              # Color will be 256
        plot2.set_bitmap_size(800)                 # Not used for postscript
        plot2.set_display('tiff')
        plot2.set_output_filename(TESTS_DIR + 'testdislinplot.tiff')
        plot2.set_xname('X Position')
        plot2.set_yname('Y Position')
        plot2.set_input_bmpfile(TESTS_DIR + 'testdislin_or_Eye1_noselect.bmp')

        # Remove the file if it already exists
        if os.access(TESTS_DIR + 'testdislinplot.tiff',os.F_OK):
            os.remove(TESTS_DIR + 'testdislinplot.tiff')

        # Open up the data file for conversion and put in a list
        image = Image.open(TESTS_DIR + 'testdislin_od_noselect_bw.bmp')
        imagebw = ImageOps.grayscale(image).rotate(270) # Rotated!??
        (width, height) = image.size
        pixels = list(imagebw.getdata())
    
        #Add contour, data, and then plot.  Parameter returned is actual filename.
        plot2.add_layer('NONE',255. / 2,255)
        plot2.add_grid(width,height,pixels)
        filename = plot2.genplot()
        # print 'Plot 2 file created and named: ', filename

        # Assert that the two files match
        assert(compare_files(TESTS_DIR + 'testdislin_target.tiff',TESTS_DIR + 'testdislinplot.tiff'))


    def test_dislinplot_2(self):
        "Template example for creating a postscript file from DislinPlot"
        plot2 = dislinplot.DislinPlot()
        plot2.set_dislin_scale(True)
        #plot2.set_bitmap_size(800)                 # Not used for postscript
        plot2.set_display('postscript')             # Or 'tiff'
        plot2.set_xname('X Position')
        plot2.set_yname('Y Position')
        plot2.set_input_bmpfile(TESTS_DIR + 'testdislin_or_Eye1_noselect.bmp')
        plot2.set_output_filename(TESTS_DIR + 'testdislinplot.eps')

        # Remove the file if it already exists
        if os.access(TESTS_DIR + 'testdislinplot.eps',os.F_OK):
            os.remove(TESTS_DIR + 'testdislinplot.eps')
    
        # Open up the data file for conversion and put in a list
        image = Image.open(TESTS_DIR + 'testdislin_od_noselect_bw.bmp')
        imagebw = ImageOps.grayscale(image).rotate(270) # Rotated!?? Fortran?
        (width, height) = image.size
        pixels = list(imagebw.getdata())
    
        #Add contour, data, and then plot.  Parameter returned is actual filename.
        plot2.add_layer('NONE',255. / 2,255)
        plot2.add_grid(width,height,pixels)
        filename = plot2.genplot()
        # print 'Plot 3 file created and named: ', filename


suite = unittest.TestSuite()
suite.addTest(unittest.makeSuite(TestDislinPlot))
