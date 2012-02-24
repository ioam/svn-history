"""
The complex cell LISSOM model with push-pull connectivity.
"""
import __main__
import numpy
from math import pi, sqrt
import param

import topo.pattern.basic
import topo.pattern.random
import topo.pattern.image
from topo.sheet.lissom import LISSOM
from topo.sheet.basic import JointNormalizingCFSheet_Continuous, GeneratorSheet
from topo.projection.basic import CFProjection, SharedWeightCFProjection,OneToOneProjection
from topo.responsefn.optimized import CFPRF_DotProduct_opt
from topo.base.cf import CFSheet
from topo.base.boundingregion import BoundingBox
from topo.learningfn.optimized import CFPLF_Hebbian_opt
from topo.transferfn.optimized import CFPOF_DivisiveNormalizeL1_opt
from topo.transferfn.misc import PatternCombine, HalfRectify
from topo.transferfn.basic import DivisiveNormalizeL1, HomeostaticMaxEnt, Sigmoid ,Hysteresis
from topo import numbergen
from topo.pattern.basic import Gaussian
from topo.base.functionfamily import CoordinateMapperFn
from contrib.JanA.CCLISSOM_push_pull_extra import SimpleHomeoLinear, Expander, Jitterer, randomize_V1Simple_relative_LGN_strength, CFPLF_KeyserRule
from topo.numbergen import UniformRandom, BoundedNumber, ExponentialDecay

topo.sim.name = "cclissom_push_pull"

import contrib.JanA.modelparametrization

#### Set up retinal inputs

image_filenames=["images/konig/seq1/seq1-%05d.tif"%(i*10+1) for i in xrange(100)]
inputs=[topo.pattern.image.FileImage(filename=f,
	            size=10.0,  #size_normalization='original',(size=10.0)
	            x=0,y=0,scale=0.55,orientation=0)
        for f in image_filenames]

input = Jitterer(generator=topo.pattern.basic.Selector(generators=inputs),orientation=numbergen.UniformRandom(lbound=-pi,ubound=pi,seed=56),reset_period=15,jitter_magnitude=0.4)
ring = topo.pattern.basic.Composite(operator=numpy.add,x=numbergen.UniformRandom(lbound=-1.0,ubound=1.0,seed=12),
                                    y=numbergen.UniformRandom(lbound=-1.0,ubound=1.0,seed=36),
		                    generators=[topo.pattern.basic.Ring(size=0.5, aspect_ratio=1.0, scale=0.064,thickness=0.02,
                                                offset=0.0,
                                                bounds=BoundingBox(radius=2.125), smoothing=0.02),
                                		topo.pattern.random.UniformRandom(offset=0, scale=0.01)]
                                   )

retinal_waves=Expander(generator=ring,orientation=numbergen.UniformRandom(lbound=-pi,ubound=pi,seed=56),reset_period=15,speed=0.3)
zeroInput = topo.pattern.basic.Null();


# Set up the helper function for jittering of the afferent connectivity
class Jitter(CoordinateMapperFn):
    """Return the jittered x,y coordinate of the given coordinate."""
    scale =  0.5
    rand = param.Parameter(default=None)
    def __call__(self,x,y):
        return x+(self.rand()-0.5)*self.scale,y+(self.rand()-0.5)*self.scale

jitterOn = Jitter(rand =numbergen.UniformRandom(seed=1023))
jitterOff = Jitter(rand =numbergen.UniformRandom(seed=1023))
jitterOnInh = Jitter(rand =numbergen.UniformRandom(seed=1023))
jitterOffInh = Jitter(rand =numbergen.UniformRandom(seed=1023))


# Specify weight initialization, response function, and learning function
CFProjection.weights_generator=topo.pattern.random.UniformRandom()
CFProjection.cf_shape=topo.pattern.basic.Disk(smoothing=0.0)
CFProjection.response_fn=CFPRF_DotProduct_opt()
CFProjection.learning_fn=CFPLF_Hebbian_opt()
CFProjection.weights_output_fns=[CFPOF_DivisiveNormalizeL1_opt()]

# Set up transfer function and homeostatic mechanisms
V1Simple_OF = SimpleHomeoLinear(t_init=0.35,alpha=3,mu=__main__.__dict__.get('MU',0.003),eta=0.002)
V1Complex_OF=HalfRectify()
NN = PatternCombine(generator=topo.pattern.random.GaussianRandom(scale=0.02,offset=0.0),operator=numpy.add)

