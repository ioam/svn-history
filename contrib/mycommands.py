import __main__
import numpy
import pylab
import os.path
import copy
import topo.patterns.basic
import topo.commands.analysis
#from scipy.integrate import dblquad
#from scipy.optimize.tnc import fmin_tnc
#from scipy.optimize.optimize import fmin, fmin_powell
from math import pi, sqrt, exp, pow
from numpy.oldnumeric import zeros, Float, sum
from fixedpoint import FixedPoint
from topo.projections.basic import CFProjection
from topo.base.boundingregion import BoundingBox
from topo.misc.numbergenerators import UniformRandom, BoundedNumber, ExponentialDecay
from topo.patterns.basic import Gaussian
from topo.outputfns.basic import HomeostaticMaxEnt,OutputFnWithState
from topo.sheets.lissom import LISSOM
from topo.sheets.optimized import NeighborhoodMask_Opt, LISSOM_Opt
from topo.plotting.plotfilesaver import * 
from topo.commands.pylabplots import or_tuning_curve_batch, matrixplot
from topo.commands.analysis import save_plotgroup, measure_or_tuning_fullfield
from topo.misc.filepaths import normalize_path
from topo.commands.pylabplots import plot_tracked_attributes
from topo.base.parameterclasses import Number

import matplotlib 
matplotlib.use('Agg')

from pylab import *
from matplotlib import *


def save_tuning_curve_data(filename,sheet, x_axis, curve_label,x,y):
    i_value,j_value=sheet.sheet2matrixidx(x,y)
    x_values= sorted(sheet.curve_dict[x_axis][curve_label].keys())
    y_values=[sheet.curve_dict[x_axis][curve_label][key].view()[0][i_value,j_value] for key in x_values]
    
    aa = (x_values,y_values)
    
    save(filename,aa,fmt='%.6f', delimiter=',')
    return aa

def get_tuning_curve_data(sheet, x_axis, curve_label,x,y):
    i_value,j_value=sheet.sheet2matrixidx(x,y)
    x_values= sorted(sheet.curve_dict[x_axis][curve_label].keys())
    y_values=[sheet.curve_dict[x_axis][curve_label][key].view()[0][i_value,j_value] for key in x_values]
    
    if(x_axis != "size"):
        x_values.pop(0);y_values.pop(0);
    
    if(x_axis == "size"):
        for i in xrange(len(x_values)):
            x_values[i] = x_values[i]/2.0
    
    #print [x_values,y_values]
    #print [x_values).pop(0).tolist(),fromlist(y_values).pop(0).tolist()]
    return [x_values,y_values]

def save_tuning_curves(prefix):
    #directory = "./LateralLGNData/"
    directory = "./pokus/"
    filename = prefix + ",str=" + str(__main__.LGNLatStr) + ",freq=2.5" + ",surr_size=" + str(__main__.LGNSurroundSize) +  ",lat_size=" + str(__main__.LGNLatSurroundSize) + ",const=1,tsettle=2,"
    
    topo.mycommands.save_tuning_curve_data(directory+filename+"con=30%.dat",topo.sim["LGNOnSep"],"size","Contrast = 30%",0,0)
    topo.mycommands.save_tuning_curve_data(directory+filename+"con=80%.dat",topo.sim["LGNOnSep"],"size","Contrast = 80%",0,0)
    topo.mycommands.save_tuning_curve_data(directory+"Freq"+filename+"con=30%.dat",topo.sim["LGNOnSep"],"frequency","Contrast = 30%",0,0)
    topo.mycommands.save_tuning_curve_data(directory+"Freq"+filename+"con=80%.dat",topo.sim["LGNOnSep"],"frequency","Contrast = 80%",0,0)
    fit_curves(directory,filename,prefix)

