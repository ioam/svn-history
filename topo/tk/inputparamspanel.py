"""
InputParamsPanel

Sliders panel for inputs

The list of valid Input Types is automatically generated from the list
of KernelFactory subclasses found in topo.kernelfactory.  Every
Parameter defined in the KernelFactory subclass will be taken with the
intersection of valid TaggedSlider types defined in this class and
then shown in the window.

The Preview panel draws heavily from the PlotPanel class, and instead
of using a PlotGroup subclass, creates a group on the fly.  

$Id$
"""
import __main__
import math
import propertiesframe
import topo.kernelfactory
import topo.plot
import plotpanel
import Pmw
from Tkinter import IntVar, StringVar, Checkbutton
from Tkinter import TOP, LEFT, RIGHT, BOTTOM, YES, N, S, E, W, X
from copy import deepcopy
from topo.inputsheet import InputSheet
from topo.sheet import BoundingBox, Sheet
import topo.sheetview 

# Hack to reverse the order of the input EventProcessor list and the
# Preview plot list, so that it'll match the order that the plots appear
# in the Activation panel.
LIST_REVERSE = True

# Default time to show in the Presentation duration box.
DEFAULT_PRESENTATION = '1.0'

def eval_atof(in_string):
    """
    Create a float from a string.  Some defaults are necessary.  Every
    keypress in the field calls this function, so it's quite likely
    that the expression has not been defined yet, and an eval will
    raise an exception.  Catch any exceptions and return 0 if this is
    the case.  Undefined if the Parameter calling this doesn't like the
    value 0.
    """
    ### JABHACKALERT!
    ### 
    ### This dictionary needs to be replaced with a real evaluation
    ### in an appropriate namespace, presumably the global namespace.
    ### pi and PI should be defined there; RN isn't necessary at all.
    ### 
    ### If possible, it should not be undefined if the Parameter
    ### calling it does not like zero.  Instead, it should probably
    ### accept a default value when called, to be returned on
    ### exceptions.
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
    change based on the existing classes found within kernelfactory.py,
    and can be extended by the user.
    """
    return topo.kernelfactory.kernel_factories.keys()


class InputParamsPanel(plotpanel.PlotPanel):

    ### This function is too long, and should be broken up if at all possible.
    def __init__(self,parent,pengine,console=None,padding=2,**config):
        super(InputParamsPanel,self).__init__(parent,pengine,console,**config)
        self.plot_group.configure(tag_text='Preview')

        self.INITIAL_PLOT_WIDTH = 100
        self.padding = padding
        self.parent = parent
        self.console = console
        self.learning = IntVar()
        
        ### JABHACKALERT!
        ###
        ### This being a Test Pattern window, not a Training Pattern
        ### window, learning should most definitely be turned off by
        ### default.  However, when I try to do that, I get an error
        ### saying that there was a pop from an empty list.  This
        ### appears to be due to _learning_toggle saving the state
        ### when it is toggled, which seems clearly incorrect.
        ### Instead, the event queue should presumably be saved before
        ### the first test pattern is presented, and restored whenever
        ### the next training pattern is presented.  Otherwise, I
        ### can't see how one could ensure that the system is in the
        ### correct state.
        
        self.learning.set(1)
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
                                label_text = 'Input Sheets:',
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
        self.learning_button = Checkbutton(self,text='Network Learning',
                                      variable=self.learning,
                                      command=self._learning_toggle)
        self.learning_button.pack(side=TOP)
        buttonBox.add('Use for future learning',
                      command = self.use_for_learning)

        ### JABHACKALERT!
        ###
        ### Must remove the string "Factory" from all items in the
        ### list of input types.  Factory does not mean anything to
        ### the user.
        ###
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

        ### JABHACKALERT!
        ###
        ### There can't be any list of valid parameters defined in
        ### this class; the user needs to be able to add any arbitrary
        ### parameter to a new KernelFactory of his or her own design.
        ### So all the information below needs to be stored with the
        ### KernelFactory or some lower-level entity, preferably as
        ### part of the Parameter definition.  Some of the values here
        ### are just hints, while others are absolute maximum or
        ### minimums, and the Parameter definition would need to
        ### distinguish between those two cases.
        
        #                name          min-value    max-value  init-value
        #
        self.tparams['theta'] = \
          self.add_slider( 'theta',         "0"       , "PI*2",  "0"      )
        self.tparams['x'] = \
          self.add_slider( 'x',             "-1"      , "1"   ,  "0"      )
        self.tparams['y'] = \
          self.add_slider( 'y',             "-1"      , "1"   , "0"       )
        self.tparams['min'] = \
          self.add_slider( 'min',           "0"       , "1"   , "0"       )
        self.tparams['max'] = \
          self.add_slider( 'max',           "0"       , "1"   , "1"       )
        self.tparams['width'] = \
          self.add_slider( 'width',         "0.000001", "1"   , "0.2"     )
        self.tparams['height'] = \
          self.add_slider( 'height',        "0.000001", "1"   , "0.2"     )
        self.tparams['frequency'] = \
          self.add_slider( 'frequency',     "0.01"    , "7"   ,  "5"      )
        self.tparams['phase'] = \
          self.add_slider( 'phase',         "0"       , "PI*2",  "PI/2"   )
        self.tparams['disk_radius'] = \
          self.add_slider( 'disk_radius',   "0"       , "1"   ,  "0.2"    )
        self.tparams['gaussian_width'] = \
          self.add_slider( 'gaussian_width',"0.000001", "1"   ,  "0.15"   )

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

        # Hook to turn learning back on when Panel is closed.
        self.parent.protocol('WM_DELETE_WINDOW',self._reset_and_destroy)

        self.default_values = self.prop_frame.get_values()
        self._update_inputsheet_kernels()
        self.refresh()


    def _input_change(self,button_name, checked):
        """
        Called by the input box.
        The variable checked records the state, either True or False.
        The variable self.in_ep_dict records all input event
        processors, and whether they are checked or not.
        """
        self.in_ep_dict[button_name]['state'] = checked
        

    def _learning_toggle(self):
        """
        Invoked by the learning checkbox.  Requires that the initial
        state is learning.  i.e. Trying to pop state off an empty
        simulator event queue stack will causes problems.
        """
        learning = self.learning.get()
        sim = self.console.active_simulator()
        if not learning:
            sim.state_push()
            for each in sim.get_event_processors():
                if isinstance(each,Sheet):
                    each.disable_learning()
                    each.activation_push()
        else: # Turn learning back on and restore
            sim.state_pop()
            for each in sim.get_event_processors():
                if isinstance(each,Sheet):
                    each.enable_learning()
                    each.activation_pop()
            

    def _refresh_sliders(self,new_name):
        """
        Called by the Pmw.OptionMenu object when the user selects a
        KernelFactory type from the menu.  The visible TaggedSliders
        will be updated.  The old ones are removed, and new ones are
        added to the screen.  The widgets themselves do not change but
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
        self._update_inputsheet_kernels()
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
                 min_value=min,max_value=max,width=30,string_format='%.6f',
                 string_translator=eval_atof)


    def present(self):
        """
        Move the user created kernels into the InputSheets, run for
        the specified length of time, then restore the original
        kernels.  The system may become unstable if the user breaks
        this thread so that the original kernels are not properly
        restored, but then there are going to be other problems with
        the Simulator state if a run is interrupted.

        This function is run no matter if learning is enabled or
        disabled since run() will detect sheet attributes.
        """
        new_kernels_dict = self._update_inputsheet_kernels()
        original_kernels = self._store_inputsheet_kernels()
        self.register_inputsheet_kernels(new_kernels_dict)
        
        sim = self.console.active_simulator()
        sim.run(eval_atof(self.present_length.getvalue()))
        
        self.register_inputsheet_kernels(original_kernels)
        self.console.auto_refresh()


    ### JAB: It is not clear how this will need to be extended to support
    ### objects with different parameters in the different eyes, e.g. to
    ### test ocular dominance.
    def _update_inputsheet_kernels(self):
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
                ndict['density'] = self.in_ep_dict[each]['obj'].density
                ndict['bounds'] = deepcopy(self.in_ep_dict[each]['obj'].bounds)
                kf = topo.kernelfactory.__dict__[kname](**ndict)
                self.in_ep_dict[each]['kernel'] = kf
        return self.in_ep_dict  # Doesn't have to return it, but is explicit.


    def _store_inputsheet_kernels(self):
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
            # Use this to only present to the ones that are currently selected:
            # if kernels_dict[each]['state']:
            ep = kernels_dict[each]['obj']
            ep.set_input_generator(kernels_dict[each]['kernel'])


    ### JAB: It is not clear how this will need to be extended to support
    ### objects with different parameters in the different eyes, e.g. to
    ### test ocular dominance.  It is also not clear which types of
    ### randomness to add in, e.g. to provide random positions and
    ### orientations, but not random sizes.
    def use_for_learning(self):
        """
        Lock in the existing KernelFactories as the new default stimulus
        input to the input sheets.  This should work like a test stimuli,
        but the original input generator is not put back afterwards.

        This function does not run() the simulator.
        """
        new_kernels_dict = self._update_inputsheet_kernels()
        original_kernels = self._store_inputsheet_kernels()
        self.register_inputsheet_kernels(new_kernels_dict)
        self.console.auto_refresh()


    def reset_to_defaults(self):
        self.prop_frame.set_values(self.default_values)
        self.input_type.set(self.input_types[0])
        self.present_length.setvalue(DEFAULT_PRESENTATION)
        for each in self.in_ep_dict.keys():
            if not self.in_ep_dict[each]['state']:
                self.input_box.invoke(each)
        self._update_inputsheet_kernels()
        self._refresh_sliders(self.input_type.get())
        if self.auto_refresh: self.refresh()
        if not self.learning.get():
            self.learning_button.invoke()


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
        created from a set of activations defined by the user. We
        don't need a completely new PlotGroup type for this temporary
        plot.

        Post: self.pe_group contains a PlotGroup.
        """
        plist = []
        for each in self.in_ep_dict.keys():
            k = self.in_ep_dict[each]['kernel']
            sv = topo.sheetview.SheetView((k(),k.bounds),src_name=each,
                                          view_type='Kernel')
            plist.append(topo.plot.Plot((sv,None,None),topo.plot.COLORMAP))
        if LIST_REVERSE: plist.reverse()
        self.pe_group = topo.plotgroup.PlotGroup('Preview',None,plist)


    def refresh_title(self): pass

    def refresh(self):
        """
        Use the parent class refresh
        """
        self._update_inputsheet_kernels()
        for entry in self.tparams.values():
            if entry[1].need_to_refresh_slider:
                entry[1].set_slider_from_tag()
        super(InputParamsPanel,self).refresh()

    ### JABHACKALERT!
    ### 
    ### It should be perfectly ok to have multiple InputParamsPanels,
    ### and would be very useful.  E.g. in one panel one could have
    ### defined a horizontal test stimulus, and another a vertical
    ### stimulus, and the user could present either one as he or she
    ### wishes.  For this to work, some of the complicated state saving
    ### and similar code in this file needs to be moved out of this
    ### class, but that's a good idea anyway.  E.g. that code needs to
    ### be available without a GUI, e.g. for measuring preference maps.
    def _reset_and_destroy(self):
        """
        There should only be one InputParamsPanel for the Simulator.
        When the window is made to go away, a new window should be
        allowed.  More importantly, the learning needs to be turned
        back on if the learning had been previously turned off by the
        user.
        """
        if not self.learning.get():
            self.learning_button.invoke()
            self.message("Learning re-enabled.")
            topo.tk.show_cmd_prompt()
        self.console.input_params_window = None
        self.parent.destroy()