# Build simulation
topo.sim['Retina']=GeneratorSheet(nominal_density=48.0,
                                input_generator=input,  
                                period=1.0, phase=0.05,
                                nominal_bounds=BoundingBox(radius=0.5+0.25+0.375+0.25))

topo.sim['FakeRetina']=GeneratorSheet(nominal_density=48.0,
                                  input_generator=retinal_waves,  
                                  period=1.0, phase=0.05,
                                  nominal_bounds=BoundingBox(radius=0.5+0.25+0.25))


topo.sim['LGNOn']=LISSOM(nominal_density=48,
                          nominal_bounds=BoundingBox(radius=0.5+0.25+0.25),
                          output_fns=[HalfRectify(t_init=0.0)],tsettle=0,
                          measure_maps=False)

topo.sim['LGNOff']=LISSOM(nominal_density=48,
                           nominal_bounds=BoundingBox(radius=0.5+0.25+0.25),
                           output_fns=[HalfRectify(t_init=0.0)],tsettle=0,
                           measure_maps=False)

topo.sim['V1Simple'] = JointNormalizingCFSheet_Continuous(nominal_density=__main__.__dict__.get('default_density',96),
                        nominal_bounds=BoundingBox(radius=0.5),
                        output_fns=[Hysteresis(time_constant=0.3),NN,V1Simple_OF])

topo.sim['V1SimpleInh'] = JointNormalizingCFSheet_Continuous(nominal_density=__main__.__dict__.get('default_density',96),
                        nominal_bounds=BoundingBox(radius=0.5),
                        output_fns=[Hysteresis(time_constant=0.3),NN,V1Simple_OF])

topo.sim['V1Complex'] = JointNormalizingCFSheet_Continuous(nominal_density=__main__.__dict__.get('default_density',96),
                        nominal_bounds=BoundingBox(radius=0.5),
                        output_fns=[Hysteresis(time_constant=0.3),V1Complex_OF])

# DoG weights for the LGN
centerg   = Gaussian(size=0.07,aspect_ratio=1.0,output_fns=[DivisiveNormalizeL1()])
surroundg = Gaussian(size=0.2,aspect_ratio=1.0,output_fns=[DivisiveNormalizeL1()])

on_weights = topo.pattern.basic.Composite(
    generators=[centerg,surroundg],operator=numpy.subtract)

off_weights = topo.pattern.basic.Composite(
    generators=[surroundg,centerg],operator=numpy.subtract)

topo.sim.connect('FakeRetina','LGNOn',delay=0.05,
                 connection_type=OneToOneProjection,strength=7.0,
                 nominal_bounds=BoundingBox(radius=0.375),name='Afferent')
    
topo.sim.connect('FakeRetina','LGNOff',delay = 0.05,
                 connection_type=OneToOneProjection,strength=7.0,
                 nominal_bounds=BoundingBox(radius=0.375),name='Afferent')


g1 = Gaussian(aspect_ratio=1.0,scale=1.0,size=numbergen.UniformRandom(lbound=0.8,ubound=0.8,seed=56))
g1._Dynamic_time_fn = None
g2 = Gaussian(aspect_ratio=1.0,scale=1.0,size=numbergen.UniformRandom(lbound=0.8,ubound=0.8,seed=56))
g2._Dynamic_time_fn = None

LGNStr = 4
inbalance = 0.1
LGNOnStr = LGNStr+LGNStr*inbalance
LGNOffStr = LGNStr-LGNStr*inbalance

#Layer 4C
topo.sim.connect('LGNOn','V1Simple',delay=0.025,dest_port=('Activity','JointNormalize', 'Afferent'),
                 connection_type=CFProjection,strength=LGNOnStr,name='LGNOnExcAfferent',
                 weights_generator=topo.pattern.basic.Composite(operator=numpy.multiply, 
                     generators=[g1
                 ,topo.pattern.random.UniformRandom()]),
                 nominal_bounds_template=BoundingBox(radius=0.2),
                 coord_mapper=jitterOn,apply_output_fns_init=False,
                 learning_rate=(BoundedNumber(bounds=(0.0,None),generator=
                               ExponentialDecay(starting_value = 0.5,
                                                time_constant=16000))))


