"""
WeightsArray Panel for TK GUI visualization.

$Id$
"""
from topo.tk.plotpanel import *

class WeightsArrayPanel(PlotPanel):
    def __init__(self,parent,pengine,console=None,**config):

        self.skip_str = StringVar()
        self.skip_str.set('N/8')

        self.situate = StringVar()
        self.situate.set(0)

        self.region = StringVar()
        self.region.set('None')

        self.weight_name = StringVar()
        self.weight_name.set('None')

        # Used by update_projection_options()
        self._sim_eps = []

        # Generate the initial plot_key
        self.generate_plot_key()
        self.debug('plot_key = ' + str(self.plot_key))

        PlotPanel.__init__(self,parent,pengine,console,**config)

        self.params_frame1 = Frame(master=self)
        self.params_frame1.pack(side=BOTTOM,expand=YES,fill=X)

        Message(self.params_frame1,text="Skip:",aspect=1000).pack(side=LEFT)
        Entry(self.params_frame1,textvariable=self.skip_str).pack(side=LEFT,expand=YES,fill=X)
        Checkbutton(self.params_frame1,text="Situate",variable=self.situate,
                    command=self.refresh).pack(side=LEFT)

        self.params_frame2 = Frame(master=self)
        self.params_frame2.pack(side=BOTTOM,expand=YES,fill=X)

        # Create the item list for RFSheet 'Region'  This will not change
        # since this window will only examine one Simulator.
        sim = console.active_simulator()
        self._sim_eps = [ep for ep in sim.get_event_processors()
                  if isinstance(ep,topo.rfsheet.RFSheet)]
        sim_ep_names = [ep.name for ep in self._sim_eps]
        if len(sim_ep_names) > 0:
            self.region.set(sim_ep_names[0])

        Pmw.OptionMenu(self.params_frame2,
                       command = self._update_projection_options,
                       labelpos = 'w',
                       label_text = 'Region:',
                       menubutton_textvariable = self.region,
                       items = sim_ep_names
                       ).pack(side=LEFT)

        # Create the item list for Unit Projection names.  This will
        # be changing based on which Region is selected.  See
        # self.update_projection_options()
        sim_ep = [ep for ep in self._sim_eps
                  if ep.name == self.region.get()][0]
        projection_dict = sim_ep.projections
        projection_list_names = projection_dict.keys()
        if len(projection_list_names) > 0:
            self.weight_name.set(projection_list_names[0])

        self.projection_menu = Pmw.OptionMenu(self.params_frame2,
                       labelpos = 'w',
                       label_text = 'Projection:',
                       menubutton_textvariable = self.weight_name,
                       items = projection_list_names)
        self.projection_menu.pack(side=LEFT)


    def _update_projection_options(self,sheet_name):
        """
        Create the Projection menu.  This function is only called by the
        PMW.OptionMenu inside self.params_frame when the Region has been
        changed.
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


    def generate_plot_key(self):
        """
        The plot_key for the WeightsArrayPanel will change depending
        on the input within the window widgets.  This means that the
        key needs to be regenerated at the appropriate times.

        Key Format:  Tuple: ('WeightsArray' ... unknown)
        """
        # From WeightsPanel code
        # g = __main__.__dict__
        # self.r = eval(self.row_str.get(),g)
        # self.c = eval(self.col_str.get(),g)
        # if isinstance(self.r,int): self.r = float(self.r)
        # if isinstance(self.c,int): self.c = float(self.c)
        self.plot_key = 'Activation'
        # self.plot_key = ('WeightsArray',3,3)


    def do_plot_cmd(self):
        Pmw.showbusycursor()

        self.generate_plot_key()
        self.pe_group = self.pe.get_plot_group(self.plot_key)
        self.plot_tuples = self.pe_group.plots()
        self.pe.debug('Type of plot_group', type(self.pe_group))

        self.plotlist = []
        self.plotlabels = []

        self.pe_group = self.pe.get_plot_group(self.plot_key)
        self.plot_tuples = self.pe_group.plots()
        self.pe.debug('Type of plot_group', type(self.pe_group))

#        self.parent.title("Weights Array %d. (r=%0.4f, c=%0.4f)" %
#                          (self.console.num_weights_windows,self.r, self.c))
        Pmw.hidebusycursor()

    def load_images(self):
        # need to calculate the old min width, so we know if we need to reset
        # the zoom factors
        if self.images:
            old_min_width = reduce(min,[im.width() for im in self.images])
        else:
            old_min_width = -1

        self.images = []
        for (figure_tuple, hist_tuple) in self.plot_tuples:
            (r,g,b) = figure_tuple
            if r.shape != (0,0) and g.shape != (0,0) and b.shape != (0,0):
                # Normalize activation to a maximum of 1.  Will scale brighter
                # or darker, depending.
                if max(r.flat) > 0: r = Numeric.divide(r,max(r.flat))
                if max(g.flat) > 0: g = Numeric.divide(g,max(g.flat)) 
                if max(b.flat) > 0: b = Numeric.divide(b,max(b.flat))
                win = topo.bitmap.RGBMap(r,g,b)
                self.images.append(win)
                self.plotlist.append(win)
                self.plotlabels.append(self.pe_group.name + ' ' + str(len(self.plotlist)))

        
        if self.images:
            min_width = reduce(min,[im.width() for im in self.images])
        else:
            min_width = 0
        
        if old_min_width != min_width:
            # if the min width changed, then recalculate the zoom factor
            # If no plots, then no window.
            if MIN_PLOT_WIDTH > min_width and old_min_width != -1:
                self.min_zoom_factor = MIN_PLOT_WIDTH/min_width + 1
            else:
                self.min_zoom_factor = 1

            print 'pre zoom_factor', self.zoom_factor
        

            self.zoom_factor = self.min_zoom_factor
            print 'post zoom_factor', self.zoom_factor
            self.reduce_button.config(state=DISABLED)

        
    def display_plots(self):
        self.zoomed_images = [ImageTk.PhotoImage(im.zoom(self.zoom_factor)) for im in self.images]
        old_canvases = self.canvases
        self.canvases = [Canvas(self.plot_frame,
                                width=image.width(),
                                height=image.height(),
                                bd=2)
                         for image in self.zoomed_images]
        for i,image,canvas in zip(range(len(self.zoomed_images)),
                                  self.zoomed_images,self.canvases):
            canvas.grid(row=0,column=i,padx=5)
            canvas.create_image(image.width()/2,image.height()/2,image=image)

        for c in old_canvases:
            c.grid_forget()

    def display_labels(self):
        for i,name in enum(self.plotlabels):
            self.debug(i, " ", name)
            Label(self.plot_frame,text=name).grid(row=1,column=i,sticky=NSEW)




    def plotname_to_filename(self,plotname):
        """CURRENTLY NOT USED 3/2005"""
        return 'gui.'+self.plotname_components(plotname)[0]+'_Weights.ppm'
####################
