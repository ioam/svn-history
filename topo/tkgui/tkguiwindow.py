### This file has the unrelated Menu, TkguiWindow, and TaggedSlider
### classes.

### CEBALERT: need to re-organize files in tkgui.

### CEBALERT: there is at least one import problem in tkgui (probably
### caused by files importing each other). (Putting even a do-nothing,
### import-nothing version of the TkguiWindow class in any of the
### existing tkgui files and then trying to use it in
### plotgrouppanel.py generates an import error.)




######################################################################
import Tkinter
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
import os.path, sys
import topo.tkgui
topo_dir = os.path.split(os.path.split(sys.executable)[0])[0]
class TkguiWindow(Tkinter.Toplevel):
    """
    The standard tkgui window (the parent of most other tkgui windows).

    Defines attributes common to tkgui windows.
    """
    def __init__(self,**config):
        Tkinter.Toplevel.__init__(self,**config)

        ### Window icon
        if topo.tkgui.system_platform is 'mac':
            # CB: To get a proper icon on OS X, we probably have to bundle into an application
            # package or something like that.
            pass # (don't know anything about the file format required)
            # self.attributes("-titlepath","/Users/vanessa/topographica/AppIcon.icns")
        else:
            # CB: It may be possible for the icon be in color (using
            # e.g. topo/tkgui/topo.xpm), see http://www.thescripts.com/forum/thread43119.html
            # or http://mail.python.org/pipermail/python-list/2005-March/314585.html
            self.iconbitmap('@'+(os.path.join(topo_dir,'topo/tkgui/topo.xbm')))


        ### Universal right-click menu   CB: not currently used by anything but the plotgrouppanels
        self.context_menu = Menu(self, tearoff=0)
##         self.bind("<<right-click>>",self.display_context_menu)

##     # CB: still to decide between frame/window; the right-click stuff will probably change.
    
######################################################################


     







    


######################################################################
### CEB: working here
        
# CEBALERT: Should make TaggedSlider accept either numeric or string
# values (including for max_value and min_value).

# CEBALERT: If we can make slider:tag space ratio about 2:1 (if it's
# possible to have relative sizes like that), then we won't have to have
# widths specified everywhere.

from inspect import getdoc

from Tkinter import Frame, IntVar, Scale, Entry, Checkbutton, Label
from Tkinter import LEFT, RIGHT, TOP, BOTTOM, YES, BOTH, NORMAL
import Pmw
import string



class WidgetTranslator(object):
    """
    Abstract superclass for objects (typically Widgets) that accept a string
    value and compute a true value from that.  Subclasses must provide 
    a get() operation (as do Tk Widgets)
    """
    def __init__(self, translator=None):
        """
        The translator should be a function accepting one string argument
        and returning the result of the translation.
        """
        self.translator = translator


    def get(self):
        "Must be implemented by subclasses."
        raise NotImplementedError


    def get_value(self):
        """
        Method called by clients to get the real value that this widget
        is representing.

        Although a widget will typically display its contents as
        a string, the underlying variable could be any type. Clients
        can call this method to get that variable's value.
        """
        if self.translator != None:
            return self.translator(self.get())
        else:
            return self.get()


class TaggedSlider(Frame,WidgetTranslator):
    """
    Widget for manipulating a numeric value using either a slider or a
    text-entry box, keeping the two values in sync.

    The expressions typed into the text-entry box are evaluated using
    the given translator, which can be overridden with a custom
    expression evaluator (e.g. to do a Python eval() in the namespace
    of a particular object.)

    point out it only expects strings to come in, converts internally.

    """
    def __init__(self,root,
                 variable=None,
                 min_value="0.0",
                 max_value="1.0",
                 string_format = '%f',
                 tag_width=10,
                 slider_length=100,
                 translator=string.atof,
                 **params):

        Frame.__init__(self,root,**params)
        WidgetTranslator.__init__(self,translator=translator)

        self.root = root
        self.__string_format = string_format
        
        # Add the tag
        self.__tag_val = variable
        self.__tag = Entry(self,textvariable=self.__tag_val,width=tag_width)
        self.__tag.bind('<FocusOut>', self.refresh) # slider is updated on tag return... 
        self.__tag.bind('<Return>', self.action)   # ...and on tag losing focus
        self.__tag.pack(side=LEFT)

        self.set_bounds(min_value,max_value,refresh=False)

        
        # Add the slider        
        self.__slider_val = IntVar(0)
        self.__slider = Scale(self,showvalue=0,from_=0,to=10000,
                              orient='horizontal',
                              length=slider_length,
                              variable=self.__slider_val,
                              command=self.__slider_command)
        self.__slider.pack(side=LEFT,expand=YES,fill=BOTH)
        self.__set_slider_from_tag()
        self.__first_slider_command = True          # see self.__slider_command below


    def set_bounds(self,min,max,refresh=True):
        self.__min_value=self.translator(min)
        self.__max_value = self.translator(max)
        if refresh: self.refresh()

    # CEBALERT: I find the refresh() and optional_refresh() methods
    # confusing. Is there a simpler way to implement this kind of
    # functionality?    
    def refresh(self,e=None):
        """
        Sets the slider's position according to the value in the tag.
        Additionally, calls the parent widget's optional_refresh()
        method.
        """
        self.__set_slider_from_tag()
        try:
            # Refresh the ParametersFrame (if embedded in one)
            self.root.optional_refresh()
        except AttributeError:
            pass

    # CB: having said the above, I compounded the problem by adding
    # more of the same.
    def action(self, e=None):
        """
        Pressing return in a TaggedSlider causes the slider itself to
        be refresh()ed, but also (optionally) allows an action to be
        'passed up' to its parent.
        """
        try:
            self.root.optional_action()
        except AttributeError:
            pass
        self.refresh()


    # CEBALERT: the comment is true, this is required. But
    # maybe there's a cleaner way?
    def __slider_command(self,arg):
        """
        When this frame is first shown, it calls the slider callback,
        which would overwrite the initial string value with a string
        translation (e.g. 'PI' -> '3.142').  This code prevents that.
        """
        if not self.__first_slider_command:
            self.__set_tag_from_slider()
            try:
                # Refresh the ParametersFrame (if embedded in one)
                self.root.optional_refresh()
            except AttributeError:
                pass
        else:
            self.__first_slider_command = False


    def get(self):
        """
        Return the (string) value stored in the tag.
        """
        return self.__tag_val.get()

     

    def __set_tag_from_slider(self):
        new_string = self.__string_format % self.__get_slider_value()
        self.__tag_val.set(new_string)

         
    def __set_slider_from_tag(self):
        """
        Set the slider (including its movement limits) to match the tag value.
        """
        val = self.translator(self.__tag_val.get())
        if val > self.__max_value:
            self.__max_value = val
        elif val < self.__min_value:
            self.__min_value = val

        self.__set_slider_value(val)


    def __get_slider_value(self):
        # CEBALERT: range is an inbuilt function!
        range = self.__max_value - self.__min_value
        return self.__min_value + (self.__slider_val.get()/10000.0 * range)
    
    def __set_slider_value(self,val):
        range = self.__max_value - self.__min_value
        assert range!=0, "A TaggedSlider cannot have a maximum value equal to its minimum value."
        new_val = 10000 * (val - self.__min_value)/range
        self.__slider_val.set(int(new_val))


