import unittest

class TestPlot(unittest.TestCase):
    def SetUp(self):
        self.assertEqual(1+1,2)

    def test_add(self):
        self.assertEqual(1+1,2)



suite = unittest.TestSuite()
suite.addTest(unittest.makeSuite(TestPlot))
