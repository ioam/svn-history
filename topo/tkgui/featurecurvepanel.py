"""
class FeatureCurvePanel and FullFieldFeatureCurvePanel

Panel for displaying tuning curves.

Uses a PlotGroup to generate the pylab plots 
which are currently displayed separately from the gui.

$Id$
"""
__version__='$Revision$'

from Tkinter import Label

import topo

from topo.base.projection import ProjectionSheet

from topo.plotting.plotgroup import FeatureCurvePlotGroup

from plotgrouppanel import PlotGroupPanel
from tkparameterizedobject import ButtonParameter


## CEBALERT: same as for featurecurveplotgroup: shares code with templateplotgrouppanel
# Should be changed to inherit from UnitPGPanel, or whatever is created to handle the PlotGroup
# hierarchy.
class FeatureCurvePanel(PlotGroupPanel):

    plotgroup_type = FeatureCurvePlotGroup


    # CEBHACKALERT: to which types of sheet is this plotgroup supposed to be applicable?
    # Also applies to populate_sheet_param() below.
    @staticmethod
    def valid_context():
        """
        Return true if there appears to be data available for this type of plot.

        To avoid confusing error messages, this method should be
        defined to return False in the case where there is no
        appropriate data to plot.  This information can be used to,
        e.g., gray out the appropriate menu item.
        By default, PlotPanels are assumed to be valid only for
        simulations that contain at least one Sheet.  Subclasses with
        more specific requirements should override this method with
        something more appropriate.
        """
        if topo.sim.objects(ProjectionSheet).items():
            return True
        else:
            return False


    def __init__(self,console,master,pg=None,**params):       
	PlotGroupPanel.__init__(self,console,master,pg=pg,**params)

        self.pack_param("sheet",parent=self.control_frame_3,on_change=self.sheet_change,
                        widget_options={'sort_fn_args':
                                        {'cmp':lambda x, y: cmp(-x.precedence,-y.precedence)}})


        self.pack_param("x",parent=self.control_frame_3)
        self.pack_param("y",parent=self.control_frame_3)

        # remove currently irrelevant widgets (plots are drawn in a separate window by pylab)
        # CEBNOTE: when plots are in this window, remove this line.
        for name in ['Enlarge','Reduce','Back','Fwd']: self.hide_param(name)

        self.auto_refresh= False
        if self.plotgroup.plot_immediately: self.refresh()

        self.display_note()


##############################################################################
        self.sheet_change()
    def sheet_change(self):

        s = self.sheet
        l,b,r,t = s.bounds.lbrt()

        x = self.get_parameter_object('x')
        y = self.get_parameter_object('y')

        x.bounds=(l,r)
        y.bounds=(b,t)

        self.x = 0.0
        self.y = 0.0

        if 'x' and 'y' in self.representations:
            w1,w2=self.representations['x']['widget'],self.representations['y']['widget']
            w1.set_bounds(*x.bounds)
            w2.set_bounds(*y.bounds)
            
            w1.refresh();w2.refresh()
##############################################################################


    def populate_sheet_param(self,p):
        sheets = topo.sim.objects(ProjectionSheet).values() 
        p.params()['sheet'].Arange = sheets
        p.sheet = sheets[0] # CB: necessary?


    def generate_plotgroup(self,pg=None):
        """
        Create the right Plot Key that will define the needed
        information for a FeatureCurvePlotGroup. 
        """
        p = pg or self.plotgroup_type()
        self.populate_sheet_param(p)
	return p

    def _plot_title(self):
        # CEBHACKALERT: str()  (shouldn't lanbl be string already?)
        return str(self.plotgroup_label)+' at time ' + str(self.plotgroup.time)


    def display_labels(self):
        """plots are displayed in new windows, so don't add any labels"""
        pass


    def display_note(self):
        self.plot_labels=[Label(self.plot_frame,text="""
                        (Press Refresh on the update command to
                        generate the plot, after modifying the
                        commands below if necessary.  Refreshing may
                        take some time.  Note that plots currently
                        open in new windows.
                        
                        Many commands accept 'display=True' so that
                        the progress can be viewed in an open Activity
                        window, e.g. for debugging.)""")]
        self.plot_labels[0].grid(row=1,column=0,sticky='nsew')
        self.window_master.sizeright()






