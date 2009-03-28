"""
Grating and contour stimuli according to Hegde and Van Essen works,
usually composite using basic patterns.

Grating stimuli subclasses:
- sinusoidal
- hyberbolic
- polar (concentric-like)
- polar (radial-like)

Contour stimuli subclasses:
- bar
- tri-star
- cross
- star/circle
- acute angle
- right angle
- obtuse angle
- semi-circle
- 3/4 arc

Stimuli from one subclass have common shape characteristics but vary in orientation,
size and/or spatial frequency.

$Id$
"""
__version__ = "$Revision$"

from math import sin, cos, pi

import numpy

from topo.pattern.basic import *

# Number of variants for each subclass

variants = 4

## GRATINGS ##

# Sinusoidal
sin1 = [SineGrating(phase=3*pi/2,frequency=2.0,orientation=i*pi/variants)
        for i in range(variants)]
sin2 = [SineGrating(phase=3*pi/2,frequency=3.2,orientation=i*pi/variants)
        for i in range(variants)]
sin3 = [SineGrating(phase=3*pi/2,frequency=5.2,orientation=i*pi/variants)
        for i in range(variants)]

# Hyperbolic
hyp1 = [HyperbolicGrating(orientation=i*pi/(2*variants)) for i in range(variants)]
hyp2 = [Composite(generators=[HyperbolicGrating(axis=0.25*(p+1)-0.12,thickness=0.03,
                  smoothing=0.04,orientation=i*pi/(2*variants)) for p in range(2)])
        for i in range(variants)]
hyp3 = [Composite(generators=[HyperbolicGrating(axis=0.16*(p+1)-0.08,thickness=0.02,
                  smoothing=0.03,orientation=i*pi/(2*variants)) for p in range(3)])
        for i in range(variants)]

# Polar
pol1 = [ConcentricRings(spacing=0.6/(1+j),thickness=0.025-j*0.005,smoothing=0.04/(1+j*0.15))
        for j in range(variants)]
pol2 = [Composite(generators=[SpiralGrating(density=0.35/(1+j*2),thickness=0.03-j*0.005,
                  smoothing=0.13/(j+1),orientation=i*2*pi/2) for i in range(2)])
        for j in range(variants)]
pol3 = [Composite(generators=[SpiralGrating(density=0.55/(1+j*1.5),thickness=0.02-j*0.003,
                  smoothing=0.13/(j+1),orientation=i*2*pi/4) for i in range(4)])
        for j in range(variants)]
pol4 = [Composite(generators=[SpiralGrating(density=0.75/(1+j*1.0),thickness=0.02-j*0.002,
                  smoothing=0.13/(j+1),orientation=i*2*pi/6) for i in range(6)])
        for j in range(variants)]
pol5 = [Composite(generators=[SpiralGrating(density=0.95/(1+j*1.0),thickness=0.015-j*0.002,
                  smoothing=0.13/(j+1),orientation=i*2*pi/8) for i in range(8)])
        for j in range(variants)]
pol6 = [Composite(generators=[RadialGrating(wide=0.25/(j*0.5+1),smoothing=0.25/(j*0.5+1),
                  orientation=i*2*pi/((j+1)*2)) for i in range((j+1)*2)])
        for j in range(variants)]


## CONTOUR STIMULI ##

# Bar
bar1 = [Rectangle(orientation=j*pi/4,smoothing=0.01,aspect_ratio=0.075,size=0.6)
        for j in range(variants)]
bar2 = [Rectangle(orientation=j*pi/4,smoothing=0.01,aspect_ratio=0.1,size=0.3)
        for j in range(variants)]

# Tri-star
par = 3 # number of parts of pattern
# This function is just abbreviation for next lines to avoid redundant code. Returns orientation
# of pattern parts in composite. Parameter i identify part of pattern, j stays for variant.
# This function is redefined later in code as necessary.
def angs(i,j):
  """Calculation of angles."""
  return j*pi/2+i*2*pi/par
