"""
Projection Panel for TK GUI visualization.

$Id$
"""
__version__='$Revision$'

import __main__
from Tkinter import StringVar, Frame, YES, LEFT, TOP, RIGHT, X, Message, \
     Entry, Canvas, FLAT
import Pmw
import ImageTk
from topo.plotting.templates import plotgroup_templates
from math import ceil
from cfsheetplotpanel import CFSheetPlotPanel
from plotgrouppanel import PlotGroupPanel
from itertools import chain
from topo.base.projection import ProjectionSheet
import topoconsole
from topo.base.utils import dict_sort
from topo.misc.keyedlist import KeyedList
from math import ceil


from topo.plotting.plotgroup import plotgroup_dict, ProjectionPlotGroup
UNIT_PADDING = 1
BORDERWIDTH = 1
# JDALERT: The canvas creation, border placement, and image
# positioning, of Tkiner is very fragile.  This value boosts the size
# of the canvas that the plot image is displayed on.  Too large and
# the border will not be close, too small, and some of the image is
# not displayed.
CANVASBUFFER = 1

class ProjectionPanel(CFSheetPlotPanel):
    def __init__(self,parent,console=None,plot_group_key=None,pgt_name=None,**config):
        super(ProjectionPanel,self).__init__(parent,console,plot_group_key,pgt_name,**config)

        self.MIN_PLOT_WIDTH = 1
        self.INITIAL_PLOT_WIDTH = 13

        self.density_str = StringVar()
        self.density_str.set('10.0')
        self.density = float(eval(self.density_str.get(),__main__.__dict__))

        self.weight_name = StringVar()
        self.weight_name.set('None')
        self.projections = {}

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

        self.auto_refresh_checkbutton.invoke()
        self.refresh()


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
                                     chain(*self._sim_ep.in_projections.values())])

            ### JCHACKALERT! This has been done to solve the problem of the displaying order in
            ### the projection panel: this way, we start to plot in the alphabetical order
            ### which corresponds (luckily) to the order we want
            self.projections = KeyedList()
            sorted_list = self.tmp_projections.items()
            sorted_list.sort()
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


    @staticmethod
    def valid_context():
        """
        Only open if ProjectionSheets are in the Simulator.
        """
        if topoconsole.active_sim().objects(ProjectionSheet).items():
            return True
        else:
            return False


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
        self.parent.title("Projection (%s projection %s) time:%s" % (self.region.get(),
            self.weight_name.get(),self.console.simulator.time()))
        

    def generate_plot_group_key(self):
        """
        Generate the key used to look up the PlotGroup for this Projection.

        The plot_group_key for retrieving the PlotGroup depends on the
        values entered in the window widgets.  This method generates
        the appropriate key based on those values, using a tuple like:
        ('Projection', self.weight_name, self.density, self.region).
        """
        self.density = float(eval(self.density_str.get(),__main__.__dict__))
        self.plot_group_key = ('Projection',self.weight_name.get(),self.density,self.region.get())

        pt = plotgroup_templates['Projection'].plot_templates['Projection']
        pt['Density'] = self.density
        pt['Projection_name'] = self.weight_name.get()
        

    def do_plot_cmd(self):
        """
        self.generate_plot_group_key() creates the density information needed for
        a ProjectionPlotGroup to create necessary Plots.
        """
  
        self.generate_plot_group_key()

	self.pe_group = plotgroup_dict.get(self.plot_group_key,None)
	if self.pe_group == None:
	    self.pe_group = ProjectionPlotGroup(self.console.simulator,self.pgt,self.plot_group_key,
					         self.region.get(),[])

        self.pe_group.do_plot_cmd()
        
        # self.situate is defined in the super class CFSheetPlotPanel
        self.pe_group.situate= self.situate
 

    def display_plots(self):
        """
        This must be changed from PlotGroupPanels version since
        ProjectionPanel requires a 2D grid of plots.
        """
        if self.pe_group:
            # Generate the zoomed images.
            self.zoomed_images = [ImageTk.PhotoImage(im.zoom(self.zoom_factor))
                                  for im in self.pe_group.bitmaps]
            old_canvases = self.canvases
            self.canvases = [Canvas(self.plot_frame,
                               width=image.width()+BORDERWIDTH*2+CANVASBUFFER,
                               height=image.height()+BORDERWIDTH*2+CANVASBUFFER,
                               bd=0)
                             for image in self.zoomed_images]
    
            # Lay out images
            for i,image,canvas in zip(range(len(self.zoomed_images)),
                                      self.zoomed_images,self.canvases):
                canvas.grid(row=i//self.pe_group.shape[0],
                            column=i%self.pe_group.shape[1],
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

            new_title = 'Projection ' + self.weight_name.get() + ' from ' + src_name + ' to ' \
                        + self.region.get() + ' at time ' + str(self.console.simulator.time())
            self.plot_group.configure(tag_text = new_title)
        else:
            self.plot_group.configure(tag_text = 'No Projections')
        



