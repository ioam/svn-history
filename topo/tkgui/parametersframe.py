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
import Pmw


# CEBHACKALERT: this file is still being reorganized; there are still
# temporary methods.

# CEBHACKALERT: doesn't work for TopoObject class.


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

    def __init__(self, parent=None, **config):
        """
        """
        Frame.__init__(self,parent,config)
        self.__properties_frame = PropertiesFrame(parent)
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

        self.topo_obj = None

        self.__help_balloon = Pmw.Balloon(parent)
        
        self.__widgets = {} # should it be none?
        self.__visible_parameters = {}

        # The dictionary of parameter_type:property_to_add pairs.
        self.__parameter_property = {
            topo.base.parameter.Constant:         self.__add_readonly_text_property,
            topo.base.parameter.Number:           self.__add_numeric_property,
            topo.base.parameter.Enumeration:      self.__add_enumeration_property,
            topo.base.parameter.PackageParameter: self.__add_package_property,
            topo.base.parameter.BooleanParameter: self.__add_boolean_property}



##     def install_as_class_defaults(self):
##         """
##         """
##         assert self.topo_obj!=None, "ParametersFrame must be associated with a TopoObj()."
        
##         # go through, get parameters, set them on the classobj
##         t = type(self.topo_obj)
        
##         for (name,parameter) in self.__visible_parameters.items():
##             w = self.__widgets[name][1]
##             setattr(t,name,w.get_value())


##     # CEBHACKALERT
##     def revert_to_class_defaults(self):
##         pass
        

##     # CEBHACKALERT
##     def restore_class_defaults(self):
##         """
##         """
##         pass


    # CEBHACKALERT: rename to set_object_parameters, probably.
    def set_obj_params(self):
        """
        For all non-Constant Parameters of the currently set TopoObject(),
        set the values of the Parameters to those specified by the widgets.
        """
        assert self.topo_obj!=None, "ParametersFrame must be associated with a TopoObj()."
        
        parameters_to_modify = [ (name,parameter)
                                 for (name,parameter)
                                 in self.__visible_parameters.items()
                                 if not type(parameter)==topo.base.parameter.Constant]
        
        for (name,parameter) in parameters_to_modify:
            w = self.__widgets[name][1]  # [0] is label (Message), [1] is widget
            setattr(self.topo_obj,name,w.get_value())

        
    def create_widgets(self, topo_obj):
        """
        Create widgets for all non-hidden Parameters of topo_obj and add them
        to the screen.

        Each Parameter gets a suitable widget (e.g. a slider for a Number with
        soft_bounds). The default widget is a text box.

        parameters must be Parameter objects.

        Widgets are added in order of the Parameters' precedences.
        """
        self.topo_obj=topo_obj

        # wipe old labels and widgets from screen
        for (label,widget) in self.__widgets.values():
            label.grid_forget()
            widget.grid_forget()

        # find visible parameters for topo_obj
        self.__visible_parameters = dict([(parameter_name,parameter)
                                        for (parameter_name,parameter)
                                        in self.topo_obj.get_paramobj_dict().items()
                                        if not parameter.hidden])

        # create the widgets
        self.__widgets = {}
        for (parameter_name, parameter) in self.__visible_parameters.items():
            self.__add_property_for_parameter(parameter_name,parameter)

        # sort Parameters by precedence (oops actually reverse of precedence!)
        parameter_precedences = {}
        for name,parameter in self.__visible_parameters.items():
            parameter_precedences[name] = parameter.precedence
        sorted_parameter_names = keys_sorted_by_value(parameter_precedences)

        # add widgets to screen
        rows = range(len(sorted_parameter_names))
        for (row,parameter_name) in zip(rows,sorted_parameter_names): 
            (label,widget) = self.__widgets[parameter_name]
            help_text = self.__visible_parameters[parameter_name].__doc__

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


    def __add_property_for_parameter(self,parameter_name,parameter):
        """
        Find the correct property type for the given parameter.

        If the parameter's type is not listed in
        self.__parameter_property, the class hierarchy is traversed until
        a match is found. If no match is found, the Parameter just gets a
        textbox. 
        """
        for c in topo.base.parameter.classlist(type(parameter))[::-1]:
            if self.__parameter_property.has_key(c):
                # find the right method...
                property_to_add = self.__parameter_property[c]
                # ...then call it
                property_to_add(parameter_name,parameter)
                return
        # no match: use text box
        self.__add_text_property(parameter_name,parameter)
            

    # CEBHACKALERT: don't need to pass parameter. See HACKALERT below
    # about DynamicNumber
    def __add_text_property(self,parameter_name,parameter):
        """
        Add a text property to the properties_frame.
        """
        self.__widgets[parameter_name] = self.__properties_frame.add_text_property(
            parameter_name,
            value = getattr(self.topo_obj,parameter_name))

    def __add_readonly_text_property(self,parameter_name,parameter):
        """
        Add a readonly text property to the properties_frame.
        """
        self.__widgets[parameter_name] = self.__properties_frame.add_text_property(
            parameter_name,
            value = getattr(self.topo_obj,parameter_name),
            readonly = True)

    def __add_numeric_property(self,parameter_name,parameter):
        """
        Add a numeric property to the properties_frame.

        If the parameter has distinct low and high softbounds, a tagged_slider
        property is added. Otherwise, just a textbox is added (with
        a translator for string to float).
        """
        try:
            low_bound,high_bound = parameter.get_soft_bounds()

            if low_bound==None or high_bound==None or low_bound==high_bound:
                raise AttributeError # i.e. there aren't really softbounds

            # CEBHACKALERT: revert to previous behaviour for DynamicNumber
            # until we figure out how to do it properly.
            if isinstance(parameter, topo.base.parameter.DynamicNumber):
                v = parameter.default
            else:
                v = getattr(self.topo_obj,parameter_name)

            self.__widgets[parameter_name] = self.__properties_frame.add_tagged_slider_property(
                parameter_name,
                v,
                min_value = str(low_bound),
                max_value = str(high_bound),
                width = 30,
                string_format = '%.6f',
                translator = topo.base.utils.eval_atof)

        except AttributeError:
            self.__widgets[parameter_name] = self.__properties_frame.add_text_property(
                parameter_name,
                value = getattr(self.topo_obj,parameter_name),
                translator = topo.base.utils.eval_atof)

    def __add_enumeration_property(self,parameter_name,parameter):
        """
        Add an enumeration property to the properties_frame by representing
        it with a ComboBox.
        """
        # an Enumeration gets a ComboBox
        # CEBHACKALERT: only string Enumerations work at the moment.
        self.__widgets[parameter_name] = self.__properties_frame.add_combobox_property(
                    parameter_name,
                    value = getattr(self.topo_obj,parameter_name),
                    scrolledlist_items = parameter.available)

    def __add_package_property(self,parameter_name,parameter):
        """
        Add a package property to the properties_frame by representing it
        with a ComboBox.
        """
        self.__widgets[parameter_name] = self.__properties_frame.add_combobox_property(
                    parameter_name,
                    value = parameter.get_default_class_name(), #.getattr(self.topo_obj,parameter_name),
                    scrolledlist_items = parameter.range().keys(),
                    translator = parameter.get_from_key)

    def __add_boolean_property(self,parameter_name,parameter):
        """
        Add a boolean property to the properties_frame by representing it with a
        Checkbutton.
        """
        self.__widgets[parameter_name] = self.__properties_frame.add_checkbutton_property(
                    parameter_name,
                    value = getattr(self.topo_obj,parameter_name))













