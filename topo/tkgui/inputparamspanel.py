"""
InputParamsPanel

Sliders panel for inputs

# CEBHACKALERT: I will update this.

The list of valid Input Types is automatically generated from the
PatternGenerator subclasses found in topo.base.patterngenerator (which
can be extended by the user by setting a variable in that namespace to
the name of their new class).  Every Parameter defined in the
PatternGenerator subclass will be shown in the window.

The Preview panel draws heavily from the PlotGroupPanel class, and instead
of using a PlotGroup subclass, creates a group on the fly.  

$Id$
"""
__version__='$Revision$'

import __main__
import math
import parametersframe
import topo.base.patterngenerator
import topo.plotting.plot
import plotgrouppanel
import Pmw
import topo.base.sheetview 
import topoconsole
from Tkinter import IntVar, StringVar, Checkbutton
from Tkinter import TOP, LEFT, RIGHT, BOTTOM, YES, N, S, E, W, X
import topo.base.parameter
from topo.base.utils import eval_atof,find_classes_in_package, classname_repr, class_parameters
from topo.sheets.generatorsheet import GeneratorSheet
from topo.base.sheet import Sheet

from topo.commands.basic import pattern_present,save_input_generators,restore_input_generators
from copy import deepcopy

# Hack to reverse the order of the input EventProcessor list and the
# Preview plot list, so that it'll match the order that the plots appear
# in the Activity panel.
LIST_REVERSE = True

# Default time to show in the Presentation duration box.
DEFAULT_PRESENTATION = '1.0'


