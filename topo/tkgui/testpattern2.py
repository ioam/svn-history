"""

$Id$
"""
__version__='$Revision$'


# CEB: simplification of testpattern.TestPattern.

## Needs to be upgraded to behave how we want, but should be simpler
## to do that from here than the original test pattern.

## Notes:
# * need to remove audigen pgs
# * there was: buttonBox.add('Use for future learning',command = self.use_for_learning)
# * missing disparity flip hack (though see JABHACKALERT below)
# * missing 'reset to defaults'

### JABHACKALERT: Should use PatternPresenter (from
### topo.commands.analysis), which will allow flexible support for
### making objects with different parameters in the different eyes,
### e.g. to test ocular dominance or disparity.



from Tkinter import Frame

import topo

from topo.base.sheetview import SheetView
from topo.base.parameterclasses import BooleanParameter,Number,ClassSelectorParameter,ObjectSelectorParameter
from topo.base.patterngenerator import PatternGenerator
from topo.sheets.generatorsheet import GeneratorSheet
from topo.commands.basic import pattern_present
from topo.misc.keyedlist import KeyedList
from topo.plotting.plot import make_template_plot
from topo.plotting.plotgroup import SheetPlotGroup

from parametersframe import XParametersFrame
from plotgrouppanel import XPGPanel
from tkparameterizedobject import ButtonParameter


DEFAULT_PRESENTATION = 1.0


class TestPatternPlotGroup(SheetPlotGroup):

    def __init__(self,sheets=None,**params):
        super(TestPatternPlotGroup,self).__init__(sheets=sheets,**params)
            
    def _plot_list(self):
        plot_list = []
        for sheet in self._sheets():
            plot_list.append(self._create_plot(sheet))

        return plot_list
        
    def _create_plot(self,sheet):
        new_view = SheetView((sheet.input_generator(),sheet.bounds),
                              sheet.name,sheet.precedence,topo.sim.time())        
        sheet.sheet_view_dict['Activity']=new_view
        channels = {'Strength':'Activity','Hue':None,'Confidence':None}

        ### JCALERT! it is not good to have to pass '' here... maybe a test in plot would be better
        p = make_template_plot(channels,sheet.sheet_view_dict,
                               sheet.xdensity,sheet.bounds,self.normalize,name='')
        return p
        




class TestPattern(XPGPanel):

    plotgroup_type = TestPatternPlotGroup

    edit_sheet = ObjectSelectorParameter()

    learning = BooleanParameter(default=False,doc="""Whether to enable learning during presentation.""")
    duration = Number(default=1.0,doc="""How long to run the simulator when presenting.""")

    present = ButtonParameter(doc="""Present this pattern to the simulation.""")

    pattern_generator = ClassSelectorParameter(class_=PatternGenerator, doc="""Type of pattern to present. Each type will have various parameters that can be changed.""")


    @staticmethod
    def valid_context():
        """Only open if GeneratorSheets are in the Simulation."""
        if topo.sim.objects(GeneratorSheet).items():
            return True
        else:
            return False


    def generate_plotgroup(self):
        # CB: could copy the sheets
        sheets = []
        for gen_sheet in topo.sim.objects(GeneratorSheet).values():
            gscopy = GeneratorSheet(
                name=gen_sheet.name,
                nominal_density=gen_sheet.nominal_density,
                nominal_bounds=gen_sheet.nominal_bounds)
            sheets.append(gscopy)

        return self.plotgroup_type(
            sheets=sheets)


    def __init__(self,console,master,label="Preview",**params):
	super(TestPattern,self).__init__(console,master,label,**params)

        self.auto_refresh = True

        # Remove plot_ & update_command
        self.plotcommand_frame.pack_forget()
        for name in ['update_command','Fwd','Back']:
            self.hide_param(name) 

        edit_sheet_param = self.get_parameter_object('edit_sheet')
        edit_sheet_param.Arange = self.plotgroup._sheets()


        self.pg_control_pane = Frame(self,bd=1,relief="sunken")
        self.pg_control_pane.pack(side="top",expand='yes',fill='x')
        
        self.params_frame = XParametersFrame(self.pg_control_pane,
                                             PO=self.pattern_generator,
                                             on_modify=self.conditional_refresh)

        self.params_frame.hide_param('Close')


        self.pack_param('edit_sheet',parent=self.pg_control_pane,on_modify=self.switch_sheet)
        self.pack_param('pattern_generator',parent=self.pg_control_pane,
                        on_modify=self.change_pattern_generator,
                        side="top")
        
        self.change_pattern_generator()

        
        present_frame = Frame(self)
        present_frame.pack(side='bottom')

        self.pack_param('learning',side='bottom',parent=present_frame)

        self.params_frame.pack(side='bottom',expand='yes',fill='x')
        
        self.pack_param('duration',parent=present_frame,
                        side="left")
        self.pack_param('present',parent=present_frame,on_change=self.present_pattern,
                        side="right")

        
    def switch_sheet(self):
        self.pattern_generator = self.edit_sheet.input_generator
        self.change_pattern_generator()


    def conditional_refresh(self):
        if self.auto_refresh:self.refresh()

        
    def change_pattern_generator(self):
        """
        Set the current PatternGenerator to the one selected and get the
        ParametersFrame to draw the relevant widgets
        """
        self.params_frame.create_widgets(self.pattern_generator)

        for sheet in self.plotgroup._sheets():
            if sheet==self.edit_sheet:
                sheet.set_input_generator(self.pattern_generator)
        
        self.conditional_refresh()


    def present_pattern(self):
        """
        Move the user created patterns into the GeneratorSheets, run for
        the specified length of time, then restore the original
        patterns.
        """
	topo.sim.state_push()

        input_dict = dict([(sheet.name,sheet.input_generator) for sheet in self.plotgroup._sheets()])
        
        pattern_present(input_dict,self.duration,
                        learning=self.learning,overwrite_previous=False)

        self.console.auto_refresh()
	topo.sim.state_pop()



    




    


