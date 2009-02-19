# Adding support for RGB images (work in progress)
import topo


from topo.sheet.basic import GeneratorSheet,FunctionEvent,PeriodicEventSequence,param,PatternGenerator
from topo import pattern

class ColorImageSheet(GeneratorSheet):
    """
    A GeneratorSheet that handles RGB images.

    Accepts either a single-channel or a RGB input_generator.  If the
    input_generator stores separate red, green, and blue patterns, it
    is used as-is; other (monochrome) PatternGenerators are first
    wrapped using ExtendToRGB to create the RGB patterns.

    When a pattern is generated, a monochrome version is sent out on
    the Activity port as usual for a GeneratorSheet, and red, green,
    and blue activities are sent out on the RedActivity,
    GreenActivity, and BlueActivity ports.  Thus this class can be used
    just like GeneratorSheet, but with optional color channels.
    """

    src_ports=['Activity','RedActivity','GreenActivity','BlueActivity']

    def __init__(self,**params):
        super(ColorImageSheet,self).__init__(**params)
        self.activity_red=self.activity.copy()
        self.activity_green=self.activity.copy()
        self.activity_blue=self.activity.copy()


    def set_input_generator(self,new_ig,push_existing=False):
        """Wrap new_ig in ExtendToRGB if necessary."""

        if not hasattr(new_ig,'red'):
            new_ig = ExtendToRGB(generator=new_ig)
            
        super(ColorImageSheet,self).set_input_generator(new_ig,push_existing=push_existing)

        
    def generate(self):
        """
        Works as in the superclass, but also generates RGB output and sends
        it out on the RedActivity, GreenActivity, and BlueActivity ports.
        """
        super(ColorImageSheet,self).generate()
        
        g = self.input_generator
        
        self.activity_red[:]   = g.red
        self.activity_green[:] = g.green
        self.activity_blue[:]  = g.blue
        
        if self.apply_output_fns:
            for output_fn in self.output_fns:
                output_fn(self.activity_red)
                output_fn(self.activity_green)
                output_fn(self.activity_blue)

        self.send_output(src_port='RedActivity',  data=self.activity_red)
        self.send_output(src_port='GreenActivity',data=self.activity_green)
        self.send_output(src_port='BlueActivity', data=self.activity_blue)




import copy
from topo.param.parameterized import ParamOverrides
class ExtendToRGB(PatternGenerator):
    """
    Wrapper for a single-channel (monochrome) PatternGenerator that
    synthesizes Red, Green, and Blue channels, e.g. for use with
    ColorImageSheet.
    """

    channels = ["red","green","blue"]

    generator = param.Parameter(default=pattern.Constant())

    channel_strengths = param.List([1.0/3,1.0/3,1.0/3]) # not sure what to call it

    def __init__(self,**params):
        super(ExtendToRGB,self).__init__(**params)
        for c in self.channels:
            setattr(self,c,None)

    def __call__(self,**params):
        p = ParamOverrides(self,params)

        # as for Selector etc, pass through certain parameters to
        # generator
        params['xdensity']=p.xdensity
        params['ydensity']=p.ydensity
        params['bounds']=p.bounds

        # (not **p because that would be extra parameters)
        gray = p.generator(**params)
        
        # CEB: method more complicated than it needs to be; maybe if
        # the various selector pattern generators had a way of
        # accessing the current generator's parameters, it could be
        # simpler?

        # got to get the generator that's actually making the pattern!
        if hasattr(p.generator,'get_current_generator'):
            # access the generator without causing any index to be advanced
            generator = p.generator.get_current_generator()
        elif hasattr(p.generator,'generator'):
            # CB: could at least add appropriate
            # get_current_generator() to patterns other than Selector,
            # like Translator etc
            generator = p.generator.generator
        else:
            generator = p.generator
            
        if hasattr(generator,'red'):
            # promote the red, green, blue from 'actual generator' if it has them
            for c in self.channels:
                setattr(self,c,getattr(generator,c))
        else:
            # otherwise set red, green, blue from gray with r/g/b channel_strength
            c_strength=iter(p.channel_strengths)
            for c in self.channels:
                setattr(self,c,gray*c_strength.next())
        return gray

        
