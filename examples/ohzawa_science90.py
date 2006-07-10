"""
Partial implementation of the Ohzawa et al. (Science 1990, 249:1037-1041) models
for disparity neurons based on spatiotemporal energy.

Not yet tested.

$Id$
"""
__version__='$Revision$'

import RandomArray
import fixedpoint
import copy

from math import pi, sqrt
from fixedpoint import FixedPoint

import topo.patterns.basic
import topo.patterns.random

from topo.sheets.generatorsheet import GeneratorSheet
from topo.projections.basic import CFProjection, SharedWeightCFProjection
from topo.base.parameterclasses import DynamicNumber,Number
from topo.base.cf import CFSheet
from topo.base.boundingregion import BoundingBox
from topo.outputfns.basic import PiecewiseLinear,HalfRectifyAndSquare
from topo.base.functionfamilies import OutputFn
from topo.base.arrayutils import clip_in_place
from topo.misc.numbergenerators import UniformRandom

topo.sim.name = "ohzawa_science90"

input_pattern = topo.patterns.basic.Gaussian(
    scale=1.0,size = 2*0.0468,aspect_ratio=4.0,
    x=DynamicNumber(UniformRandom(lbound=-0.5,ubound=0.5,seed=12)),
    y=DynamicNumber(UniformRandom(lbound=-0.5,ubound=0.5,seed=34)),
    orientation=DynamicNumber(UniformRandom(lbound=-pi,ubound=pi,seed=56)))
    
# Specify weight initialization, response function, and learning function
RandomArray.seed(500,500)
# Comment this line out if these models use square Gabor CFs


CFProjection.weights_shape = topo.patterns.basic.Disk(smoothing=0.0)
CFProjection.weights_generator = topo.patterns.random.UniformRandom()

# Input regions
topo.sim['LeftRetina']  = GeneratorSheet(nominal_density=24.0,
                                         nominal_bounds=BoundingBox(radius=0.5+0.25+0.375),
                                         input_generator=input_pattern,phase=0.05)
                        
topo.sim['RightRetina'] = GeneratorSheet(nominal_density=24.0,
                                         nominal_bounds=BoundingBox(radius=0.5+0.25+0.375),
                                         input_generator=input_pattern,phase=0.05)

                        
# Binocular simple cells
topo.sim['TunedExc'] = CFSheet(nominal_density=10.0,measure_maps=False,
                            output_fn=HalfRectifyAndSquare(),
                            nominal_bounds=BoundingBox(radius=0.5+0.25))

topo.sim['TunedInh'] = CFSheet(nominal_density=10.0,measure_maps=False,
                              output_fn=HalfRectifyAndSquare(),
                              nominal_bounds=BoundingBox(radius=0.5+0.25))

topo.sim['Far'] = CFSheet(nominal_density=10.0,measure_maps=False,
                                  output_fn=HalfRectifyAndSquare(),
                                  nominal_bounds=BoundingBox(radius=0.5+0.25))

topo.sim['Near'] = CFSheet(nominal_density=10.0,measure_maps=False,
                                output_fn=HalfRectifyAndSquare(),
                                nominal_bounds=BoundingBox(radius=0.5+0.25))


# Complex cells
topo.sim['V1'] = CFSheet(nominal_density=10.0,
                         nominal_bounds=BoundingBox(radius=0.5+0.25))


##Parameters defining the connection field of each unit in TunedExc,TunedInh,Far and Near

SharedWeightCFProjection.strength=1.0
SharedWeightCFProjection.nominal_bounds_template=BoundingBox(radius=0.2) 

topo.patterns.basic.Gabor.orientation=pi/2
topo.patterns.basic.Gabor.size=0.70
topo.patterns.basic.Gabor.frequency=2.4
topo.patterns.basic.Gabor.aspect_ratio=1


