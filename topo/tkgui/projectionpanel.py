"""
Projection Panel for TK GUI visualization.

$Id$
"""
__version__='$Revision$'




from Tkinter import StringVar, BooleanVar, Frame, YES, LEFT, TOP, RIGHT
from Tkinter import X, Message, Entry, Canvas, FLAT, Checkbutton, NORMAL, DISABLED

import Pmw
import ImageTk

### JCALERT! Try not to have to use chain and delete this import.
from itertools import chain

import topo
from topo.misc.keyedlist import KeyedList
from topo.base.cf import CFSheet, CFProjection
from topo.plotting.templates import plotgroup_templates
from topo.plotting.plotgroup import ProjectionPlotGroup

from templateplotgrouppanel import TemplatePlotGroupPanel


### JCALERT! See if we could delete this import * and replace it...
#from topo.commands.analysis import *



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


# CEBALERT: the class hierarchy and naming is not finished!  Initially
# I'm just removing duplicate code and cleaning up (including
# documenting).  After that it will be much easier to get the classes
# right.
# I'm making assumptions about CFs explicit, even if we'd like a class
# to be more general eventually.
#

# CEBHACKALERT: I've caused (uncovered?) a bug: sheets other than
# CFSheets are having their Projection views requested when
# CFProjectionPanel and ConnectionFieldsPanel are created. The
# _set_situate() method is where the error comes from (the plotgroup
# not being correct at the time it calls refresh(). This bug should go
# away during my cleanup.


class SomethingPanel(TemplatePlotGroupPanel):

    def __init__(self,console,pgt_name,**params):


        self.sheet_var = StringVar()
        super(SomethingPanel,self).__init__(console,pgt_name,**params)


        self._params_frame = Frame(master=self)
        self._params_frame.pack(side=LEFT,expand=YES,fill=X)

        self._add_sheet_menu() # CEBALERT: need situate button to be left of this, not right
        self.auto_refresh.set(False) # panels can be slow to refresh


    @staticmethod
    def valid_context():
        """
        Return True if there are CFProjections in the simulation.

        Used by TopoConsole to determine whether or not to open a SomethingPanel.
        """
        cfsheets = topo.sim.objects(CFSheet).values()
        if not cfsheets:
            return False

        cfprojectionlists=[cfsheet.in_connections for cfsheet in cfsheets]
        cfprojections=[i for i in chain(*cfprojectionlists)]
        return (not cfprojections == [])



    def _add_sheet_menu(self):
        """
        Add a menu to self._params_frame for selecting a sheet from
        those available in the simulation.
        """
        cfsheets = topo.sim.objects(CFSheet).values()
        
	cfsheets.sort(lambda x, y: cmp(-x.precedence,-y.precedence))
        self.sheet_var.set(cfsheets[0].name)

        # The GUI label says Sheet, not CFSheet, because users probably 
        # don't need to worry about the distinction.
        self.sheet_menu = Pmw.OptionMenu(self._params_frame,
                       command = self.refresh,
                       labelpos = 'w',
                       label_text = 'Sheet:',
                       menubutton_textvariable = self.sheet_var,
                       items=[cfsheet.name for cfsheet in cfsheets])
        self.sheet_menu.pack(side=LEFT)
        self.balloon.bind(self.sheet_menu,
"""CFSheet whose unit(s) will be plotted.""")


    def _add_situate_button(self):
        """
        Add 'situate' checkbutton to self._params_frame (and set to False)
        """        
	self.situate_var = BooleanVar()
        self.situate_var.trace_variable('w',lambda x,y,z: self.set_situate())
	#self.situate_var.set(False)
        self.situate_checkbutton = Checkbutton(self._params_frame,
             text="Situate",variable=self.situate_var)
        self.situate_checkbutton.pack(side=LEFT)
        self.balloon.bind(self.situate_checkbutton,
"""If True, plots the weights on the entire source sheet, using zeros for all
weights outside the ConnectionField.  If False, plots only the actual weights that
are stored.""")


    def set_situate(self):
        """Set the plotgroup.situate attribute, plus update and display plots."""
        if self.plotgroup != None: # CB: is this test required?
            self.plotgroup.situate = self.situate_var.get()
            self.plotgroup.initial_plot = True
            self.plotgroup.height_of_tallest_plot = self.min_master_zoom = 1
            self.plotgroup.update_plots(False)
            self.display_plots()

    