from topo.pattern.image import FileImage,edge_average,PIL
import ImageOps
import numpy

class ColorImage(FileImage):
    """
    A FileImage that handles RGB color images.
    """

    def _get_image(self,p):
        if p.filename!=self.last_filename or self._image is None:
            self.last_filename=p.filename
            rgbimage = PIL.open(p.filename)
            R,G,B = rgbimage.split()
            self._image_red  = R
            self._image_green = G
            self._image_blue = B
            self._image = ImageOps.grayscale(rgbimage)
            return True
        else:
            return False

    def function(self,params):
        """
        In addition to returning grayscale, stores red, green, and
        blue components.
        """

        gray = super(ColorImage,self).function(params)

        # now store red, green, blue
        # (by repeating the super's function call, but each time first
        # resetting the pattern sampler to use the right color
        # channel)
        self.pattern_sampler._set_image(self._image_red)
        self.pattern_sampler._initialize_image()
        self.red = super(ColorImage,self).function(params)

        self.pattern_sampler._set_image(self._image_green)
        self.pattern_sampler._initialize_image()
        self.green = super(ColorImage,self).function(params)

        self.pattern_sampler._set_image(self._image_blue)
        self.pattern_sampler._initialize_image()
        self.blue = super(ColorImage,self).function(params)

        # note: currently, red, green, blue have to be cached
        return gray

    
import random
from contrib.rgbhsv import rgb_to_hsv_array ,hsv_to_rgb_array 
class RotatedHuesImage(ColorImage):
    """
    A ColorImage that rotates the hues in the image by a random value.
    """
    def __init__(self,**params):
        """
        If seed=X is specified, sets the Random() instance's seed.
        Otherwise, calls the instance's jumpahead() method to get a
        state very likely to be different from any just used.
        """
        self.random_generator = random.Random()
        if 'seed' in params:
            self.random_generator.seed(params['seed'])
            del params['seed']
        else:
            self.random_generator.jumpahead(10)
        super(RotatedHuesImage,self).__init__(**params)
        

    def function(self,params):
        gray = super(RotatedHuesImage,self).function(params)

        H,S,V = rgb_to_hsv_array(numpy.array(255*self.red,dtype=numpy.int32),
                                 numpy.array(255*self.green,dtype=numpy.int32),
                                 numpy.array(255*self.blue,dtype=numpy.int32))

        H+=self.random_generator.uniform(0,1.0)
        H%=1.0

        r,g,b = hsv_to_rgb_array(H,S,V)

        self.red=r.astype(numpy.float32)/255.0
        self.green=g.astype(numpy.float32)/255.0
        self.blue=b.astype(numpy.float32)/255.0

        return gray

    
######################################################################
######################################################################
## ONLINE ANALYSIS
# (not special to rgb)

def get_activity(**data):
    """Helper function: return 'Activity' from data."""
    return data['Activity']

def hue_from_rgb(**data):
    """
    Helper function: given arrays of RedActivity, GreenActivity, and
    BlueActivity (values in [0,1]), return an array of the
    corresponding hues.
    """
    red,green,blue = data['RedActivity'],data['GreenActivity'],data['BlueActivity']
    H,S,V = rgb_to_hsv_array(
        numpy.array(255*red,dtype=numpy.int32),
        numpy.array(255*green,dtype=numpy.int32),
        numpy.array(255*blue,dtype=numpy.int32))
    return H


class DataAnalyser(param.Parameterized):
    """
    When called, accepts any list of keywords and returns XXXX numpy array
    according to data_transform_fn.
    """
    data_transform_fn = param.Parameter(default=get_activity,doc=
       """
       Gets the relevant data from those supplied.
       
       Will be called with data supplied to this class when the class
       itself is called; should return the data relevant for the
       analysis.
       """)

    def __call__(self,**data):
        relevant_data = self.data_transform_fn(**data)
        return relevant_data


