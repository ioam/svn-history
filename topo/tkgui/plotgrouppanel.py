"""
Classes BasicPlotGroupPanel and PlotGroupPanel.

These classes provide GUI windows for PlotGroups, allowing sets of
related plots to be displayed.

$Id$
"""
__version__='$Revision$'


import numpy.oldnumeric as Numeric
import copy

from inspect import getdoc
from math import floor

import Image
import ImageTk
import Pmw
from Tkinter import  Frame, TOP, YES, BOTH, BOTTOM, X, Button, LEFT, \
     RIGHT, DISABLED, Checkbutton, NORMAL, Canvas, Label, NSEW, IntVar, \
     BooleanVar, StringVar, FLAT, SUNKEN, RAISED, GROOVE, RIDGE, \
     Scrollbar, Y, VERTICAL, HORIZONTAL, Menu, END

from topo.base.parameterizedobject import ParameterizedObject
from topo.base.sheet import Sheet

from topo.plotting.templates import plotgroup_templates
from topo.plotting.plotgroup import PlotGroup,identity

import topo.tkgui

BORDERWIDTH = 1

# Unfortunately, the canvas creation, border placement, and image
# positioning of Tkinter are very fragile.  This value boosts the size
# of the canvas that the plot image is displayed on.  Too large and
# the border will not be close, too small, and some of the image is
# not displayed.  
CANVASBUFFER = 1


class BasicPlotGroupPanel(Frame,ParameterizedObject):
    """
    Abstract BasicPlotGroupPanel class for displaying plots to a TK
    GUI window. Implements only basic buttons required. 
    Must be subclassed to be usable.
    """
	
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
        if topo.sim.objects(Sheet).items():
            return True
        else:
            return False


    def __init__(self,parent,console,plotgroup_key,**params):
        """
        parent:  it is the window (GUIToplevel()) that contains the panel.
        console: is the associated console, (i.e. the TopoConsole that has this panel)
        name: name associated with the panel
	"""

        Frame.__init__(self,parent)
        topo.plotting.plot.ParameterizedObject.__init__(self,**params)

	self.console = console
        self.parent = parent
	# balloon help component
        self.balloon = Pmw.Balloon(parent)
        self.canvases = []

	### JCALERT: we will have to rename plotgroup_key to something like 
	### plotgroup_label.
	# For a BasicPlotGroupPanel, the plotgroup_key is the name passed at creation.
	# (e.g for testpattern it is 'Preview')
        # For a TemplatePlotGroupPanel, name is the name of the associated template 
        # For a ConnectionField or a Projection Panel, the plotgroup_key is re-generated
	self.plotgroup_key = plotgroup_key

        self.labels = []
        ### JCALERT! Figure out why we need that!
        self._num_labels = 0

        # Create and fill the 2 control Frames
	self.control_frame_1 = Frame(self)
        self.control_frame_1.pack(side=TOP,expand=YES,fill=X)
	self.control_frame_2 = Frame(self)
        self.control_frame_2.pack(side=TOP,expand=YES,fill=X)

        # JAB: Because these three buttons are present in nearly every
        # window, and aren't particularly important, we should
        # probably use small icons for them instead of text.  That way
        # they will form a visual group that users can typically
        # ignore.  Of course, the icons will need to announce their
        # names as help text if the mouse lingers over them, so that
        # the user can figure them out the first time.
        # 
       
        self.refresh_button = Button(self.control_frame_1,text="Refresh",
                                          command=self.refresh)
        self.refresh_button.pack(side=LEFT)
        self.balloon.bind(self.refresh_button,"Force the current plot to be regenerated.")
               
        # Auto_refresh check button.
        # Default is to not have the window Auto-refresh, because some
        # plots are very slow to generate (e.g. some preference map
        # plots).  Call self.auto_refresh.set(True) to enable
        # autorefresh in a subclassed constructor function.
	self.auto_refresh = BooleanVar()
	self.auto_refresh.set(False)
        if self.auto_refresh.get():
            self.console.auto_refresh_panels.append(self)
        self.auto_refresh_checkbutton = \
            Checkbutton(self.control_frame_1, text="Auto-refresh",
                        variable=self.auto_refresh,command=self.set_auto_refresh)
        self.auto_refresh_checkbutton.pack(side=RIGHT)
        self.balloon.bind(self.auto_refresh_checkbutton,
            "Whether to regenerate this plot whenever the simulation time advances.")

        # Main Plot group title can be changed from a subclass with the
        # command: self.plot_group.configure(tag_text='NewName')
	self.plot_group_title = Pmw.Group(self,tag_text=str(self.plotgroup_key))
        self.plot_group_title.pack(side=TOP,expand=YES,fill=BOTH,padx=5,pady=5)
	self.plot_frame = self.plot_group_title.interior()

        ### JABALERT! Need to implement scrollbars for viewing plots
        ### too large for the screen.
	# JC: A way of implementing it. Needs more work: for the moment,
        # the window expands without the scrollbar, but does not when the scrollbar is on.
