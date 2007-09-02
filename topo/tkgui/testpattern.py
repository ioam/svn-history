"""
The Test Pattern window...

$Id$
"""
__version__='$Revision$'

## Notes:
# * need to remove audigen pgs
# * missing disparity flip hack (though see JABHACKALERT below)
# * values like pi are written over
# * need to sort the list of Pattern generators

## Needs to be upgraded to behave how we want:
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


class TestPatternPlotGroup(SheetPlotGroup):

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
        return make_template_plot(channels,sheet.sheet_view_dict,
                                  sheet.xdensity,sheet.bounds,self.normalize,name='')



class TestPattern(XPGPanel):

    plotgroup_type = TestPatternPlotGroup

    edit_sheet = ObjectSelectorParameter(doc="""Sheet for which to edit pattern properties.""")

    learning = BooleanParameter(default=False,doc="""Whether to enable learning during presentation.""")
    duration = Number(default=1.0,doc="""How long to run the simulator when presenting.""",
                      softbounds=(0.0,10.0))

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
        # CB: could copy the sheets instead (deleting connections etc)
        sheets = [GeneratorSheet(name=gs.name,nominal_bounds=gs.nominal_bounds,
                        nominal_density=gs.nominal_density) for gs in topo.sim.objects(GeneratorSheet).values()]
        return self.plotgroup_type(sheets=sheets)


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
                                             on_modify=self.conditional_update)

        self.params_frame.hide_param('Close')
        self.params_frame.hide_param('Defaults') # CB: see ALERT in ParameterizedObject.reset_params()
        # (Additionally, changing the pattern generator has the same
        # effect as pressing Defaults would have if it worked. In
        # fact, changes to the pattern generators probably ought to
        # persist.)

        self.pack_param('edit_sheet',parent=self.pg_control_pane,on_modify=self.switch_sheet)
        self.pack_param('pattern_generator',parent=self.pg_control_pane,
                        on_modify=self.change_pattern_generator,
                        side="top")
        
        present_frame = Frame(self)
        present_frame.pack(side='bottom')

        self.pack_param('learning',side='bottom',parent=present_frame)
        self.params_frame.pack(side='bottom',expand='yes',fill='x')
        self.pack_param('duration',parent=present_frame,side='left')
        self.pack_param('present',parent=present_frame,on_change=self.present_pattern,side="right")

    
    def switch_sheet(self):
        self.pattern_generator = self.edit_sheet.input_generator
        self.change_pattern_generator()

        
    def change_pattern_generator(self):
        """
        Set the current PatternGenerator to the one selected and get the
        ParametersFrame to draw the relevant widgets
        """
        self.params_frame.set_PO(self.pattern_generator)

        for sheet in self.plotgroup._sheets():
            if sheet==self.edit_sheet:
                sheet.set_input_generator(self.pattern_generator)
        
        self.conditional_refresh()

    def conditional_update(self):
        if self.auto_refresh: self.make_plots()

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
        
