"""
ParametersFrame class.

$Id$
"""
__version__='$Revision$'

from propertiesframe import PropertiesFrame
from Tkinter import Frame, Button, RIGHT, TOP, BOTH, BOTTOM, END, YES, N,S,E,W,X, Menu, Toplevel, Label
import topo.base.utils
from topo.base.utils import keys_sorted_by_value, dict_translator, string_int_translator, string_bb_translator
import topo
import topo.base.parameterclasses
import Pmw

import topo.base.parameterizedobject

# CEBHACKALERT: this file is still being reorganized; there are still
# temporary methods.

# CEBHACKALERT: doesn't work for ParameterizedObject class.

# CEBHACKALERT: there used to be a 'reset_to_defaults' method, which
# didn't work. When Parameters can be set and then maintained between
# classes (e.g. for PatternGenerators), reset_to_defaults() should be
# re-implemented so that Parameters can be returned to default values
# for the current class.



class ParametersFrame(Frame):
    """
    Frame for all non-hidden Parameters of a ParameterizedObject class.


    When asked to create wigets, ... makes a PropertiesFrame containing all the specified class' Parameters.
    """

    def __init__(self, parent=None, **config):
        """
        """
        Frame.__init__(self,parent,config)
        self.__properties_frame = PropertiesFrame(parent)
        self.__properties_frame.pack(side=TOP,expand=YES,fill=BOTH)

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

        self.option_add("*Menu.tearOff", "0") 
        self.menu = Menu(self)
        self.menu.insert_command(END, label = 'Properties', command = lambda: 
            self.show_parameter_properties(self.parameters_properties))

        self.__help_balloon = Pmw.Balloon(parent)
        
        self.__widgets = {} # should it be none?
        self.__visible_parameters = {}

        # The dictionary of class_type: property_to_add pairs.
        self.__class_property = {
            int:                                  self.__add_int_property,
            topo.base.boundingregion.BoundingBox: self.__add_bounding_box_property}

        # The dictionary of parameter_type:property_to_add pairs.
        self.__parameter_property = {
            topo.base.parameterclasses.Number:           self.__add_numeric_property,
            topo.base.parameterclasses.Enumeration:      self.__add_enumeration_property,
            topo.base.parameterclasses.BooleanParameter: self.__add_boolean_property,
            topo.base.parameterclasses.ClassSelectorParameter: self.__add_class_selector_property}



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

    def set_class_parameters(self) :
        assert self.topo_class != None, ("ParameterFrame must be associated with a Class, " + 
            "to set its parameters")
        for (name) in self.__visible_parameters :
            w = self.__widgets[name][1]
            setattr(self.topo_class, name, w.get_value())

    # CEBHACKALERT: rename to set_object_parameters, probably.
    def set_obj_params(self):
        """
        For all non-Constant Parameters of the currently set ParameterizedObject(),
        set the values of the Parameters to those specified by the widgets.

        Only sets the value on the object if the value in the widget is
        different from the one in the object. This prevents a local copy
        of a variable being made into a ParameterizedObject just because the ParameterizedObject
        is opened in the model editor.
        """
        assert self.topo_obj!=None, "ParametersFrame must be associated with a TopoObj()."
        parameters_to_modify = [ (name,parameter)
                                 for (name,parameter)
                                 in self.__visible_parameters.items()
                                 if not parameter.constant==True]

        for (name,parameter) in parameters_to_modify:
            w = self.__widgets[name][1]  # [0] is label (Message), [1] is widget

            if w.get_value()!=getattr(self.topo_obj,name):
                setattr(self.topo_obj,name,w.get_value())


    def create_class_widgets(self, topo_class = None, translator_dictionary = {}, topo_object = None) :
        """
        Allows the Constant parameters of a class to be changed.

        ALALERT First attempt solution that will probably need strong revision. 
        """
        self.translator_dictionary = translator_dictionary

        # wipe old labels and widgets from screen
        for (label,widget) in self.__widgets.values():
            label.grid_forget()
            widget.grid_forget()

        if not(topo_object == None) :
            self.topo_obj = topo_object
            self.topo_class = topo_object.__class__

        elif not(topo_class == None) :
            self.topo_obj = topo_class()
            self.topo_class = topo_class

        else : # No object or class to create widgets of.
            return

        # find constant fields from topo_obj, for topo_class
        self.__visible_parameters = list(parameter_name
                                    for (parameter_name,parameter)
                                    in self.topo_obj.params().items()
                                    if parameter.constant == True
                                    and not(parameter.hidden))    
 
        # create the widgets
        self.__widgets = {}
        row = 0
        for parameter_name in self.__visible_parameters :
            self.__add_property_for_class(parameter_name)
            (label,widget) = self.__widgets[parameter_name]
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
            row += 1

    def create_widgets(self, topo_obj, translator_dictionary = {}):
        """
        topo.base.parameterclasses.Constant:
        Create widgets for all non-hidden Parameters of topo_obj and add them
        to the screen.

        Each Parameter gets a suitable widget (e.g. a slider for a Number with
        soft_bounds). The default widget is a text box.

        parameters must be Parameter objects.

        Widgets are added in order of the Parameters' precedences.

        If a dictionary is passed in when create_widgets is called __add_class_selector_property
        will attempt to get dictionary[parameter_name]. It expects these entries to be lists of 
        relevant objects to cover the selectable classes. It updates the lists and it can be 
        retrieved from self.translator_dictionary when set_obj_params is called and used on 
        subsequent uses.
        """
        self.topo_obj=topo_obj
        self.translator_dictionary = translator_dictionary
        self.object_dictionary = {}
        # wipe old labels and widgets from screen
        for (label,widget) in self.__widgets.values():
            label.grid_forget()
            widget.grid_forget()

        # find visible parameters for topo_obj
        self.__visible_parameters = dict([(parameter_name,parameter)
                                        for (parameter_name,parameter)
                                        in self.topo_obj.params().items()
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
        if parameter.constant==True:
            self.__add_readonly_text_property(parameter_name,parameter)
        else:
            for c in topo.base.parameterizedobject.classlist(type(parameter))[::-1]:
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
    def __add_text_property(self,parameter_name,parameter, translator = None):
        """
        Add a text property to the properties_frame.
        """
        attr = getattr(self.topo_obj,parameter_name)
        str_attr = str(attr)
        if not(translator == None) or (attr == str_attr) :
            value = attr
        else :
            translator = lambda in_string: dict_translator(in_string, translator_dictionary = {str_attr:attr})
            value = str_attr
        self.__widgets[parameter_name] = self.__properties_frame.add_text_property(
            parameter_name,
            translator = translator,
            value = value)

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

            #CEBHACKALERT: but one is ok - change this
            if low_bound==None or high_bound==None or low_bound==high_bound:
                raise AttributeError # i.e. there aren't really softbounds

            # CEBHACKALERT: revert to previous behaviour for DynamicNumber
            # until we figure out how to do it properly.
            if isinstance(parameter, topo.base.parameterclasses.DynamicNumber):
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

    def __add_class_selector_property(self,parameter_name,parameter):
        """
        Add a package property to the properties_frame by representing it
        with a ComboBox.
        """
        # get the current value of this field
        attr = getattr(self.topo_obj, parameter_name)
        translator_dictionary = {}
        self.object_dictionary[parameter_name] = {}
        value = ''
        # for each of the classes that this selector can select between loop through
        # and find if there is a suitable object already instantiated in either the
        # current value or in the dictionary passed in.
        for key in parameter.range().keys() :
            parameter_entry = parameter.range()[key]
            if parameter_entry == attr.__class__ :
                translator_dictionary[key] = attr
                self.object_dictionary[parameter_name][key] = attr
                value = key
            else :
                # look for an entry in the passed in dict
                if self.translator_dictionary.has_key(parameter_name) :
                    if self.translator_dictionary[parameter_name].has_key(key) :
                        translator_dictionary[key] = self.translator_dictionary[parameter_name][key]
                        self.object_dictionary[parameter_name][key] = translator_dictionary[key]
                    else :
                        # if no suitable objects, use class
                        translator_dictionary[key] = parameter.range()[key]
                else :
                    translator_dictionary[key] = parameter.range()[key]

        # if the current value lies outwith the recognised classes, then add the class to the list, with
        # the current value as the object.
        if (value == '') :
            translator_dictionary[attr.name] = attr
            self.object_dictionary[parameter_name][attr.name] = attr
            value = attr.name
        self.translator_dictionary[parameter_name] = translator_dictionary
        # maps the class key to the object found above. 
        translator = lambda in_string: dict_translator(in_string, parameter_name, 
            translator_dictionary = self.translator_dictionary)
        self.__widgets[parameter_name] = self.__properties_frame.add_combobox_property(
                    parameter_name,
                    value = value,
                    scrolledlist_items = translator_dictionary.keys(),
                    translator = translator)
        w = self.__widgets[parameter_name][1]
        # bind right click to allow the selected classes properties to be changed.
        w._entryWidget.bind('<Button-3>', 
            lambda event: self.right_click(event, w, parameter_name))

    def right_click(self, event, widget, name) :
        self.parameters_properties = widget, name
        self.menu.tk_popup(event.x_root, event.y_root)

    def show_parameter_properties(self, param) :
        w, name = param
        obj = w.get_value()
        # It is possible that the selected field is a Class. Check and if it is, 
        # instantiate a new object of the class and enter it in the dictionary.
        from topo.base.parameterizedobject import ParameterizedObject
        if not isinstance(obj, ParameterizedObject) :
            try :
                obj = obj()
                obj_key = w.get()
                self.translator_dictionary[name][obj_key] = obj
                self.object_dictionary[name][obj_key] = obj
            except : return
        parameter_window = Toplevel()
        Label(parameter_window, text = obj.name).pack(side = TOP)
        parameter_frame = ParametersFrame(parameter_window)
        parameter_frame.create_widgets(obj)
        button_panel = Frame(parameter_window)
        button_panel.pack(side = BOTTOM)
        Button(button_panel, text = 'Ok', command = lambda frame=parameter_frame, win=parameter_window: 
            self.parameter_properties_ok(frame, win)).pack(side = RIGHT)
        Button(button_panel, text = 'Apply', 
            command = parameter_frame.set_obj_params).pack(side = RIGHT)

    def parameter_properties_ok(self,frame, win) :
        frame.set_obj_params()
        win.destroy()

    def __add_boolean_property(self,parameter_name,parameter):
        """
        Add a boolean property to the properties_frame by representing it with a
        Checkbutton.
        """
        self.__widgets[parameter_name] = self.__properties_frame.add_checkbutton_property(
                    parameter_name,
                    value = getattr(self.topo_obj,parameter_name))

    def __add_bounding_box_property(self,parameter_name,parameter) :
        attr = getattr(self.topo_obj,parameter_name)
        points = attr.aarect().lbrt()
        translator = lambda in_string: string_bb_translator(in_string, default = points)
        self.__widgets[parameter_name] = self.__properties_frame.add_text_property(
            parameter_name,
            translator = translator,
            value = points)
        
    def __add_int_property(self, parameter_name, parameter) :
        attr = getattr(self.topo_obj, parameter_name)
        translator = lambda num: string_int_translator(num, default = attr)
        self.__add_text_property(parameter_name,parameter, translator = translator)

    def __add_property_for_class(self, parameter_name) :
        attr = getattr(self.topo_obj,parameter_name)
        attr_class = attr.__class__
        if self.__class_property.has_key(attr_class) :
            self.__class_property[attr.__class__](parameter_name, None)
        else :
            self.__add_text_property(parameter_name,None)

