"""
File saving routines for plots.

Currently unimplemented.  When implemented, will need to be able to save
the Plots in a PlotGroup into files on disk, choosing meaningful names
for each file.

$Id$
"""
__version__='$Revision$'



### Currently being written

# (revision 1.33 can actually be used to plot activities and preference maps)



# Plan:
# - get working for activity, orientation pref, projection
#   (The next thing that needs to happen is just to adjust
#   CFProjectionPlotGroupSaver's "make_contact_sheet" method to position
#   different sized CFs properly. And then,the arguments should be
#   filled in.)

# - clean up
# - add cf



# PIL has ImageFont module




import topo
from topo.base.parameterizedobject import ParameterizedObject,Parameter

from plotgroup import PlotGroup,TemplatePlotGroup,ProjectionPlotGroup
from templates import plotgroup_templates

class PlotGroupSaver(ParameterizedObject):

    file_format = Parameter(default="PNG")

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

import Image
from topo.base.parameterclasses import Number

import ImageOps
import numpy

# produce a projection plot 
# ./topographica -g examples/cfsom_or.ty -c "from topo.plotting.plotfilesaver import *; p = CFProjectionPlotGroupSaver('Projection');p.projection_name='Afferent';p.sheet_name='V1';p.plotgroup=p.generate_plotgroup();p.plotgroup.update_plots(True); i = p.make_contact_sheet((10,10),(3,3,3,3),3); i.show()"

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
        # need to format e.g. time like it's done elsewhere with some leading 0s
        n = topo.sim.name
        t = topo.sim.time()

        sheet = topo.sim[self.sheet_name]
        proj = topo.sim[self.sheet_name].projections()[self.projection_name]

        i = self.make_contact_sheet( self.plotgroup.proj_plotting_shape, (3,3,3,3), 3)

        name = "%s.%s.%s"%(n,t,self.projection_name)
        
        i.save(self.filename_prefix+name+".%s"%self.file_format,self.file_format)



    # Adapting from:
    # http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/412982
    # 
    def make_contact_sheet(self,(ncols,nrows),
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
        imgs = numpy.array([p.bitmap.image for p in self.plotgroup.plots]).reshape(nrows,ncols)

        # CB: *** should do this in numpy without the conversion to list and back! ***
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

       


