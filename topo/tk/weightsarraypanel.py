"""
WeightsArray Panel for TK GUI visualization.

$Id$
"""
import __main__
from topo.tk.regionplotpanel import *
from topo.tk.plotpanel import *

class WeightsArrayPanel(RegionPlotPanel):
    def __init__(self,parent,pengine,console=None,**config):
        super(WeightsArrayPanel,self).__init__(parent,pengine,console,**config)

        self.MIN_PLOT_WIDTH = 20
        self.INITIAL_PLOT_WIDTH = None
        self.panel_num = self.console.num_weights_array_windows

        self.density_str = StringVar()
        self.density_str.set('100.0/10.0')
        self.density = float(eval(self.density_str.get(),__main__.__dict__))

        self.weight_name = StringVar()
        self.weight_name.set('None')

        self.params_frame1 = Frame(master=self)
        self.params_frame1.pack(side=RIGHT,expand=YES,fill=X)
        Message(self.params_frame1,text="Units per 1.0:",aspect=1000).pack(side=LEFT)
        Entry(self.params_frame1,
              textvariable=self.density_str).pack(side=LEFT,expand=YES,fill=X)

        self._add_projection_menu()

        # Situate currently not implemented!  When implemented, should
        # have each unit plotted within a frame that shows the
        # sensitivity region on the source Sheet.
        #
        # self.situate = StringVar()
        # self.situate.set(0)
        # Checkbutton(self.params_frame1,text="Situate",variable=self.situate,
        #             command=self.refresh).pack(side=LEFT)


    def _add_projection_menu(self):
        """
        
        Adds a Projection Widget to th existing frame, and creates the
        item list for Unit Projection names.  This needs to be
        changing based on which Region is selected.  See
        self.region_refresh()

        """
        self.params_frame2 = Frame(master=self)
        self.params_frame2.pack(side=LEFT,expand=YES,fill=X)

        self._sim_ep = [ep for ep in self._sim_eps
                  if ep.name == self.region.get()][0]
        projection_dict = self._sim_ep.projections
        projection_list_names = projection_dict.keys()
        if len(projection_list_names) > 0:
            self.weight_name.set(projection_list_names[0])

        self.projection_menu = Pmw.OptionMenu(self.params_frame2,
                       labelpos = 'w',
                       label_text = 'Projection:',
                       menubutton_textvariable = self.weight_name,
                       items = projection_list_names)
        self.projection_menu.pack(side=LEFT)
        

    def region_refresh(self,sheet_name):
        """
        Update the Projection menu.  This overwrites the parent class
        function RegionPlotPanel.region_refresh() which is called when
        the Region menu is changed.
        """
        sim_ep = [ep for ep in self._sim_eps if ep.name == sheet_name][0]
        projection_dict = sim_ep.projections
        projection_list_names = projection_dict.keys()
        old_projection_name = self.weight_name.get()
        if len(projection_list_names) == 0:
            self.weight_name.set('None')
        elif old_projection_name not in projection_list_names:
            self.weight_name.set(projection_list_names[0])
        self.projection_menu.setitems(projection_list_names)


    def refresh_title(self):
        self.parent.title("Weights Array %d. (Region %s, Projection %s, Density %0.2f)" %
                          (self.panel_num,self.region.get(),
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


#     def generate_coords(self, num_points, bbox):
#         """
#         Evenly space out the units within the sheet bounding box, so
#         that it doesn't matter which corner the measurements start
#         from.  A 4 unit grid needs 5 segments.
#         """
#         aarect = bbox.aarect()
#         (l,b,r,t) = aarect.lbrt()
#         x = float(r - l)
#         y = float(b - t)
#         x_step = x / (num_points + 1)
#         y_step = y / (num_points + 1)
#         l = l + x_step
#         t = t + y_step
#         coords = []
#         for j in range(num_points):
#             y_list = []
#             for i in range(num_points):
#                 y_list.append((x_step*j + l, y_step*i + t))
#             coords.append(y_list)
#         return coords
#             


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
            canvas.grid(row=0,column=i,padx=5)
            canvas.create_image(image.width()/2,image.height()/2,image=image)

        # Delete old ones.  This may resize the grid.
        for c in old_canvases:
            c.grid_forget()


    def display_labels(self):
        """
        It's not a good idea to show the name of every plot, but it is reasonable
        to put information on the X and Y axes.
        """
        for i,name in enum(self.plotlabels):
            self.debug(i, " ", name)
            Label(self.plot_frame,text=name).grid(row=1,column=i,sticky=NSEW)