def fit_curves(directory,filename,prefix):
    
    stat_filename = "stats"
    #from mlabwrap import mlab  # start a Matlab session
    
    c_asc30 = get_tuning_curve_data(topo.sim["LGNOnSep"],"size","Contrast = 30%",0,0)
    c_asc80 = get_tuning_curve_data(topo.sim["LGNOnSep"],"size","Contrast = 80%",0,0)
    c_freq30 = get_tuning_curve_data(topo.sim["LGNOnSep"],"frequency","Contrast = 30%",0,0)
    c_freq80 = get_tuning_curve_data(topo.sim["LGNOnSep"],"frequency","Contrast = 80%",0,0)
    
    #(trash1,trash2,asc30) = fmin_tnc(fitDoG, [0, 100 , 2,   0.001,   0.03], fprime= None, args = c_asc30, #approx_grad=True,bounds=[[-1,1],[0,200],[0,30],[0,0.01],[0,0.1]])
    #(trash1,trash2,asc80) = fmin_tnc(fitDoG, [0, 100 , 2,   0.001,   0.03], fprime= None, args = c_asc80, #approx_grad=True,bounds=[[-1,1],[0,200],[0,30],[0,0.01],[0,0.1]])
    #(trash1,trash2,dog30) = fmin_tnc(fitDoGfreq, [0,-0.2,-0.18,3, 0.7], fprime= None, args = c_freq30, #approx_grad=True,bounds=[[-1,1],[-1,0],[-1,0],[0,10],[0,1]])
    #(trash1,trash2,dog80) = fmin_tnc(fitDoGfreq, [0,-0.2,-0.18,3,0.7], fprime= None, args = c_freq80, #approx_grad=True,bounds=[[-1,1],[-1,0],[-1,0],[0,10],[0,1]])
    
    asc30 = fmin(fitDoG, [0.3, 30 , 4,   0.003,   0.015],args = c_asc30,xtol = 0.00000001, ftol = 0.00000001,maxiter=12000,maxfun=12000)
    asc80 = fmin(fitDoG, [0.3, 100 , 5,   0.002,   0.03], args = c_asc80,xtol = 0.00000001, ftol = 0.00000001,maxiter=12000,maxfun=12000)
    dog30 = fmin(fitDoGfreq, [0.3,-0.2,-0.18,3,0.7],args = c_freq30,xtol = 0.000001, ftol = 0.000001,maxiter=12000,maxfun=12000)
    dog80 = fmin(fitDoGfreq, [0.3,-0.4,-0.5,3,1],args = c_freq80,xtol = 0.000001, ftol = 0.000001,maxiter=12000,maxfun=12000)
    

    #save the graphs
    clf()
    plot(c_asc30[0],c_asc30[1])
    plot(c_asc30[0],DoG(c_asc30[0],asc30[0],asc30[1],asc30[2],asc30[3],asc30[4]))
    savefig(directory + prefix+ filename + "ASC30"+".png");
    clf()
    plot(c_asc80[0],c_asc80[1])
    plot(c_asc80[0],DoG(c_asc80[0],asc80[0],asc80[1],asc80[2],asc80[3],asc80[4]))
    savefig(directory + prefix+filename + "ASC80"+".png");
    clf()
    plot(c_freq30[0],c_freq30[1])
    plot(c_freq30[0],DoGfreq(c_freq30[0],dog30[0],dog30[1],dog30[2],dog30[3],dog30[4]))
    savefig(directory + prefix+filename + "DOG30"+".png");
    clf()
    plot(c_freq80[0],c_freq80[1])
    plot(c_freq80[0],DoGfreq(c_freq80[0],dog80[0],dog80[1],dog80[2],dog80[3],dog80[4]))
    savefig(directory + prefix+filename + "DOG80"+".png");
    clf()
    # now save to file
    if(not os.path.exists(directory+stat_filename)):
        print "1\n"
        f = open(directory+stat_filename,"w")
        f.write(" Prefix LGNLatStr Frequency CRFSurrSize ECRFSurrSize Const Tsettle Contrast R_0 K_e K_i alpha beta\n")
    else:
        print "2\n"
        f = open(directory+stat_filename,"a")
    
    f.write(prefix + " " + str(__main__.LGNLatStr) + " 2.5 " + str(__main__.LGNSurroundSize) +  " " + str(__main__.LGNLatSurroundSize) + " 1 2 " + " 80 " + str(asc80)+"\n")
    
    f.write(prefix + " " + str(__main__.LGNLatStr) + " 2.5 " + str(__main__.LGNSurroundSize) +  " " + str(__main__.LGNLatSurroundSize) + " 1 2 " + " 30 " + str(asc30)+"\n")
    
    f.write("Freq" + prefix + " " + str(__main__.LGNLatStr) + " 2.5 " + str(__main__.LGNSurroundSize) +  " " + str(__main__.LGNLatSurroundSize) + " 1 2 " + " 80 " + str(dog80)+"\n")
    
    f.write("Freq" + prefix + " " + str(__main__.LGNLatStr) + " 2.5 " + str(__main__.LGNSurroundSize) +  " " + str(__main__.LGNLatSurroundSize) + " 1 2 " + " 30 " + str(dog30)+"\n")
    
    f.close()
    
    print "END"
    
