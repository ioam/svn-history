"""
Plot that measures preference maps.  Should be designed so that other
types of HSV based plots can be created either by using this or
extending it.

$Id$
"""

from Tkinter import StringVar, Frame, YES, LEFT, TOP, RIGHT, X, Message, \
     Entry, Canvas
import plotpanel
import Pmw
from topo.plotting.plot import PlotTemplate
from topo.plotting.plotgroup import PlotGroupTemplate
from topo.plotting.bitmap import WHITE_BACKGROUND, BLACK_BACKGROUND
import topo.base.registry

### We want to support any featuremap type defined in that file, and so import all of them here.
from topo.analysis.featuremap import *

### JABHACKALERT: This class fully supports only Orientation Preferences plots
### at present, and needs to be cleaned up a bit to work in general.
### E.g. it probably shouldn't have the mapname ComboBox, and should instead
### use the name from the pgt_name that it was called with.
class PreferenceMapPanel(plotpanel.PlotPanel):
    def __init__(self,parent,pengine=None,console=None,plot_key='Activity',map_name='Orientation Preference',**config):
        plotpanel.PlotPanel.__init__(self,parent,pengine,console=console,plot_key=plot_key,pgt_name=map_name,**config)

        self.panel_num = self.console.num_orientation_windows

        self.pgt = topo.base.registry.plotgroup_templates[map_name]
        #self.mapcmds = dict((('Orientation Preference',      'measure_or_pref()'),
        #                     ('Ocular Preference',           'pass')))

        # Name of the plotgroup to plot
        self.mapname = StringVar()

        #self.mapname.set('Orientation Preference')
        self.mapname.set(self.pgt.name)
        
        
        
        # lissom command used to refresh the plot, if any
        self.cmdname = StringVar()
        
        #self.cmdname.set(self.mapcmds[self.mapname.get()])
        self.cmdname.set(self.pgt.command)

        
        params_frame = Frame(master=self)
        params_frame.pack(side=TOP,expand=YES,fill=X)
        
        #Pmw.ComboBox(params_frame,autoclear=1,history=1,dropdown=1,
        #             entry_textvariable=self.mapname,
        #             scrolledlist_items=(['Orientation Preference'])
        #             ).pack(side=LEFT,expand=YES,fill=X)
        ### There was 'Ocular Preference' in the list before, but does not work yet

        # Ideally, whenever self.mapname changes this selection would be 
        # updated automatically by looking in self.mapcmds.  However, I 
        # don't know how to set up such a callback. (jbednar@cs)
        Pmw.ComboBox(params_frame,autoclear=1,history=1,dropdown=1,
                     entry_textvariable=self.cmdname,
                     scrolledlist_items=([self.pgt.command])
                     ).pack(side=LEFT,expand=YES,fill=X)

        #Pmw.ComboBox(params_frame,autoclear=1,history=1,dropdown=1,
        #             entry_textvariable=self.cmdname,
        #             scrolledlist_items=(['measure_or_pref()'])
        #             ).pack(side=LEFT,expand=YES,fill=X)


        self.refresh()
        self.auto_refresh_checkbutton.invoke()

        ### JCHACKALERT! Rewrites that so it returns the appropriate plot keys 
    def generate_plot_key(self):
        """
        Key Format:  Tuple: (Color name, Strength name, Confidence name)
        """
        # g = __main__.__dict__
        # ep = [ep for ep in self.console.active_simulator().get_event_processors()
        #       if ep.name == self.region.get()][0]
        # # This assumes that displaying the rectangle information is enough.
        # l,b,r,t = ep.bounds.aarect().lbrt()
        self.plot_key = ('Activity','Activity','Activity')


    ### JABHACKALERT!
    ### 
    ### This function needs to be fixed and/or documented; the old
    ### documentation was incorrect (copied from another file).
    def do_plot_cmd(self):
        """
        Needs fixing.
        """
        if self.console.active_simulator().get_event_processors():

            ## to fix so that it executes the command that have been typed instead of
            ## at the moment it will only execute measure_or_pref()
            exec self.cmdname.get()
            pgt = topo.base.registry.plotgroup_templates[self.mapname.get()]
            self.pe_group = self.pe.get_plot_group(self.mapname.get(),pgt)
            self.pe_group.do_plot_cmd()

            
            

    def display_labels(self):
        """
        Change the title of the grid group, then call PlotPanel's
        display_labels().
        """
        self.plot_group.configure(tag_text = self.mapname.get())
        super(PreferenceMapPanel,self).display_labels()


    def refresh_title(self):
        self.parent.title(self.mapname.get() + " %d." % self.panel_num)
