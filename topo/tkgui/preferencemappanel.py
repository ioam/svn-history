"""
Plot for displaying preference maps.

$Id$
"""
__version__='$Revision $'

### JABALERT!
###
### This file should be combined with BasicPlotPanel and perhaps
### PlotPanel, so that all these plots use the same class by default.
### In each case the class will accept a plotgrouptemplate and look in
### it for a user-editable command used to update the plots, and will
### just call the command and plot whatever comes back from the
### template.
###
### If it does continue to exist, it should probably be renamed to
### FeatureMapPanel.


import Pmw
from Tkinter import StringVar, Frame, YES, LEFT, TOP, RIGHT, X, Message, \
     Entry, Canvas
import plotpanel
import topo.base.registry


### We want to support any featuremap type defined in that file, and
### so import all of them here.
from topo.analysis.featuremap import *


class PreferenceMapPanel(plotpanel.PlotPanel):
    def __init__(self,parent,pengine,console,pgt_name,**config):
        plotpanel.PlotPanel.__init__(self,parent,pengine,console,pgt_name=pgt_name,**config)

        # Plotgroup Template associated
        self.pgt = topo.base.registry.plotgroup_templates[pgt_name]
     
        # Name of the plotgroup to plot
        self.mapname = StringVar()
        self.mapname.set(self.pgt.name)
                
        # Command used to refresh the plot, if any
        self.cmdname = StringVar()
        
        #self.cmdname.set(self.mapcmds[self.mapname.get()])
        self.cmdname.set(self.pgt.command)

        
        params_frame = Frame(master=self)
        params_frame.pack(side=TOP,expand=YES,fill=X)
        Message(params_frame,text="Update command:",aspect=1000).pack(side=LEFT)

        Pmw.ComboBox(params_frame,autoclear=1,history=1,dropdown=1,
                     entry_textvariable=self.cmdname,
                     scrolledlist_items=([self.pgt.command])
                     ).pack(side=LEFT,expand=YES,fill=X)


        self.refresh()

        # To make the auto-refresh button not on by default when opening the panel
        self.auto_refresh_checkbutton.invoke()

    def do_plot_cmd(self):
        """
        Function that generates the plot for the panel.

        When the panel is first created or refreshed, the specified
        command is executed, then the plot is generated using the
        specified PlotGroupTemplate.
        """
 
        exec self.cmdname.get()
        pgt = topo.base.registry.plotgroup_templates[self.mapname.get()]
        self.pe_group = self.pe.get_plot_group(self.mapname.get(),pgt)
        self.pe_group.do_plot_cmd()

            
    def display_labels(self):
        """
        Change the title of the grid group by refreshing the time simulator,
        then call PlotPanel's display_labels().
        """
        self.plot_group.configure(tag_text = self.mapname.get() + \
                                  ' at time ' + str(self.pe.simulation.time()))
        super(PreferenceMapPanel,self).display_labels()


    def refresh_title(self):
        self.parent.title(self.mapname.get() + " time:%s" % (self.pe.simulation.time()))
