"""
Class file for a TaggedSlider widget.

$Id$
"""
__version__='$Revision$'

from Tkinter import Frame, IntVar, Scale, Entry, Checkbutton
from Tkinter import LEFT, RIGHT, TOP, BOTTOM, YES, BOTH
import string


# CEBHACKALERT: sometime in the day or two before 15/12 I introduced
# a bug where Image's taggedsliders for size and aspect ratio are
# not right to begin with (ie slider doesn't match tag).

# CEBHACKALERT: somewhere there has to be better handling of bad input.
# e.g. "cat" gives orientation zero, as does "pI/4".


class TaggedSlider(Frame):
    """
    Widget for manipulating a numeric value using either a slider or a
    text-entry box, keeping the two values in sync.

    The expressions typed into the text-entry box are evaluated using
    the given string_translator, which can be overridden with a custom
    expression evaluator (e.g. to do a Python eval() in the namespace
    of a particular object.)

    """

    def __init__(self,root,
                 tagvariable=None,
                 min_value=0,
                 max_value=100,
                 string_format = '%f',
                 tag_width=10,
                 string_translator=string.atof,
                 **config):

        Frame.__init__(self,root,**config)
        self.root = root
        self.fmt = string_format
        self.string_translator = string_translator
        
        # Add the tag
        self.tag_val = tagvariable
        self.tag = Entry(self,textvariable=self.tag_val,width=tag_width)

        self.min_value = self.string_translator(min_value)
        self.max_value = self.string_translator(max_value)
        

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
        val = self.string_translator(self.tag_val.get())
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
        return self.string_translator(self.tag_val.get())
        
                 


# CEBHACKALERT: much here is temporary .This file needs to be renamed.
# There should be a base class which has things like get_value(),
# self.string_translator, other common stuff we need the widgets to
# have, and so on and so on.

class EntryEval(Entry):

    # get rid of stuff like width from here.
    def __init__(self, master=None, textvariable="",string_translator=None, width=20):
        """
        String translator defaults to None because default is text.
        """
        Entry.__init__(self,master=master,textvariable=textvariable,width=width)
        self.string_translator = string_translator

    def get_value(self):
        if self.string_translator != None:
            return self.string_translator(self.get())
        else:
            return self.get()



from Pmw import ComboBox
class ComboBoxEval(ComboBox):

    def __init__(self,
                 parent,
                 selectioncommand=None,
                 scrolledlist_items=[],
                 string_translator=None):
        """
        String translator defaults to None because default is text.
        """

        ComboBox.__init__(self,
                          parent,
                          selectioncommand=selectioncommand,
                          scrolledlist_items=scrolledlist_items)
        self.string_translator = string_translator

    def get_value(self):
        if self.string_translator != None:
            return self.string_translator(self.get())
        else:
            return self.get()


class CheckbuttonEval(Checkbutton):

    def __init__(self, master=None, text="",variable=None, **kw):
        """
        String translator defaults to None because default is text.
        """
        Checkbutton.__init__(self,master=master,text=text,variable=variable,**kw)
        self.var = variable

    # CEBHACKALERT: surely I don't have to do this.
    def get_value(self):
        if self.var.get()==1:
            return True
        else:
            return False
