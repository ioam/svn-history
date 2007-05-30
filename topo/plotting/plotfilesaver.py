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
            p.bitmap.image.save(name+".%s"%self.file_format,self.file_format)



class TemplatePlotGroupSaver(PlotGroupSaver):

    def __init__(self,pgt_name,**params):
        self.pgt = plotgroup_templates.get(pgt_name,None)
        super(TemplatePlotGroupSaver,self).__init__(pgt_name,**params)

    def generate_plotgroup(self):
	plotgroup = TemplatePlotGroup([],self.pgt,None)
	return plotgroup

import Image
from topo.base.parameterclasses import Number




# produce a projection plot (all cfs same size)...
# ./topographica -g examples/cfsom_or.ty -c "from topo.plotting.plotfilesaver import *; p = CFProjectionPlotGroupSaver('Projection');p.projection_name='Afferent';p.sheet_name='V1';p.plotgroup=p.generate_plotgroup();p.plotgroup.update_plots(True); i = p.make_contact_sheet((10,10),(40,40),(10,10,10,10),3); i.show()

class CFProjectionPlotGroupSaver(TemplatePlotGroupSaver):

    sheet_name = Parameter(default="")
    projection_name = Parameter(default="")
    density = Number(default=10.0)

    def generate_plotgroup(self):
 	plotgroup = ProjectionPlotGroup([],self.pgt,self.sheet_name,
					self.projection_name,
                                        self.density)
        return plotgroup



    # Almost straight from:
    # http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/412982
    # 
    # shows how to make a composite image
    # should be easy to modify to do what we want.
    def make_contact_sheet(self,(ncols,nrows),(photow,photoh),
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

        # Read in all images and resize appropriately
        #imgs = [Image.open(fn).resize((photow,photoh)) for fn in fnames]

        imgs = [p.bitmap.image for p in self.plotgroup.plots]


        # **temp: resize all the same at the moment.
        imgs = [i.resize((photow,photoh)) for i in imgs]


        # Calculate the size of the output image, based on the
        #  photo thumb sizes, margins, and padding
        marw = marl+marr
        marh = mart+ marb

        padw = (ncols-1)*padding
        padh = (nrows-1)*padding
        isize = (ncols*photow+marw+padw,nrows*photoh+marh+padh)

        # Create the new image. The background doesn't have to be white
        white = (255,255,255)
        inew = Image.new('RGB',isize,white)

        # Insert each thumb:
        for irow in range(nrows):
            for icol in range(ncols):
                left = marl + icol*(photow+padding)
                right = left + photow
                upper = mart + irow*(photoh+padding)
                lower = upper + photoh
                bbox = (left,upper,right,lower)
                try:
                    img = imgs.pop(0)
                except:
                    print "doh"
                    break
                inew.paste(img,bbox)
        return inew


