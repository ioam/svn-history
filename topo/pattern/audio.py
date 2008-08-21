"""
Pattern generators for audio signals.


$Id$
"""
__version__='$Revision$'

import numpy

# CEBALERT: you need to build pyaudiolab to use this file.
# (Not tested it on Windows or OS X.)
try:
    import pyaudiolab
except ImportError:
    print "Warning: pyaudiolab must be built to use audio.py"

from .. import param

from topo.misc.filepaths import Filename

from topo.pattern.basic import OneDPowerSpectrum



class Audio(OneDPowerSpectrum):
    """
    ** Untested: currently being written. ** 
    """
    # CB: find an example sound (I haven't listened to this one;
    # there's no signal in it for the first hundred or so frames).
    # Use a wav file.
    filename = Filename(
        default='lib/python2.4/site-packages/pyaudiolab/test_data/test.flac',
        precedence=0.9,doc=
        """
        File path (can be relative to Topographica's base path) to an audio file.
        The audio can be in any format accepted by pyaudiolab, e.g. WAV, AIFF, or FLAC.
        """)

    # CEBHACKALERT: make Audio's parameters window_length,overlap be independent of
    # the sampling rate.

    def __init__(self,**params):
        """
        Read the audio file into an array.
        """
        self._source = pyaudiolab.sndfile(params.get('filename',self.filename),'read')
        n_frames = self._source.get_nframes()        
        sig =  self._source.read_frames(n_frames,dtype=numpy.float32)
        spacing = 1.0/self._source.get_samplerate()

        super(Audio,self).__init__(signal=sig,sample_spacing=spacing,**params)
                