# 	self.scrollbar = Pmw.ScrolledFrame(self,borderframe=0,
# 					   horizflex = 'elastic', vertflex='elastic',
# 					   hscrollmode = 'dynamic', vscrollmode = 'dynamic')
# 	self.scrollbar.pack(side=TOP,expand=YES,fill=X)
#       self.plot_frame = self.scrollbar.interior()
        
        self.control_frame = Frame(self)
        self.control_frame.pack(side=TOP,expand=YES,fill=X)

	# Hotkey for killing the window
	self.parent.bind('<Control-q>',self.parent_destroy)


    def refresh(self,update=True):
        """
        Main steps for generating plots in the Frame. 
	Must be re-implemented in sub-classes which save a history of the plots.
        """
        Pmw.showbusycursor()
	self.plotgroup = copy.copy(self.plotgroup)
	self.update_plotgroup_variables() # update PlotGroup variables
	# if update is True, the SheetViews are re-generated
	self.plotgroup.update_plots(update)
	self.display_plots()              # Put images in GUI canvas
        self.display_labels()             # Match labels to grid
        self.refresh_title()              # Update Frame title.
        Pmw.hidebusycursor()


    def refresh_title(self):
        """
        Change the window title.  TopoConsole will call this on
        startup of window.  
        """
        self.parent.title(topo.sim.name+': '+"%s time:%s" %
                          (self.plotgroup_key,self.plotgroup.time))
          
    def display_plots(self):
	"""Implemented in sub-classes."""
	pass


    def display_labels(self):
	"""Implemented in sub-classes."""
	pass


    def set_auto_refresh(self):
        """Function called by Widget when check-box clicked."""

        if self.auto_refresh.get():
            if not (self in self.console.auto_refresh_panels):
                self.console.auto_refresh_panels.append(self)
        else:
            if self in self.console.auto_refresh_panels:
                self.console.auto_refresh_panels.remove(self)
            
        # JAB: it might make sense for turning on auto-refresh
        # to do a refresh automatically, though that might have
        # unexpected behavior for a preference map calculation
        # (where it would do unnecessary, and potentially lengthy,
        # recalculation).
        
    def destroy(self):
        if self.auto_refresh.get():
            if self in self.console.auto_refresh_panels:
                self.console.auto_refresh_panels.remove(self)
        Frame.destroy(self)

    # The dummy argument makes the method signature match what is
    # required by the Control-q hotkey
    def parent_destroy(self,dummy):
	self.destroy()
	self.parent.destroy()