topo.sim.connect('LGNOff','V1Simple',delay=0.025,dest_port=('Activity','JointNormalize', 'Afferent'),
                 connection_type=CFProjection,strength=LGNOffStr,name='LGNOffExcAfferent',
                 weights_generator=topo.pattern.basic.Composite(operator=numpy.multiply, 
                     generators=[g2
                 ,topo.pattern.random.UniformRandom()]),
                 nominal_bounds_template=BoundingBox(radius=0.2),
                 coord_mapper=jitterOff,apply_output_fns_init=False,
                 learning_rate=(BoundedNumber(bounds=(0.0,None),generator=
                               ExponentialDecay(starting_value = 0.5,
                                                time_constant=16000))))

topo.sim.connect('LGNOn','V1SimpleInh',delay=0.025,dest_port=('Activity','JointNormalize', 'Afferent'),
                 connection_type=CFProjection,strength=LGNOnStr,name='LGNOnInhAfferent',
                 weights_generator=topo.pattern.basic.Composite(operator=numpy.multiply, 
                     generators=[g1
                 ,topo.pattern.random.UniformRandom()]),
                 nominal_bounds_template=BoundingBox(radius=0.2),
                 coord_mapper=jitterOffInh,apply_output_fns_init=False,
                 learning_rate=(BoundedNumber(bounds=(0.0,None),generator=
                               ExponentialDecay(starting_value = 0.5,
                                                time_constant=16000))))


topo.sim.connect('LGNOff','V1SimpleInh',delay=0.025,dest_port=('Activity','JointNormalize', 'Afferent'),
                 connection_type=CFProjection,strength=LGNOffStr,name='LGNOffInhAfferent',
                 weights_generator=topo.pattern.basic.Composite(operator=numpy.multiply, 
                     generators=[g2
                 ,topo.pattern.random.UniformRandom()]),
                 nominal_bounds_template=BoundingBox(radius=0.2),
                 coord_mapper=jitterOnInh,apply_output_fns_init=False,
                 learning_rate=(BoundedNumber(bounds=(0.0,None),generator=
                               ExponentialDecay(starting_value = 0.5,
                                                time_constant=16000))))


topo.sim.connect('V1Simple','V1Simple',delay=0.025,
                 connection_type=CFProjection,strength=0.5,name='V1SimpleExcToExc',
                 weights_generator=Gaussian(aspect_ratio=1.0, size=0.3),
                 nominal_bounds_template=BoundingBox(radius=0.3),learning_rate=0.1)


topo.sim.connect('V1Simple','V1SimpleInh',delay=0.025,
                 connection_type=CFProjection,strength=1.0,name='V1SimpleExcToInh',
                 weights_generator=Gaussian(aspect_ratio=1.0, size=0.3),
                 nominal_bounds_template=BoundingBox(radius=0.3),learning_rate=0.1)


topo.sim.connect('V1SimpleInh','V1Simple',delay=0.025,
                 connection_type=CFProjection,strength=-0.5,name='V1SimpleInhToExc',
                 weights_generator=Gaussian(aspect_ratio=1.0, size=0.3),
                 nominal_bounds_template=BoundingBox(radius=0.3),
                 learning_fn = CFPLF_KeyserRule("V1Simple",['V1SimpleInhToExc']),learning_rate=0.1)


topo.sim.connect('V1SimpleInh','V1SimpleInh',delay=0.025,
                 connection_type=CFProjection,strength=-0.5,name='V1SimpleInhToInh',
                 weights_generator=Gaussian(aspect_ratio=1.0, size=0.3),
                 nominal_bounds_template=BoundingBox(radius=0.3),
                 learning_fn = CFPLF_KeyserRule("V1SimpleInh",['V1SimpleInhToInh']),learning_rate=0.1)


#Layer 2/3
topo.sim.connect('V1Simple','V1Complex',delay=0.025,
                 connection_type=CFProjection,strength=2.5,name='V1SimpleAfferent',
                 weights_generator=Gaussian(aspect_ratio=1.0, size=0.05),
                 nominal_bounds_template=BoundingBox(radius=0.075),learning_rate=0.0)
                