class Summer(DataAnalyser):
    def __call__(self,**data):
        r = super(Summer,self).__call__(**data)
        return r.sum()


class Histogrammer(DataAnalyser):
    """DataAnalyser that returns a numpy.histogram."""

    num_bins = param.Number(10,constant=True,doc=
       """Number of bins for the histogram: see numpy.histogram.""")

    range_ = param.NumericTuple((0.0,1.0),constant=True,doc=
       """Range of data values: see numpy.histogram.""")

    def __init__(self,**params):
        super(Histogrammer,self).__init__(**params)
        self.bins = None

    def __call__(self,**data):
        d = super(Histogrammer,self).__call__(**data)        
        counts,self.bins = numpy.histogram(d,bins=self.num_bins,range=self.range_)
        return counts


from topo.base.simulation import EventProcessor
class OnlineAnalyser(EventProcessor):
    """
    EventProcessor that supplies data to a data_analysis_fn, then
    stores the result.

    If dest_ports is not None, it should specify a list of all data
    required before the data_analysis_fn is called (with that data).

    The result can be combined with previous ones by specifying an
    appropriate operator. 
    """
    data_analysis_fn = param.Callable(default=Summer(),constant=True,doc=
       """Callable to which the data are passed.""")
    
    operator_ = param.Parameter(default=None,doc=
       """
       Operator used to combine a result with previous results. If none, the current
       result overwrites the previous one.
       """)
    
    def __init__(self,dest_ports=None,**params):
        self.dest_ports = dest_ports
        super(OnlineAnalyser,self).__init__(**params)
        self.analysis_result = None
        self._data = {}
        
    def input_event(self,conn,data):

        self._data[conn.src_port]=data

        r = None

        if self.dest_ports is None or set(self._data.keys()).issuperset(set(self.dest_ports)):
            r = self.data_analysis_fn(**self._data)
            self._data={}

        if r is not None:
            if self.analysis_result is not None and self.operator_ is not None:
                self.analysis_result = self.operator_(r,self.analysis_result)
            else:
                self.analysis_result = r

######################################################################
######################################################################

if __name__=="__main__" or __name__=="__mynamespace__":

    from topo import sheet
    import glob
    image_filenames = glob.glob('/disk/scratch/fast/v1cball/mcgill/foilage/*.tif') # sic
    images0 = [ColorImage(filename=f) for f in image_filenames]
    images1 = [RotatedHuesImage(filename=f) for f in image_filenames]
    
    input_generator0 = pattern.Selector(generators=images0)
    input_generator1 = pattern.Selector(generators=images1)

    topo.sim['Retina0']=ColorImageSheet(input_generator=input_generator0,nominal_density=48)
    topo.sim['Retina1']=ColorImageSheet(input_generator=input_generator1,nominal_density=48)

    cone_types = ['Red','Green','Blue']
    for c in cone_types:
        for i in range(0,2):
            topo.sim[c+str(i)]=sheet.ActivityCopy(nominal_density=48)
            topo.sim.connect('Retina'+str(i),c+str(i),src_port='%sActivity'%c,dest_port='Activity')


    ## examples of online analysis
    topo.sim['A'] = OnlineAnalyser(
        data_analysis_fn=Histogrammer(data_transform_fn=hue_from_rgb),
        operator_=numpy.add,
        dest_ports=['RedActivity','GreenActivity','BlueActivity'])

    for c in cone_types:
        topo.sim.connect('Retina1','A',name='h%s'%c,
                         src_port='%sActivity'%c,
                         dest_port='%sActivity'%c)


    topo.sim['B'] = OnlineAnalyser(
        data_analysis_fn=Histogrammer(),
        operator_=numpy.add)

    topo.sim.connect('Retina1','B',src_port='Activity')


    topo.sim['C'] = OnlineAnalyser(
        data_analysis_fn=Summer(),
        operator_=numpy.add)

    topo.sim.connect('Retina1','C',src_port='Activity')
