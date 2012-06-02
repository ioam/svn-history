import numpy as np
import os, colorsys

import matplotlib
import matplotlib.pyplot as plt

from PIL import Image

###################
# Stability plots #
###################

rgb_to_hsv = np.vectorize(colorsys.rgb_to_hsv)
hsv_to_rgb = np.vectorize(colorsys.hsv_to_rgb)

def HSVBars(selectivities, stabilities, aspect=0.7, filename='HSVBars.pdf'): 
   ''' 21 bars: time=0, then 20 bars sampled every 1000 iterations. Inputs should be numpy arrays.'''
   bar_count = len(selectivities)
   assert bar_count == len(stabilities), "Selectivity and stability lists must be same length!"
   stability_hues =  np.abs(stabilities-1.0) / 6.0
   RGBs = zip(*hsv_to_rgb(stability_hues, selectivities, np.ones(bar_count)))
   fig = plt.figure(frameon=False)
   ax = fig.add_subplot(111, aspect=aspect)
   for (ind, (r,g,b)) in enumerate(RGBs):
      ax.add_patch(matplotlib.patches.Rectangle((ind,0), width=0.8, height=10, facecolor=(r,g,b,1.0)))
   ax.xaxis.set_visible(False); ax.yaxis.set_visible(False)
   plt.xlim([0,bar_count]); plt.ylim([0,10])
   plt.savefig(filename,bbox_inches='tight', pad_inches=0)

def HSVKey(filename='HSVKey.pdf', dim=11):
   (h,s) = np.mgrid[0:dim,0:dim]
   h = h / (6.0*dim); s =  s / float(dim)
   v = np.ones((dim,dim)) 
   r,g,b = hsv_to_rgb(h,s,v)
   c = np.dstack([r,g,b])
   c = np.flipud(c) ; c = np.rot90(c)
   fig = plt.figure(frameon=False)
   ax = fig.add_subplot(111)
   ax.xaxis.set_visible(False); ax.yaxis.set_visible(False)
   plt.imshow(c, interpolation='nearest')
   plt.savefig(filename,bbox_inches='tight', pad_inches=0)


def blackZeroSelectivity(image, whitelevel=0.2):
   """ Makes zero selectivity black for publication.
       Follows the original Imagemagik convert commands used to 
       swap the saturation and value ie. uses saturation as the value. 
       The saturation is scaled by the whitelevel. """
   whitefactor = 1.0 / whitelevel  # 25% multiplies by 4.0
   imageRGBA = image.convert('RGBA')                             
   arr = np.asarray(imageRGBA).astype('float')
   r, g, b, a = np.rollaxis(arr, axis=-1)
   h, s, v = rgb_to_hsv(r, g, b)   # s is [0,1] all v are 255.0  
   s *= (255.0 * whitefactor)      
   r, g, b = hsv_to_rgb(h, (v / 255.0), np.clip(s, 0, 255.0))
   arr = np.dstack((r, g, b, a))
   return Image.fromarray(arr.astype('uint8'), 'RGBA')


def crop(image, box):
   (left, top, width, height) = box
   crop_area = (left, top, left+width, top+height)
   return image.crop(crop_area)


FFTCropBox = (143,174,154,154)   # For cropping FFT plots...
#  For slicing rows/columns out of the On_cf*.png plots
CF_VBox = (112,28,31,227); CF_HBox = (28,112,227,31) 

if __name__ == '__main__':

   # Crop tests for FFT and CFs...
   fft_uncropped = Image.open(os.path.join('.', 'FFT_uncropped.png'))
   crop(fft_uncropped, FFTCropBox).save('FFT_cropped.png')

   CFs_uncropped = Image.open(os.path.join('.', 'CFs_uncropped.png'))
   crop(CFs_uncropped, CF_HBox).save('CF_HBox.png')
   crop(CFs_uncropped, CF_VBox).save('CF_VBox.png')

   # Test the black HSV conversion
   or_sel = Image.open(os.path.join('.', 'OR_Sel.png'))
   or_sel_black = blackZeroSelectivity(or_sel)
   or_sel_black.save('OR_Sel_Black.png')

   # Test the figure generation code
   HSVBars(np.random.rand(21), np.random.rand(21))
   HSVKey()


