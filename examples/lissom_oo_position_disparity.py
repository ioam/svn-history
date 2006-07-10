"""
Example of a LISSOM-based Position Disparity map with ON/OFF channels.

"""

import RandomArray
import fixedpoint


from math import pi, sqrt
from fixedpoint import FixedPoint

import topo.patterns.basic
import topo.patterns.random
import copy

from topo.sheets.lissom import LISSOM
from topo.sheets.generatorsheet import GeneratorSheet
from topo.projections.basic import CFProjection, SharedWeightCFProjection
from topo.responsefns.optimized import CFPRF_DotProduct_opt, CFPRF_SharedWeightDotProduct_opt
from topo.base.parameterclasses import DynamicNumber,Number
from topo.base.cf import CFSheet
from topo.base.boundingregion import BoundingBox
from topo.learningfns.optimized import CFPLF_Hebbian_opt
from topo.outputfns.optimized import CFPOF_DivisiveNormalizeL1_opt
from topo.outputfns.basic import PiecewiseLinear, DivisiveNormalizeL1
from topo.misc.numbergenerators import UniformRandom

topo.sim.name = "lissom_oo_position_disparity"


### Present input patterns that are at non-corresponding locations on each retina
left_x=UniformRandom(lbound=-0.5,ubound=0.5,seed=12)
left_x_copy=copy.deepcopy(left_x)
disparity=UniformRandom(lbound=-0.1,ubound=0.1,seed=12)
disparity_copy=copy.deepcopy(disparity)
right_x=lambda:left_x_copy() + disparity_copy()


left_input_pattern = topo.patterns.basic.Gaussian(
          size=2*0.0468, aspect_ratio=4.0,
          scale=DynamicNumber(UniformRandom(lbound=0,ubound=2,seed=200)), 
          x=DynamicNumber(left_x),
          y=DynamicNumber(UniformRandom(lbound=-0.5,ubound=0.5,seed=34)),
          orientation=DynamicNumber(UniformRandom(lbound=-pi,ubound=pi,seed=56)))


right_input_pattern = topo.patterns.basic.Gaussian(
          size=2*0.0468, aspect_ratio=4.0,
          scale=DynamicNumber(UniformRandom(lbound=0,ubound=2,seed=200)), 
          x=DynamicNumber(right_x),
          y=DynamicNumber(UniformRandom(lbound=-0.5,ubound=0.5,seed=34)),
          orientation=DynamicNumber(UniformRandom(lbound=-pi,ubound=pi,seed=56)))


                          
# Specify weight initialization, response function, and learning function
RandomArray.seed(500,500)
CFProjection.weights_generator=topo.patterns.random.UniformRandom()
CFProjection.weights_shape=topo.patterns.basic.Disk(smoothing=0.0)
CFProjection.response_fn=CFPRF_DotProduct_opt()
CFProjection.learning_fn=CFPLF_Hebbian_opt()
CFProjection.weights_output_fn=CFPOF_DivisiveNormalizeL1_opt()
SharedWeightCFProjection.response_fn=CFPRF_SharedWeightDotProduct_opt()

SharedWeightCFProjection.weights_output_fn.single_cf_fn=DivisiveNormalizeL1()

###########################################
# build simulation


topo.sim['LeftRetina']=GeneratorSheet(nominal_density=24.0,
                                  input_generator=left_input_pattern,
                                  period=1.0, phase=0.05,
                                  nominal_bounds=BoundingBox(radius=0.5+0.25+0.375))

topo.sim['RightRetina']=GeneratorSheet(nominal_density=24.0,
                                  input_generator=right_input_pattern,
                                  period=1.0, phase=0.05,
                                  nominal_bounds=BoundingBox(radius=0.5+0.25+0.375))

topo.sim['LGNOnLeft']=CFSheet(nominal_density=24.0,
                          nominal_bounds=BoundingBox(radius=0.5+0.25),
                          output_fn=PiecewiseLinear(lower_bound=0.0,upper_bound=1.0),
                          measure_maps=False)

topo.sim['LGNOffLeft']=CFSheet(nominal_density=24.0,
                           nominal_bounds=BoundingBox(radius=0.5+0.25),
                           output_fn=PiecewiseLinear(lower_bound=0.0,upper_bound=1.0),
                           measure_maps=False)

topo.sim['LGNOnRight']=CFSheet(nominal_density=24.0,
                          nominal_bounds=BoundingBox(radius=0.5+0.25),
                          output_fn=PiecewiseLinear(lower_bound=0.0,upper_bound=1.0),
                          measure_maps=False)

topo.sim['LGNOffRight']=CFSheet(nominal_density=24.0,
                           nominal_bounds=BoundingBox(radius=0.5+0.25),
                           output_fn=PiecewiseLinear(lower_bound=0.0,upper_bound=1.0),
                           measure_maps=False)

topo.sim['V1'] = LISSOM(nominal_density=locals().get('default_density',48.0),
                        nominal_bounds=BoundingBox(radius=0.5))

topo.sim['V1'].output_fn.lower_bound=0.083
topo.sim['V1'].output_fn.upper_bound=0.633



