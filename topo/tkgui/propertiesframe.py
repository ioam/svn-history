"""
Generic property list frame that can be used for any object's properties.

Makes a frame and allows the caller to add properties of various types to it.

$Id$
"""
__version__='$Revision$'

from Tkinter import Frame, StringVar, Message, Label, IntVar, N,S,E,W,X, NORMAL, Entry
from translatorwidgets import TaggedSlider,EntryTranslator,ComboBoxTranslator,CheckbuttonTranslator


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


    def optional_refresh(self,event=None):
        try:
            if self.parent.auto_refresh: self.parent.refresh()
        except AttributeError:
            pass
        


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


    def add_text_property(self,name,value="",readonly=False,**kw):
        """
        Create a TKInter.Entry box and add it to self.properties,
        unless readonly is True - in which case create a readonly
        Entry.
        """
        var = StringVar()

        if readonly:
            control = Entry(self,
                            state="readonly",
                            fg="gray45",
                            width=35,
                            textvariable = var,
                            **kw)
        else:
            control = EntryTranslator(self,
                                textvariable = var,
                                width=35,
                                **kw)
            control.bind('<Return>', self.optional_refresh)
            
        return self.add_property(name,var,control,value)

        
    def add_tagged_slider_property(self, name, value, **kw):
        """
        Create a TaggedSlider and add it to self.properties.
        """
        var = StringVar()
        var.set(value)
        control = TaggedSlider(self,
                               tagvariable=var,
                               **kw)
        return self.add_property(name,var,control,value)


    def add_combobox_property(self,name,value='',**kw):
        """
        Create a ComboBox that can convert its string variable using the given translator and add it to self.properties.
        """        
        var = StringVar()
        control = ComboBoxTranslator(self,
                               selectioncommand=(lambda value: self.properties[name].set(value)),**kw)
                
        control.selectitem(value)

        # CEBHACKALERT: this doesn't work for PMW. How do we bind the return
        # key to a PMW combobox? I couldn't figure it out.
        control.bind('<Return>', self.optional_refresh)
        return self.add_property(name,var,control,value)


    def add_checkbutton_property(self,name,value=0,**kw):
         """
         """
         var = IntVar()
         control = CheckbuttonTranslator(self, variable=var, **kw)
         return self.add_property(name,var,control,value)


    # CEBHACKALERT: currently unused, but could be used in the future to set the
    # properties from a dictionary (see CEBHACKALERT in ParametersFrame).
##     def set_values(self,values):
##         for (name,value) in values.items():
##             self.properties[name].set(value)

        
