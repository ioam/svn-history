"""
Pattern generators for audio signals.


$Id$
"""
__version__='$Revision$'

import numpy
import numpy.fft
import pyaudiolab

from topo.base.patterngenerator import PatternGenerator
from topo.base.parameterclasses import Filename,Integer,Parameter



# CEBALERT: will split into topo.patterns.basic.OneDPowerSpectrum(PatternGenerator)
# and topo.patterns.audio.Audio(OneDPowerSpectrum).


# CB: being a PatternGenerator gives this lots of parameters that don't really
# mean anything.
class Audio(PatternGenerator):
    """
    Performs a discrete Fourier transform each time it's called,
    on a rolling window of the signal.
    
    Over time, outputs a power spectrum.

    ** This class has not been tested, and is not documented **
    """
    # CB: find a decent example sound (I haven't listened to this)
    filename = Filename(default='examples/test.flac',precedence=0.9,doc=
        """
        File path (can be relative to Topographica's base path) to an audio file.
        The audio can be in any format accepted by pyaudiolab, e.g. WAV, AIFF, or FLAC.
        """)

    windowing_function = Parameter(default=numpy.hanning)

    # CEBALERT: parameters are not sampling-rate independent
    window_length = Integer(default=12)

    window_overlap = Integer(default=2)
    
    # CB: add option to select a section of the file to use; use all
    # by default.
    def __init__(self,**params):
        """
        Read the audio file into an array.
        """
        super(Audio,self).__init__(**params)
        self._source = pyaudiolab.sndfile(params.get('filename',self.filename),'read')

        # CB: add pre-processing options (e.g. remove DC) here? Or users should do them
        # first if they want them?

        n_frames = self._source.get_nframes()        
        self.signal = self._source.read_frames(n_frames,dtype=numpy.float32)

        # current position of 'read pointer' in the signal
        self.location = 0

        self.sample_rate = self._source.get_samplerate()
        

    def __call__(self,**params):
        """
        Perform a DFT (FFT) of the current sample from the signal multiplied
        by the smoothing window.
        """
        # CB: How much to explain in docstring? numpy.fft.fft has
        # documentation e.g. numpy.fft.fft most efficient if
        # window_length 'is a power of 2 (or decomposable into low
        # prime factors)', and what the output represents.


        # currently these can all be changed each call: is that useful?
        # (unusual for creating a spectrogram)
        n_frames = params.get('window_length',self.window_length)
        overlap = params.get('window_overlap',self.window_overlap)
        w_func = params.get('windowing_function',self.windowing_function)
        
        start = max(self.location-overlap,0)
        end = start+n_frames
        signal_sample = self.signal[start:end]

        self.location+=n_frames

        # make the frequencies easily available; would be calc'd only once
        # if the above parameters were constant
        self.last_freq = numpy.fft.fftfreq(n_frames,d=1.0/self.sample_rate)

        # again, would store if above parameters were constant
        smoothing_window = w_func(n_frames)  

        return numpy.fft.fft(signal_sample*smoothing_window)
    




