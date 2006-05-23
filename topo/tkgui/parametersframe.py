"""
ParametersFrame class.


$Id$
"""
__version__='$Revision$'

# CEBHACKALERT: this file is being reorganized.

from inspect import getdoc

import Pmw
from Tkinter import Frame, Button, RIGHT, TOP, BOTH, BOTTOM, END, YES, N,S,E,W,X, Menu, Toplevel, Label, LEFT

import topo.misc.utils
from topo.misc.utils import keys_sorted_by_value, dict_translator, eval_atof
from topo.base.parameterizedobject import ParameterizedObject,ParameterizedObjectMetaclass,classlist
from topo.base.parameterclasses import Number,Enumeration,ClassSelectorParameter,BooleanParameter

from propertiesframe import PropertiesFrame
from translatorwidgets import CheckbuttonTranslator

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

        # CB: investigate
        self.translator_dictionary = {}

        # CB: surely there's a better way?
        self.topo_obj = None
        self.topo_class = None

        # CB: what does all this do?
        self.option_add("*Menu.tearOff", "0") 
        self.menu = Menu(self)
        self.menu.insert_command(END, label = 'Properties', command = lambda: 
            self.show_parameter_properties(self.parameters_properties))

        self.__help_balloon = Pmw.Balloon(parent)

        # CB: check these are used consistently
        self.__widgets = {}
        self.__visible_parameters = {}


        # The dictionary of parameter_type:property_to_add pairs.
        self.__parameter_property = {
            Number: self.__add_numeric_property,
            Enumeration: self.__add_enumeration_property,
            BooleanParameter: self.__add_boolean_property,
            ClassSelectorParameter: self.__add_class_selector_property}



    def set_class_parameters(self) :
        """
        """
        assert isinstance(self.topo_class,ParameterizedObjectMetaclass), "ParameterFrame must be associated with a ParameterizedObjectMetaclass to set class parameters."

        for name in self.__visible_parameters: 
            # [0] is label (Message), [1] is widget
            w = self.__widgets[name][1]
            
            if w.get_value()!=getattr(self.topo_class,name):
                setattr(self.topo_class,name,w.get_value())


    def set_obj_params(self):
        """
        For all non-Constant Parameters of the currently set
        ParameterizedObject(), set the values of the Parameters to
        those specified by the widgets.

        Only sets the value on the object if the value in the widget
        is different from the one in the object. This prevents a local
        copy of a variable being made into a ParameterizedObject just
        because the ParameterizedObject is opened in the model editor.
        """
        assert isinstance(self.topo_obj,ParameterizedObject), "ParametersFrame must be associated with a ParameterizedObject to set object parameters."

        # CEBHACKALERT: name should be a constant Parameter; the
        # 'or name==...' can be removed when it is.
        parameters_to_modify = [(name,parameter)
                                for (name,parameter)
                                in self.__visible_parameters.items()
                                if not (parameter.constant==True or name=='name')]

        for (name,parameter) in parameters_to_modify:
            # [0] is label (Message), [1] is widget
            w = self.__widgets[name][1]
            
            if w.get_value()!=getattr(self.topo_obj,name):
                setattr(self.topo_obj,name,w.get_value())



    def __new_widgets(self,class_=False):
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
            self.__add_property_for_parameter(parameter_name,parameter,class_=class_)

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



    def create_class_widgets(self, topo_class, translator_dictionary = {}) :
        """
        """
        assert isinstance(topo_class,ParameterizedObjectMetaclass), "ParameterFrame must be passed a ParameterizedObjectMetaclass to create widgets for class Parameters."
        
        self.translator_dictionary = translator_dictionary

        self.topo_class = topo_class

        self.__visible_parameters = dict([(parameter_name,parameter)
                                      for (parameter_name,parameter)
                                      in self.topo_class.classparams().items()
                                      if not parameter.hidden])
        self.__new_widgets(class_=True)
 


    def create_widgets(self, topo_obj, translator_dictionary = {}):
        """
        topo.base.parameterclasses.Constant:
        Create widgets for all non-hidden Parameters of topo_obj and add them
        to the screen.

        Each Parameter gets a suitable widget (e.g. a slider for a Number with
        soft_bounds). The default widget is a text box.

        parameters must be Parameter objects.

        Widgets are added in order of the Parameters' precedences.

        If a dictionary is passed in when create_widgets is called
        __add_class_selector_property will attempt to get
        dictionary[parameter_name]. It expects these entries to be
        lists of relevant objects to cover the selectable classes. It
        updates the lists and it can be retrieved from
        self.translator_dictionary when set_obj_params is called and
        used on subsequent uses.
        """
        assert isinstance(topo_obj,ParameterizedObject), "ParameterFrame must be passed a ParameterizedObject to create widgets for Parameters."

        self.topo_obj=topo_obj


        self.__visible_parameters = dict([(parameter_name,parameter)
                                        for (parameter_name,parameter)
                                        in self.topo_obj.params().items()
                                        if not parameter.hidden])
        self.__new_widgets()




    def __add_property_for_parameter(self,parameter_name,parameter,class_=False):
        """
        Find the correct property type for the given parameter.

        If the parameter's type is not listed in
        self.__parameter_property, the class hierarchy is traversed until
        a match is found. If no match is found, the Parameter just gets a
        textbox. 
        """
        # CEBHACKALERT: results in DynamicNumber being called and producing
        # a value, rather than displaying information about the dynamic number.
        if class_:
            value = getattr(self.topo_class,parameter_name)
            # or parameter.default for the class?
        else:
            value = getattr(self.topo_obj,parameter_name)

        # CEBHACKALERT: name should be a constant Parameter; the
        # 'or parameter_name' can be removed when it is. (see earlier alert too)
        if (parameter.constant==True or parameter_name=='name') and class_==False:
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
        try:
            low_bound,high_bound = parameter.get_soft_bounds()

            # CEBHACKALERT: but one is ok - change this
            # CB: This seems ok to me now, what's the problem?
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

    # CB: how does this work?
    def __add_class_selector_property(self,parameter_name,value,parameter):
        """
        Add a package property to the properties_frame by representing it
        with a ComboBox.
        """
        attr = value

        # get the current value of this field
        translator_dictionary = {}
        # self.object_dictionary[parameter_name] = {}  what?
        value = ''
        
        # for each of the classes that this selector can select
        # between loop through and find if there is a suitable object
        # already instantiated in either the current value or in the
        # dictionary passed in.
        
        for key in parameter.range().keys() :
            parameter_entry = parameter.range()[key]
            if parameter_entry == attr.__class__ :
                translator_dictionary[key] = attr
                #self.object_dictionary[parameter_name][key] = attr
                value = key
            else :
                # look for an entry in the passed in dict
                #if self.translator_dictionary.has_key(parameter_name) :
                #    if self.translator_dictionary[parameter_name].has_key(key) :
                #        translator_dictionary[key] = self.translator_dictionary[parameter_name][key]
                #        self.object_dictionary[parameter_name][key] = translator_dictionary[key]
                    #else :
                        # if no suitable objects, use class
                    #    translator_dictionary[key] = parameter.range()[key]
                #else :
                translator_dictionary[key] = parameter.range()[key]

        # if the current value lies outwith the recognised classes, then add the class to the list, with
        # the current value as the object.
        if (value == '') :
            translator_dictionary[attr.name] = attr
            #self.object_dictionary[parameter_name][attr.name] = attr
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



    def __add_boolean_property(self,parameter_name,value,parameter):
        """
        Add a boolean property to the properties_frame by representing it with a
        Checkbutton.
        """
        self.__widgets[parameter_name] = self.__properties_frame.add_checkbutton_property(parameter_name,value=value)


    # CB: I guess this does a new frame?
    # JAB: Yes -- try it on something like an output_fn; it lets you
    # edit the properties of that object.
    def right_click(self, event, widget, name) :
        self.parameters_properties = widget, name
        self.menu.tk_popup(event.x_root, event.y_root)


    # CB: there's no way this can work, but I don't know what it's for yet.
    # JAB: See above.
    def show_parameter_properties(self, param) :
        w, name = param
        obj = w.get_value()
        # It is possible that the selected field is a Class. Check and if it is, 
        # instantiate a new object of the class and enter it in the dictionary.
        if not isinstance(obj, ParameterizedObject) :
            try :
                obj = obj()
                obj_key = w.get()
                self.translator_dictionary[name][obj_key] = obj
                self.object_dictionary[name][obj_key] = obj
            except : return
        parameter_window = Toplevel()
        parameter_window.title(obj.name+' parameters')
        Label(parameter_window, text = obj.name).pack(side = TOP)
        parameter_frame = ParametersFrame(parameter_window)
        parameter_frame.create_widgets(obj)
        button_panel = Frame(parameter_window)
        button_panel.pack(side = BOTTOM)
        Button(button_panel, text = 'Ok', command = lambda frame=parameter_frame, win=parameter_window: 
            self.parameter_properties_ok(frame, win)).pack(side = RIGHT)
        Button(button_panel, text = 'Apply', 
            command = parameter_frame.set_obj_params).pack(side = RIGHT)

    # CB: where's this called from.
    def parameter_properties_ok(self,frame, win) :
        frame.set_obj_params()
        win.destroy()
                
                
