"""
ParametersFrame class.

$Id$
"""
__version__='$Revision$'

from propertiesframe import PropertiesFrame
from Tkinter import Frame, Button, RIGHT, TOP, BOTTOM, END, YES, N,S,E,W,X, Menu, Toplevel, Label
import topo.base.utils
from topo.base.utils import keys_sorted_by_value, dict_translator
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

        self.option_add("*Menu.tearOff", "0") 
        self.menu = Menu(self)
        self.menu.insert_command(END, label = 'Properties', command = lambda: 
            self.showParamProperties(self.show_my_parameters))

        self.__help_balloon = Pmw.Balloon(parent)
        
        self.__widgets = {} # should it be none?
        self.__visible_parameters = {}

        # The dictionary of parameter_type:property_to_add pairs.
        self.__parameter_property = {
            topo.base.parameter.Constant:         self.__add_readonly_text_property,
            topo.base.parameter.Number:           self.__add_numeric_property,
            topo.base.parameter.Enumeration:      self.__add_enumeration_property,
            topo.base.parameter.BooleanParameter: self.__add_boolean_property,
            topo.base.parameter.ClassSelectorParameter: self.__add_class_selector_property}



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

    def create_widgets(self, topo_obj, translator_dictionary = {}):
        """
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

            # CEBHACKALERT: known not to be working.
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
        attr = getattr(self.topo_obj,parameter_name)
        str_attr = str(attr)
        if attr == str_attr :
            translator = None
            value = attr
        else :
            translator = lambda in_string: dict_translator(in_string, trdict = {str_attr:attr})
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

    def __add_class_selector_property(self,parameter_name,parameter):
        """
        Add a package property to the properties_frame by representing it
        with a ComboBox.
        """
        # get the current value of this field
        attr = getattr(self.topo_obj, parameter_name)
        translator_dictionary = {}
        value = ''
        # for each of the classes that this selector can select between loop through
        # and find if there is a suitable object already instantiated in either the
        # current value or in the dictionary passed in.
        for key in parameter.range().keys() :
            paramEntry = parameter.range()[key]
            if paramEntry == attr.__class__ :
                # if the class is the same as the class of the current value, use the
                # this as the cover for this class; note that this is the current selection
                translator_dictionary[key] = attr
                value = key
            else :
                try :
                    # loop through the passed in list for this field and if an entry is of the
                    # correct class, use it as a cover for the class
                    for entry in self.translator_dictionary[parameter_name] :
                        try :
                            if (self.translator_dictionary[entry].__class__ == paramEntry) :
                                translator_dictionary[key] = self.translator_dictionary[entry]
                        except Exception: pass # if entry does not have a class field
                    else :
                        # if no suitable objects, make a new object of the class
                        try : # ALALERT This means if an object of this class cannot be instantiated here
                              # it can't be selected in this selector
                            translator_dictionary[key] = parameter.range()[key]()
                        except Exception : pass
                except KeyError : # if there is no list entry for this field
                        try :# ALALERT This needs to be dealt with properly; as above
                            translator_dictionary[key] = parameter.range()[key]()
                        except Exception : pass

        # maps the class key to the object found above. 
        translator = lambda in_string: dict_translator(in_string, trdict = translator_dictionary)
        self.__widgets[parameter_name] = self.__properties_frame.add_combobox_property(
                    parameter_name,
                    value = value,
                    scrolledlist_items = translator_dictionary.keys(),
                    translator = translator)
        w = self.__widgets[parameter_name][1]
        # this could be retained and passed back, to retain the values of all object
        self.translator_dictionary[parameter_name] = translator_dictionary.values()
        # bind right click to allow the selected classes properties to be changed.
        w._entryWidget.bind('<Button-3>', 
            lambda event, w = w: self.rightClick(event, w))

    def rightClick(self, event, widget) :
        self.show_my_parameters = widget.get_value()
        self.menu.tk_popup(event.x_root, event.y_root)

    def showParamProperties(self, obj) :
        paramWindow = Toplevel()
        Label(paramWindow, text = obj.name).pack(side = TOP)
        paramFrame = ParametersFrame(paramWindow)
        paramFrame.create_widgets(obj)
        buttonPanel = Frame(paramWindow)
        buttonPanel.pack(side = BOTTOM)
        Button(buttonPanel, text = 'Apply', 
            command = paramFrame.set_obj_params).pack(side = RIGHT)
        Button(buttonPanel, text = 'Ok', command = lambda frame=paramFrame, win=paramWindow: 
            self.paramPropertiesOk(frame, win)).pack(side = RIGHT)

    def paramPropertiesOk(self,frame, win) :
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













