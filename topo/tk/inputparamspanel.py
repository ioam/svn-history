"""
InputParamsPanel

Sliders panel for inputs

$Id$
"""
import __main__
import math
import propertiesframe
from plotpanel import *
from regionplotpanel import *


def eval_atof(in_string):
    """
    Create a float from a string.  Some defaults are necessary.
    """
    x_dict = {'PI':math.pi, 'RN':2.5}
    val = eval(in_string,x_dict)
    return val


class InputParamsPanel(Frame):
    def __init__(self,parent,console=None,**config):

        self.console = console
        self.input_type = StringVar()
        self.input_type.set('Gaussian')
        self.learning = IntVar()
        self.learning.set(0)

        Frame.__init__(self,parent,config)

        input_types = [ 'Gaussian',
                        'SineGrating',
                        'Gabor',
                        'UniformRandomNoise',
                        'Rectangle',
                        'FuzzyLine',
                        'FuzzyDisc',
                        'Photograph']

        buttonBox = Pmw.ButtonBox(self,
                                  orient = 'horizontal',
                                  padx=0,pady=0,
                                  #frame_borderwidth = 2,
                                  #frame_relief = 'groove'
                                  )
        buttonBox.pack(side=TOP)

        Pmw.OptionMenu(self,
                       labelpos = 'w',
                       label_text = 'Input Type:',
                       menubutton_textvariable = self.input_type,
                       items = input_types
                       ).pack(side=TOP)
 

        buttonBox.add('Present', command = self.present)
        buttonBox.add('Reset to Defaults', command = self.reset_to_defaults)
        buttonBox.add('Use for Training', command = self.use_for_training)
        Checkbutton(self,text='learning',variable=self.learning).pack(side=TOP)
       

        self.prop_frame = propertiesframe.PropertiesFrame(self)


        #                name          min-value    max-value  init-value
        #				    	       
        self.add_slider( 'theta',        "0"     ,   "PI*2"   ,  "PI/2"    )
        self.add_slider( 'cx'   ,        "-RN/4" ,   "5*RN/4" ,  "RN/2"    )
        self.add_slider( 'cy'   ,        "-RN/4"  ,  "5*RN/4"  , "RN/2"    )
        self.add_slider( 'xsigma',       "0"     ,   "RN"     ,  "7.5"     )
        self.add_slider( 'ysigma',       "0"     ,   "RN"     ,  "1.5"     )
        self.add_slider( 'center_width', "0"     ,   "RN"     ,  "10"      )
        self.add_slider( 'scale',        "0"     ,   "3"      ,  "1.0"     )
        self.add_slider( 'offset',       "-3"    ,   "3"      ,  "0.0"     )
        self.add_slider( 'freq',         "0.01"  ,   "1.25"   ,  "0.5"     )
        self.add_slider( 'phase',        "0"     ,   "PI*2"   ,  "PI/2"    )

        self.prop_frame.add_combobox_property('Photograph',
                                              value='small/ellen_arthur.pgm',
                                              scrolledlist_items=('small/arch.pgm',
                                                                  'small/ellen_arthur.pgm',
                                                                  'small/gene.pgm',
                                                                  'small/lochnessroad.pgm',
                                                                  'small/loghog.pgm',
                                                                  'small/skye.pgm'))

        self.add_slider( 'size_scale' ,  "0"     ,   "5"      ,  "1"    )

       
        self.prop_frame.pack(side=TOP,expand=YES,fill=X)

        self.default_values = self.prop_frame.get_values()

    def add_slider(self,name,min,max,init):
        self.prop_frame.add_tagged_slider_property(name,init,
                                                   min_value=min,max_value=max,
                                                   width=30,
                                                   string_format='%.3f')
#                                                   string_translator=Lissom.eval_expr)
#                                                   string_translator=Lissom.eval_expr)




    def present(self):
#        Lissom.cmd(self.get_cmd())
        self.console.auto_refresh()
        
    def use_for_training(self):
        pass
#        dummy()  # Added so do_command doesn't freak with no body.
#        Lissom.cmd(self.get_training_pattern_cmd())

    def reset_to_defaults(self):
        self.prop_frame.set_values(self.default_values)
        self.input_type.set('Gaussian')
        self.learning.set(0)

    def get_cmd(self):
        format = """input_present_object learning=%s All Input_%s %s
                    theta=%s cx=%s cy=%s xsigma=%s ysigma=%s scale=%s
                    offset=%s freq=%s phase=%s center_width=%s size_scale=%s"""
        params = self.get_params()
        return format % (params['learning'],
                         params['type'],
                         params['filename'],
                         params['theta'],
                         params['cx'],
                         params['cy'],
                         params['xsigma'],
                         params['ysigma'],
                         params['scale'],
                         params['offset'],
                         params['freq'],
                         params['phase'],
                         params['center_width'],
                         params['size_scale'])


    def get_training_pattern_cmd(self):

        format = """exec input_undefine 'input_define Obj0 All
                    Input_%s %s xsigma=%s ysigma=%s scale=%s offset=%s
                    freq=%s phase=%s center_width=%s size_scale=%s'"""
        params = self.get_params()
        return format % (params['type'],
                         params['filename'],
                         params['xsigma'],
                         params['ysigma'],
                         params['scale'],
                         params['offset'],
                         params['freq'],
                         params['phase'],
                         params['center_width'],
                         params['size_scale'])
        

    def get_params(self):

        # Get the property values as a dictionary
        params = self.prop_frame.get_values()

        if self.input_type.get() == 'Photograph':
            # if it's a photo, the type is PGM and the file name is the Photograph
            params['type'] = 'PGM'
            params['filename'] = "'" + params['Photograph'] + "'"
        else:
            # Otherwise get the type from the input_type selector
            # and set the filename to null
            params['type'] = self.input_type.get()
            params['filename'] = ''

        if self.learning.get():
            params['learning'] = 'true'
        else:
            params['learning'] = 'false'
        
        return params