topo.sim.connect('LeftRetina','TunedExc',delay = FixedPoint("0.05"),name='LTunedExc',
                 connection_type=SharedWeightCFProjection,
                 weights_generator=topo.patterns.basic.Gabor(phase=0))

topo.sim.connect('RightRetina','TunedExc',delay = FixedPoint("0.05"),name='RTunedExc',
                 connection_type=SharedWeightCFProjection,
                 weights_generator=topo.patterns.basic.Gabor(phase=0))


topo.sim.connect('LeftRetina','TunedInh',delay = FixedPoint("0.05"),name='LTunedInh',
                 connection_type=SharedWeightCFProjection,
                 weights_generator=topo.patterns.basic.Gabor(phase=pi))

topo.sim.connect('RightRetina','TunedInh',delay = FixedPoint("0.05"),name='RTunedInh',
                 connection_type=SharedWeightCFProjection,
                 weights_generator=topo.patterns.basic.Gabor(phase=pi))



topo.sim.connect('LeftRetina','Far',delay = FixedPoint("0.05"),name='LFar',
                 connection_type=SharedWeightCFProjection,
                 weights_generator=topo.patterns.basic.Gabor(phase=pi/2))

topo.sim.connect('RightRetina','Far',delay = FixedPoint("0.05"),name='RFar',
                 connection_type=SharedWeightCFProjection,
                 weights_generator=topo.patterns.basic.Gabor(phase=pi/2))


topo.sim.connect('LeftRetina','Near',delay = FixedPoint("0.05"),name='LNear',
                 connection_type=SharedWeightCFProjection,
                 weights_generator=topo.patterns.basic.Gabor(phase=3*pi/2))

topo.sim.connect('RightRetina','Near',delay = FixedPoint("0.05"),name='RNear',
                 connection_type=SharedWeightCFProjection,
                 weights_generator=topo.patterns.basic.Gabor(phase=3*pi/2))



# The BoundingBox here should enclose only a single unit....previously had radius 0.01...too small
topo.sim.connect('TunedExc','V1',delay = FixedPoint("0.05"),name='TunedExcToV1',
                 connection_type=CFProjection,
                 min_matrix_radius=0,nominal_bounds_template=BoundingBox(radius=0.01),
                 weights_generator=topo.patterns.basic.Gabor(phase=pi/2))

topo.sim.connect('TunedInh','V1',delay = FixedPoint("0.05"),name='TunedInhToV1',
                 connection_type=CFProjection,
                 min_matrix_radius=0,nominal_bounds_template=BoundingBox(radius=0.01),
                 weights_generator=topo.patterns.basic.Gabor(phase=pi/2))


topo.sim.connect('Far','V1',delay = FixedPoint("0.05"),name='FarToV1',
                 connection_type=CFProjection,
                 min_matrix_radius=0,nominal_bounds_template=BoundingBox(radius=0.01),
                 weights_generator=topo.patterns.basic.Gabor(phase=3*pi/2))

topo.sim.connect('Near','V1',delay = FixedPoint("0.05"),name='NearToV1',
                 connection_type=CFProjection,
                 min_matrix_radius=0,nominal_bounds_template=BoundingBox(radius=0.01),
                 weights_generator=topo.patterns.basic.Gabor(phase=3*pi/2))


# default locations for model editor
topo.sim['V1'].gui_x=437.0
topo.sim['V1'].gui_y=54.0
topo.sim['LeftRetina'].gui_x=284.0
topo.sim['LeftRetina'].gui_y=576.0
topo.sim['RightRetina'].gui_x=745.0
topo.sim['RightRetina'].gui_y=532.0
topo.sim['TunedExc'].gui_x=142.0
topo.sim['TunedExc'].gui_y=230.0
topo.sim['TunedInh'].gui_x=396.0
topo.sim['TunedInh'].gui_y=230.0
topo.sim['Far'].gui_x=658.0
topo.sim['Far'].gui_y=230.0
topo.sim['Near'].gui_x=902.0
topo.sim['Near'].gui_y=230.0
