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
import parametersframe
import topo.base.patterngenerator
import topo.plotting.plot
import plotpanel
import Pmw
import topo.base.sheetview 
import topo.base.registry
from Tkinter import IntVar, StringVar, Checkbutton
from Tkinter import TOP, LEFT, RIGHT, BOTTOM, YES, N, S, E, W, X
from topo.base.utils import eval_atof
from topo.sheets.generatorsheet import GeneratorSheet
from topo.base.sheet import BoundingBox, Sheet
from topo.base.utils import find_classes_in_package
from topo.base.patterngenerator import PatternGenerator
from topo.patterns.patternpresent import pattern_present,save_input_generators,restore_input_generators

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
from topo.base.keyedlist import KeyedList

def patterngenerator_names():
    """
    Return the existing list of PatternGenerator names as a KeyedList.

    In the returned dictionary the Keys are the viewable names, and
    the Values are the class names.  This list will change based on
    the existing classes found in the registry, and can be extended by
    the user.
    """
    k = topo.base.registry.pattern_generators.keys()
    k = [(re.sub('Generator$','',name),name) for name in k]  # Cut off 'Generator'
    for i in range(len(k)):        # Add spaces before capital leters
        for c in string.uppercase:
            k[i] = (k[i][0].replace(c,' '+c).strip(),k[i][1])
    return KeyedList(k)


class InputParamsPanel(plotpanel.PlotPanel):
    def __init__(self,parent,pengine,console=None,padding=2,**config):
        super(InputParamsPanel,self).__init__(parent,pengine,console,**config)
        self.plot_group.configure(tag_text='Preview')
        self.INITIAL_PLOT_WIDTH = 100
        self.padding = padding
        self.parent = parent
        self.console = console
        self.learning = IntVar()
        self.learning.set(0)

        # Variables and widgets for maintaining the list of input sheets
        # that will be given the user defined stimuli.
        self.in_ep_dict = {}
        for (each,obj) in self.console.active_simulator().objects(GeneratorSheet).items():
            self.in_ep_dict[each] = {'obj':obj,'state':True,'pattern':None} 
        self.input_box = Pmw.RadioSelect(parent, labelpos = 'w',
                                command = self._input_change,label_text = 'Input Sheets:',
                                frame_borderwidth = 2,frame_relief = 'ridge',
                                selectmode = 'multiple')
        self.input_box.pack(fill = 'x', padx = 5)
        in_ep_names = self.in_ep_dict.keys()
        if LIST_REVERSE: in_ep_names.reverse()  
        for each in in_ep_names:
            self.input_box.add(each)
            self.input_box.invoke(each)

        self.present_length = Pmw.EntryField(self,
                labelpos = 'w',label_text = 'Duration to Present:',
                value = DEFAULT_PRESENTATION,validate = {'validator' : 'real'})
        self.present_length.pack(fill='x', expand=1, padx=10, pady=5)

        buttonBox = Pmw.ButtonBox(self,orient = 'horizontal',padx=0,pady=0)
        buttonBox.pack(side=TOP)
        buttonBox.add('Present', command = self.present)
        buttonBox.add('Reset to Defaults', command = self.reset_to_defaults)
        self.learning_button = Checkbutton(self,text='Network Learning',
                                      variable=self.learning)
        self.learning_button.pack(side=TOP)
        buttonBox.add('Use for future learning',command = self.use_for_learning)

        # Define menu of valid PatternGenerator types
        self.pg_name_dict = patterngenerator_names()
        self.input_types = self.pg_name_dict.keys()
        self.input_type = StringVar()
        self.input_type.set(self.input_types[0])
        Pmw.OptionMenu(self,command = self._refresh_sliders,
                       labelpos = 'w',label_text = 'Input Type:',
                       menubutton_textvariable = self.input_type,
                       items = self.input_types
                       ).pack(side=TOP)
 
        self.param_frame = parametersframe.ParametersFrame(self)
        self._refresh_sliders(self.input_type.get())
        self.param_frame.pack(side=TOP,expand=YES,fill=X)

        self.in_ep_dict = self.param_frame.create_patterns(self.cur_pg_name(),self.in_ep_dict)
        self.refresh()


    def cur_pg_name(self):
        """Readability furction to get the real name of the selected PatternGenerator"""
        return self.pg_name_dict[self.input_type.get()]


    def _input_change(self,button_name, checked):
        """
        The variable checked records the state, either True or False.

        Called by the input box.  The variable self.in_ep_dict records
        all input event processors, and whether they are checked or
        not.
        """
        self.in_ep_dict[button_name]['state'] = checked
        

    def _refresh_sliders(self,new_name):
        """
        Called by the Pmw.OptionMenu object when the user selects a
        PatternGenerator type from the menu.  The visible TaggedSliders
        will be updated.  The old ones are removed, and new ones are
        added to the screen.  The widgets themselves do not change but
        the grid location does.
        """
        new_name = self.pg_name_dict[new_name]
        self.param_frame.refresh_sliders(new_name)
        self.in_ep_dict = self.param_frame.create_patterns(self.cur_pg_name(),self.in_ep_dict)
        if self.auto_refresh: self.refresh()


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
        new_patterns_dict = self.param_frame.create_patterns(self.cur_pg_name(),self.in_ep_dict)
        input_dict = dict([(name,d['pattern'])
                           for (name,d) in new_patterns_dict.items()])
        pattern_present(input_dict,self.present_length.getvalue(),
                        learning=self.learning.get(),overwrite_previous=False)
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
        new_patterns_dict = self.param_frame.create_patterns(self.cur_pg_name(),self.in_ep_dict)
        input_dict = dict([(name,d['pattern'])
                           for (name,d) in new_patterns_dict.items()])
        # a call to save_input_generators would allow recovery of earlier patterns
        pattern_present(input_dict,0.0,sim=None,learning=True)
        self.console.auto_refresh()


    def reset_to_defaults(self):
        self.param_frame.reset_to_defaults()
        self.input_type.set(self.input_types[0])
        self.present_length.setvalue(DEFAULT_PRESENTATION)
        for each in self.in_ep_dict.keys():
            if not self.in_ep_dict[each]['state']:
                self.input_box.invoke(each)
        self.in_ep_dict = self.param_frame.create_patterns(self.cur_pg_name(),self.in_ep_dict)
        self._refresh_sliders(self.input_type.get())
        if self.auto_refresh: self.refresh()
        if self.learning.get():
            self.learning_button.invoke()


    def do_plot_cmd(self):
        """
        Replace the superclass do_plot_cmd.
        Create a PlotGroup that has a list of Plots that have been
        created from a set of activitys defined by the user. We
        don't need a completely new PlotGroup type for this temporary
        plot.

        Return self.pe_group which contains a PlotGroup.
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
        Refresh this class and also call the parent class refresh.
        """
        self.in_ep_dict = self.param_frame.create_patterns(self.cur_pg_name(),self.in_ep_dict)
        self.param_frame.refresh()
        super(InputParamsPanel,self).refresh()

