"""
Collection of compound widgets for Tkinter.

Widgets in this file only depend on Tkinter (or other general packages
of widgets, such as bwidget) - they are not specific to Topographica.


$Id$
"""
__version__='$Revision$'

### CEBALERT: there is at least one import problem in tkgui (probably
### caused by files importing each other). (Putting even a do-nothing,
### import-nothing version of the TkguiWindow class in any of the
### existing tkgui files and then trying to use it in
### plotgrouppanel.py generates an import error.)
# CB: after reorganization, see if this problem persists.

import copy
import operator
import decimal
import Tkinter
import traceback
import code
import StringIO
import __main__

import Pmw
import bwidget




######################################################################
######################################################################
# CEBALERT: rename, bring in method from ControllableMenu
class Menu(Tkinter.Menu):
    """
    Tkinter Menu, but with a way to access entries by name.

    Supply indexname to any of the add/insert/delete methods
    and that indexname can be used to get the index of the entry
    later on (if 'indexname' not supplied, uses 'label' instead, if that was supplied).
    """
    ## (Original Menu class is in lib/python2.4/lib-tk/Tkinter.py)
    
    ## Note that I added a separate indexname rather than using label
    ## or some other existing name because those could change, and
    ## they're different for different widgets.  Unfortunately this
    ## means sometimes specifying label="Something" and
    ## indexname="Something".
    ## CB: It's probably possible to remove the requirement
    ## for a separate indexname, taking label or whatever instead. I've tried
    ## that (taking label if indexname not supplied).
    
    def index2indexname(self,index):
        for name,i in self.indexname2index.items():
            if index==i: return name
        raise ValueError("%s not in Tkinter.Menu %s"%(index,self))

    def index_convert(self,index):
        """Return the Tkinter index, whether given an indexname or index."""
        if isinstance(index,str):
            i=self.indexname2index[index]
        else:
            i=index
        return i


    ########## METHODS OVERRIDDEN to keep track of contents
    def __init__(self, master=None, cnf={}, **kw):
        self.indexname2index = {}  # rename to indexnames2index or similar
        self.entries = {}
        Tkinter.Menu.__init__(self,master,cnf,**kw)


    def add(self, itemType, cnf={}, **kw):
        indexname = cnf.pop('indexname',kw.pop('indexname',None))

        # take indexname as label if indexname isn't actually specified
        if indexname is None:
            indexname = cnf.get('label',kw.get('label',None))
        
        Tkinter.Menu.add(self,itemType,cnf,**kw)
        i = self.index("last") 
        self.indexname2index[indexname or i] = i

        # this pain is to keep the actual item, if it's a menu or a command, available to access
        self.entries[indexname or i] = cnf.get('menu',kw.get('menu',cnf.get('command',kw.get('command',None))))
        
        
    def insert(self, index, itemType, cnf={}, **kw):
        indexname = cnf.pop('indexname',kw.pop('indexname',index))

        # take indexname as label if indexname isn't actually specified
        if indexname is None:
            indexname = cnf.get('label',kw.get('label',None))

        self.indexname2index[indexname] = index
        Tkinter.Menu.insert(self,index,itemType,cnf,**kw)

        # this pain is to keep the actual item, if it's a menu or a command, available to access
        self.entries[indexname] = cnf.get('menu',kw.get('menu',cnf.get('command',kw.get('command',None))))

        
    def delete(self, index1, index2=None):
        assert index2 is None, "I only thought about single-item deletions: code needs to be upgraded..."

        i1 = self.index(index1)
        self.indexname2index.pop(self.index2name(i1))
        self.entries.pop(self.index2name(i1))

        Tkinter.Menu.delete(self,index1,index2)


    ########## METHODS OVERRIDDEN FOR CONVENIENCE
    def entryconfigure(self, index, cnf=None, **kw):
        """Configure a menu item at INDEX."""
        i = self.index_convert(index)
        Tkinter.Menu.entryconfigure(self,i,cnf,**kw)
        
    entryconfig = entryconfigure

    def invoke(self, index):
        """Invoke a menu item identified by INDEX and execute
        the associated command."""
        return Tkinter.Menu.invoke(self,self.index_convert(index))

    # other methods can be overriden if they're needed
    

