"""
Pattern generators for audio signals.


$Id$
"""
__version__='$Revision$'

import numpy

# CEBALERT: you need to build pyaudiolab to use this file.
# (Not tested it on Windows or OS X.)
try:
    import scikits.audiolab as pyaudiolab
except ImportError:
    print "Warning: pyaudiolab must be built to use audio.py"

import param

from topo.misc.filepath import Filename

from topo.pattern.basic import PatternGenerator





# CEBALERT: should be in pattern.basic, but then it would appear in
# the GUI (which doesn't support any non-2D PGs...)
class OneDPowerSpectrum(PatternGenerator):
    """
    ** This class has not been tested, and is still being written **
    
    Returns the spectral density of a rolling window of the input signal
    each time it is called. Over time, outputs a spectrogram.
    """
    window_length = param.Integer(constant=True,default=2,doc="""
    The interval of the signal on which to perform the Fourier transform.
    
    The Fourier transform algorithm is most efficient if this is a power of 2
    (or can be decomposed into small prime factors - see numpy.fft).""")

    
    # CEBALERT: this should be constant, but setting it so gives an error
    windowing_function = param.Parameter(default=numpy.hanning,doc="""
    This function is multiplied with the interval of signal before performing the
    Fourier transform (i.e. it is used to shape the interval). 

    The function chosen here dictates the tradeoff between resolving comparable
    signal strengths with similar frequencies, and resolving disparate signal
    strengths with dissimilar frequencies.

    See  http://en.wikipedia.org/wiki/Window_function
    """)

    window_overlap = param.Integer(default=0,doc="""Amount of overlap between each window of
    the signal.""")
    
    sample_spacing = param.Number(constant=True,default=1.0,doc="""
    ...1/samplerate,relate to time, etc...""")
    
    
    def __init__(self,signal=[1,1,1,1],start_location=0,**params):
        """
        Reads the given signal into a float32 array.

        The current position of the 'read pointer' in the signal array
        is given by self.location. start_location allows the starting
        point to be set.

        self.frequencies gives the DFT's sample frequencies, matching
        the order returned by __call__().
        """
        super(OneDPowerSpectrum,self).__init__(**params)
        
        # CB: add pre-processing options (e.g. remove DC) here?
        # Or should users do them first, if they want them?

        self.signal = numpy.asarray(signal,dtype=numpy.float32)
        self.location = start_location
        self.frequencies = numpy.fft.fftfreq(self.window_length,d=self.sample_spacing)

        self.smoothing_window = self.windowing_function(self.window_length)  


    def __call__(self):
        """
        Perform a DFT (FFT) of the current sample from the signal multiplied
        by the smoothing window.

        See numpy.fft for information about the Fourier transform.
        """
        start = max(self.location-self.window_overlap,0)
        end = start+self.window_length
        signal_sample = self.signal[start:end]

        self.location+=self.window_length

        return numpy.fft.fft(signal_sample*self.smoothing_window) #,n=n_samples)



class Audio(OneDPowerSpectrum):
    """
    ** Untested: currently being written. ** 
    """
    # CB: find an example sound (I haven't listened to this one;
    # there's no signal in it for the first hundred or so frames).
    # Use a wav file.
    filename = Filename(
        default='test.wav',
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
        self._source = pyaudiolab.Sndfile(params.get('filename',self.filename),'r')
        sig =  self._source.read_frames(self._source.nframes,dtype=numpy.float32)
        spacing = 1.0/self._source.samplerate

        super(Audio,self).__init__(signal=sig,sample_spacing=spacing,**params)
                


if __name__=="__main__" or __name__=="__mynamespace__":
    print "testing topo.pattern.audio..."
    a = Audio()
    out = a()
    print "...finished."