def pokus():
    #f = open("a.dat","r")
    #data = [line.split() for line in f]
    #f.close()
    #return data
    data = [[0.023333,0.046667,0.070000,0.093333,0.116667,0.140000,0.163333,0.186667,0.210000,0.233333,0.256667,0.280000,0.303333,0.326667,0.350000,0.373333,0.396667,0.420000,0.443333,0.466667,0.490000,0.513333,0.536667,0.560000,0.583333,0.606667,0.630000,0.653333,0.676667,0.700000],[0.000000,0.140682,0.323128,0.381151,0.453309,0.495148,0.511234,0.503472,0.476296,0.452621,0.421329,0.391765,0.378917,0.358795,0.345896,0.327351,0.318290,0.308762,0.297803,0.292149,0.285739,0.281539,0.274593,0.272147,0.266158,0.263694,0.259160,0.255340,0.252024,0.248111]]
    

def DoG(Input,Rz,Ke,Ki,alpha,beta):
    A = lambda phi,r: r*exp(-(pow(r,2.0)/alpha))
    B = lambda phi,r: r*exp(-(pow(r,2.0)/beta))
    l = lambda x: 0
    h = lambda x: 2*pi
    x = zeros(len(Input),Float)
    for i in xrange(len(Input)):
        x[i] = Rz + Ke*dblquad(A,0,Input[i],l,h)[0] - Ki*dblquad(B,0,Input[i],l,h)[0] 
    return x

def DoGfreq(Input,Rz,Ke,Ki,alpha,beta):
    A = lambda f: 1-exp(-pow((f/(alpha*2)),2))
    B = lambda f: 1-exp(-pow((f/(beta*2)),2))
    
    x = zeros(len(Input),Float)
    for i in xrange(len(Input)):
        x[i] = Rz + Ke*A(Input[i]) - Ki*B(Input[i])
    return x
    
def fitDoG(x,Input,Actual_Output):
    Rz = x[0]
    Ke = x[1]
    Ki = x[2]
    alpha = x[3]
    beta = x[4]
    Fitted_Curve=DoG(Input,Rz,Ke,Ki,alpha,beta)
    s = 0
    for i in xrange(len(Fitted_Curve)):
        s = s + (Fitted_Curve[i]- Actual_Output[i])*(Fitted_Curve[i]- Actual_Output[i])
    return s

def fitDoGfreq(x,Input,Actual_Output):
    Rz = x[0]
    Ke = x[1]
    Ki = x[2]
    alpha = x[3]
    beta = x[4]
    Fitted_Curve=DoGfreq(Input,Rz,Ke,Ki,alpha,beta)
    s = 0
    for i in xrange(len(Fitted_Curve)):
        s = s + (Fitted_Curve[i]- Actual_Output[i])*(Fitted_Curve[i]- Actual_Output[i])
    return s


def save_plots(prefix):
    p  = CFProjectionPlotGroupSaver("Projection"),
    pre = prefix + create_prefix(["V1afferent_lr" , "V1afferent_str", "V1afferent_lrtc", "V1afferent_size", "V2lateral_inh_size", "V2lateral_exc_size"]),
    p.filename_prefix = pre,
    p.projection_name="V1Afferent",
    p.sheet_name="V2",
    p.plotgroup=p.generate_plotgroup(),
    p.plotgroup.update_plots(True),
    p.save_to_disk()

def create_prefix(variables):
    prefix = ""
    for var in variables:
        prefix = prefix + " " + var +"=" + str(__main__.__dict__[var])
    return prefix


def _run_combinations_rec(func,param,params,index):
    if(len(params) == index):
        func(*param)
        return
    a = params[index]
    for p in a:
        new_param = param + [p]
        _run_combinations_rec(func,new_param,params,index+1)

def run_combinations(func, params):
    """
        this function runs function func with all combinations of params defined in the array params, eg.
        params = [[1,2,3],[1,2,3]...]
    """
    _run_combinations_rec(func,[],params,0)


