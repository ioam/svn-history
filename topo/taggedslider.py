from Tkinter import *
import string

class TaggedSlider(Frame):

    def __init__(self,root,
                 tagvariable=None,
                 min_value='0',
                 max_value='100',
                 string_format = '%f',
                 tag_width=10,
                 string_translator=string.atof,
                 **config):

        Frame.__init__(self,root,**config)

        self.min_value = string_translator(min_value)
        self.max_value = string_translator(max_value)
        self.fmt = string_format

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
        self.tag.pack(side=LEFT)

        self.tag_val.trace_variable('w',self.tag_val_callback)
        #print 'self.tag_val = ' + self.tag_val.get()
        self.set_slider_from_tag()


    def tag_val_callback(self,*args):
        self.set_slider_from_tag()
        
    def slider_command(self,arg):
        #
        # When this frame is first shown, it calls the slider
        # callback, which would overwrite the initial string value
        # with a string translation (e.g. 'PI' -> '3.142').
        # This prevents that.
        #
        if not self.first_slider_command:
            self.set_tag_from_slider()
        else:
            self.first_slider_command = 0
        
        
    def tag_keypress(self,ev):
        print 'tag_keypress: '+ev.char
        self.set_slider_from_tag()

    def set_tag_from_slider(self):
        new_string = self.fmt % self.get_slider_value()
        self.tag_val.set(new_string)
        
    def set_slider_from_tag(self):
        try:
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
        
    
if __name__ == '__main__':

    import Lissom
    
    root = Tk()
    slider_val = StringVar()
    slider_val.set('PI')
    slider = TaggedSlider(root,tagvariable=slider_val,
                          max_value='PI*2',                          
                          string_translator=Lissom.eval_expr,
                          string_format='%.3f')
    slider.pack(side=TOP,expand=YES,fill=X)
    #root.mainloop()
        
        
                 
