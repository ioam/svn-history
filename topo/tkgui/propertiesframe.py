"""
Generic property list frame that can be used for any object's properties.

Makes a frame and allows the caller to add properties of various types to it.

$Id$
"""
__version__='$Revision$'

from Tkinter import Frame, StringVar, Entry, Message, Checkbutton, IntVar, N,S,E,W,X
from taggedslider import TaggedSlider,EntryEval,ComboBoxEval


class PropertiesFrame(Frame):
    """
    GUI window for displaying and manipulating the properties of an
    object.  This class is very general, and could be used for
    manipulating any object that has enumerable properties.
    """
    def __init__(self, parent=None, padding=2,**config):
        self.parent = parent
        self.properties = {}
        self.padding = padding
        Frame.__init__(self,parent,config)


    def optional_refresh(self,CEBHACKALERT=None):
        if self.parent.auto_refresh: self.parent.refresh()


    def add_property(self,name,var,control,value):
        p = Message(self,text=name,aspect=5000)
        p.grid(row=len(self.properties),column=0,padx=self.padding,
               pady=self.padding,sticky=E)
        control.grid(row=len(self.properties),
                     column=1,
                     padx=self.padding,
                     pady=self.padding,
                     sticky=N+S+W+E)

        self.properties[name] = var
        self.properties[name].set(value)
        return (p,control)


    # CEBHACKALERT: re-implement checkbox

    def add_text_property(self,name,value="",string_translator=None,width=20):
        """
        Create a TKInter.Entry box and add it to self.properties.

        This property stores its value in a TKInter StringVar.
        """
        var = StringVar()
        control = EntryEval(self,
                            textvariable = var,
                            string_translator = string_translator,
                            width=width)
        
        control.bind('<Return>', self.optional_refresh)
        return self.add_property(name,var,control,value)

        
    def add_tagged_slider_property(self, name, value="", string_translator=None, **kw):
        """
        Create a TaggedSlider and add it to self.properties.
        
        This property stores its value in a TKInter StringVar.
        """
        var = StringVar()
        var.set(value)
        control = TaggedSlider(self,
                               tagvariable=var,
                               string_translator=string_translator,
                               **kw)
        return self.add_property(name,var,control,value)


    def add_combobox_property(self,name,value='',items=[], string_translator=None):
        """
        Create a ComboBox that can convert its string variable using the given string_translator and add it to self.properties.
        """        
        var = StringVar()
        control = ComboBoxEval(self,
                               selectioncommand=(lambda value: self.properties[name].set(value)),
                               scrolledlist_items = items,
                               string_translator = string_translator)
                
        control.selectitem(value)
        control.bind('<Return>', self.optional_refresh)
        return self.add_property(name,var,control,value)



    # CEBHACKALERT: currently unused, but could be used in the future to set the
    # properties from a dictionary (see CEBHACKALERT in ParametersFrame).
##     def set_values(self,values):
##         for (name,value) in values.items():
##             self.properties[name].set(value)

        
