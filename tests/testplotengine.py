import unittest

class TestPlotEngine(unittest.TestCase):
    def test_add(self):
        self.assertEqual(1+1,2)



suite = unittest.TestSuite()
suite.addTest(unittest.makeSuite(TestPlotEngine))
