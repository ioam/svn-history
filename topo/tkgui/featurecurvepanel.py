"""
class FeatureCurvePanel and FullFieldFeatureCurvePanel

Panel for displaying tuning curves.

Uses a PlotGroup to generate the pylab plots 
which are currently displayed separately from the gui.

$Id$
"""
__version__='$Revision$'


import topo

from topo.base.projection import ProjectionSheet

from topo.plotting.plotgroup import FeatureCurvePlotGroup

from plotgrouppanel import PlotGroupPanel
from tkparameterizedobject import ButtonParameter


## CEBALERT: same as for featurecurveplotgroup: shares code with templateplotgrouppanel
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


    def __init__(self,console,master,pgt,**params):       
        self.pgt=pgt
	PlotGroupPanel.__init__(self,console,master,pgt.name,**params)

        self.pack_param("sheet",parent=self.control_frame_3,on_change=self.sheet_change)
        self.pack_param("x",parent=self.control_frame_3)
        self.pack_param("y",parent=self.control_frame_3)

        # remove currently irrelevant widgets (plots are drawn in a separate window by pylab)
        [self._widgets[n].destroy() for n in ['Enlarge','Reduce']]

        self.auto_refresh= False
        if self.pgt.plot_immediately: self.refresh()


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

        if 'x' and 'y' in self._widgets:
            w1,w2=self._widgets['x'],self._widgets['y']
            w1.set_bounds(*x.bounds)
            w2.set_bounds(*y.bounds)
            
            w1.refresh();w2.refresh()
##############################################################################


    def populate_sheet_param(self,p):
        sheets = topo.sim.objects(ProjectionSheet).values() 
        sheets.sort(lambda x, y: cmp(-x.precedence,-y.precedence))
        p.params()['sheet'].range = sheets
        p.sheet = sheets[0]


    def generate_plotgroup(self):
        """
        Create the right Plot Key that will define the needed
        information for a FeatureCurvePlotGroup. 
        """
        p = self.plotgroup_type(template=self.pgt)
        self.populate_sheet_param(p)
	return p

    def _plot_title(self):
        # CEBHACKALERT: str()  (shouldn't lanbl be string already?)
        return str(self.plotgroup_label)+' at time ' + str(self.plotgroup.time)


    def display_labels(self):
        # plots are displayed in new windows, so don't add any labels
        pass



class FullFieldFeatureCurvePanel(FeatureCurvePanel):
    """
    In some cases it is not necessary to use the full updatecommand before plotting.
    This class creates a gui window showing the reduced update command and in which updating the
    plotgroup variables from the gui calls the plotcommand rather than the full updatecommand.
    """

### CEBHACKALERT! Not sure how best to handle redrawing here. Don't want to redraw on dragging the sliders,
### I guess...would lead to too many windows.

    Redraw = ButtonParameter(doc="""Redraw plots using existing data.""")

    def __init__(self,console,master,pgt,**config):
        FeatureCurvePanel.__init__(self,console,master,pgt,**config)

        self.pack_param('Redraw',parent=self.control_frame_1,
                        on_change=self.redraw_plots,side="left")
