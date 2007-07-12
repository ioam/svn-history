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

DEFAULT_PRESENTATION = 1.0


from topo.plotting.plotgroup import XPlotGroup

class TestPatternPlotGroup(XPlotGroup):
    def __init__(self,**params):
        super(TestPatternPlotGroup,self).__init__(**params)

        

from topo.plotting.plotgroup import RangedParameter


class TestPattern(XPGPanel):

    sheet_type = GeneratorSheet
    plotgroup_type = TestPatternPlotGroup

    learning = BooleanParameter(default=False,doc="""Whether to enable learning during presentation.""")
    duration = Number(default=1.0,doc="""How long to run the simulator when presenting.""")

    present = ButtonParameter(doc="""Present this pattern to the simulation.""")
    reset = ButtonParameter(doc="""Reset the parameters for this pattern back to their defaults.""")

    pattern_generator = RangedParameter(doc="""Type of pattern to present. Each type will have various parameters that can be changed.""")
    
    
    def __init__(self,console,master,label="Preview",**params):
	super(TestPattern,self).__init__(console,master,label,**params)
        self.auto_refresh=True

        #self.plotgroup.params()['sheet'].range=topo.sim.objects(GeneratorSheet).values()


        gsig = GeneratorSheet.classparams()['input_generator']

        pgparam = self.params()['pattern_generator']
        pgparam.range = [pg() for pg in gsig.range().values()]
        self.pattern_generator = gsig.default()
        #pgparam.default = GeneratorSheet.classparams()['input_generator'].default        
        self.pack_param('pattern_generator',on_change=self.change_pattern_generator)


        # Because this window applies changes to an object immediately
        # (unlike ParametersFrame), the button to 'reset' is
        # 'Defaults'. 'Reset' would do nothing.
        self.params_frame = parametersframe.ParametersFrame(self,buttons_to_remove=['Apply','Close','Reset'])


        self.params_frame.create_widgets(self.pattern_generator) 
        self.params_frame.pack(side=TOP,expand=YES,fill=X)


        ### Find generator sheets        
        self.generator_sheets_patterns = dict.fromkeys(topo.sim.objects(GeneratorSheet),None)



        self.pack_param('learning')
        self.pack_param('duration')

        self.pack_param('present',on_change=self.present_pattern)
        self.pack_param('reset',on_change=self.reset_to_defaults)
        
        
        # CB: remember
        # - to remove audiogen
        # - editing 'pattern_generator': None} 


        

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
        #self.generator_sheets_patterns[button_name]['editing'] = checked

        #if not self.generator_sheets_patterns[button_name]['editing']:
        #    self.generator_sheets_patterns[button_name]['pattern_generator'] = copy.copy(self.__current_pattern_generator)
        #else:
        self.__setup_pattern_generators()
        if self.auto_refresh:self.refresh()
        
    def change_pattern_generator(self):
        """
        Set the current PatternGenerator to the one selected and get the
        ParametersFrame to draw the relevant widgets
        """
        if self.pattern_generator is not None: self.params_frame.create_widgets(self.pattern_generator) 
        if self.auto_refresh: self.refresh()

    def present_pattern(self):
        """
        Move the user created patterns into the GeneratorSheets, run for
        the specified length of time, then restore the original
        patterns.
        """
	topo.sim.state_push()
        self.__setup_pattern_generators()

        input_dict = dict([(name,pg)
                           for name,pg in self.generator_sheets_patterns.items()])
        
        pattern_present(input_dict,self.duration,
                        learning=self.learning,overwrite_previous=False)

        self.console.auto_refresh()
	topo.sim.state_pop()

    def reset_to_defaults(self):
        """
        Reset to default presentation length, no learning, and the original PatternGenerator.
        """
        self.duration=DEFAULT_PRESENTATION
        #self.learning_button.deselect()
        #self.pg_choice_box.invoke(self.__default_pattern_generator_name)
        if self.auto_refresh: self.refresh()

    ###############################################################################################


    def update_plotgroup_variables(self):
        plot_list = []       
        for sheetname,pg in self.generator_sheets_patterns.items():
            view_dict = {}
            # xdensity and ydensity are the same for the pattern_generator
            # because they were set from a Sheet xdensity and ydensity,
            # which are guaranteed to be the same
	    density = pg.xdensity
            
	    view_dict[sheetname] = topo.base.sheetview.SheetView((pg(),pg.bounds),src_name=sheetname)
	    channels = {'Strength':sheetname,'Hue':None,'Confidence':None}
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
        
        self.params_frame.set_parameters()

        for sheetname in self.generator_sheets_patterns:
            #if o_s_p['editing']==True:
                
            newpattern = copy.deepcopy(self.params_frame.parameterized_object)

            sheet = topo.sim[sheetname]
            
            newpattern.bounds   = copy.deepcopy(sheet.bounds)
            newpattern.xdensity = sheet.xdensity
            newpattern.ydensity = sheet.ydensity

            self.generator_sheets_patterns[sheetname] = newpattern