# CEBALERT: not sure if, internally, Tkinter uses dictionary access to
# do things. So testing this class out, but methods would otherwise be
# in the Menu class above.
class ControllableMenu(Menu):
    def __getitem__(self,name):
        return self.entries[name]
######################################################################
######################################################################
    



######################################################################
######################################################################
# CB: cleanup and document
class ResizableScrollableFrame(Tkinter.Frame):
    """
    A scrollable frame that can also be manually resized.

    Any normal scrollable frame will not resize automatically to
    accommodate its contents, because that would defeat the
    purpose of scrolling in the first place.  However, having a
    scrollable frame that can be resized manually is useful; this
    class adds easy resizing to a bwidget
    ScrollableFrame/ScrolledWindow combination.
    """
    def __init__(self,master,**config):
        """
        The 'contents' attribute is the frame into which contents
        should be placed (for the contents to be inside the
        scrollable area), i.e. almost all use of
        f=ResizableScrollableFrame(master) will be via f.contents.
        """
        Tkinter.Frame.__init__(self,master,**config)

        # non-empty Frames ignore any specified width/height, so create two empty
        # frames used purely for setting height & width
        self.__height_sizer = Tkinter.Frame(self,height=0,width=0)
        self.__height_sizer.pack(side="left")
        self.__width_sizer = Tkinter.Frame(self,width=0,height=0)
        self.__width_sizer.pack()

        # the scrollable frame, with scrollbars
        self._scrolled_window = bwidget.ScrolledWindow(self,auto="both",
                                                       scrollbar="both")
        # set small start height/width, will grow if necessary
        scrolled_frame = bwidget.ScrollableFrame(self._scrolled_window,
                                                 height=50,width=50)
        self.scrolled_frame = scrolled_frame
        self._scrolled_window.setwidget(scrolled_frame)
        self._scrolled_window.pack(fill="both",expand='yes')

        # CB: tk docs say getframe() not necessary? Where did I see that?
        self.contents = scrolled_frame.getframe()


    def set_size(self,width=None,height=None):
        """
        Manually specify the size of the scrollable frame area.
        """
        self._scrolled_window.pack_forget() # try to stop stray scrollbars        
        if width:self.__width_sizer['width']=width
        if height:self.__height_sizer['height']=height
        self._scrolled_window.pack(fill="both",expand="yes")


##     def _fractions_visible(self):
##         X = [float(x) for x in self.scrolled_frame.xview().split(' ')]
##         Y = [float(x) for x in self.scrolled_frame.xview().split(' ')]
##         return X[1]-X[0],Y[1]-Y[0]

######################################################################
######################################################################
        



