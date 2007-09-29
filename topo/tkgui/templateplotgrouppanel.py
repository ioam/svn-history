"""
class TemplatePlotGroupPanel
Panel for displaying preference maps and activity plot groups.

$Id$
"""
__version__='$Revision$'


from inspect import getdoc
from math import pi
from numpy.fft.fftpack import fft2
from numpy.fft.helper import fftshift
from numpy import abs

import copy
import Pmw
from Tkinter import StringVar, Frame, YES, LEFT, TOP, RIGHT, X, Message, \
     Entry, Canvas, Checkbutton, BooleanVar, DISABLED, NORMAL,NO
from tkFileDialog import asksaveasfilename

import topo

from topo.base.parameterclasses import BooleanParameter

from plotgrouppanel import SheetPGPanel
from topo.plotting.plotgroup import TemplatePlotGroup

from tkguiwindow import Menu

### We want to support any featuremap type defined in that file, and
### so import all of them here.
import matplotlib
matplotlib.use('TkAgg')

### JABALERT: Should change this to discover and import all the
### commands/*.py files automatically
import __main__
exec "from topo.commands.analysis import *" in __main__.__dict__
exec "from topo.commands.basic import *"  in __main__.__dict__
exec "from topo.commands.pylabplots import *" in __main__.__dict__


### CEBALERT: additional dynamic info/right-click problems:
#
# 1: If I open an Activity plot and then measure an orientation map,
# the plot only shows Activity, but the dynamic info includes the or
# pref and selectivity.  That makes sense, given that the plot would
# show that if it were refreshed, but it's confusing. 
#
# 2. Once I've measured an orientation map, the dynamic info in the
# cfsom_or.ty Activity window is very long, and it causes the window
# size to change dynamically as I drag the mouse around.  That's very
# distracting.  Is there any way to make the window enlarge only once,
# and then keep it big? How to do that without disrupting
# enlarge/reduce etc.?
#
# 3. Formatting of plot name (a tuple) in CF window (e.g. cfsom_or,
# Unit X: 0.3).



# CEBALERT: should  be something in plot or wherever, or maybe I don't see how to get this
# info the easy way from it? Not sure I actually wrote this correctly, anyway.
def available_plot_channels(plot):
    """
    Return the channels+names of the channels that have views.
    """
    available_channels = {}
    for name,channel in plot.channels.items():
        if plot.view_dict.has_key(channel):
            available_channels[name]=channel
    return available_channels




### CB: I'm working here at the moment.

