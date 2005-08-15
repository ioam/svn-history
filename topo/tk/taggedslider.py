"""
Class file for a TaggedSlider widget.

$Id$
"""
from Tkinter import Frame, IntVar, Scale, Entry
from Tkinter import LEFT, RIGHT, TOP, BOTTOM, YES, BOTH
import string
import inputparamspanel 

### JABHACKALERT!
###
### This file must be changed so that it does not depend on
### inputparamspanel; it's a general widget that could be useful in
### any Tk program.  It should probably just define a general
### string_translator function, e.g. string.atof, which would then be
### overridden with inputparamspanel.eval_atof.  Because it's not
### actually inputparamspanel that defines the sliders, but
### propertiesframe, propertiesframe would need to have a constructor
### argument for the appropriate string_translator, and would pass
### that on to the TaggedSlider.

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
                 min_value='0',
                 max_value='100',
                 string_format = '%f',
                 tag_width=10,
                 string_translator=inputparamspanel.eval_atof,
#                 string_translator=string.atof,
                 **config):

        Frame.__init__(self,root,**config)
        self.root = root

        self.min_value = string_translator(min_value)
        self.max_value = string_translator(max_value)
        self.fmt = string_format

        self.need_to_refresh_slider = True
        self.string_translator = string_translator

        # Add the slider
        
        self.slider_val = IntVar(0)
        self.slider = Scale(self,showvalue=0,from_=0,to=10000,orient='horizontal',
                           variable=self.slider_val, command=self.slider_command)
        self.slider.pack(side=LEFT,expand=YES,fill=BOTH)

        # see self.slider_command below
        self.first_slider_command = 1

        # Add the tag
        self.tag_val = tagvariable
        self.tag = Entry(self,textvariable=self.tag_val,width=tag_width)
        self.tag.bind('<KeyRelease>', self.tag_keypress)
        self.tag.bind('<FocusOut>', self.refresh)
        
        self.tag.pack(side=LEFT)

        self.tag_val.trace_variable('w',self.tag_val_callback)
        #print 'self.tag_val = ' + self.tag_val.get()
        self.set_slider_from_tag()

    def refresh(self,e):
        self.root.optional_refresh()

    def tag_val_callback(self,*args):
        self.set_slider_from_tag()
        
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
            self.first_slider_command = 0
        
        
    def tag_keypress(self,ev):
        #print 'tag_keypress: '+ev.char
        if ev.char != '\r':
            self.need_to_refresh_slider = True
        self.set_slider_from_tag(ev.char)

    def set_tag_from_slider(self):
        new_string = self.fmt % self.get_slider_value()
        self.tag_val.set(new_string)
##
        
    def set_slider_from_tag(self,evchar=None):
        # Attempt to update the sliders only on return.
        if not self.first_slider_command \
               and evchar == '\r' and self.need_to_refresh_slider:
            self.need_to_refresh_slider = False
            self.root.optional_refresh()
        try:
            if self.need_to_refresh_slider: 
                #print 'tag_keypress: '+evchar

                val = self.string_translator(self.tag_val.get())
                if val > self.max_value:
                    self.max_value = val
                elif val < self.min_value:
                    self.min_value = val
                        
                self.set_slider_value(val)

        except ValueError:
            pass
        
    def get_slider_value(self):
        range = self.max_value - self.min_value
        return self.min_value + (self.slider_val.get()/10000.0 * range)
    
    def set_slider_value(self,val):
        range = self.max_value - self.min_value
        new_val = 10000 * (val - self.min_value)/range
        self.slider_val.set(int(new_val))
        

        
                 
