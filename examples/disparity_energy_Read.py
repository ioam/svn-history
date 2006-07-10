"""
Partial implementation of and Read et al. (Vis. Neurosci 2002, 19:735-753) 
models for disparity neurons based on spatiotemporal energy.

Not yet tested.

"""

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
from topo.outputfns.basic import PiecewiseLinear,HalfRectifyAndSquare,HalfRectify,Square
from topo.base.functionfamilies import OutputFn
from topo.base.arrayutils import clip_in_place
from topo.misc.numbergenerators import UniformRandom

topo.sim.name = "read_visneuro02"

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


# Monocular simple cells
topo.sim['LTunedExcMono'] = CFSheet(nominal_density=10.0,measure_maps=False,
                            output_fn=HalfRectify(),
                            nominal_bounds=BoundingBox(radius=0.5+0.25))

topo.sim['RTunedExcMono'] = CFSheet(nominal_density=10.0,measure_maps=False,
                            output_fn=HalfRectify(),
                            nominal_bounds=BoundingBox(radius=0.5+0.25))

topo.sim['LTunedInhMono'] = CFSheet(nominal_density=10.0,measure_maps=False,
                              output_fn=HalfRectify(),
                              nominal_bounds=BoundingBox(radius=0.5+0.25))

topo.sim['RTunedInhMono'] = CFSheet(nominal_density=10.0,measure_maps=False,
                              output_fn=HalfRectify(),
                              nominal_bounds=BoundingBox(radius=0.5+0.25))

topo.sim['LFarMono'] = CFSheet(nominal_density=10.0,measure_maps=False,
                                  output_fn=HalfRectify(),
                                  nominal_bounds=BoundingBox(radius=0.5+0.25))

topo.sim['RFarMono'] = CFSheet(nominal_density=10.0,measure_maps=False,
                                  output_fn=HalfRectify(),
                                  nominal_bounds=BoundingBox(radius=0.5+0.25))

topo.sim['LNearMono'] = CFSheet(nominal_density=10.0,measure_maps=False,
                                output_fn=HalfRectify(),
                                nominal_bounds=BoundingBox(radius=0.5+0.25))

topo.sim['RNearMono'] = CFSheet(nominal_density=10.0,measure_maps=False,
                                output_fn=HalfRectify(),
                                nominal_bounds=BoundingBox(radius=0.5+0.25))


                        
# Binocular simple cells
topo.sim['TunedExc'] = CFSheet(nominal_density=10.0,measure_maps=False,
                            output_fn=Square(),
                            nominal_bounds=BoundingBox(radius=0.5+0.25))

topo.sim['TunedInh'] = CFSheet(nominal_density=10.0,measure_maps=False,
                              output_fn=Square(),
                              nominal_bounds=BoundingBox(radius=0.5+0.25))

topo.sim['Far'] = CFSheet(nominal_density=10.0,measure_maps=False,
                                  output_fn=Square(),
                                  nominal_bounds=BoundingBox(radius=0.5+0.25))

topo.sim['Near'] = CFSheet(nominal_density=10.0,measure_maps=False,
                                output_fn=Square(),
                                nominal_bounds=BoundingBox(radius=0.5+0.25))


# V1
topo.sim['V1'] = CFSheet(nominal_density=10.0,
                         nominal_bounds=BoundingBox(radius=0.5+0.25))


SharedWeightCFProjection.strength=1.0
SharedWeightCFProjection.nominal_bounds_template=BoundingBox(radius=0.4)

topo.patterns.basic.Gabor.orientation=pi/2
topo.patterns.basic.Gabor.size=0.70
topo.patterns.basic.Gabor.frequency=2.4
topo.patterns.basic.Gabor.aspect_ratio=1


# Connections from retina to monocular simple cells

topo.sim.connect('LeftRetina','LTunedExcMono',delay = FixedPoint("0.05"),name='LTunedExcMono',
                 connection_type=SharedWeightCFProjection,
                 weights_generator=topo.patterns.basic.Gabor(phase=0))