class TemplatePlotGroupPanel(SheetPGPanel):

    plotgroup_type = TemplatePlotGroup

    strength_only = BooleanParameter(default=False,doc="""If true, disables all but the Strength channel of each plot,
disabling all color coding for Strength/Hue/Confidence plots.""")

    ####################################################################
    # CEBALERT: Ugly hack!  Basic idea for method copied from previous
    # tkgui.  Instead, we probably want a mechanism for doing this
    # from the command line, probably a global 'monochrome' parameter
    # that all plots respect, and then people can modify the plot
    # templates directly if they need more control than that.
    def strength_only_fn(self):
        if self.strength_only:
            for name,template in self.plotgroup.plot_templates:
                for c in ['Confidence','Hue']:
                    if c in template:
                        self.__non_so_templates[name][c]=template[c]
                        del template[c]
        else:
            for name,template in self.plotgroup.plot_templates:
                for c in ['Confidence','Hue']:
                    if c in self.__non_so_templates[name]:
                        template[c]=self.__non_so_templates[name][c]
        
        super(TemplatePlotGroupPanel,self).redraw_plots()
    def __init_strength_only_hack(self):
        self.__non_so_templates = copy.deepcopy(self.plotgroup.plot_templates)
    ####################################################################



    ## CB: update init args now we have no pgts.
    def __init__(self,console,master,pg=None,**params):

        super(TemplatePlotGroupPanel,self).__init__(console,master,pg=pg,**params)

        self.pack_param('strength_only',parent=self.control_frame_1,
                        on_change=self.strength_only_fn,side='right')
        self.__init_strength_only_hack()
        
        # To make the auto-refresh button off by default except for
        # the Activity PlotGroup
	if self.plotgroup_label == 'Activity':self.auto_refresh=True


        # Display any plots that can be done with existing data, but
        # don't regenerate the SheetViews
        self.refresh(update=self.plotgroup.plot_immediately)# self.pgt.plot_immediately)



        #################### RIGHT-CLICK MENU STUFF ####################
        self._sheet_menu.add_command(label="Save image",
                                     command=self.__save_to_postscript)

        
        self._unit_menu.add_command(label="Print info",
                                    command=self.__print_info)


        ## Strength channel
        self._strength_menu = Menu(self._canvas_menu, tearoff=0)
        self._canvas_menu.add_cascade(menu=self._strength_menu,label='Strength channel',
                                      indexname="Strength")
        
        ## Hue channel
        self._hue_menu = Menu(self._canvas_menu, tearoff=0)
        self._canvas_menu.add_cascade(menu=self._hue_menu,label='Hue channel',
                                      indexname="Hue")

        ## Confidence channel
        self._conf_menu = Menu(self._canvas_menu, tearoff=0)
        self._canvas_menu.add_cascade(menu=self._conf_menu,label='Confidence channel',
                                      indexname="Confidence")


        # CEBALERT: there doesn't seem to be any way within tkinter itself to let me
        # know which submenu was used! (Hence the repetition.)
        # http://mail.python.org/pipermail/python-list/1999-May/003482.html
        # http://groups.google.com/group/comp.lang.python/browse_thread/thread/de5cf21073610446/7ce05db5dbc4c3f3%237ce05db5dbc4c3f3

        # If the repetition here and elsewhere in this file (and tkgui
        # in general) can't be avoided with loops, there is probably
        # something else, like using a function to return the slightly
        # different versions of the calls.
        #
        # In any case, shouldn't be assuming SHC here.

        # CB: note that I've made Menu indexable by name (in tkguiwindow.py), so can now change this code.

        self._strength_menu.add_command(label="Plot in new window",
                                        command=lambda: self.__plot_matrix('Strength'))
        self._strength_menu.add_command(label="Fourier transform",
                                        command=lambda: self.__fft('Strength'))
        self._strength_menu.add_command(label="Histogram",
                                        command=lambda: self.__histogram('Strength'))
        self._strength_menu.add_command(label="Gradient",
                                        command=lambda: self.__gradient('Strength'))


        self._hue_menu.add_command(label="Plot in new window",
                                   command=lambda: self.__plot_matrix('Hue'))
        self._hue_menu.add_command(label="Fourier transform",
                                   command=lambda: self.__fft('Hue'))
        self._hue_menu.add_command(label="Histogram",
                                        command=lambda: self.__histogram('Hue'))
        self._hue_menu.add_command(label="Gradient",
                                   command=lambda: self.__gradient('Hue'))

        
        self._conf_menu.add_command(label="Plot in new window",
                                    command=lambda: self.__plot_matrix('Confidence'))
        self._conf_menu.add_command(label="Fourier transform",
                                    command=lambda: self.__fft('Confidence'))
        self._conf_menu.add_command(label="Histogram",
                                        command=lambda: self.__histogram('Confidence'))
        self._conf_menu.add_command(label="Gradient",
                                        command=lambda: self.__gradient('Confidence'))


        
        #self._sheet_menu.add_command(label="Print matrix values",
        #                             command=self.__print_matrix)
        #################################################################


