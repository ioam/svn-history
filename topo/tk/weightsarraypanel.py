"""
WeightsArray Panel for TK GUI visualization.

$Id$
"""
import __main__
from topo.tk.regionplotpanel import *
from topo.tk.plotpanel import *
from itertools import chain

class WeightsArrayPanel(RegionPlotPanel):
    def __init__(self,parent,pengine,console=None,**config):
        super(WeightsArrayPanel,self).__init__(parent,pengine,console,**config)

        self.MIN_PLOT_WIDTH = 5
        self.INITIAL_PLOT_WIDTH = 20
        self.panel_num = self.console.num_weights_array_windows

        self.density_str = StringVar()
        self.density_str.set('100.0/10.0')
        self.density = float(eval(self.density_str.get(),__main__.__dict__))
        self.shape = (0,0)

        self.weight_name = StringVar()
        self.weight_name.set('None')
        self.projections = {}


        self.params_frame1 = Frame(master=self)
        self.params_frame1.pack(side=RIGHT,expand=YES,fill=X)
        Message(self.params_frame1,text="Units per 1.0:",aspect=1000).pack(side=LEFT)
        Entry(self.params_frame1,
              textvariable=self.density_str).pack(side=LEFT,expand=YES,fill=X,padx=5)

        self._add_projection_menu()

        # Situate currently not implemented!  When implemented, should
        # have each unit plotted within a frame that shows the
        # sensitivity region on the source Sheet.
        #
        # self.situate = StringVar()
        # self.situate.set(0)
        # Checkbutton(self.params_frame1,text="Situate",variable=self.situate,
        #             command=self.refresh).pack(side=LEFT)

        self.refresh()


    def _create_projection_dict(self,sheet_name):
        """
        PRE: Each Projection in the RFSheet should have a unique name.
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
        Adds a Projection Widget to th existing frame, and creates the
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
        is updated.  The do_plot_cmd() already polls the correct
        Projection but this will force a refresh() if auto_refresh if
        it is enabled.
        """
        if self.auto_refresh:
            self.refresh()
        
        
    def region_refresh(self,sheet_name):
        """
        Update the Projection menu.  This overwrites the parent class
        function RegionPlotPanel.region_refresh() which is called when
        the Region Widget menu is changed.
        """
        self._create_projection_dict(sheet_name)
        self.projection_menu.setitems(self.projections.keys())
        if self.auto_refresh:
            self.refresh()


    def refresh_title(self):
        self.parent.title("Weights Array %d. (Region %s, Projection %s, Density %0.2f)" % (self.panel_num,self.region.get(),
            self.weight_name.get(), self.density))
        

    def generate_plot_key(self):
        """
        The plot_key for the WeightsArrayPanel will change depending
        on the input within the window widgets.  This means that the
        key needs to be regenerated at the appropriate times.

        Key Format:  Tuple: ('WeightsArray', self.weight_name, self.density)
        """
        self.density = float(eval(self.density_str.get(),__main__.__dict__))
        self.plot_key = ('WeightsArray',self.weight_name.get(),self.density)


    def do_plot_cmd(self):
        """
        The WeightsArrayPanel will calculate the number of plots to
        show for the active Sheet and Projection.  It will generate
        multiple unit_view() requests; keep the Projections desired,
        and then store the composite list back into the Sheet under a
        key that other functions in this class will use to display.
        """
        self.generate_plot_key()
        coords = self.generate_coords()
        
        full_unitview_list = [self._sim_ep.unit_view(x,y)
                         for (x,y) in coords]
        filtered_list = [view for view in chain(*full_unitview_list)
                         if view.projection == self.projections[self.weight_name.get()]]
        self._sim_ep.add_sheet_view(self.plot_key,filtered_list)

        super(WeightsArrayPanel,self).do_plot_cmd()

        for (x,y) in coords: self._sim_ep.release_unit_view(x,y)
        

    def generate_coords(self):
        """
        Evenly space out the units within the sheet bounding box, so
        that it doesn't matter which corner the measurements start
        from.  A 4 unit grid needs 5 segments.
        """
        aarect = self._sim_ep.bounds.aarect()
        (l,b,r,t) = aarect.lbrt()
        x = float(r - l) 
        y = float(t - b)
        x_step = x / (int(x * self.density) + 1)
        y_step = y / (int(y * self.density) + 1)
        l = l + x_step
        b = b + y_step
        coords = []
        self.shape = (int(x * self.density), int(y * self.density))
        for j in range(self.shape[1]):
            for i in range(self.shape[0]):
                coords.append((x_step*j + l, y_step*i + b))
        return coords
            


    def display_plots(self):
        """
        PlotPanel will display plots in a single row.  WeightsArrayPanel requires
        a 2D grid of plots.
        """
        # Generate the zoomed images.
        self.zoomed_images = [ImageTk.PhotoImage(im.zoom(self.zoom_factor))
                              for im in self.images]
        old_canvases = self.canvases
        self.canvases = [Canvas(self.plot_frame,
                                width=image.width(),
                                height=image.height(),
                                bd=2)
                         for image in self.zoomed_images]

        # Lay out images
        for i,image,canvas in zip(range(len(self.zoomed_images)),
                                  self.zoomed_images,self.canvases):
            canvas.grid(row=i%self.shape[0],column=i//self.shape[1],
                        padx=1,pady=1)
            canvas.create_image(image.width()/2,image.height()/2,image=image)

        # Delete old ones.  This may resize the grid.
        for c in old_canvases:
            c.grid_forget()


    def display_labels(self):
        """
        It's not a good idea to show the name of every plot, but it is
        reasonable to put information on the X and Y axes.
        """
        if len(self.projections) > 0:
            src_name = self.projections[self.weight_name.get()].src.name
            new_title = 'Projections from ' + src_name
            self.plot_group.configure(tag_text = new_title)
        else:
            self.plot_group.configure(tag_text = 'No Projections')
        



