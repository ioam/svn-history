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

import copy
import Pmw
from Tkinter import StringVar, Frame, YES, LEFT, TOP, RIGHT, X, Message, \
     Entry, Canvas, Checkbutton, BooleanVar, Menu

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


class TemplatePlotGroupPanel(PlotGroupPanel):
    def __init__(self,parent,console,pgt_name,**params):
        # Plotgroup Template associated
        self.pgt = plotgroup_templates.get(pgt_name,None)

	# Strength only check button
	self.strengthonly = BooleanVar()
	self.strengthonly.set(False)

	PlotGroupPanel.__init__(self,parent,console,pgt_name,**params)

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
        params_frame.pack(side=TOP,expand=YES,fill=X)
        cmdlabel = Message(params_frame,text="Update command:",aspect=1000)
        cmdlabel.pack(side=LEFT)
        self.balloon.bind(cmdlabel,getdoc(self.plotgroup.params()['updatecommand']))
        
        cmdbox = Pmw.ComboBox(params_frame,autoclear=1,history=1,dropdown=1,
                              entry_textvariable=self.cmdname,
                              scrolledlist_items=([self.cmdname.get()]))
        cmdbox.pack(side=LEFT,expand=YES,fill=X)
        self.balloon.bind(cmdbox,getdoc(self.plotgroup.params()['updatecommand']))
       
        # To make the auto-refresh button off by default except for
        # the Activity PlotGroup
	if self.mapname.get() == 'Activity':
	    self.auto_refresh.set(True)
            self.set_auto_refresh()

        # Display any plots that can be done with existing data, but
        # don't regenerate the SheetViews
        if self.__class__ == TemplatePlotGroupPanel:
            self.refresh(update=self.pgt.plot_immediately)

        sheet_menu = Menu(self)
        sheet_menu.insert_command(2,label="plot ft",command=self.__fft)
        sheet_menu.insert_command(1,label="print matrix values",command=self.__print_matrix)
        sheet_menu.insert_command(0,label="plot in new window",command=self.__plot_matrix)

        unit_menu = Menu(self)
        unit_menu.insert_command(0,label="print info",command=self.__print_info)

        self._canvas_menu.entryconfig(0,menu=unit_menu)
        self._canvas_menu.entryconfig(1,menu=sheet_menu)


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

    # JABALERT: Should change these commands to be part of submenus
    # for Strength, Hue, etc., instead of checking it here.
    def __fft(self):
        plot = self._canvas_click_info[0]
        description = "%s %s at time %0.2f" % (plot.plot_src_name, plot.name, topo.sim.time())
        if plot.channels.has_key('Strength'):
            m=plot._get_matrix('Strength')
        elif plot.channels.has_key('Hue'):
            m=plot._get_matrix('Hue')
        fft_plot=fftshift(fft2(m-0.5, s=None, axes=(-2,-1)))
        topo.commands.pylabplots.matrixplot(fft_plot, title="FFT Plot: " + description)        

    def __print_matrix(self):
        plot = self._canvas_click_info[0]
        description = "%s %s at time %0.2f" % (plot.plot_src_name, plot.name, topo.sim.time())
        print ("#" + description)
        if plot.channels.has_key('Strength'):
            m=plot._get_matrix('Strength')
        elif plot.channels.has_key('Hue'):
            m=plot._get_matrix('Hue')
        print m


    def __plot_matrix(self):
        plot = self._canvas_click_info[0]
        description = "%s %s at time %0.2f" % (plot.plot_src_name, plot.name, topo.sim.time())
        if plot.channels.has_key('Strength'):
            m=plot._get_matrix('Strength')
        elif plot.channels.has_key('Hue'):
            m=plot._get_matrix('Hue')
        topo.commands.pylabplots.matrixplot(m, title=description)


    def __print_info(self):
        plot,r,c,x,y = self._canvas_click_info
        description ="%s %s, row %d, col %d at time %0.2f: " % (plot.plot_src_name, plot.name, r, c, topo.sim.time())
        if plot.channels.has_key('Strength'):
            m=plot._get_matrix('Strength')
        elif plot.channels.has_key('Hue'):
            m=plot._get_matrix('Hue')
        print "%s %f" % (description, m[r,c])


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
        self.parent.title(topo.sim.name+': '+self.mapname.get() + " time:%s" % self.plotgroup.time)