##     def generate_plotgroup(self):
##         return self.plotgroup_type()





    ### JABALERT: Should remove the assumption that the plot will be
    ### SHC (could e.g.  be RGB).
    ### 
    ### Should add the ability to turn off any of the channels
    ### independently (just as the Strength-only button does), and
    ### eventually should allow the user to type in the name of any
    ### SheetView to change the template as desired to visualize any
    ### quantity.
    ###
    # CB: something about these methods does not seem to fit the PlotGroup hierarchy.
    def _canvas_right_click(self,event_info):
        """
        Make whichever of the SHC channels is present in the plot available on the menu.
        """
        super(TemplatePlotGroupPanel,self)._canvas_right_click(event_info,show_menu=False)
        
        if 'plot' in event_info:
            plot = event_info['plot']
            
            available_channels =available_plot_channels(plot) 

            for channel in ('Strength','Hue','Confidence'):
                if channel in available_channels:
                    self._canvas_menu.entryconfig(channel,
                                                  label="%s channel: %s" %
                                                  (channel,str(plot.channels[channel])),state=NORMAL)
                else:
                    self._canvas_menu.entryconfig(channel,
                                                  label="%s channel: None" %
                                                  (channel),state=DISABLED)

            self._canvas_menu.tk_popup(event_info['event'].x_root,
                                       event_info['event'].y_root)


     # just about copied from editorwindow.py
    def __save_to_postscript(self):

        canvas = self._right_click_info['event'].widget
        
        POSTSCRIPT_FILETYPES = [('Encapsulated PostScript images','*.eps'),
                                ('PostScript images','*.ps'),('All files','*')]
        snapshot_name = asksaveasfilename(filetypes=POSTSCRIPT_FILETYPES)
        if snapshot_name:
            canvas.postscript(file=snapshot_name)

    # CB: these methods assume channel has a view (the menu only displays those that do)
    def __fft(self,channel):
        plot = self._right_click_info['plot']
        description = "%s %s at time %0.2f" % (plot.plot_src_name, plot.name, topo.sim.time())
        m=plot._get_matrix(channel)
        fft_plot=1-abs(fftshift(fft2(m-0.5, s=None, axes=(-2,-1))))
        topo.commands.pylabplots.matrixplot(fft_plot, title="FFT Plot: " + description)        

    def __histogram(self,channel):
        plot = self._right_click_info['plot']
        description = "%s %s at time %0.2f" % (plot.plot_src_name, plot.name, topo.sim.time())
        m=plot._get_matrix(channel)
        topo.commands.pylabplots.histogramplot(m,title="Histogram: "+ description)

    def __gradient(self,channel):
        plot = self._right_click_info['plot']
        description = "%s %s at time %0.2f" % (plot.plot_src_name, plot.name, topo.sim.time())
        m=plot._get_matrix(channel)
        topo.commands.pylabplots.gradientplot(m,title="Gradient: " + description)

    def __print_matrix(self,channel):
        plot = self._right_click_info['plot']
        description = "%s %s at time %0.2f" % (plot.plot_src_name, plot.name, topo.sim.time())
        print ("#" + description)
        m=plot._get_matrix(channel)
        print m

    def __plot_matrix(self,channel):
        plot = self._right_click_info['plot']
        description = "%s %s at time %0.2f" % (plot.plot_src_name, plot.name, topo.sim.time())
        m=plot._get_matrix(channel)
        topo.commands.pylabplots.matrixplot(m, title=description)

    # CEBALERT: decide if and how to allow any of these functions to be used for getting as many
    # channels' info as possible.
    # e.g. in this one...
    def __print_info(self,channel=None):
        plot = self._right_click_info['plot']
        (r,c),(x,y) = self._right_click_info['coords']
        description ="%s %s, row %d, col %d at time %0.2f: " % (plot.plot_src_name, plot.name, r, c, topo.sim.time())

        channels_info = ""
        if channel is None:
            for channel,name in available_plot_channels(plot).items():
                m=plot._get_matrix(channel)
                channels_info+="%s:%f"%(name,m[r,c])
        else:
            m=plot._get_matrix(channel)
            channels_info+="%s:%f"%(plot.channels[channel],m[r,c])
            
        print "%s %s" % (description, channels_info)





    def _dynamic_info_string(self,event_info,basic_text):
        """
        Also print whatever other channels are there and have views.
        """
        plot = event_info['plot']
        r,c = event_info['coords'][0]
        
        info_string = basic_text

        for channel,channel_name in available_plot_channels(plot).items():
            info_string+=" %s: % 1.3f"%(channel_name,plot._get_matrix(channel)[r,c])
                                        
        return info_string

    



