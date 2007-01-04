"""
Tk widgets that support evaluation (translation) of a string to set their value.

$Id$
"""
__version__='$Revision$'

from Tkinter import Frame, IntVar, Scale, Entry, Checkbutton, Label
from Tkinter import LEFT, RIGHT, TOP, BOTTOM, YES, BOTH, NORMAL
import Pmw
import string



class WidgetTranslator(object):
    """
    Abstract superclass for objects (typically Widgets) that accept a string
    value and compute a true value from that.  Subclasses must provide 
    a get() operation (as do Tk Widgets)
    """
    def __init__(self, translator=None):
        """
        The translator should be a function accepting one string argument
        and returning the result of the translation.
        """
        self.translator = translator


    def get(self):
        "Must be implemented by subclasses."
        raise NotImplementedError


    def get_value(self):
        """
        Method called by clients to get the real value that this widget
        is representing.

        Although a widget will typically display its contents as
        a string, the underlying variable could be any type. Clients
        can call this method to get that variable's value.
        """
        if self.translator != None:
            return self.translator(self.get())
        else:
            return self.get()
    

class EntryTranslator(Entry,WidgetTranslator):
    """
    Tkinter Entry widget with a translator.
    """
    def __init__(self, master, textvariable="", translator=None, **kw):
        Entry.__init__(self, master=master, textvariable=textvariable, **kw)
        WidgetTranslator.__init__(self, translator=translator)



class ComboBoxTranslator(Pmw.ComboBox,WidgetTranslator):
    """
    A Pmw ComboBox with a translator.
    """
    def __init__(self, parent,selectioncommand=None,scrolledlist_items=[],
                 translator=None, **kw):
        Pmw.ComboBox.__init__(self, parent,
                              selectioncommand=selectioncommand,
                              scrolledlist_items=scrolledlist_items, **kw)
        WidgetTranslator.__init__(self,translator=translator)



class CheckbuttonTranslator(Checkbutton,WidgetTranslator):
    """
    A Tkinter Checkbutton with a translator.
    """
    # CEB: It should be possible to eliminate self.var=variable and get();
    # should check out the Checkbutton documentation.
    def __init__(self, master, variable, **kw):
        self.var = variable
        Checkbutton.__init__(self,master=master,variable=variable,**kw)        
        WidgetTranslator.__init__(self,translator=None)

    def get(self):
        if self.var.get()==1:
            return True
        else:
            return False
    

# CEBALERT: Should make TaggedSlider accept either numeric or string
# values (including for max_value and min_value).

# CEBALERT: If we can make slider:tag space ratio about 2:1 (if it's
# possible to have relative sizes like that), then we won't have to have
# widths specified everywhere.

class TaggedSlider(Frame,WidgetTranslator):
    """
    Widget for manipulating a numeric value using either a slider or a
    text-entry box, keeping the two values in sync.

    The expressions typed into the text-entry box are evaluated using
    the given translator, which can be overridden with a custom
    expression evaluator (e.g. to do a Python eval() in the namespace
    of a particular object.)

    point out it only expects strings to come in, converts internally.

    """
    def __init__(self,root,
                 tagvariable=None,
                 min_value="0.0",
                 max_value="1.0",
                 string_format = '%f',
                 tag_width=10,
                 slider_length=100,
                 translator=string.atof,
                 **params):

        Frame.__init__(self,root,**params)
        WidgetTranslator.__init__(self,translator=translator)

        self.root = root
        self.__string_format = string_format
        
        # Add the tag
        self.__tag_val = tagvariable
        self.__tag = Entry(self,textvariable=self.__tag_val,width=tag_width)
        self.__tag.bind('<FocusOut>', self.refresh) # slider is updated on tag return... 
        self.__tag.bind('<Return>', self.action)   # ...and on tag losing focus
        self.__tag.pack(side=LEFT)

        self.__min_value = self.translator(min_value)
        self.__max_value = self.translator(max_value)
        
        # Add the slider        
        self.__slider_val = IntVar(0)
        self.__slider = Scale(self,showvalue=0,from_=0,to=10000,
                              orient='horizontal',
                              length=slider_length,
                              variable=self.__slider_val,
                              command=self.__slider_command)
        self.__slider.pack(side=LEFT,expand=YES,fill=BOTH)
        self.__set_slider_from_tag()
        self.__first_slider_command = True          # see self.__slider_command below
        

    # CEBALERT: I find the refresh() and optional_refresh() methods
    # confusing. Is there a simpler way to implement this kind of
    # functionality?    
    def refresh(self,e=None):
        """
        Sets the slider's position according to the value in the tag.
        Additionally, calls the parent widget's optional_refresh()
        method.
        """
        self.__set_slider_from_tag()
        try:
            # Refresh the PropertiesFrame (if embedded in one)
            self.root.optional_refresh()
        except AttributeError:
            pass

    # CB: having said the above, I compounded the problem by adding
    # more of the same.
    def action(self, e=None):
        """
        Pressing return in a TaggedSlider causes the slider itself to
        be refresh()ed, but also (optionally) allows an action to be
        'passed up' to its parent.
        """
        try:
            self.root.optional_action()
        except AttributeError:
            pass
        self.refresh()


    # CEBALERT: the comment is true, this is required. But
    # maybe there's a cleaner way?
    def __slider_command(self,arg):
        """
        When this frame is first shown, it calls the slider callback,
        which would overwrite the initial string value with a string
        translation (e.g. 'PI' -> '3.142').  This code prevents that.
        """
        if not self.__first_slider_command:
            self.__set_tag_from_slider()
            try:
                # Refresh the PropertiesFrame (if embedded in one)
                self.root.optional_refresh()
            except AttributeError:
                pass
        else:
            self.__first_slider_command = False


    def get(self):
        """
        Return the (string) value stored in the tag.
        """
        return self.__tag_val.get()

     

    def __set_tag_from_slider(self):
        new_string = self.__string_format % self.__get_slider_value()
        self.__tag_val.set(new_string)

         
    def __set_slider_from_tag(self):
        """
        Set the slider (including its movement limits) to match the tag value.
        """
        val = self.translator(self.__tag_val.get())
        if val > self.__max_value:
            self.__max_value = val
        elif val < self.__min_value:
            self.__min_value = val

        self.__set_slider_value(val)

        
    def __get_slider_value(self):
        range = self.__max_value - self.__min_value
        return self.__min_value + (self.__slider_val.get()/10000.0 * range)
    
    def __set_slider_value(self,val):
        range = self.__max_value - self.__min_value
        assert range!=0, "A TaggedSlider cannot have a maximum value equal to its minimum value."
        new_val = 10000 * (val - self.__min_value)/range
        self.__slider_val.set(int(new_val))
        

        