# LGN ON channel
topo.sim.connect('LeftRetina','LGNOnLeft',delay=FixedPoint("0.05"),
                  connection_type=SharedWeightCFProjection,strength=2.33,
                  nominal_bounds_template=BoundingBox(radius=0.375),name='LCenterOn',
                  weights_generator=topo.patterns.basic.Gaussian(size=0.0417,
                                                                 aspect_ratio=1))

topo.sim.connect('LeftRetina','LGNOnLeft',delay = FixedPoint("0.05"),
                  connection_type=SharedWeightCFProjection,strength=-2.33,
                  name='LSurroundOn',nominal_bounds_template=BoundingBox(radius=0.375),
                  weights_generator=topo.patterns.basic.Gaussian(size=0.1667,
                                                                 aspect_ratio=1))

topo.sim.connect('RightRetina','LGNOnRight',delay=FixedPoint("0.05"),
                  connection_type=SharedWeightCFProjection,strength=2.33,
                  nominal_bounds_template=BoundingBox(radius=0.375),name='RCenterOn',
                  weights_generator=topo.patterns.basic.Gaussian(size=0.0417,
                                                                 aspect_ratio=1))

topo.sim.connect('RightRetina','LGNOnRight',delay = FixedPoint("0.05"),
                  connection_type=SharedWeightCFProjection,strength=-2.33,
                  name='RSurroundOn',nominal_bounds_template=BoundingBox(radius=0.375),
                  weights_generator=topo.patterns.basic.Gaussian(size=0.1667,
                                                                 aspect_ratio=1))


# LGN OFF channel
topo.sim.connect('LeftRetina','LGNOffLeft',delay = FixedPoint("0.05"),
                  connection_type=SharedWeightCFProjection,strength=-2.33,
                  name='LCenterOff',nominal_bounds_template=BoundingBox(radius=0.375),
                  weights_generator=topo.patterns.basic.Gaussian(size=0.0417,
                                                                 aspect_ratio=1))

topo.sim.connect('LeftRetina','LGNOffLeft',delay = FixedPoint("0.05"),
                  connection_type=SharedWeightCFProjection,strength=2.33,
                  name='LSurroundOff',nominal_bounds_template=BoundingBox(radius=0.375),
                  weights_generator=topo.patterns.basic.Gaussian(size=0.1667,
                                                                 aspect_ratio=1))

topo.sim.connect('RightRetina','LGNOffRight',delay = FixedPoint("0.05"),
                  connection_type=SharedWeightCFProjection,strength=-2.33,
                  name='RCenterOff',nominal_bounds_template=BoundingBox(radius=0.375),
                  weights_generator=topo.patterns.basic.Gaussian(size=0.0417,
                                                                 aspect_ratio=1))

topo.sim.connect('RightRetina','LGNOffRight',delay = FixedPoint("0.05"),
                  connection_type=SharedWeightCFProjection,strength=2.33,
                  name='RSurroundOff',nominal_bounds_template=BoundingBox(radius=0.375),
                  weights_generator=topo.patterns.basic.Gaussian(size=0.1667,
                                                                 aspect_ratio=1))

# Connections from LGNs to V1

topo.sim.connect('LGNOnLeft','V1',delay=FixedPoint("0.05"),
                  connection_type=CFProjection,strength=0.75,name='LGNOnLeftAfferent',
                  nominal_bounds_template=BoundingBox(radius=0.25),learning_rate=0.9590)

topo.sim.connect('LGNOffLeft','V1',delay=FixedPoint("0.05"),
                  connection_type=CFProjection,strength=0.5,name='LGNOffLeftAfferent',
                  nominal_bounds_template=BoundingBox(radius=0.25),learning_rate=0.9590)

topo.sim.connect('LGNOnRight','V1',delay=FixedPoint("0.05"),
                  connection_type=CFProjection,strength=0.75,name='LGNOnRightAfferent',
                  nominal_bounds_template=BoundingBox(radius=0.25),learning_rate=0.9590)

topo.sim.connect('LGNOffRight','V1',delay=FixedPoint("0.05"),
                  connection_type=CFProjection,strength=0.5,name='LGNOffRightAfferent',
                  nominal_bounds_template=BoundingBox(radius=0.25),learning_rate=0.9590)


# Lateral Connections

topo.sim.connect('V1','V1',delay=FixedPoint("0.05"),name='LateralExcitatory',
                  connection_type=CFProjection,strength=0.9,
                  nominal_bounds_template=BoundingBox(radius=0.10),learning_rate=3.2018) 
            
topo.sim.connect('V1','V1',delay=FixedPoint("0.05"),name='LateralInhibitory',
                  connection_type=CFProjection,strength=-0.9,
                  nominal_bounds_template=BoundingBox(radius=0.23),learning_rate=1.9626)  



### Actions scheduled to occur as the simulation proceeds.
### Copied from lissom_oo_or


topo.sim.startup_commands.append("from topo.base.boundingregion import BoundingBox")

