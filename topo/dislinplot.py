"""
 Dislin Plotting interface.  Started August 2003 by Judah De Paula for
 the Topographica project.

 Requirements:
 * Needs dislin to be installed.
 * Needs Python's PIL to be installed.

 Development Assumptions:
 * Currently does not delete files after generation as I assume the
   caller will delete it when they are done.
 * Only accepts color BMP files as the background images.

 Problems:
 * TIFF output can only generate 256 colors if the background image is
   to be scaled properly.  But this procedure limits the postscript
   output to 256 as well.  Two methods of scaling are required:  If
   you want postscript truecolor output, call set_dislin_scale(True)
   but if you want something that is semi-useable then call
   set_dislin_scale(False)

 Porting
 * On Darwin, the Python 2.2 installed does not have the True/False
   flags defined.  Once defined in each module 'True, False = 1, 0'
   then it will run on that platform.

 Contour Colors:
 To change the contour colors, change the third parameter of
 set_layer(..) to an integer value between 0 and 255.  0 is Black,
 255 is White.  No code changes are necessary as this feature was
 anticipated.


 THINGS THAT COULD BE TURNED INTO FUNCTIONS, BUT JIM DIDN'T THINK
 WAS REQUIRED:

 Axis Labels (On/Off):
 Currently labels are always displayed.  To turn them off search for
 AXIS LABELS in a comment.  Comment out the dislin name command to turn
 them off.

 Axis Ticks:
 Currently tick marks are set to the default.  To turn them off:
 search for AXIS TICKS in a comment and uncomment the two lines there.

 Axis Titles:
 Currently axes always have titles.  To not display them search for
 AXIS TITLES and comment out the two lines found there.  Like I said
 earlier, a function could do this.

 Vectors:
 There is a commented line that shows how to display a vector.  Search
 for 'vector' to see how it works.  linwid() allows the trailing line
 to thicken.

 Bounding Box:
 The original bounding box gave room for labels, titles, and tick marks
 But if that is assumed to be gone, the defaults allow a tighter box
 Seach for BOUNDINGBOX for the commented out originals.
 
 <Insert other useful information here>

"""

import math, dislin, Image, ImageOps

