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

import Tkinter
from decimal import Decimal
class TaggedSlider(Tkinter.Frame):
    """
    Widget for manipulating a numeric value using either a slider or a
    text-entry box, keeping the two values in sync.
    """
    
    def __init__(self,master,variable,min_value=0,max_value=1,resolution=0.001,slider_length=100,
                 tag_width=10,
                 tag_extra_config={},slider_extra_config={}):

        Tkinter.Frame.__init__(self,master)

        self.variable=variable

        self.tag = Tkinter.Entry(self,textvariable=variable,width=tag_width,
                           **tag_extra_config)
        self.tag.pack(side='left')
        self.tag.bind('<Return>', self.tag_changed)  

        self.slider_variable = Tkinter.DoubleVar()
        self.slider_variable.trace_variable('w',self.slider_changed)        
        
        self.slider = Tkinter.Scale(self,variable=self.slider_variable,
                    from_=min_value,to=max_value,resolution=resolution,
                    showvalue=0,orient='horizontal',length=slider_length,
                    **slider_extra_config)
        self.slider.pack(side='right')


    def slider_changed(self,*args,**opts):
        self.variable.set(self.slider_variable.get())

    def tag_changed(self,event=None):
        val = self.variable.get()
        self.slider_variable.set(float(val))
        # how to find n. dp simply? I just happened to know the
        # Decimal module...
        p = Decimal(str(val)).as_tuple()[2]
        self.slider['resolution']=10**p

    def refresh(self):
        self.tag_changed()

    # for matching old callers: should be removed
    def get_value(self):
        return float(self.variable.get())

    # convenience methods
    def set_bounds(self,min_val,max_val,refresh=True):
        self.slider.config(from_=min_val,to=max_val)

    def config(self,**options):
        if 'state' in options:
            self.tag['state']=options['state']
            self.slider['state']=options['state']
            del options['state']
        if len(options)>0:
            raise NotImplementedError("Only state option is currently supported for this widget; \
            set options on either the component tag or the slider instead.")
######################################################################
        


