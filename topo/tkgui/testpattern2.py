"""

$Id$
"""
__version__='$Revision$'


### JABHACKALERT: Need to remove Back/Forward buttons, because they do not
### do what the user would expect.  


# CEBALERT: taggedsliders refresh the display even when auto-refresh is off.

# CB changing pattern doesn't refresh plots even when autorefresh is on.


import copy
import Pmw

import topo

import topo.base.patterngenerator
import topo.base.sheetview
from topo.base.parameterclasses import BooleanParameter,Number

from topo.sheets.generatorsheet import GeneratorSheet
from topo.commands.basic import pattern_present
from topo.plotting.plotgroup import identity

from topo.misc.keyedlist import KeyedList

import parametersframe
from plotgrouppanel import XPGPanel

from topo.plotting.plot import make_template_plot

from Tkinter import IntVar, StringVar, Checkbutton
from Tkinter import TOP, LEFT, RIGHT, BOTTOM, YES, N, S, E, W, X,NO,NONE


from tkparameterizedobject import ButtonParameter

DEFAULT_PRESENTATION = '1.0'


from topo.plotting.plotgroup import XPlotGroup

class TestPatternPlotGroup(XPlotGroup):
    def __init__(self,**params):
        super(TestPatternPlotGroup,self).__init__(**params)

        

    


class TestPattern(XPGPanel):

    sheet_type = GeneratorSheet
    plotgroup_type = TestPatternPlotGroup

    learning = BooleanParameter(default=False,doc="""Whether to enable learning during presentation.""")
    duration = Number(default=1.0,doc="""How long to run the simulator when presenting.""")

    present = ButtonParameter(doc="""Present this pattern to the simulation.""")
    reset = ButtonParameter(doc="""Reset the parameters for this pattern back to their defaults.""")
    
    
    def __init__(self,console,master,label="Preview",**params):
	super(TestPattern,self).__init__(console,master,label,**params)
        self.auto_refresh=True


        # FIND GENERATOR SHEETS
        ###############################################################################################
        self.plotgroup.params()['sheet'].range=topo.sim.objects(GeneratorSheet).values()
        
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
        ###############################################################################################


        self.pack_param('learning')
        self.pack_param('duration')

        self.pack_param('present',on_change=self.present_pattern)
        self.pack_param('reset',on_change=self.reset_to_defaults)
        


        # LIST OF PATTERNGENERATORS
        ###############################################################################################
        ### Menu of PatternGenerator types
        # Take the list of PatternGenerators from the first
        # GeneratorSheet's input_generator PatternGeneratorParameter.
        # pattern_generators = {'Pattern': <PatternGenerator_obj>}
        for generator_sheet_name in self.generator_sheets_patterns.values():
            generator_sheet_params = generator_sheet_name['generator_sheet'].params()
            pattern_generators = generator_sheet_params['input_generator'].range()
            break
        
        self.pattern_generators = KeyedList()
        self.pattern_generators.update(pattern_generators)
        self.pattern_generators.sort()  # sorted so the pgs appear alphabetically

        self.__current_pattern_generator = GeneratorSheet.classparams()['input_generator'].default
        self.__current_pattern_generator_name = StringVar()

        for (pg_name,pg) in self.pattern_generators.items():
            if pg==type(self.__current_pattern_generator):
                self.__current_pattern_generator_name.set(pg_name)
                self.__default_pattern_generator_name = pg_name 


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
        # (remember to remove audiogen)
        ###############################################################################################


        # PARAMETERSFRAME
        ###############################################################################################
        # Because this window applies changes to an object immediately
        # (unlike ParametersFrame), the button to 'reset' is
        # 'Defaults'. 'Reset' would do nothing.
        self.__params_frame = parametersframe.ParametersFrame(self,buttons_to_remove=['Apply','Close','Reset'])
        self.__params_frame.create_widgets(self.__current_pattern_generator)
        self.__params_frame.pack(side=TOP,expand=YES,fill=X)
        ###############################################################################################
        

        # SELECT GENERATORSHEET BUTTONS
        ###############################################################################################
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
        ###############################################################################################
            

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
        self.update_plotgroup_variables()
        self.__setup_pattern_generators()
        super(TestPattern,self).refresh()



    # METHODS FOR BUTTONS
    ###############################################################################################
    def _input_change(self,button_name, checked):
        """
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
        Set the current PatternGenerator to the one selected and get the
        ParametersFrame to draw the relevant widgets
        """
        self.__current_pattern_generator = self.pattern_generators[pattern_generator_name]()
        self.__params_frame.create_widgets(self.__current_pattern_generator)
        if self.auto_refresh: 
	    self.refresh()

    def present_pattern(self):
        """
        Move the user created patterns into the GeneratorSheets, run for
        the specified length of time, then restore the original
        patterns.
        """
	topo.sim.state_push()
        self.__setup_pattern_generators()

        input_dict = dict([(name,d['pattern_generator'])
                           for (name,d) in self.generator_sheets_patterns.items()])
        
        pattern_present(input_dict,self.duration,
                        learning=self.learning,overwrite_previous=False)

        self.console.auto_refresh()
	topo.sim.state_pop()

    def reset_to_defaults(self):
        """
        Reset to default presentation length, no learning, and the original PatternGenerator.
        """
        self.present_length.setvalue(DEFAULT_PRESENTATION)
        #self.learning_button.deselect()
        self.pg_choice_box.invoke(self.__default_pattern_generator_name)
        if self.auto_refresh: self.refresh()

    ###############################################################################################


    def update_plotgroup_variables(self):
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

        self.plotgroup.plot_list = plot_list
	self.plotgroup.time = topo.sim.time()
 				
    

    ### JABHACKALERT: This should be replaced with a PatternPresenter
    ### (from topo.commands.analysis), which will allow flexible
    ### support for making objects with different parameters in the
    ### different eyes, e.g. to test ocular dominance or disparity.

    # (there was a) buttonBox.add('Use for future learning',command = self.use_for_learning)
    def __setup_pattern_generators(self):
        """
        Make an instantiation of the current user patterns.

        Also does some other things...
        """
        # CB: remember to replace disparity flip stuff.
        
        self.__params_frame.set_parameters()

        for (gs_name,o_s_p) in self.generator_sheets_patterns.items():
            if o_s_p['editing']==True:
                
                newpattern = copy.deepcopy(self.__params_frame.parameterized_object)

                newpattern.bounds   = copy.deepcopy(o_s_p['generator_sheet'].bounds)
                newpattern.xdensity = o_s_p['generator_sheet'].xdensity
                newpattern.ydensity = o_s_p['generator_sheet'].ydensity

                o_s_p['pattern_generator'] = newpattern



