import unittest

class TestDummy(unittest.TestCase):
    def test_add(self):
        self.assertEqual(1+1,2)



suite = unittest.TestSuite()
suite.addTest(unittest.makeSuite(TestDummy))
