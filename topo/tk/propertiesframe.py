"""
Class file for a properties page.

CURRENT STATUS: Taken verbatim from LISSOM 5.0; not yet used.  

$Id$
"""

from Tkinter import *
from taggedslider import *
import Pmw

class PropertiesFrame(Frame):
    """
    GUI window for displaying and manipulating the properties of an object.
    """
    def __init__(self, parent=None, padding=2,**config):
        self.properties = {}
        self.padding = padding
        Frame.__init__(self,parent,config)


    def add_property(self,name,var,control,value):
        Message(self,text=name,aspect=5000).grid(row=len(self.properties),
                                                 column=0,
                                                 padx=self.padding,
                                                 pady=self.padding,
                                                 sticky=E)
        control.grid(row=len(self.properties),
                     column=1,
                     padx=self.padding,
                     pady=self.padding,
                     sticky=N+S+W+E)

        self.properties[name] = var
        self.set_value(name,value)


    def add_text_property(self,name,value="",**kw):
        var = StringVar()
        control = Entry(self,textvariable = var,width=50)
        self.add_property(name,var,control,value,**kw)
        

    def add_checkbutton_property(self,name,value=0,**kw):
        var = IntVar()
        control = Checkbutton(self,text="",variable=var,**kw)
        self.add_property(name,var,control,value)
        
    def add_tagged_slider_property(self,name,value='0',**kw):
        var = StringVar()
        var.set(value)
        control = TaggedSlider(self,tagvariable=var,**kw)
        self.add_property(name,var,control,value)

    def add_combobox_property(self,name,value='',**kw):
        var = StringVar()
        var.set(value)
        control = Pmw.ComboBox(self,entry_textvariable=var,dropdown=1,**kw)
        self.add_property(name,var,control,value)

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



#  This code moved to topographica/tests/testpropertiesframe.py
#  if __name__ == '__main__':
#      root = Tk()
#      root.title('Properties Frame Test')
#      pp = PropertiesFrame(root,padding=0)
#      pp.pack(expand=YES,fill=X)
#      
#      pp.add_text_property('Name', 'Jefferson Provost')
#      pp.add_text_property('Addr', '1601 Faro Dr. #1504')
#      pp.add_checkbutton_property('Student', 1)
#  
#      for i in range(5):
#          pp.add_text_property('Prop'+`i`, `i`)
#  
#      pp.add_tagged_slider_property("Volume",value='5',
#                                    string_format='%d',
#                                    min_value='0',max_value='11')
#  
#      pp.add_combobox_property("File",value='xxx',
#                               scrolledlist_items=('AAA','BBB','CCC'))
#      
#      values = pp.get_values()
#      print 'values = ' + `values`
#      pp.set_values(values)
