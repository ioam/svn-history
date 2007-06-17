"""
Projection Panel for TK GUI visualization.

$Id$
"""
__version__='$Revision$'


import ImageTk
### JCALERT! Try not to have to use chain and delete this import.
from itertools import chain
from Tkinter import Canvas, FLAT 

import topo

from topo.base.cf import CFSheet, CFProjection
from topo.base.projection import ProjectionSheet
from topo.base.parameterclasses import BooleanParameter

from topo.plotting.plotgroup import CFProjectionPlotGroup,ProjectionSheetPlotGroup,CFPlotGroup

from templateplotgrouppanel import TemplatePlotGroupPanel


### JCALERT! See if we could delete this import * and replace it...
#from topo.commands.analysis import *


def cmp_projections(p1,p2):
    """
    Comparison function for Plots.
    It compares the precedence number first and then the src_name and name attributes.
    """
    if p1.src.precedence != p2.src.precedence:
	return cmp(p1.src.precedence,p2.src.precedence)
    else:
	return cmp(p1,p2)


UNIT_PADDING = 1
BORDERWIDTH = 1

# JDALERT: The canvas creation, border placement, and image
# positioning of Tkinter is very fragile.  This value boosts the size
# of the canvas that the plot image is displayed on.  Too large and
# the border will not be close, too small, and some of the image is
# not displayed.
CANVASBUFFER = 1


# need some refreshing when changing params?

class ProjectionSheetPGPanel(TemplatePlotGroupPanel):
    """
    Abstract base class for panels relating to ProjectionSheets.
    """
    # CB: abstract

    plotgroup_type = ProjectionSheetPlotGroup
    sheet_type = ProjectionSheet

    auto_refresh = BooleanParameter(False) # these panels can be slow to refresh

    # CEBHACKALERT: valid_context() needs to be more specific in
    # subclasses.  How to allow valid_context() to work for more
    # specific subclasses (e.g. to replace ProjectionSheet with
    # CFSheet)?
    @staticmethod
    def valid_context():
        """
        Return True if there are Projections in the simulation.

        Used by TopoConsole to determine whether or not to open a ProjectionPanel.
        """
        sheets = topo.sim.objects(ProjectionSheet).values()
        if not sheets:
            return False
        projectionlists=[sheet.in_connections for sheet in sheets]
        projections=[i for i in chain(*projectionlists)]
        return (not projections == [])


    def __init__(self,console,master,pgt,**params):
        super(ProjectionSheetPGPanel,self).__init__(console,master,pgt,**params)
        self.pack_param('sheet',parent=self.control_frame_3,on_change=self.sheet_change)
        #self.refresh()


    def generate_plotgroup(self):
        p = self.plotgroup_type(template=self.pgt)
        self.populate_sheet_param(p)
        return p


    def sheet_change(self):
        pass
        # don't self.update_plots() because they have to select the projection first
        ## CEBHACKALERT: think it gets updated anywhere somewhere in the refresh+prjections part.

        
    def populate_sheet_param(self,p):
        sheets = topo.sim.objects(self.sheet_type).values() 
        sheets.sort(lambda x, y: cmp(-x.precedence,-y.precedence))
        p.params()['sheet'].range = sheets
        p.sheet = sheets[0]

        
   

class CFPGPanel(ProjectionSheetPGPanel):
    """
    Existence is dedicated to...a situate button! 
    """
    # CB: declare abstract

    sheet_type = CFSheet
    plotgroup_type = CFPlotGroup
    
    def __init__(self,console,master,pgt,**params):
        super(CFPGPanel,self).__init__(console,master,pgt,**params)
        self.min_master_zoom = 1
        self.pack_param('situate',parent=self.control_frame_3,on_change=self.situate_change)

# CEBALERT: can't this be simplified? what's min_master_zoom?
    def situate_change(self):
        if self.situate:
            self.plotgroup.initial_plot=True
            self.plotgroup.height_of_tallest_plot = self.min_master_zoom = 1
        else:
            pass
        self.redraw_plots()





class CFProjectionPGPanel(CFPGPanel):
    """
    Panel for displaying CFProjections.
    """

    plotgroup_type = CFProjectionPlotGroup

    def __init__(self,console,master,pgt,**params):
        super(CFProjectionPGPanel,self).__init__(console,master,pgt,**params)
        self.pack_param('projection',parent=self.control_frame_3,on_change=self.update_plots)
        self.pack_param('density',parent=self.control_frame_3)


    def generate_plotgroup(self):
        p = super(CFProjectionPGPanel,self).generate_plotgroup()        
        self.populate_projection_param(p)
        return p

    
    def refresh_title(self):
        self.title(topo.sim.name+': '+"Projection %s %s time:%s" % (self.plotgroup.sheet.name,
                                                                    self.projection.name,self.plotgroup.time))


    def sheet_change(self):
        self.refresh_projections()


    def populate_projection_param(self,p):
        prjns = p.sheet.projections().values() 
        prjns.sort(cmp_projections)
        p.params()['projection'].range = prjns
        p.projection = prjns[0]        

    def refresh_projections(self):
        self.populate_projection_param(self.plotgroup)
        
        # CB: How do you change list of tkinter.optionmenu options? Use pmw's optionmenu?
        # Currently, replace widget completely: looks bad and is complex.
        if 'projection' in self._widgets:
            self._widgets['projection'].destroy()
            self._furames['projection'][1].destroy()
            self.pack_param('projection',parent=self._furames['projection'][0])


    def display_plots(self):
        """
        CFProjectionPanel requires a 2D grid of plots.
        """
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
        # CB: not a gui thing + there'll be a problem when changing sheets
        src_name = self.projection.src.name
        
        new_title = 'Projection ' + self.projection.name + ' from ' + src_name + ' to ' \
                    + self.sheet.name + ' at time ' + str(self.plotgroup.time)
        
        self.plot_group_title.configure(tag_text = new_title)
            