topo.sim.connect('RightRetina','RTunedExcMono',delay = FixedPoint("0.05"),name='RTunedExcMono',
                 connection_type=SharedWeightCFProjection,
                 weights_generator=topo.patterns.basic.Gabor(phase=0))


topo.sim.connect('LeftRetina','LTunedInhMono',delay = FixedPoint("0.05"),name='LTunedInhMono',
                 connection_type=SharedWeightCFProjection,
                 weights_generator=topo.patterns.basic.Gabor(phase=pi))

topo.sim.connect('RightRetina','RTunedInhMono',delay = FixedPoint("0.05"),name='RTunedInhMono',
                 connection_type=SharedWeightCFProjection,
                 weights_generator=topo.patterns.basic.Gabor(phase=pi))


topo.sim.connect('LeftRetina','LFarMono',delay = FixedPoint("0.05"),name='LFarMono',
                 connection_type=SharedWeightCFProjection,
                 weights_generator=topo.patterns.basic.Gabor(phase=pi/2))

topo.sim.connect('RightRetina','RFarMono',delay = FixedPoint("0.05"),name='RFarMono',
                 connection_type=SharedWeightCFProjection,
                 weights_generator=topo.patterns.basic.Gabor(phase=pi/2))

topo.sim.connect('LeftRetina','LNearMono',delay = FixedPoint("0.05"),name='LNearMono',
                 connection_type=SharedWeightCFProjection,
                 weights_generator=topo.patterns.basic.Gabor(phase=3*pi/2))

topo.sim.connect('RightRetina','RNearMono',delay = FixedPoint("0.05"),name='RNearMono',
                 connection_type=SharedWeightCFProjection,
                 weights_generator=topo.patterns.basic.Gabor(phase=3*pi/2))



# The BoundingBox here should enclose only a single unit


# Connections from monocular to binocular simple cells

topo.sim.connect('LTunedExcMono','TunedExc',delay = FixedPoint("0.05"),name='LTEMonoToTunedExc',
                 connection_type=SharedWeightCFProjection,
                 min_matrix_radius=0,nominal_bounds_template=BoundingBox(radius=0.01),
                 weights_generator=topo.patterns.basic.Gabor(phase=pi/2))

topo.sim.connect('RTunedExcMono','TunedExc',delay = FixedPoint("0.05"),name='RTEMonoToTunedExc',
                 connection_type=SharedWeightCFProjection,
                 min_matrix_radius=0,nominal_bounds_template=BoundingBox(radius=0.01),
                 weights_generator=topo.patterns.basic.Gabor(phase=pi/2))

topo.sim.connect('LTunedInhMono','TunedInh',delay = FixedPoint("0.05"),name='LTIMonoToTunedInh',
                 connection_type=SharedWeightCFProjection,
                 min_matrix_radius=0,nominal_bounds_template=BoundingBox(radius=0.01),
                 weights_generator=topo.patterns.basic.Gabor(phase=pi/2))

topo.sim.connect('RTunedInhMono','TunedInh',delay = FixedPoint("0.05"),name='RTIMonoToTunedInh',
                 connection_type=SharedWeightCFProjection,
                 min_matrix_radius=0,nominal_bounds_template=BoundingBox(radius=0.01),
                 weights_generator=topo.patterns.basic.Gabor(phase=pi/2))


topo.sim.connect('LFarMono','Far',delay = FixedPoint("0.05"),name='LFarMonoToFar',
                 connection_type=SharedWeightCFProjection,
                 min_matrix_radius=0,nominal_bounds_template=BoundingBox(radius=0.01),
                 weights_generator=topo.patterns.basic.Gabor(phase=3*pi/2))

topo.sim.connect('RFarMono','Far',delay = FixedPoint("0.05"),name='RFarMonoToFar',
                 connection_type=SharedWeightCFProjection,
                 min_matrix_radius=0,nominal_bounds_template=BoundingBox(radius=0.01),
                 weights_generator=topo.patterns.basic.Gabor(phase=3*pi/2))

