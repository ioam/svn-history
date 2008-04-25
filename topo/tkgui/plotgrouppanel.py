"""
Classes providing GUI windows for PlotGroups, allowing sets of related plots
to be displayed.

$Id$
"""
__version__='$Revision$'


import copy

from inspect import getdoc
from math import floor

import ImageTk

import Tkinter, _tkinter
from Tkinter import  Frame, TOP, YES, BOTH, BOTTOM, X, Button, LEFT, \
     RIGHT, DISABLED, Checkbutton, NORMAL, Canvas, Label, NSEW, IntVar, \
     BooleanVar, StringVar, FLAT, SUNKEN, RAISED, GROOVE, RIDGE, \
     Scrollbar, Y, VERTICAL, HORIZONTAL, END, NO, NONE,Scrollbar,Canvas, \
     TclError

import topo

from topo.base.parameterizedobject import ParameterizedObject
from topo.base.parameterclasses import BooleanParameter, Integer
from topo.base.sheet import Sheet
from topo.base.cf import CFSheet

from topo.plotting.plotgroup import PlotGroup,SheetPlotGroup

from topo.commands.pylabplots import matrixplot

from topo.sheets.generatorsheet import GeneratorSheet

from widgets import Menu,StatusBar,with_busy_cursor
from tkparameterizedobject import ButtonParameter, TkParameterizedObject


BORDERWIDTH = 1

# Unfortunately, the canvas creation, border placement, and image
# positioning of Tkinter are very fragile.  This value boosts the size
# of the canvas that the plot image is displayed on.  Too large and
# the border will not be close, too small, and some of the image is
# not displayed.  
CANVASBUFFER = 1