topo.sim.connect('V1Complex','V1Simple',delay=0.025,
                 connection_type=CFProjection,strength=0.14,name='V1SimpleFeedback',
                 weights_generator=Gaussian(aspect_ratio=1.0, size=18),
                 nominal_bounds_template=BoundingBox(radius=0.0025),
                 learning_rate=0)


topo.sim.connect('V1Complex','V1SimpleInh',delay=0.025,
                 connection_type=CFProjection,strength=0.14,name='V1SimpleInhFeedback',
                 weights_generator=Gaussian(aspect_ratio=1.0, size=18),
                 nominal_bounds_template=BoundingBox(radius=0.0025),
                 learning_rate=0)

topo.sim.connect('V1Complex','V1Complex',delay=0.025,name='LateralExcitatory',
                 connection_type=CFProjection,strength=1.5,
                 weights_generator=topo.pattern.basic.Gaussian(aspect_ratio=1.0, size=0.4),
                 nominal_bounds_template=BoundingBox(radius=0.12),
                 learning_rate=0.0)

topo.sim.connect('V1Complex','V1Complex',delay=0.025,name='LateralInhibitory',
                 connection_type=CFProjection,strength=-1.5,
                 weights_generator=topo.pattern.basic.Composite(operator=numpy.multiply, 
                     generators=[Gaussian(aspect_ratio=1.0, size=2*0.22917),
                                topo.pattern.random.UniformRandom()]),
                 nominal_bounds_template=BoundingBox(radius=0.4),
                 learning_rate=(BoundedNumber(bounds=(0.0,None),generator=
                               ExponentialDecay(starting_value=0.2,time_constant=8000))))

topo.sim.schedule_command(5000,"secondStage()")

def secondStage():
    topo.sim.connect('Retina','LGNOn',delay=0.05,
                    connection_type=SharedWeightCFProjection,strength=7.0,
                    nominal_bounds_template=BoundingBox(radius=0.375),name='LGNOnAfferent3',
                    weights_generator=on_weights)
    
    topo.sim.connect('Retina','LGNOff',delay = 0.05,
                    connection_type=SharedWeightCFProjection,strength=7.0,
                    nominal_bounds_template=BoundingBox(radius=0.375),name='LGNOffAfferent4',
                    weights_generator=off_weights)
    
    topo.sim['FakeRetina'].set_input_generator(zeroInput)
    topo.sim['LGNOn'].in_connections[0].strength=0
    topo.sim['LGNOff'].in_connections[0].strength=0
    randomize_V1Simple_relative_LGN_strength(prob=0.5)


# change the default parameters of the measuring commands to obtain better quality and match the paper
from topo.analysis.featureresponses import MeasureResponseCommand, FeatureMaps, SinusoidalMeasureResponseCommand,FeatureCurveCommand
FeatureMaps.num_orientation=16
MeasureResponseCommand.scale=3.0
MeasureResponseCommand.duration=4.0
FeatureCurveCommand.num_orientation=20
FeatureCurveCommand.curve_parameters=[{"contrast":10},{"contrast":90}]


# model exploration
parameters = [ "topo.sim[\"V1Simple\"].projections()[\"V1SimpleExcToExc\"].strength",
               "topo.sim[\"V1Simple\"].projections()[\"V1SimpleInhToExc\"].strength",
               "topo.sim[\"V1Simple\"].projections()[\"V1SimpleFeedback\"].strength",
               "topo.sim[\"V1SimpleInh\"].projections()[\"V1SimpleExcToInh\"].strength",
               "topo.sim[\"V1SimpleInh\"].projections()[\"V1SimpleInhToInh\"].strength",
               "topo.sim[\"V1SimpleInh\"].projections()[\"V1SimpleInhFeedback\"].strength",
             ]   
             
parameter_values = [ [0.8,0.9,1.2],
                     [-0.9,-1.1,-0.8],
                     [0.1,0.12,0.14],
                     [0.7,0.65,0.75],
                     [-0.4,-0.5,-0.6],
                     [0.17,0.2,0.27]
                   ]

#contrib.JanA.modelparametrization.explore_initial_activity(parameters,parameter_values,["V1Simple","V1SimpleInh","V1Complex","V1Complex"],None,"FakeRetina",0,4.0,'Activities')
contrib.JanA.modelparametrization.ModelParametrization.set_parameters(parameters,[0.9,-0.9,0.1,0.7,-0.5,0.2])

