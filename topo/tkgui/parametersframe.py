"""
ParametersFrame class.

$Id$
"""

    ### JABHACKALERT!  This should be made into part of a
    ### PatternGeneratorParameter widget.
    ### GeneratorSheet.input_generator would be declared as a
    ### PatternGeneratorParameter, and such a widget would allow the
    ### user to select a PatternGenerator from the known list.  The
    ### code for that should be done very generally, because we'll
    ### need to do something very similar for learning rules,
    ### activation functions, etc.  Even then, it should probably not
    ### be part of this class, because this class is for the
    ### parameters of one single TopoObject.  At the moment it has a
    ### selection box for choosing such an object, and also includes
    ### its parameters, which is a mess.
    # CEB: I'm working on this.

__version__='$Revision $'

from propertiesframe import PropertiesFrame
from Tkinter import Frame, TOP, LEFT, RIGHT, BOTTOM, YES, N,S,E,W,X
from topo.base.utils import eval_atof, class_parameters, keys_sorted_by_value
import topo

class ParametersFrame(Frame):
    """
    Frame for the Parameters of a TopoObject.

    Makes a PropertiesFrame containing all TopoObject's Parameters.
    """

    def __init__(self, parent=None,**config):
        """
        """
        self.__properties_frame = PropertiesFrame(parent,string_translator=eval_atof)
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


    # need to refresh things other than sliders - do this properly
    def refresh(self):
        """
        something like, this makes slider match tag or whatever
        """
        try: 
            for entry in self.__widgets.values():
                if entry[1].need_to_refresh_slider:
                    entry[1].set_slider_from_tag()
        except AttributeError:
            pass


    def refresh_widgets(self,topo_class):
        """
        Refresh the widgets.

        Any current widgets are first removed from the screen, then new widgets are
        added for all non-hidden Parameters of topo_class.

        Widgets for Parameters are added in order or Parameters' precedence.
        """

        # self.__widgets is
        # {parameter_name: (Tkinter.Message instance, widget)
                            # (name,Parameter) 
        for (s,c) in self.__widgets.values():
            s.grid_forget()
            c.grid_forget()

        # find class' Parameters
        parameters = class_parameters(topo_class)
        self.__widgets = self.__make_widgets(parameters)

        # sort Parameters by precedence (oops actually reverse of precedence!)
        parameter_precedences = {}
        for name,parameter in parameters:
            parameter_precedences[name] = parameter.precedence
        parameter_names = keys_sorted_by_value(parameter_precedences)

        # add widgets to control Parameters
        i = 0  # lose the i counting
        for parameter_name in parameter_names: 
            (s,c) = self.__widgets[parameter_name]
            s.grid(row=i,column=0,padx=self.__properties_frame.padding,
                   pady=self.__properties_frame.padding,sticky=E)
            c.grid(row=i,
                   column=1,
                   padx=self.__properties_frame.padding,
                   pady=self.__properties_frame.padding,
                   sticky=N+S+W+E)
            i = i + 1


    def __make_widgets(self,parameters):
        """

        """
        widget_dict = {}

        for (parameter_name, parameter) in parameters:

            if isinstance(parameter, topo.base.parameter.Number):
                try:
                    (low,high) = parameter.get_soft_bounds()
                    default = parameter.default
                    widget_dict[parameter_name] = self.__add_slider(parameter_name,str(low),str(high),str(default))
                except AttributeError:
                    # has no soft bounds
                    widget_dict[parameter_name] = self.__add_text_box(parameter_name,value)
                    
            # default to text entry    
            else:
                value = parameter.default                
                widget_dict[parameter_name] = self.__add_text_box(parameter_name,value)

        return widget_dict
                
            
    def __add_text_box(self,name,value):
        return self.__properties_frame.add_text_property(name,value)

    def __add_slider(self,name,min,max,init):
        return self.__properties_frame.add_tagged_slider_property(name,init,
                 min_value=min,max_value=max,width=30,string_format='%.6f')









