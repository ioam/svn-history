"""
ConnectionFieldsPanel for GUI visualization of ConnectionFieldsPlotGroup.


$Id$
"""
__version__='$Revision$'


import topo

from topo.plotting.plotgroup import ConnectionFieldsPlotGroup
from topo.base.cf import CFSheet

from projectionpanel import CFPGPanel


# CEBHACKALERT: various parts of the dynamic info/right-click menu stuff
# don't make sense at the moment when things like 'situate' are clicked.

class ConnectionFieldsPanel(CFPGPanel):

    plotgroup_type = ConnectionFieldsPlotGroup


        # CEBALERT: used to eval x,y in main here and elsewhere in tkgui so that variables could be used.
        # Now that the widget selection is automatic, this should be taken care of (at least partly) elsewhere
        # (e.g. a taggedslider that converts to float by doing an eval in main and float(), etc).

    
    def __init__(self,console,master,pgt,**params):       
        super(ConnectionFieldsPanel,self).__init__(console,master,pgt,**params) 
        self.pack_param('x',parent=self.control_frame_3,on_change=self.update_plots)
        self.pack_param('y',parent=self.control_frame_3,on_change=self.update_plots)

##############################################################################       
        # Need to couple taggedslider to a Number parameter in a better way
        # somewhere else.
        # Current defects:
        # e.g. bound on parameter is 0.5 but means <0.5, taggedslider
        #   still lets you set to 0.5 -> error
        self.sheet_change()
    def sheet_change(self):

        super(ConnectionFieldsPanel,self).sheet_change()

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


    def display_labels(self):
        """
        Change the title of the grid group, then call PlotGroupPanel's
        display_labels().
        """
        new_title = 'Connection Fields of ' + self.sheet.name + \
                    ' unit (' + str(self.plotgroup.x) + ',' + str(self.plotgroup.y) + ') at time '\
                    + str(self.plotgroup.time)
        self.plot_group_title.configure(tag_text = new_title)
        super(ConnectionFieldsPanel,self).display_labels()


    def refresh_title(self):
        self.title(topo.sim.name+': '+self.pgt.name + " %s (%0.3f,%0.3f) time:%s" %
                          (self.plotgroup.sheet.name,self.plotgroup.x,self.plotgroup.y,self.plotgroup.time))



