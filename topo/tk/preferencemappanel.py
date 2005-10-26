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

### JAB: This class is not currently useful; it will need to be revisited once
### preference maps can be measured.
class PreferenceMapPanel(plotpanel.PlotPanel):
    def __init__(self,parent,pengine=None,console=None,plot_key='Activity',**config):
        plotpanel.PlotPanel.__init__(self,parent,pengine,console=console,plot_key=plot_key,pgt_name='Preference',**config)

        self.panel_num = self.console.num_orientation_windows
        
        self.mapcmds = dict((('Orientation Preference',      'measure_or_pref()'),
                             ('Ocular Preference',           'pass')))

        # Name of the plotgroup to plot
        self.mapname = StringVar()
        self.mapname.set('Orientation Preference')
        
        # lissom command used to refresh the plot, if any
        self.cmdname = StringVar()
        self.cmdname.set(self.mapcmds[self.mapname.get()])
        
        params_frame = Frame(master=self)
        params_frame.pack(side=TOP,expand=YES,fill=X)
        
        Pmw.ComboBox(params_frame,autoclear=1,history=1,dropdown=1,
                     entry_textvariable=self.mapname,
                     scrolledlist_items=('Orientation Preference',
                                         'Ocular Preference')
                     ).pack(side=LEFT,expand=YES,fill=X)

        # Ideally, whenever self.mapname changes this selection would be 
        # updated automatically by looking in self.mapcmds.  However, I 
        # don't know how to set up such a callback. (jbednar@cs)
        Pmw.ComboBox(params_frame,autoclear=1,history=1,dropdown=1,
                     entry_textvariable=self.cmdname,
                     scrolledlist_items=('measure_or_pref()')
                     ).pack(side=LEFT,expand=YES,fill=X)

        self.refresh()


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
            print 'mapname', self.mapname.get()
            pgt = topo.base.registry.plotgroup_templates[self.mapname.get()]
            print 'pgt',pgt
            self.pe_group = self.pe.get_plot_group(self.mapname.get(),pgt)
            self.pe_group.do_plot_cmd()
            

    def display_labels(self):
        """
        Change the title of the grid group, then call PlotPanel's
        display_labels().
        """
        self.plot_group.configure(tag_text = 'Preference Map')
        super(PreferenceMapPanel,self).display_labels()


    def refresh_title(self):
        self.parent.title("Preference Map %d." % self.panel_num)
