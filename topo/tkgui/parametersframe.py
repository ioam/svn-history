"""
ParametersFrame class.

$Id$
"""
__version__='$Revision$'

from propertiesframe import PropertiesFrame
from Tkinter import Frame, TOP, YES, N,S,E,W,X
import topo.base.utils
from topo.base.utils import keys_sorted_by_value
import topo
import topo.base.parameter
#from topo.base.topoobject import class_parameters

import Pmw
# CEBHACKALERT: this file is still being reorganized; there are still
# temporary methods.


# CEBHACKALERT: there used to be a 'reset_to_defaults' method, which
# didn't work. When Parameters can be set and then maintained between
# classes (e.g. for PatternGenerators), reset_to_defaults() should be
# re-implemented so that Parameters can be returned to default values
# for the current class.
# To maintain values of Parameters between classes, the object using
# the ParametersFrame will need to do something like pass
# ParametersFrame a dictionary of {parameter:value} pairs, which
# ParametersFrame should be able to use selectively (i.e. use if
# relevant to the current class but ignore otherwise).


class ParametersFrame(Frame):
    """
    Frame for all non-hidden Parameters of a TopoObject class.


    When asked to create wigets, ... makes a PropertiesFrame containing all the specified class' Parameters.
    """

    def __init__(self, parent=None, topo_obj=None, **config):
        """
        """
        self.__properties_frame = PropertiesFrame(parent)
        Frame.__init__(self,parent,config)
        self.__properties_frame.pack(side=TOP,expand=YES,fill=X)

        # CEBHACKALERT: these buttons should be stacked on the window or
        # something, but I don't know how to do that.
        
        # buttons for setting/(restoring) class Parameter values.
        #pattern_buttonBox = Pmw.ButtonBox(self,orient = 'horizontal',padx=0,pady=0)
        #pattern_buttonBox.add('Install as class defaults',
        #                      command=self.install_as_class_defaults)
        #pattern_buttonBox.add('Revert to class defaults',
        #                      command=self.revert_to_class_defaults)

        # CEBHACKALERT: need this to revert to defaults in the file...
        #pattern_buttonBox.add('Restore class defaults',
        #                      command=self.restore_class_defaults)

        #pattern_buttonBox.pack(side=TOP)


        self.__help_balloon = Pmw.Balloon(parent)
        
        self.widgets = {}
        self.topo_obj = topo_obj
        self.visible_parameters = None


    def install_as_class_defaults(self):
        """
        """
        # go through, get parameters, set them on the classobj
        t = type(self.topo_obj)
        
        for (name,parameter) in self.visible_parameters.items():
            w = self.widgets[name][1]
            setattr(t,name,w.get_value())


    # CEBHACKALERT
    def revert_to_class_defaults(self):
        pass
        

    # CEBHACKALERT
    def restore_class_defaults(self):
        """
        """
        pass


    def set_obj_params(self):
        """
        """
        # go through, get parameters, set them on the topo_obj
        parameters_to_modify = [ (name,parameter)
                                 for (name,parameter)
                                 in self.visible_parameters.items()
                                 if not type(parameter)==topo.base.parameter.Constant]
        
        for (name,parameter) in parameters_to_modify:
            w = self.widgets[name][1]
            # print "[", self.topo_obj,name,w.get_value()  ,"]" 
            setattr(self.topo_obj,name,w.get_value())

        
       

    def create_widgets(self, topo_obj):
        """
        Create widgets for all non-hidden Parameters of the current topo_obj.

        Any current widgets are first removed from the dictionary of widgets, then
        new ones are added for all non-hidden Parameters of topo_class.

        Widgets are added in order of the Parameters' precedences.
        """
        self.topo_obj=topo_obj
        
        for (label,widget) in self.widgets.values():
            label.grid_forget()
            widget.grid_forget()

        # find visible parameters for topo_obj
        # {name:parameter}
        self.visible_parameters = dict([(parameter_name,parameter)
                                        for (parameter_name,parameter)
                                        in self.topo_obj.get_paramobj_dict().items()
                                        if not parameter.hidden])

        # create the widgets
        self.widgets = self.__create_widget_dict()
                      
        # sort Parameters by precedence (oops actually reverse of precedence!)
        parameter_precedences = {}
        for name,parameter in self.visible_parameters.items():
            parameter_precedences[name] = parameter.precedence
        sorted_parameter_names = keys_sorted_by_value(parameter_precedences)

        # add widgets to control Parameters
        rows = range(len(sorted_parameter_names))
        for (row,parameter_name) in zip(rows,sorted_parameter_names): 
            (label,widget) = self.widgets[parameter_name]
            help_text = self.visible_parameters[parameter_name].__doc__

            label.grid(row=row,
                       column=0,
                       padx=self.__properties_frame.padding,
                       pady=self.__properties_frame.padding,
                       sticky=E)

            widget.grid(row=row,
                        column=1,
                        padx=self.__properties_frame.padding,
                        pady=self.__properties_frame.padding,
                        sticky=N+S+W+E)
            
            self.__help_balloon.bind(label, help_text)
            

    def __create_widget_dict(self):
        """
        Create a dictionary of widgets representing the Parameters.

        Each Parameter gets a suitable widget (e.g. a slider for a Number with
        soft_bounds). The default widget is a text box.

        parameters must be Parameter objects.
        """

        # CEBHACKALERT: this will change (to a dictionary
        # mapping parameter types to methods)
        
        widget_dict = {}
        for (parameter_name, parameter) in self.visible_parameters.items():

            # find the appropriate entry widget for the parameter...

            # CEBHACKALERT: not going to help if it's the class and you want to
            # make this for the first time
            if isinstance(parameter, topo.base.parameter.Constant):
                
                widget_dict[parameter_name] = self.__properties_frame.add_text_property(
                    parameter_name,
                    value = getattr(self.topo_obj,parameter_name),
                    readonly = True)
            
            elif isinstance(parameter, topo.base.parameter.Number):
                try:
                    low_bound,high_bound = parameter.get_soft_bounds()

                    # well it doesn't really have softbounds!
                    if low_bound==None or high_bound==None or low_bound==high_bound:
                        raise AttributeError
                    
                    # a Number with softbounds gets a slider
                    # CEBHACKALERT: revert to previous behaviour for DynamicNumber
                    # until we figure out how to do it properly.
                    if isinstance(parameter, topo.base.parameter.DynamicNumber):
                        v = parameter.default
                    else:
                        v = getattr(self.topo_obj,parameter_name)
                        
                    widget_dict[parameter_name] = self.__add_slider(
                        parameter_name,
                        str(low_bound),
                        str(high_bound),
                        v)

                except AttributeError:
                    # a Number with no softbounds gets a textbox that can translate
                    # strings to floats
                    widget_dict[parameter_name] = self.__properties_frame.add_text_property(
                        parameter_name,
                        value = getattr(self.topo_obj,parameter_name),
                        translator = topo.base.utils.eval_atof)
                    
            elif isinstance(parameter, topo.base.parameter.Enumeration):
                # an Enumeration gets a ComboBox
                # CEBHACKALERT: only string Enumerations make sense at the moment.
                widget_dict[parameter_name] = self.__properties_frame.add_combobox_property(
                    parameter_name,
                    value = getattr(self.topo_obj,parameter_name),
                    items = parameter.available)

            elif isinstance(parameter, topo.base.parameter.PackageParameter):
                widget_dict[parameter_name] = self.__properties_frame.add_combobox_property(
                    parameter_name,
                    value = parameter.get_default_class_name(), #.getattr(self.topo_obj,parameter_name),
                    items = parameter.range().keys(),
                    translator = parameter.get_from_key)
            elif isinstance(parameter, topo.base.parameter.BooleanParameter):
                widget_dict[parameter_name] = self.__properties_frame.add_checkbutton_property(
                    parameter_name,
                    value = getattr(self.topo_obj,parameter_name))


            else:
                # everything else gets a textbox   
                widget_dict[parameter_name] = self.__properties_frame.add_text_property(
                    parameter_name,
                    value = getattr(self.topo_obj,parameter_name))
        return widget_dict


    def __add_slider(self,name,min_value,max_value,initial_value):
        """
        Call the propertiesframe's add_tagged_slider_property(), but with
        a particular width, string format, and translator.
        """
        return self.__properties_frame.add_tagged_slider_property(
            name,
            initial_value,
            min_value=min_value,
            max_value=max_value,
            width=30,
            string_format='%.6f',
            translator=topo.base.utils.eval_atof)  # sliders are always numeric









