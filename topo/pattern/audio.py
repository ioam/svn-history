"""
Pattern generators for audio signals.


$Id$
"""
__version__='$Revision$'

import numpy
import param

from topo.misc.filepath import Filename
from topo.pattern.basic import Spectrogram

try:
    import scikits.audiolab as pyaudiolab
except ImportError:
    param.Parameterized().warning("scikits.audiolab (pyaudiolab) must be available to use audio.py")


class Audio(Spectrogram):
    """
    Returns the spectral density of a rolling window of the input
    audio signal each time it is called. Over time, outputs an audio
    spectrogram.
    """

    filename=Filename(default='sounds/complex/daisy.wav',precedence=0.9,doc="""
        File path (can be relative to Topographica's base path) to an
        audio file. The audio can be in any format accepted by pyaudiolab, 
        e.g. WAV, AIFF, or FLAC.""")
    
    # BKALERT: Should eventually make this class return the spectrogram 
    # laid on an accurate cochlear map (or at least have the option to).
    # To do so we need to define our own cochlear space, and extend 
    # PowerSpectrum to accept a space parameter, which isn't *that* hard, 
    # but it'll take a while and its not currently a priority.

    # CEBALERT: should make super's window_length, window_overlap,
    # sample_rate, and windowing_function be read-only/hidden for
    # users of this class.
    
    def __init__(self, **params):
        # overload default filename if a new one is supplied
        for parameter,value in params.items():
            if parameter == "filename":
                setattr(self,parameter,value)
                break
        
        # load file from disk.
        self._source=pyaudiolab.Sndfile(self.filename, 'r')
        # read its contents as a float32 array.
        super(Audio, self).__init__(signal=self._source.read_frames(self._source.nframes, dtype=numpy.float32), 
                                    sample_rate=self._source.samplerate, **params)

            
if __name__=='__main__' or __name__=='__mynamespace__':

    from topo import sheet
    import topo

    topo.sim['C']=sheet.GeneratorSheet(
        input_generator=Audio(filename='sounds/sine_waves/20000.wav',sample_window=0.3,
            seconds_per_timestep=0.1,min_frequency=20,max_frequency=20000),
            nominal_bounds=sheet.BoundingBox(points=((-0.1,-0.5),(0.0,0.5))),
            nominal_density=10,period=1.0,phase=0.05)


