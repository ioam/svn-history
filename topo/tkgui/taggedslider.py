"""
Class file for a TaggedSlider widget.

$Id$
"""
__version__='$Revision$'

from Tkinter import Frame, IntVar, Scale, Entry, Checkbutton, Label
from Tkinter import LEFT, RIGHT, TOP, BOTTOM, YES, BOTH, NORMAL
import Pmw
import string


# CEBHACKALERT: This file needs to be renamed.

# CEBHACKALERT: somewhere there has to be better handling of bad input.
# e.g. "cat" gives orientation zero, as does "pI/4".


# CEBHACKALERT: this should be an abstract class.
# Something isn't quite right because this isn't actually a widget,
# it just assumes that when instantiated the object will also be a widget.
class TranslatorWidget(object):
    """
    Abstract superclass for a widget that represents its true value with a string.
    """
    def __init__(self, translator=None):
        self.translator = translator


    def get_value(self):
        """
        Method called by clients to get the real value that this widget
        is representing.

        Although a widget will typically display its contents as
        a string, the underlying variable could be any type. Clients
        can call this method to get that variable's value.
        """
        # the get() method should come with being a widget...
        assert hasattr(self,'get'),\
               'Subclasses of TranslatorWidget must have a get() method. '+repr(self)
        
        if self.translator != None:
            return self.translator(self.get())
        else:
            return self.get()



class EntryTranslator(Entry,TranslatorWidget):
    """
    Tkinter Entry widget with a translator.
    """
    def __init__(self, master, textvariable="", translator=None, **kw):
        Entry.__init__(self, master=master, textvariable=textvariable, **kw)
        TranslatorWidget.__init__(self, translator=translator)



class ComboBoxTranslator(Pmw.ComboBox,TranslatorWidget):
    """
    A Pmw ComboBox with a translator.
    """
    def __init__(self, parent,selectioncommand=None,scrolledlist_items=[],
                 translator=None, **kw):
        Pmw.ComboBox.__init__(self, parent,
                              selectioncommand=selectioncommand,
                              scrolledlist_items=scrolledlist_items, **kw)
        TranslatorWidget.__init__(self,translator=translator)



class CheckbuttonTranslator(Checkbutton,TranslatorWidget):
    """
    A Tkinter Checkbutton...
    """
    # CEBHACKALERT: surely I don't have to do self.var=variable and get()?
    # Look at Checkbutton documentation
    def __init__(self, master, variable, **kw):
        self.var = variable
        Checkbutton.__init__(self,master=master,variable=variable,**kw)        
        TranslatorWidget.__init__(self,translator=None)

    def get(self):
        if self.var.get()==1:
            return True
        else:
            return False
    

# CEBHACKALERT: need to update with TranslatorWidget
class TaggedSlider(Frame):
    """
    Widget for manipulating a numeric value using either a slider or a
    text-entry box, keeping the two values in sync.

    The expressions typed into the text-entry box are evaluated using
    the given translator, which can be overridden with a custom
    expression evaluator (e.g. to do a Python eval() in the namespace
    of a particular object.)

    """
    def __init__(self,root,
                 tagvariable=None,
                 min_value=0,
                 max_value=100,
                 string_format = '%f',
                 tag_width=10,
                 translator=string.atof,
                 **config):

        Frame.__init__(self,root,**config)
        self.root = root
        self.fmt = string_format
        self.translator = translator
        
        # Add the tag
        self.tag_val = tagvariable
        self.tag = Entry(self,textvariable=self.tag_val,width=tag_width)

        self.min_value = self.translator(min_value)
        self.max_value = self.translator(max_value)
        

        # Add the slider        
        self.slider_val = IntVar(0)
        self.slider = Scale(self,showvalue=0,from_=0,to=10000,orient='horizontal',
                           variable=self.slider_val, command=self.slider_command)
        self.slider.pack(side=LEFT,expand=YES,fill=BOTH)
        self.set_slider_from_tag()
        self.first_slider_command = True          # see self.slider_command below

        


        self.tag.bind('<FocusOut>', self.refresh) # slider is updated on tag return... 
        self.tag.bind('<Return>', self.refresh)   # ...and on tag losing focus

        
        self.tag.pack(side=LEFT)

        


    def refresh(self,e=None):
        self.set_slider_from_tag()
        self.root.optional_refresh()


    # CEBALERT: the comment is true, this is required. But
    # maybe there's a cleaner way?
    def slider_command(self,arg):
        """
        When this frame is first shown, it calls the slider callback,
        which would overwrite the initial string value with a string
        translation (e.g. 'PI' -> '3.142').  This code prevents that.
        """
        if not self.first_slider_command:
            self.set_tag_from_slider()
            self.root.optional_refresh()
        else:
            self.first_slider_command = False
        
     

    def set_tag_from_slider(self):
        new_string = self.fmt % self.__get_slider_value()
        self.tag_val.set(new_string)

         
    def set_slider_from_tag(self):
        """
        Set the slider (including its limits) to match the tag value.
        """
        val = self.translator(self.tag_val.get())
        if val > self.max_value:
            self.max_value = val
        elif val < self.min_value:
            self.min_value = val

        self.__set_slider_value(val)

        
    def __get_slider_value(self):
        range = self.max_value - self.min_value
        return self.min_value + (self.slider_val.get()/10000.0 * range)
    
    def __set_slider_value(self,val):
        range = self.max_value - self.min_value
        new_val = 10000 * (val - self.min_value)/range
        self.slider_val.set(int(new_val))
        

    def get_value(self):
        return self.translator(self.tag_val.get())
        



