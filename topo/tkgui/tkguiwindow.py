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
            # e.g. topo/tkgui/icons/topo.xpm), see http://www.thescripts.com/forum/thread43119.html
            # or http://mail.python.org/pipermail/python-list/2005-March/314585.html
            self.iconbitmap('@'+(os.path.join(topo_dir,'topo/tkgui/icons/topo.xbm')))


        ### Universal right-click menu   CB: not currently used by anything but the plotgrouppanels
        self.context_menu = Menu(self, tearoff=0)
##         self.bind("<<right-click>>",self.display_context_menu)

##     # CB: still to decide between frame/window; the right-click stuff will probably change.
    
######################################################################


import bwidget
# CB: move out of here + cleanup and document
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



class ScrolledTkguiWindow(TkguiWindow):

    def __init__(self,**config):
        TkguiWindow.__init__(self,**config)

        self.maxsize(self.winfo_screenwidth(),self.winfo_screenheight())
        
        self._scroll_frame = ResizableScrollableFrame(self,borderwidth=2,
                                                       relief="groove")
        self._scroll_frame.pack(expand="yes",fill="both")
        
        self.content = self._scroll_frame.contents


# CB: will try to make the window know when to resize itself, rather
# than having window users tell it
##         self.bind("<Configure>",self.deal_with_configure)

##     def deal_with_configure(self,e=None):
##         print e


    # CB: should be able to move to resizablescrollableframe
    def sizeright(self):
        # if user has changed window size, need to tell tkinter that it should take
        # control again.
        self.geometry('')

        self.update_idletasks()

        # extra for width of scrollbars
        extraw = self._scroll_frame._scrolled_window.winfo_reqwidth() - \
                 self._scroll_frame.scrolled_frame.winfo_reqwidth() + 3
        extrah = self._scroll_frame._scrolled_window.winfo_reqheight() - \
                 self._scroll_frame.scrolled_frame.winfo_reqheight() + 3

        w = min(self.content.winfo_reqwidth()+extraw,self.winfo_screenwidth())
        # -60 for task bars etc on screen...how to find true viewable height?
        h = min(self.content.winfo_reqheight()+extrah,self.winfo_screenheight()-60)

        if not hasattr(self,'oldsize') or self.oldsize!=(w,h): 
            self._scroll_frame.set_size(w,h)
            self.oldsize = (w,h)
            


     

######################################################################
import copy
import operator
import Tkinter
from decimal import Decimal
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
        p = Decimal(str(value)).as_tuple()[2]
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





# CB: haven't decided what to do. Might be temporary.
class TkPOTaggedSlider(TaggedSlider):
    """
    Adds extra ability to set slider when e.g. a variable
    name is in the tag.
    """
    def _try_to_set_slider_resolution(self):
        if not TaggedSlider._try_to_set_slider_resolution(self):
            # get the actual value as set on
            # the object (which might be the "last good" value)
            try:
                self._set_slider_resolution(self.variable._true_val())
            except: # probably tclerror
                pass


    def _try_to_set_slider(self):
        if not TaggedSlider._try_to_set_slider(self):
            v = self.variable._true_val()

            if operator.isNumberType(v):
                self.set_slider_bounds(min(self.bounds[0],v),
                                       max(self.bounds[1],v))
                self.slider.set(v)

    
    def refresh(self):
        """Could anything survive in tkgui without a refresh() method?"""
        self.tag_set()



    

######################################################################
        