class PlotGroupPanel(TkParameterizedObject,Frame):

    __abstract = True


    dock = BooleanParameter(default=False,doc="on console or not")

    # Default size for images used on buttons
    button_image_size=(20,20)

    Refresh = ButtonParameter(image_path="topo/tkgui/icons/redo-small.png",
        size=button_image_size,
        doc="""
        Refresh the current plot (i.e. force the current plot to be regenerated
        by executing update_command and plot_command).""")

    Redraw = ButtonParameter(image_path="topo/tkgui/icons/redo-small.png",
        size=button_image_size,
        doc="""Redraw the plot from existing data (i.e. execute plot_command only).""")
    
    Enlarge = ButtonParameter(image_path="topo/tkgui/icons/viewmag+_2.2.png",
        size=button_image_size,
        doc="""Increase the displayed size of the current plots by about 20%.""")
                          
    Reduce = ButtonParameter(image_path="topo/tkgui/icons/viewmag-_2.1.png",
        size=button_image_size,doc="""
        Reduce the displayed size of the current plots by about 20%.
        A minimum size that preserves at least one pixel per unit is
        enforced, to ensure that no data is lost when displaying.""")

    Fwd = ButtonParameter(image_path="topo/tkgui/icons/forward-2.0.png",
        size=button_image_size,doc="""
        Move forward through the history of all the plots shown in this window.""")

    Back = ButtonParameter(image_path="topo/tkgui/icons/back-2.0.png",
        size=button_image_size,doc="""
        Move backward through the history of all the plots shown in
        this window.  When showing a historical plot, some functions
        will be disabled, because the original data is no longer
        available.""")
    
    gui_desired_maximum_plot_height = Integer(default=150,bounds=(0,None),doc="""
        Value to provide for PlotGroup.desired_maximum_plot_height for
        PlotGroups opened by the GUI.  Determines the initial, default
        scaling for the PlotGroup.""")
    
    # CB: is there a better way than using a property?
    def get_plotgroup(self):
        return self._extraPO
    def set_plotgroup(self,new_pg):
        self.change_PO(new_pg)
        
    plotgroup = property(get_plotgroup,set_plotgroup)


    def __init__(self,master,plotgroup,**params):
        """
        If your parameter should be available in history, add its name
        to the params_in_history list, otherwise it will be disabled
        in historical views.
        """
        
        TkParameterizedObject.__init__(self,master,extraPO=plotgroup,**params)
        Frame.__init__(self,master)
        
        self.setup_plotgroup()





        self.canvases = []
        self.plot_labels = []

        ### JCALERT! Figure out why we need that!
        self._num_labels = 0
        
        self.plotgroups_history=[]
        self.history_index = 0
        self.params_in_history = [] # parameters valid to adjust in history
                                  
    	# Factor for reducing or enlarging the Plots (where 1.2 = 20% change)
	self.zoom_factor = 1.2
        
        # CEBALERT: rename these frames
        self.control_frame_1 = Frame(self)
        self.control_frame_1.pack(side=TOP,expand=NO,fill=X)

	self.control_frame_2 = Frame(self)
        self.control_frame_2.pack(side=TOP,expand=NO,fill=X)

	self.plot_frame = Tkinter.LabelFrame(self,text=self.plotgroup.name)
        self.plot_frame.pack(side=TOP,expand=YES,fill=BOTH)#,padx=5,pady=5)        

        # CB: why did I need a new frame after switching to 8.5?
        # I've forgotten what i changed.
        self.plot_container = Tkinter.Frame(self.plot_frame)
        self.plot_container.pack(anchor="center")


        # Label does have a wraplength option...but it's in screen
        # units. Surely tk has a function to convert between
        # text and screen units?
        no_plot_note_text = """      
Press Refresh on the update command to generate the plot, after modifying the commands below if necessary. Note that Refreshing may take some time.

Many commands accept 'display=True' so that the progress can be viewed in an open Activity window, e.g. for debugging.
"""

        self.no_plot_note=Label(self.plot_container,text=no_plot_note_text,
                                justify="center",wraplength=350)
        self.no_plot_note_enabled=False


        self.control_frame_3 = Frame(self)
        self.control_frame_3.pack(side=TOP,expand=NO,fill=X)

        self.control_frame_4 = Frame(self)
        self.control_frame_4.pack(side=TOP,expand=NO,fill=NONE)

        self.updatecommand_frame = Frame(self.control_frame_3)
        self.updatecommand_frame.pack(side=TOP,expand=YES,fill=X)

        self.plotcommand_frame = Frame(self.control_frame_3)
        self.plotcommand_frame.pack(side=TOP,expand=YES,fill=X)


        #################### DYNAMIC INFO BAR ####################
	self.messageBar = StatusBar(self)
	self.messageBar.pack(side=BOTTOM,fill=X,expand=NO)
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
        
            
        self.pack_param('Enlarge',parent=self.control_frame_1,
                        on_change=self.enlarge_plots,side=LEFT)
        self.params_in_history.append('Enlarge') # CEBNOTE: while it's a GUI op

        self.pack_param('Reduce',parent=self.control_frame_1,
                        on_change=self.reduce_plots,side=LEFT)
        self.params_in_history.append('Reduce')