size = 0.4 # size of basic pattern part
star1 = [Composite(generators=[Rectangle(orientation=angs(i,j),smoothing=0.01,aspect_ratio=0.1,
                   size=size,x=-size/2*sin(angs(i,j)),y=size/2*cos(angs(i,j)))
                   for i in range(par)])
         for j in range(variants)]
size = 0.2
star2 = [Composite(generators=[Rectangle(orientation=angs(i,j),smoothing=0.01,aspect_ratio=0.15,
                   size=size,x=-size/2*sin(angs(i,j)),y=size/2*cos(angs(i,j)))
                   for i in range(par)])
         for j in range(variants)]

# Cross
par = 2
def angs(i,j):
  """Calculation of angles."""
  return j*pi/8+i*pi/par
star3 = [Composite(generators=[Rectangle(orientation=angs(i,j),smoothing=0.01,
                   aspect_ratio=0.05,size=0.8) for i in range(par)])
         for j in range(variants)]
star4 = [Composite(generators=[Rectangle(orientation=angs(i,j),smoothing=0.01,
                   aspect_ratio=0.075,size=0.4) for i in range(par)])
         for j in range(variants)]

# Star/Circle
par = 5
def angs(i,j):
  """Calculation of angles."""
  return j*pi+i*2*pi/par
size = 0.4
star5 = [Composite(generators=[Rectangle(orientation=angs(i,j),smoothing=0.01,aspect_ratio=0.1,
                   size=size,x=-size/2*sin(angs(i,j)),y=size/2*cos(angs(i,j))) for i in range(par)])
         for j in range(2)]
par = 3
star5.append(Composite(generators=[Rectangle(orientation=i*2*pi/par,smoothing=0.01,
                       aspect_ratio=0.075,size=size*2) for i in range(par)]))
star5.append(Ring(smoothing=0.005,thickness=0.05,size=0.75))

par = 5
def angs(i,j):
  """Calculation of angles."""
  return j*pi+i*2*pi/par
size = 0.2
star6 = [Composite(generators=[Rectangle(orientation=angs(i,j),smoothing=0.01,aspect_ratio=0.1,
                   size=size,x=-size/2*sin(angs(i,j)),y=size/2*cos(angs(i,j))) for i in range(par)])
         for j in range(2)]
par = 3
star6.append(Composite(generators=[Rectangle(orientation=i*2*pi/par,smoothing=0.01,
                       aspect_ratio=0.075,size=size*2) for i in range(par)]))
star6.append(Ring(smoothing=0.01,thickness=0.035,size=0.35))

# Acute angle
angs = [(i*2*pi/16) for i in [-1,1]]
size = 0.6
ang1 = [Sweeper(generator=Composite(generators=[Rectangle(orientation=angs[i],smoothing=0.02,
                aspect_ratio=0.05,size=size,x=-size/2*sin(angs[i]),y=size/2*cos(angs[i]))
                for i in range(2)]),step=-1.2,orientation=j*2*pi/variants)
        for j in range(variants)]
size = 0.25
ang2 = [Sweeper(generator=Composite(generators=[Rectangle(orientation=angs[i],smoothing=0.02,
                aspect_ratio=0.05,size=size,x=-size/2*sin(angs[i]),y=size/2*cos(angs[i]))
                for i in range(2)]),step=-0.6,orientation=j*2*pi/variants)
        for j in range(variants)]

# Right angle
angs = [(i*2*pi/8) for i in [-1,1]]
size = 0.55
ang3 = [Sweeper(generator=Composite(generators=[Rectangle(orientation=angs[i],smoothing=0.02,
                aspect_ratio=0.05,size=size,x=-size/2*sin(angs[i]),y=size/2*cos(angs[i]))
                for i in range(2)]),step=-1.0,orientation=j*2*pi/variants)
        for j in range(variants)]
size = 0.25
ang4 = [Sweeper(generator=Composite(generators=[Rectangle(orientation=angs[i],smoothing=0.02,
                aspect_ratio=0.05,size=size,x=-size/2*sin(angs[i]),y=size/2*cos(angs[i]))
                for i in range(2)]),step=-0.3,orientation=j*2*pi/variants)
        for j in range(variants)]

