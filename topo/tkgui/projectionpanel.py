"""
Projection Panel for TK GUI visualization.

$Id$
"""
__version__='$Revision$'


import __main__

from Tkinter import StringVar, BooleanVar, Frame, YES, LEFT, TOP, RIGHT
from Tkinter import X, Message, Entry, Canvas, FLAT, Checkbutton, NORMAL, DISABLED

import Pmw
import ImageTk
from math import ceil
### JCALERT! Try not to have to use chain and delete this import.
from itertools import chain

import topo
from topo.misc.keyedlist import KeyedList
from topo.base.projection import ProjectionSheet
from topo.base.sheet import Sheet
import topo.base.cf
from topo.plotting.templates import plotgroup_templates
from topo.plotting.plotgroup import ProjectionPlotGroup

from templateplotgrouppanel import TemplatePlotGroupPanel
import topoconsole

### JCALERT! See if we could delete this import * and replace it...
from topo.commands.analysis import *



UNIT_PADDING = 1
BORDERWIDTH = 1

# JDALERT: The canvas creation, border placement, and image
# positioning of Tkinter is very fragile.  This value boosts the size
# of the canvas that the plot image is displayed on.  Too large and
# the border will not be close, too small, and some of the image is
# not displayed.
CANVASBUFFER = 1


def cmp_projections(p1,p2):
    """
    Comparison function for Plots.
    It compares the precedence number first and then the src_name and name attributes.
    """
    if p1[1].src.precedence != p2[1].src.precedence:
	return cmp(p1[1].src.precedence,p2[1].src.precedence)
    else:
	return cmp(p1[0],p2[0])


### JABALERT: Maybe this should be called CFProjectionPanel instead,
### since it is only valid for CFProjections.
class ProjectionPanel(TemplatePlotGroupPanel):
    def __init__(self,parent,console=None,pgt_name=None,**params):
        
        self.region = StringVar()
	self.density_str = StringVar()
        self.density_str.set('10.0')
        self.density = float(eval(self.density_str.get(),__main__.__dict__))
	self.weight_name = StringVar()
        self.projections = KeyedList()
 
	super(ProjectionPanel,self).__init__(parent,console,pgt_name,**params)

        self.__params_frame = Frame(master=self)
        self.__params_frame.pack(side=LEFT,expand=YES,fill=X)

        self._add_situate_button()
	self.situate.set(False)
        self._add_region_menu()
        
     #    self.MIN_PLOT_HEIGHT = 1
