# Topographica Package Include List

# For using .ty file types.
import tyimputil

# core
import simulator
import params
import utils

# sheets and sheet geometry
import sheet
import boundingregion
import convolve2d

# kernels
import kernelfactory

# sheet types
import rfsom
import image
import inputsheet

# plotting
import bitmap
import sheetview
import plot
import plotengine
import histogram
import palette

# GUI files
import propertiesframe
import taggedslider
import gui

# set import all the important stuff directly into the package
# namespace.
from simulator import *
from sheet import *



