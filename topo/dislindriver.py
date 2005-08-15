"""
Driver program to call DislinPlot with some sample plots.  This way it
can be tested independently of Topographica proper.

This file is NOT yet integrated into Topographica, as of 8/2005.

$Id$
"""
import dislinplot, math, Image, ImageOps


def generate_zmat(gridsize):
    "Example from Dislin.  Example contour map for simple overlay of bitmap"
    n = gridsize
    m = gridsize
    xray = range (n)
    yray = range (m)
    zmat = range (n*m)
    fpi  = 3.1415927 / 180.
    stepx = 360. / (n - 1)
    stepy = 360. / (m - 1)
    
    for i in range (0, n):
      xray[i] = xray[i] * stepx
    
    for i in range (0, m):
      yray[i] = yray[i] * stepy
    
    for i in range (0, n):
      x = xray[i] * fpi
      for j in range (0, m):
        y = yray[j] * fpi
        zmat[i*m+j] = 2 * math.sin(x) * math.sin(y)
    return zmat

def generate_layers(plot):
  for i in range (0, 9):
    zlev = -2. + i * 0.5
    if i == 4:
      plot.add_layer('NONE',zlev,(i+1) * 28)
    else:
      plot.add_layer('FLOAT',zlev,(i+1) * 28)


def plot1():
    "First example plot.  Proof of concept, don't use as a template."
    zmat = generate_zmat(50)
    contourplot = dislinplot.DislinPlot()
    generate_layers(contourplot)
    contourplot.add_grid(50, 50, zmat)
    filename = contourplot.genplot()
    print 'Test plot that uses mostly defaults: ', filename
#######


def plot2():
    "Template example for creating a tiff file from DislinPlot"
    # Set plot options for a tiff output file
    plot2 = dislinplot.DislinPlot()
    plot2.set_dislin_scale(False)              # Color will be 256
    plot2.set_bitmap_size(800)                 # Not used for postscript
    plot2.set_display('tiff')
    plot2.set_xname('X Position')
    plot2.set_yname('Y Position')
    plot2.set_input_bmpfile('030423_oo_dir_map_od_512MB.020000.or_Eye1_noselect.bmp')

    # Open up the data file for conversion and put in a list
    image = Image.open('030423_oo_dir_map_od_512MB.020000.od_noselect_bw.bmp')
    imagebw = ImageOps.grayscale(image).rotate(270) # Rotated!??
    (width, height) = image.size
    pixels = list(imagebw.getdata())

    #Add contour, data, and then plot.  Parameter returned is actual filename.
    plot2.add_layer('NONE',255. / 2,255)
    plot2.add_grid(width,height,pixels)
    filename = plot2.genplot()
    print 'Plot 2 file created and named: ', filename


def plot3():
    "Template example for creating a postscript file from DislinPlot"
    plot2 = dislinplot.DislinPlot()
    plot2.set_dislin_scale(True)
    #plot2.set_bitmap_size(800)                 # Not used for postscript
    plot2.set_display('postscript')             # Or 'tiff'
    plot2.set_xname('X Position')
    plot2.set_yname('Y Position')
    plot2.set_input_bmpfile('030423_oo_dir_map_od_512MB.020000.or_Eye1_noselect.bmp')

    # Open up the data file for conversion and put in a list
    image = Image.open('030423_oo_dir_map_od_512MB.020000.od_noselect_bw.bmp')
    imagebw = ImageOps.grayscale(image).rotate(270) # Rotated!?? Fortran?
    (width, height) = image.size
    pixels = list(imagebw.getdata())

    #Add contour, data, and then plot.  Parameter returned is actual filename.
    plot2.add_layer('NONE',255. / 2,255)
    plot2.add_grid(width,height,pixels)
    filename = plot2.genplot()
    print 'Plot 3 file created and named: ', filename


# Begin main
if __name__ == '__main__':
    plot1()
    plot2()
    plot3()