def AddV2():
    corners = [topo.patterns.basic.Composite(operator = numpy.maximum,
                    generators = [
                                       #topo.patterns.basic.Gaussian(scale=1,size = 0.08838,orientation=0,aspect_ratio=5.6666,x=0.45),
                                       #topo.patterns.basic.Gaussian(scale=1,size = 0.08838,orientation=pi/2,aspect_ratio=5.6666,y=0.45)],
                                       topo.patterns.basic.Gaussian(scale=1,size = 0.06,orientation=0,aspect_ratio=7,x=0.3),
                                       topo.patterns.basic.Gaussian(scale=1,size = 0.06,orientation=pi/2,aspect_ratio=7,y=0.3)],
                    scale=1.0, bounds=BoundingBox(radius=0.8),
                    x=UniformRandom(lbound=-(globals().get('BS',0.5)+0.25),ubound=(globals().get('BS',0.5)+0.25),seed=12),
                    y=UniformRandom(lbound=-(globals().get('BS',0.5)+0.25),ubound=(globals().get('BS',0.5)+0.25),seed=34),
                    orientation=UniformRandom(lbound=-pi,ubound=pi,seed=56))
                for i in xrange(1)]
    #combined_corners = topo.patterns.basic.SeparatedComposite(min_separation=2.2*0.27083,generators=corners)
    combined_corners = corners[0]

    topo.sim['Retina'].set_input_generator(combined_corners)
    
    topo.sim['V2'] = LISSOM(nominal_density=globals().get('default_density',48.0),
                        nominal_bounds=BoundingBox(radius=globals().get('CS',0.5)),tsettle=9,
                        output_fn=HomeostaticMaxEnt(a_init=14.5, b_init=globals().get('BINI',-4), mu=globals().get('V2MU',0.01)))

    topo.sim.connect('V1Complex','V2',delay=FixedPoint("0.05"),dest_port=('Activity','JointNormalize', 'Afferent'),
                    connection_type=CFProjection,strength=globals().get('V1aff_str',1),name='V1Afferent',
                    weights_generator=topo.patterns.basic.Composite(operator=numpy.multiply, 
                                                                    generators=[Gaussian(aspect_ratio=1.0, size=3),#globals().get('V1aff_size',30)),
                                                                                topo.patterns.random.UniformRandom()]),
                    nominal_bounds_template=BoundingBox(radius=globals().get('V1aff_size',2*0.27083)/2),learning_rate=(BoundedNumber(bounds=(0.137,None),generator=
                                                                                                    ExponentialDecay(starting_value = globals().get('V1aff_lr',0.9590/2),
                                                                                                                    time_constant=globals().get('V1aff_lrtc',1600),
                                                                                                                    time_offset=2000))))
    topo.sim.connect('V2','V2',delay=FixedPoint("0.05"),name='V2LateralExcitatory',
                    connection_type=CFProjection,strength=0.9,
                    weights_generator=topo.patterns.basic.Gaussian(aspect_ratio=1.0, size=globals().get('V2lat_exc_size',0.04)),
                    nominal_bounds_template=BoundingBox(radius=globals().get('V2lat_exc_size',0.04)/2),learning_rate=0) 
                
    topo.sim.connect('V2','V2',delay=FixedPoint("0.05"),name='V2LateralInhibitory',
                    connection_type=CFProjection,strength=-0.9,
                    weights_generator=topo.patterns.basic.Composite(operator=numpy.multiply, 
                                                                    generators=[Gaussian(aspect_ratio=1.0,      size=globals().get('V2lat_inh_size',2*0.22917)),
                                                                                topo.patterns.random.UniformRandom()]),
                    nominal_bounds_template=BoundingBox(radius=globals().get('V2lat_inh_size',2*0.22917)/2),learning_rate=1.8087)

    topo.sim["V1Simple"].in_connections[0].strength=1.8
    topo.sim["V1Simple"].in_connections[1].strength=1.8
    

def AddGC():
    from topo.outputfns.basic import PiecewiseLinear, DivisiveNormalizeL1,Sigmoid 
    from fixedpoint import FixedPoint
    from topo.projections.basic import CFProjection, SharedWeightCFProjection
    from topo.base.boundingregion import BoundingBox
    lgn_surroundg = Gaussian(size=locals().get('LGNLatSurroundSize',0.5),aspect_ratio=1.0,output_fn=DivisiveNormalizeL1())


    topo.sim.connect('LGNOn','LGNOn',delay=FixedPoint("0.05"),dest_port=('Activity','Divisive'),
                    connection_type=SharedWeightCFProjection,strength=locals().get('LGNLatStr',35),
                    nominal_bounds_template=BoundingBox(radius=0.5),name='LGNLateralOn',
                    weights_generator=lgn_surroundg)
    
    topo.sim.connect('LGNOff','LGNOff',delay=FixedPoint("0.05"),dest_port=('Activity','Divisive'),
                    connection_type=SharedWeightCFProjection,strength=locals().get('LGNLatStr',35),
                    nominal_bounds_template=BoundingBox(radius=0.5),name='LGNLateralOff',
                    weights_generator=lgn_surroundg)
    
    topo.sim["V1"].in_connections[0].strength=5.0
    topo.sim["V1"].in_connections[1].strength=5.0
    #topo.sim["V1"].output_fn = Sigmoid(k=-4.3,r=8.5)
    
    topo.sim["LGNOn"].tsettle = 2
    topo.sim["LGNOff"].tsettle = 2
    topo.sim["LGNOn"].strict_tsettle=1
    topo.sim["LGNOff"].strict_tsettle=1
    

