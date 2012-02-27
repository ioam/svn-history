import param

import topo.pattern
import topo.pattern.random
import __main__
import os
import contrib
import topo
from topo.transferfn.misc import PatternCombine
from topo.transferfn.misc import HalfRectify
from topo import numbergen
from topo.pattern import Gaussian
from topo.numbergen import UniformRandom, BoundedNumber, ExponentialDecay
from topo.command import pattern_present
from param import normalize_path
import numpy

from contrib.jacommands import LateralOrientationAnnisotropy

from topo.analysis.featureresponses import MeasureResponseCommand, FeatureMaps, SinusoidalMeasureResponseCommand, FeatureCurveCommand
FeatureMaps.num_orientation=16
MeasureResponseCommand.scale=1.0
MeasureResponseCommand.duration=4.0
SinusoidalMeasureResponseCommand.frequencies=[2.4]
FeatureCurveCommand.num_orientation=16
FeatureCurveCommand.curve_parameters=[{"contrast":15},{"contrast":50},{"contrast":90}]
from topo.command import load_snapshot

#load_snapshot('./DATA/LESI/TEST-small/CCSimple_000002.00.typ')
#load_snapshot('./DATA/LESI/TEST/CCSimple_000002.00.typ')

load_snapshot('./DATA/LESI/CCLESIGifLatest/CCSimple_010000.00.typ')
#load_snapshot('./DATA/LESI/CCLESIGif-NEW1/CCSimple_010000.00_with_map.typ')
#load_snapshot('./DATA/LESI/CCLESIGif12-Orig-LARGE_NEWEXPANDER5000/CCSimple_005002.00.typ')
    
from topo.command import wipe_out_activity, clear_event_queue
wipe_out_activity()
clear_event_queue()

from topo.pattern import SineGrating, Disk
class SineGratingDiskTemp(SineGrating):
      mask_shape = param.Parameter(default=Disk(smoothing=0,size=1.0))


def new_set_parameters(a,b,c,d,e,f,g):
    print a,b,c,d,e,f,g
    topo.sim["LGNOn"].projections()["LateralGC"].strength=a
    topo.sim["LGNOff"].projections()["LateralGC"].strength=a
    
    def _divide_with_constant(x, y):
        y = numpy.clip(y, 0, 10000)
        x = numpy.clip(x, 0, 10000)
        return numpy.divide(x, y + b)
    
    topo.sim["LGNOn"].projections()["LateralGC"].activity_group = (0.6,_divide_with_constant)
    
    topo.sim["V1Complex"].output_fns[1].t*=0    
    topo.sim["V1Complex"].output_fns[1].t+=c
    topo.sim["V1ComplexInh"].output_fns[1].t*=0    
    topo.sim["V1ComplexInh"].output_fns[1].t+=d
    topo.sim["V1ComplexInh"].output_fns[1].gain=e
    
    topo.sim["V1ComplexInh"].projections()["LongEI"].strength=f
    topo.sim["V1ComplexInh"].projections()["LocalEI"].strength=g
    
    
    par = "_" + str(a)+ "_" + str(b) + "_" + str(c) + "_" + str(d)+ "_" + str(e) + "_" + str(f)+ "_" + str(g)  + ".png"
    plot_size_tuning(par)

def set_parameters(a,b,c,d,e,f,g,h,i,j,k,l,m):
    print a,b,c,d,e,f,g,h,i,j,k,l,m
    
    topo.sim["V1Simple"].projections()["V1SimpleFeedbackExc1"].strength=b
    topo.sim["V1Simple"].projections()["V1SimpleFeedbackInh"].strength=c
    topo.sim["V1Complex"].projections()["LongEE"].strength=d
    topo.sim["V1ComplexInh"].projections()["LongEI"].strength=e
    topo.sim["V1Complex"].projections()["LocalIE"].strength=f
    topo.sim["V1ComplexInh"].projections()["LocalII"].strength=g
    topo.sim["V1Complex"].projections()["V1SimpleAfferent"].strength=h
    topo.sim["V1Complex"].projections()["LocalEE"].strength=i
    topo.sim["V1ComplexInh"].projections()["LocalEI"].strength=j
    topo.sim["V1Complex"].output_fns[1].t*=0    
    topo.sim["V1Complex"].output_fns[1].t+=k
    topo.sim["V1ComplexInh"].output_fns[1].t*=0    
    topo.sim["V1ComplexInh"].output_fns[1].t+=l
    topo.sim["V1ComplexInh"].output_fns[1].gain=m


def check_activity(a,b,c,d,e,f,g,h,i,j,k,l,m):

    print a,b,c,d,e,f,g,h,i,j,k,l,m
    
    #topo.sim["V1Simple"].projections()["V1SimpleFeedbackExc1"].strength=b
    #topo.sim["V1Simple"].projections()["V1SimpleFeedbackInh"].strength=c
    #topo.sim["V1Complex"].projections()["LongEE"].strength=d
    #topo.sim["V1ComplexInh"].projections()["LongEI"].strength=e
    #topo.sim["V1Complex"].projections()["LocalIE"].strength=f
    #topo.sim["V1ComplexInh"].projections()["LocalII"].strength=g
    #topo.sim["V1Complex"].projections()["V1SimpleAfferent"].strength=h
    #topo.sim["V1Complex"].projections()["LocalEE"].strength=i
    #topo.sim["V1ComplexInh"].projections()["LocalEI"].strength=j
    #topo.sim["V1Complex"].output_fns[1].t*=0    
    #topo.sim["V1Complex"].output_fns[1].t+=k
    #topo.sim["V1ComplexInh"].output_fns[1].t*=0    
    #topo.sim["V1ComplexInh"].output_fns[1].t+=l
    #topo.sim["V1ComplexInh"].output_fns[1].gain=m    
    
    par = "_" + str(a)+ "_" + str(b) + "_" + str(c) + "_" + str(d)+ "_" + str(e)  + "_" + str(f) + "_" + str(g) + "_" + str(h) + "_" + str(i) + "_" + str(j) + "_" + str(k) + "_" + str(l)+ "_" + str(m) +".png" 
    plot_neural_dynamics(par)

