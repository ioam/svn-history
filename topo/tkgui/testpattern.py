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

### JABHACKALERT: Need to remove Back/Forward buttons, because they do not
### do what the user would expect.  

import copy
import Pmw

import topo.base.patterngenerator
import topo.base.sheetview

from topo.sheets.generatorsheet import GeneratorSheet
from topo.commands.basic import pattern_present

from topo.misc.keyedlist import KeyedList

import parametersframe
import plotgrouppanel
import topoconsole

from topo.plotting.plot import make_template_plot

from Tkinter import IntVar, StringVar, Checkbutton
from Tkinter import TOP, LEFT, RIGHT, BOTTOM, YES, N, S, E, W, X

# Default time to show in the Presentation duration box.
DEFAULT_PRESENTATION = '1.0'


class TestPattern(plotgrouppanel.PlotGroupPanel):
    def __init__(self,parent,console=None,padding=2,**config):

	super(TestPattern,self).__init__(parent,console,'Preview',**config)
        self.INITIAL_PLOT_HEIGHT = 100
        self.padding = padding

        ### Find the GeneratorSheets in the simulator, set up generator_sheet_patterns dictionary
        #
        # generator_sheets_patterns = 
        # {generator_sheet_name:  { 'generator_sheet': <gs_obj>,
        #                           'editing': True/False,
        #                           'pattern_generator': <pg_obj> }
        #                         }    
        self.generator_sheets_patterns = {}
        for (gen_sheet_name,gen_sheet) in topoconsole.active_sim().objects(GeneratorSheet).items():
            self.generator_sheets_patterns[gen_sheet_name] = {'generator_sheet': gen_sheet,
                                                              'editing': True,
                                                              'pattern_generator': None} 

        ### learning buttons
        #
        # CEBHACKALERT: I think this doesn't work at the moment
        self.learning = IntVar()
        self.learning.set(0)
        self.learning_button = Checkbutton(self,text='Network Learning',
                                      variable=self.learning)
        self.learning_button.pack(side=TOP)
        # buttonBox.add('Use for future learning',command = self.use_for_learning)


        ### 'Duration to present' box
        #
        self.present_length = Pmw.EntryField(self,
                labelpos = 'w',label_text = 'Duration to Present:',
                value = DEFAULT_PRESENTATION,validate = {'validator' : 'real'})
        self.present_length.pack(fill='x', expand=1, padx=10, pady=5)


        ### 'Present'/'reset to defaults' buttons  (i.e. re: patterns themselves)
        #
        buttonBox = Pmw.ButtonBox(self,orient = 'horizontal',padx=0,pady=0)
        buttonBox.pack(side=TOP)
        buttonBox.add('Present', command=self.present)
        buttonBox.add('Reset to defaults', command=self.reset_to_defaults)


        ### Menu of PatternGenerator types
        #
        # CEBHACKALERT: this way is just temporary while I reorganize these files.
        # Take the list of PatternGenerators from the first GeneratorSheet's
        # input_generator PatternGeneratorParameter for now.
        #
        # pattern_generators = {'Pattern': <PatternGenerator_obj>}
        for generator_sheet_name in self.generator_sheets_patterns.values():
            generator_sheet_params = generator_sheet_name['generator_sheet'].params()
            pattern_generators = generator_sheet_params['input_generator'].range()
            break
        
        self.pattern_generators = KeyedList()
        self.pattern_generators.update(pattern_generators)
        self.pattern_generators.sort()  # sorted so the pgs appear alphabetically
        ## END CEBHACKALERT
        

        # Set initial PatternGenerator to PatternGeneratorParameter.default
        # 
        assert isinstance(generator_sheet_params['input_generator'].default,topo.base.patterngenerator.PatternGenerator) #CEBHACKALERT: and if that isn't to be True, this file might need changing (check that)
        self.__current_pattern_generator = generator_sheet_params['input_generator'].default
        
        self.__current_pattern_generator_name = StringVar()
        # CEBHACKALERT: you can set the current pg from the name in a better way
        for (pg_name,pg) in self.pattern_generators.items():
            if pg==type(self.__current_pattern_generator):
                self.__current_pattern_generator_name.set(pg_name)
                self.__default_pattern_generator_name = pg_name #CEBHACKALERT: don't need to store this

        # PatternGenerator choice box
        self.pg_choice_box = Pmw.OptionMenu(self,
                                            command = self.__change_pattern_generator,
                                            labelpos = 'w',
                                            label_text = 'Pattern generator:',
                                            menubutton_textvariable = self.__current_pattern_generator_name,
                                            items = self.pattern_generators.keys())
        self.pg_choice_box.pack(side=TOP)


        ### The ParametersFrame
        #
        self.__params_frame = parametersframe.ParametersFrame(self)
        self.__params_frame.pack(side=TOP,expand=YES,fill=X)
        self.__params_frame.create_widgets(self.__current_pattern_generator)


        ### 'Edit patterns in' boxes
        #
        # CEBHACKALERT: don't want these boxes up so high on window, should be lower.
        # Also, boxes are in the wrong order (need to match the plots).
        self.__input_box = Pmw.RadioSelect(parent, labelpos = 'w',
                                command = self._input_change,label_text = 'Apply to pattern in:',
                                frame_borderwidth = 2,frame_relief = 'ridge',
                                selectmode = 'multiple')
        self.__input_box.pack(fill = 'x', padx = 5)

        CEBHACKALERT = copy.copy(self.generator_sheets_patterns.keys())
        CEBHACKALERT.reverse()
        for generator_sheet_name in CEBHACKALERT:
            self.__input_box.add(generator_sheet_name)
            self.__input_box.invoke(generator_sheet_name)
        

        self.__change_pattern_generator(self.__current_pattern_generator_name.get())
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


    def refresh(self):
        """
        Change the pattern generator objects as required

        Also call the parent class refresh.
        """
        self.__setup_pattern_generators()
        ### JCALERT : temporary hack to be changed, as well as the function special_generate_plotgroup
	self.plotgroup = self.special_generate_plotgroup()
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
	    self.plotgroup=self.special_generate_plotgroup()
	    self.refresh()


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
        self.__setup_pattern_generators()
        input_dict = dict([(name,d['pattern_generator'])
                           for (name,d) in self.generator_sheets_patterns.items()])
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


    ### JCALERT! That will have to be re-written properly, but works for the moment.
    ### it is an hack to bypass the generate_plotgroup in the plotgrouppanel superclass...
    ###
    ### JABHACKALERT: This does *NOT* seem to be working even for the moment -- e.g.
    ### the reduce button enlarges if pressed after one enlarge step and a switch
    ### to Sheet coordinates.  Presumably the problem is that a new PlotGroup is
    ### created each time, throwing away the state of important variables.
    def special_generate_plotgroup(self):
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
        return topo.plotting.plotgroup.PlotGroup(plot_list,self.normalize,
						 self.sheetcoords,self.integerscaling)
    
    ### JCALERT: have to re-implement it to regenerate the PlotGroup anytime.
    def toggle_normalize(self):
        """Function called by Widget when check-box clicked"""
        self.normalize = not self.normalize
	self.plotgroup.normalize = self.normalize
	self.refresh()


    ### JABHACKALERT! Ideally this would move out of tkgui/ altogether.
    ###
    ### JAB: It is not clear how this will need to be extended to support
    ### objects with different parameters in the different eyes, e.g. to
    ### test ocular dominance.
    def __setup_pattern_generators(self):
        """
        Make an instantiation of the current user patterns.

        Also does some other things...
        """

        # CEBHACKALERT: this method (still) sets bounds and density
        # every time the pattern's redrawn.
        # This method will change.

        self.__params_frame.set_obj_params()

        for (gs_name,o_s_p) in self.generator_sheets_patterns.items():
            if o_s_p['editing']==True:
                o_s_p['pattern_generator'] = self.__params_frame.topo_obj
                setattr(o_s_p['pattern_generator'],'bounds',copy.deepcopy(o_s_p['generator_sheet'].bounds))
                setattr(o_s_p['pattern_generator'],'xdensity', o_s_p['generator_sheet'].xdensity)
                setattr(o_s_p['pattern_generator'],'ydensity', o_s_p['generator_sheet'].ydensity)                
