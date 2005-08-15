"""
Class file for a properties page.

$Id$
"""

from Tkinter import Frame, StringVar, Entry, Message, Checkbutton, IntVar
from taggedslider import TaggedSlider
import Pmw

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

    def optional_refresh(self):
        if self.parent.auto_refresh:
            self.parent.refresh()

    def add_property(self,name,var,control,value):
        p = Message(self,text=name,aspect=5000)
        # p.grid(row=len(self.properties),column=0,padx=self.padding,
        #        pady=self.padding,sticky=E)
        # control.grid(row=len(self.properties),
        #              column=1,
        #              padx=self.padding,
        #              pady=self.padding,
        #              sticky=N+S+W+E)

        self.properties[name] = var
        self.set_value(name,value)
        return (p,control)


    def add_text_property(self,name,value="",**kw):
        var = StringVar()
        control = Entry(self,textvariable = var,width=50)
        return self.add_property(name,var,control,value,**kw)
        

    def add_checkbutton_property(self,name,value=0,**kw):
        var = IntVar()
        control = Checkbutton(self,text="",variable=var,**kw)
        return self.add_property(name,var,control,value)
        
    def add_tagged_slider_property(self,name,value='0',**kw):
        var = StringVar()
        var.set(value)
        control = TaggedSlider(self,tagvariable=var,**kw)
        return self.add_property(name,var,control,value)

    def add_combobox_property(self,name,value='',**kw):
        var = StringVar()
        var.set(value)
        control = Pmw.ComboBox(self,entry_textvariable=var,dropdown=1,**kw)
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