def make_full_analysis(a,b,c,d,e,f,g,h,i,j,k,l,m):
    import topo
    print a,b,c,d,e,f,g,h,i,j,k,l,m
    
    #topo.sim["V1Simple"].projections()["V1SimpleFeedbackExc1"].strength=b
    #topo.sim["V1Simple"].projections()["V1SimpleFeedbackInh"].strength=c
    #topo.sim["V1Complex"].projections()["LongEE"].strength=d
    #topo.sim["V1ComplexInh"].projections()["LongEI"].strength=e
    #topo.sim["V1Complex"].projections()["LocalIE"].strength=f
    #topo.sim["V1ComplexInh"].projections()["LocalII"].strength=g
    #topo.sim["V1Complex"].projections()["V1SimpleAfferent"].strength=h
    #topo.sim["V1Complex"].projections()["LocalEE"].strength=i
    #topo.sim["V1ComplexInh"].projections()["LocalEI"].strength=j
    
    #topo.sim["V1Complex"].output_fns[1].t*=0    
    #topo.sim["V1Complex"].output_fns[1].t+=k
    #topo.sim["V1ComplexInh"].output_fns[1].t*=0    
    #topo.sim["V1ComplexInh"].output_fns[1].t+=l
    #topo.sim["V1ComplexInh"].output_fns[1].gain=m    

    
    #topo.sim['V1Simple'].output_fns[0].old_a*=0
    #topo.sim['V1Complex'].output_fns[0].old_a*=0
    #topo.sim['V1ComplexInh'].output_fns[0].old_a*=0

    from topo.analysis.featureresponses import MeasureResponseCommand, FeatureMaps, SinusoidalMeasureResponseCommand,FeatureCurveCommand
    FeatureMaps.num_orientation=16
    MeasureResponseCommand.scale=1.0
    SinusoidalMeasureResponseCommand.frequencies=[2.4]
    FeatureCurveCommand.num_orientation=16
    MeasureResponseCommand.duration=4.0
    FeatureCurveCommand.curve_parameters=[{"contrast":40},{"contrast":50},{"contrast":90}]    
    
    V1Splastic =     topo.sim["V1Simple"].plastic
    V1Cplastic =     topo.sim["V1Complex"].plastic
    V1CInhplastic =     topo.sim["V1ComplexInh"].plastic    
    topo.sim["V1Simple"].plastic = False
    topo.sim["V1Complex"].plastic = False
    topo.sim["V1ComplexInh"].plastic = False
    wipe_out_activity()
    clear_event_queue()
    
    par = 'Analysis:' + str(a)+ "_" + str(b) + "_" + str(c) + "_" + str(d)+ "_" + str(e)  + "_" + str(f) + "_" + str(g) + "_" + str(h) + "_" + str(i) + "_" + str(j) + "_" + str(k) + "_" + str(l) + "_" + str(m)
    #d = os.path.dirname(par)
    if not os.path.exists(par):
             os.makedirs(par)
    normalize_path.prefix = par
    
    #plot_neural_dynamics('neural_dynamics.png')
    
    import contrib.surround_analysis

    from topo.analysis.featureresponses import SinusoidalMeasureResponseCommand,FeatureCurveCommand
    from topo.base.projection import ProjectionSheet
    from topo.sheet import GeneratorSheet
    import contrib.jacommands
    import contrib.surround_analysis
    exec "from topo.analysis.vision import analyze_complexity" in __main__.__dict__
    from topo.analysis.featureresponses import PatternPresenter            
    
    PatternPresenter.duration=4.0
    import topo.command.pylabplot
    reload(topo.command.pylabplot)                
    
    #contrib.surround_analysis.run_dynamics_analysis(0.0,0.0,0.7,__main__.__dict__.get("analysis_scale",0.3))
    #PatternPresenter.duration=4.0
    #a = topo.command.pylabplot.measure_or_tuning_fullfield.instance(sheet=topo.sim["V1Complex"])
    #a.duration=4.0
    #a()
    
    #topo.command.pylabplot.cyclic_tuning_curve.instance(x_axis="orientation",filename="ORTC[0,0]",sheet=topo.sim["V1Complex"],coords=[(0,0)])()
    #topo.command.pylabplot.cyclic_tuning_curve.instance(x_axis="orientation",filename="ORTC[0.1,0.1]",sheet=topo.sim["V1Complex"],coords=[(0.1,0.1)])()
    #topo.command.pylabplot.cyclic_tuning_curve.instance(x_axis="orientation",filename="ORTC[0.1,-0.1]",sheet=topo.sim["V1Complex"],coords=[(0.1,-0.1)])()
    #topo.command.pylabplot.cyclic_tuning_curve.instance(x_axis="orientation",filename="ORTC[-0.1,0.1]",sheet=topo.sim["V1Complex"],coords=[(-0.1,0.1)])()    
    #topo.command.pylabplot.cyclic_tuning_curve.instance(x_axis="orientation",filename="ORTC[-0.1,-0.1]",sheet=topo.sim["V1Complex"],coords=[(-0.1,-0.1)])()
    #topo.command.pylabplot.cyclic_tuning_curve.instance(x_axis="orientation",filename="ORTC[0.2,0.2]",sheet=topo.sim["V1Complex"],coords=[(0.2,0.2)])()
    #topo.command.pylabplot.cyclic_tuning_curve.instance(x_axis="orientation",filename="ORTC[0.2,-0.2]",sheet=topo.sim["V1Complex"],coords=[(0.2,-0.2)])()
    #topo.command.pylabplot.cyclic_tuning_curve.instance(x_axis="orientation",filename="ORTC[-0.2,0.2]",sheet=topo.sim["V1Complex"],coords=[(-0.2,0.2)])()    
    #topo.command.pylabplot.cyclic_tuning_curve.instance(x_axis="orientation",filename="ORTC[-0.2,-0.2]",sheet=topo.sim["V1Complex"],coords=[(-0.2,-0.2)])()
    #topo.command.pylabplot.cyclic_tuning_curve.instance(x_axis="orientation",filename="ORTC[0,0.1]",sheet=topo.sim["V1Complex"],coords=[(0.0,0.1)])()
    #topo.command.pylabplot.cyclic_tuning_curve.instance(x_axis="orientation",filename="ORTC[0,-0.1]",sheet=topo.sim["V1Complex"],coords=[(0.0,-0.1)])()
    #topo.command.pylabplot.cyclic_tuning_curve.instance(x_axis="orientation",filename="ORTC[-0.1,0]",sheet=topo.sim["V1Complex"],coords=[(-0.1,0.0)])()    
    #topo.command.pylabplot.cyclic_tuning_curve.instance(x_axis="orientation",filename="ORTC[0.1,0]",sheet=topo.sim["V1Complex"],coords=[(0.1,-0.0)])()
    #topo.command.pylabplot.cyclic_tuning_curve.instance(x_axis="orientation",filename="ORTC[0.3,0.3]",sheet=topo.sim["V1Complex"],coords=[(0.3,0.3)])()
    #topo.command.pylabplot.cyclic_tuning_curve.instance(x_axis="orientation",filename="ORTC[0.3,-0.3]",sheet=topo.sim["V1Complex"],coords=[(0.3,-0.3)])()
    #topo.command.pylabplot.cyclic_tuning_curve.instance(x_axis="orientation",filename="ORTC[-0.3,0.3]",sheet=topo.sim["V1Complex"],coords=[(-0.3,0.3)])()
    #topo.command.pylabplot.cyclic_tuning_curve.instance(x_axis="orientation",filename="ORTC[-0.3,-0.3]",sheet=topo.sim["V1Complex"],coords=[(-0.3,-0.3)])()
    #topo.command.pylabplot.cyclic_tuning_curve.instance(x_axis="orientation",filename="ORTC[0.24,0.24]",sheet=topo.sim["V1Complex"],coords=[(0.25,0.25)])()
    #topo.command.pylabplot.cyclic_tuning_curve.instance(x_axis="orientation",filename="ORTC[0.24,-0.24]",sheet=topo.sim["V1Complex"],coords=[(0.25,-0.25)])()
    #topo.command.pylabplot.cyclic_tuning_curve.instance(x_axis="orientation",filename="ORTC[-0.24,0.24]",sheet=topo.sim["V1Complex"],coords=[(-0.25,0.25)])()    
    #topo.command.pylabplot.cyclic_tuning_curve.instance(x_axis="orientation",filename="ORTC[-0.24,-0.24]",sheet=topo.sim["V1Complex"],coords=[(-0.25,-0.25)])()
    #topo.command.pylabplot.cyclic_tuning_curve.instance(x_axis="orientation",filename="ORTC[0,0.24]",sheet=topo.sim["V1Complex"],coords=[(0.0,0.25)])()
    #topo.command.pylabplot.cyclic_tuning_curve.instance(x_axis="orientation",filename="ORTC[0,-0.24]",sheet=topo.sim["V1Complex"],coords=[(0.0,-0.25)])()
    #topo.command.pylabplot.cyclic_tuning_curve.instance(x_axis="orientation",filename="ORTC[-0.24,0]",sheet=topo.sim["V1Complex"],coords=[(-0.25,0.0)])()    
    #topo.command.pylabplot.cyclic_tuning_curve.instance(x_axis="orientation",filename="ORTC[0.24,0]",sheet=topo.sim["V1Complex"],coords=[(0.25,-0.0)])()
    #topo.command.pylabplot.cyclic_tuning_curve.instance(x_axis="orientation",filename="ORTC[0,0.3]",sheet=topo.sim["V1Complex"],coords=[(0.0,0.3)])()
    #topo.command.pylabplot.cyclic_tuning_curve.instance(x_axis="orientation",filename="ORTC[0,-0.3]",sheet=topo.sim["V1Complex"],coords=[(0.0,-0.3)])()
    #topo.command.pylabplot.cyclic_tuning_curve.instance(x_axis="orientation",filename="ORTC[-0.3,0]",sheet=topo.sim["V1Complex"],coords=[(-0.3,0.0)])()    
    #topo.command.pylabplot.cyclic_tuning_curve.instance(x_axis="orientation",filename="ORTC[0.3,0]",sheet=topo.sim["V1Complex"],coords=[(0.3,-0.0)])()

    #contrib.surround_analysis.surround_analysis().analyse([(0,0),(1.0,0.0),(0.0,1.0),(-1.0,0.0),(0.0,-1.0),(1.0,1.0),(-1.0,1.0),(1.0,-1.0),(-1.0,-1.0)],12,15)
    
    normalize_path.prefix = './D-with-lowhighcontrast'
    if not os.path.exists(normalize_path.prefix):
             os.makedirs(normalize_path.prefix)
    contrib.surround_analysis.surround_analysis().analyse([(0,0)],12,15)
    

