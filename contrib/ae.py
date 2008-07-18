"""
Measure the tilt aftereffect for the currently loaded simulation.

"""
from numpy import array

from topo.commands.analysis import decode_feature
from topo.base.arrayutils import wrap
from topo.misc.utils import frange
from topo.misc.keyedlist import KeyedList


def test_all_orientations(x=0,y=0):
   results=KeyedList()
   for i in frange(0.0, 1.0, 1.0/36.0, inclusive=True):
       input = Gaussian(x=x, y=y, orientation=i*pi,
                        size=0.088388, aspect_ratio=4.66667, scale=1.0)
       pattern_present(inputs={'Retina' : input}, duration=1.0,
                       plastic=False,
                       overwrite_previous=True,
                       apply_output_fn=True)
       if hasattr(topo,'guimain'):
           topo.guimain.refresh_activity_windows()
       results[i]=decode_feature(topo.sim['V1'], preference_map="OrientationPreference")
   return results


def degrees(x):
  "Convert scalar or array argument from the range [0.0,1.0] to [0.0,180.0]"
  return 180.0*array(x)


print "Measuring initial perception of all orientations..."
before=test_all_orientations(0.0,0.0)
pylab.figure(figsize=(5,5))
vectorplot(degrees(before.keys()),  degrees(before.keys()),style="--") # add a dashed reference line
vectorplot(degrees(before.values()),degrees(before.keys()),\
          title="Initial perceived values for each orientation")

print "Adapting to pi/2 gaussian at the center of retina for 90 iterations..."
for p in ["LateralExcitatory","LateralInhibitory","LGNOnAfferent","LGNOffAfferent"]:
   # Value is just an approximate match to bednar:nc00; not calculated directly
   topo.sim["V1"].projections(p).learning_rate = 0.005

inputs = [Gaussian(x = 0.0, y = 0.0, orientation = pi/2.0,
                  size=0.088388, aspect_ratio=4.66667, scale=1.0)]
topo.sim['Retina'].input_generator.generators = inputs
topo.sim.run(90)


print "Measuring adapted perception of all orientations..."
after=test_all_orientations(0.0,0.0)
before_vals = array(before.values())
after_vals  = array(after.values())
diff_vals   = before_vals-after_vals # Sign flipped to match conventions

pylab.figure(figsize=(5,5))
pylab.axvline(90.0)
pylab.axhline(0.0)
vectorplot(wrap(-90.0,90.0,degrees(diff_vals)),degrees(before.keys()),\
          title="Difference from initial perceived value for each orientation")
