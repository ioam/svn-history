"""
class BasicPlotGroupPanel
Panel for displaying preference maps and activity plot groups.

$Id$
"""
__version__='$Revision$'


### JCALERT! Now BasicPlotGroupPanel replace the former BasicPlotPanel and PreferenceMapPanel
### As well PlotPanel is now PlotGroupPanel.
### It remains to: - change the name of plotpanel.py to plotgrouppanel.py 
###                - change the name of preferencemappanel.py to basicplotgrouppanel.py
###                - change the import statements in any files using this two files
###                - write a command for the activity panel to put in the scrolled-list 
###                  (e.g. measure_activity(), it is pass for the moment )  

import Pmw
from Tkinter import StringVar, Frame, YES, LEFT, TOP, RIGHT, X, Message, \
     Entry, Canvas
import plotgrouppanel
from topo.plotting.templates import plotgroup_templates

### We want to support any featuremap type defined in that file, and
### so import all of them here.
from topo.analysis.updatecommands import *


class BasicPlotGroupPanel(plotgrouppanel.PlotGroupPanel):
    def __init__(self,parent,pengine,console,pgt_name,**config):
        plotgrouppanel.PlotGroupPanel.__init__(self,parent,pengine,console,pgt_name=pgt_name,**config)

        # Plotgroup Template associated
        self.pgt = plotgroup_templates[pgt_name]
     
        # Name of the plotgroup to plot
        self.mapname = StringVar()
        self.mapname.set(self.pgt.name)
                
        # Command used to refresh the plot, if any
        self.cmdname = StringVar()
        
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
        # but it is not the case for the Activity PlotGroup
	if self.mapname.get() != 'Activity':
	    self.auto_refresh_checkbutton.invoke()

    def do_plot_cmd(self):
        """
        Function that generates the plot for the panel.

        When the panel is first created or refreshed, the specified
        command is executed, then the plot is generated using the
        specified PlotGroupTemplate.
        """
 
	### JCALERT! That could replace the call to pe_group.do_plot_cmd gor 
        ### UnitWeight and Projection Panel...
        exec self.cmdname.get()
        pgt = plotgroup_templates[self.mapname.get()]
        self.pe_group = self.pe.get_plot_group(self.mapname.get(),pgt,class_type='BasicPlotGroup')

            
    def display_labels(self):
        """
        Change the title of the grid group by refreshing the time simulator,
        then call PlotGroupPanel's display_labels().
        """
        self.plot_group.configure(tag_text = self.mapname.get() + \
                                  ' at time ' + str(self.pe.simulation.time()))
        super(BasicPlotGroupPanel,self).display_labels()


    def refresh_title(self):
        self.parent.title(self.mapname.get() + " time:%s" % (self.pe.simulation.time()))