#global parameter holding the activities
activity_history=numpy.array([])
def collect_activity_statistics():
    topo.commands.analysis.coordinate = [0.0,0.0]
    topo.commands.analysis.sheet_name = "V1"
    
    topo.mycommands.activity_history = numpy.concatenate((topo.mycommands.activity_history,topo.sim["V1"].activity.flatten()),axis=1)

    if(topo.sim.time() == 5000): 
        pylab.figure()
        pylab.hist(topo.mycommands.activity_history,(numpy.arange(20.0)/20.0))
        pylab.savefig("./Output/" + str(topo.sim.time()) + 'activity_histogram.png')
    #    measure_or_tuning_fullfield()
    #    or_tuning_curve_batch("Output","OrientationTC:V1:[0,0]",pylab.plot,"degrees","V1",[0,0],"orientation")
        save_plotgroup('Activity')

def homeostatic_analysis_function():
    """
    Basic example of an analysis command for run_batch; users are
    likely to need something similar but highly customized.
    """
    
  
    if __main__.__dict__['triesch'] == True or  __main__.__dict__['simple'] == True: 
        plot_tracked_attributes(topo.sim["V1"].output_fn.output_fns[0], 0, topo.sim.time(), filename="Afferent", ylabel="Afferent")
        plot_tracked_attributes(topo.sim["V1"].output_fn.output_fns[2], 0, topo.sim.time(), filename="V1", ylabel="V1")
    else:
        plot_tracked_attributes(topo.sim["V1"].output_fn.output_fns[0], 0, topo.sim.time(), filename="Afferent", ylabel="Afferent")
        plot_tracked_attributes(topo.sim["V1"].output_fn.output_fns[3], 0, topo.sim.time(), filename="V1", ylabel="V1")

   
    plot_tracked_attributes(topo.sim["V1"].projections()["LGNOnAfferent"].output_fn.output_fns[1], 0,topo.sim.time(), filename="LGNOnBefore", ylabel="LGNOnBefore")
    plot_tracked_attributes(topo.sim["V1"].projections()["LGNOffAfferent"].output_fn.output_fns[1], 0,topo.sim.time(), filename="LGNOffBefore", ylabel="LGNOffBefore")
    #plot_tracked_attributes(topo.sim["V1"].projections()["LGNOnAfferent"].debug_output_fn.output_fns[1], 0,topo.sim.time(), filename="LGNOnAfter", ylabel="LGNOnAfter")
    #plot_tracked_attributes(topo.sim["V1"].projections()["LGNOffAfferent"].debug_output_fn.output_fns[1], 0,topo.sim.time(), filename="LGNOffAfter", ylabel="LGNOffAfter")
    plot_tracked_attributes(topo.sim["V1"].projections()["LateralExcitatory"].output_fn.output_fns[1], 0,topo.sim.time(), filename="LatExBefore", ylabel="LatExBefore")
    plot_tracked_attributes(topo.sim["V1"].projections()["LateralInhibitory"].output_fn.output_fns[1], 0,topo.sim.time(), filename="LatInBefore", ylabel="LatInBefore")
    

class SimpleHomeo(OutputFnWithState):
    mu = Number(default=0.01,doc="Target average activity.")
    a_init = Number(default=13,doc="Multiplicative parameter controlling the exponential.")
    b_init = Number(default=-4,doc="Additive parameter controlling the exponential.")
    eta = Number(default=0.0002,doc="Learning rate for homeostatic plasticity.")
    smoothing = Number(default=0.9997, doc="Weighting of previous activity vs. current activity when calculating the average.")

    def __init__(self,**params):
        super(SimpleHomeo,self).__init__(**params)
	self.first_call = True

    def __call__(self,x):
        
	if self.first_call:
	    self.first_call = False
	    self.a = ones(x.shape, x.dtype.char) * self.a_init
	    self.b = ones(x.shape, x.dtype.char) * self.b_init
	    self.y_avg = zeros(x.shape, x.dtype.char) 

        x_orig = copy(x)
        x *= 0.0
	x += 1.0 / (1.0 + exp(-(self.a*x_orig + self.b)))

        if self.plastic & (float(topo.sim.time()) % 1.0 >= 0.54):
	    print "IN1"
            self.y_avg = (1.0-self.smoothing)*x + self.smoothing*self.y_avg 
            # Update a and b
	    self.a += self.eta * (self.y_avg - self.mu)
