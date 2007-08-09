"""
TestPattern

Sliders panel for inputs


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



# CEBALERT: this file needs a substantial overhaul before it will work
# well.

# CEBALERT: taggedsliders refresh the display even when auto-refresh is off.



import copy
import Pmw

import topo

import topo.base.patterngenerator
import topo.base.sheetview

from topo.sheets.generatorsheet import GeneratorSheet
from topo.commands.basic import pattern_present
from topo.plotting.plotgroup import identity

from topo.misc.keyedlist import KeyedList

import parametersframe
from plotgrouppanel import XPGPanel
#from templateplotgrouppanel import TemplatePlotGroupPanel
import topoconsole

from topo.plotting.plot import make_template_plot

from Tkinter import IntVar, StringVar, Checkbutton
from Tkinter import TOP, LEFT, RIGHT, BOTTOM, YES, N, S, E, W, X,NO,NONE

# Default time to show in the Presentation duration box.
DEFAULT_PRESENTATION = '1.0'


class TestPattern(XPGPanel):

    
    def __init__(self,console,master,label="Preview",**params):
	super(TestPattern,self).__init__(console,master,label,**params)

        # CB: remove updatecommand,redraw etc stuff...remember to remove from 2
        self.plotcommand_frame.pack_forget()
        self._furames['update_command'][0].pack_forget()
        
        self._furames['Fwd'][0].pack_forget()
        self._furames['Back'][0].pack_forget()
        

        self.padding = 2
        self.auto_refresh=True

        
        ### Find the GeneratorSheets in the simulation, set up generator_sheet_patterns dictionary
        # CEBALERT: this has a difficult structure to work with.
        # generator_sheets_patterns = 
        # {generator_sheet_name:  { 'generator_sheet': <gs_obj>,
        #                           'editing': True/False,
        #                           'pattern_generator': <pg_obj> }
        #                         }    
        self.generator_sheets_patterns = {}
        for (gen_sheet_name,gen_sheet) in topo.sim.objects(GeneratorSheet).items():
            self.generator_sheets_patterns[gen_sheet_name] = {'generator_sheet': gen_sheet,
                                                              'editing': True,
                                                              'pattern_generator': None} 

        ### learning buttons
        #
        self.learning = IntVar()
        self.learning.set(0)
        self.learning_button = Checkbutton(self,text='Network Learning',
                                      variable=self.learning)
        self.learning_button.pack(side=TOP)
        self.balloon.bind(self.learning_button,
"""Whether to enable learning during presentation.""")

        # buttonBox.add('Use for future learning',command = self.use_for_learning)


        ### 'Duration to present' box
        #
        self.present_length = Pmw.EntryField(self,
                labelpos = 'w',label_text = 'Duration to Present:',
                value = DEFAULT_PRESENTATION,validate = {'validator' : 'real'},
                command = self.present)
        self.present_length.pack(fill=NONE, expand=NO, padx=10, pady=5)
        self.balloon.bind(self.present_length,
"""How long to run the simulator when presenting.""")


        ### 'Present'/'reset to defaults' buttons  (i.e. re: patterns themselves)
        #
        buttonBox = Pmw.ButtonBox(self,orient = 'horizontal',padx=0,pady=0)
        buttonBox.pack(side=TOP)
        
        present_button = buttonBox.add('Present', command=self.present)
        self.balloon.bind(present_button,
"""Present this pattern to the simulation.""")

        reset_button = buttonBox.add('Reset to defaults', command=self.reset_to_defaults)
        self.balloon.bind(reset_button,
"""Reset the parameters for this pattern back to their defaults.""")


        ### Menu of PatternGenerator types
        #
        # CEBALERT: seems like a poor way of doing this (just written
        # to get it working).
        # Take the list of PatternGenerators from the first
        # GeneratorSheet's input_generator PatternGeneratorParameter.
        #
        # pattern_generators = {'Pattern': <PatternGenerator_obj>}
        for generator_sheet_name in self.generator_sheets_patterns.values():
            generator_sheet_params = generator_sheet_name['generator_sheet'].params()
            pattern_generators = generator_sheet_params['input_generator'].range()
            break
        
        self.pattern_generators = KeyedList()
        self.pattern_generators.update(pattern_generators)

        # CEBALERT: remove OneDPowerSpectrum from list of pattern generators
        # because it doesn't yet work with the test pattern window.
        # (I think because plotting assumes 2d matrices when PatternGenerators are
        # called.)
        self.pattern_generators.remove(('OneDPowerSpectrum',topo.patterns.basic.OneDPowerSpectrum))
        
        self.pattern_generators.sort()  # sorted so the pgs appear alphabetically

        self.__current_pattern_generator = GeneratorSheet.classparams()['input_generator'].default

        
        self.__current_pattern_generator_name = StringVar()
        # CEBALERT: presumably can set the current pg from the name in a better way
        for (pg_name,pg) in self.pattern_generators.items():
            if pg==type(self.__current_pattern_generator):
                self.__current_pattern_generator_name.set(pg_name)
                self.__default_pattern_generator_name = pg_name #CEBALERT: don't need to store this, right?

        # PatternGenerator choice box
        self.pg_choice_box = Pmw.OptionMenu(self,
                                            command = self.__change_pattern_generator,
                                            labelpos = 'w',
                                            label_text = 'Pattern generator:',
                                            menubutton_textvariable = self.__current_pattern_generator_name,
                                            items = self.pattern_generators.keys())
        self.pg_choice_box.pack(side=TOP)
        self.balloon.bind(self.pg_choice_box,
"""Type of pattern to present.
Each type will have various parameters that can be changed.""")


        ### The ParametersFrame
        #
        # Because this window applies changes to an object immediately
        # (unlike ParametersFrame), the button to 'reset' is
        # 'Defaults'. 'Reset' would do nothing.
        self.__params_frame = parametersframe.ParametersFrame(self,buttons_to_remove=['Apply','Close','Reset'])
        self.__params_frame.create_widgets(self.__current_pattern_generator)
        self.__params_frame.pack(side=TOP,expand=YES,fill=X)

        ### 'Edit patterns in' boxes
        #
        # CEBHACKALERT: Buttons seem to have strange behavior!
        # Also, will boxes be in the same order as the plots?
        self.__input_box = Pmw.RadioSelect(self, labelpos = 'w',
                                           command = self._input_change,
                                           label_text = 'Apply to pattern in:',
                                           selectmode = 'multiple')
        self.__input_box.pack(expand=NO,fill=NONE,padx=5)

        keys = copy.copy(self.generator_sheets_patterns.keys())
        keys.reverse()
        for generator_sheet_name in keys:
            self.__input_box.add(generator_sheet_name)
            self.__input_box.invoke(generator_sheet_name)

        self.__change_pattern_generator(self.__current_pattern_generator_name.get())
	self.refresh()


    @staticmethod
    def valid_context():
        """
        Only open if GeneratorSheets are in the Simulation.
        """
        sim = topo.sim
        if sim.objects(GeneratorSheet).items():
            return True
        else:
            return False


    def refresh(self):
        """
        Change the pattern generator objects as required

        Also call the parent class refresh.
        """
        self.update_plotgroup_variables()
        self.__setup_pattern_generators()
        super(TestPattern,self).refresh()


        
    def _input_change(self,button_name, checked):
        """
        The variable checked records the state, either True or False.

        Called by the input box.  The variable self.generator_sheets_patterns records
        all input event processors, and whether they are checked or
        not.
        """
        self.generator_sheets_patterns[button_name]['editing'] = checked

        if not self.generator_sheets_patterns[button_name]['editing']:
            self.generator_sheets_patterns[button_name]['pattern_generator'] = copy.copy(self.__current_pattern_generator)
        else:
            if self.auto_refresh:
                self.__setup_pattern_generators()
                self.refresh()
        

    def __change_pattern_generator(self,pattern_generator_name):
        """
        Change to the selected PatternGenerator.

        Set the current PatternGenerator to the one selected and get the
        ParametersFrame to draw the relevant widgets
        """
        self.__current_pattern_generator = self.pattern_generators[pattern_generator_name]()
        self.__params_frame.create_widgets(self.__current_pattern_generator)
        if self.auto_refresh:
	    self.refresh()
            self.refresh() # CEBHACKALERT! No comment


    def present(self):
        """
        Move the user created patterns into the GeneratorSheets, run for
        the specified length of time, then restore the original
        patterns.  The system may become unstable if the user breaks
        this thread so that the original patterns are not properly
        restored, but then there are going to be other problems with
        the Simulation state if a run is interrupted.

        This function is run no matter if learning is enabled or
        disabled since run() will detect sheet attributes.
        """

	topo.sim.state_push()
        self.__setup_pattern_generators()
        input_dict = dict([(name,d['pattern_generator'])
                           for (name,d) in self.generator_sheets_patterns.items()])
        pattern_present(input_dict,self.present_length.getvalue(),
                        learning=self.learning.get(),overwrite_previous=False)

        self.console.auto_refresh()
	topo.sim.state_pop()

    def use_for_learning(self):
        """
        Lock in the existing PatternFactories as the new default stimulus
        input to the input sheets.  This should work like a test stimuli,
        but the original input generator is not put back afterwards.

        This function does run() the simulation, but for 0.0 time.
        """
        #self.__setup_pattern_generators()
        #input_dict = dict([(name,d['pattern_generator'])
        #                   for (name,d) in new_patterns_dict.items()])
        #pattern_present(input_dict,0.0,learning=True,overwrite_previous=True)
        #self.console.auto_refresh()
        pass



    def reset_to_defaults(self):
        """
        Reset to default presentation length, no learning, and the original PatternGenerator.
        """
        self.present_length.setvalue(DEFAULT_PRESENTATION)
        self.learning_button.deselect()
        self.pg_choice_box.invoke(self.__default_pattern_generator_name)
        if self.auto_refresh: self.refresh()


    ### JCALERT! This has to be re-implemented for testpattern, it has to be done in a better way:
    ### it does not work for integerscaling being on.
    def update_plotgroup_variables(self):
        """
        Replace the superclass do_plot_cmd.
        Create a PlotGroup that has a list of Plots that have been
        created from a set of activities defined by the user. We
        don't need a completely new PlotGroup type for this temporary
        plot.

        Return self.pe_group which contains a PlotGroup.
        """
        plot_list = []       
        for each in self.generator_sheets_patterns.keys():
            view_dict = {}
            k = self.generator_sheets_patterns[each]['pattern_generator']
            # xdensity and ydensity are the same for the pattern_generator
            # because they were set from a Sheet xdensity and ydensity,
            # which are guaranteed to be the same
	    density = k.xdensity
            
	    view_dict[each] = topo.base.sheetview.SheetView((k(),k.bounds),src_name=each)
	    channels = {'Strength':each,'Hue':None,'Confidence':None}
	    ### JCALERT! it is not good to have to pass '' here... maybe a test in plot would be better
	    plot_list.append(make_template_plot(channels,view_dict,density,None,self.normalize,name=''))


        # CEBHACKALERT (** change   any point marking hackalerts in here?
	new_plotgroup = self.generate_plotgroup() #topo.plotting.plotgroup.PlotGroup(plot_list)
        new_plotgroup.plot_list = plot_list
	new_plotgroup.height_of_tallest_plot = self.plotgroup.height_of_tallest_plot
	new_plotgroup.initial_plot = self.plotgroup.initial_plot
	new_plotgroup.sheet_coords = self.plotgroup.sheet_coords
	new_plotgroup.integer_scaling = self.plotgroup.integer_scaling
	new_plotgroup.sizeconvertfn = self.plotgroup.sizeconvertfn
	new_plotgroup.normalize = self.plotgroup.normalize
	new_plotgroup.minimum_height_of_tallest_plot = self.plotgroup.minimum_height_of_tallest_plot
	new_plotgroup.time = topo.sim.time()

	self.plotgroup = new_plotgroup
 				
    
    ### JCALERT: have to re-implement it to regenerate the PlotGroup anytime.
    def set_normalize(self):
        """Function called by Widget when check-box clicked"""
	#self.plotgroup.normalize = self.normalize.get()
	self.plotgroup.update_plots(False)
	self.refresh()

    ### JCALERT: have to re-implement it to regenerate the PlotGroup anytime.
    def set_sheet_coords(self):
        """Function called by Widget when check-box clicked"""
	#self.plotgroup.sheetcoords = self.sheetcoords.get()
	self.plotgroup.update_plots(False)
	self.display_plots()
	self.refresh()

    ### JCALERT: have to re-implement it to regenerate the PlotGroup anytime.
    def set_integer_scaling(self):
        """Function called by Widget when check-box clicked"""
        if self.integer_scaling:#.get():
            self.plotgroup.sizeconvertfn = int
        else:
            self.plotgroup.sizeconvertfn = identity
	self.refresh()


    ### JABHACKALERT: This should be replaced with a PatternPresenter
    ### (from topo.commands.analysis), which will allow flexible
    ### support for making objects with different parameters in the
    ### different eyes, e.g. to test ocular dominance or disparity.
    def __setup_pattern_generators(self):
        """
        Make an instantiation of the current user patterns.

        Also does some other things...
        """
        self.__params_frame.set_parameters()

        disparity_flip=1

        for (gs_name,o_s_p) in self.generator_sheets_patterns.items():
            if o_s_p['editing']==True:
                
                newpattern = copy.deepcopy(self.__params_frame.parameterized_object)

                ###TRHACKALERT: Supports two-eye disparity model for RandomDotStereogram only,
                ###alternating direction for each eye
                if type(newpattern) == topo.patterns.rds.RandomDotStereogram:
                    newpattern.xdisparity=disparity_flip*newpattern.xdisparity/2
                    newpattern.ydisparity=disparity_flip*newpattern.ydisparity/2
                    disparity_flip=-1

                newpattern.bounds   = copy.deepcopy(o_s_p['generator_sheet'].bounds)
                newpattern.xdensity = o_s_p['generator_sheet'].xdensity
                newpattern.ydensity = o_s_p['generator_sheet'].ydensity

                o_s_p['pattern_generator'] = newpattern



