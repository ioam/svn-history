"""
class TemplatePlotGroupPanel
Panel for displaying preference maps and activity plot groups.

$Id$
"""
__version__='$Revision$'

from inspect import getdoc

import Pmw
from Tkinter import StringVar, Frame, YES, LEFT, TOP, RIGHT, X, Message, \
     Entry, Canvas, Checkbutton

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

	PlotGroupPanel.__init__(self,parent,console,pgt_name,**params)

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
                              scrolledlist_items=([self.cmdname]))
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
	plotgroup = TemplatePlotGroup([],self.pgt,None,
                                      normalize=self.normalize.get(),
				      sheetcoords=self.sheetcoords.get(),
                                      integerscaling=self.integerscaling.get())
	return plotgroup

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
