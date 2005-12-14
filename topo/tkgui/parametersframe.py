"""
ParametersFrame class.

$Id$
"""
__version__='$Revision$'

from propertiesframe import PropertiesFrame
from Tkinter import Frame, TOP, YES, N,S,E,W,X
from topo.base.utils import class_parameters, keys_sorted_by_value
import topo
import topo.base.parameter

# CEBHACKALERT: this file is still being reorganized

class ParametersFrame(Frame):
    """
    Frame for all non-hidden Parameters of a TopoObject class.

    Makes a PropertiesFrame containing all the specified class' Parameters.

    CEBHACKALERT: shouldn't this be associated with one class all the time it exists,
    rather than specifying the class of interest each time in create_widgets()?
    We'll see this when we do TestPattern, I guess.
    """

    def __init__(self, parent=None,**config):
        """
        """
        self.__properties_frame = PropertiesFrame(parent)
        Frame.__init__(self,parent,config)
        self.__widgets = {}
        self.__default_values = self.__properties_frame.get_values()
        self.__properties_frame.pack(side=TOP,expand=YES,fill=X)


    def get_values(self):
        """
        Return a dictionary of Parameter names:values.
        """
        return self.__properties_frame.get_values()


    def reset_to_defaults(self):
        """
        Reset the Parameters to their original values.
        """
        self.__properties_frame.set_values(self.__default_values)


    # CEBHACKALERT: it would be better if the TaggedSliders looked after themselves.
    def refresh(self):
        """
        """
        try: 
            for entry in self.__widgets.values():
                if entry[1].need_to_refresh_slider:
                    entry[1].set_slider_from_tag()
        except AttributeError:
            pass


    def create_widgets(self,topo_class):
        """
        Create widgets for all non-hidden Parameters of the given class.

        Any current widgets are first removed from the screen, then new widgets are
        added for all non-hidden Parameters of topo_class.

        Widgets for Parameters are added in order or Parameters' precedence.
        """
        for (s,c) in self.__widgets.values():
            s.grid_forget()
            c.grid_forget()

        parameters = class_parameters(topo_class)
        self.__widgets = self.__make_widgets(parameters)

        # sort Parameters by precedence (oops actually reverse of precedence!)
        parameter_precedences = {}
        for name,parameter in parameters:
            parameter_precedences[name] = parameter.precedence
        parameter_names = keys_sorted_by_value(parameter_precedences)

        # add widgets to control Parameters
        i = 0  # CEBHACKALERT: lose the i counting
        for parameter_name in parameter_names: 
            (s,c) = self.__widgets[parameter_name]
            s.grid(row=i,column=0,padx=self.__properties_frame.padding,
                   pady=self.__properties_frame.padding,sticky=E)
            c.grid(row=i,
                   column=1,
                   padx=self.__properties_frame.padding,
                   pady=self.__properties_frame.padding,
                   sticky=N+S+W+E)
            i += 1


    def __make_widgets(self,parameters):
        """
        Create a dictionary of widgets representing the Parameters.

        Each Parameter gets a suitable widget (e.g. a slider for a Number with
        soft_bounds). The default widget is a text box.

        parameters must be Parameter objects.
        """
        widget_dict = {}
        for (parameter_name, parameter) in parameters:

            # find the appropriate entry widget for the parameter...
            
            if isinstance(parameter, topo.base.parameter.Number):
                try:
                    low_bound,high_bound = parameter.get_soft_bounds()

                    # well it doesn't really have softbounds!
                    if low_bound==None or high_bound==None:
                        raise AttributeError
                    
                    # a Number with softbounds gets a slider
                    widget_dict[parameter_name] = self.__add_slider(parameter_name,
                                                                    low_bound,
                                                                    high_bound,
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









