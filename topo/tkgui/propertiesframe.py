"""
Generic property list frame that can be used for any object's properties.

Makes a frame and allows the caller to add properties of various types to it.

$Id$
"""
__version__='$Revision$'

from Tkinter import Frame, StringVar, Entry, Message, Checkbutton, IntVar, N,S,E,W,X
from taggedslider import TaggedSlider
import Pmw
from topo.base.utils import eval_atof

class PropertiesFrame(Frame):
    """
    GUI window for displaying and manipulating the properties of an
    object.  This class is very general, and could be used for
    manipulating any object that has enumerable properties.
    """
    def __init__(self, parent=None, padding=2,string_translator=eval_atof,**config):
        self.parent = parent
        self.properties = {}
        self.padding = padding
        self.string_translator = string_translator
        Frame.__init__(self,parent,config)

    def optional_refresh(self):
        if self.parent.auto_refresh:
            self.parent.refresh()

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
        self.set_value(name,value)
        return (p,control)


    def add_text_property(self,name,value="",width=20,**kw):
        """
        Create a TKInter.Entry box and add it to self.properties.

        This property stores its value in a TKInter StringVar.
        """
        var = StringVar()
        control = Entry(self,textvariable=var,width=width)
        return self.add_property(name,var,control,value,**kw)

    def add_checkbutton_property(self,name,value=0,**kw):
        # not used so far: not tested
        var = IntVar()
        control = Checkbutton(self,text="",variable=var,**kw)
        return self.add_property(name,var,control,value)
        
    def add_tagged_slider_property(self,name,value='0',**kw):
        """
        Create a TaggedSlider and add it to self.properties.
        
        This property stores its value in a TKInter StringVar.
        The TaggedSlider gets this object's string translator.
        """
        var = StringVar()
        control = TaggedSlider(self,tagvariable=var,string_translator=self.string_translator,**kw)
        return self.add_property(name,var,control,value)

    def add_combobox_property(self,name,value='',items=[],**kw):
        """
        Create a Pmw.ComboBox and add it to self.properties.
        
        This property stores its value in a TKInter StringVar.
        """        
        var = StringVar()
        control = Pmw.ComboBox(self,
                               selectioncommand = (lambda value: self.set_value(name,value)), 
                               scrolledlist_items = items,
                               **kw)
        control.selectitem(value)
        return self.add_property(name,var,control,value)

    def get_value(self,name):
        return self.properties[name].get()

    def set_value(self,name,value):
        self.properties[name].set(value)

    def get_values(self):
        result = {}
        for (k,v) in self.properties.items():
            result[k] = v.get()
        return result


    def set_values(self,values):
        for (name,value) in values.items():
            self.set_value(name,value)

        
