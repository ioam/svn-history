import unittest

class TestPlotPannel(unittest.TestCase):
    def test_add(self):
        self.assertEqual(1+1,2)



suite = unittest.TestSuite()
#  Uncomment the following line of code, to not run the test if
#  $DISPLAY is undefined.  Used mainly for GUI testing.
suite.requires_display = True
suite.addTest(unittest.makeSuite(TestPlotPannel))
