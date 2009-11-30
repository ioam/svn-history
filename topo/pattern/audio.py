"""
Pattern generators for audio signals.


$Id$
"""
__version__='$Revision$'


# how much preprocessing to offer? E.g. Offer to remove DC? Etc.

import numpy

try:
    import scikits.audiolab as pyaudiolab
except ImportError:
    param.Parameterized().warning("scikits.audiolab (pyaudiolab) must be available to use audio.py")

import param
from param.parameterized import as_uninitialized,ParamOverrides

from topo.base.sheetcoords import SheetCoordinateSystem
from topo.misc.filepath import Filename
from topo.pattern.basic import PatternGenerator



# CEBALERT: should be in pattern.basic
class OneDPowerSpectrum(PatternGenerator):
    """
    ** This class has not been tested, and is still being written **
    
    Returns the spectral density of a rolling window of the input
    signal each time it is called. Over time, outputs a spectrogram.
    """

    window_length = param.Number(default=4,constant=True,doc="""
        The most recent portion of the signal on which to perform the
        Fourier transform, in units of 1/sample_rate.

        The Fourier transform algorithm is most efficient for powers
        of 2 (or can be decomposed into small prime factors - see
        numpy.fft.rfft).""")

    window_overlap = param.Number(default=1,constant=True,doc="""
        The amount of overlap between each window, in units of 
        1/sample_rate.""")

    sample_rate = param.Number(default=100,constant=True,doc="""
        Defines the unit for frequency.""")

    windowing_function = param.Parameter(default=numpy.hanning,constant=True,doc="""
        This function is multiplied with the window most recent portion of the waveforminterval of signal before
        performing the Fourier transform (i.e. it is used to shape the
        interval).

        The function chosen here dictates the tradeoff between
        resolving comparable signal strengths with similar
        frequencies, and resolving disparate signal strengths with
        dissimilar frequencies.

        numpy provides a number of options, e.g. bartlett, blackman,
        hamming, hanning, kaiser; see
        http://docs.scipy.org/doc/numpy/reference/routines.window.html. You
        can also supply your own.""")

    min_frequency = param.Number(default=1,doc="""
        Smallest frequency for which to return an amplitude.""")

    max_frequency = param.Number(default=10,doc="""
        Largest frequency for which to return an amplitude.""")


    def __init__(self,signal=[1]*24,**params):
        super(OneDPowerSpectrum,self).__init__(**params)
        self._initialize_window_parameters(signal)


    @as_uninitialized
    def _initialize_window_parameters(self,signal,**params):
        # CEBALERT! For subclasses: to specify the values of
        # parameters on this, the parent class, subclasses might first
        # need access to their own parameter values. Having the window
        # initialization in this separate method allows subclasses to
        # make the usual super.__init__(**params) call.
        for n,v in params.items():
            setattr(self,n,v)

        self._window_samples = int(self.window_length*self.sample_rate)
        self._overlap_samples = int(self.window_overlap*self.sample_rate)
        
        self.signal = numpy.asarray(signal,dtype=numpy.float32)
        assert len(self.signal)>0 

        self.location = 0
        
        self._all_frequencies = numpy.fft.fftfreq(
            self._window_samples,
            d=1.0/self.sample_rate)[0:self._window_samples/2]

        assert self._all_frequencies.min()>=0 # depends on numpy.fftfreq ordering

        self.smoothing_window = self.windowing_function(self._window_samples)  


    def _create_indices(self,p):
        # given all the constant params, could do some caching

        if not self._all_frequencies.min()<=p.min_frequency or not self._all_frequencies.max()>=p.max_frequency:
            raise ValueError("Specified frequency interval [%s,%s] is unavailable (actual interval is [%s,%s]. Adjust sample_rate and/or window_length."%(p.min_frequency,p.max_frequency,self._all_frequencies.min(),self._all_frequencies.max()))

        shape = SheetCoordinateSystem(p.bounds,p.xdensity,p.ydensity).shape

        # index of closest to minimum and maximum
        mini = numpy.nonzero(self._all_frequencies>=p.min_frequency)[0][0]
        maxi = numpy.nonzero(self._all_frequencies<=p.max_frequency)[0][-1]

        self._frequency_indices=self._generate_frequency_indices(mini,maxi,shape[0])#row
        self.frequencies = self._all_frequencies[self._frequency_indices]

        # How many times to repeat the 1d output for the specified 2d bounds.
        # Probably a better alternative would be to treat the second
        # dimension as a stack or temporal buffer.
        self._column_repeat = shape[1]#col
        if self._column_repeat > 1:
            self.warning("Shape mismatch: 1D output will be repeated to fill the array.")

    def _generate_frequency_indices(self,mini,maxi,length):
        # linear selection
        return numpy.linspace(mini,maxi,num=length,endpoint=True).astype(int)


    def __call__(self,**params_to_override):
        """
        Perform a real Discrete Fourier Transform (DFT; implemented
        using a Fast Fourier Transform algorithm, FFT) of the current
        sample from the signal multiplied by the smoothing window.

        See numpy.rfft for information about the Fourier transform.
        """
        p = ParamOverrides(self,params_to_override)
        self._create_indices(p)

        self.location+=self._window_samples
        end = self.location-self._overlap_samples
        start = end-self._window_samples

        if start < 0:
            # enough signal hasn't yet passed through to fill window
            signal_sample = numpy.zeros(self.smoothing_window.shape)
        elif end > self.signal.size:
            # Could loop around and print warning. 

            # Consider how to provide good support for the presumably
            # common use case of having a directory full of auditory
            # samples from which to choose in a random order, with
            # each one having a different length.  In that case one
            # will want to have some indication of when a sample as
            # run out, in order to move on to the next one.  Maybe
            # there needs to be a special AudioComposite generator to
            # do that, and eventually that would allow mixing of
            # signals too.
            raise ValueError("Reached the end of the signal.")
        else:
            signal_sample = self.signal[start:end]

        all_amplitudes = numpy.abs(numpy.fft.rfft(
                signal_sample*self.smoothing_window))[0:len(signal_sample)/2]

        amplitudes = all_amplitudes[self._frequency_indices].reshape((len(self._frequency_indices),1))

        # tile to get a 2d array where the 1 column is repeated; see
        # comment by self._column_repeat
        return numpy.tile(amplitudes,(1,self._column_repeat))
    
    

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



