"""
Collection of compound widgets for Tkinter.

$Id: widgets.py 8443 2008-04-27 05:08:51Z ceball $
"""
__version__='$Revision: 8443 $'


import decimal
import Tkinter

from tkMessageBox import _show,QUESTION,YESNO
from scrodget import Scrodget


# Barely wrapped tooltip from tklib.
# CB: this isn't the right way to do it, and it breaks menubar
# tips for some reason, but user code didn't have to change.

class Balloon(Tkinter.Widget):
    
    _tkname = '::tooltip::tooltip'

    def __init__(self,master,cnf={},**kw):
        master.tk.call("package","require","tooltip")
        Tkinter.Widget.__init__(self, master,self._tkname, cnf, kw)

    def bind(self,*args):
        """
        e.g. for a Button b and a Menu m with item 'Quit' in a Toplevel t
        
        balloon = Balloon(t)
        balloon.bind(b,'some guidance')
        balloon.bind(m,'Quit','more guidance')
        """
        if len(args)>2:            
            self.tk.call(self._tkname,args[0]._w,'-index',args[1],args[2])
        else:
            self.tk.call(self._tkname,*args)

##     def tagbind(self,*args,**kw):
##         print "### Balloon.tagbind(): not yet implemented error ###"



# CEBALERT: should be renamed to something like IndexMenu, but then
# I am not sure if some of our tk hacks would work (e.g. in topoconsole,
# we set something for Menu on linux so that the popup behavior is
# reasonable).
class Menu(Tkinter.Menu):
    """
    Tkinter Menu, but with a way to access entries by name.

    Supply indexname to any of the add/insert/delete methods and that
    indexname can be used to get the index of the entry later on (if
    'indexname' not supplied, uses 'label' instead, if that was
    supplied).
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
        self.tag.bind('<Leave>', self._tag_focus_out)

        # no variable: we control the slider ourselves
        self.slider = Tkinter.Scale(self,variable=None,
                    from_=self.bounds[0],to=self.bounds[1],
                    orient='horizontal',length=slider_length,
                    showvalue=0,**slider_extra_config)
        
        self.slider.pack(side='right',expand="yes",fill='x')
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
        
 
    # CB: why isn't this used for [] access? What should this
    # be called? Is it configure?
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

        return {} # CEBALERT: need to return same object as Tkinter would.
    

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
        """
        Use the actual number in the box to set the slider's resolution,
        so that user-entered resolutions are respected (e.g. 0.1 vs 0.1000).

        If that's not possible (e.g. there's text in the box), use the
        value contained in the variable (because whatever owns the
        variable could have performed a conversion of the text -
        TkParameterized does this, for instance).

        Leaves the resolution as it was if no number is available.
        """
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
        If the value in the box can't be converted to a float, the slider doesn't get set.
        """
        tagvar_val = self.variable.get()
        try:
            val = float(tagvar_val)
            self.set_slider_bounds(min(self.bounds[0],val),
                                   max(self.bounds[1],val))
            self.slider.set(val)
        except ValueError:
            pass


class FocusTakingButton(Tkinter.Button):
    """
    A Tkinter Button that takes the focus when the mouse <Enter>s.

    (Tkinter.Button doesn't get focus even when it's clicked,
    and only <Enter> and <Leave> events work for buttons.)
    """
    def __init__(self, master=None, cnf={}, **kw):
        Tkinter.Button.__init__(self,master=master,cnf=cnf,**kw)
        self.bind("<Enter>", lambda e=None,x=self: x.focus_set())
        #self['highlightthickness']=0



# Might wonder why we need <<SizeRight>> event, and don't just use the
# <Configure> event for calling sizeright: Can't distinguish manual
# resize from autoresizing.

class ScrolledFrame(Tkinter.Frame):
    """
    XXXX
    
    Content to be scrolled should go in the 'content' frame.
    """
    def __init__(self,parent,**config):
        Tkinter.Frame.__init__(self,parent,**config)

        self.canvas = Tkinter.Canvas(self)
        self.canvas.pack()
        self.canvas.configure(width=0,height=0)
        
        self.sc = Scrodget(self,autohide=1)
        self.sc.associate(self.canvas)
        self.sc.pack(expand=1,fill="both")
        
        self.content = Tkinter.Frame(self.canvas)
        self.content.title = lambda x: self.title(x)
        
        self.canvas.create_window(0,0,window=self.content,anchor='nw')

        self.bind("<<SizeRight>>",self.sizeright)



    def sizeright(self,event=None):
        self.content.update_idletasks()
        self.canvas.configure(scrollregion=(0, 0, self.content.winfo_width(),
                                           self.content.winfo_height()))
        self.canvas.configure(width=self.content.winfo_width(),
                             height=self.content.winfo_height())





class ScrolledWindow(Tkinter.Toplevel):

    def __init__(self,parent,**config):
        Tkinter.Toplevel.__init__(self,parent,**config)
        self.maxsize(self.winfo_screenwidth(),self.winfo_screenheight())
        self._scrolledframe = ScrolledFrame(self)
        self._scrolledframe.pack(expand=1,fill='both')
        self.content = self._scrolledframe.content

    # required? presumably should be deleted
    def sizeright(self,event=None):
        self._scrolledframe.sizeright()


class StatusBar(Tkinter.Frame):

    def __init__(self, master):
        Tkinter.Frame.__init__(self, master)
        self.label = Tkinter.Label(self, borderwidth=1, relief='sunken', anchor='w')
        self.label.pack(fill='x')

    def message(self,chuck=None,message=None):
        self.set(message)

    def set(self, format, *args):
        self.label.config(text=format % args)
        self.label.update_idletasks()

    def clear(self):
        self.label.config(text="")
        self.label.update_idletasks()



class AppWindow(ScrolledWindow):
    """
    A ScrolledWindow with extra features intended to be common to all
    windows of an application.
    
    Currently this only includes a window icon, but we intend to
    add a right-click menu and possibly more.
    """
    window_icon_path = None

    def __init__(self,parent,status=False,**config):

        ScrolledWindow.__init__(self,parent)
        self.content.title = self.title

        # CEBALERT: doesn't work on OS X, and is a strange color on
        # Windows.  To get a proper icon on OS X, we probably have to
        # bundle into an application package or something like that.
        # On OS X, could possibly alter the small titlebar icon with something like:
        # self.attributes("-titlepath","/Users/x/topographica/AppIcon.icns")
        self.iconbitmap('@'+self.window_icon_path)

        ### Universal right-click menu
        # CB: not currently used by anything but the plotgrouppanels
        # self.context_menu = Tkinter.Menu(self, tearoff=0)
        # self.bind("<<right-click>>",self.display_context_menu)

        # status bar is currenlty inside scrolled area (a feature
        # request is to move it outside ie replace self.content with
        # just self)
        self.status = StatusBar(self.content) 
        if status:
            self.status.pack(side="bottom",fill="x",expand="no")
        


# CEB: workaround for tkinter lagging behind tk (tk must have changed
# the type of a returned value).  This is copied almost exactly from
# tkMessageBox If there are other things like this, we could have the
# gui load some 'dynamic patches' to tkinter on startup, which could
# then be removed when tkinter is updated (they'd all be in one place,
# and no tkgui code would have to change).
def askyesno(title=None, message=None, **options):
    "Ask a question; return true if the answer is yes"
    s = _show(title, message, QUESTION, YESNO, **options)
    return str(s) == "yes"
