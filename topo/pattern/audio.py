"""
Pattern generators for audio signals.


$Id$
"""
__version__='$Revision$'

import numpy
import param
import os

from topo.misc.filepath import Filename
from topo.pattern.basic import Spectrogram
from numpy import float32, zeros

try:
    import scikits.audiolab as pyaudiolab
except ImportError:
    param.Parameterized().warning("scikits.audiolab (pyaudiolab) must be available to use audio.py")


class AudioFile(Spectrogram):
    """
    Returns a spectrogram, i.e. the spectral density over time 
    of a rolling window of the input audio signal.
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
        super(Audio, self).__init__(signal=self._source.read_frames(self._source.nframes, dtype=float32), 
                                    sample_rate=self._source.samplerate, **params)


class AudioFolder(Spectrogram):
    """
    Returns a spectrogram, i.e. the spectral density over time 
    of a rolling window of the input audio signal, for all files 
    in the specified folder.
    """
      
    folderpath=param.String(default='sounds/complex/',precedence=0.9,doc="""
        Folder path (can be relative to Topographica's base path) to a
        folder containing audio files. The audio can be in any format 
        accepted by pyaudiolab, e.g. WAV, AIFF, or FLAC.""")

    samplerate=param.Number(default=44100,precedence=0.9,doc="""
        The sample rate of the audio files contained in folderpath.
        All files must have the same sample rate.""")
        
    gap_between_sounds=param.Number(default=0.0,precedence=0.9,doc="""
        The gap in seconds to insert between consecutive soundfiles.""")
        
    def __init__(self, **params):
        # overload default foldername if a new one is supplied
        for parameter,value in params.items():
            if parameter == "folderpath":
                setattr(self,parameter,value)
                break
         
        combined_signal = zeros(self.samplerate,float32)
        
        # list all sound files in the directory
        all_files = os.listdir(self.folderpath)
        for file in all_files:
            if file[-4:]==".wav" or file[-3:]==".wv" \
                or file[-5:]==".aiff" or file[-4:]==".aif" \
                or file[-5:]==".flac":
                
                # get pylab to load the file
                source = pyaudiolab.Sndfile(self.folderpath+file, 'r')
                
                # make sure sample rates match
                if not (self.samplerate==source.samplerate):
                    raise ValueError("Sample rates of all audio files must match the \
                    sample rate specified. %s has a sample rate of %s, you specified a \
                    sample rate of %s." %(file, source.samplerate, self.samplerate))
                    
                # add the signal to the others
                combined_signal = numpy.hstack((combined_signal, source.read_frames(source.nframes, dtype=float32)))
                
                # if a gap between sounds was specified, add it.
                if (self.gap_between_sounds > 0.0):
                    combined_signal = numpy.hstack((combined_signal, zeros(self.samplerate*self.gap_between_sounds,float32)))
        
        super(AudioFolder, self).__init__(signal=combined_signal, sample_rate=self.samplerate, **params)
                  

if __name__=='__main__' or __name__=='__mynamespace__':

    from topo import sheet
    import topo

    topo.sim['C']=sheet.GeneratorSheet(
        input_generator=AudioFile(filename='sounds/sine_waves/20000.wav',sample_window=0.3,
            seconds_per_timestep=0.1,min_frequency=20,max_frequency=20000),
            nominal_bounds=sheet.BoundingBox(points=((-0.1,-0.5),(0.0,0.5))),
            nominal_density=10,period=1.0,phase=0.05)


