### CEBALERT! TkguiWindow shouldn't be in a file by itself, but there
### is at least one import problem in tkgui (probably caused by files
### importing each other). (Putting even a do-nothing, import-nothing
### version of this class in any of the existing tkgui files and then
### trying to use it in plotgrouppanel.py generates an import error.)


import os.path, sys

import Tkinter

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
