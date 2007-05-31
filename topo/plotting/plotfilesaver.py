"""
File saving routines for plots.

Currently unimplemented.  When implemented, will need to be able to save
the Plots in a PlotGroup into files on disk, choosing meaningful names
for each file.

$Id$
"""
__version__='$Revision$'


# (see comments at the end of this file)
plotsaving_classes = {}


def save_plotgroup(name,**params):
    """
    Convenience command for saving a set of plots to disk.  Examples:

      save_plotgroup("Activity")
      save_plotgroup("Orientation Preference")
      save_plotgroup("Projection",projection_name='Afferent',sheet_name='V1')

    Some plotgroups accept optional parameters, which can be passed
    like projection_name and sheet_name above.
    """
    class_ = plotsaving_classes.get(name,TemplatePlotGroupSaver)
    p = class_(name,**params)
    print p.projection_name,p.sheet_name
    p.plotgroup=p.generate_plotgroup()
    p.plotgroup.update_plots(True)
    p.save_to_disk()


### Currently being written

# (any code written using these classes will have to be altered in the future)


### Examples
#
# Activity:
#./topographica -g examples/cfsom_or.ty -c "topo.sim.run(1); from topo.plotting.plotfilesaver import *; p = TemplatePlotGroupSaver('Activity');p.plotgroup=p.generate_plotgroup();p.plotgroup.update_plots(True);p.save_to_disk()"
#
# Projection:
#./topographica -g examples/cfsom_or.ty -c "from topo.plotting.plotfilesaver import *; p = CFProjectionPlotGroupSaver('Projection');p.projection_name='Afferent';p.sheet_name='V1';p.plotgroup=p.generate_plotgroup();p.plotgroup.update_plots(True);p.save_to_disk()"#
# Orientation Preference:
#./topographica -g examples/cfsom_or.ty -c "topo.sim.run(10); from topo.plotting.plotfilesaver import *; p = TemplatePlotGroupSaver('Orientation Preference');p.plotgroup=p.generate_plotgroup();p.plotgroup.update_plots(True);p.save_to_disk()"
#
# If you have an existing Plot?Saver p, you can use it again:
#  topo.sim.run(10)
#  p.plotgroup.update_plots();p.save_to_disk()


 
# Plan:
# - clean up
# - add cf



# PIL has ImageFont module




import topo
from topo.base.parameterizedobject import ParameterizedObject,Parameter

from plotgroup import PlotGroup,TemplatePlotGroup,ProjectionPlotGroup
from templates import plotgroup_templates


import ImageOps
import numpy

import Image
from topo.base.parameterclasses import Number


# move elsewhere, and give it some parameters etc
# Alos, maybe call something more specific than compositor, since
# it's jiust for building an array (grid) of images into one big image/
class ImageCompositor(ParameterizedObject):

    # Adapting from:
    # http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/412982
    def make_contact_sheet(self,imgs,
                       (marl,mart,marr,marb),
                       padding):
        """\
        Make a contact sheet from a group of filenames:
        
        fnames       A list of names of the image files

        ncols        Number of columns in the contact sheet
        nrows        Number of rows in the contact sheet
        photow       The width of the photo thumbs in pixels
        photoh       The height of the photo thumbs in pixels

        marl         The left margin in pixels
        mart         The top margin in pixels
        marr         The right margin in pixels
        marl         The left margin in pixels

        padding      The padding between images in pixels

        returns a PIL image object.
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

        # Create the new image. The background doesn't have to be white
        white = (255,255,255)
        inew = Image.new('RGB',isize,white)

        # CB: should be replaced with a more numpy technique.        
        for irow in range(nrows):
            for icol in range(ncols):
                # if different widths in a col, or different heights in a row,
                # each image will just go at top left defined by largest in col/row
                # (should probably be centered)
                left = marl+col_widths[0:icol].sum()+icol*padding
                right = left+i_widths[irow,icol]
                upper = mart+row_heights[0:irow].sum()+irow*padding
                lower = upper+i_heights[irow,icol] 
                inew.paste(imgs[irow,icol],(left,upper,right,lower))
        return inew




class PlotGroupSaver(ParameterizedObject):

    file_format = Parameter(default="png")

    filename_prefix=Parameter(default="")
# filename_format:
#  "topo.sim.name+'.'+topo.sim.time()+'.'+current_sheet+'.'+current_plot+'.'+current_unit'"
# (Eventually we could customize this to allow each template in topo/commands/analysis.py
# to have a nice short filename format.)

    #filename_format = Parameter

    def __init__(self,plotgroup_label,**params):
        super(PlotGroupSaver,self).__init__(**params)
        self.plotgroup_label = plotgroup_label
        #self.plotgroup = self.generate_plotgroup()
        #self.plotgroup.update_plots(True)

    def generate_plotgroup(self):
	return PlotGroup([])
 
    def save_to_disk(self):
        # need to format e.g. time like it's done elsewhere with some leading 0s
        n = topo.sim.name
        t = topo.sim.time()
        for p,l in zip(self.plotgroup.plots,self.plotgroup.labels):
            name = "%s.%s.%s"%(n,t,l.replace('\n','.'))
            #print "outfile",name
            p.bitmap.image.save(self.filename_prefix+name+".%s"%self.file_format,self.file_format)



class TemplatePlotGroupSaver(PlotGroupSaver):

    def __init__(self,pgt_name,**params):
        self.pgt = plotgroup_templates.get(pgt_name,None)
        super(TemplatePlotGroupSaver,self).__init__(pgt_name,**params)

    def generate_plotgroup(self):
	plotgroup = TemplatePlotGroup([],self.pgt,None)
	return plotgroup



class CFProjectionPlotGroupSaver(TemplatePlotGroupSaver):

    sheet_name = Parameter(default="")
    projection_name = Parameter(default="")
    density = Number(default=10.0)

    def generate_plotgroup(self):
 	plotgroup = ProjectionPlotGroup([],self.pgt,self.sheet_name,
					self.projection_name,
                                        self.density)
        return plotgroup


    def save_to_disk(self):
        

        imgs = numpy.array([p.bitmap.image for p in self.plotgroup.plots]).reshape(self.plotgroup.proj_plotting_shape)

        i = ImageCompositor().make_contact_sheet(imgs, (3,3,3,3), 3)
        
        
        n = topo.sim.name
        t = topo.sim.time()

        sheet = topo.sim[self.sheet_name]
        proj = topo.sim[self.sheet_name].projections()[self.projection_name]

        name = "%s.%s.%s"%(n,t,self.projection_name)
        
        i.save(self.filename_prefix+name+".%s"%self.file_format,self.file_format)


# plotsaving_classes is like plotpanel_classes in tkgui/topoconsole.py;
# it allows anyone to add their own special plotsaving_classes for any
# particular PlotGroup.  By default, everything uses TemplatePlotGroupSaver
# unless that is overridden explicitly for a particular PlotGroup using
# this data structure.
plotsaving_classes['Projection'] = CFProjectionPlotGroupSaver
#plotsaving_classes['Connection Fields'] = ConnectionFieldsPlotGroupSaver
