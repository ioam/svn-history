"""
class TemplatePlotGroupPanel
Panel for displaying preference maps and activity plot groups.

$Id$
"""
__version__='$Revision$'


import Pmw
from Tkinter import StringVar, Frame, YES, LEFT, TOP, RIGHT, X, Message, \
     Entry, Canvas, Checkbutton

import plotgrouppanel
from topo.plotting.templates import plotgroup_templates
from topo.plotting.plotgroup import plotgroup_dict, TemplatePlotGroup

### We want to support any featuremap type defined in that file, and
### so import all of them here.
import matplotlib
matplotlib.use('TkAgg')

### JABALERT: Should change this to discover and import all the
### commands/*.py files automatically
from topo.commands.analysis import *
from topo.commands.basic import *
from topo.commands.pylabplots import *


class TemplatePlotGroupPanel(plotgrouppanel.PlotGroupPanel):
    def __init__(self,parent,console,pgt_name,**config):
        plotgrouppanel.PlotGroupPanel.__init__(self,parent,console,pgt_name,**config)

        # Plotgroup Template associated
        self.pgt = plotgroup_templates[pgt_name]
     
        # Command used to refresh the plot, if any
        self.cmdname = StringVar()
        
        self.cmdname.set(self.pgt.command)

	### JCALERT! We might get rid of that, as it is redundant with plotgroup_key
        self.mapname = StringVar()       
        self.mapname.set(self.pgt.name)

        self.actualsize_checkbutton = Checkbutton(self.shared_control_frame,
                                                    text="Actualsize",
                                                    command=self.toggle_actualsize)
        self.actualsize_checkbutton.pack(side=LEFT)

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
	    ### JCALERT! Maybe if the template specified a PlotGroup, we could
            ### take the one that is specified.
            ### Otherwise, we could assume that each panel is associated with a PlotGroup
            ### and then specify a panel for each template. (as it is done from topoconsole)
	    self.pe_group = TemplatePlotGroup(self.plot_group_key,[],self.normalize,
					      self.pgt,None)

            
    def display_labels(self):
        """
        Change the title of the grid group by refreshing the time simulator,
        then call PlotGroupPanel's display_labels().
        """
        self.plot_group_title.configure(tag_text = self.mapname.get() + \
                                  ' at time ' + str(self.console.simulator.time()))
        super(TemplatePlotGroupPanel,self).display_labels()


    def refresh_title(self):
        self.parent.title(topo.sim.name+': '+self.mapname.get() + " time:%s" % (topo.sim.time()))
