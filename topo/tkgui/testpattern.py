"""
TestPattern

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

from topo.plotting.plot import make_plot
import plotgrouppanel
import Pmw
import topo.base.sheetview 
import topoconsole
from Tkinter import IntVar, StringVar, Checkbutton
from Tkinter import TOP, LEFT, RIGHT, BOTTOM, YES, N, S, E, W, X
import topo.base.parameter
from topo.base.utils import eval_atof,find_classes_in_package, classname_repr
from topo.sheets.generatorsheet import GeneratorSheet
from topo.base.sheet import Sheet
from topo.base.topoobject import class_parameters

from topo.commands.basic import pattern_present,save_input_generators,restore_input_generators
from copy import deepcopy

# Hack to reverse the order of the input EventProcessor list and the
# Preview plot list, so that it'll match the order that the plots appear
# in the Activity panel.
LIST_REVERSE = True

# Default time to show in the Presentation duration box.
DEFAULT_PRESENTATION = '1.0'


class TestPattern(plotgrouppanel.PlotGroupPanel):
    def __init__(self,parent,pengine,console=None,padding=2,**config):
        super(TestPattern,self).__init__(parent,pengine,console,plot_group_key='Preview',**config)

        self.INITIAL_PLOT_WIDTH = 100
        self.padding = padding
        self.parent = parent
        self.console = console
        self.learning = IntVar()
        self.learning.set(0)

        # Variables and widgets for maintaining the list of input sheets
        # that will be given the user defined stimuli.
        self.gen_sheets = {}
        for (gen_sheet_name,gen_sheet) in topoconsole.active_sim().objects(GeneratorSheet).items():
            self.gen_sheets[gen_sheet_name] = {'obj':gen_sheet,'state':True,'pattern':None} 

        # duration to present stuff
        self.present_length = Pmw.EntryField(self,
                labelpos = 'w',label_text = 'Duration to Present:',
                value = DEFAULT_PRESENTATION,validate = {'validator' : 'real'})
        self.present_length.pack(fill='x', expand=1, padx=10, pady=5)

        # Draw on GeneratorSheet boxes
        # CEBHACKALERT: (1) these don't work (temporarily: the system of
        # creating the patterns to draw will be changed first).
        # (2) don't want these boxes up so high on window, should be lower
        #self.input_box = Pmw.RadioSelect(parent, labelpos = 'w',
        #                        command = self._input_change,label_text = 'Draw on:',
        #                        frame_borderwidth = 2,frame_relief = 'ridge',
        #                        selectmode = 'multiple')
        #self.input_box.pack(fill = 'x', padx = 5)

        #gen_sheet_names = self.gen_sheets.keys()
        #if LIST_REVERSE: gen_sheet_names.reverse() # what?
        #for gen_sheet_name in gen_sheet_names:
        #    self.input_box.add(gen_sheet_name)
        #    self.input_box.invoke(gen_sheet_name)

        # buttons relating to generator sheets
        buttonBox = Pmw.ButtonBox(self,orient = 'horizontal',padx=0,pady=0)
        buttonBox.pack(side=TOP)
        buttonBox.add('Present', command=self.present)
        buttonBox.add('Reset to defaults', command=self.reset_to_defaults)

        # learning buttons
        # CEBHACKALERT: I think this doesn't work at the moment
        self.learning_button = Checkbutton(self,text='Network Learning',
                                      variable=self.learning)
        self.learning_button.pack(side=TOP)
        # buttonBox.add('Use for future learning',command = self.use_for_learning)
        

        # Define menu of valid PatternGenerator types

        # CEBHACKALERT: this is just temporary while I reorganize these files.
        # Take the list of PatternGenerators from the first GeneratorSheet's
        # input_generator PatternGeneratorParameter for now.
        for thing in self.gen_sheets.values():
            generator_sheet = thing['obj']
            generator_sheet_params = generator_sheet.get_paramobj_dict()
            self.pg_name_dict = generator_sheet_params['input_generator'].range()
            break

        self.pattern_generators = self.pg_name_dict.keys()
        self.pattern_generator = StringVar()
        self.pattern_generator.set(self.pattern_generators[0])

        # PatternGenerator choice box
        Pmw.OptionMenu(self,command = self._refresh_widgets,
                       labelpos = 'w',label_text = 'Pattern generator:',
                       menubutton_textvariable = self.pattern_generator,
                       items = self.pattern_generators
                       ).pack(side=TOP)
 
        # ParametersFrame
        self.param_frame = parametersframe.ParametersFrame(self)


        self._refresh_widgets(self.pattern_generator.get())

        self.param_frame.pack(side=TOP,expand=YES,fill=X)

        self.gen_sheets = self.create_patterns(self.gen_sheets)


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

        
    def _input_change(self,button_name, checked):
        """
        The variable checked records the state, either True or False.

        Called by the input box.  The variable self.gen_sheets records
        all input event processors, and whether they are checked or
        not.
        """
        self.gen_sheets[button_name]['state'] = checked
        

    def _refresh_widgets(self,new_name):
        """
        Called by the Pmw.OptionMenu object when the user selects a
        PatternGenerator type from the menu.  The visible TaggedSliders
        will be updated.  The old ones are removed, and new ones are
        added to the screen.  
        """
        self.pg = self.pg_name_dict[new_name]()
        self.param_frame.create_widgets(self.pg)
        self.gen_sheets = self.create_patterns(self.gen_sheets)
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
        new_patterns_dict = self.create_patterns(self.gen_sheets)
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
        new_patterns_dict = self.create_patterns(self.gen_sheets)
        input_dict = dict([(name,d['pattern'])
                           for (name,d) in new_patterns_dict.items()])
        pattern_present(input_dict,0.0,sim=None,learning=True,overwrite_previous=True)
        self.console.auto_refresh()


    # CEBHACKALERT
    def reset_to_defaults(self):        
        # self.param_frame.reset_to_defaults()
        # self.pattern_generator.set(self.pattern_generators[0])
        self.present_length.setvalue(DEFAULT_PRESENTATION)
        for each in self.gen_sheets.keys():
            if not self.gen_sheets[each]['state']:
                self.input_box.invoke(each)
        self.gen_sheets = self.create_patterns(self.gen_sheets)        
        self._refresh_widgets(self.pattern_generator.get())
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
        for each in self.gen_sheets.keys():
            k = self.gen_sheets[each]['pattern']
            sv = topo.base.sheetview.SheetView((k(),k.bounds),src_name=each,
                                          view_type='Pattern')
	    view_dict[each] = sv
	    ### JCALERT ! This is working for the moment but that could be made simpler
            ### (which is also true for most of the file!!)
	    channels = {'Strength':each,'Hue':None,'Confidence':None}
            plist.append(make_plot(channels,view_dict,name=''))
        if LIST_REVERSE: plist.reverse()
        ### JCALERT! It is the only call to PlotGroup with template is None. Need to change.
        self.pe_group = topo.plotting.plotgroup.PlotGroup(self.pe.simulation,None,plot_group_key='Preview',plot_list=plist)


    def refresh_title(self): pass

    def refresh(self):
        """
        Refresh this class and also call the parent class refresh.
        """
        self.gen_sheets = self.create_patterns(self.gen_sheets)
        self.param_frame.refresh()
        super(TestPattern,self).refresh()



    ### JABHACKALERT! Ideally this would move out of tkgui/ altogether.
    ###
    ### JAB: It is not clear how this will need to be extended to support
    ### objects with different parameters in the different eyes, e.g. to
    ### test ocular dominance.
    def create_patterns(self,ep_dict):
        """
        Make an instantiation of the current user patterns.

        Also does some other things...
        """

        # CEBHACKALERT: this method (still) sets bounds and density
        # every time the pattern's redrawn.

        # This whole system will be changed significanly. For one thing,
        # these lines need only run once, until the patterngenerator is
        # changed again.

        self.param_frame.set_obj_params()
        pg = self.param_frame.topo_obj

        for each in ep_dict.keys():
            setattr(pg,'bounds',deepcopy(ep_dict[each]['obj'].bounds))
            setattr(pg,'density', ep_dict[each]['obj'].density)
            ep_dict[each]['pattern'] = pg

        return ep_dict
