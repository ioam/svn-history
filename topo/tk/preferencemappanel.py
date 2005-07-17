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
from topo.plot import SCCPlot
from topo.plotgroup import PreferenceMapPlotGroup
     
class PreferenceMapPanel(plotpanel.PlotPanel):
    def __init__(self,parent,pengine=None,console=None,plot_key='Activation',**config):
        plotpanel.PlotPanel.__init__(self,parent,pengine,console=console,plot_key=plot_key,**config)

        self.panel_num = self.console.num_orientation_windows
        
        self.mapcmds = dict((('OrientationPreference',      'call measure_or_pref '),
                             ('OcularPreference',           'call measure_or_pref'),
                             ('DirectionPreference',        'call measure_dir_pref'),
                             ('PositionPreference',         'call measure_cog'),
                             ('SpatialFrequencyPreference', 'call measure_or_pref'),
                             ('SpatialPhasePreference',     'call measure_or_pref'),
                             ('SpeedPreference',            'call measure_dir_pref')))

        # Name of the plotgroup to plot
        self.mapname = StringVar()
        self.mapname.set('OrientationPreference')

        # lissom command used to refresh the plot, if any
        self.cmdname = StringVar()
        self.cmdname.set(self.mapcmds[self.mapname.get()])
        
        params_frame = Frame(master=self)
        params_frame.pack(side=TOP,expand=YES,fill=X)
        
        Pmw.ComboBox(params_frame,autoclear=1,history=1,dropdown=1,
                     entry_textvariable=self.mapname,
                     scrolledlist_items=('OrientationPreference',
                                         'OcularPreference',
                                         'DirectionPreference',
                                         'PositionPreference',
                                         'SpatialFrequencyPreference',
#                                        'SpatialPhasePreference',
                                         'SpeedPreference')
                     ).pack(side=LEFT,expand=YES,fill=X)

        # Ideally, whenever self.mapname changes this selection would be 
        # updated automatically by looking in self.mapcmds.  However, I 
        # don't know how to set up such a callback. (jbednar@cs)
        Pmw.ComboBox(params_frame,autoclear=1,history=1,dropdown=1,
                     entry_textvariable=self.cmdname,
                     scrolledlist_items=('call measure_or_pref',
                                         'call measure_od_pref',
                                         'call measure_dir_pref',
                                         'call measure_cog')
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
        self.plot_key = ('Activation','Activation','Activation')



    def do_plot_cmd(self):
        """
        Create the right Plot Key that will define the needed
        information for a WeightsPlotGroup.  This is the key-word
        'Weights', and the necessary x,y coordinate.  Once the
        PlotGroup is created, and call its do_plot_cmd() to prepare
        the Plot objects.
        """
        if self.console.active_simulator().get_event_processors():
            self.generate_plot_key()

            # This is what should be done once the plot engine can
            # handle three-color plots.
            # self.pe_group = self.pe.get_plot_group(self.plot_key,
            #                                        'PreferenceMapPlotGroup')
            #                                        # self.region.get())
            #                                        # No filter
            # self.pe_group.do_plot_cmd()

            all_sheets = self.console.active_simulator().get_event_processors()
            print 'all_sheets', all_sheets
            plotlist = [SCCPlot(('Activation','Activation','Activation'),
                                sheet=each)
                        for each in all_sheets]
            print plotlist
            self.pe_group = PreferenceMapPlotGroup('None',None,plotlist)
            self.plots = self.pe_group.plots()

    def display_labels(self):
        """
        Change the title of the grid group, then call PlotPanel's
        display_labels().
        """
        self.plot_group.configure(tag_text = 'Preference Map')
        super(PreferenceMapPanel,self).display_labels()


    def refresh_title(self):
        self.parent.title("Preference Map Panel %d." % self.panel_num)