class DislinPlot:
    """
    Each DislinPlot is in charge of a single plot instance.  Since most
    of the member data is reconfigurable one only needs to have one
    DislinPlot object in memory, however it is easier to switch between
    two plots by having multiple instances.
    """
    
    # By adding a format entry here, other file types can be added
    # easily.  You need to give the different values for each dictionary
    # entry, and that should be enough.  The setfil is only a base, as
    # Dislin changes the name to something else if the file already
    # exists.
    xwin = {'setfil'   : 'nofile.txt',  # Quickly added.  Symetric w/ TIFF
            'metafl'   : 'xwin',
            'scrmod'   : 'NOREV',       # 
            'fcolor'    : 'black',
            'bcolor'   : 255,           #
            'needcrop' : True}
    tiff = {'setfil'   : 'dislinplot.tiff',
            'metafl'   : 'tiff',
            'scrmod'   : 'NOREV',       # Or REVERSE
            'fcolor'    : 'black',
            'bcolor'   : 255,           # White, 0 is Black
            'needcrop' : True}
    postscript = {'setfil'   : 'dislinplot.eps',
                  'metafl'   : 'eps',
                  'scrmod'   : 'NOREV',
                  'fcolor'    :'black', # For the axis color
                  'bcolor'   : 255,     # White, 0 is Black
                  'needcrop' : False}
    format = {'xwin'       : xwin,
              'tiff'       : tiff,
              'postscript' : postscript}
              
    def __init__(self):
        # Default settings for plot generation.  Gives a little whitespace
        # around all edges for labels, Titles, ticks, etc. BOUNDINGBOX
        #self.PAGE_SQUARE = 2000
        #self.AXIS_HT = 1500
        #self.AXIS_WT = 1500
        #self.AXIS_XPOS = 300
        #self.AXIS_YPOS = self.PAGE_SQUARE - 300

        # Tightest box possible so don't try adding things outside window.
        self.PAGE_SQUARE = 1770
        self.AXIS_HT = 1500
        self.AXIS_WT = 1500
        self.AXIS_XPOS = 230
        self.AXIS_YPOS = self.PAGE_SQUARE - 165

        # xlow/ylow          --  Value of lowest x/y coordinate on axis
        # xhigh/yhigh        --  Value of largest x/y coordinate on axis
        # xlabst/ylabst      --  x/y coordinates of first labels on axis
        # xlabstep/ylabstep  --  Steps between labels on respective axis
        # Default sets these to the bitmap size once it is loaded
        self.xlow, self.xhigh, self.xlabst, self.xlabstep = 0., 360., 0., 90.
        self.ylow, self.yhigh, self.ylabst, self.ylabstep = 0., 360., 0., 90.

        # These are defaults that should be replaced by the user:
        self.BITMAP_SQUARE = 600          # 100 pixels per inch estimated
        #self.display = 'tiff'
        self.dislinscale = False
        self.display = 'postscript'          # Set to a name in self.format
        self.infilename = 'dislindriver.bmp' # Base name.  May be different.
        self.outfilename = None              # Output filename.  Must be set.
        self.xaxis_name = 'X-Axis Title'     # X Axis Title
        self.yaxis_name = 'Y-Axis Title'     # Y Axis Title
        self.layers = []               # (label, threshold, color)
        self.grid = []                 # Holding matrix for data points
        self.xgrid, self.ygrid = 0, 0  # Dimension of x and y in self.grid

        # Not yet implemented so turn off the pre-crop zoom.
        self.BITMAP_CROP_RATIO = 2./3.    # Trim excess page off bitmaps
        self.PRECROP_SQUARE = self.BITMAP_SQUARE # Crop not implemented yet
        #self.PRECROP_SQUARE = int(self.BITMAP_SQUARE / self.BITMAP_CROP_RATIO)


    def set_dislin_scale(self, value):
        """
        Use Dislin's built in image insert if set to True for full color.
        Use Topographica's scale for lower colors, but scaled in rasters.
        """
        self.dislinscale = value
        

    def set_bitmap_size(self, size):
        """
        Set the size of the output bitmaps for zooming or shrinking.  The
        default is to set it to 600 pixels by 600 pixels.
        """
        self.PRECROP_SQUARE = size
        

    def set_display(self, disp='postscript'):
        """
        Set the output file format type.  You currently have two choices:
        'tiff' or 'postscript'.  The default is postscript if you do not
        call this function or you do not pass in a parameter
        """
        self.display = disp


    def set_input_bmpfile(self,name):
        """
        Set the filename for the input file.  Currently must be of the
        BMP file format.
        """
        self.infilename = name        

    def set_output_filename(self,name):
        """
        Set the output filename of the plot.  The output name may be
        different if the filename already exists.  To make sure this is
        the actual name, be sure to remove any files with the same name
        first.
        """
        self.outfilename = name


    def set_xname(self, name):
        """
        Set new x-axis name
        """
        self.xaxis_name = name


    def set_yname(self, name):
        """
        Set new y-axis name
        """
        self.yaxis_name = name


    def add_layer(self, label, threshold, color):
        """
        Add a contour layer.  Default is for no layers.
        label can be the string "FLOAT" or "NONE"
        threshold is the numeric value between layers
        color is an integer that indexes the Dislin
        color table.  0 is Black, 255 is White.
        """
        self.layers.append((label, threshold, color))


    def add_grid(self, xlen, ylen, ingrid):
        """
        ingrid is the array of values that make up the contour plot.  
        xlen and ylen are the dimensions of ingrid
        """
        self.xgrid, self.ygrid, self.grid = xlen, ylen, ingrid
        

    def __scale_and_post(self, post_x, post_y, scale_x, scale_y, filename):
        """
        Algorithm to scale up an image.  No guarantee that this is bug-free
        as I wrote it quickly.  Should not need to be called by instance
        users.   Used because dislin can only scale under postscript and
        pdf so we needed it for bitmaps and now use it always to maintain
        consistency.
        """
        post_y = post_y + 0    # Possible need for axis adjustment
        dislin.frame(0)        # Turn off frames if set.  Really should reset
        dislin.shdpat(16)      # Set the fill pattern to solid
        # Read in sample .PPM file using PIL
        image = Image.open(filename)
        bwimage = ImageOps.grayscale(image)
        (width, height) = image.size

        # Set the Axis labels according to the number of pixels
        self.xlow, self.ylow, self.xhigh, self.yhigh = 0, 0, width-1, height-1
        self.xlabst, self.ylabst = 0, 0
        self.xlabstep, self.ylabstep = 20, 20

        cur_y, pixel_y = 0, 0
        while pixel_y < height:
            left_in_image = height - pixel_y
            left_on_screen = scale_y - cur_y
            stretch_y = int(round(left_on_screen / float(left_in_image)))
            cur_x, pixel_x = 0, 0

            while pixel_x < width:
                ximage = width - pixel_x
                xscreen = scale_x - cur_x
                stretch_x = int(round(xscreen / float(ximage)))

                # Let it guess an approximation or not
                #dislin.setclr(bwimage.getpixel((pixel_x,pixel_y)))

                #pix = image.getpixel((pixel_x,pixel_y))
                #dislin.setrgb(pix[0]/255.,pix[1]/255.,pix[2]/255.)

                # Authors say this will do truecolor:
                pixel = image.getpixel((pixel_x,pixel_y))
                pixr = pixel[0] / 256.
                pixg = pixel[1] / 256.
                pixb = pixel[2] / 256.
                dislin.setind(100,pixr,pixg,pixb)
                dislin.setclr(100)
                

                dislin.rectan(post_x+cur_x,post_y+cur_y,stretch_x,stretch_y)
                cur_x = cur_x + stretch_x
                pixel_x = pixel_x + 1

            cur_y = cur_y + stretch_y
            pixel_y = pixel_y + 1

        

    def genplot(self):
        """
        Generate plot using the values currently stored in the object
        instance.
        """
        dislin.setfil (self.outfilename)
        dislin.metafl (self.format[self.display]['metafl'])
        dislin.scrmod (self.format[self.display]['scrmod'])
        dislin.imgfmt('RGB')   # Change default from 256 palette for tiffs

        # Default is 100 points per centimeter for the display
        # Default is 100 pixels per inch for TIFF: making equal
        dislin.tifmod (100,'CM','RESOLUTION')
        dislin.page   (self.PAGE_SQUARE, self.PAGE_SQUARE)
        
        # The resolution of the output raster image file.
        # This does not affect postscript output.  Oversize the image
        # so that the crop will be the requested size. Dislin sets
        # the Tiff to 2/3 of the page.  Don't know how to unset it.
        dislin.winsiz (self.PRECROP_SQUARE,self.PRECROP_SQUARE)
        dislin.disini ()
        #dislin.setvlt('SPEC')
        
        # Turned off frame once all borders have been understood.
        # dislin.pagera ()
        dislin.complx ()
        dislin.helve ()

        dislin.intax  ()
        dislin.axspos (self.AXIS_XPOS, self.AXIS_YPOS)
        dislin.axslen (self.AXIS_WT, self.AXIS_HT)
        dislin.color  (self.format[self.display]['fcolor'])
        dislin.pagfll (self.format[self.display]['bcolor'])

        # Settings special to postscript
        if self.display == 'postscript':
            dislin.psfont('HELVETICA')
        if self.dislinscale:
            image = Image.open(self.infilename)
            (width, height) = image.size
            self.xlow, self.ylow, self.xhigh, self.yhigh = 0,0,width-1,height-1
            self.xlabst, self.ylabst = 0, 0
            self.xlabstep, self.ylabstep = 20, 20
            dislin.filbox (self.AXIS_XPOS, self.AXIS_YPOS - self.AXIS_HT,
                           self.AXIS_WT, self.AXIS_HT)
            dislin.incfil (self.infilename)
        else:
            # Have to do my own scaling for bitmaps otherwise I would use
            # the built-in:
            self.__scale_and_post(self.AXIS_XPOS,
                                  self.AXIS_YPOS - self.AXIS_HT,
                                  self.AXIS_WT,self.AXIS_HT,self.infilename)

        dislin.color  (self.format[self.display]['fcolor'])

        # AXIS TITLES comment out next two lines for no axis titles
        dislin.name   (self.xaxis_name, 'X')
        dislin.name   (self.yaxis_name, 'Y')
        
        # AXIS LABELS Uncomment next two lines for no axis numbers in plot
        #dislin.labels ('NONE','X')
        #dislin.labels ('NONE','Y')
        
        # AXIS TICKS  Uncomment to turn off or change tick marks
        #dislin.ticks  (0,'X')
        #dislin.ticks  (0,'Y')

        dislin.linwid (5)
        dislin.graf   (self.xlow, self.xhigh, self.xlabst, self.xlabstep,
                       self.ylow, self.yhigh, self.ylabst, self.ylabstep)
        dislin.linwid (1)
        dislin.height (30)

        # Sample the matrix space for scaling across the axis range
        xaxisrange = self.xhigh - self.xlow
        yaxisrange = self.yhigh - self.ylow
        stepx = []
        stepy = []
        for i in range(self.xgrid):
            curstep = round(xaxisrange/(self.xgrid-1) * i)
            stepx.append(curstep)
        for i in range(self.ygrid):
            curstep = round(yaxisrange/(self.ygrid-1) * i)
            stepy.append(curstep)

        dislin.linwid (7)
        # Said contour width could also be set with: dislin.thkcrv

        # Draw layers that have been added
        for lev in self.layers:
            dislin.labels (lev[0], 'CONTUR')
            dislin.setclr (lev[2])

            dislin.contur (stepx, self.xgrid,
                           stepy, self.ygrid, self.grid, lev[1])

        # Vector example
        #dislin.color('Black')
        #dislin.linwid (15)
        #dislin.vector(560,500,700,750,1701)

        # Options are 'WARNINGS', 'CHECK', 'PROTOCOL' and 'ALL'.  Toggle: 'ON', 'OFF'
        # Have turned off Protocol (File writing notifcation) but Warnings should still
        # work.
        dislin.errmod ('PROTOCOL','OFF')
        dislin.errmod ('WARNINGS','ON')
        dislin.errmod ('CHECK','ON')
        # Options are 'FILE', or 'CONS'
        # dislin.errdev ('FILE')

        actual_filename = dislin.getfil()
        dislin.disfin ()

        ## Here should be the TIFF crop code segment if it is going to be
        ## implemented.
        return actual_filename
###################
