"""
InputParamsPanel

Sliders panel for inputs

The list of valid Input Types is retrieved from the registry, and
would normally contain an automatically generated list of
PatternGenerator subclasses found in topo.base.patterngenerator.  Every
Parameter defined in the PatternGenerator subclass will be taken with the
intersection of valid TaggedSlider types defined in this class and
then shown in the window.

The Preview panel draws heavily from the PlotPanel class, and instead
of using a PlotGroup subclass, creates a group on the fly.  

$Id$
"""
import __main__
import math, string, re
import parameterframe
import topo.base.patterngenerator
import topo.plotting.plot
import plotpanel
import Pmw
import topo.base.sheetview 
import topo.base.registry
from Tkinter import IntVar, StringVar, Checkbutton
from Tkinter import TOP, LEFT, RIGHT, BOTTOM, YES, N, S, E, W, X
from copy import deepcopy
from topo.base.utils import eval_atof
from topo.sheets.generatorsheet import GeneratorSheet
from topo.base.sheet import BoundingBox, Sheet
from topo.base.utils import find_classes_in_package
from topo.base.patterngenerator import PatternGenerator
from topo.patterns.patternpresent import generator_eps, pattern_present

# Hack to reverse the order of the input EventProcessor list and the
# Preview plot list, so that it'll match the order that the plots appear
# in the Activity panel.
LIST_REVERSE = True

# Default time to show in the Presentation duration box.
DEFAULT_PRESENTATION = '1.0'


# By default, none of the pattern types in topo/patterns/ are imported
# in Topographica, but for the GUI, we want all of them to be
# available as a list from which the user can select. To do this, we
# import all of the PatternGenerator classes in all of the modules
# mentioned in topo.patterns.__all__, and will also use any that the
# user has defined and registered.
from topo.patterns import *
patternclasses=find_classes_in_package(topo.patterns,PatternGenerator)
topo.base.registry.pattern_generators.update(patternclasses)



    

def patterngenerator_names():
    """
    Return the existing list of PatternGenerator subclasses.  This list
    will change based on the existing classes found in the registry,
    and can be extended by the user.
    """
    k = topo.base.registry.pattern_generators.keys()
    k = [re.sub('Generator$','',name) for name in k]  # Cut off 'Generator'
    for i in range(len(k)):        # Add spaces before capital leters
        for c in string.uppercase:
            k[i] = k[i].replace(c,' '+c).strip()
    return k


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

        # Variables and widgets for maintaining the list of input sheets
        # that will be given the user defined stimuli.
        self.in_ep_dict = {}
        for (each,obj) in generator_eps(self.console.active_simulator()).items():
            self.in_ep_dict[each] = {'obj':obj,'state':True,'pattern':None} 
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
        buttonBox.add('Use for future learning',command = self.use_for_learning)

        # Define menu of valid PatternGenerator types
        self.input_types = patterngenerator_names()
        
        self.input_type = StringVar()
        self.input_type.set(self.input_types[0])
        Pmw.OptionMenu(self,
                       command = self._refresh_sliders,
                       labelpos = 'w',
                       label_text = 'Input Type:',
                       menubutton_textvariable = self.input_type,
                       items = self.input_types
                       ).pack(side=TOP)
 
        self.param_frame = parameterframe.ParameterFrame(self)


