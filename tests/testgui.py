import unittest
from topo.gui import *

class TestGui(unittest.TestCase):
    def test_Gui(self):
        True

    def test_Gui_2(self):
        True


suite = unittest.TestSuite()
suite.addTest(unittest.makeSuite(TestGui))