### JABALERT: This should be called CFProjectionPanel since it is only
### valid for CFProjections. We can consider having an abstract
### ProjectionPanel above this class, or at least a common parent
### for all the *Panel classes that share common code.
class CFProjectionPanel(SomethingPanel):
    def __init__(self,console=None,pgt_name=None,**params):
	self.projection_var = StringVar()
        self.projections = KeyedList()
	self.density_var = StringVar()
        self.density_var.set('10.0')
        super(CFProjectionPanel,self).__init__(console,pgt_name,**params)

 
        
        # self.MIN_PLOT_HEIGHT = 1
        # self.INITIAL_PLOT_HEIGHT = 6
        # self.min_master_zoom=1

        params_frame1 = Frame(master=self)
        params_frame1.pack(side=RIGHT,expand=YES,fill=X)
        pd = Message(params_frame1,text="Plotting Density:",aspect=1000)
        pd.pack(side=LEFT)
        self.balloon.bind(pd,'Number of units to plot per 1.0 distance in sheet coordinates')

        density_entry = Entry(params_frame1,textvariable=self.density_var)
        density_entry.bind('<FocusOut>', self.refresh)
        density_entry.bind('<Return>', self.refresh)
        density_entry.pack(side=LEFT,expand=YES,fill=X,padx=2)

        self._add_projection_menu()
        self._add_situate_button()
        
        self.refresh()
        


    ### JC: this function has to be re-written anyway...
    def _create_projection_dict(self,sheet_name):
        """
        Create a KeyedList of the CFProjections into sheet_name.  

        Does something else after that...
        """
        self.projections = [(p.name,p) for p in topo.sim[sheet_name].in_connections
                            if isinstance(p,CFProjection)]
        
        self.projections.sort(cmp_projections)

        ### JC: I don't know why self.projections is a KeyedList...
        self.projections = KeyedList(self.projections)

        old_projection_name = self.projection_var.get()
        if len(self.projections.keys()) == 0:
            self.projection_var.set('None')
        elif old_projection_name not in self.projections.keys():
            self.projection_var.set(self.projections.keys()[0])


    def _add_projection_menu(self):
        """
        Adds a Projection Widget to the existing frame, and creates the
        item list for Unit Projection names.  This needs to be
        changing based on which Sheet is selected.  See
        self.sheet_refresh() 
        """
        params_frame2 = Frame(master=self)
        params_frame2.pack(side=LEFT,expand=YES,fill=X)

        self._create_projection_dict(self.sheet_var.get())
       
        self.projection_menu = Pmw.OptionMenu(params_frame2,
                       command = self.refresh,
                       labelpos = 'w',
                       label_text = 'Projection:',
                       menubutton_textvariable = self.projection_var,
                       items = self.projections.keys())
        self.projection_menu.pack(side=LEFT)
        # Should be shared with projectionpanel
        self.balloon.bind(self.projection_menu,
"""Projection to plot.""")




        

    # CEBHACKALERT q
    def refresh(self,q=None):
        """
        Update the Projection menu.  This overwrites the parent class
        function CFSheetPlotPanel.sheet_refresh() which is called when
        the Sheet Widget menu is changed.
        """
        sheet_name = self.sheet_var.get()
        self._create_projection_dict(sheet_name)
        self.projection_menu.setitems(self.projections.keys())
        super(CFProjectionPanel,self).refresh()


    def refresh_title(self):
        self.title(topo.sim.name+': '+"Projection %s %s time:%s" % (self.plotgroup.sheet_name,
            self.plotgroup.weight_name,self.plotgroup.time))
        

    def update_plotgroup_variables(self):
        """
        Generate the key used to look up the PlotGroup for this Projection.

        The plotgroup_key for retrieving the PlotGroup depends on the
        values entered in the window widgets.  This method generates
        the appropriate key based on those values, using a tuple like:
        ('Projection', self.projection_var, self.density, self.sheet_var).
        """
	self.plotgroup.situate= self.situate_var.get()
	self.plotgroup.density = float(self.density_var.get())
	self.plotgroup.sheet_name=self.sheet_var.get()
	self.plotgroup.weight_name = self.projection_var.get()


    def generate_plotgroup(self):
        """
        self.generate_plotgroup_key() creates the density information needed for
        a ProjectionPlotGroup to create necessary Plots.
        """
 	plotgroup = ProjectionPlotGroup([],self._pg_template(),self.sheet_var.get(),
					self.projection_var.get(),
                                        float(self.density_var.get()),
                                        normalize=self.normalize.get(),
                                        sheetcoords=self.sheetcoords.get(),
                                        integerscaling=self.integerscaling.get())
  	return plotgroup


    def display_plots(self):
        """
        This must be changed from PlotGroupPanels version since
        CFProjectionPanel requires a 2D grid of plots.
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
            src_name = self.projections[self.projection_var.get()].src.name

            new_title = 'Projection ' + self.plotgroup.weight_name + ' from ' + src_name + ' to ' \
                        + self.plotgroup.sheet_name + ' at time ' + str(self.plotgroup.time)
            self.plot_group_title.configure(tag_text = new_title)
        else:
            self.plot_group_title.configure(tag_text = 'No Projections')
        

    def restore_panel_environment(self):
	super(CFProjectionPanel,self).restore_panel_environment()
	if self.plotgroup.situate != self.situate_var.get():
	    self.situate_checkbutton.config(state=NORMAL)
	    self.situate_checkbutton.invoke()
	    self.situate_checkbutton.config(state=DISABLED)

    def update_back_fwd_button(self):
	super(CFProjectionPanel,self).update_back_fwd_button()
	if (self.history_index > 0):
            self.situate_checkbutton.config(state=DISABLED)
	    ### JCALERT: Should find a way to disable the sheet menu
	    ### (What I tried below does not work)
	    ### Also, disabled the text for the xy_boxes (i.e., X,Y)
	    ## Also, when changing the menu while looking in history,
            ### it will replaced the old current one by the new one instead of adding
	    ### the new at the following.
	    #self.sheet_menu.config(state=DISABLED)

        if self.history_index >= len(self.plotgroups_history)-1:
	    self.situate_checkbutton.config(state=NORMAL)
	    #self.sheet_menu.config(state=NORMAL)


