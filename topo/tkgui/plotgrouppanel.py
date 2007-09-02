"""
Classes BasicPlotGroupPanel and PlotGroupPanel.

These classes provide GUI windows for PlotGroups, allowing sets of
related plots to be displayed.


$Id$
"""
__version__='$Revision$'

# CEBERRORALERT: I've (accidentally, temporarily) broken most of the
# buttons like normalize and sheet_coords...will be fixed when I clean
# up all the update methods.

import copy

from inspect import getdoc
from math import floor

import ImageTk
import Pmw

try:
    import bwidget
    bwidget_imported=True
except:
    bwidget_imported=False

import Tkinter, _tkinter
from Tkinter import  Frame, TOP, YES, BOTH, BOTTOM, X, Button, LEFT, \
     RIGHT, DISABLED, Checkbutton, NORMAL, Canvas, Label, NSEW, IntVar, \
     BooleanVar, StringVar, FLAT, SUNKEN, RAISED, GROOVE, RIDGE, \
     Scrollbar, Y, VERTICAL, HORIZONTAL, END, NO, NONE,Scrollbar,Canvas

import topo

from topo.base.parameterizedobject import ParameterizedObject
from topo.base.parameterclasses import BooleanParameter
from topo.base.sheet import Sheet

from topo.plotting.plotgroup import PlotGroup,SheetPlotGroup

from topo.commands.pylabplots import matrixplot

from tkguiwindow import TkguiWindow, Menu
from tkparameterizedobject import ButtonParameter, TkParameterizedObject


BORDERWIDTH = 1

# Unfortunately, the canvas creation, border placement, and image
# positioning of Tkinter are very fragile.  This value boosts the size
# of the canvas that the plot image is displayed on.  Too large and
# the border will not be close, too small, and some of the image is
# not displayed.  
CANVASBUFFER = 1




## CB: When I click off a text entry box after editing it (e.g. by
## clicking on some bit of unused window), my change should be
## applied. Currently, it is only applied if another widget gets the
## focus. So do something like make the background get the focus if
## it's clicked.
## I don't want this behavior in the model editor, though. Although both use
## ParametersFrame, a distinction is that in the Test Pattern window's
## ParametersFrame, there is no 'Apply' button (because we want changes to be
## applied immediately). So this indicates two different modes of use for
## ParametersFrame.

### CEBHACKALERT: something's funny with packing sometimes (e.g. open connection fields
### window, change params, then redraw). (It's to do with labels being left behind.)

### CEBHACKALERT: balloon help can show up on the wrong window!
### (Probably bound the balloon incorrectly somewhere.)
        


if bwidget_imported:
    class ResizableScrollableFrame(Tkinter.Frame):
        """
        A scrollable frame that can also be manually resized.
        
        Any normal scrollable frame will not resize automatically to
        accommodate its contents, because that would defeat the
        purpose of scrolling in the first place.  However, having a
        scrollable frame that can be resized manually is useful; this
        class adds easy resizing to a bwidget
        ScrollableFrame/ScrolledWindow combination.
        """
        def __init__(self,master,**config):
            """
            The 'contents' attribute is the frame into which contents
            should be placed (for the contents to be inside the
            scrollable area), i.e. almost all use of
            f=ResizableScrollableFrame(master) will be via f.contents.
            """
            Tkinter.Frame.__init__(self,master,**config)

            # non-empty Frames ignore any specified width/height, so create two empty
            # frames used purely for setting height & width
            self.__height_sizer = Frame(self,height=0,width=0)
            self.__height_sizer.pack(side=LEFT)
            self.__width_sizer = Frame(self,width=0,height=0)
            self.__width_sizer.pack()

            # the scrollable frame, with scrollbars
            self.__scrolled_window = bwidget.ScrolledWindow(self,auto="both",scrollbar="both")

            # set small start height/width, will grow if necessary
            scrolled_frame = bwidget.ScrollableFrame(self.__scrolled_window,height=50,width=50) 
            self.__scrolled_window.setwidget(scrolled_frame)
            self.__scrolled_window.pack(fill="both",expand='yes')

            # CB: tk docs say getframe() not necessary? Where did I see that?
            self.contents = scrolled_frame.getframe()


        def set_size(self,width=None,height=None):
            """
            Manually specify the size of the scrollable frame area.
            """
            self.__scrolled_window.pack_forget() # removing and redrawing stops stray scrollbars
            if width is not None: self.__width_sizer['width']=width
            if height is not None: self.__height_sizer['height']=height
            self.__scrolled_window.pack(fill="both",expand="yes")





