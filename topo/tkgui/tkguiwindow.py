### CEBALERT! TkguiWindow shouldn't be in a file by itself, but there
### is at least one import problem in tkgui (probably caused by files
### importing each other). (Putting even a do-nothing, import-nothing
### version of this class in any of the existing tkgui files and then
### trying to use it in plotgrouppanel.py generates an import error.)



import Tkinter

# most of the classes in tkinter probably need to be in a different
# file from the one they're currently in...so does this one.
class Menu(Tkinter.Menu):
    """
    Tkinter Menu, but with a way to access entries by name.

    Supply indexname to any of the add/insert/delete methods
    and that indexname can be used to get the index of the entry
    later on.
    """
    ## note that I added a separate indexname rather than using
    ## label or some other existing name because those could
    ## change, and they're different for different widgets
    
    def index2indexname(self,index):
        for name,i in self.contents.items():
            if index==i: return name
        raise ValueError("%s not in Tkinter.Menu %s"%(index,self))


    ########## METHODS OVERRIDDEN to keep track of contents
    def __init__(self, master=None, cnf={}, **kw):
        self.contents = {}
        Tkinter.Menu.__init__(self,master,cnf,**kw)


    def add(self, itemType, cnf={}, **kw):
        indexname = cnf.pop('indexname',kw.pop('indexname',None))        
        Tkinter.Menu.add(self,itemType,cnf,**kw)
        i = self.index("last") 
        self.contents[indexname or i] = i 
        

        
    def insert(self, index, itemType, cnf={}, **kw):
        indexname = cnf.pop('indexname',kw.pop('indexname',index))
        self.contents[indexname] = index
        Tkinter.Menu.insert(self,index,itemType,cnf,**kw)

        
    def delete(self, index1, index2=None):
        assert index2 is None, "I only thought about single-item deletions: code needs to be upgraded..."

        i1 = self.index(index1)
        self.contents.pop(self.index2name(i1))

        Tkinter.Menu.delete(self,index1,index2)


    ########## METHODS OVERRIDDEN FOR CONVENIENCE
    def entryconfigure(self, index, cnf=None, **kw):
        """Configure a menu item at INDEX."""
        if isinstance(index,str):
            i=self.contents[index]
        else:
            i=index      
        Tkinter.Menu.entryconfigure(self,i,cnf,**kw)
        
    entryconfig = entryconfigure

    # other methods can be overriden if they're needed
    



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


        ### Universal right-click menu
        self.context_menu = Menu(self, tearoff=0)
##         self.bind("<<right-click>>",self.display_context_menu)


##         self.context_menu.add_command(0,label="Save window",
##                                       indexname="save_to_postscript",
##                                       command=self.save_to_postscript)
        


    # CB: still to decide between frame/window; the right-click stuff will probably change.
    
##     def display_context_menu(self,e):
##         self.context_menu.tk_popup(e.x_root,
##                                    e.y_root)
        
##     def save_to_postscript(self):
##         print "save to postscript"

     







    
