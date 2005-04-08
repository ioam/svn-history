"""
InputParamsPanel

Sliders panel for inputs

The list of valid Input Types is automatically generated from the list
of KernelFactory subclasses found in topo.kernelfactory.  By adding a
new subclass, it will be added to the list of input types.  Every
Parameter defined in the KernelFactory subclass will be taken with the
intersection of valid TaggedSlider types defined in this class and
shown in the window.

$Id$
"""
import __main__
import math, pyclbr
import propertiesframe
import topo.kernelfactory
from plotpanel import *
from regionplotpanel import *


def eval_atof(in_string):
    """
    Create a float from a string.  Some defaults are necessary.  Every
    keypress in the field calls this function, so it's quite likely
    that the expression has not been defined yet, and an eval will
    raise an exception.  Catch any exceptions and return 0 if this is
    the case.
    """
    x_dict = {'PI':math.pi, 'pi':math.pi, 'Pi':math.pi, 'pI':math.pi,
              'RN':1.0}
    try:
        val = eval(in_string,x_dict)
    except Exception:
        val = 0
    return val


def kernelfactory_names():
    """
    Return the existing list of KernelFactory subclasses.  This list will
    change based on the existing classes found within kernelfactory.py
    """
    names = [x for x in pyclbr.readmodule('topo.kernelfactory').keys()
             if issubclass(topo.kernelfactory.__dict__[x],
                           topo.kernelfactory.KernelFactory) \
                and x != 'KernelFactory']
    return names


def relevant_parameters(kf_classname,param_list):
    """
    Pre:  kf_classname is the string name of a KernelFactory subclass.
          param_list is a list of strings of parameter tagged sliders
          that are viewable from the window.
    Post: List of strings that is the Intersection of kf_classname's
          class member keys, and param_list entries.
    """
    kf_class_keylist = topo.kernelfactory.__dict__[kf_classname].__dict__.keys()
    rlist = [s for s in param_list if s in kf_class_keylist]
    return rlist


class InputParamsPanel(Frame):
    def __init__(self,parent,console=None,padding=2,**config):

        self.padding = padding
        self.console = console
        self.learning = IntVar()
        self.learning.set(0)
        self.tparams = {}

        Frame.__init__(self,parent,config)

        self.input_types = kernelfactory_names()
        self.input_type = StringVar()
        self.input_type.set(self.input_types[0])

        buttonBox = Pmw.ButtonBox(self,
                                  orient = 'horizontal',
                                  padx=0,pady=0,
                                  #frame_borderwidth = 2,
                                  #frame_relief = 'groove'
                                  )
        buttonBox.pack(side=TOP)

        buttonBox.add('Present', command = self.present)
        buttonBox.add('Reset to Defaults', command = self.reset_to_defaults)
        # It's all training for now, so there's no need for a check box.
        #Checkbutton(self,text='learning',
        #            variable=self.learning).pack(side=TOP)
        #buttonBox.add('Use for Training', command = self.use_for_training)

        Pmw.OptionMenu(self,
                       command = self.refresh_sliders,
                       labelpos = 'w',
                       label_text = 'Input Type:',
                       menubutton_textvariable = self.input_type,
                       items = self.input_types
                       ).pack(side=TOP)
 
        self.prop_frame = propertiesframe.PropertiesFrame(self)

        #                name          min-value    max-value  init-value
        #				    	       
        self.tparams['theta'] = \
          self.add_slider( 'theta',        "0"     ,   "PI*2"   ,  "PI/2"    )
        self.tparams['x'] = \
          self.add_slider( 'x'   ,        "-RN/4" ,   "5*RN/4" ,  "RN/2"    )
        self.tparams['y'] = \
          self.add_slider( 'y'   ,        "-RN/4"  ,  "5*RN/4"  , "RN/2"    )
        self.tparams['xsigma'] = \
          self.add_slider( 'xsigma',       "0"     ,   "RN"     ,  "7.5"     )
        self.tparams['ysigma'] = \
          self.add_slider( 'ysigma',       "0"     ,   "RN"     ,  "1.5"     )
        self.tparams['center_width'] = \
          self.add_slider( 'center_width', "0"     ,   "RN"     ,  "10"      )
        self.tparams['scale'] = \
          self.add_slider( 'scale',        "0"     ,   "3"      ,  "1.0"     )
        self.tparams['offset'] = \
          self.add_slider( 'offset',       "-3"    ,   "3"      ,  "0.0"     )
        self.tparams['freq'] = \
          self.add_slider( 'freq',         "0.01"  ,   "1.25"   ,  "0.5"     )
        self.tparams['phase'] = \
          self.add_slider( 'phase',        "0"     ,   "PI*2"   ,  "PI/2"    )

        self.tparams['photograph'] = \
          self.prop_frame.add_combobox_property('Photograph',
                  value='small/ellen_arthur.pgm',
                  scrolledlist_items=('small/arch.pgm',
                                      'small/skye.pgm'))
        self.tparams['size_scale'] = \
          self.add_slider( 'size_scale' ,  "0"     ,   "5"      ,  "1"    )

        self.refresh_sliders(self.input_type.get())
        self.prop_frame.pack(side=TOP,expand=YES,fill=X)

        self.default_values = self.prop_frame.get_values()


    def refresh_sliders(self,new_name):
        # How to wipe the widgets off the screen
        for (s,c) in self.tparams.values():
            s.grid_forget()
            c.grid_forget()
            new_sliders = relevant_parameters(new_name,self.tparams.keys())
            for i in range(len(new_sliders)):
                (s,c) = self.tparams[new_sliders[i]]
                s.grid(row=i,column=0,padx=self.padding,
                       pady=self.padding,sticky=E)
                c.grid(row=i,
                       column=1,
                       padx=self.padding,
                       pady=self.padding,
                       sticky=N+S+W+E)
            


    def add_slider(self,name,min,max,init):
        return self.prop_frame.add_tagged_slider_property(name,init,
                 min_value=min,max_value=max,width=30,string_format='%.3f',
                 # Needs work.
                 string_translator=eval_atof)
                 # string_translator=Lissom.eval_expr)


    def present(self):
        p = self.get_params()
        rp = relevant_parameters(self.input_type.get(),self.tparams.keys())
        ndict = {}
        for each in rp:
            ndict[each] = eval_atof(p[each])
        kf = topo.kernelfactory.__dict__[self.input_type.get()](**ndict)
        # Do cool stuff to the simulation.
        self.console.auto_refresh()
        

    def use_for_training(self):
        pass # Added so do_command doesn't freak with no body.
#        Lissom.cmd(self.get_training_pattern_cmd())

    def reset_to_defaults(self):
        self.prop_frame.set_values(self.default_values)
        self.input_type.set(self.input_types[0])
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
