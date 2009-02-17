# Adding support for RGB images (work in progress)
import topo

############################################################
from topo.sheet.basic import GeneratorSheet,FunctionEvent,PeriodicEventSequence,param,PatternGenerator
from topo import pattern

class ColorImageSheet(GeneratorSheet):
    src_ports=['Activity','RedActivity','GreenActivity','BlueActivity']
    input_generator = param.ClassSelector(PatternGenerator,default=pattern.Selector()) # ** RGBify **
    
    def __init__(self,**params):
        super(ColorImageSheet,self).__init__(**params)

        # should instead be array of zeros of same size,
        # although this has same effect because activity is
        # array of zeros to begin with
        self._redact=self.activity.copy()
        self._greenact=self.activity.copy()
        self._blueact=self.activity.copy()

#    def set_input_generator(self,new_ig,push_existing=False):
#    def push_input_generator(self):
#    def pop_input_generator(self):

    def generate(self):
        self.verbose("Generating a new pattern")

        self.activity[:] = self.input_generator()

        #g = self.input_generator.get_current_generator()

        # ABOVE looks like the super call to me
        g = self.input_generator
        
        self._redact[:] = g._red
        self._greenact[:] = g._green
        self._blueact[:] = g._blue
        
        if self.apply_output_fns:
            for output_fn in self.output_fns:
                output_fn(self.activity)
                output_fn(self._redact)
                output_fn(self._greenact)
                output_fn(self._blueact)

        self.send_output(src_port='Activity',data=self.activity)
        self.send_output(src_port='RedActivity',data=self._redact)
        self.send_output(src_port='GreenActivity',data=self._greenact)
        self.send_output(src_port='BlueActivity',data=self._blueact)
############################################################    



import copy
from topo.param.parameterized import ParamOverrides
class RGBify(PatternGenerator):
    # allows any pg to work with rgb

    channels = ["_red","_green","_blue"]

    generator = param.Parameter(default=pattern.Constant())

    channel_strengths = param.List([1.0/3,1.0/3,1.0/3]) # not sure what to call it
    
    def __init__(self,**params):
        super(RGBify,self).__init__(**params)
        # copy to ensure random number streams not affected by rgbification
        #self._set_up_generators()


    def __call__(self,**params):
        p = ParamOverrides(self,params)

        #result = p.generator(**params) # oops passing extra params specific to this PG!

        params['xdensity']=p.xdensity
        params['ydensity']=p.ydensity
        params['bounds']=p.bounds
        
        result = p.generator(**params)
        # method more complicated than it needs to be; maybe if the
        # various selector pattern generators had a way of accessing
        # the current generator's parameters, it could be simpler
        
        if hasattr(p.generator,'get_current_generator'):
            generator = p.generator.get_current_generator()
        elif hasattr(p.generator,'generator'):
            # could at least add appropriate get_current_generator()
            # to patterns other than Selector, like Translator etc
            generator = p.generator.generator
        else:
            generator = p.generator

        
        if hasattr(generator,'_red'):
            for c in self.channels:
                setattr(self,c,getattr(generator,c))
        else:
            results = []
            c_strength=iter(p.channel_strengths)
            for c in self.channels:
                setattr(self,c,result*c_strength.next())

        return result

        



############################################################
from topo.pattern.image import FileImage,edge_average,PIL
import numpy

class ColorImage(FileImage):

    def _get_image(self,params):
        filename = params['filename']

        if filename!=self.last_filename or self._image is None:
            self.last_filename=filename
            self._image = PIL.open(self.filename)
            return True
        else:
            return False


    def function(self,params):
        xdensity = params['xdensity']
        ydensity = params['ydensity']
        x        = params['pattern_x']
        y        = params['pattern_y']
        size_normalization = params.get('scaling') or self.size_normalization  #params.get('scaling',self.size_normalization)

        height = params['size']
        width = params['aspect_ratio']*height

        whole_image_output_fns = params['whole_image_output_fns']

        if self._get_image(params) or whole_image_output_fns != self.last_wiofs:
            self.last_wiofs = whole_image_output_fns

            R,G,B = self._image.split()
            red_pattern_array = numpy.array(R,dtype=numpy.float32) 
            green_pattern_array = numpy.array(G,dtype=numpy.float32)
            blue_pattern_array = numpy.array(B,dtype=numpy.float32)

            # 3 pattern samplers for now because of whole image output
            # fn and background value fn; need to sort those out
            self.ps=self.pattern_sampler_type(pattern_array=red_pattern_array, 
                                              whole_pattern_output_fns=self.last_wiofs,
                                              background_value_fn=edge_average)
            
            self._gps = self.pattern_sampler_type(pattern_array=green_pattern_array, 
                                              whole_pattern_output_fns=self.last_wiofs,
                                              background_value_fn=edge_average)

            self._bps = self.pattern_sampler_type(pattern_array=blue_pattern_array, 
                                              whole_pattern_output_fns=self.last_wiofs,
                                              background_value_fn=edge_average)
            

        self._red = self.ps(x.copy(),y.copy(),float(xdensity),float(ydensity),
                            size_normalization,float(width),float(height))

        self._green = self._gps(x.copy(),y.copy(),float(xdensity),float(ydensity),
                                size_normalization,float(width),float(height)) 

        self._blue = self._bps(x,y,float(xdensity),float(ydensity),
                               size_normalization,float(width),float(height))

        #print self._red

        if not self.cache_image:
            del self.ps     ; self.ps=None
            del self._image ; self._image=None
            # uh-oh: got to cache _red, _green, _blue for the moment
            # can still get rid of _gps and _bps
            
        return self._red # should instead be grayscale


import random
from contrib.rgbhsv import rgb_to_hsv_array ,hsv_to_rgb_array 
class TColorImage(ColorImage):

    def function(self,params):
        res = super(TColorImage,self).function(params)

        H,S,V = rgb_to_hsv_array(numpy.array(255*self._red,dtype=numpy.int32),
                                 numpy.array(255*self._green,dtype=numpy.int32),
                                 numpy.array(255*self._blue,dtype=numpy.int32))

        rot = random.uniform(0,1.0)
        #r2 = random.uniform(0,1.0)

        #if r2>=0.5:
        #    H+=rot
        H+=rot
        H%=1.0

        r,g,b = hsv_to_rgb_array(H,S,V)

        self._red=r.astype(numpy.float32)/255.0 # 'activities' are always expected to be between 0&1
        self._green=g.astype(numpy.float32)/255.0
        self._blue=b.astype(numpy.float32)/255.0

        return res

    
######################################################################
######################################################################
## ONLINE ANALYSIS

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
    images1 = [TColorImage(filename=f) for f in image_filenames]
    
    input_generator0 = pattern.Selector(generators=images0)
    input_generator1 = pattern.Selector(generators=images1)

    topo.sim['Retina0']=ColorImageSheet(input_generator=RGBify(generator=input_generator0),nominal_density=48)
    topo.sim['Retina1']=ColorImageSheet(input_generator=RGBify(generator=input_generator1),nominal_density=48)

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
