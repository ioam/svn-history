import unittest

class TestSheetView(unittest.TestCase):
    def test_view(self):
        self.assertEqual(1+1,2)
    def test_sum_maps(self):
        self.assertEqual(1+1,2)



suite = unittest.TestSuite()
suite.addTest(unittest.makeSuite(TestSheetView))