def plot_size_tuning(params):
    sheet_names=["V1Complex"]
    prefix="/home/jan/topographica/ActivityExploration/"

    from topo.command.basic import pattern_present
    from topo.base.functionfamily import PatternDrivenAnalysis
    from topo.analysis.featureresponses import PatternPresenter
    from topo.base.sheet import Sheet
    import pylab

    V1Splastic =     topo.sim["V1Simple"].plastic
    V1Cplastic =     topo.sim["V1Complex"].plastic
    V1CInhplastic =     topo.sim["V1ComplexInh"].plastic    
    topo.sim["V1Simple"].plastic = False
    topo.sim["V1Complex"].plastic = False
    topo.sim["V1ComplexInh"].plastic = False
    
    x = 0
    y = 0.06
    (X,Y) = topo.sim["V1Complex"].sheet2matrixidx(x,y)
    (Xl,Yl) = topo.sim["LGNOn"].sheet2matrixidx(x,y)
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    #orr=numpy.pi*topo.sim["V1Complex"].sheet_views["OrientationPreference"].view()[0][X][Y]
    #phase = 2*numpy.pi*topo.sim["V1Simple"].sheet_views["PhasePreference"].view()[0][X][Y]
    orr =0
    phase =0 
    
    stc_e_hc = []
    stc_i_hc = []
    stc_LongEE_hc = []
    stc_LocalEE_hc = []
    stc_LocalIE_hc = []
    stc_Aff_hc = []
    
    LGN_hc = []
    V1S_hc = []
    
    
    num_sizes = 50
    max_size = 1.3
    
    for size in xrange(0,num_sizes):
        size = float(size)/num_sizes*max_size
        ip = topo.sim['Retina'].input_generator
        topo.sim['Retina'].set_input_generator(SineGratingDiskTemp(orientation=orr,phase=phase,size=size,scale=1.0,x=x,y=y,frequency=2.4))
        topo.sim['V1Simple'].output_fns[0].old_a*=0
        topo.sim['V1Complex'].output_fns[0].old_a*=0
        topo.sim['V1ComplexInh'].output_fns[0].old_a*=0
        wipe_out_activity()
        clear_event_queue()
        topo.sim.state_push()     
        topo.sim.run(4.0)           
                
        stc_e_hc.append(topo.sim["V1Complex"].activity[X,Y].copy())
        stc_i_hc.append(topo.sim["V1ComplexInh"].activity[X,Y].copy())
        LGN_hc.append(topo.sim["LGNOn"].activity[Xl,Yl].copy())
        V1S_hc.append(topo.sim["V1Simple"].activity[X,Y].copy())
        stc_Aff_hc.append(topo.sim["V1Complex"].projections()["V1SimpleAfferent"].activity[X,Y].copy())
        stc_LongEE_hc.append(topo.sim["V1Complex"].projections()["LongEE"].activity[X,Y].copy())
        stc_LocalEE_hc.append(topo.sim["V1Complex"].projections()["LocalEE"].activity[X,Y].copy())
        stc_LocalIE_hc.append(topo.sim["V1Complex"].projections()["LocalIE"].activity[X,Y].copy())
        topo.sim.state_pop()        

    stc_e_lc = []
    stc_i_lc = []
    stc_LongEE_lc = []
    stc_LocalEE_lc = []
    stc_LocalIE_lc = []
    stc_Aff_lc = []
    LGN_lc = []
    V1S_lc = []
    
    sizes=[]
    for size in xrange(0,num_sizes):
        size = float(size)/num_sizes*max_size
        ip = topo.sim['Retina'].input_generator
        topo.sim['Retina'].set_input_generator(SineGratingDiskTemp(orientation=orr,phase=phase,size=size,scale=0.3,x=x,y=y,frequency=2.4))
        topo.sim['V1Simple'].output_fns[0].old_a*=0
        topo.sim['V1Complex'].output_fns[0].old_a*=0
        topo.sim['V1ComplexInh'].output_fns[0].old_a*=0
        wipe_out_activity()
        clear_event_queue()
        topo.sim.state_push()     
        topo.sim.run(4.0)           
                
        stc_e_lc.append(topo.sim["V1Complex"].activity[X,Y].copy())
        stc_i_lc.append(topo.sim["V1ComplexInh"].activity[X,Y].copy())
        LGN_lc.append(topo.sim["LGNOn"].activity[Xl,Yl].copy())
        V1S_lc.append(topo.sim["V1Simple"].activity[X,Y].copy())
        stc_Aff_lc.append(topo.sim["V1Complex"].projections()["V1SimpleAfferent"].activity[X,Y].copy())
        stc_LongEE_lc.append(topo.sim["V1Complex"].projections()["LongEE"].activity[X,Y].copy())
        stc_LocalEE_lc.append(topo.sim["V1Complex"].projections()["LocalEE"].activity[X,Y].copy())
        stc_LocalIE_lc.append(topo.sim["V1Complex"].projections()["LocalIE"].activity[X,Y].copy())
        topo.sim.state_pop()        
        sizes.append(size)
    
    pylab.figure(figsize=(20,15))
    pylab.subplot(6,1,1)
    pylab.plot(sizes,stc_e_lc,'ro',label='exc lc')
    pylab.plot(sizes,stc_e_lc,'r')
    pylab.plot(sizes,stc_i_lc,'bo',label='inh lc')
    pylab.plot(sizes,stc_i_lc,'b')
    pylab.plot(sizes,stc_e_hc,'r+',label='exc hc')
    pylab.plot(sizes,stc_e_hc,'r')
    pylab.plot(sizes,stc_i_hc,'b+',label='inh hc')
    pylab.plot(sizes,stc_i_hc,'b')
    pylab.legend()
    
    pylab.subplot(6,1,2)
    pylab.plot(sizes,numpy.array(stc_Aff_lc)+numpy.array(stc_LongEE_lc)+numpy.array(stc_LocalEE_lc),'ro',label='exc lc')
    pylab.plot(sizes,numpy.array(stc_Aff_lc)+numpy.array(stc_LongEE_lc)+numpy.array(stc_LocalEE_lc),'r')
    pylab.plot(sizes,stc_LocalIE_lc,'bo',label='ing lc')
    pylab.plot(sizes,stc_LocalIE_lc,'b')
    pylab.plot(sizes,numpy.array(stc_Aff_hc)+numpy.array(stc_LongEE_hc)+numpy.array(stc_LocalEE_hc),'r+',label='exc hc')
    pylab.plot(sizes,numpy.array(stc_Aff_hc)+numpy.array(stc_LongEE_hc)+numpy.array(stc_LocalEE_hc),'r')
    pylab.plot(sizes,stc_LocalIE_hc,'b+',label='inh hc')
    pylab.plot(sizes,stc_LocalIE_hc,'b')
    pylab.legend()
    
    pylab.subplot(6,1,3)
    pylab.plot(sizes,numpy.array(stc_Aff_lc)+numpy.array(stc_LongEE_lc),'ro',label='exc lc')
    pylab.plot(sizes,numpy.array(stc_Aff_lc)+numpy.array(stc_LongEE_lc),'r')
    pylab.plot(sizes,stc_LocalIE_lc,'bo',label='ing lc')
    pylab.plot(sizes,stc_LocalIE_lc,'b')
    pylab.plot(sizes,numpy.array(stc_Aff_hc)+numpy.array(stc_LongEE_hc),'r+',label='exc hc')
    pylab.plot(sizes,numpy.array(stc_Aff_hc)+numpy.array(stc_LongEE_hc),'r')
    pylab.plot(sizes,stc_LocalIE_hc,'b+',label='inh hc')
    pylab.plot(sizes,stc_LocalIE_hc,'b')
    pylab.legend()

    pylab.subplot(6,1,4)
    pylab.plot(sizes,numpy.array(stc_Aff_lc),'ko',label='aff lc')
    pylab.plot(sizes,numpy.array(stc_Aff_lc),'k')
    pylab.plot(sizes,numpy.array(stc_LongEE_lc),'kx',label='long lc')
    pylab.plot(sizes,numpy.array(stc_LongEE_lc),'k')
    pylab.plot(sizes,numpy.array(stc_LocalEE_lc)/10,'k*',label='local lc')
    pylab.plot(sizes,numpy.array(stc_LocalEE_lc)/10,'k')
    pylab.plot(sizes,numpy.array(stc_Aff_hc),'go',label='aff hc')
    pylab.plot(sizes,numpy.array(stc_Aff_hc),'g')
    pylab.plot(sizes,numpy.array(stc_LongEE_hc),'gx',label='long hc')
    pylab.plot(sizes,numpy.array(stc_LongEE_hc),'g')
    pylab.plot(sizes,numpy.array(stc_LocalEE_hc)/10,'g*',label='local hc')
    pylab.plot(sizes,numpy.array(stc_LocalEE_hc)/10,'g')
    pylab.legend()
    
    pylab.subplot(6,1,5)
    pylab.plot(sizes,numpy.array(V1S_lc),'ko',label='V1S lc')
    pylab.plot(sizes,numpy.array(V1S_lc),'k')
    pylab.plot(sizes,numpy.array(V1S_hc),'go',label='V1S hc')
    pylab.plot(sizes,numpy.array(V1S_hc),'g')
    pylab.legend()
    
    pylab.subplot(6,1,6)
    pylab.plot(sizes,numpy.array(LGN_lc),'ko',label='LGN lc')
    pylab.plot(sizes,numpy.array(LGN_lc),'k')
    pylab.plot(sizes,numpy.array(LGN_hc),'go',label='LGN hc')
    pylab.plot(sizes,numpy.array(LGN_hc),'g')
    pylab.legend()
    
    pylab.savefig(prefix+  params);    
    
    