######################################################################
######################################################################
class TaggedSlider(Tkinter.Frame):
    """
    Widget for manipulating a numeric value using either a slider or a
    text-entry box, keeping the two values in sync.

    Generates a number of Events:

    <<TagFocusOut>>  - tag loses focus
    <<TagReturn>>    - Return pressed in tag
    <<SliderSet>>    - slider is clicked/dragged
    """
    def __init__(self,master,variable,bounds=(0,1),
                 slider_length=100,tag_width=10,
                 tag_extra_config={},slider_extra_config={}):
        """
        On clicking or dragging the slider, the tag value is set
        to the slider's value.

        On pressing Return in or moving focus from the tag, the slider
        value is set, but also:
        
        * the range of the slider is adjusted (e.g. to fit a larger
          max value)

        * the resolution of the slider is adjusted based on the
          the value in the tag (e.g. 0.01 in the tag gives a
          resolution of 0.01), also taking into account the precision
          of the value in the tag (e.g. 0.0100 gives a resolution
          of 0.0001).
        """
        # CEBALERT: ...although respecting the precision isn't always
        # helpful because the slider can still have a limited
        # resolution anyway (from its length and the range, given the
        # size of a pixel...)
        Tkinter.Frame.__init__(self,master)

        self.variable= variable
        self.bounds = bounds

        self.tag = Tkinter.Entry(self,textvariable=self.variable,
                                 width=tag_width,**tag_extra_config)
        self.tag.pack(side='left')
        self.tag.bind('<Return>', self._tag_press_return)  
        self.tag.bind('<FocusOut>', self._tag_focus_out)

        # no variable: we control the slider ourselves
        self.slider = Tkinter.Scale(self,variable=None,
                    from_=self.bounds[0],to=self.bounds[1],
                    showvalue=0,orient='horizontal',length=slider_length,
                    **slider_extra_config)
        
        self.slider.pack(side='right')
        self.slider.bind('<ButtonRelease-1>', self._slider_used)
        self.slider.bind('<B1-Motion>', self._slider_used)

        self.tag_set()


    def tag_set(self):
        """
        After entering a value into the tag, this method should be
        called to set the slider correctly.

        (Called automatically for tag's <Return> and <FocusOut>
        events.)
        """
        # Set slider resolution. This is important because
        # we want the slider to be positioned at the exact
        # tag value.
        self._try_to_set_slider_resolution()
        self._try_to_set_slider()


    def set_slider_bounds(self,lower,upper):
        """
        Set new lower and upper bounds for the slider.
        """
        self.bounds = (lower,upper)
        self.slider.config(from_=lower,to=upper)
    set_bounds = set_slider_bounds
        
                     
    def config(self,**options):
        """
        TaggedSlider is a compound widget. In most cases, config
        options should be passed to one of the component widgets
        (i.e. the tag or the slider). For some options, however,
        we need to handle them being set on the widget as a whole;
        further, some of these should be applied to both component
        widgets, but some should just be applied to one.

        Options handled:
        * state (applied to both)
        * background, foreground (applied to tag only)
        """
        if 'state' in options:
            self.tag['state']=options['state']
            self.slider['state']=options['state']
            del options['state']
        if 'background' in options:
            self.tag['background']=options['background']
            del options['background']
        if 'foreground' in options:
            self.tag['foreground']=options['foreground']
            del options['foreground']
        if len(options)>0:
            raise NotImplementedError(
                """Only state, background, and foreground options are
                currently supported for this widget; set options on
                either the component tag or slider instead.""")


    def get(self):
        """
        Calls the tag's get() method.

        Helps to match behavior of other Tkinter Widgets.
        """
        return self.tag.get()


    # CEBALERT: three different events for max. flexibility...but
    # often a user will just want to know if the value was set. Could
    # also generate a "<<TaggedSliderSet>>" event each time, which a
    # user could just look for. Or could these events all be children
    # of a <<TaggedSliderSet>>?
    def _slider_used(self,event=None):
        self.variable.set(self.slider.get())
        self.event_generate("<<SliderSet>>")


    def _tag_press_return(self,event=None):
        self.event_generate("<<TagReturn>>")
        self.tag_set()


    def _tag_focus_out(self,event=None):
        self.event_generate("<<TagFocusOut>>")
        self.tag_set()        


    def _set_slider_resolution(self,value):
        # CEBALERT: how to find n. dp simply?
        p = decimal.Decimal(str(value)).as_tuple()[2]
        self.slider['resolution']=10**p


    def _try_to_set_slider_resolution(self):
        try:
            # 1st choice is to get the actual number in the box:
            # allows us to respect user-entered resolution
            # (e.g. 0.010000) 
            self._set_slider_resolution(self.tag.get())
            return True
        except: # probably tclerror
            try:
                # ...but that might have been text.  2nd choice is to
                # get the value from the variable (e.g. 0.01)
                self._set_slider_resolution(self.variable.get())
                return True
            except: # probably tclerror
                return False # can't set a new resolution


    def _try_to_set_slider(self):
        """
        expand bounds if necessary
        """
        tagvar_val = self.variable.get()
        
        if operator.isNumberType(tagvar_val):
            self.set_slider_bounds(min(self.bounds[0],tagvar_val),
                                   max(self.bounds[1],tagvar_val))
            self.slider.set(tagvar_val)
            return True
        else:
            return False

######################################################################
######################################################################        