class PlotGroupPanel(TkParameterizedObject,Frame):

    _abstract_class_name = "PlotGroupPanel"

    plotgroup_type = PlotGroup


    # Default is to not have the window Auto-refresh, because some
    # plots are very slow to generate (e.g. some preference map
    # plots).
    auto_refresh = BooleanParameter(default=False,doc="Whether to regenerate this plot whenever the simulation time advances.")
    # CEBALERT: (if someone clicks 'back' on a window, would
    # they expect auto-refresh to become unchecked/disabled?)

    Refresh = ButtonParameter(doc="Force the current plot to be regenerated (i.e. execute update_command and plot_command).")

    Redraw = ButtonParameter(doc="Redraw the plot from existing data (i.e. execute plot_command only).")

    Enlarge = ButtonParameter(doc="""Increase the displayed size of the current plots by about 20%.""")

    Reduce = ButtonParameter(doc=
            """
            Reduce the displayed size of the current plots by about 20%.  A
            minimum size that preserves at least one pixel per unit is enforced,
            to ensure that no data is lost when displaying.
            """)

    Fwd = ButtonParameter(doc="Move forward through the history of all the plots shown in this window.")

    Back = ButtonParameter(doc=
            """
            Move backward through the history of all the plots shown in this
            window.  When showing a historical plot, some functions will be
            disabled, because the original data is no longer available.
            """)
    
    
    # CB: Surely there's a better way?
    # Maybe we don't need the plotgroup attribute, since all the
    # plotgroup's attributes (e.g. self.plotgroup.a) are available via
    # this object itself (e.g. self.a). Will address this later...
    def get_plotgroup(self):
        return self._extraPO
    def set_plotgroup(self,new_pg):
        self._extraPO = new_pg
        #del self._extra_pos[0]
        #self.add_extra_po(new_pg)

    plotgroup = property(get_plotgroup,set_plotgroup,"""something something.""")

    ## CB: Rather than passing params for the PlotGroup in **params, have plotgroup_params
    ## and pass those to generate_plotgroup(**params)?
    def __init__(self,console,master,plotgroup_label,**params):
        """
        If your parameter should be available in history, add its name
        to the params_in_history list, otherwise it will be disabled
        in historical views.
        """
        TkParameterizedObject.__init__(self,master,extraPO=self.generate_plotgroup(),**params)
        Frame.__init__(self,master)

        self.plotgroup_label = plotgroup_label

        self.console=console

        self.canvases = []
        self.plot_labels = []

        ### JCALERT! Figure out why we need that!
        self._num_labels = 0
        

        self.plotgroups_history=[]
        self.history_index = 0
        self.params_in_history = [] # parameters valid to adjust in history
                              
            
    	# Factor for reducing or enlarging the Plots (where 1.2 = 20% change)
	self.zoom_factor = 1.2
        

        # -----------------------
        # | ------------------- |
        # | | control_frame_1 | |
        # | ------------------- |
        # |                     |
        # | ------------------- |
        # | | control_frame_2 | |
        # | ------------------- |
        # |                     |
        # | ------------------- |
        # | |                 | |
        # | |   plot_frame    | |
        # | |                 | |
        # | ------------------- |
        # |                     |
        # | ------------------- |
        # | | control_frame_3 | |
        # | ------------------- |
        # |                     |
        # |     messagebar      |
        # -----------------------  





        # CB: rename these frames
        self.control_frame_1 = Frame(self)
        self.control_frame_1.pack(side=TOP,expand=NO,fill=X)

	self.control_frame_2 = Frame(self)
        self.control_frame_2.pack(side=TOP,expand=NO,fill=X)


        #################### PLOT AREA ####################
        # Main Plot group title can be changed from a subclass with the
        # command: self.plot_group.configure(tag_text='NewName')
	self.plot_group_title = Pmw.Group(self,tag_text=self.plotgroup_label)
        self.plot_group_title.pack(side=TOP,expand=YES,fill=BOTH)#,padx=5,pady=5)
        
        if bwidget_imported:
            # max window size (works on all platforms? os x?)
            self.master.maxsize(self.winfo_screenwidth(),self.winfo_screenheight())
            self.__scroll_frame = ResizableScrollableFrame(self.plot_group_title.interior())
            self.__scroll_frame.pack()
            self.plot_frame = self.__scroll_frame.contents
        else:
            self.plot_frame = self.plot_group_title.interior()
        ###################################################       


        # control_frame_3 is:
        #
        # -----------------------
        # | updatecommand_frame |
        # |---------------------|
        # |  plotcommand_frame  |        
        # -----------------------


        self.control_frame_3 = Frame(self)
        self.control_frame_3.pack(side=TOP,expand=NO,fill=X)

        self.updatecommand_frame = Frame(self.control_frame_3)
        self.updatecommand_frame.pack(side=TOP,expand=YES,fill=X)

        self.plotcommand_frame = Frame(self.control_frame_3)
        self.plotcommand_frame.pack(side=TOP,expand=YES,fill=X)


        #################### DYNAMIC INFO BAR ####################
	self.messageBar = Pmw.MessageBar(self,entry_relief='groove')
	self.messageBar.pack(side=BOTTOM,fill=X,expand=NO,padx=4,pady=8)
        ##########################################################



        self.pack_param('update_command',parent=self.updatecommand_frame,
                        expand='yes',fill='x',side='left')

        self.pack_param('Refresh',parent=self.updatecommand_frame,
                        on_change=self.refresh,side='right')
        self.params_in_history.append('Refresh')

        self.pack_param('plot_command',parent=self.plotcommand_frame,
                        expand='yes',fill='x',side='left')
        # CEBALERT: should disable unless data exists.
        self.pack_param('Redraw',parent=self.plotcommand_frame,
                        on_change=self.redraw_plots,side='right')
        

        
        # JAB: Because the Refresh, Reduce, and Enlarge buttons are
        # present in nearly every window, and aren't particularly
        # important, we should probably use small icons for them
        # instead of text.  That way they will form a visual group
        # that users can typically ignore.  Of course, the icons will
        # need to announce their names as help text if the mouse
        # lingers over them, so that the user can figure them out the
        # first time.
    

        self.pack_param('auto_refresh',parent=self.control_frame_1,
                        on_change=self.set_auto_refresh,
                        side=RIGHT)
        self.params_in_history.append('auto_refresh')

        if self.auto_refresh: self.console.auto_refresh_panels.append(self)
            
        self.pack_param('Enlarge',parent=self.control_frame_1,
                        on_change=self.enlarge_plots,side=LEFT)
        self.params_in_history.append('Enlarge') # CEBNOTE: while it's a GUI op

        self.pack_param('Reduce',parent=self.control_frame_1,
                        on_change=self.reduce_plots,side=LEFT)
        self.params_in_history.append('Reduce')


        # Don't need to add these two to params_in_history because their
        # availability is controlled separately (determined by what's
        # in the history)
        self.pack_param('Back',parent=self.control_frame_2,
                        on_change=lambda x=-1: self.navigate_pg_history(x),
                        side=LEFT)

        self.pack_param('Fwd',parent=self.control_frame_2,
                        on_change=lambda x=+1: self.navigate_pg_history(x),
                        side=LEFT)




        #################### RIGHT-CLICK MENU STUFF ####################
        ### Right-click menu for canvases; subclasses can add cascades
        ### or insert commands on the existing cascades.
        self._canvas_menu = Menu(self, tearoff=0) #self.context_menu 

        self._unit_menu = Menu(self._canvas_menu, tearoff=0)
        self._canvas_menu.add_cascade(menu=self._unit_menu,state=DISABLED,
                                      indexname='unit_menu')
        
        self._sheet_menu = Menu(self._canvas_menu, tearoff=0)
        self._canvas_menu.add_cascade(menu=self._sheet_menu,state=DISABLED,
                                      indexname='sheet_menu') 
        

        ## CEBHACKALERT: got to control when menu options show. No good asking
        ## for connection fields of a connection field! Or asking for connection
        ## fields of a sheet that's not a cf sheet. And so on...
        
        self._unit_menu.add_command(label='Connection Fields',indexname='connection_fields',
                                    command=self.__connection_fields_window)
                                    
        self._unit_menu.add_command(label='Receptive Field',indexname='receptive_field',
                                    command=self.__receptive_field_window)                             
                                    
                                    
        #################################################################

        # CB: don't forget to include ctrl-q
        # import __main__; __main__.__dict__['qqq']=self


    # CB: rename to _generate_plotgroup()
    def generate_plotgroup(self):
	"""
        Create this Panel's PlotGroup.

        Reimplement in subclasses that must perform additional setup of their
        PlotGroup (e.g. populating Parameter ranges).
	"""
        return self.plotgroup_type()

 
    def set_auto_refresh(self):
        """Function called by Widget when check-box clicked."""
        if self.auto_refresh: 
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
        # CB: not to mention the bad news of calling refresh before
        # various subclasses have finished creating themselves!


    def __connection_fields_window(self):
        if 'plot' in self._right_click_info:
            sheet = topo.sim[self._right_click_info['plot'].plot_src_name]
            x,y =  self._right_click_info['coords'][1]
            # CEBHACKALERT: should avoid requesting cf out of range.
            self.console['Plots']["Connection Fields"](x=x,y=y,sheet=sheet)
            
    def __receptive_field_window(self):
        if 'plot' in self._right_click_info:
            try:
                plot = self._right_click_info['plot']
                x,y =  self._right_click_info['coords'][0]
                sheet = topo.sim[plot.plot_src_name]
                # CB: not sure how title works for matrixplot - might need to be formatted better
                matrixplot(topo.analysis.featureresponses.grid[sheet][x,y],title=("Receptive Field",sheet.name,x,y))
            except KeyError:
                topo.sim.warning("No RF measurements are available yet; run the Receptive Fields plot before accessing this right-click menu option.")

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


    def _update_dynamic_info(self,event_info):
        """
        Update dynamic information.
        """

        if 'plot' in event_info:
            plot = event_info['plot']
            (r,c),(x,y) = event_info['coords']
            location_string="%s Unit:(% 3d,% 3d) Coord:(% 2.2f,% 2.2f)"%(plot.plot_src_name,r,c,x,y)
            # CB: isn't there a nicer way to allow more info to be added?
            self.messageBar.message('state', self._dynamic_info_string(event_info,location_string))
        else:
            self.messageBar.message('state',"")

        

        
    def _dynamic_info_string(self,event_info,x):
        """
        Subclasses can override to add extra relevant information.
        """
        return x
        

    def conditional_refresh(self):
        """
        Only calls refresh() if auto_refresh is enabled.
        """
        if self.auto_refresh:self.refresh()


    # CEBALERT: Now clean up the update, redraw, refresh methods in here
    # and in plotgroup.
    def update_plots(self):
        
        # shouldn't call this from within history unless you've copied
        # the plotgroup (as in refresh)
        
        # assert self.history_index==0,"Programming error: can't
        # update plotgroup while looking in history." # (never update
        # plots in the history, or they go to current activity)

        self.plotgroup.draw_plots(update=True)
        self.display_plots()
        self.refresh_title()
        
        #self.display_labels()
    def redraw_plots(self):
        self.plotgroup.draw_plots(update=False)
        #self.display_plots()  # ?


    def refresh(self,update=True):
        """
        Main steps for generating plots in the Frame. 
	Must be re-implemented in sub-classes which save a history of the plots.

        # if update is True, the SheetViews are re-generated
        """
        Pmw.showbusycursor()

        # if we've been looking in the history, now need to return to the "current time"
        # plotgroup (but copy it: don't update the old one, which is a record of the previous state)
        if self.history_index!=0:
            self.plotgroup = copy.copy(self.plotgroups_history[-1])


        if update:
            self.update_plots()            
        else:
            self.redraw_plots()


	self.display_plots()              # Put images in GUI canvas
        self.display_labels()             # Match labels to grid
        self.refresh_title()              # Update Frame title.

        self.add_to_history()             
        
        self.update_widgets()
        Pmw.hidebusycursor()



    # CEBALERT: this method needs cleaning, along with its versions in subclasses.
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
	self.zoomed_images = [ImageTk.PhotoImage(p.bitmap.image) for p in plots]
        # If the number of canvases or their sizes has changed, then
        # create a new set of canvases.  If the old canvases still can
        # work, then reuse them to prevent flicker.
        if self.canvases and len(self.zoomed_images) > 0:
            new_sizes = [(str(zi.width()+BORDERWIDTH*2+CANVASBUFFER),
                          str(zi.height()+BORDERWIDTH*2+CANVASBUFFER))
                         for zi in self.zoomed_images]
            old_sizes = [(zi['width'],zi['height'])
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
            canvas.bind('<<right-click>>',lambda event: self.__process_canvas_event(event,self._canvas_right_click))
            canvas.bind('<Motion>',lambda event: self.__process_canvas_event(event,self._update_dynamic_info))

            canvas.bind('<Leave>',lambda event: self.__process_canvas_event(event,self._update_dynamic_info))
            # When user has a menu up, it's often natural to click elsewhere to make the menu disappear. Need
            # to update the dynamic information in that case. (Happens on OS X anyway, but needed on Win and linux.)
            canvas.bind('<Button-1>',lambda event: self.__process_canvas_event(event,self._update_dynamic_info))



        self.sizeright()
        


    def display_labels(self):
        """
        This function should be redefined by subclasses to match any
        changes made to display__plots().  Depending on the situation,
        it may be useful to make this function a stub, and display the
        labels at the same time the images are displayed.
        """
        
        if len(self.canvases) == 0:
            # If there are no plots yet, tell the user what to do.
            self.plot_labels=[Label(self.plot_frame,text="""
              (Press Refresh to generate the plot, after
              modifying the commands below if necessary.
              Refreshing may take some time.  Many
              commands accept 'display=True' so that
              the progress can be viewed in an open
              Activity window, e.g. for debugging.)
              """)]
            self.plot_labels[0].grid(row=1,column=0,sticky=NSEW)

        elif self._num_labels != len(self.canvases):
            old_labels = self.plot_labels
            self.plot_labels = [Label(self.plot_frame,text=each)
				 for each in self.plotgroup.labels]
            for i in range(len(self.plot_labels)):
                self.plot_labels[i].grid(row=1,column=i,sticky=NSEW)
            for l in old_labels:
                l.grid_forget()
            self._num_labels = len(self.canvases)
        else:  # Same number of labels; reuse to avoid flickering.
            for i in range(len(self.plot_labels)):
                self.plot_labels[i].configure(text=self.plotgroup.labels[i]) 

        self.sizeright()
      

    def reduce_plots(self):
        """Function called by widget to reduce the plot size, when possible."""
        if (not self.plotgroup.scale_images(1.0/self.zoom_factor)):
            self.representations['Reduce']['widget']['state']=DISABLED
        self.representations['Enlarge']['widget']['state']=NORMAL
        self.display_plots()

    def enlarge_plots(self):
        """Function called by widget to increase the plot size, when possible."""
        if (not self.plotgroup.scale_images(self.zoom_factor)):
            self.representations['Enlarge']['widget']['state']=DISABLED
        self.representations['Reduce']['widget']['state']=NORMAL
        self.display_plots()


####################### HISTORY METHODS ##########################         
    # CEBHACKALERT: currently, any click on refresh adds to history
    def add_to_history(self):
        self.plotgroups_history.append(copy.copy(self.plotgroup))
        self.history_index=0
        self.update_widgets() 

    def update_widgets(self):
        """
        The plotgroup's non-history widgets are all irrelevant when the plotgroup's from
        history.
        """
        if self.history_index!=0: 
            state= 'disabled'
        else:
            state = 'normal'

        
        widgets_to_update = [self.representations[p_name]['widget'] for p_name in self.representations
                             if p_name not in self.params_in_history]

        for widget in widgets_to_update:
            try:  ### CEBHACKALERT re TaggedSlider: doesn't support state! Need to be
                  ### able to disable taggedsliders, so that class needs modifying.
                  ### Plus, when TSs are changed, need to handle refreshing properly.
                widget['state']=state
            except _tkinter.TclError:
                pass

        ## CEBHACKALERT: necessary to update the gui.
        ## Instead of this, need to handle replacing an extra PO properly in
        ## tkparameterizedobject.
        ## CB: huh?
        for n in self.representations:
            self._tk_vars[n].get() 
        

        self.update_history_buttons()


    def update_history_buttons(self):
        space_back = len(self.plotgroups_history)-1+self.history_index
        space_fwd  = -self.history_index 

        back_button = self.representations['Back']['widget']
        forward_button = self.representations['Fwd']['widget']
        
        if space_back>0:
            back_button['state']='normal'
        else:
            back_button['state']='disabled'

        if space_fwd>0:
            forward_button['state']='normal'
        else:
            forward_button['state']='disabled'

        
    # JLENHANCEMENT: It would be nice to be able to scroll back through many
    # iterations.  Could put in a box for entering either the iteration
    # number you want to view, or perhaps how many you want to jump...
    def navigate_pg_history(self,steps):
        self.history_index+=steps
        
        self.plotgroup = self.plotgroups_history[len(self.plotgroups_history)-1+self.history_index]

        self.update_widgets()
        
 	self.display_plots()
        self.display_labels()
        self.refresh_title()
        
###########################################################         


    # CEBHACKALERT
    def title(self,t):
        # assumes Frame is in a window dedicated to that Frame
        self.master.title(t)

    def _plot_title(self):
        """
        Provide a string describing the current plot.

        Override in subclasses to provide more information.
        """
        return "%s at time %s"%(self.plotgroup_label,self.plotgroup.time)

                
    # rename to refresh_titles
    def refresh_title(self):
        """
        Set Window title and plot frame's title.
        """
        title = self._plot_title()
        
        self.plot_group_title.configure(tag_text=title)
        window_title = "%s: %s"%(topo.sim.name,title)
        self.title(window_title)

          
    def destroy(self):
        """overrides toplevel destroy, adding removal from autorefresh panels"""
        if self.console and self in self.console.auto_refresh_panels:
            self.console.auto_refresh_panels.remove(self)
        Frame.destroy(self)


    # CB: rename, document, and if possible delay showing the window until all the jiggling is over
    def sizeright(self):
        if bwidget_imported:
            self.master.geometry('') # if user has changed window size, need to tell tkinter that it should take
                              # control again.
            self.update_idletasks()
        
            # CB: the +'s are hacks, because for some reason the requested values aren't quite
            # large enough (noticably when there are labels).
            w = min(self.plot_frame.winfo_reqwidth()+30,self.winfo_screenwidth())
            # The - is to prevent the plot engulfing the rest of the plot window, obscuring controls at the bottom
            # (not so important right now, since plots would rarely be as large as the screen height)
            h = min(self.plot_frame.winfo_reqheight()+20,self.winfo_screenheight()-250)
            
            self.__scroll_frame.set_size(w,h)







class XPGPanel(PlotGroupPanel):

    plotgroup_type = SheetPlotGroup
    

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
        

    def __init__(self,console,master,plotgroup_label,**params):
        super(XPGPanel,self).__init__(console,master,plotgroup_label,**params)

        self.pack_param('normalize',parent=self.control_frame_1,
                        on_change=self.redraw_plots,side="right")
        # Actually, these could simply call scale_images(), skipping redrawing...
        self.pack_param('integer_scaling',parent=self.control_frame_2,
                        on_change=self.redraw_plots,side='right')
        self.pack_param('sheet_coords',parent=self.control_frame_2,
                        on_change=self.redraw_plots,side='right')
        


