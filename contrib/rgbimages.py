# Adding support for RGB images (work in progress)

############################################################
from topo.sheet.basic import GeneratorSheet,FunctionEvent,PeriodicEventSequence,param,PatternGenerator
from topo import pattern

class ColorImageSheet(GeneratorSheet):
    src_ports=['Activity','RedActivity','GreenActivity','BlueActivity']
    input_generator = param.ClassSelector(PatternGenerator,default=pattern.Selector())
    
    def __init__(self,**params):
        super(ColorImageSheet,self).__init__(**params)

        self._redact=self.activity.copy()
        self._greenact=self.activity.copy()
        self._blueact=self.activity.copy()

#    def set_input_generator(self,new_ig,push_existing=False):
#    def push_input_generator(self):
#    def pop_input_generator(self):

    def generate(self):
        self.verbose("Generating a new pattern")

        self.activity[:] = self.input_generator()

        g = self.input_generator.get_current_generator()
        
        self._redact[:] = g._red
        self._greenact[:] = g._green
        self._blueact[:] = g._blue
        
        if self.apply_output_fn:
            self.output_fn(self.activity)
            self.output_fn(self._redact)
            self.output_fn(self._greenact)
            self.output_fn(self._blueact)

        self.send_output(src_port='Activity',data=self.activity)
        self.send_output(src_port='RedActivity',data=self._redact)
        self.send_output(src_port='GreenActivity',data=self._greenact)
        self.send_output(src_port='BlueActivity',data=self._blueact)
############################################################    


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

        whole_image_output_fn = params['whole_image_output_fn']

        if self._get_image(params) or whole_image_output_fn != self.last_wiof:
            self.last_wiof = whole_image_output_fn

            R,G,B = self._image.split()
            # with PIL 1.1.6 will be just red_pattern.array = numpy.array(R)
            red_pattern_array = numpy.array(R.getdata(),numpy.float32)
            red_pattern_array.shape = (self._image.size[::-1]) 

            green_pattern_array = numpy.array(G.getdata(),numpy.float32)
            green_pattern_array.shape = (self._image.size[::-1])
            
            blue_pattern_array = numpy.array(B.getdata(),numpy.float32)
            blue_pattern_array.shape = (self._image.size[::-1]) 
            ####

            # 3 pattern samplers for now because of whole image output
            # fn and background value fn; need to sort those out
            self.ps=self.pattern_sampler_type(pattern_array=red_pattern_array, 
                                              whole_pattern_output_fn=self.last_wiof,
                                              background_value_fn=edge_average)
            
            self._gps = self.pattern_sampler_type(pattern_array=green_pattern_array, 
                                              whole_pattern_output_fn=self.last_wiof,
                                              background_value_fn=edge_average)

            self._bps = self.pattern_sampler_type(pattern_array=blue_pattern_array, 
                                              whole_pattern_output_fn=self.last_wiof,
                                              background_value_fn=edge_average)
            

        self._red = self.ps(x.copy(),y.copy(),float(xdensity),float(ydensity),
                            size_normalization,float(width),float(height))

        self._green = self._gps(x.copy(),y.copy(),float(xdensity),float(ydensity),
                                size_normalization,float(width),float(height)) 

        self._blue = self._bps(x,y,float(xdensity),float(ydensity),
                               size_normalization,float(width),float(height))
        

        if not self.cache_image:
            del self.ps     ; self.ps=None
            del self._image ; self._image=None
            # uh-oh: got to cache _red, _green, _blue for the moment
            # can still get rid of _gps and _bps
            
        return self._red # should instead be grayscale
############################################################


############################################################
import glob
image_filenames = glob.glob('/disk/scratch/mcgill/foilage/*.tif') # sic
images = [ColorImage(filename=f) for f in image_filenames]

from topo import sheet

cone_types = ['Red','Green','Blue']

topo.sim['P']=ColorImageSheet()
topo.sim['P'].input_generator.generators=images

for c in cone_types:
    topo.sim[c]=sheet.ActivityCopy()
    topo.sim.connect('P',c,src_port='%sActivity'%c,dest_port='Activity')
############################################################