def plot_neural_dynamics(params):

    sheet_names=["V1Complex"]

    ip = topo.sim['Retina'].input_generator
    topo.sim['Retina'].set_input_generator(SineGratingDiskTemp(orientation=0.0,phase=0.0,size=10,scale=1.0,x=0.0,y=0.0,frequency=2.4))

    from topo.pattern import OrientationContrast
    from topo.command import pattern_present
    from topo.base.functionfamily import PatternDrivenAnalysis
    from topo.pattern import OrientationContrast
    from topo.analysis.featureresponses import PatternPresenter
    from topo.base.sheet import Sheet
    import pylab

    topo.sim['V1Simple'].output_fns[0].old_a*=0
    topo.sim['V1Complex'].output_fns[0].old_a*=0
    topo.sim['V1ComplexInh'].output_fns[0].old_a*=0

    V1Splastic =     topo.sim["V1Simple"].plastic
    V1Cplastic =     topo.sim["V1Complex"].plastic
    V1CInhplastic =     topo.sim["V1ComplexInh"].plastic    
    topo.sim["V1Simple"].plastic = False
    topo.sim["V1Complex"].plastic = False
    topo.sim["V1ComplexInh"].plastic = False

    prefix="/home/jan/topographica/ActivityExploration/"
    
    topo.sim.state_push()
    
    from topo.command import pattern_present
    from topo.base.functionfamily import PatternDrivenAnalysis
    from topo.pattern import OrientationContrast
    from topo.analysis.featureresponses import PatternPresenter
    from topo.base.sheet import Sheet
    
    data={}
    
    for key in sheet_names:
        data[key] = {}
        for i in topo.sim[key].projections().keys():
            data[key][i]=[]
        data[key]["act"]=[]

    (X,Y) = topo.sim["V1Complex"].sheet2matrixidx(0.0,0.0)
    LateralOrientationAnnisotropy()
    #return
    for i in xrange(0,100):
	topo.sim.run(0.05)        
        for key in sheet_names:
            for i in topo.sim[key].projections().keys():
                data[key][i].append(topo.sim[key].projections()[i].activity.copy())
            data[key]["act"].append(topo.sim[key].activity.copy())
    
    acts = topo.sim["V1Simple"].activity.copy()      
    actc = topo.sim["V1Complex"].activity.copy()      

    topo.sim.state_pop()        

    m = numpy.argmax(data["V1Complex"]["act"][-1])
    

    #(X,Y) = numpy.unravel_index(m, data["V1Complex"]["act"][-1].shape)

    orr=numpy.pi*topo.sim["V1Complex"].sheet_views["OrientationPreference"].view()[0][X][Y]
    phase = 2*numpy.pi*topo.sim["V1Complex"].sheet_views["PhasePreference"].view()[0][X][Y]

    print X,Y

    pylab.figure(figsize=(20,15))
    pylab.subplot(5,3,1)
    pylab.title(prefix+sheet_names[0]+" [" + str(X) + "," +str(Y) + "]")

    for projname in data[sheet_names[0]].keys():
        a = []
        for act in data[sheet_names[0]][projname]:
            a.append(act[X,Y])
        pylab.plot(a,label=projname)
    #pylab.legend(loc='upper left')
    pylab.subplot(5,3,2)
    pylab.imshow(acts)
    pylab.colorbar()
    pylab.subplot(5,3,3)
    pylab.imshow(actc)
    pylab.colorbar()
    (xx,yy) = topo.sim["V1Complex"].matrixidx2sheet(X,Y)
    # now lets collect the size tuning 
    step_size=0.2
    stc_lc = []
    stc_aff_lc = []
    stc_lr_exc_lc = []
    stc_sr_exc_lc = []
    stc_sr_inh_lc = []
    
    for i in xrange(0,10):
        topo.sim['V1Simple'].output_fns[0].old_a*=0
        topo.sim['V1Complex'].output_fns[0].old_a*=0
        topo.sim['V1ComplexInh'].output_fns[0].old_a*=0
        wipe_out_activity()
        clear_event_queue()

	topo.sim['Retina'].set_input_generator(SineGratingDiskTemp(orientation=0.0,phase=0.0,size=i*step_size,scale=0.3,x=xx,y=yy,frequency=2.4))
	topo.sim.state_push()     
	topo.sim.run(2.0)           
        stc_lc.append(topo.sim["V1Complex"].activity[X,Y].copy())
        stc_aff_lc.append(topo.sim["V1Complex"].projections()["V1SimpleAfferent"].activity[X,Y].copy())
        stc_lr_exc_lc.append(topo.sim["V1Complex"].projections()["LongEE"].activity[X,Y].copy())
	stc_sr_exc_lc.append(topo.sim["V1Complex"].projections()["LocalEE"].activity[X,Y].copy())
        stc_sr_inh_lc.append(topo.sim["V1Complex"].projections()["LocalIE"].activity[X,Y].copy())
        topo.sim.state_pop()        


    stc_hc = []
    stc_aff_hc = []
    stc_lr_exc_hc = []
    stc_sr_exc_hc = []
    stc_sr_inh_hc = []

    for i in xrange(0,10):
        topo.sim['V1Simple'].output_fns[0].old_a*=0
        topo.sim['V1Complex'].output_fns[0].old_a*=0
        topo.sim['V1ComplexInh'].output_fns[0].old_a*=0
        wipe_out_activity()
	clear_event_queue()
    	topo.sim['Retina'].set_input_generator(SineGratingDiskTemp(orientation=0.0,phase=0.0,size=i*step_size,scale=1.0,x=xx,y=yy,frequency=2.4))
	topo.sim.state_push()     
	topo.sim.run(2.0)           
        stc_hc.append(topo.sim["V1Complex"].activity[X,Y].copy())
        stc_aff_hc.append(topo.sim["V1Complex"].projections()["V1SimpleAfferent"].activity[X,Y].copy())
        stc_lr_exc_hc.append(topo.sim["V1Complex"].projections()["LongEE"].activity[X,Y].copy())
	stc_sr_exc_hc.append(topo.sim["V1Complex"].projections()["LocalEE"].activity[X,Y].copy())
        stc_sr_inh_hc.append(topo.sim["V1Complex"].projections()["LocalIE"].activity[X,Y].copy())
        topo.sim.state_pop()        

    

    # lets do the surround contrast analysis
    cs = 0.6
    scale=1.0
    colinear = OrientationContrast(orientationcenter=orr,orientationsurround=orr,sizecenter=cs,sizesurround=4.0,thickness=4.0-cs,scalecenter=scale,scalesurround=scale,x=xx,y=yy,frequency=__main__.__dict__.get('FREQ',2.4),phase=phase)
    orthogonal = OrientationContrast(orientationcenter=orr,orientationsurround=orr+numpy.pi/2,sizecenter=cs,sizesurround=4.0,thickness=4.0-cs,scalecenter=scale,scalesurround=scale,x=xx,y=yy,frequency=__main__.__dict__.get('FREQ',2.4),phase=phase)


    ortc_or = []
    ortc_aff_or = []
    ortc_lr_exc_or = []
    ortc_sr_exc_or = []
    ortc_sr_inh_or = []

    inh_ortc_or = []
    inh_ortc_lr_exc_or = []
    inh_ortc_sr_exc_or = []
    inh_ortc_sr_inh_or = []

    topo.sim['V1Simple'].output_fns[0].old_a*=0
    topo.sim['V1Complex'].output_fns[0].old_a*=0
    topo.sim['V1ComplexInh'].output_fns[0].old_a*=0
    wipe_out_activity()
    clear_event_queue()
    topo.sim.state_push()     
    topo.sim['Retina'].set_input_generator(orthogonal)
    
    for i in xrange(0,80):
	topo.sim.run(0.05)           
        ortc_or.append(topo.sim["V1Complex"].activity[X,Y].copy())
        ortc_aff_or.append(topo.sim["V1Complex"].projections()["V1SimpleAfferent"].activity[X,Y].copy())
        ortc_lr_exc_or.append(topo.sim["V1Complex"].projections()["LongEE"].activity[X,Y].copy())
	ortc_sr_exc_or.append(topo.sim["V1Complex"].projections()["LocalEE"].activity[X,Y].copy())
        ortc_sr_inh_or.append(topo.sim["V1Complex"].projections()["LocalIE"].activity[X,Y].copy())

        inh_ortc_or.append(topo.sim["V1ComplexInh"].activity[X,Y].copy())
        inh_ortc_lr_exc_or.append(topo.sim["V1ComplexInh"].projections()["LongEI"].activity[X,Y].copy())
	inh_ortc_sr_exc_or.append(topo.sim["V1ComplexInh"].projections()["LocalEI"].activity[X,Y].copy())
        inh_ortc_sr_inh_or.append(topo.sim["V1ComplexInh"].projections()["LocalII"].activity[X,Y].copy())

    ortc_or_V1Complex_act = topo.sim["V1Complex"].activity.copy()
    ortc_or_V1Simple_act = topo.sim["V1Simple"].activity.copy()
    ortc_or_LGNOn_act = topo.sim["LGNOn"].activity.copy()
    inh_ortc_or_V1Complex_act = topo.sim["V1ComplexInh"].activity.copy()

        
    topo.sim.state_pop()        

    ortc_cl = []
    ortc_aff_cl = []
    ortc_lr_exc_cl = []
    ortc_sr_exc_cl = []
    ortc_sr_inh_cl = []

    inh_ortc_cl = []
    inh_ortc_lr_exc_cl = []
    inh_ortc_sr_exc_cl = []
    inh_ortc_sr_inh_cl = []

    
    topo.sim['V1Simple'].output_fns[0].old_a*=0
    topo.sim['V1Complex'].output_fns[0].old_a*=0
    topo.sim['V1ComplexInh'].output_fns[0].old_a*=0
    wipe_out_activity()
    clear_event_queue()
    topo.sim.state_push()     
    topo.sim['Retina'].set_input_generator(colinear)
    
    for i in xrange(0,80):
	topo.sim.run(0.05)           
        ortc_cl.append(topo.sim["V1Complex"].activity[X,Y].copy())
        ortc_aff_cl.append(topo.sim["V1Complex"].projections()["V1SimpleAfferent"].activity[X,Y].copy())
        ortc_lr_exc_cl.append(topo.sim["V1Complex"].projections()["LongEE"].activity[X,Y].copy())
	ortc_sr_exc_cl.append(topo.sim["V1Complex"].projections()["LocalEE"].activity[X,Y].copy())
        ortc_sr_inh_cl.append(topo.sim["V1Complex"].projections()["LocalIE"].activity[X,Y].copy())

        inh_ortc_cl.append(topo.sim["V1ComplexInh"].activity[X,Y].copy())
        inh_ortc_lr_exc_cl.append(topo.sim["V1ComplexInh"].projections()["LongEI"].activity[X,Y].copy())
	inh_ortc_sr_exc_cl.append(topo.sim["V1ComplexInh"].projections()["LocalEI"].activity[X,Y].copy())
        inh_ortc_sr_inh_cl.append(topo.sim["V1ComplexInh"].projections()["LocalII"].activity[X,Y].copy())


    ortc_cl_V1Complex_act = topo.sim["V1Complex"].activity.copy()
    ortc_cl_V1Simple_act = topo.sim["V1Simple"].activity.copy()
    ortc_cl_LGNOn_act = topo.sim["LGNOn"].activity.copy()
    inh_ortc_cl_V1Complex_act = topo.sim["V1ComplexInh"].activity.copy()
    
    topo.sim.state_pop()        



        
    pylab.subplot(5,3,4)
    pylab.plot(stc_lc,label='act')
    pylab.plot(stc_aff_lc,label='aff')
    pylab.plot(stc_lr_exc_lc,label='LongEE')
    pylab.plot(stc_sr_exc_lc,label='ShortEE')
    pylab.plot(stc_sr_inh_lc,label='ShortIE')
    pylab.plot(numpy.array(stc_sr_exc_lc)/(-1.0*numpy.array(stc_sr_inh_lc)+0.01)/10,label='E:I ratio')
    pylab.xlim=(0,20)
    pylab.legend()


    pylab.subplot(5,3,5)
    pylab.plot(stc_hc,label='act')
    pylab.plot(stc_aff_hc,label='aff')
    pylab.plot(stc_lr_exc_hc,label='LongEE')
    pylab.plot(stc_sr_exc_hc,label='ShortEE')
    pylab.plot(stc_sr_inh_hc,label='ShortIE')
    pylab.plot(numpy.array(stc_sr_exc_hc)/(-1.0*numpy.array(stc_sr_inh_hc)+0.01)/10,label='E:I ratio')
    pylab.xlim=(0,20)
    pylab.legend()

    pylab.subplot(5,3,6)
    pylab.plot(stc_hc,label='act hc')
    pylab.plot(stc_lc,label='act lc')
    pylab.xlim=(0,20)
    pylab.legend()




    pylab.subplot(5,3,7)
    pylab.title('collinear')
    pylab.plot(ortc_cl,label='act')
    pylab.plot(ortc_aff_cl,label='aff')
    pylab.plot(ortc_lr_exc_cl,label='LongEE')
    pylab.plot(ortc_sr_exc_cl,label='ShortEE')
    pylab.plot(ortc_sr_inh_cl,label='ShortIE')
    pylab.xlim=(0,60)
    pylab.legend()

    pylab.subplot(5,3,8)
    pylab.title('orthogonal')
    pylab.plot(ortc_or,label='act')
    pylab.plot(ortc_aff_or,label='aff')
    pylab.plot(ortc_lr_exc_or,label='LongEE')
    pylab.plot(ortc_sr_exc_or,label='ShortEE')
    pylab.plot(ortc_sr_inh_or,label='ShortIE')
    pylab.xlim=(0,60)
    pylab.legend()

    pylab.subplot(5,3,9)
    pylab.title('collinear inh')
    pylab.plot(inh_ortc_cl,label='act')
    pylab.plot(inh_ortc_lr_exc_cl,label='LongEE')
    pylab.plot(inh_ortc_sr_exc_cl,label='ShortEE')
    pylab.plot(inh_ortc_sr_inh_cl,label='ShortIE')
    pylab.xlim=(0,60)
    pylab.legend()

    pylab.subplot(5,3,10)
    pylab.title('orthogonal inh')
    pylab.plot(inh_ortc_or,label='act')
    pylab.plot(inh_ortc_lr_exc_or,label='LongEE')
    pylab.plot(inh_ortc_sr_exc_or,label='ShortEE')
    pylab.plot(inh_ortc_sr_inh_or,label='ShortIE')
    pylab.xlim=(0,60)
    pylab.legend()


    pylab.subplot(5,3,11)
    pylab.imshow(ortc_cl_V1Complex_act,vmin=0,vmax=1.0)
    pylab.subplot(5,3,12)
    pylab.imshow(inh_ortc_cl_V1Complex_act,vmin=0,vmax=1.0)
    #pylab.subplot(5,3,13)
    #pylab.imshow(ortc_cl_LGNOn_act,vmin=0,vmax=1.0)
    pylab.subplot(5,3,13)
    pylab.imshow(ortc_or_V1Complex_act,vmin=0,vmax=1.0)
    pylab.subplot(5,3,14)
    pylab.imshow(inh_ortc_or_V1Complex_act,vmin=0,vmax=1.0)
    pylab.subplot(5,3,15)
    pylab.imshow(ortc_or_LGNOn_act,vmin=0,vmax=1.0)
    
    

    topo.sim["V1Simple"].plastic = V1Splastic
    topo.sim["V1Complex"].plastic = V1Cplastic
    topo.sim["V1ComplexInh"].plastic = V1CInhplastic
    wipe_out_activity()
    clear_event_queue()
    
    topo.sim['Retina'].set_input_generator(ip)
    pylab.savefig(prefix+ sheet_names[0] + params);    



