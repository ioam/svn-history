"""
File saving routines for plots.

Typically called using save_plotgroup in commands/analysis.py, but these
objects can also be instantiated explicitly, to save a series of plots.

$Id$
"""
__version__='$Revision$'

import Image
import ImageOps
import numpy

from topo.base.parameterizedobject import ParameterizedObject,Parameter
from topo.base.parameterclasses import Number, StringParameter

from plotgroup import PlotGroup,TemplatePlotGroup,ProjectionPlotGroup
from templates import plotgroup_templates

import topo

# Consider using PIL's ImageFont module


class PlotGroupSaver(ParameterizedObject):
    """
    Allows a PlotGroup to be saved as a set of bitmap files on disk.
    """

    file_format = StringParameter(default="png",doc="""
        Bitmap image file format to use.""")

    filename_prefix = StringParameter(default="",doc="""
        Optional prefix that can be used in the filename_format command
        to disambiguate different simulations or conditions.""")

    filename_format = StringParameter(default=
        "%(filename_prefix)s%(sim_name)s_%(time)09.2f_%(plot_label)s.%(file_format)s",doc="""
        Format string to use for generating filenames for plots.  This
        string will be evaluated in the context of a dictionary that
        defines various items commonly used when generating filenames,
        including::

          time:        the current simulation time (topo.sim.time())
          sim_name:    the name of the current simulation (topo.sim.name)
          plot_label:  the label specfied in the PlotGroup for this plot
          file_format: the bitmap image file format for this type of plot
      """)
    # Should move this out of plotfilesaver to get the same filenames in the GUI.
    # Should also allow each template in topo/commands/analysis.py to have a nice
    # short filename format, perhaps as an option.


    def __init__(self,plotgroup_label,**params):
        super(PlotGroupSaver,self).__init__(**params)
        self.plotgroup_label = plotgroup_label


    def generate_plotgroup(self):
	return PlotGroup([])


    def filename(self,label):
        """Calculate a specific filename from the filename_format."""
        
        self.sim_name = topo.sim.name
        self.time = topo.sim.time()
        self.plot_label=label
        vars = dict(self.get_param_values())
        vars.update(self.__dict__)
        
        return self.filename_format % vars
 

    def save_to_disk(self):
         for p,l in zip(self.plotgroup.plots,self.plotgroup.labels):
            p.bitmap.image.save(self.filename(l.replace('\n','_')))



class TemplatePlotGroupSaver(PlotGroupSaver):

    def __init__(self,pgt_name,**params):
        self.pgt = plotgroup_templates.get(pgt_name,None)
        super(TemplatePlotGroupSaver,self).__init__(pgt_name,**params)


    def generate_plotgroup(self):
	plotgroup = TemplatePlotGroup([],self.pgt,None)
	return plotgroup


# CEBALERT: Need to add Connection Fields plot
# class ConnectionFieldsPlotGroupSaver(TemplatePlotGroupSaver):
#     ...



# Could move this elsewhere if it will be useful.
#
# Adapted from:
# http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/412982
def make_contact_sheet(imgs, (marl,mart,marr,marb), padding):
    """
    Make a contact sheet (image grid) from a 2D array of PIL images::
    
      imgs     2D array of images
               
      marl     The left margin in pixels
      mart     The top margin in pixels
      marr     The right margin in pixels
      marb     The bottom margin in pixels

      padding  The padding between images in pixels

    Returns a PIL image object.
    """
    # should make sure imgs is numpy array
    
    # CB: *** should do this in numpy without the conversion to list and back! ***
    nrows,ncols = imgs.shape
    i_widths = numpy.array([i.size[0] for i in imgs.ravel()]).reshape(nrows,ncols)
    i_heights = numpy.array([i.size[1] for i in imgs.ravel()]).reshape(nrows,ncols)

    col_widths = i_widths.max(axis=0)
    row_heights = i_heights.max(axis=1)
    
    marw = marl+marr
    marh = mart+ marb

    padw = (ncols-1)*padding
    padh = (nrows-1)*padding

    isize = (col_widths.sum()+marw+padw, row_heights.sum()+marh+padh)

    # Create the new image. The background doesn't have to be white.
    white = (255,255,255)
    inew = Image.new('RGB',isize,white)

    # CB: should be replaced with a more numpy technique.        
    for irow in range(nrows):
        for icol in range(ncols):
            # if different widths in a col, or different heights in a
            # row, each image will currently just go at top left
            # defined by largest in col/row (should be centered
            # instead)
            left = marl+col_widths[0:icol].sum()+icol*padding
            right = left+i_widths[irow,icol]
            upper = mart+row_heights[0:irow].sum()+irow*padding
            lower = upper+i_heights[irow,icol] 
            inew.paste(imgs[irow,icol],(left,upper,right,lower))
    return inew




class CFProjectionPlotGroupSaver(TemplatePlotGroupSaver):

    sheet_name = Parameter(default="")
    projection_name = Parameter(default="")
    density = Number(default=10.0)

    def generate_plotgroup(self):
        ## CEBHACKALERT: the PlotGroups should check this stuff
        assert self.sheet_name in topo.sim.objects(), "no sheet %s" % self.sheet_name
        assert self.projection_name in topo.sim[self.sheet_name].projections().keys(),\
            "no proj %s for %s"%(self.projection_name,self.sheet_name)
        
 	plotgroup = ProjectionPlotGroup([],self.pgt,self.sheet_name,
					self.projection_name,
                                        self.density)
        return plotgroup


    def save_to_disk(self):
        imgs = numpy.array([p.bitmap.image for p in self.plotgroup.plots]).reshape(self.plotgroup.proj_plotting_shape)
        img = make_contact_sheet(imgs, (3,3,3,3), 3)
        img.save(self.filename(self.sheet_name+"_"+self.projection_name))



# Data structure to allow anyone to add special plotsaving_classes for
# any particular PlotGroup, or to override those defined here.  See
# plotpanel_classes in tkgui/topoconsole.py for a related structure
# used in the GUI.
# 
# By default, everything uses TemplatePlotGroupSaver unless that is
# overridden explicitly for a particular PlotGroup using this data
# structure.  This default is stored in plotsaving_classes[None], by
# convention.
plotsaving_classes = {}
plotsaving_classes[None] = TemplatePlotGroupSaver
plotsaving_classes['Projection'] = CFProjectionPlotGroupSaver
#plotsaving_classes['Connection Fields'] = ConnectionFieldsPlotGroupSaver
