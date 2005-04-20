"""
InputParamsPanel

Sliders panel for inputs

The list of valid Input Types is automatically generated from the list
of KernelFactory subclasses found in topo.kernelfactory.  Every
Parameter defined in the KernelFactory subclass will be taken with the
intersection of valid TaggedSlider types defined in this class and
shown in the window.

The Preview panel draws heavily from the PlotPanel class, and just
needs a redefinition of the do_plot_cmd().

$Id$
"""
import __main__
import math
import propertiesframe
import topo.kernelfactory
import topo.plot
from plotpanel import *
from regionplotpanel import *
from topo.inputsheet import InputSheet
import topo.sheetview 

# Hack to reverse the order of the input EventProcessor list and the
# Preview plot list, so that it'll match the order that the plots appear
# in the Acivation panel.
LIST_REVERSE = True
# Default time to show in the Presentation duration box.
DEFAULT_PRESENTATION = '1.0'

def eval_atof(in_string):
    """
    Create a float from a string.  Some defaults are necessary.  Every
    keypress in the field calls this function, so it's quite likely
    that the expression has not been defined yet, and an eval will
    raise an exception.  Catch any exceptions and return 0 if this is
    the case.  Undefined is the Parameter calling this doesn't like the
    value 0.
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
    return topo.kernelfactory.kernel_factories.keys()
    # Slow method, only looks at kernelfactory.py
    #import pyclbr
    #names = [x for x in pyclbr.readmodule('topo.kernelfactory').keys()
    #         if issubclass(topo.kernelfactory.__dict__[x],
    #                       topo.kernelfactory.KernelFactory) \
    #            and x != 'KernelFactory']
    return names


class InputParamsPanel(PlotPanel):
    def __init__(self,parent,pengine,console=None,padding=2,**config):
#        megaparent = parent
#        parent = parent.component('hull')
        super(InputParamsPanel,self).__init__(parent,pengine,console,**config)
        self.plot_group.configure(tag_text='Preview')

        self.INITIAL_PLOT_WIDTH = 25
        self.padding = padding
        self.console = console
        self.learning = IntVar()
        self.learning.set(0)
        self.tparams = {}

        # Variables and widgets for maintaining the list of input sheets
        # that will be given the user defined stimuli.
        self.in_ep_dict = {}
        for each in self.input_eps():
            self.in_ep_dict[each.name] = {'obj':each,
                                          'state':True,
                                          'kernel':None} 
        self.input_box = Pmw.RadioSelect(parent, labelpos = 'w',
                                command = self._input_change,
                                label_text = 'Adjust Input:',
                                frame_borderwidth = 2,
                                frame_relief = 'ridge',
                                selectmode = 'multiple')
        self.input_box.pack(fill = 'x', padx = 5)
        in_ep_names = self.in_ep_dict.keys()
        if LIST_REVERSE: in_ep_names.reverse()  
        for each in in_ep_names:
            self.input_box.add(each)
            self.input_box.invoke(each)

        self.present_length = Pmw.EntryField(self,
                labelpos = 'w',
                label_text = 'Duration to Present:',
                value = DEFAULT_PRESENTATION,
                validate = {'validator' : 'real'},
                )
        self.present_length.pack(fill='x', expand=1, padx=10, pady=5)

        buttonBox = Pmw.ButtonBox(self,orient = 'horizontal',padx=0,pady=0)
        buttonBox.pack(side=TOP)
        buttonBox.add('Present', command = self.present)
        buttonBox.add('Reset to Defaults', command = self.reset_to_defaults)
        Checkbutton(self,text='Network Learning',
                    variable=self.learning,state=DISABLED).pack(side=TOP)
        buttonBox.add('Always use for Training',
                      command = self.use_for_training)

        # Menu of valid KernelFactory types defined.
        self.input_types = kernelfactory_names()
        self.input_type = StringVar()
        self.input_type.set(self.input_types[0])
        Pmw.OptionMenu(self,
                       command = self._refresh_sliders,
                       labelpos = 'w',
                       label_text = 'Input Type:',
                       menubutton_textvariable = self.input_type,
                       items = self.input_types
                       ).pack(side=TOP)
 
        self.prop_frame = propertiesframe.PropertiesFrame(self)

        #                name          min-value    max-value  init-value
        #				    	       
        self.tparams['theta'] = \
          self.add_slider( 'theta',        "0"     ,   "PI*2"   ,  "PI/2"   )
        self.tparams['x'] = \
          self.add_slider( 'x'   ,        "-1"     ,   "1"      ,  "0"      )
        self.tparams['y'] = \
          self.add_slider( 'y'   ,        "0"      ,  "1"       , "0"       )
        self.tparams['min'] = \
          self.add_slider( 'min' ,        "0"      ,  "1"       , "0"       )
        self.tparams['max'] = \
          self.add_slider( 'max'  ,       "0"      ,  "1"       , "1"       )
        self.tparams['width'] = \
          self.add_slider( 'width',       "0"      ,  "1"       , "0.5"     )
        self.tparams['height'] = \
          self.add_slider( 'height',      "0"      ,  "1"       , "0.5"     )
        self.tparams['frequency'] = \
          self.add_slider( 'frequency',   "0.01"  ,   "1.25"   ,  "0.5"     )
        self.tparams['phase'] = \
          self.add_slider( 'phase',        "0"     ,   "PI*2"   ,  "PI/2"   )
        self.tparams['disk_radius'] = \
          self.add_slider( 'disk_radius',  "0"     ,   "1"      ,  "0.8"    )
        self.tparams['gaussian_width'] = \
          self.add_slider( 'gaussian_width',"0"    ,   "1"      ,  "1"      )

# NOT IN EXISTING KERNELFACTORIES 4/2005
#        self.tparams['xsigma'] = \
#          self.add_slider( 'xsigma',       "0"     ,   "RN"     ,  "7.5"     )
#        self.tparams['ysigma'] = \
#          self.add_slider( 'ysigma',       "0"     ,   "RN"     ,  "1.5"     )
#        self.tparams['center_width'] = \
#          self.add_slider( 'center_width', "0"     ,   "RN"     ,  "10"      )
#        self.tparams['scale'] = \
#          self.add_slider( 'scale',        "0"     ,   "3"      ,  "1.0"     )
#        self.tparams['offset'] = \
#          self.add_slider( 'offset',       "-3"    ,   "3"      ,  "0.0"     )
#        self.tparams['photograph'] = \
#          self.prop_frame.add_combobox_property('Photograph',
#                  value='small/ellen_arthur.pgm',
#                  scrolledlist_items=('small/arch.pgm',
#                                      'small/skye.pgm'))
#        self.tparams['size_scale'] = \
#          self.add_slider( 'size_scale' ,  "0"     ,   "5"      ,  "1"    )

        self._refresh_sliders(self.input_type.get())
        self.prop_frame.pack(side=TOP,expand=YES,fill=X)

        self.default_values = self.prop_frame.get_values()
        self.update_inputsheet_kernels()
        self.refresh()


    def _input_change(self,button_name, checked):
        """
        Called by the input box.
        checked records the state, True/False.  The self.in_ep_dict
        records all input event processors, and if they're checked
        or not.
        """
        self.in_ep_dict[button_name]['state'] = checked
        

    def _refresh_sliders(self,new_name):
        """
        Called by the Pmw.OptionMenu object when the user selects a
        KernelFactory type from the menu.  The visible TaggedSliders
        will be updated.  The old ones are removed, and new ones are
        added to the screen.  The widgets themselfs do not change but
        the grid location does.
        """
        # How to wipe the widgets off the screen
        for (s,c) in self.tparams.values():
            s.grid_forget()
            c.grid_forget()
        # Make relevant parameters visible.
        new_sliders = self.relevant_parameters(new_name,self.tparams.keys())
        for i in range(len(new_sliders)):
            (s,c) = self.tparams[new_sliders[i]]
            s.grid(row=i,column=0,padx=self.padding,
                   pady=self.padding,sticky=E)
            c.grid(row=i,
                   column=1,
                   padx=self.padding,
                   pady=self.padding,
                   sticky=N+S+W+E)
        self.update_inputsheet_kernels()
        if self.auto_refresh: self.refresh()


    def relevant_parameters(self,kf_classname,param_list):
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


    def input_eps(self):
        """
        Return a list of event processors in the active simulator that
        can have Factories added to them.

        For now, anything that is an InputSheet will be added.
        """
        sim = self.console.active_simulator()
        eps = sim.get_event_processors()
        i_eps = [i for i in eps if isinstance(i,InputSheet)]
        return i_eps
        


    def add_slider(self,name,min,max,init):
        return self.prop_frame.add_tagged_slider_property(name,init,
                 min_value=min,max_value=max,width=30,string_format='%.3f',
                 string_translator=eval_atof)


    def present(self):
        """
        CURRENT IMPLEMENTATION GENERATES SIDE EFFECTS TO THE MODEL,
        AND THERE IS NO WAY TO DISABLE LEARNING.
        """
        new_kernels_dict = self.update_inputsheet_kernels()
        original_kernels = self.store_inputsheet_kernels()
        self.register_inputsheet_kernels(new_kernels_dict)
        
        sim = self.console.active_simulator()
        sim.run(eval_atof(self.present_length.getvalue()))
        
        self.register_inputsheet_kernels(original_kernels)
        self.console.auto_refresh()


    def update_inputsheet_kernels(self):
        """
        Make an instantiation of the current user kernel, and put it into
        all of the selected input sheets.
        """
        kname = self.input_type.get()
        p = self.get_params()
        rp = self.relevant_parameters(kname,self.tparams.keys())
        ndict = {}
        for each in rp:
            ndict[each] = eval_atof(p[each])
        for each in self.in_ep_dict.keys():
            if self.in_ep_dict[each]['state']:
                kf = topo.kernelfactory.__dict__[kname](**ndict)
                self.in_ep_dict[each]['kernel'] = kf
        return self.in_ep_dict  # Doesn't have to return it, but is explicit.


    def store_inputsheet_kernels(self):
        """
        Store the kernels currently in the InputSheets.
        """
        kernel_dict = {}
        for each in self.in_ep_dict.keys():
            kernel_dict[each] = {}
            kernel_dict[each]['obj'] = self.in_ep_dict[each]['obj']
            kernel_dict[each]['state'] = True
            kernel_dict[each]['kernel'] = kernel_dict[each]['obj'].get_input_generator()
        return kernel_dict
    

    def register_inputsheet_kernels(self,kernels_dict):
        """
        Each dictionary entry must have an 'obj' with an InputSheet as
        value, with 'state' set to True or False to see if the kernel
        should be replaced, and a 'kernel' key with the kernel object
        as value that should be moved into the InputSheet.
        """
        for each in self.in_ep_dict.keys():
            if kernels_dict[each]['state']:
                ep = kernels_dict[each]['obj']
                ep.set_input_generator(kernels_dict[each]['kernel'])


    def use_for_training(self):
        """
        Lock in the existing KernelFactory as the new default stimulus
        input to the input layer.  This should work like a test stimuli,
        but the original input generator is not put back afterwards.
        """
        pass # Added so do_command doesn't freak with no body.
#        Lissom.cmd(self.get_training_pattern_cmd())


    def reset_to_defaults(self):
        self.prop_frame.set_values(self.default_values)
        self.input_type.set(self.input_types[0])
        self.present_length.setvalue(DEFAULT_PRESENTATION)
        for each in self.in_ep_dict.keys():
            if not self.in_ep_dict[each]['state']:
                self.input_box.invoke(each)
        self.update_inputsheet_kernels()
        self._refresh_sliders(self.input_type.get())
        if self.auto_refresh: self.refresh()
        self.learning.set(0)


    def get_cmd(self):
        format = """input_present_object learning=%s All Input_%s %s
                    theta=%s cx=%s cy=%s xsigma=%s ysigma=%s scale=%s
                    offset=%s freq=%s phase=%s center_width=%s size_scale=%s"""
        params = self.get_params()
        return format % (params['learning'],
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
        """Get the property values as a dictionary."""
        params = self.prop_frame.get_values()

# With no Photograph option, this block is not useful.  Something similar
# may have to go back in once Photograph kernels are created.
#        if self.input_type.get() == 'Photograph':
#            # The type is PGM and the file name is the Photograph
#            params['type'] = 'PGM'
#            params['filename'] = "'" + params['Photograph'] + "'"
#        else:
#            # Otherwise get the type from the input_type selector
#            # and set the filename to null
#            params['type'] = self.input_type.get()
#            params['filename'] = ''

        if self.learning.get():
            params['learning'] = 'true'
        else:
            params['learning'] = 'false'
        
        return params


    def do_plot_cmd(self):
        """
        Replace the superclass do_plot_cmd.
        Create a PlotGroup that has a list of Plots that have been
        created from a set of activations defined by the user.

        Post: self.pe_group contains a PlotGroup, and self.plots is
        a list from the PlotGroup.plots()
        """
        plist = []
        for each in self.in_ep_dict.keys():
            k = self.in_ep_dict[each]['kernel']
            sv = topo.sheetview.SheetView((k(),k.bounds),src_name=each,
                                          view_type='Kernel')
            p = topo.plot.Plot((sv,None,None),topo.plot.COLORMAP)
            plist.append(p)
        if LIST_REVERSE: plist.reverse()
        self.pe_group = topo.plot.PlotGroup(plist)
        self.plots = self.pe_group.plots()


    def refresh_title(self): pass

    def refresh(self):
        """
        Use the parent class refresh
        """
        self.update_inputsheet_kernels()
        super(InputParamsPanel,self).refresh()

#    def destroy(self):
#        print "inputparamspanel destroy"
