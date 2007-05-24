"""
class TemplatePlotGroupPanel
Panel for displaying preference maps and activity plot groups.

$Id$
"""
__version__='$Revision$'

# CEBALERT: on orienation full field plot, there's no text telling you
# to click refresh. (Not the right place for this alert!)


from inspect import getdoc
from math import pi
from numpy.fft.fftpack import fft2
from numpy.fft.helper import fftshift
from numpy import abs

import copy
import Pmw
from Tkinter import StringVar, Frame, YES, LEFT, TOP, RIGHT, X, Message, \
     Entry, Canvas, Checkbutton, BooleanVar, Menu, DISABLED, NORMAL,NO

import topo
from plotgrouppanel import PlotGroupPanel
from topo.plotting.templates import plotgroup_templates
from topo.plotting.plotgroup import TemplatePlotGroup

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



class TemplatePlotGroupPanel(PlotGroupPanel):
    def __init__(self,console,pgt_name,**params):
        # Plotgroup Template associated
        self.pgt = plotgroup_templates.get(pgt_name,None)

	# Strength only check button
        # CEBHACKALERT: not among the buttons disabled when in the history!
        # Means update_back_fwd... has to be overridden in this class, too.
        # But there's a note saying that method's temporary and needs to be
        # removed...
	self.strengthonly = BooleanVar()
	self.strengthonly.set(False)

	PlotGroupPanel.__init__(self,console,pgt_name,**params)

	self.strengthonly_checkbutton = Checkbutton(self.control_frame_1,
             text="Strength only",variable=self.strengthonly,command=self.set_strengthonly)
	self.strengthonly_checkbutton.pack(side=RIGHT)
        self.balloon.bind(self.strengthonly_checkbutton,
"""If true, disables all but the Strength channel of each plot,
disabling all color coding for Strength/Hue/Confidence plots.""")

	self.normalize.set(self.pgt.normalize)
        self.plotgroup.normalize=self.normalize.get()

        # Command used to refresh the plot, if any
        self.cmdname = StringVar()
	self.cmdname.set(self.plotgroup.updatecommand)

	### JCALERT! We might get rid of that, as it is redundant with plotgroup_key
        self.mapname = StringVar()       
        self.mapname.set(self.pgt.name)
        
	# For a BasicPlotGroup, the plotgroup_key is the name of the template
	self.plotgroup_key=self.pgt.name
        
        params_frame = Frame(master=self)
        params_frame.pack(side=TOP,expand=NO,fill=X)
        cmdlabel = Message(params_frame,text="Update command:",aspect=1000)
        cmdlabel.pack(side=LEFT,expand=NO,fill=X)
        self.balloon.bind(cmdlabel,getdoc(self.plotgroup.params()['updatecommand']))
        
        cmdbox = Pmw.ComboBox(params_frame,autoclear=1,history=1,dropdown=1,
                              entry_textvariable=self.cmdname,
                              selectioncommand=self.refresh,
                              scrolledlist_items=([self.cmdname.get()]))
        cmdbox.pack(side=LEFT,expand=YES,fill=X)
        self.balloon.bind(cmdbox,getdoc(self.plotgroup.params()['updatecommand']))
       
        # To make the auto-refresh button off by default except for
        # the Activity PlotGroup
	if self.mapname.get() == 'Activity':
	    self.auto_refresh_var.set(True)
            self.set_auto_refresh()

        # Display any plots that can be done with existing data, but
        # don't regenerate the SheetViews
        if self.__class__ == TemplatePlotGroupPanel:
            self.refresh(update=self.pgt.plot_immediately)


        self._sheet_menu.add_command(label="Save image",
                                     state=DISABLED)

        
        self._unit_menu.add_command(label="Print info",
                                    command=self.__print_info)



        # CEBALERT: do we have to index with numbers? It will get
        # messy if we want to add something in the middle...and it's
        # already a pain for accessing the items.

        ## Strength channel
        self._canvas_menu.insert_cascade(2) 
        self._strength_menu = Menu(self._canvas_menu, tearoff=0)
        self._canvas_menu.entryconfig(2,menu=self._strength_menu,label='Strength channel')
        
        ## Hue channel
        self._canvas_menu.insert_cascade(3) 
        self._hue_menu = Menu(self._canvas_menu, tearoff=0)
        self._canvas_menu.entryconfig(3,menu=self._hue_menu,label='Hue channel')

        ## Confidence channel
        self._canvas_menu.insert_cascade(4) 
        self._conf_menu = Menu(self._canvas_menu, tearoff=0)
        self._canvas_menu.entryconfig(4,menu=self._conf_menu,label='Confidence channel')


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
        

    def _pg_template(self):
        """
        Function that returns the plotgroup_template for this panel,
        after first stripping non-strength plots if necessary
        """
        # Strip Hue and Confidence if strengthonly is set
        if self.strengthonly.get() == False:
            return self.pgt
        else:
            pgt = copy.deepcopy(self.pgt)
            for name,template in pgt.plot_templates:
                if template.has_key('Hue'):
                    del template['Hue']
                if template.has_key('Confidence'):
                    del template['Confidence']
            return pgt
        
    def generate_plotgroup(self):
        """
        Function that generates the plot for the panel.

        When the panel is first created or refreshed, the specified
        command is executed, then the plot is generated using the
        specified PlotGroupTemplate.
        """
        ### JCALERT! Maybe if the template specified a PlotGroup, we could
        ### take the one that is specified.
        ### Otherwise, we could assume that each panel is associated with a PlotGroup
        ### and then specify a panel for each template. (as it is done from topoconsole)
	plotgroup = TemplatePlotGroup([],self._pg_template(),None,
                                      normalize=self.normalize.get(),
				      sheetcoords=self.sheetcoords.get(),
                                      integerscaling=self.integerscaling.get())

        
	return plotgroup

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

            for channel,menu_posn in zip(('Strength','Hue','Confidence'),(2,3,4)):
                if channel in available_channels:
                    self._canvas_menu.entryconfig(menu_posn,label="%s channel: %s" %
                                                  (channel,str(plot.channels[channel])),state=NORMAL)
                else:
                    self._canvas_menu.entryconfig(menu_posn,label="%s channel: None" %
                                                  (channel),state=DISABLED)

            self._canvas_menu.tk_popup(event_info['event'].x_root,
                                       event_info['event'].y_root)

 

        

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



    def set_strengthonly(self):
        """Function called by Widget when check-box clicked"""
	self.plotgroup=self.generate_plotgroup()
        self.refresh(update=False)
	self.plotgroup.update_plots(False)
        self.display_plots()
        self.display_labels()

        
    def update_plotgroup_variables(self):
        self.plotgroup.updatecommand = self.cmdname.get()
 
    def display_labels(self):
        """
        Change the title of the grid group by refreshing the simulated time,
        then call PlotGroupPanel's display_labels().
        """
        self.plot_group_title.configure(tag_text = self.mapname.get() + \
                                  ' at time ' + str(self.plotgroup.time))
        super(TemplatePlotGroupPanel,self).display_labels()


    def refresh_title(self):
        self.title(topo.sim.name+': '+self.mapname.get() + " time:%s" % self.plotgroup.time)


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




