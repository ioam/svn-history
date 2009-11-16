"""

$Id$
"""
__version__='$Revision$'

# CEBALERT: incomplete!

import unittest
from numpy.testing import assert_array_almost_equal

from topo import pattern 
import topo.pattern.audio

class TestAudio(unittest.TestCase):

    def setUp(self):
        self.audio = pattern.audio.Audio(filename="sounds/test.wav")

    def test_basic(self):
        result = self.audio()


suite = unittest.TestSuite()
suite.addTest(unittest.makeSuite(TestAudio))
