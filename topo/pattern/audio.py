"""
Pattern generators for audio signals.


$Id$
"""
__version__='$Revision$'


# how much preprocessing to offer? E.g. Offer to remove DC? Etc.

import numpy
import param

from topo.misc.filepath import Filename
from topo.pattern.basic import PatternGenerator, OneDPowerSpectrum
from param.parameterized import as_uninitialized, ParamOverrides

try:
    import scikits.audiolab as pyaudiolab

except ImportError:
    param.Parameterized().warning("scikits.audiolab (pyaudiolab) must be available to use audio.py")



class Spectrogram(OneDPowerSpectrum):
    """
    Returns the spectral density of a rolling window of the input
    audio signal each time it is called. Over time, outputs an audio
    spectrogram.
    """

    filename=Filename(default='sounds/complex/daisy.wav',constant=True,precedence=0.9,doc="""
        File path (can be relative to Topographica's base path) to an
        audio file.  The audio can be in any format accepted by
        pyaudiolab, e.g. WAV, AIFF, or FLAC.""")

    seconds_per_timestep=param.Number(default=1.0,constant=True,doc="""
        Number of seconds represented by 1 simulation time step.""")

    sample_window=param.Number(default=1.0,constant=True,doc="""
        The length of interval of the signal (in seconds) on which to
        perform the Fourier transform.

        How much history of the signal to include in the window.
        sample_window > seconds_per_timestep -> window overlap
                                         
        The Fourier transform algorithm is most efficient if the
        resulting window_length(sample_window * sample_rate) is a
        power of 2, or can be decomposed into small prime factors; see
        numpy.fft.""")

    # CEBALERT: should make super's window_length, window_overlap,
    # sample_rate, and windowing_function be read-only/hidden for
    # users of this class.
    def __init__(self, **params):
        PatternGenerator.__init__(self, **params)
        self._source=pyaudiolab.Sndfile(self.filename, 'r')

        if self.sample_window < self.seconds_per_timestep:
            self.warning("sample_window < seconds_per_timestep; some signal will be skipped.")

        self._initialize_window_parameters(signal=self._source.read_frames(self._source.nframes, dtype=numpy.float32), 
                                           sample_rate=self._source.samplerate,
                                           window_length=self.seconds_per_timestep,
                                           window_overlap=self.sample_window-self.seconds_per_timestep)
    
    
    def _initialize_window_parameters(self, signal, **params):
        # this is used by _create_indices when initialising the spectrogram array
        self._first_run = True
        
        super(Spectrogram, self)._initialize_window_parameters(signal, **params)
        
    
    # BKALERT: accurate cochlear map is very simple but we need to define our own space.
    #          again, not hard or long, just not currently a priority
    def _generate_frequency_indices(self, mini, maxi, length):
        return numpy.logspace(numpy.log10(maxi),numpy.log10(mini),num=length,endpoint=True).astype(int)
        #return numpy.linspace(maxi, mini, num = length, endpoint = True).astype(int)


    def _create_indices(self, p):
        super(Spectrogram, self)._create_indices(p)

        # initalise a new, empty, spectrogram of the size of the sheet
        # ie implicitly control buffer size through sheet size 
        if self._first_run:
            self._spectrogram = numpy.zeros(self.sheet_shape, dtype = numpy.float32)
            self._first_run = False
            
            
    def __call__(self, **params_to_override):
        """
        Return a spectrogram by performing a real Discrete Fourier 
        Transform (DFT; implemented using a Fast Fourier Transform 
        algorithm, FFT) of the next sample segment in the signal, 
        appended to the previous spectral history.

        See numpy.rfft for information about the Fourier transform.
        """
        amplitudes = super(Spectrogram, self)._do_fft(**params_to_override)
        
        # add on latest spectral information to the left edge
        self._spectrogram = numpy.hstack((amplitudes, self._spectrogram))
                
        # knock off the column on the right-most edge
        self._spectrogram = self._spectrogram[0:, 0:self._spectrogram.shape[1]-1]
        return self._spectrogram
        

if __name__=='__main__' or __name__=='__mynamespace__':

    from topo import sheet
    import topo

    topo.sim['C']=sheet.GeneratorSheet(
        input_generator=Spectrogram(filename='sounds/complex/daisy.wav',sample_window=0.3,
            seconds_per_timestep=0.1,min_frequency=20,max_frequency=20000),nominal_density=10,
            nominal_bounds=sheet.BoundingBox(points=((-0.1,-0.5),(0.0,0.5))),period=1.0,phase=0.05)