##         self.pack_param("dock",parent=self.control_frame_1,
##                         on_change=self.set_dock,side=LEFT)


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

        self._canvas_menu.add_separator()
        
        # CEBALERT: scheme for enabling/disabling menu items ('disable
        # items hack') needs to be generalized. What we have now is
        # just a mechanism to disable/enable cfs/rfs plots as
        # necessary. Hack includes the attribute below as well as
        # other items marked 'disable items hack'.
        # (Note that tk 8.5 has better handling of state switching
        # (using flags for each state, I think), so presumably this
        # can be cleaned up easily.)
        self._unit_menu_updaters = {}
        
        self._sheet_menu = Menu(self._canvas_menu, tearoff=0)
        self._canvas_menu.add_cascade(menu=self._sheet_menu,state=DISABLED,
                                      indexname='sheet_menu')
        self._canvas_menu.add_separator()


        self.update_plot_frame(plots=False)

        #################################################################

        # CB: don't forget to include ctrl-q
        # import __main__; __main__.__dict__['qqq']=self


    def set_dock(self):
        if self.dock:
            topo.guimain.some_area.consume(self._container)
            self.refresh_title()
        else:
            topo.guimain.some_area.eject(self._container)
            self.refresh_title()
            


    def setup_plotgroup(self):
        """
        Perform any necessary initialization of the plotgroup.

        Subclasses can use this to set Parameters on their PlotGroups.
        """
        self.plotgroup.desired_maximum_plot_height=self.gui_desired_maximum_plot_height
        

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

            self._canvas_menu.entryconfig("sheet_menu",
                label="Combined plot: %s %s"%(plot.plot_src_name,plot.name),
                state=NORMAL)            
            (r,c),(x,y) = event_info['coords']
            self._canvas_menu.entryconfig("unit_menu",
                label="Single unit:(% 3d,% 3d) Coord:(% 2.2f,% 2.2f)"%(r,c,x,y),
                state=NORMAL)
            self._right_click_info = event_info

            # CB: part of disable items hack
            for v in self._unit_menu_updaters.values(): v(plot)

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


    # rename (not specific to plot_frame)
    # document, and make display_* methods semi-private methods
    def update_plot_frame(self,plots=True,labels=True):
        
        if plots:
            self.plotgroup.scale_images()
            self.display_plots()
        if labels: self.display_labels()
        self.refresh_title()

        if len(self.canvases)==0:
            # CEB: check that pack's ok here
            self.no_plot_note.grid(row=1,column=0,sticky='nsew')
            self.no_plot_note_enabled=True
            self.representations['Enlarge']['widget']['state']=DISABLED
            self.representations['Reduce' ]['widget']['state']=DISABLED
            
        elif self.no_plot_note_enabled:
            self.no_plot_note.grid_forget()
            self.no_plot_note_enabled=False
            self.representations['Enlarge']['widget']['state']=NORMAL
            self.representations['Reduce' ]['widget']['state']=NORMAL

        self.__update_widgets_for_history()
        # have a general update_widgets method instead (that calls
        # update_widgets_for_history; can it also include
        # enlarge/reduce alterations?)

        # CBALERT: problem when docked: this event isn't being caught,
        # ie it doesn't end up going to the right place... (i.e. no
        # scrollbars when docked).
        self.event_generate("<<SizeRight>>")
        

    @with_busy_cursor
    def refresh_plots(self):
        """
        Call plotgroup's make_plots with update=True (i.e. run
        update_command and plot_command), then display the result.
        """
        self.plotgroup.make_plots(update=True)
        self.update_plot_frame()        
        self.add_to_plotgroups_history()


    @with_busy_cursor
    def redraw_plots(self):
        """
        Call plotgroup's make_plots with update=False (i.e. run only
        plot_command, not update_command), then display the result.
        """
        self.plotgroup.make_plots(update=False)
        self.update_plot_frame(labels=False)


    def rescale_plots(self):
        """
        Rescale the existing plots, without calling either the
        plot_command or the update_command, then display the result.
        """
        self.plotgroup.scale_images()
        self.update_plot_frame(labels=False)

    
    def refresh(self,update=True):
        """
        Main steps for generating plots in the Frame. 

        # if update is True, the SheetViews are re-generated
        """
        
        # if we've been looking in the history, now need to return to the "current time"
        # plotgroup (but copy it: don't update the old one, which is a record of the previous state)
        if self.history_index!=0:
            self._switch_plotgroup(copy.copy(self.plotgroups_history[-1]))
            self.history_index = 0

        if update:
            self.refresh_plots()            
        else:
            self.redraw_plots()



    # CEBALERT: this method needs cleaning, along with its versions in subclasses.
    def display_plots(self):
        """

        This function should be redefined in subclasses for interesting
        things such as 2D grids.
        """
        ### JABALERT: Can we make it simple to make plots be put onto multiple lines here?
	plots = self.plotgroup.plots
        
	self.zoomed_images = [ImageTk.PhotoImage(p.bitmap.image) for p in plots]


        new_sizes = [(str(zi.width()+BORDERWIDTH*2+CANVASBUFFER),
                      str(zi.height()+BORDERWIDTH*2+CANVASBUFFER))
                     for zi in self.zoomed_images]
        old_sizes = [(canvas['width'],canvas['height'])
                     for canvas in self.canvases]

        # If the number of canvases or their sizes has changed, then
        # create a new set of canvases.  If the new images will fit into the
        # old canvases, reuse them (prevents flicker)

        if len(self.zoomed_images) != len(self.canvases) or \
               new_sizes != old_sizes:
            # Need new canvases...
            old_canvases = self.canvases
            self.canvases = [Canvas(self.plot_container,
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


        else:
            # Don't need new canvases...
            for i,image,canvas in zip(range(len(self.zoomed_images)),
                                      self.zoomed_images,self.canvases):
                canvas.create_image(image.width()/2+BORDERWIDTH+1,
                                    image.height()/2+BORDERWIDTH+1,image=image)
                canvas.grid(row=0,column=i,padx=5)


                

        ### plotting over; bind events to each canvas
        for plot,canvas in zip(plots,self.canvases):
            # Store the corresponding plot with each canvas so that the
            # plot information (e.g. scale_factor) will be available
            # for the right_click menu.
            canvas.plot=plot
            # CEBALERT: I want process_canvas_event to be called for
            # all of these bindings, with an additional method also
            # called to do something specific to the action. I'm sure
            # python has something that lets this be done in a clearer
            # way.
            canvas.bind('<<right-click>>',lambda event: \
                        self.__process_canvas_event(event,self._canvas_right_click))
            canvas.bind('<Motion>',lambda event: \
                        self.__process_canvas_event(event,self._update_dynamic_info))

            canvas.bind('<Leave>',lambda event: \
                        self.__process_canvas_event(event,self._update_dynamic_info))
            # When user has a menu up, it's often natural to click
            # elsewhere to make the menu disappear. Need to update the
            # dynamic information in that case. (Happens on OS X
            # anyway, but needed on Win and linux.)
            canvas.bind('<Button-1>',lambda event: \
                        self.__process_canvas_event(event,self._update_dynamic_info))

        

        
        

    def display_labels(self):
        """
        This function should be redefined by subclasses to match any
        changes made to display__plots().  Depending on the situation,
        it may be useful to make this function a stub, and display the
        labels at the same time the images are displayed.
        """
        
        if len(self.canvases) == 0:
            pass
        elif self._num_labels != len(self.canvases):
            old_labels = self.plot_labels
            self.plot_labels = [Label(self.plot_container,text=each)
				 for each in self.plotgroup.labels]
            for i in range(len(self.plot_labels)):
                self.plot_labels[i].grid(row=1,column=i,sticky=NSEW)
            for l in old_labels:
                l.grid_forget()
            self._num_labels = len(self.canvases)
        else:  # Same number of labels; reuse to avoid flickering.
            for i in range(len(self.plot_labels)):
                self.plot_labels[i].configure(text=self.plotgroup.labels[i]) 

      

    # CEBERRORALERT (minor): if no plot's displayed and I click
    # enlarge, then the enlarge button gets disabled. If I then press
    # refresh to get a plot, I can't enlarge it because the button's
    # disabled. Probably need to reset button status if the plots
    # change.
    def reduce_plots(self):
        """Function called by widget to reduce the plot size, when possible."""
        if (not self.plotgroup.scale_images(1.0/self.zoom_factor)):
            self.representations['Reduce']['widget']['state']=DISABLED
        self.representations['Enlarge']['widget']['state']=NORMAL
        self.update_plot_frame(labels=False)

    def enlarge_plots(self):
        """Function called by widget to increase the plot size, when possible."""
        if (not self.plotgroup.scale_images(self.zoom_factor)):
            self.representations['Enlarge']['widget']['state']=DISABLED
        self.representations['Reduce']['widget']['state']=NORMAL
        self.update_plot_frame(labels=False)
        

######################################################################
### HISTORY METHODS

    # CEBERRORALERT: history grows and grows! Consider what happens when
    # a window's open with auto-refresh and many plots are generated
    # (e.g. measure_rfs). And plotgroups might be much bigger than they
    # need to be.

    # CEBALERT: in a history research, a disabled widget does not display
    # up-to-date information (e.g. normalize checkbutton doesn't change).
    def add_to_plotgroups_history(self):
        """
        If there are plots on display, and we're not doing a history research,
        the plotgroup is stored in the history.
        """
        if self.history_index==0 and not len(self.canvases)==0:
            self.plotgroups_history.append(copy.copy(self.plotgroup))
        self.__update_widgets_for_history() 

    def __set_widget_state(self,widget,state):
        # sets the widget's state to state, unless state=='normal'
        # and the widget's current state is 'readonly', in which
        # case readonly is preserved.
        # If a widget state was set to 'disabled' deliberately, this
        # will have the unwanted effect of enabling that widget.
        # Surely there's a better way than this!
        # (Probably the history stuff should store the old state
        # on the widget somewhere. That would also eliminate the
        # combobox-specific hack.)

        # CEBALERT: I guess some widgets don't have state?
        try:
            current_state = widget.configure('state')[3]
        except TclError:
            return

        ### hack to deal with combobox: see tkparameterizedobject's
        ###  create_selector_widget().
        if state=='normal':
            if hasattr(widget,'_readonly_'):
                state='readonly'
        ###########################################################
                            
        widget.configure(state=state)
            
        
    def __update_widgets_for_history(self):
        """
        The plotgroup's non-history widgets are all irrelevant when the plotgroup's from
        history.
        """
        if self.history_index!=0: 
            state= 'disabled'
        else:
            state = 'normal'
        
        widgets_to_update = [self.representations[p_name]['widget']
                             for p_name in self.representations
                             if p_name not in self.params_in_history]

        for widget in widgets_to_update:
            self.__set_widget_state(widget,state)
            
        self.__update_history_buttons()


    def __update_history_buttons(self):
        """
        Enable/disable the back and forward buttons depending on
        where we are in a history research.
        """
        space_back = len(self.plotgroups_history)+self.history_index-1
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
        self._switch_plotgroup(self.plotgroups_history[len(self.plotgroups_history)+self.history_index-1])
        self.update_plot_frame()

######################################################################


    def _switch_plotgroup(self,newpg):
        """
        Switch to a different plotgroup, e.g. one from the history buffer.
        Preserves some attributes from the current plotgroup that can apply
        across history, but leaves the others as-is.
        """
        oldpg=self.plotgroup
        
        newpg.desired_maximum_plot_height=oldpg.desired_maximum_plot_height
        newpg.sheet_coords=oldpg.sheet_coords
        newpg.integer_scaling=oldpg.integer_scaling
        
        self.plotgroup=newpg


###########################################################         



    def _plot_title(self):
        """
        Provide a string describing the current set of plots.

        Override in subclasses to provide more information.
        """
        return "%s at time %s"%(self.plotgroup.name,topo.sim.timestr(self.plotgroup.time))

                
    # rename to refresh_titles
    def refresh_title(self):
        """
        Set Window title and plot frame's title.
        """
        title = self._plot_title()
        
        self.plot_frame.configure(text=title)
        self.master.title(title.replace(" at time ","/"))

          
    def destroy(self):
        """overrides toplevel destroy, adding removal from autorefresh panels"""
        if topo.guimain.auto_refresh_panels:
            topo.guimain.auto_refresh_panels.remove(self)
        Frame.destroy(self)
            


class SheetPanel(PlotGroupPanel):    

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
        

    def __init__(self,master,plotgroup,**params):
        super(SheetPanel,self).__init__(master,plotgroup,**params)

        self.pack_param('auto_refresh',parent=self.control_frame_1,
                        on_change=self.set_auto_refresh,
                        side=RIGHT)
        self.params_in_history.append('auto_refresh')

        if self.auto_refresh:
            topo.guimain.auto_refresh_panels.append(self)


        self.pack_param('normalize',parent=self.control_frame_1,
                        on_change=self.redraw_plots,side="right")
        self.pack_param('integer_scaling',parent=self.control_frame_2,
                        on_change=self.rescale_plots,side='right')
        self.pack_param('sheet_coords',parent=self.control_frame_2,
                        on_change=self.rescale_plots,side='right')

        self.params_in_history.append('sheet_coords')
        self.params_in_history.append('integer_scaling')


        
        self._unit_menu.add_command(label='Connection Fields',indexname='connection_fields',
                                    command=self._connection_fields_window)
                                    
        self._unit_menu.add_command(label='Receptive Field',
                                    indexname='receptive_field',
                                    command=self._receptive_field_window)

###### part of disable items hack #####
        self._unit_menu_updaters['connection_fields'] = self.check_for_cfs
        self._unit_menu_updaters['receptive_field'] = self.check_for_rfs        

    def check_for_cfs(self,plot):
        show_cfs = False
        if plot.plot_src_name in topo.sim.objects():
            if isinstance(topo.sim[plot.plot_src_name],CFSheet):
                show_cfs = True
        self.__showhide("connection_fields",show_cfs)

    def check_for_rfs(self,plot):
        show_rfs = False
        if plot.plot_src_name in topo.sim.objects():
            sheet = topo.sim[plot.plot_src_name]

            # RFHACK: if any one generatorsheet has RF views for this sheet, then enable the menu option
            # At the moemnt, njust a hack to prevent menu option for generator sheets.
            if not isinstance(sheet,GeneratorSheet):
                show_rfs = True
            else:
                show_rfs = False

        self.__showhide("receptive_field",show_rfs)

    def __showhide(self,name,show):
        if show:
            state = 'normal'            
        else:
            state = 'disabled'
        self._unit_menu.entryconfig(name,state=state)
#######################################


    def set_auto_refresh(self):
        """
        Add or remove this panel from the console's
        auto_refresh_panels list.
        """
        if self.auto_refresh: 
            if not (self in topo.guimain.auto_refresh_panels):
                topo.guimain.auto_refresh_panels.append(self)
        else:
            if self in topo.guimain.auto_refresh_panels:
                topo.guimain.auto_refresh_panels.remove(self)


    def _connection_fields_window(self):
        """
        Open a Connection Fields plot for the unit currently
        identified by a right click.
        """
        if 'plot' in self._right_click_info:
            sheet = topo.sim[self._right_click_info['plot'].plot_src_name]
            x,y =  self._right_click_info['coords'][1]
            # CEBERRORALERT: should avoid requesting cf out of range.
            topo.guimain['Plots']["Connection Fields"](x=x,y=y,sheet=sheet)
            
    def _receptive_field_window(self):
        """
        Open a Receptive Field plot for the unit currently
        identified by a right click.
        """
        if 'plot' in self._right_click_info:
            plot = self._right_click_info['plot']
            x,y = self._right_click_info['coords'][1]
            sheet = topo.sim[plot.plot_src_name]
            center_x,center_y = sheet.closest_cell_center(x,y)

            # RFHACK:
            # just matrixplot for whatever generatorsheets have the views
            for g in topo.sim.objects(GeneratorSheet).values():
                try:
                    view=g.sheet_views[('RFs',sheet.name,center_x,center_y)]
                    matrixplot(view.view()[0],
                               title=("Receptive Field of %s unit (%2.2f,%2.2f) at time %s"% (sheet.name,center_x,center_y,topo.sim.timestr(view.timestamp))))
                except KeyError:
                    # maybe lose this warning
                    topo.sim.warning("No RF measurements are available yet for input_sheet %s; run the Receptive Field plot for that input_sheet to see the RF."%g.name)

    def conditional_refresh(self):
        """
        Only calls refresh() if auto_refresh is enabled.
        """
        if self.auto_refresh:self.refresh()

    def conditional_redraw(self):
        """
        Only calls redraw_plots() if auto_refresh is enabled.
        """
        if self.auto_refresh:self.redraw_plots()
