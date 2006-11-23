"""
ParametersFrame class.


$Id$
"""
__version__='$Revision$'

from inspect import getdoc

import Pmw
from Tkinter import Frame, Button, RIGHT, TOP, BOTH, BOTTOM, END, YES, N,S,E,W,X, Menu, Toplevel, Label, LEFT

import topo.misc.utils
from topo.misc.utils import keys_sorted_by_value, dict_translator, eval_atof
from topo.base.parameterizedobject import ParameterizedObject,ParameterizedObjectMetaclass,classlist
from topo.base.parameterclasses import Integer,Number,Enumeration,ClassSelectorParameter,BooleanParameter

from propertiesframe import PropertiesFrame
from translatorwidgets import CheckbuttonTranslator

# Some things missing from/wrong with ParametersFrame (other than the HACKALERTs):
#
# - There used to be a 'reset_to_defaults' method, which
#   didn't work. It would be good to be able to reset an object to have
#   the class defaults.
# - When creating a new Projection, we offer a 'name' field and
#   allow it to be typed in, but then ignore any text that's been entered.
# - Some kind of 'cancel' button, for window managers that don't have the
#   'X' button to close a window.




class ParametersFrame(Frame):
    """
    Frame that displays (and allows alteration of) the Parameters of
    an associated ParameterizedObject instance or class (via a
    PropertiesFrame for that ParameterizedObject).
    """
    def __init__(self, parent=None, **config):
        """
        """
        Frame.__init__(self,parent,config)
        self.__properties_frame = PropertiesFrame(parent)
        self.__properties_frame.pack(side=TOP,expand=YES,fill=BOTH)

        # Add the right click properties menu
        self.option_add("*Menu.tearOff", "0") 
        self.menu = Menu(self)
        self.menu.insert_command(END, label = 'Properties', command = lambda: 
            self.show_parameter_properties(self.parameters_properties))

        self.__help_balloon = Pmw.Balloon(parent)


        self.translator_dictionary = {}

        # The ParameterizedObject instance or class for which this
        # ParametersFrame displays and alters parameters.
        self.parameterized_object = None

        self.__widgets = {}
        self.__visible_parameters = {}

        # The dictionary of parameter_type:property_to_add pairs.
        self.__parameter_property = {
            Number: self.__add_numeric_property,
            Enumeration: self.__add_enumeration_property,
            BooleanParameter: self.__add_boolean_property,
            ClassSelectorParameter: self.__add_class_selector_property}


    def set_parameters(self) :
        """
        Set the parameters on the associated ParameterizedObject class or
        instance to the values specified by the widgets.
        
        For an instance, only sets the values of non-Constant Parameters,

        Only sets a value if the value in the widget is different from the one
        in the ParameterizedObject. This prevents a local copy of a variable
        being made into a ParameterizedObject just because the
        ParameterizedObject is opened in the model editor.
        """
        if isinstance(self.parameterized_object,ParameterizedObjectMetaclass):
            for name in self.__visible_parameters: 
                # [0] is label (Message), [1] is widget
                w = self.__widgets[name][1]

                if w.get_value()!=getattr(self.parameterized_object,name):
                    setattr(self.parameterized_object,name,w.get_value())

        elif isinstance(self.parameterized_object,ParameterizedObject):
            # CEBHACKALERT: name should be a constant Parameter; the
            # 'or name==...' can be removed when it is.
            parameters_to_modify = [(name,parameter)
                                    for (name,parameter)
                                    in self.__visible_parameters.items()
                                    if not (parameter.constant==True or name=='name')]

            for (name,parameter) in parameters_to_modify:
                # [0] is label (Message), [1] is widget
                w = self.__widgets[name][1]

                if w.get_value()!=getattr(self.parameterized_object,name):
                    setattr(self.parameterized_object,name,w.get_value())

        else:
            raise TypeError, "ParameterFrame must be associated with a ParameterizedObject class or instance to set parameters."


 

    def create_widgets(self, parameterized_object, translator_dictionary = {}):
        """
        Create widgets for all non-hidden Parameters of parameterized_object and add them
        to the screen.

        Each Parameter gets a suitable widget (e.g. a slider for a Number with
        soft_bounds). The default widget is a text box.

        Widgets are added in order of the Parameters' precedences.

        If a dictionary is passed in when create_widgets is called
        __add_class_selector_property will attempt to get
        dictionary[parameter_name]. It expects these entries to be
        lists of relevant objects to cover the selectable classes. It
        updates the lists and it can be retrieved from
        self.translator_dictionary when set_parameters is called and
        used on subsequent uses.
        """
        self.parameterized_object = parameterized_object
        params = None

        if isinstance(parameterized_object,ParameterizedObjectMetaclass):
            self.translator_dictionary = translator_dictionary
            params = self.parameterized_object.classparams().items()
        elif isinstance(parameterized_object,ParameterizedObject):
            params = self.parameterized_object.params().items()
        else:
            raise TypeError, "ParameterFrame must be passed a ParameterizedObject class or instance to create widgets for Parameters."

        self.__visible_parameters = dict([(parameter_name,parameter)
                                      for (parameter_name,parameter)
                                      in params
                                      if not parameter.hidden])
        self.__new_widgets()


    def __new_widgets(self):
        """
        Remove old labels and widgets from the screen (if there
        are any), then create new ones, sort them by Parameter
        precedence, and finally add them to the screen.
        """
        # wipe old labels and widgets from screen
        for (label,widget) in self.__widgets.values():
            label.grid_forget()
            widget.grid_forget()

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

            help_text = getdoc(self.__visible_parameters[parameter_name])

            label.grid(row=row,
                       column=0,
                       padx=self.__properties_frame.padding,
                       pady=self.__properties_frame.padding,
                       sticky=E)

            # We want widgets to stretch to both sides...
            posn=E+W
            # ...except Checkbuttons, which should be left-aligned.
            if isinstance(widget,CheckbuttonTranslator):
                posn=W
                
            widget.grid(row=row,
                        column=1,
                        padx=self.__properties_frame.padding,
                        pady=self.__properties_frame.padding,
                        sticky=posn)

            self.__help_balloon.bind(label, help_text)



    def __add_property_for_parameter(self,parameter_name,parameter):
        """
        Find the correct property type for the given parameter.

        If the parameter's type is not listed in
        self.__parameter_property, the class hierarchy is traversed until
        a match is found. If no match is found, the Parameter just gets a
        textbox. 
        """
        # CEBHACKALERT: results in DynamicNumber being called and producing
        # a value, rather than displaying information about the dynamic number.
        value = getattr(self.parameterized_object,parameter_name)

        # CEBHACKALERT: name should be a constant Parameter; the
        # 'or parameter_name' can be removed when it is. (see earlier alert too)
        if (parameter.constant==True or parameter_name=='name') and isinstance(self.parameterized_object,ParameterizedObject):
            self.__add_readonly_text_property(parameter_name,value,parameter)
        else:
            for c in classlist(type(parameter))[::-1]:
                if self.__parameter_property.has_key(c):
                    # find the right method...
                    property_to_add = self.__parameter_property[c]
                    # ...then call it
                    property_to_add(parameter_name,value,parameter)
                    return
            # no match: use text box
            self.__add_text_property(parameter_name,value,parameter)
            

    def __add_text_property(self,parameter_name,value,parameter):
        """
        Add a text property to the properties_frame.
        """
        # Used to keep track of the value and its string representation, or
        # to evaluate the string representation in __main__.__dict__
        translator = lambda in_string: dict_translator(in_string,translator_dictionary={str(value):value})
        
        self.__widgets[parameter_name]=self.__properties_frame.add_text_property(
            parameter_name,
            translator = translator,
            value = value)


    def __add_readonly_text_property(self,parameter_name,value,parameter):
        """
        Add a readonly text property to the properties_frame.
        """
        self.__widgets[parameter_name] = self.__properties_frame.add_text_property(
            parameter_name,
            value = value,
            readonly = True)

    def __add_numeric_property(self,parameter_name,value,parameter):
        """
        Add a numeric property to the properties_frame.

        If the parameter has distinct low and high softbounds, a tagged_slider
        property is added. Otherwise, just a textbox is added (with
        a translator for string to float).
        """
        # CEBHACKALERT: because TaggedSlider only works for floats, subclasses
        # of Number (like Integer) are just represented with a text box
        # (for the moment).
        if type(parameter)==Number:
            try:
                low_bound,high_bound = parameter.get_soft_bounds()

                if low_bound==None or high_bound==None or low_bound==high_bound:
                    # i.e. there aren't really softbounds
                    raise AttributeError 

                self.__widgets[parameter_name] = self.__properties_frame.add_tagged_slider_property(
                    parameter_name,
                    value,
                    min_value = str(low_bound),
                    max_value = str(high_bound),
                    string_format = '%.6f',
                    translator = topo.misc.utils.eval_atof)

            except AttributeError:
                self.__widgets[parameter_name] = self.__properties_frame.add_text_property(parameter_name,value=value,translator=topo.misc.utils.eval_atof)
        else:
            self.__widgets[parameter_name] = self.__properties_frame.add_text_property(parameter_name,value=value,translator=topo.misc.utils.eval_atof)


    def __add_enumeration_property(self,parameter_name,value,parameter):
        """
        Add an enumeration property to the properties_frame by representing
        it with a ComboBox.
        """
        # CEBHACKALERT: only string Enumerations work at the moment.
        self.__widgets[parameter_name] = self.__properties_frame.add_combobox_property(
                    parameter_name,
                    value = value,
                    scrolledlist_items = parameter.available)


    def __add_class_selector_property(self,parameter_name,value,parameter):
        """
        Add a package property to the properties_frame by representing it
        with a ComboBox.
        """
        translator_dictionary = {}
        value_text = ''
        
        possible_classes = parameter.range()
        self.translator_dictionary[parameter_name] = possible_classes


        # CEBHACKALERT: since this method is only called on creation of
        # the widgets, 'caching' the object like this only works for the
        # default object! This means that when you right click on a Parameter
        # and get a new ParameterizedObject, if you change the values of the
        # PO's Paremeters, they won't be saved...unless you're editing the
        # default (original) PO.
        for (visible_name,class_) in possible_classes.items():
            if class_ == value.__class__:
                value_text = visible_name
                # overwrite the class in {visible_name:class} with
                # the object, so it will be returned rather than a
                # new object if this class is selected again 
                self.translator_dictionary[parameter_name].update(
                    {visible_name:value})
                break


        # maps the class key to the object found above. 
        translator = lambda in_string: dict_translator(in_string, parameter_name, 
            translator_dictionary = self.translator_dictionary)


        self.__widgets[parameter_name] = self.__properties_frame.add_combobox_property(
                    parameter_name,
                    value = value_text,
                    scrolledlist_items = possible_classes.keys(),
                    translator = translator)
        w = self.__widgets[parameter_name][1]
        # bind right click to allow the selected classes properties to be changed.
        w._entryWidget.bind('<Button-3>', 
            lambda event: self.__right_click(event, w))


    def __add_boolean_property(self,parameter_name,value,parameter):
        """
        Add a boolean property to the properties_frame by representing it with a
        Checkbutton.
        """
        self.__widgets[parameter_name] = self.__properties_frame.add_checkbutton_property(parameter_name,value=value)


    def __right_click(self, event, widget) :
        self.parameters_properties = widget
        self.menu.tk_popup(event.x_root, event.y_root)


    def show_parameter_properties(self, widget):
        """
        Open a new window containing a ParametersFrame for the
        current object in the supplied widget.
        """
        obj = widget.get_value()

        parameter_window = Toplevel()
        parameter_window.title(obj.name+' parameters')
        title = Label(parameter_window, text = obj.name)
        title.pack(side = TOP)
        self.__help_balloon.bind(title,getdoc(obj))
        parameter_frame = ParametersFrame(parameter_window)
        parameter_frame.create_widgets(obj)
        button_panel = Frame(parameter_window)
        button_panel.pack(side = BOTTOM)
        Button(button_panel, text = 'Ok', command = lambda frame=parameter_frame, win=parameter_window: 
            self.__parameter_properties_ok(frame, win)).pack(side = RIGHT)
        Button(button_panel, text = 'Apply', 
            command = parameter_frame.set_parameters).pack(side = RIGHT)


    def __parameter_properties_ok(self,frame, win) :
        frame.set_parameters()
        win.destroy()
                
                