# How to access the list of non-hidden Parameters in a PatternGenerator object
#        # Test to find the params and names.
#        pgc = topo.base.registry.pattern_generators[kf_classname] 
#        pg = pgc()
#        plist = [(k,v)
#                 for (k,v)  # ('name':'...', 'density':10000, ...)
#                 in pg.get_paramobj_dict().items()
#                 if not v.hidden
#                 ]
#        print plist


        self._refresh_sliders(self.input_type.get())
        self.param_frame.pack(side=TOP,expand=YES,fill=X)

        # Hook to turn learning back on when Panel is closed.
        self.parent.protocol('WM_DELETE_WINDOW',self._reset_and_destroy)

        self.default_values = self.param_frame.prop_frame.get_values()
        self._create_inputsheet_patterns()
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
                    each.learning = False
                    each.activity_push()
        else: # Turn learning back on and restore
            sim.state_pop()
            for each in sim.get_event_processors():
                if isinstance(each,Sheet):
                    each.learning = True
                    each.activity_pop()
            

    def _refresh_sliders(self,new_name):
        """
        Called by the Pmw.OptionMenu object when the user selects a
        PatternGenerator type from the menu.  The visible TaggedSliders
        will be updated.  The old ones are removed, and new ones are
        added to the screen.  The widgets themselves do not change but
        the grid location does.
        """
        new_name = new_name.replace(' ','') + 'Generator'
        # How to wipe the widgets off the screen
        for (s,c) in self.param_frame.tparams.values():
            s.grid_forget()
            c.grid_forget()
        # Make relevant parameters visible.
        new_sliders = self.relevant_parameters(new_name,self.param_frame.tparams.keys())
        for i in range(len(new_sliders)):
            (s,c) = self.param_frame.tparams[new_sliders[i]]
            s.grid(row=i,column=0,padx=self.padding,
                   pady=self.padding,sticky=E)
            c.grid(row=i,
                   column=1,
                   padx=self.padding,
                   pady=self.padding,
                   sticky=N+S+W+E)
        self._create_inputsheet_patterns()
        if self.auto_refresh: self.refresh()


    def relevant_parameters(self,kf_classname,param_list):
        """
        Pre:  kf_classname is the string name of a PatternGenerator subclass.
              param_list is a list of strings of parameter tagged sliders
              that are viewable from the window.
        Post: List of strings that is the Intersection of kf_classname's
              class member keys, and param_list entries.
        """

        kf_class_keylist = topo.base.registry.pattern_generators[kf_classname].__dict__.keys()
        rlist = [s for s in param_list if s in kf_class_keylist]

        return rlist



    def present(self):
        """
        Move the user created patterns into the GeneratorSheets, run for
        the specified length of time, then restore the original
        patterns.  The system may become unstable if the user breaks
        this thread so that the original patterns are not properly
        restored, but then there are going to be other problems with
        the Simulator state if a run is interrupted.

        This function is run no matter if learning is enabled or
        disabled since run() will detect sheet attributes.
        """
        new_patterns_dict = self._create_inputsheet_patterns()
        input_dict = dict([(name,d['pattern'])
                           for (name,d) in new_patterns_dict.items()])
        pattern_present(input_dict,self.present_length.getvalue())
        self.console.auto_refresh()


    ### JAB: It is not clear how this will need to be extended to support
    ### objects with different parameters in the different eyes, e.g. to
    ### test ocular dominance.  It is also not clear which types of
    ### randomness to add in, e.g. to provide random positions and
    ### orientations, but not random sizes.
    def use_for_learning(self):
        """
        Lock in the existing PatternFactories as the new default stimulus
        input to the input sheets.  This should work like a test stimuli,
        but the original input generator is not put back afterwards.

        This function does run() the simulator but for 0.0 time.
        """
        new_patterns_dict = self._create_inputsheet_patterns()
        input_dict = dict([(name,d['pattern'])
                           for (name,d) in new_patterns_dict.items()])
        pattern_present(input_dict,0.0,sim=None,restore=False)
        self.console.auto_refresh()



    ### JAB: It is not clear how this will need to be extended to support
    ### objects with different parameters in the different eyes, e.g. to
    ### test ocular dominance.
    def _create_inputsheet_patterns(self):
        """
        Make an instantiation of the current user pattern in
        preparation of passing in the set to the pattern presentation
        function.  The new pattern generator will be placed in a
        dictionary for the input sheet under the key 'pattern'.

        If the 'state' is turned off (from a button on the Frame),
        then do not change the currently stored generator.  This
        allows eyes to have different presentation patterns.
        """
        kname = self.input_type.get() + 'Generator'
        kname = kname.replace(' ','')
        p = self.get_params()
        rp = self.relevant_parameters(kname,self.param_frame.tparams.keys())
        ndict = {}
        ### JABHACKALERT!
        ###
        ### How will this work for photographs and other items that need non-numeric
        ### input boxes?  It *seems* to be assuming that everything is a float.
        for each in rp:
            ndict[each] = eval_atof(p[each])
        for each in self.in_ep_dict.keys():
            if self.in_ep_dict[each]['state']:
                ndict['density'] = self.in_ep_dict[each]['obj'].density
                ndict['bounds'] = deepcopy(self.in_ep_dict[each]['obj'].bounds)
                pg = topo.base.registry.pattern_generators[kname](**ndict)
                self.in_ep_dict[each]['pattern'] = pg
        return self.in_ep_dict  # Doesn't have to return it, but is explicit.


    def reset_to_defaults(self):
        self.param_frame.prop_frame.set_values(self.default_values)
        self.input_type.set(self.input_types[0])
        self.present_length.setvalue(DEFAULT_PRESENTATION)
        for each in self.in_ep_dict.keys():
            if not self.in_ep_dict[each]['state']:
                self.input_box.invoke(each)
        self._create_inputsheet_patterns()
        self._refresh_sliders(self.input_type.get())
        if self.auto_refresh: self.refresh()
        if not self.learning.get():
            self.learning_button.invoke()


    def get_params(self):
        """Get the property values as a dictionary."""
        params = self.param_frame.prop_frame.get_values()

# With no Photograph option, this block is not useful.  Something similar
# may have to go back in once Photograph patterns are created.
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
        created from a set of activitys defined by the user. We
        don't need a completely new PlotGroup type for this temporary
        plot.

        Post: self.pe_group contains a PlotGroup.
        """
        plist = []
        for each in self.in_ep_dict.keys():
            k = self.in_ep_dict[each]['pattern']
            sv = topo.base.sheetview.SheetView((k(),k.bounds),src_name=each,
                                          view_type='Pattern')
            plist.append(topo.plotting.plot.Plot((sv,None,None),topo.plotting.plot.COLORMAP))
        if LIST_REVERSE: plist.reverse()
        self.pe_group = topo.plotting.plotgroup.PlotGroup('Preview',None,plist)


    def refresh_title(self): pass

    def refresh(self):
        """
        Use the parent class refresh
        """
        self._create_inputsheet_patterns()
        for entry in self.param_frame.tparams.values():
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

