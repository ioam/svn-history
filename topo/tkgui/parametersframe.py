"""
ParametersFrame class.

$Id$
"""
__version__='$Revision$'

from propertiesframe import PropertiesFrame
from Tkinter import Frame, TOP, YES, N,S,E,W,X
from topo.base.utils import keys_sorted_by_value
import topo
import topo.base.parameter
from topo.base.topoobject import class_parameters

import Pmw
# CEBHACKALERT: this file is still being reorganized


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

    def __init__(self, parent=None,**config):
        """
        """
        self.__properties_frame = PropertiesFrame(parent)
        Frame.__init__(self,parent,config)
        self.__widgets = {}
        self.__properties_frame.pack(side=TOP,expand=YES,fill=X)

        self.__help_balloon = Pmw.Balloon(parent)


    def get_values(self):
        """
        Return a dictionary of Parameter names:values.
        """
        return self.__properties_frame.get_values()


    # CEBHACKALERT: it would be better if the TaggedSliders looked after themselves.
    def refresh(self):
        """
        """
        try: 
            for (msg,widget) in self.__widgets.values():
                widget.set_slider_from_tag()
        except AttributeError:
            pass


    def create_widgets(self, topo_class):
        """
        Create widgets for all non-hidden Parameters of the given class.

        Any current widgets are first removed from the screen, then new widgets are
        added for all non-hidden Parameters of topo_class.

        Widgets for Parameters are added in order or Parameters' precedence.
        """
        for (label,widget) in self.__widgets.values():
            label.grid_forget()
            widget.grid_forget()

        parameters = class_parameters(topo_class)
        self.__widgets = self.__make_widgets(parameters)

        # sort Parameters by precedence (oops actually reverse of precedence!)
        parameter_precedences = {}
        for name,parameter in parameters.items():
            parameter_precedences[name] = parameter.precedence

        sorted_parameter_names = keys_sorted_by_value(parameter_precedences)

        # add widgets to control Parameters
        rows = range(len(sorted_parameter_names))
        for (row,parameter_name) in zip(rows,sorted_parameter_names): 
            (label,widget) = self.__widgets[parameter_name]
            help_text = parameters[parameter_name].__doc__

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
            

    def __make_widgets(self,parameters):
        """
        Create a dictionary of widgets representing the Parameters.

        Each Parameter gets a suitable widget (e.g. a slider for a Number with
        soft_bounds). The default widget is a text box.

        parameters must be Parameter objects.
        """
        widget_dict = {}
        for (parameter_name, parameter) in parameters.items():

            # find the appropriate entry widget for the parameter...
            
            if isinstance(parameter, topo.base.parameter.Number):
                try:
                    low_bound,high_bound = parameter.get_soft_bounds()

                    # well it doesn't really have softbounds!
                    if low_bound==None or high_bound==None or low_bound==high_bound:
                        raise AttributeError
                    
                    # a Number with softbounds gets a slider
                    widget_dict[parameter_name] = self.__add_slider(parameter_name,
                                                                    str(low_bound),
                                                                    str(high_bound),
                                                                    parameter.default)
                except AttributeError:
                    # a Number with no softbounds gets a textbox
                    widget_dict[parameter_name] = self.__properties_frame.add_text_property(
                        parameter_name,parameter.default,width=7)
                    
            elif isinstance(parameter, topo.base.parameter.Enumeration):
                # an Enumeration gets a ComboBox
                items = parameter.available
                widget_dict[parameter_name] = self.__properties_frame.add_combobox_property(
                    parameter_name,parameter.default,items)

            elif isinstance(parameter, topo.base.parameter.PackageParameter):
                items = parameter.range().keys()
                widget_dict[parameter_name] = self.__properties_frame.add_combobox_property(
                    parameter_name,parameter.get_default_class_name(),items)

            else:
                # everything else gets a textbox   
                widget_dict[parameter_name] = self.__properties_frame.add_text_property(
                    parameter_name,parameter.default)
        return widget_dict
                

    def __add_slider(self,name,min,max,init):
        """
        Call the propertiesframe's add_tagged_slider_property(), but with
        a particular width and string format.
        """
        return self.__properties_frame.add_tagged_slider_property(name,init,
                 min_value=min,max_value=max,width=30,string_format='%.6f')