### Lateral excitatory bounds changes
topo.sim.schedule_command(200,'topo.sim["V1"].projections()["LateralExcitatory"].change_bounds(BoundingBox(radius=0.06))')
topo.sim.schedule_command(500,'topo.sim["V1"].projections()["LateralExcitatory"].change_bounds(BoundingBox(radius=0.042))')

### Lateral excitatory learning rate changes
topo.sim.schedule_command(200,'topo.sim["V1"].projections()["LateralExcitatory"].learning_rate=1.2213')
topo.sim.schedule_command(500,'topo.sim["V1"].projections()["LateralExcitatory"].learning_rate=0.3466')

### Afferent learning rate changes
topo.sim.schedule_command(  500,'topo.sim["V1"].projections()["LGNOnLeftAfferent"].learning_rate=0.6850;topo.sim["V1"].projections()["LGNOffLeftAfferent"].learning_rate=0.6850')
topo.sim.schedule_command( 2000,'topo.sim["V1"].projections()["LGNOnLeftAfferent"].learning_rate=0.5480;topo.sim["V1"].projections()["LGNOffLeftAfferent"].learning_rate=0.5480')
topo.sim.schedule_command( 4000,'topo.sim["V1"].projections()["LGNOnLeftAfferent"].learning_rate=0.4110;topo.sim["V1"].projections()["LGNOffLeftAfferent"].learning_rate=0.4110')
topo.sim.schedule_command(20000,'topo.sim["V1"].projections()["LGNOnLeftAfferent"].learning_rate=0.2055;topo.sim["V1"].projections()["LGNOffLeftAfferent"].learning_rate=0.2055')

topo.sim.schedule_command(  500,'topo.sim["V1"].projections()["LGNOnRightAfferent"].learning_rate=0.6850;topo.sim["V1"].projections()["LGNOffRightAfferent"].learning_rate=0.6850')
topo.sim.schedule_command( 2000,'topo.sim["V1"].projections()["LGNOnRightAfferent"].learning_rate=0.5480;topo.sim["V1"].projections()["LGNOffRightAfferent"].learning_rate=0.5480')
topo.sim.schedule_command( 4000,'topo.sim["V1"].projections()["LGNOnRightAfferent"].learning_rate=0.4110;topo.sim["V1"].projections()["LGNOffRightAfferent"].learning_rate=0.4110')
topo.sim.schedule_command(20000,'topo.sim["V1"].projections()["LGNOnRightAfferent"].learning_rate=0.2055;topo.sim["V1"].projections()["LGNOffRightAfferent"].learning_rate=0.2055')


### LISSOM output function bounds changes
topo.sim.schedule_command(  200,'topo.sim["V1"].output_fn.lower_bound=0.093;topo.sim["V1"].output_fn.upper_bound=0.643')
topo.sim.schedule_command(  500,'topo.sim["V1"].output_fn.lower_bound=0.103;topo.sim["V1"].output_fn.upper_bound=0.643')
topo.sim.schedule_command( 1000,'topo.sim["V1"].output_fn.lower_bound=0.133;topo.sim["V1"].output_fn.upper_bound=0.663')
topo.sim.schedule_command( 2000,'topo.sim["V1"].output_fn.lower_bound=0.163;topo.sim["V1"].output_fn.upper_bound=0.683')
topo.sim.schedule_command( 3000,'topo.sim["V1"].output_fn.lower_bound=0.183;topo.sim["V1"].output_fn.upper_bound=0.713')
topo.sim.schedule_command( 4000,'topo.sim["V1"].output_fn.lower_bound=0.183;topo.sim["V1"].output_fn.upper_bound=0.743')
topo.sim.schedule_command( 5000,'topo.sim["V1"].output_fn.lower_bound=0.193;topo.sim["V1"].output_fn.upper_bound=0.773')
topo.sim.schedule_command( 6500,'topo.sim["V1"].output_fn.lower_bound=0.203;topo.sim["V1"].output_fn.upper_bound=0.803')
topo.sim.schedule_command( 8000,'topo.sim["V1"].output_fn.lower_bound=0.213;topo.sim["V1"].output_fn.upper_bound=0.833')
topo.sim.schedule_command(20000,'topo.sim["V1"].output_fn.lower_bound=0.223;topo.sim["V1"].output_fn.upper_bound=0.863')

# default locations for model editor

topo.sim['V1'].gui_x=600.0;      topo.sim['V1'].gui_y=225.0
topo.sim['LGNOnLeft'].gui_x=200.0;   topo.sim['LGNOnLeft'].gui_y=445.0
topo.sim['LGNOffLeft'].gui_x=482.0;  topo.sim['LGNOffLeft'].gui_y=445.0
topo.sim['LeftRetina'].gui_x=279.0;  topo.sim['LeftRetina'].gui_y=700.0

topo.sim['LGNOnRight'].gui_x=750.0;   topo.sim['LGNOnRight'].gui_y=445.0
topo.sim['LGNOffRight'].gui_x=1030.0;  topo.sim['LGNOffRight'].gui_y=445.0
topo.sim['RightRetina'].gui_x=879.0;  topo.sim['RightRetina'].gui_y=700.0