### CB: I'm working here at the moment.

class TemplatePlotGroupPanel2(PlotGroupPanel):
    def __init__(self,console,pgt_name,master,**params):

        self.pgt_name = pgt_name
        self.pgt=plotgroup_templates[pgt_name]

        PlotGroupPanel.__init__(self,console,pgt_name,master, **params)


        self.pack_param('strength_only',parent=self.control_frame_1,
                        on_change=self.update_plots,side='right')

        self.pack_param('updatecommand')

               
        # To make the auto-refresh button off by default except for
        # the Activity PlotGroup
	if self.plotgroup_label == 'Activity':self.trial.set_param('auto_refresh',True)


        # Display any plots that can be done with existing data, but
        # don't regenerate the SheetViews
        if self.__class__ == TemplatePlotGroupPanel: # shen me?
            self.refresh(update=self.pgt.plot_immediately)




        #################### RIGHT-CLICK MENU STUFF ####################
        self._sheet_menu.add_command(label="Save image",
                                     state=DISABLED)
        
        self._unit_menu.add_command(label="Print info",
                                    command=self.__print_info)

        # CEBALERT: do we have to index with numbers? It will get
        # messy if we want to add something in the middle...and it's
        # already a pain for accessing the items.

        ## Strength channel
        self._canvas_menu.insert_cascade(2) 
        self._strength_menu = Menu(self._canvas_menu, tearoff=0)
        self._canvas_menu.entryconfig(2,menu=self._strength_menu,label='Strength channel')
        
        ## Hue channel
        self._canvas_menu.insert_cascade(3) 
        self._hue_menu = Menu(self._canvas_menu, tearoff=0)
        self._canvas_menu.entryconfig(3,menu=self._hue_menu,label='Hue channel')

        ## Confidence channel
        self._canvas_menu.insert_cascade(4) 
        self._conf_menu = Menu(self._canvas_menu, tearoff=0)
        self._canvas_menu.entryconfig(4,menu=self._conf_menu,label='Confidence channel')


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
        
        

    def generate_plotgroup(self):
        return TemplatePlotGroup([],self.pgt,None)


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

            for channel,menu_posn in zip(('Strength','Hue','Confidence'),(2,3,4)):
                if channel in available_channels:
                    self._canvas_menu.entryconfig(menu_posn,label="%s channel: %s" %
                                                  (channel,str(plot.channels[channel])),state=NORMAL)
                else:
                    self._canvas_menu.entryconfig(menu_posn,label="%s channel: None" %
                                                  (channel),state=DISABLED)

            self._canvas_menu.tk_popup(event_info['event'].x_root,
                                       event_info['event'].y_root)

 

        

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


 
    def display_labels(self):
        """
        Change the title of the grid group by refreshing the simulated time,
        then call PlotGroupPanel's display_labels().
        """
        self.plot_group_title.configure(tag_text = self.plotgroup_label + \
                                  ' at time ' + str(self.plotgroup.time))
        super(TemplatePlotGroupPanel,self).display_labels()


    def refresh_title(self):
        self.title(topo.sim.name+': '+self.plotgroup_label + " time:%s" % self.plotgroup.time)


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

    


#TemplatePlotGroupPanel = TemplatePlotGroupPanel2