# Obtuse angle
angs = [(i*2*pi/6) for i in [-1,1]]
size = 0.45
ang5 = [Sweeper(generator=Composite(generators=[Rectangle(orientation=angs[i],smoothing=0.02,
                aspect_ratio=0.05,size=size,x=-size/2*sin(angs[i]),y=size/2*cos(angs[i]))
                for i in range(2)]),step=-0.6,orientation=j*2*pi/variants)
        for j in range(variants)]
size = 0.20
ang6 = [Sweeper(generator=Composite(generators=[Rectangle(orientation=angs[i],smoothing=0.02,
                aspect_ratio=0.05,size=size,x=-size/2*sin(angs[i]),y=size/2*cos(angs[i]))
                for i in range(2)]),step=-0.3,orientation=j*2*pi/variants)
        for j in range(variants)]

# Quarter arc
arc1 = [Sweeper(generator=Composite(generators=[Ring(smoothing=0.02,thickness=0.025,size=0.6),
                RadialGrating(wide=pi/2,smoothing=0.06)],operator=numpy.minimum),step=-0.8,
                orientation=pi+i*2*pi/variants)
        for i in range(variants)]
arc2 = [Sweeper(generator=Composite(generators=[Ring(smoothing=0.015,thickness=0.025,size=0.3),
                RadialGrating(wide=pi/2,smoothing=0.04)],operator=numpy.minimum),step=-0.4,
                orientation=pi+i*2*pi/variants)
        for i in range(variants)]

# Semi-circle
arc3 = [Sweeper(generator=Composite(generators=[Ring(smoothing=0.02,thickness=0.025,size=0.6),
                RadialGrating(wide=pi,smoothing=0.06)],operator=numpy.minimum),step=-0.5,
                orientation=pi+i*2*pi/variants)
        for i in range(variants)]
arc4 = [Sweeper(generator=Composite(generators=[Ring(smoothing=0.015,thickness=0.025,size=0.3),
                RadialGrating(wide=pi,smoothing=0.04)],operator=numpy.minimum),step=-0.25,
                orientation=pi+i*2*pi/variants)
        for i in range(variants)]

# 3/4 arc
arc5 = [Sweeper(generator=Composite(generators=[Ring(smoothing=0.02,thickness=0.025,size=0.6),
                RadialGrating(wide=3*pi/2,smoothing=0.06)],operator=numpy.minimum),step=-0.05,
                orientation=pi+i*2*pi/variants)
        for i in range(variants)]
arc6 = [Sweeper(generator=Composite(generators=[Ring(smoothing=0.015,thickness=0.025,size=0.3),
                RadialGrating(wide=3*pi/2,smoothing=0.04)],operator=numpy.minimum),step=-0.07,
                orientation=pi+i*2*pi/variants)
        for i in range(variants)]


## Stimuli subclasses
sinusoidal = sin1 + sin2 + sin3
hyperbolic = hyp1 + hyp2 + hyp3
polar = pol1 + pol2 + pol3 + pol4 + pol5 + pol6
concentric_like = pol1 + pol2[1:] + pol3[2:] + pol4[2:] + pol5[3:]
radial_like = pol2[:1] + pol3[:2] + pol4[:2] + pol5[:3] + pol6
bar = bar1 + bar2
tristar = star1 + star2
cross = star3 + star4
star = star5 + star6
acute = ang1 + ang2
right = ang3 + ang4
obtuse = ang5 + ang6
quarter = arc1 + arc2
semi = arc3 + arc4
threeqtrs = arc5 + arc6

## Stimuli classes
simple_grating = sinusoidal
simple_contour = bar
complex_grating = hyperbolic + polar
complex_contour = tristar + cross + star + acute + right + obtuse + quarter + semi + threeqtrs
all_stimuli = sinusoidal + hyperbolic + polar + bar + tristar + cross + star +\
              acute + right + obtuse + quarter + semi + threeqtrs