class InputParamsPanel(plotgrouppanel.PlotGroupPanel):
    def __init__(self,parent,pengine,console=None,padding=2,**config):
        super(InputParamsPanel,self).__init__(parent,pengine,console,plot_group_key='Preview',**config)

        self.INITIAL_PLOT_WIDTH = 100
        self.padding = padding
        self.parent = parent
        self.console = console
        self.learning = IntVar()
        self.learning.set(0)

        # Variables and widgets for maintaining the list of input sheets
        # that will be given the user defined stimuli.
        self.in_ep_dict = {}
        for (each,obj) in topoconsole.active_sim().objects(GeneratorSheet).items():
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

        # CEBHACKALERT: this is just temporary while I reorganize these files.
        # Take the list of PatternGenerators from the first GeneratorSheet's
        # input_generator PatternGeneratorParameter for now.
        for thing in self.in_ep_dict.values():
            generator_sheet = thing['obj']
            generator_sheet_params = generator_sheet.get_paramobj_dict()
            self.pg_name_dict = generator_sheet_params['input_generator'].range()
            break
            
        self.input_types = self.pg_name_dict.keys()
        self.input_type = StringVar()
        self.input_type.set(self.input_types[0])


        Pmw.OptionMenu(self,command = self._refresh_widgets,
                       labelpos = 'w',label_text = 'Input Type:',
                       menubutton_textvariable = self.input_type,
                       items = self.input_types
                       ).pack(side=TOP)
 
        self.param_frame = parametersframe.ParametersFrame(self)
        self._refresh_widgets(self.input_type.get())
        self.param_frame.pack(side=TOP,expand=YES,fill=X)

        self.in_ep_dict = self.create_patterns(self.cur_pg_name(),self.in_ep_dict)
        self.refresh()


    @staticmethod
    def valid_context():
        """
        Only open if GeneratorSheets are in the Simulator.
        """
        sim = topoconsole.active_sim()
        if sim.objects(GeneratorSheet).items():
            return True
        else:
            return False
        

    def cur_pg_name(self):
        """Return the name of the selected PatternGenerator, as text."""
        return self.pg_name_dict[self.input_type.get()]


    def _input_change(self,button_name, checked):
        """
        The variable checked records the state, either True or False.

        Called by the input box.  The variable self.in_ep_dict records
        all input event processors, and whether they are checked or
        not.
        """
        self.in_ep_dict[button_name]['state'] = checked
        

    def _refresh_widgets(self,new_name):
        """
        Called by the Pmw.OptionMenu object when the user selects a
        PatternGenerator type from the menu.  The visible TaggedSliders
        will be updated.  The old ones are removed, and new ones are
        added to the screen.  The widgets themselves do not change but
        the grid location does.
        """
        pg_class = self.pg_name_dict[new_name]
        
        self.param_frame.create_widgets(pg_class)
        self.in_ep_dict = self.create_patterns(self.cur_pg_name(),self.in_ep_dict)
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
        new_patterns_dict = self.create_patterns(self.cur_pg_name(),self.in_ep_dict)
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
        new_patterns_dict = self.create_patterns(self.cur_pg_name(),self.in_ep_dict)
        input_dict = dict([(name,d['pattern'])
                           for (name,d) in new_patterns_dict.items()])
        pattern_present(input_dict,0.0,sim=None,learning=True,overwrite_previous=True)
        self.console.auto_refresh()


    def reset_to_defaults(self):
        self.param_frame.reset_to_defaults()
        self.input_type.set(self.input_types[0])
        self.present_length.setvalue(DEFAULT_PRESENTATION)
        for each in self.in_ep_dict.keys():
            if not self.in_ep_dict[each]['state']:
                self.input_box.invoke(each)
        self.in_ep_dict = self.create_patterns(self.cur_pg_name(),self.in_ep_dict)
        self._refresh_widgets(self.input_type.get())
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
        view_dict = {}
        for each in self.in_ep_dict.keys():
            k = self.in_ep_dict[each]['pattern']
            sv = topo.base.sheetview.SheetView((k(),k.bounds),src_name=each,
                                          view_type='Pattern')
	    view_dict[each] = sv
	    ### JCALERT ! This is working for the moment but that could be made simpler
            ### (which is also true for most of the file!!)
	    channels = {'Strength':each,'Hue':None,'Confidence':None}
            plist.append(topo.plotting.plot.Plot(channels,view_dict, name=''))
        if LIST_REVERSE: plist.reverse()
        self.pe_group = topo.plotting.plotgroup.PlotGroup(self.pe.simulation,plot_group_key='Preview',plot_list=plist)


    def refresh_title(self): pass

    def refresh(self):
        """
        Refresh this class and also call the parent class refresh.
        """
        self.in_ep_dict = self.create_patterns(self.cur_pg_name(),self.in_ep_dict)
        self.param_frame.refresh()
        super(InputParamsPanel,self).refresh()


    ### JABHACKALERT! Ideally this would move out of tkgui/ altogether.
    ###
    ### JAB: It is not clear how this will need to be extended to support
    ### objects with different parameters in the different eyes, e.g. to
    ### test ocular dominance.
    def create_patterns(self,pg_name,ep_dict):
        """
        Make an instantiation of the current user patterns.

        Gets the values set on the panel, and creates the PatternGenerator
        pg_name with its Parameters set to those values.

        Also does some other things...
        """
        parameters = dict(class_parameters(pg_name))
        input_values = self.param_frame.get_values()
        
        new_parameter_values = {}
        
        for (name,parameter) in parameters.items():
            if isinstance(parameter, topo.base.parameter.Number):
                # Numbers are changed back from string to float
                new_parameter_values[name] = eval_atof(input_values[name])
            elif isinstance(parameter, topo.base.parameter.PackageParameter):
                parameter.set_from_key(input_values[name])
                new_parameter_values[name] = parameter.default
            else:
                new_parameter_values[name] = input_values[name]                


        # If the 'state' is turned off (from a button on the Frame),
        # then do not change the currently stored generator.  This
        # allows eyes to have different presentation patterns.
        for each in ep_dict.keys():
            if ep_dict[each]['state']:
                new_parameter_values['density'] = ep_dict[each]['obj'].density
                new_parameter_values['bounds'] = deepcopy(ep_dict[each]['obj'].bounds)
                pg = pg_name(**new_parameter_values)
                ep_dict[each]['pattern'] = pg
        return ep_dict  