class PlotGroupPanel(BasicPlotGroupPanel):
    """
    Abstract PlotGroupPanel class for displaying bitmapped images to a TK
    GUI window.  Must be subclassed to be usable.

    Sub-classes BasicPlotGroupPanel and adds features to support
    displaying bitmap images (enlarge, reduce, integer_scaling,
    sheet_coordinates and normalize) and storing plot history.
    """
	
    def __init__(self,parent,console,plotgroup_key,**params):
        """
        parent:  it is the window (GUIToplevel()) that contains the panel.
        console: is the associated console, (i.e. the TopoConsole that has this panel)
        name: name associated with the panel
	"""
	BasicPlotGroupPanel.__init__(self,parent,console,plotgroup_key,**params)
      
        self.plotgroups_history=[]
        self.history_index = -1
	# indicate if we are currently looking into the past
	self.looking_in_history = False

         
        # Reduce, Enlarge, Back and Forward Buttons.
                      
        self.reduce_button = Button(self.control_frame_1,text="Reduce",
                                    command=self.reduce)
        self.reduce_button.pack(side=LEFT)
        self.balloon.bind(self.reduce_button,
            """
            Reduce the displayed size of the current plots by about 20%.  A
            minimum size that preserves at least one pixel per unit is enforced,
            to ensure that no data is lost when displaying.
            """)

        
        enlarge_button=Button(self.control_frame_1,text="Enlarge",
                              command=self.enlarge)
        enlarge_button.pack(side=LEFT)
        self.balloon.bind(enlarge_button,
            """Increase the displayed size of the current plots by about 20%.""")

        self.back_button = Button(self.control_frame_2,text="Back",
                                  state = DISABLED,command=self.back)
        self.back_button.pack(side=LEFT)
        self.balloon.bind(self.back_button,
            """
            Move backward through the history of all the plots shown in this
            window.  When showing a historical plot, some functions will be
            disabled, because the original data is no longer available.
            """)

        self.forward_button = Button(self.control_frame_2,text="Forward",
                                     state = DISABLED,
                                     command=self.forward)
        self.forward_button.pack(side=LEFT)
        self.balloon.bind(self.forward_button,
            "Move forward through the history of all the plots shown in this window.")

	# Normalize check button
	self.normalize = BooleanVar()
	self.normalize.set(False)
	self.normalize_checkbutton = Checkbutton(self.control_frame_1,
             text="Normalize",variable=self.normalize,command=self.set_normalize)
	self.normalize_checkbutton.pack(side=RIGHT)

        # Integerscaling check button
	self.integerscaling = BooleanVar()
	self.integerscaling.set(False)
	self.integerscaling_checkbutton = Checkbutton(self.control_frame_2,
             text="Integer scaling", variable=self.integerscaling,
             command=self.set_integerscaling)
        self.integerscaling_checkbutton.pack(side=RIGHT)
        self.sizeconvertfn = identity
        
	# Sheet coordinates check button
	self.sheetcoords = BooleanVar()
	self.sheetcoords.set(False)
	self.sheetcoords_checkbutton = Checkbutton(self.control_frame_2,
             text="Sheet coordinates",variable=self.sheetcoords,command=self.set_sheetcoords)
        self.sheetcoords_checkbutton.pack(side=RIGHT)
        self.sheetcoords_checkbutton.var=False
            
    	# Factor for reducing or enlarging the Plots (where 1.2 = 20% change)
	self.zoom_factor = 1.2
        
	self.plotgroup = self.generate_plotgroup()
        # For now, the balloon help needs to be separate from the buttons
        # above, because it depends on the plotgroup and they are needed
        # for creating the plotgroup.  All of this needs to be cleaned up
        # drastically.
        self.balloon.bind(self.normalize_checkbutton,
                          getdoc(self.plotgroup.params()['normalize']))
        self.balloon.bind(self.sheetcoords_checkbutton,
                          getdoc(self.plotgroup.params()['sheetcoords']))
        self.balloon.bind(self.integerscaling_checkbutton,
                          getdoc(self.plotgroup.params()['integerscaling']))


        ### Dynamic info about cursor location on plot
        # CEBALERT: the location of this widget is simply good luck: should position properly.
        self.dynamic_info = StringVar()
        Label(self,textvariable=self.dynamic_info).pack(side=TOP) #,font=("courier",12)

        ### Right-click menu for canvases; subclasses can add cascades
        ### or insert commands on the existing cascades.
        self._canvas_menu = Menu(self, tearoff=0)

        # sheet submenu
        self._canvas_menu.insert_cascade(1) 
        self._sheet_menu = Menu(self._canvas_menu)
        self._canvas_menu.entryconfig(1,menu=self._sheet_menu,state=DISABLED)

        # unit submenu
        self._canvas_menu.insert_cascade(0)
        self._unit_menu = Menu(self._canvas_menu)
        self._canvas_menu.entryconfig(0,menu=self._unit_menu,state=DISABLED)
        
        
        self._unit_menu.add_command(label='Connection Fields',
                                    command=self.__connection_fields_window)


               
    def __connection_fields_window(self):
        if 'plot' in self._right_click_info:
            plot = self._right_click_info['plot']
            x,y =  self._right_click_info['coords'][1]
            # CEBHACKALERT: should avoid requesting cf out of range.
            self.console.plots_menu_entries["Connection Fields"].command(x=x,y=y)


    def __process_canvas_event(self,event,func):
        """
        Return a dictionary containing the event itself, and, if the
        event occurs on a plot of a sheet, store the plot and the
        coordinates on the sheet.

        Then, call func.
        """
        # CB: I want this to be called for all the canvas events - see
        # ALERT by canvas button bindings. Surely can do better than
        # just passing func through.
        plot=event.widget.plot
        event_info = {'event':event} # store event in case more info needed elsewhere

        # Later functions assume that if event_info does not contain
        # 'plot', then the event did not occur on a plot of a sheet
        # (or occurred outside the sheet's bounds).  If sometime in
        # the future we want to do things for plots that do not have
        # sheets, then this can be changed (e.g. we can put in plot
        # but not coords, and use a check for coords to discover if
        # there is a sheet or not).
        
        if plot.plot_src_name is not '':
            canvas_x,canvas_y = event.x-CANVASBUFFER,event.y-CANVASBUFFER
            sf = plot.scale_factor
            canvas_r,canvas_c=int(floor(canvas_y/sf)),int(floor(canvas_x/sf))

            sheet = topo.sim[plot.plot_src_name]
            r,c = canvas_r,canvas_c 
            x,y = sheet.matrix2sheet(r,c)

            ## The plot doesn't correspond exactly to the sheet (there
            ## is some kind of border), so only store the plot and
            ## coords if we're actually on the sheet
            max_r,max_c = sheet.activity.shape
            if 0<=r<max_r and 0<=c<max_c:
                event_info['plot'] = plot
                event_info['coords'] = [(r,c),(x,y)]

        func(event_info)
        

    def _canvas_right_click(self,event_info,show_menu=True):
        """
        Update labels on right-click menu and popup the menu, plus store the event info
        for access by any menu commands that require it.

        If show_menu is False, popup menu is not displayed (in case subclasses
        wish to add extra menu items first).
        """        
        if 'plot' in event_info:
            plot = event_info['plot']

            self._canvas_menu.entryconfig(1,label="Combined plot: %s %s"%(plot.plot_src_name,plot.name),state=NORMAL)            
            (r,c),(x,y) = event_info['coords']
            self._canvas_menu.entryconfig(0,label="Single unit:(% 3d,% 3d) Coord:(% 2.2f,% 2.2f)"%(r,c,x,y),state=NORMAL)
            self._right_click_info = event_info

            if show_menu:
                self._canvas_menu.tk_popup(event_info['event'].x_root,
                                           event_info['event'].y_root)


    def __update_dynamic_info(self,event_info):
        """
        Update dynamic information.
        """
        if 'plot' in event_info:
            plot = event_info['plot']
            (r,c),(x,y) = event_info['coords']
            location_string="%s Unit:(% 3d,% 3d) Coord:(% 2.2f,% 2.2f)"%(plot.plot_src_name,r,c,x,y)
            # CB: isn't there a nicer way to allow more info to be added?
            self.dynamic_info.set(self._dynamic_info_string(event_info,location_string))
        else:
            self.dynamic_info.set("")

        
    def _dynamic_info_string(self,event_info,x):
        """
        Subclasses can override to add extra relevant information.
        """
        return x
        
   
    def generate_plotgroup(self):
	"""
	Function that creates the PlotGroupPanels's plotgroup.
	Needs to be reimplemented for subclasses.
	"""
	plotgroup = PlotGroup([],
			      normalize=self.normalize.get(),
			      sheetcoords=self.sheetcoords.get(),
			      integerscaling=self.integerscaling.get())
	return plotgroup


    def refresh(self,update=True):
        """
        Main steps for generating plots in the Frame.
        """
        super(PlotGroupPanel,self).refresh(update)
	self.add_to_history()             # Add current Plotgroup to history


    def update_plotgroup_variables(self):
	"""
	Update the variables of the plotgroup according to the panel's variables.
	Re-implemented for sub-classes.
	"""
	pass


    def display_plots(self):
        """
        Pre:  self.bitmaps contains a list of topo.bitmap objects.

        Post: The bitmaps have been displayed to the screen in the active
              console window.  All images are displayed from left to right,
              in a single row.  If the number of images have changed since
              the last display, the grid size is increased, or decreased
              accordingly.

        This function should be redefined in subclasses for interesting
        things such as 2D grids.
        """
	plots = self.plotgroup.plots
	### JCALERT: Temporary: delete when sorting the bitmap history
	self.bitmaps = [p.bitmap for p in plots]
	self.zoomed_images = [ImageTk.PhotoImage(p.bitmap.image) for p in plots]
        # If the number of canvases or their sizes has changed, then
        # create a new set of canvases.  If the old canvases still can
        # work, then reuse them to prevent flicker.
        if self.canvases and len(self.zoomed_images) > 0:
            new_sizes = [(str(zi.width()+BORDERWIDTH*2+CANVASBUFFER),
                          str(zi.height()+BORDERWIDTH*2+CANVASBUFFER))
                         for zi in self.zoomed_images]
            old_sizes = [(zi.config()['width'][-1],zi.config()['height'][-1])
                         for zi in self.canvases]
        else:
            new_sizes, old_sizes = 0, 0
        if len(self.zoomed_images) != len(self.canvases) or \
               new_sizes != old_sizes:
            old_canvases = self.canvases
            self.canvases = [Canvas(self.plot_frame,
                               width=image.width()+BORDERWIDTH*2+CANVASBUFFER,
                               height=image.height()+BORDERWIDTH*2+CANVASBUFFER,
                               bd=0)
                             for image in self.zoomed_images]
            for i,image,canvas in zip(range(len(self.zoomed_images)),
                                      self.zoomed_images,self.canvases):
                # BORDERWIDTH is added because the border is drawn on the
                # canvas, overwriting anything underneath it.
                # The +1 is necessary since the TKinter Canvas object
                # has a problem with axis alignment, and 1 produces
                # the best result.
                canvas.create_rectangle(1, 1, image.width()+BORDERWIDTH*2,
                                        image.height()+BORDERWIDTH*2,
                                        width=BORDERWIDTH,outline="black")
                canvas.create_image(image.width()/2+BORDERWIDTH+1,
                                    image.height()/2+BORDERWIDTH+1,
                                    image=image)
                canvas.config(highlightthickness=0,borderwidth=0,relief=FLAT)
                canvas.grid(row=0,column=i,padx=5)

                
            for c in old_canvases:
                c.grid_forget()
        else:  # Width of first plot still same, and same number of images.
            for i,image,canvas in zip(range(len(self.zoomed_images)),
                                      self.zoomed_images,self.canvases):
                canvas.create_image(image.width()/2+BORDERWIDTH+1,
                                    image.height()/2+BORDERWIDTH+1,image=image)
                canvas.grid(row=0,column=i,padx=5)

        ### bind events to each canvas
        for plot,canvas in zip(plots,self.canvases):
            # Store the corresponding plot with each canvas so that the
            # plot information (e.g. scale_factor) will be available
            # for the right_click menu.
            canvas.plot=plot
            # CEBALERT: I want process_canvas_event to be called for all of these bindings, with
            # an additional method also called to do something specific to the action. I'm sure
            # python has something that lets this be done in a clearer way.
            canvas.bind('<Button-3>',lambda event: self.__process_canvas_event(event,self._canvas_right_click))
            canvas.bind('<Motion>',lambda event: self.__process_canvas_event(event,self.__update_dynamic_info))

            canvas.bind('<Leave>',lambda event: self.__process_canvas_event(event,self.__update_dynamic_info))
            # When user has a menu up, it's often natural to click elsewhere to make the menu disappear. Need
            # to update the dynamic information in that case. (Happens on OS X anyway, but needed on Win and linux.)
            canvas.bind('<Button-1>',lambda event: self.__process_canvas_event(event,self.__update_dynamic_info))


        
            
            

    def add_to_history(self):
	"""
        If new_iteration is True, advances the plot history counter; otherwise
        just overwrites the current one.
	"""
	# if we hit refresh during a Back research, we do not want to copy the 
	# same PlotGroup two times in the history.
	if self.looking_in_history == True:
	    self.history_index = len(self.plotgroups_history)-1
	    self.plotgroups_history[self.history_index]=self.plotgroup	
	else:
	    self.plotgroups_history.append(self.plotgroup)
	    self.history_index = len(self.plotgroups_history)-1
	self.update_back_fwd_button()


    def set_normalize(self):
        """Function called by Widget when check-box clicked"""
	self.plotgroup.normalize = self.normalize.get()
	self.plotgroup.update_plots(False)
        self.display_plots()


    def set_integerscaling(self):
        """Function called by Widget when check-box clicked"""
 	self.plotgroup.integerscaling = self.integerscaling.get()
        if self.integerscaling.get():
            self.plotgroup.sizeconvertfn = int
        else:
            self.plotgroup.sizeconvertfn = identity
	self.plotgroup.update_plots(False)
        self.display_plots()


    ### Temporary; needs to be removed:  
    def update_back_fwd_button(self):	
	if (self.history_index > 0):
            self.back_button.config(state=NORMAL)
	    self.normalize_checkbutton.config(state=DISABLED)
	    self.sheetcoords_checkbutton.config(state=DISABLED)
	    self.integerscaling_checkbutton.config(state=DISABLED)
        else:
            self.back_button.config(state=DISABLED)

        if self.history_index >= len(self.plotgroups_history)-1:
            self.forward_button.config(state=DISABLED)
	    self.normalize_checkbutton.config(state=NORMAL)
	    self.sheetcoords_checkbutton.config(state=NORMAL)
	    self.integerscaling_checkbutton.config(state=NORMAL)
	    self.looking_in_history = False
        else:
            self.forward_button.config(state=NORMAL)


    def display_labels(self):
        """
        This function should be redefined by subclasses to match any
        changes made to display__plots().  Depending on the situation,
        it may be useful to make this function a stub, and display the
        labels at the same time the images are displayed.
        """
        if len(self.canvases) == 0:
            # If there are no plots yet, tell the user what to do.
            self.labels=[Label(self.plot_frame,text="""
              (Press Refresh to generate the plot, after
              modifying the commands below if necessary.
              Refreshing may take some time.  Many
              commands accept 'display=True' so that
              the progress can be viewed in an open
              Activity window, e.g. for debugging.)
              """)]
            self.labels[0].grid(row=1,column=0,sticky=NSEW)
                
        elif self._num_labels != len(self.canvases):
            old_labels = self.labels
            self.labels = [Label(self.plot_frame,text=each)
				 for each in self.plotgroup.labels]
            for i in range(len(self.labels)):
                self.labels[i].grid(row=1,column=i,sticky=NSEW)
            for l in old_labels:
                l.grid_forget()
            self._num_labels = len(self.canvases)
        else:  # Same number of labels; reuse to avoid flickering.
            for i in range(len(self.labels)):
                self.labels[i].configure(text=self.plotgroup.labels[i]) 
 
      

    def reduce(self):
        """Function called by Widget to reduce the plot size"""
        new_height = self.plotgroup.height_of_tallest_plot / self.zoom_factor
        if new_height < self.plotgroup.minimum_height_of_tallest_plot:
            self.reduce_button.config(state=DISABLED)
        else:
            self.change_plot_sizes(new_height)


    def enlarge(self):
        """Function called by Widget to increase the plot size"""
        new_height = self.plotgroup.height_of_tallest_plot * self.zoom_factor
        self.reduce_button.config(state=NORMAL)
        self.change_plot_sizes(new_height)

        
    def change_plot_sizes(self,new_height):
        """Set the plots to have a new maximum height"""
        if self.looking_in_history == True:
            self.plotgroup = self.plotgroups_history[self.history_index]
            self.plotgroup.height_of_tallest_plot = new_height
            self.plotgroup.scale_images()
        else:
            self.plotgroup.height_of_tallest_plot = new_height
            self.plotgroup.update_plots(False)
            
        self.display_plots()


    # JLENHANCEMENT: It would be nice to be able to scroll back through many
    # iterations.  Could put in a box for entering either the iteration
    # number you want to view, or perhaps how many you want to jump...
    def back(self):
        """Function called by Widget to scroll back through the previous bitmaps"""
  
	self.looking_in_history = True
        self.history_index -= 1
	self.update_back_fwd_button()
        self.plotgroup = self.plotgroups_history[self.history_index]
	self.display_plots()
        self.display_labels()
        self.refresh_title() 
	self.restore_panel_environment()
	self.update_back_fwd_button()
  


    def forward(self):
        """
        Function called by Widget to scroll forward through the bitmaps.
        Only useful if previously you have scrolled back.
        """
        self.history_index += 1
	self.plotgroup=self.plotgroups_history[self.history_index]
	self.display_plots()
        self.display_labels()
        self.refresh_title()
	self.restore_panel_environment()
	self.update_back_fwd_button()
	
    def restore_panel_environment(self):
	if self.plotgroup.normalize != self.normalize.get():
	    self.normalize_checkbutton.config(state=NORMAL)
	    self.normalize_checkbutton.invoke()
	    self.normalize_checkbutton.config(state=DISABLED)
	if self.plotgroup.sheetcoords != self.sheetcoords.get():
	    self.sheetcoords_checkbutton.config(state=NORMAL)
	    self.sheetcoords_checkbutton.invoke()
	    self.sheetcoords_checkbutton.config(state=DISABLED)
	if self.plotgroup.integerscaling != self.integerscaling.get():
	    self.integerscaling_checkbutton.config(state=NORMAL)
	    self.integerscaling_checkbutton.invoke()
	    self.integerscaling_checkbutton.config(state=DISABLED)
	

    def set_sheetcoords(self):
        """Function called by Widget when check-box clicked"""
	self.plotgroup.sheetcoords = self.sheetcoords.get()
	self.plotgroup.update_plots(False)
	self.display_plots()


 