class TaggedSlider2(Frame):
    """
    Widget for manipulating a numeric value using either a slider or a
    text-entry box, keeping the two values in sync.

    The expressions typed into the text-entry box are evaluated using
    the given translator, which can be overridden with a custom
    expression evaluator (e.g. to do a Python eval() in the namespace
    of a particular object.)

    point out it only expects strings to come in, converts internally.

    """
    def __init__(self,master,variable,min_value=0.0,max_value=1.0,string_format=None,
                 tag_width=10,slider_length=100,translator=None,**config):

        Frame.__init__(self,master,**config)
        self.master = master

        self.__tag_val = variable
        
        self.__tag = Entry(self,textvariable=self.__tag_val,width=tag_width)
        self.__tag.pack(side=LEFT)
        
        self.__tag.bind('<FocusOut>', self.refresh) # slider is updated on tag return... 
        self.__tag.bind('<Return>', self.action)   # ...and on tag losing focus
        

        self.set_bounds(min_value,max_value,refresh=False)


        self.__slider_val = IntVar(0)
        self.__slider = Scale(self,showvalue=0,from_=0,to=10000,
                              orient='horizontal',
                              length=slider_length,
                              variable=self.__slider_val,
                              command=self.__slider_command)
        self.__slider.pack(side=LEFT,expand=YES,fill=BOTH)

        self.__set_slider_from_tag()



    def set_bounds(self,mn,mx,refresh=True):
        mn+1.0
        mx+1.0
        self.__min_value=mn
        self.__max_value=mx
        if refresh: self.refresh()

    # CEBALERT: I find the refresh() and optional_refresh() methods
    # confusing. Is there a simpler way to implement this kind of
    # functionality?    
    def refresh(self,e=None):
        """
        Sets the slider's position according to the value in the tag.
        Additionally, calls the parent widget's optional_refresh()
        method.
        """
        self.__set_slider_from_tag()
        try:
            # Refresh the ParametersFrame (if embedded in one)
            self.master.optional_refresh()
        except AttributeError:
            pass

    # CB: having said the above, I compounded the problem by adding
    # more of the same.
    def action(self, e=None):
        """
        Pressing return in a TaggedSlider causes the slider itself to
        be refresh()ed, but also (optionally) allows an action to be
        'passed up' to its parent.
        """
        try:
            self.master.optional_action()
        except AttributeError:
            pass
        self.refresh()


    # CEBALERT: the comment is true, this is required. But
    # maybe there's a cleaner way?
    def __slider_command(self,arg):
        """
        When this frame is first shown, it calls the slider callback,
        which would overwrite the initial string value with a string
        translation (e.g. 'PI' -> '3.142').  This code prevents that.
        """
        self.__set_tag_from_slider()



    def get(self):
        """
        Return the (string) value stored in the tag.
        """
        return self.__tag_val.get()

     

    def __set_tag_from_slider(self):
        new_string = self.__get_slider_value() #self.__string_format % self.__get_slider_value()
        self.__tag_val.set(new_string)

         
    def __set_slider_from_tag(self):
        """
        Set the slider (including its movement limits) to match the tag value.
        """
        # CEBALERT!
        try:
            val = float(self.__tag_val.get())
        except ValueError:
            print "VA in TS"
            from topo.misc.utils import eval_atof
            val = eval_atof(self.__tag_val.get())

        #val = self.__tag_val.get()
        if val > self.__max_value:
            self.__max_value = val
        elif val < self.__min_value:
            self.__min_value = val

        self.__set_slider_value(val)


    def __get_slider_value(self):
        range_ = self.__max_value - self.__min_value
        return self.__min_value + (self.__slider_val.get()/10000.0 * range_)
    
    def __set_slider_value(self,val):
        range = self.__max_value - self.__min_value
        assert range!=0, "A TaggedSlider cannot have a maximum value equal to its minimum value."
        new_val = 10000 * (val - self.__min_value)/range
        self.__slider_val.set(int(new_val))


TaggedSlider=TaggedSlider2
######################################################################
        