topo.sim.connect('LNearMono','Near',delay = FixedPoint("0.05"),name='LNearMonoToNear',
                 connection_type=SharedWeightCFProjection,
                 min_matrix_radius=0,nominal_bounds_template=BoundingBox(radius=0.01),
                 weights_generator=topo.patterns.basic.Gabor(phase=3*pi/2))

topo.sim.connect('RNearMono','Near',delay = FixedPoint("0.05"),name='RNearMonoToNear',
                 connection_type=SharedWeightCFProjection,
                 min_matrix_radius=0,nominal_bounds_template=BoundingBox(radius=0.01),
                 weights_generator=topo.patterns.basic.Gabor(phase=3*pi/2))



# Connections from binocular simple cells to V1

topo.sim.connect('TunedExc','V1',delay = FixedPoint("0.05"),name='TunedExcToV1',
                 connection_type=SharedWeightCFProjection,
                 min_matrix_radius=0,nominal_bounds_template=BoundingBox(radius=0.01),
                 weights_generator=topo.patterns.basic.Gabor(phase=pi/2))

topo.sim.connect('TunedInh','V1',delay = FixedPoint("0.05"),name='TunedInhToV1',
                 connection_type=SharedWeightCFProjection,
                 min_matrix_radius=0,nominal_bounds_template=BoundingBox(radius=0.01),
                 weights_generator=topo.patterns.basic.Gabor(phase=pi/2))

topo.sim.connect('Far','V1',delay = FixedPoint("0.05"),name='FarToV1',
                 connection_type=SharedWeightCFProjection,
                 min_matrix_radius=0,nominal_bounds_template=BoundingBox(radius=0.01),
                 weights_generator=topo.patterns.basic.Gabor(phase=3*pi/2))

topo.sim.connect('Near','V1',delay = FixedPoint("0.05"),name='NearToV1',
                 connection_type=SharedWeightCFProjection,
                 min_matrix_radius=0,nominal_bounds_template=BoundingBox(radius=0.01),
                 weights_generator=topo.patterns.basic.Gabor(phase=3*pi/2))

# default locations for model editor
topo.sim['V1'].gui_x=800.0
topo.sim['V1'].gui_y=40.0
topo.sim['LeftRetina'].gui_x=380.0
topo.sim['LeftRetina'].gui_y=820.0
topo.sim['RightRetina'].gui_x=1000.0
topo.sim['RightRetina'].gui_y=820.0
topo.sim['TunedExc'].gui_x=334.0
topo.sim['TunedExc'].gui_y=244.0
topo.sim['TunedInh'].gui_x=586.0
topo.sim['TunedInh'].gui_y=244.0
topo.sim['Far'].gui_x=824.0
topo.sim['Far'].gui_y=244.0
topo.sim['Near'].gui_x=1074.0
topo.sim['Near'].gui_y=244.0

topo.sim['LTunedExcMono'].gui_x=229.0
topo.sim['LTunedExcMono'].gui_y=587.0
topo.sim['RTunedExcMono'].gui_x=330.0
topo.sim['RTunedExcMono'].gui_y=476.0
topo.sim['LTunedInhMono'].gui_x=519.0
topo.sim['LTunedInhMono'].gui_y=585.0
topo.sim['RTunedInhMono'].gui_x=614.0
topo.sim['RTunedInhMono'].gui_y=469.0
topo.sim['LFarMono'].gui_x=803.0
topo.sim['LFarMono'].gui_y=577.0
topo.sim['RFarMono'].gui_x=885.0
topo.sim['RFarMono'].gui_y=466.0
topo.sim['LNearMono'].gui_x=1117.0
topo.sim['LNearMono'].gui_y=553.0
topo.sim['RNearMono'].gui_x=1215.0
topo.sim['RNearMono'].gui_y=432.0