class InterpreterComboBox(Pmw.ComboBox):

    # Subclass of combobox to allow null strings to be passed to
    # the interpreter.
    
    def _addHistory(self):
        input = self._entryWidget.get()
        if input == '':
            self['selectioncommand'](input)
        else:
            Pmw.ComboBox._addHistory(self)


class OutputText(Tkinter.Text):
    """
    A Tkinter Text widget but with some convenience methods.

    (Notably the Text stays DISABLED (i.e. not editable)
    except when we need to display new text).
    """

    def append_cmd(self,cmd,output):
        """
        Print out:
        >>> cmd
        output

        And scroll to the end.
        """
        self.config(state=NORMAL)
        self.insert(END,">>> "+cmd+"\n"+output)
        self.insert(END,"\n")
        self.config(state=DISABLED)        
        self.see(END)

    def append_text(self,text):
        """
        Print out:
        text

        And scroll to the end.
        """
        self.config(state=NORMAL)
        self.insert(END,text)
        self.insert(END,"\n")
        self.config(state=DISABLED)
        self.see(END)



# CB: can we embed some shell or even ipython instead? Maybe not
# ipython for a while:
# http://lists.ipython.scipy.org/pipermail/ipython-user/2006-March/003352.html
# If we were to use ipython as the default interpreter for
# topographica, then we wouldn't need any of this, since all platforms
# could have a decent command line (could users override what they
# wanted to use as their interpreter in a config file?).  Otherwise
# maybe we can turn this into something capable of passing input to
# and from some program that the user can specify?
class CommandPrompt(Tkinter.Frame):
    """
    A Tkinter Frame widget that provides simple access to python interpreter.

    Useful when there is no decent system terminal (e.g. on Windows).

    Provides status messages to any supplied msg_bar (which should be a Pmw.MessageBar).
    """
    def __init__(self,master,msg_bar=None,**config):
        Tkinter.Frame.__init__(self,master,**config)


        self.msg_bar=msg_bar
        self.balloon = Pmw.Balloon(self)

        # command interpreter for executing commands (used by exec_cmd).
        self.interpreter = code.InteractiveConsole(__main__.__dict__)
        
        ### Make a ComboBox (command_entry) for entering commands.
        self.command_entry=InterpreterComboBox(self,autoclear=1,history=1,dropdown=1,
                                               label_text='>>> ',labelpos='w',
                                               # CB: if it's a long command, the gui obviously stops responding.
                                               # On OS X, a spinning wheel appears. What about linux and win?
                                               selectioncommand=self.exec_cmd)
        
        self.balloon.bind(self.command_entry,
             """Accepts any valid Python command and executes it in main as if typed at a terminal window.""")

        scrollbar = Tkinter.Scrollbar(self)
        scrollbar.pack(side='right', fill='y')
        # CEBALERT: what length history is this going to keep?
        self.command_output = OutputText(self,
                                         state='disabled',
                                         height=10,
                                         yscrollcommand=scrollbar.set)
        self.command_output.pack(side='top',expand='yes',fill='both')
        scrollbar.config(command=self.command_output.yview)

        self.command_entry.pack(side='bottom',expand='no',fill='x')


    def exec_cmd(self,cmd):
        """
        Pass cmd to the command interpreter.

        Redirects sys.stdout and sys.stderr to the output text window
        for the duration of the command.
        """   
        capture_stdout = StringIO.StringIO()
        capture_stderr = StringIO.StringIO()

        # capture output and errors
        sys.stdout = capture_stdout
        sys.stderr = capture_stderr

        if self.interpreter.push(cmd):
            self.command_entry.configure(label_text='... ')
            result = 'Continue: ' + cmd
        else:
            self.command_entry.configure(label_text='>>> ')
            result = 'OK: ' + cmd

        output = capture_stdout.getvalue()
        error = capture_stderr.getvalue()

        self.command_output.append_cmd(cmd,output)
        
        if error:
            self.command_output.append_text("*** Error:\n"+error)
            
        # stop capturing
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
                
        capture_stdout.close()
        capture_stderr.close()

        if self.msg_bar: self.msg_bar.message('state', result)

        self.command_entry.component('entryfield').clear()
