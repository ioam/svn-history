"""
Pattern generators for audio signals.


$Id$
"""
__version__='$Revision$'


# how much preprocessing to offer? E.g. Offer to remove DC? Etc.

import numpy
import param
from param.parameterized import as_uninitialized,ParamOverrides

try:
    import scikits.audiolab as pyaudiolab
except ImportError:
    param.Parameterized().warning("scikits.audiolab (pyaudiolab) must be available to use audio.py")

from topo.misc.filepath import Filename
from topo.pattern.basic import PatternGenerator,OneDPowerSpectrum



class Audio(OneDPowerSpectrum):
    """
    ** Untested: currently being written. ** 
    """

    filename = Filename(default='sounds/test.wav',constant=True,precedence=0.9,doc="""
        File path (can be relative to Topographica's base path) to an
        audio file.  The audio can be in any format accepted by
        pyaudiolab, e.g. WAV, AIFF, or FLAC.""")

    seconds_per_timestep = param.Number(constant=True,default=1.0,doc="""
        Number of seconds represented by 1 simulation time step.""")

    sample_window = param.Number(default=2.0,constant=True,doc="""
        The length of interval of the signal (in seconds) on which to
        perform the Fourier transform.

        How much history of the signal to include in the window.
        sample_window>seconds_per_timestep -> window overlap
    
        The Fourier transform algorithm is most efficient if the
        resulting window_length (sample_window*sample_rate) is a power
        of 2 (or can be decomposed into small prime factors - see
        numpy.fft).
        """)

    # CEBALERT: should make super's window_length, window_overlap,
    # sample_rate, and windowing_function be read-only/hidden for
    # users of this class.

    def __init__(self,**params):
        PatternGenerator.__init__(self,**params)
        self._source = pyaudiolab.Sndfile(self.filename,'r')

        if self.sample_window<self.seconds_per_timestep:
            self.warning("sample_window<seconds_per_timestep; some signal will be skipped.")

        self._initialize_window_parameters(
            signal=self._source.read_frames(
                self._source.nframes,dtype=numpy.float32),
            sample_rate=self._source.samplerate,
            window_length=self.seconds_per_timestep,
            window_overlap=self.sample_window-self.seconds_per_timestep)


    def _generate_frequency_indices(self,mini,maxi,length):
        # logarithmic selection
        return numpy.logspace(numpy.log10(mini),numpy.log10(maxi),
                              num=length,endpoint=True).astype(int)



if __name__=='__main__' or __name__=='__mynamespace__':

    from topo import sheet
    import topo

    topo.sim['C']=sheet.GeneratorSheet(
        input_generator = Audio(filename='sounds/test.wav',
                                sample_window=0.3,seconds_per_timestep=0.1,
                                min_frequency=100,max_frequency=10000),
        nominal_density=10,
        nominal_bounds=sheet.BoundingBox(points=((-0.1,-0.5),(0.0,0.5))),
        period=1.0, phase=0.05)



