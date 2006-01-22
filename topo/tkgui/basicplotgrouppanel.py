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
from topo.plotting.plotgroup import plotgroup_dict, BasicPlotGroup

### We want to support any featuremap type defined in that file, and
### so import all of them here.
from topo.commands.analysis import *


### JCALERT! Get rid of the pengine parameter.
class BasicPlotGroupPanel(plotgrouppanel.PlotGroupPanel):
    def __init__(self,parent,console,pgt_name,**config):
        plotgrouppanel.PlotGroupPanel.__init__(self,parent,console,pgt_name=pgt_name,**config)

        # Plotgroup Template associated
        self.pgt = plotgroup_templates[pgt_name]
     
        # Command used to refresh the plot, if any
        self.cmdname = StringVar()
        
        self.cmdname.set(self.pgt.command)

	### JCALERT! We might get rid of that, as it is redundant with plotgroup_key
        self.mapname = StringVar()       
        self.mapname.set(self.pgt.name)

	# For a BasicPlotGroup, the plot_group_key is the name of the template
	self.plot_group_key=self.pgt.name
        
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
 
        exec self.cmdname.get()

	self.pe_group = plotgroup_dict.get(self.plot_group_key,None)
	if self.pe_group == None:
	    self.pe_group = BasicPlotGroup(self.console.simulator,self.pgt,self.plot_group_key,
					   None,[])

            
    def display_labels(self):
        """
        Change the title of the grid group by refreshing the time simulator,
        then call PlotGroupPanel's display_labels().
        """
        self.plot_group.configure(tag_text = self.mapname.get() + \
                                  ' at time ' + str(self.console.simulator.time()))
        super(BasicPlotGroupPanel,self).display_labels()


    def refresh_title(self):
        self.parent.title(self.mapname.get() + " time:%s" % (self.console.simulator.time()))