#         self.INITIAL_PLOT_HEIGHT = 6
#         self.min_master_zoom=1

        self.params_frame1 = Frame(master=self)
        self.params_frame1.pack(side=RIGHT,expand=YES,fill=X)
        pd = Message(self.params_frame1,text="Plotting Density:",aspect=1000)
        pd.pack(side=LEFT)
        self.balloon.bind(pd,'Number of units to plot per 1.0 distance in sheet coordinates')
        self.de = Entry(self.params_frame1,textvariable=self.density_str)
        self.de.bind('<FocusOut>', self.refresh)
        self.de.bind('<Return>', self.refresh)
        self.de.pack(side=LEFT,expand=YES,fill=X,padx=2)

        self._add_projection_menu()

        self.auto_refresh.set(False)
        self.set_auto_refresh()
        
        self.refresh()

    def _add_region_menu(self):
        """
        This function adds a Sheet: menu that queries the active
        simulation for the list of options.  When an update is made,
        _region_refresh() is called.  It can either call the refresh()
        function, or update another menu, and so on.
        """

        # Create the item list for CFSheet 'Sheet'  This will not change
        # since this window will only examine one Simulation.
        sim = topo.sim
        self._sim_eps = [ep for ep in sim.objects(Sheet).values()
                  if isinstance(ep,topo.base.cf.CFSheet)]
	self._sim_eps.sort(lambda x, y: cmp(-x.precedence,-y.precedence))
        sim_ep_names = [ep.name for ep in self._sim_eps]
        if len(sim_ep_names) > 0:
            self.region.set(sim_ep_names[0])

        # The GUI label says Sheet, not CFSheet, because users probably 
        # don't need to worry about the distinction.
        self.opt_menu = Pmw.OptionMenu(self.__params_frame,
                       command = self.region_refresh,
                       labelpos = 'w',
                       label_text = 'Sheet:',
                       menubutton_textvariable = self.region,
                       items = sim_ep_names)
        self.opt_menu.pack(side=LEFT)
        # Should be shared with projectionpanel
        self.balloon.bind(self.opt_menu,
"""CFSheet whose unit(s) will be plotted.""")

    def _add_situate_button(self):
        
	self.situate = BooleanVar()
	self.situate.set(True)
        self.situate_checkbutton = Checkbutton(self.__params_frame,
             text="Situate",variable=self.situate,command=self.set_situate)
        self.situate_checkbutton.pack(side=LEFT)
        # Should move into the documentation for a situate parameter shared with connectionfieldspanel
        self.balloon.bind(self.situate_checkbutton,
"""If True, plots the weights on the entire source sheet, using zeros for all
weights outside the ConnectionField.  If False, plots only the actual weights that
are stored.""")

    def set_situate(self):
        """Set the attribute situate."""
        if self.plotgroup != None:
            self.plotgroup.situate = self.situate.get()
        self.plotgroup.initial_plot = True
        self.plotgroup.height_of_tallest_plot = self.min_master_zoom = 1
	self.plotgroup.update_plots(False)
	self.display_plots()

        
    ### JABHACKALERT!
    ###
    ### This function should test the projections list from a Sheet to
    ### make sure that only those of type CFProjection are included,
    ### because those are the only ones that this code knows how to
    ### deal with.  The abstract Projection class does not know
    ### anything about CFs, and this code can only handle CFs (at
    ### present).
    ###
    ### JABHACKALERT!
    ###
    ### Items in the Projection list in CFSheets should always be
    ### guaranteed to have unique names; if that's not true at
    ### present, the definition of an EventProcessor or a CFSheet (as
    ### appropriate) should be changed to force unique names.  We
    ### should not have to be reasoning about multiple Projections
    ### with the same name anywhere in the code except when such
    ### Projections are first defined, because it's meaningless to
    ### have such a set of Projections.  Thus all comments like the
    ### PRE below should be deleted, once the behavior of the list of
    ### projections has been verified.

    ### JC: this function has to be re-written anyway... 
    ###	e.g I don't know why self.projections is a KeyedList...
    def _create_projection_dict(self,sheet_name):
        """
        PRE: Each Projection in the CFSheet should have a unique name.
        If there are two Projections with the same name, then even
        though the list will show two entries with the same name, only
        one Projection object will be accessible.

        POST: self.projections dictionary has been populated with the
        list of projections for the active Region name in self.region.
        
        Both _add_projection_menu(), and refresh_region() need to
        create a dictionary with the Projection Name as key, and the
        Projection object as value, so this is its own function since
        it needs to be done the same way in both places.
        """
        if self._sim_eps:
            self._sim_ep = [ep for ep in self._sim_eps
                            if ep.name == sheet_name][0]
            self.tmp_projections = dict([(i.name, i) for i in
                                         self._sim_ep.in_connections])
	    self.projections= KeyedList()
            sorted_list = self.tmp_projections.items()
            sorted_list.sort(cmp_projections)
            for item in sorted_list:
                self.projections.append((item[0],item[1]))
                
        old_projection_name = self.weight_name.get()
        if len(self.projections.keys()) == 0:
            self.weight_name.set('None')
        elif old_projection_name not in self.projections.keys():
            self.weight_name.set(self.projections.keys()[0])


    def _add_projection_menu(self):
        """
        Adds a Projection Widget to the existing frame, and creates the
        item list for Unit Projection names.  This needs to be
        changing based on which Region is selected.  See
        self.region_refresh() 
        """
        self.params_frame2 = Frame(master=self)
        self.params_frame2.pack(side=LEFT,expand=YES,fill=X)

        self._create_projection_dict(self.region.get())
       
        self.projection_menu = Pmw.OptionMenu(self.params_frame2,
                       command = self.projection_refresh,
                       labelpos = 'w',
                       label_text = 'Projection:',
                       menubutton_textvariable = self.weight_name,
                       items = self.projections.keys())
        self.projection_menu.pack(side=LEFT)
        # Should be shared with projectionpanel
        self.balloon.bind(self.projection_menu,
"""Projection to plot.""")


    @staticmethod
    def valid_context():
        """
        Only open if there are Projections defined.
        """
        projectionsheets=topo.sim.objects(ProjectionSheet).values()
        if not projectionsheets:
            return False

        projectionlists=[i.projections().values() for i in projectionsheets]
        projections=[i for i in chain(*projectionlists)]
        return (not projections == [])


    def projection_refresh(self,projection_name):
        """
        Called by the Pmw.OptionMenu when the menubutton_textvariable
        is updated.  The do_plot_cmd() already plots the correct
        Projection but this will force a refresh().
        """
        self.refresh()
        
        
    def region_refresh(self,sheet_name):
        """
        Update the Projection menu.  This overwrites the parent class
        function CFSheetPlotPanel.region_refresh() which is called when
        the Region Widget menu is changed.
        """
        self._create_projection_dict(sheet_name)
        self.projection_menu.setitems(self.projections.keys())
        self.refresh()


    def refresh_title(self):
        self.parent.title(topo.sim.name+': '+"Projection %s %s time:%s" % (self.plotgroup.sheet_name,
            self.plotgroup.weight_name,self.plotgroup.time))
        

    def update_plotgroup_variables(self):
        """
        Generate the key used to look up the PlotGroup for this Projection.

        The plotgroup_key for retrieving the PlotGroup depends on the
        values entered in the window widgets.  This method generates
        the appropriate key based on those values, using a tuple like:
        ('Projection', self.weight_name, self.density, self.region).
        """
        self.density = float(eval(self.density_str.get(),__main__.__dict__))
	self.plotgroup.situate= self.situate.get()
	self.plotgroup.density = self.density
	self.plotgroup.sheet_name=self.region.get()
	self.plotgroup.weight_name = self.weight_name.get()


    def generate_plotgroup(self):
        """
        self.generate_plotgroup_key() creates the density information needed for
        a ProjectionPlotGroup to create necessary Plots.
        """
 	plotgroup = ProjectionPlotGroup([],self.pgt,self.region.get(),
					self.weight_name.get(),self.density,
                                        normalize=self.normalize.get(),
                                        sheetcoords=self.sheetcoords.get(),
                                        integerscaling=self.integerscaling.get())
  	return plotgroup


    def display_plots(self):
        """
        This must be changed from PlotGroupPanels version since
        ProjectionPanel requires a 2D grid of plots.
        """
        if self.plotgroup:
	    plots=self.plotgroup.plots
	    ### Momentary: delete when sorting the bitmap history
	    self.bitmaps = [p.bitmap for p in plots]
            # Generate the zoomed images.
            self.zoomed_images = [ImageTk.PhotoImage(p.bitmap.image)
                                  for p in plots]
            old_canvases = self.canvases
            self.canvases = [Canvas(self.plot_frame,
                               width=image.width()+BORDERWIDTH*2+CANVASBUFFER,
                               height=image.height()+BORDERWIDTH*2+CANVASBUFFER,
                               bd=0)
                             for image in self.zoomed_images]
    
            # Lay out images
            for i,image,canvas in zip(range(len(self.zoomed_images)),
                                      self.zoomed_images,self.canvases):
                canvas.grid(row=i//self.plotgroup.proj_plotting_shape[0],
                            column=i%self.plotgroup.proj_plotting_shape[1],
                            padx=UNIT_PADDING,pady=UNIT_PADDING)
                # BORDERWIDTH is added because the border is drawn on the
                # canvas, overwriting anything underneath it.
                # The +1 is necessary since the TKinter Canvas object
                # has a problem with axis alignment, and 1 produces
                # the best result.
                canvas.create_image(image.width()/2+BORDERWIDTH+1,
                                    image.height()/2+BORDERWIDTH+1,
                                    image=image)
                canvas.config(highlightthickness=0,borderwidth=0,relief=FLAT)
                canvas.create_rectangle(1, 1, image.width()+BORDERWIDTH*2,
                                        image.height()+BORDERWIDTH*2,
                                        width=BORDERWIDTH,outline="black")

    
            # Delete old ones.  This may resize the grid.
            for c in old_canvases:
                c.grid_forget()
    

    def display_labels(self):
        """
        It's not a good idea to show the name of every plot, but it is
        reasonable to put information around the plot group.
        """
        if len(self.projections) > 0:
            src_name = self.projections[self.weight_name.get()].src.name

            new_title = 'Projection ' + self.plotgroup.weight_name + ' from ' + src_name + ' to ' \
                        + self.plotgroup.sheet_name + ' at time ' + str(self.plotgroup.time)
            self.plot_group_title.configure(tag_text = new_title)
        else:
            self.plot_group_title.configure(tag_text = 'No Projections')
        

    def restore_panel_environment(self):
	super(ProjectionPanel,self).restore_panel_environment()
	if self.plotgroup.situate != self.situate.get():
	    self.situate_checkbutton.config(state=NORMAL)
	    self.situate_checkbutton.invoke()
	    self.situate_checkbutton.config(state=DISABLED)

    def update_back_fwd_button(self):
	super(ProjectionPanel,self).update_back_fwd_button()
	if (self.history_index > 0):
            self.situate_checkbutton.config(state=DISABLED)
	    ### JCALERT: Should find a way to disable the region menu
	    ### (What I tried below does not work)
	    ### Also, disabled the text for the xy_boxes (i.e., X,Y)
	    ## Also, when changing the menu while looking in history,
            ### it will replaced the old current one by the new one instead of adding
	    ### the new at the following.
	    #self.opt_menu.config(state=DISABLED)

        if self.history_index >= len(self.plotgroups_history)-1:
	    self.situate_checkbutton.config(state=NORMAL)
	    #self.opt_menu.config(state=NORMAL)