#topo.sim["V1Simple"].projections()["V1SimpleFeedbackExc1"].strength=0
#topo.sim["V1Simple"].projections()["V1SimpleFeedbackInh"].strength=0
contrib.jacommands.run_combinations(new_set_parameters,[[0.5],[0.18], [0.1] , [0.4,0.3,0.1], [1.0], [3.8,3.4,3.8,4.2,4.6,5.0], [2.4,1.8,1.2,0.6]])
#plot_size_tuning('')



#contrib.jacommands.run_combinations(check_activity,[[0],[0.1],[-2.5],[0.1],[4.0,5.0,6.0],[-1.0,-1.1],[-0.9,-0.8],[3.0],[1.7],[2.2],[0.1],[0.2,0.3]])
#make_full_analysis(0,0.1,-2.5,0.4,0.1,-8.0,-1.2,1.0,0.6,0.2,0.05,0.0,3.0)


#make_full_analysis(0,0.0,0,0,0,0,0,0,0,0,0,0,0)
#check_activity(0,0.0,0,0,0,0,0,0,0,0,0,0,0)


#contrib.jacommands.run_combinations(check_activity,[[0],[0.1],[-2.5,-2.0,-3.0],[1.6],[0.4],[-8.0,-5.0,-6.0],[-1.2,-1.3,-1.4],[2.0],[0.4],[0.1],[0.05],[0.0,0.02],[4.0]])

#contrib.jacommands.run_combinations(check_activity,[[0],[0.0],[0.0],[0.4,0.8],[0.1,0.2],[-8.0,-5.0,-6.0],[-1.2],[1.0,0.5],[0.6],[0.2],[0.05,0.1],[0.0,0.05],[1.0,2.0,3.0]])
#set_parameters(0,0.1,-2.5,0.4,0.1,-8.0,-1.2,0.5,0.6,0.2,0.05,0.05,3.0)
