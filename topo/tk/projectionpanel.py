"""
Projection Panel for TK GUI visualization.

$Id$
"""
import __main__
from Tkinter import StringVar, Frame, YES, LEFT, TOP, RIGHT, X, Message, \
     Entry, Canvas
import Pmw
import ImageTk
import topo.plotengine as plotengine
from math import ceil
from topo.tk.regionplotpanel import CFSheetPlotPanel
from topo.tk.plotpanel import PlotPanel
from itertools import chain

### JABHACKALERT!
###
### This file and the class in it should be renamed to
### projectionpanel.py and ProjectionPanel.py, respectively. I've
### already changed the relevant menu items, and the code should be
### changed to match.

class ProjectionPanel(CFSheetPlotPanel):
    def __init__(self,parent,pengine,console=None,**config):
        super(ProjectionPanel,self).__init__(parent,pengine,console,**config)

        self.MIN_PLOT_WIDTH = 1
        self.INITIAL_PLOT_WIDTH = 13
        self.panel_num = self.console.num_weights_array_windows

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
        Entry(self.params_frame1,
              textvariable=self.density_str).pack(side=LEFT,expand=YES,fill=X,padx=2)

        self._add_projection_menu()

        # Situate currently not implemented!  When implemented, should
        # have each unit plotted within a frame that shows the
        # sensitivity region on the source Sheet.
        #
        # self.situate = StringVar()
        # self.situate.set(0)
        # Checkbutton(self.params_frame1,text="Situate",variable=self.situate,
        #             command=self.refresh).pack(side=LEFT)

        self.auto_refresh_checkbutton.invoke()
        self.refresh()


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
            self.projections = dict([(i.name, i) for i in
                                     chain(*self._sim_ep.projections.values())])

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


    def projection_refresh(self,projection_name):
        """
        Called by the Pmw.OptionMenu when the menubutton_textvariable
        is updated.  The do_plot_cmd() already plots the correct
        Projection but this will force a refresh() if auto_refresh if
        it is enabled.
        """
        if self.auto_refresh:
            self.refresh()
        
        
    def region_refresh(self,sheet_name):
        """
        Update the Projection menu.  This overwrites the parent class
        function CFSheetPlotPanel.region_refresh() which is called when
        the Region Widget menu is changed.
        """
        self._create_projection_dict(sheet_name)
        self.projection_menu.setitems(self.projections.keys())
        if self.auto_refresh:
            self.refresh()


    def refresh_title(self):
        self.parent.title("Projection %d. (Region %s, Projection %s, Density %0.2f)" % (self.panel_num,self.region.get(),
            self.weight_name.get(), self.density))
        

    def generate_plot_key(self):
        """
        The plot_key for the ProjectionPanel will change depending
        on the input within the window widgets.  This means that the
        key needs to be regenerated at the appropriate times.

        Key Format:  Tuple: ('Projection', self.weight_name, self.density)
        """
        self.density = float(eval(self.density_str.get(),__main__.__dict__))
        self.plot_key = ('Projection',self.weight_name.get(),self.density)

        pt = plotengine.plotgroup_templates['Projection'].plot_templates['Projection']
        pt.channels['Density'] = self.density
        pt.channels['Projection_name'] = self.weight_name.get()
        

    def do_plot_cmd(self):
        """
        self.generate_plot_key() creates the density information needed for
        a ProjectionPlotGroup to create necessary Plots.
        """
        if self.console.active_simulator().get_event_processors():
            self.generate_plot_key()
            self.pe_group = self.pe.get_plot_group(self.plot_key,
                                                   plotengine.plotgroup_templates['Projection'],
                                                   self.region.get(),
                                                   'ProjectionPlotGroup')
            self.pe_group.do_plot_cmd()
            self.plots = self.pe_group.plots()


    def display_plots(self):
        """
        This must be changed from PlotPanels version since
        ProjectionPanel requires a 2D grid of plots.
        """
        if self.pe_group:
            # Generate the zoomed images.
            self.zoomed_images = [ImageTk.PhotoImage(im.zoom(self.zoom_factor))
                                  for im in self.pe_group.bitmaps]
            old_canvases = self.canvases
            self.canvases = [Canvas(self.plot_frame,
                                    width=image.width(),
                                    height=image.height(),
                                    bd=0)
                             for image in self.zoomed_images]
    
            # Lay out images
            for i,image,canvas in zip(range(len(self.zoomed_images)),
                                      self.zoomed_images,self.canvases):
                canvas.grid(row=i//self.pe_group.shape[0],
                            column=i%self.pe_group.shape[1],
                            padx=6,pady=6)
                canvas.create_image(image.width()/2+2,image.height()/2+2,image=image)
    
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

            new_title = 'Projection ' + self.weight_name.get() + ' from ' + src_name + ' to ' + self.region.get()
            self.plot_group.configure(tag_text = new_title)
        else:
            self.plot_group.configure(tag_text = 'No Projections')
        



