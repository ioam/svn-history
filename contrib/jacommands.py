import __main__
import numpy
import pylab
import os.path
import os
import copy
import pdb

from topo import param

import topo.pattern.basic
import topo.command.analysis
from math import pi, sqrt, exp, pow
from numpy.oldnumeric import zeros, Float, sum
from topo.projection.basic import CFProjection
from topo.base.boundingregion import BoundingBox
from topo.misc.numbergenerator import UniformRandom, BoundedNumber, ExponentialDecay
from topo.pattern.basic import Gaussian,Selector,Null
from topo.outputfn.basic import HomeostaticMaxEnt,OutputFnWithState
from topo.base.arrayutil import clip_lower
from topo.sheet.lissom import LISSOM
from topo.sheet.optimized import NeighborhoodMask_Opt, LISSOM_Opt
from topo.plotting.plotfilesaver import * 
from topo.command.pylabplots import cyclic_tuning_curve, matrixplot
from topo.command.analysis import save_plotgroup
from topo.misc.filepath import normalize_path,application_path
from topo.command.pylabplots import plot_tracked_attributes
from topo.base.functionfamily import CoordinateMapperFn
from topo.plotting.bitmap import MontageBitmap
from topo.base.patterngenerator import PatternGenerator,Constant 
from topo.outputfn.basic import  Sigmoid



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
    corners = [topo.pattern.basic.Composite(operator = numpy.maximum,
                    generators = [
                                       #topo.pattern.basic.Gaussian(scale=1,size = 0.08838,orientation=0,aspect_ratio=5.6666,x=0.45),
                                       #topo.pattern.basic.Gaussian(scale=1,size = 0.08838,orientation=pi/2,aspect_ratio=5.6666,y=0.45)],
                                       topo.pattern.basic.Gaussian(scale=1,size = 0.04,orientation=0,aspect_ratio=9,x=0.2),
                                       topo.pattern.basic.Gaussian(scale=1,size = 0.04,orientation=pi/2,aspect_ratio=9,y=0.2)],
                    scale=1.0, bounds=BoundingBox(radius=0.5),
                    x=UniformRandom(lbound=-(__main__.__dict__.get('BS',0.5)),ubound=(__main__.__dict__.get('BS',0.5)),seed=12),
                    y=UniformRandom(lbound=-(__main__.__dict__.get('BS',0.5)),ubound=(__main__.__dict__.get('BS',0.5)),seed=34),
                    orientation=UniformRandom(lbound=-pi,ubound=pi,seed=56))
                for i in xrange(1)]
    #combined_corners = topo.pattern.basic.SeparatedComposite(min_separation=2.2*0.27083,generators=corners)
    combined_corners = corners[0]

    topo.sim['Retina'].set_input_generator(combined_corners)
    
    topo.sim['V2'] = LISSOM(nominal_density=__main__.__dict__.get('default_density',48.0),
                        nominal_bounds=BoundingBox(radius=__main__.__dict__.get('CS',0.5)),tsettle=9,
                        #output_fn=HomeostaticMaxEnt(a_init=14.5, b_init=__main__.__dict__.get('BINI',-4), mu=__main__.__dict__.get('V2MU',0.01)))
                        output_fn=Sigmoid(r=locals().get('r_init',8),k=locals().get('k_init',-3)))

    topo.sim.connect('V1Complex','V2',delay=0.05,dest_port=('Activity','JointNormalize', 'Afferent'),
                    connection_type=CFProjection,strength=__main__.__dict__.get('V2aff_str',0.8),name='V1Afferent',
                    weights_generator=topo.pattern.basic.Composite(operator=numpy.multiply, 
                                                                    generators=[Gaussian(aspect_ratio=1.0, size=3),#__main__.__dict__.get('V1aff_size',30)),
                                                                                topo.pattern.random.UniformRandom()]),
                    nominal_bounds_template=BoundingBox(radius=__main__.__dict__.get('V2aff_size',2*0.27083)/2),learning_rate=1.0);

    topo.sim.connect('V2','V2',delay=0.025,name='V2LateralExcitatory',
                    connection_type=CFProjection,strength=0.9,
                    weights_generator=topo.pattern.basic.Gaussian(aspect_ratio=1.0, size=__main__.__dict__.get('V2lat_exc_size',0.04)),
                    nominal_bounds_template=BoundingBox(radius=__main__.__dict__.get('V2lat_exc_size',0.08)/2),learning_rate=0) 
                
    topo.sim.connect('V2','V2',delay=0.025,name='V2LateralInhibitory',
                    connection_type=CFProjection,strength=-0.9,
                    weights_generator=topo.pattern.basic.Composite(operator=numpy.multiply, 
                                                                    generators=[Gaussian(aspect_ratio=1.0,      size=__main__.__dict__.get('V2lat_inh_size',2*0.22917)),
                                                                                topo.pattern.random.UniformRandom()]),
                    nominal_bounds_template=BoundingBox(radius=__main__.__dict__.get('V2lat_inh_size',2*0.22917)/2),learning_rate=0)

    topo.sim["V1Simple"].in_connections[0].strength=2.5
    topo.sim["V1Simple"].in_connections[1].strength=2.5
    #topo.sim["V1Complex"].output_fn.output_fns[1].r=7
    topo.sim["V1Simple"].plastic=False
    topo.sim["V1Complex"].plastic=False
    
    ### Lateral excitatory bounds changes
    LE='topo.sim["V2"].projections()["V2LateralExcitatory"]'

    topo.sim.schedule_command( 20200,LE+'.change_bounds(BoundingBox(radius=0.06250))')
    topo.sim.schedule_command( 20500,LE+'.change_bounds(BoundingBox(radius=0.04375))')
    topo.sim.schedule_command( 21000,LE+'.change_bounds(BoundingBox(radius=0.03500))')
    topo.sim.schedule_command( 22000,LE+'.change_bounds(BoundingBox(radius=0.02800))')
    topo.sim.schedule_command( 23000,LE+'.change_bounds(BoundingBox(radius=0.02240))')
    topo.sim.schedule_command( 24000,LE+'.change_bounds(BoundingBox(radius=0.01344))')
    topo.sim.schedule_command( 25000,LE+'.change_bounds(BoundingBox(radius=0.00806))')
    topo.sim.schedule_command( 26500,LE+'.change_bounds(BoundingBox(radius=0.00484))')
    topo.sim.schedule_command( 28000,LE+'.change_bounds(BoundingBox(radius=0.00290))')
    topo.sim.schedule_command(40000,LE+'.change_bounds(BoundingBox(radius=0.00174))')
    
    

def divide_with_constant(x,y):
    return numpy.divide(x,y+1.0)
    

def AddGC():
    from topo.outputfn.basic import PiecewiseLinear, DivisiveNormalizeL1,Sigmoid 
    from topo.projection.basic import CFProjection, SharedWeightCFProjection
    from topo.base.boundingregion import BoundingBox
    lgn_surroundg = Gaussian(size=__main__.__dict__.get('LGNLatSurroundSize',0.5),aspect_ratio=1.0,output_fn=DivisiveNormalizeL1())


    topo.sim.connect('LGNOn','LGNOn',delay=0.05,dest_port=('Activity'),activity_group=(0.6,divide_with_constant),
                    connection_type=SharedWeightCFProjection,strength=__main__.__dict__.get('LGNLatStr',135),
                    nominal_bounds_template=BoundingBox(radius=0.5),name='LGNLateralOn',
                    weights_generator=lgn_surroundg)
    
    topo.sim.connect('LGNOff','LGNOff',delay=0.05,dest_port=('Activity'),activity_group=(0.6,divide_with_constant),
                    connection_type=SharedWeightCFProjection,strength=__main__.__dict__.get('LGNLatStr',135),
                    nominal_bounds_template=BoundingBox(radius=0.5),name='LGNLateralOff',
                    weights_generator=lgn_surroundg)
    
    topo.sim["LGNOn"].tsettle = 2
    topo.sim["LGNOff"].tsettle = 2
    topo.sim["LGNOn"].strict_tsettle=1
    topo.sim["LGNOff"].strict_tsettle=1
    

#global parameter holding the activities
activity_history=numpy.array([])
def collect_activity_statistics():
    topo.mycommands.activity_history = numpy.concatenate((topo.mycommands.activity_history,topo.sim["V1"].activity.flatten()),axis=1)

    if(topo.sim.time() == 5000): 
        pylab.figure()
        pylab.hist(topo.mycommands.activity_history,(numpy.arange(20.0)/20.0))
        pylab.savefig("./Output/" + str(topo.sim.time()) + 'activity_histogram.png')
    #    measure_or_tuning_fullfield()
    #    cyclic_tuning_curve_batch(filename="OrientationTC:V1:[0,0]",sheet=topo.sim["V1"],coords=[(0,0)],x_axis="orientation")
        save_plotgroup('Activity')

def homeostatic_analysis_function():
    """
    Basic example of an analysis command for run_batch; users are
    likely to need something similar but highly customized.
    """
    #plot_tracked_attributes(output_fn=topo.sim["V1"].output_fn.output_fns[0], init_time=0, final_timetopo.sim.time(), filename="Afferent", ylabel="Afferent")
    #plot_tracked_attributes(output_fn=topo.sim["V1"].output_fn.output_fns[2], init_time=0, final_timetopo.sim.time(), filename="V1", ylabel="V1")

  
    

class SimpleHomeoSigmoid(OutputFnWithState):
    mu = param.Number(default=0.01,doc="Target average activity.")
    a_init = param.Number(default=13,doc="Multiplicative parameter controlling the exponential.")
    b_init = param.Number(default=-4,doc="Additive parameter controlling the exponential.")
    eta = param.Number(default=0.0002,doc="Learning rate for homeostatic plasticity.")
    smoothing = param.Number(default=0.9997, doc="Weighting of previous activity vs. current activity when calculating the average.")
    randomized_init = param.Boolean(False, doc="Whether to randomize the initial B parameter")
    noise_magnitude =  param.Number(default=0.1, doc="The magnitude of the additive noise to apply to the B parameter at initialization")

    def __init__(self,**params):
        super(SimpleHomeoSigmoid,self).__init__(**params)
        self.first_call = True

    def __call__(self,x):
       
        if self.first_call:
            self.first_call = False
            self.a = ones(x.shape, x.dtype.char) * self.a_init
            if self.randomized_init:
                self.b = ones(x.shape, x.dtype.char) * self.b_init  + (topo.pattern.random.UniformRandom()(xdensity=x.shape[0],ydensity=x.shape[1])-0.5)*self.noise_magnitude*2
            else:
                self.b = ones(x.shape, x.dtype.char) * self.b_init
            
            self.y_avg = zeros(x.shape, x.dtype.char) * self.mu

        x_orig = copy(x)
        x *= 0.0
        x += 1.0 / (1.0 + exp(-(self.a*x_orig + self.b)))

        if self.plastic & (float(topo.sim.time()) % 1.0 >= 0.54):
            self.y_avg = (1.0-self.smoothing)*x + self.smoothing*self.y_avg
            self.b -= self.eta * (self.y_avg - self.mu)


class SimpleHomeoLinear(OutputFnWithState):
    mu = param.Number(default=0.01,doc="Target average activity.")
    t_init = param.Number(default=0.0,doc="Threshold parameter")
    eta = param.Number(default=0.0002,doc="Learning rate for homeostatic plasticity.")
    smoothing = param.Number(default=0.9997, doc="Weighting of previous activity vs. current activity when calculating the average.")
    randomized_init = param.Boolean(False, doc="Whether to randomize the initial t parameter")
    noise_magnitude =  param.Number(default=0.1, doc="The magnitude of the additive noise to apply to the B parameter at initialization")

    def __init__(self,**params):
        super(SimpleHomeoLinear,self).__init__(**params)
        self.first_call = True

    def __call__(self,x):
       
        if self.first_call:
            self.first_call = False
            if self.randomized_init:
                self.t = ones(x.shape, x.dtype.char) * self.t_init  + (topo.pattern.random.UniformRandom()(xdensity=x.shape[0],ydensity=x.shape[1])-0.5)*self.noise_magnitude*2
            else:
                self.t = ones(x.shape, x.dtype.char) * self.t_init
            
            self.y_avg = zeros(x.shape, x.dtype.char) * self.mu

        x_orig = copy(x)
        x -= self.t
        clip_lower(x,0)

        if self.plastic & (float(topo.sim.time()) % 1.0 >= 0.54):
            self.y_avg = (1.0-self.smoothing)*x + self.smoothing*self.y_avg 
            self.t += self.eta * (self.y_avg - self.mu)

class SimpleHomeoLinearRelative(OutputFnWithState):
    input_output_ratio = param.Number(default=3.6,doc="The ratio between the average input and output activity")
    t_init = param.Number(default=-0.0,doc="Threshold parameter")
    eta = param.Number(default=0.0002,doc="Learning rate for homeostatic plasticity.")
    smoothing = param.Number(default=0.9997, doc="Weighting of previous activity vs. current activity when calculating the average.")
    randomized_init = param.Boolean(False, doc="Whether to randomize the initial t parameter")
    noise_magnitude =  param.Number(default=0.1, doc="The magnitude of the additive noise to apply to the B parameter at initialization")
        
    def __init__(self,**params):
        super(SimpleHomeoLinearRelative,self).__init__(**params)
        self.first_call = True
        self.mu = 0

    def __call__(self,x):
       
        if self.first_call:
            self.first_call = False
            if self.randomized_init:
                self.t = ones(x.shape, x.dtype.char) * self.t_init  + (topo.pattern.random.UniformRandom()(xdensity=x.shape[0],ydensity=x.shape[1])-0.5)*self.noise_magnitude*2
            else:
                self.t = ones(x.shape, x.dtype.char) * self.t_init
            
            self.y_avg = zeros(x.shape, x.dtype.char) * self.mu

        x_orig = copy(x)
        x -= self.t
        clip_lower(x,0)
        self.mu = topo.sim["V1"].x_avg/self.input_output_ratio
        if self.plastic & (float(topo.sim.time()) % 1.0 >= 0.54):
            self.y_avg = (1.0-self.smoothing)*x + self.smoothing*self.y_avg 
            self.t += self.eta * (self.y_avg - self.mu)
        # recalculate the mu based on the input/ output ratio
        


class Jitter(CoordinateMapperFn):
    scale =  0.4    
    rand = param.Parameter(default=None)    
    def __call__(self,x,y):
            return x+(self.rand()-0.5)*self.scale,y+(self.rand()-0.5)*self.scale


current_histogram = []
activity_queue = []
call_time=0
def update_histogram(sheet_name="V1"):
    import contrib.jacommands
    contrib.jacommands.activity_queue.insert(0,topo.sim[sheet_name].activity)
    if(contrib.jacommands.call_time>=1000):
        contrib.jacommands.activity_queue.pop()
    contrib.jacommands.call_time=contrib.jacommands.call_time+1
    contrib.jacommands.current_histogram = numpy.empty(0)
    for a in contrib.jacommands.activity_queue:
        numpy.concatenate((contrib.jacommands.current_histogram,a.flatten()),axis=1)
    print contrib.jacommands.current_histogram     


activities = []
def collect_activity(sheet_name):
    import contrib.jacommands
    contrib.jacommands.activities.insert(0,topo.sim[sheet_name].activity.copy())

def measure_histogram(iterations=1000,sheet_name="V1"):
    import contrib.jacommands    
    
    topo.sim["V1"].plastic=False
    topo.sim.state_push()
    
    for i in xrange(0,iterations):
        topo.sim.run(1)
        contrib.jacommands.collect_activity(sheet_name)
        
    topo.sim.state_pop()
    concat_activities=[]
        
    for a in contrib.jacommands.activities:
            concat_activities = numpy.concatenate((concat_activities,a.flatten()),axis=1)
    
    topo.sim["V1"].plastic=True
    contrib.jacommands.activities = []
    
    pylab.figure()
    pylab.subplot(111, yscale='log')
    #pylab.subplot(111)
    mu = sum(concat_activities)/size(concat_activities)
    (bins,a,b) =  pylab.hist(concat_activities,(numpy.arange(40.0)/40.0)*2,visible=False)
    bins_axis = numpy.arange(40.0)/40.0*2
    bins = bins *1.0/ sum(bins)
    exponential = numpy.arange(40,dtype='float32')/40.0*2
    # compute the mean of the actual distribution
    print mu
    exponential=  numpy.exp(-(1/mu)*exponential) / mu
    pylab.plot(bins_axis,bins/0.05)
    pylab.plot(bins_axis,bins/0.05,'ro')
    pylab.plot(bins_axis,exponential)
    pylab.plot(bins_axis,exponential,'go')
    pylab.axis(ymin=0.000001,ymax=1)
    #pylab.axis("tight")
    pylab.show()
      
    
    pylab.savefig(normalize_path(str(topo.sim.time()) + 'activity_histogram.png'))

    
    
def enable_movie():
    # Add a timecode to each movie
    ActivityMovie.add_timecode = True
    ActivityMovie.timecode_fmt = '%.2f'

    # The format for times in filenames
    ActivityMovie.filename_time_fmt = '%06.2f'

    # Frame filenames should be like: "frame002.30.tif"
    ActivityMovie.filename_fmt = 'frame%t.%T'

    # The directory for movie frames:
    ActivityMovie.filename_prefix = 'lissom_or_movie/'

    # Frames should be on a white background
    MontageBitmap.bg_color = (1,1,1)
    # Maps within each frame will fit to 200x200 pixel tiles
    MontageBitmap.tile_size = (200,200)

    # The montages will contain 1x2 images
    MontageBitmap.shape = (1,2)
    # Frame title parameters
    MontageBitmap.title_pos = (5,5)
    #MontageBitmap.title_options = dict(fill='white')

    topo.sim['Data'] = InMemoryRecorder()
    
    topo.sim.connect('Retina','Data',
                    src_port = 'Activity',
                    name = 'Retina Activity')
    topo.sim.connect('V1','Data',
                    src_port = 'Activity',
                    name = 'V1 Activity')

def save_movie():
    # Create a movie
    print 'Composing movie...'
    movie = ActivityMovie(name = 'Lissom Orientation Movie',
                        recorder = topo.sim['Data'],
                        montage_params = dict(titles=['Retina','V1']),
                        variables = ['Retina Activity','V1 Activity'],
                        frame_times = list(numpy.arange(0,10.0,0.1)))

    
    # Save the frames to files:
    print 'Saving movie to %s...' % ActivityMovie.filename_prefix
    movie.save()
    
def randomize_V1Simple_relative_LGN_strength(sheet_name="V1Simple",prob=0.1):
    lgn_on_proj =  topo.sim[sheet_name].in_connections[0]
    lgn_off_proj = topo.sim[sheet_name].in_connections[1]
    
    rand = UniformRandom()
    
    rows,cols = lgn_on_proj.cfs.shape
    for r in xrange(rows):
        for c in xrange(cols):
            print r,c
            cf_on = lgn_on_proj.cfs[r,c]
            cf_off = lgn_off_proj.cfs[r,c]
            
            cf_on._has_norm_total=False
            cf_off._has_norm_total=False

            ra = rand()
            a = prob
            if ra>=0.5: a = (1-a)
            
            cf_on.weights*=a 
            cf_off.weights*=(1-a)
            

            
            
class CascadeHomeostatic(OutputFnWithState):
    """
    """

    a_init = param.Number(default=13,doc="Multiplicative parameter controlling the exponential.")
    
    b_init = param.Number(default=-4,doc="Additive parameter controlling the exponential.")
    
    b_eta = param.Number(default=0.02,doc="Learning rate for homeostatic plasticity.")
    
    a_eta = param.Number(default=0.002,doc="Learning rate for homeostatic plasticity.")
    
    mu = param.Number(default=0.01,doc="Target average firing rate.")
    
    b_smoothing = param.Number(default=0.997, doc="""
        Weighting of previous activity vs. current activity when calculating the average.""")
    
    a_smoothing = param.Number(default=0.9997, doc="""
        Weighting of previous activity vs. current activity when calculating the average.""")

    g_smoothing = param.Number(default=0.99, doc="")

    num_cascades = param.Number(default=9,doc="Target average firing rate.")
    thresholds = [0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9]
    a_grad  = []
    step = param.Number(default=1, doc="""
        How often to update the a and b parameters.
        For instance, step=1 means to update it every time this OF is
        called; step=2 means to update it every other time.""")
    

    def __init__(self,**params):
        super(CascadeHomeostatic,self).__init__(**params)
        self.first_call = True
        self.n_step=0
      

    def __call__(self,x):

      
        if self.first_call:
            self.first_call = False
            self.a = ones(x.shape, x.dtype.char) * self.a_init
            self.b = ones(x.shape, x.dtype.char) * self.b_init
            self.y_avg = zeros(x.shape, x.dtype.char) 
            self.a_grad = zeros(x.shape, x.dtype.char) 
            self.y_counts = []
            self.targets = []
            for i in xrange(self.num_cascades):
                self.y_counts.append(zeros(x.shape, x.dtype.char))
                self.targets.append(exp(-self.thresholds[i]/self.mu))
            print self.targets

        # Apply sigmoid function to x, resulting in what Triesch calls y
        x_orig = copy(x)
       
        x *= 0.0
        x += 1.0 / (1.0 + exp(-(self.a*x_orig + self.b)))


        self.n_step += 1
        if self.n_step == self.step:
            self.n_step = 0
            if self.plastic:                
                self.y_avg = (1.0-self.b_smoothing)*x + self.b_smoothing*self.y_avg #Calculate average for use in debugging only
                self.b -= self.b_eta * (self.y_avg - self.mu)
                tmp = zeros(x.shape, x.dtype.char)                 
                for i in xrange(self.num_cascades):
                    self.y_counts[i] = (1.0-self.a_smoothing)*((x >= self.thresholds[i])*1.0) + self.a_smoothing*self.y_counts[i]
                    self.a -= self.a_eta * ((self.y_counts[i] >= self.targets[i])*2.0-1.0)
                    tmp += ((self.y_counts[i] >= self.targets[i])*2.0-1.0)
                #self.a_grad = tmp*(1-self.g_smoothing) + self.a_grad*self.g_smoothing
                self.a_grad = x*(1-self.g_smoothing) + self.a_grad*self.g_smoothing
                self.y_count=self.a_grad
                
                print '%05g %05g %05g %05g %05g %05g %05g %05g %05g' % tuple(self.targets)
                print '%05g %05g %05g %05g %05g %05g %05g %05g %05g' % (self.y_counts[0][24,24],self.y_counts[1][24,24],self.y_counts[2][24,24],self.y_counts[3][24,24],self.y_counts[4][24,24],self.y_counts[5][24,24],self.y_counts[6][24,24],self.y_counts[7][24,24],self.y_counts[8][24,24])
                print [self.y_count[24,24],self.a[24,24],self.b[24,24]]
                print "\n"
                

  
class ActivityHysteresis(OutputFnWithState):
    """ 
    This output function allows the activity to be smoothly interpolated between 
    individual time step of the simulation. The time_constant paremater controls the 
    time scale of this interpolation. 
    """

    time_constant  = param.Number(default = 0.3,doc="""Time constant of the continouse projection input calculation.""")
    
    def __init__(self,**params):
        super(ActivityHysteresis,self).__init__(**params)
        self.first_call = True
        self.old_a = 0 
        import topo.sheet.lissom
        import topo.base.functionfamily
        #topo.sheet.lissom.LISSOM.beginning_of_iteration.append(self.reset)
        topo.base.functionfamily.PatternDrivenAnalysis.pre_presentation_hooks.append(self.reset)
        
    def __call__(self,x):
        if (self.first_call == True):
           self.old_a = x.copy() * 0.0
           self.first_call = False
           
        #if (float(topo.sim.time()) %1.0) <= 0.15: self.old_a =  self.old_a* 0 
        new_a = x.copy()
        self.old_a = self.old_a + (new_a - self.old_a)*self.time_constant
        x*=0
        x += self.old_a
        
    def reset(self):
        self.old_a *= 0

class Habituation(OutputFnWithState):
    """ 
    This output function allows the activity to be smoothly interpolated between 
    individual time step of the simulation. The time_constant paremater controls the 
    time scale of this interpolation. 
    """

    smoothing  = param.Number(default = 0.99,doc="""The time constant defining the width of the window over which activity is averaged""")
    alpha = param.Number(default = 1.0,doc="""This parameter defines how strong influence on the output of the neuron does the habituation has """)

    def __init__(self,**params):
        super(Habituation,self).__init__(**params)
        self.first_call = True
        self.y_avg = 0 
        
    def __call__(self,x):
        if (self.first_call == True):
           self.old_a = x.copy() * 0.0
           self.first_call = False
        
        x_orig = copy(x)
        if self.plastic:                
           self.y_avg = (1.0-self.smoothing)*x + self.smoothing*self.y_avg 
   
        x -= self.alpha *self.y_avg
        x -= x*((x<=0) * 1.0)

        
class Translator(PatternGenerator):
    """
    PatternGenerator that moves another PatternGenerator over time.
    
    To create a pattern at a new location, asks the underlying
    PatternGenerator to create a new pattern at a location translated
    by an amount based on the global time.
    """

    generator = param.ClassSelector(default=Constant(scale=0.0),
        class_=PatternGenerator,doc="""Pattern to be translated.""")
        
    direction = param.Number(default=0,bounds=(-pi,pi),doc="""
        The direction in which the pattern should move, in radians.""")
    
    speed = param.Number(default=1,bounds=(0.0,None),doc="""
        The speed with which the pattern should move,
        in sheet coordinates per simulation time unit.""")
    
    reset_period = param.Number(default=1,bounds=(0.0,None),doc="""
        When pattern position should be reset, usually to the value of a dynamic parameter.

        The pattern is reset whenever fmod(simulation_time,reset_time)==0.""")
    
    last_time = 0.0


    def __init__(self,**params):
        super(Translator,self).__init__(**params)
        self.orientation = params.get('orientation',self.orientation)
        self.index = 0
        
    def __call__(self,**params):
        """Construct new pattern out of the underlying one."""
        generator = params.get('generator', self.generator)

        # JABALERT: This condition seems to conflict with the
        # docstring above; plus, the special case of 0.05 should be
        # documented.  Maybe use a special case for last_time=0.0
        # instead, to avoid depending on 0.05?
        
        xdensity=params.get('xdensity',self.xdensity)
        ydensity=params.get('ydensity',self.ydensity)
        bounds = params.get('bounds',self.bounds)

        # CB: are the float() calls required because the comparisons
        # involving FixedPoint fail otherwise? Or for some other
        # reason?
        if((float(topo.sim.time()) >= self.last_time + self.reset_period) or (float(topo.sim.time()) <=0.05)):
            if ((float(topo.sim.time()) <= (self.last_time+self.reset_period+1.0)) and (float(topo.sim.time()) >=0.05))    :
                return Null()(xdensity=xdensity,ydensity=ydensity,bounds=bounds)
        
            self.last_time += self.reset_period
            # time to reset the parameter
            (self.x, self.y, self.scale) = (generator.x,generator.y,generator.scale)
            if isinstance(generator,Selector):
                self.index = generator.index
            generator.force_new_dynamic_value('x')
            generator.force_new_dynamic_value('y')
            generator.force_new_dynamic_value('scale')
            discards = (self.direction,self.orientation)
            self.direction = ((pi +self.inspect_value("orientation") + pi/2.0) % (2*pi)) - pi
            
        (a,b,c) = (generator.x,generator.y,generator.scale)   
        
       
        # compute how much time elapsed from the last reset
        t = float(topo.sim.time())-self.last_time

        ## CEBALERT: mask gets applied twice, both for the underlying
        ## generator and for this one.  (leads to redundant
        ## calculations in current lissom_oo_or usage, but will lead
        ## to problems/limitations in the future).
        
        dirr = self.inspect_value("direction")
        # JAHACKALERT: I want it to move in perpendicular orientation
        # JAB: Does it do that now, or not?  Please clarify.
        return generator(xdensity=xdensity,ydensity=ydensity,bounds=bounds,x=self.x+t*cos(self.inspect_value("orientation")+pi/2)*self.speed,y=self.y+t*sin(self.inspect_value("orientation")+pi/2)*self.speed,orientation=self.inspect_value("orientation"),index=self.inspect_value("index"))#,scale=self.inspect_value("scale"))


class Jitterer(PatternGenerator):
    """
    PatternGenerator that moves another PatternGenerator over time.
    
    To create a pattern at a new location, asks the underlying
    PatternGenerator to create a new pattern at a location translated
    by an amount based on the global time.
    """

    generator = param.ClassSelector(default=Constant(scale=0.0),
        class_=PatternGenerator,doc="""Pattern to be translated.""")
        
    jitter_magnitude = param.Number(default=0.02,bounds=(0.0,None),doc="""
        The speed with which the pattern should move,
        in sheet coordinates per simulation time unit.""")
    
    reset_period = param.Number(default=1,bounds=(0.0,None),doc="""
        When pattern position should be reset, usually to the value of a dynamic parameter.

        The pattern is reset whenever fmod(simulation_time,reset_time)==0.""")
    
    last_time = 0.0


    def __init__(self,**params):
        super(Jitterer,self).__init__(**params)
        self.orientation = params.get('orientation',self.orientation)
        self.r = UniformRandom()
        self.index = 0
        
    def __call__(self,**params):
        """Construct new pattern out of the underlying one."""
        generator = params.get('generator', self.generator)
        xdensity=params.get('xdensity',self.xdensity)
        ydensity=params.get('ydensity',self.ydensity)
        bounds = params.get('bounds',self.bounds)

        if((float(topo.sim.time()) >= self.last_time + self.reset_period) or (float(topo.sim.time()) <=0.05)):
            if ((float(topo.sim.time()) <= (self.last_time+self.reset_period+1.0)) and (float(topo.sim.time()) >=0.05))    :
                return Null()(xdensity=xdensity,ydensity=ydensity,bounds=bounds)
        
            self.last_time += self.reset_period
            # time to reset the parameter
            (self.x, self.y, self.scale) = (generator.x,generator.y,generator.scale)
            if isinstance(generator,Selector):
                self.index = generator.index
            generator.force_new_dynamic_value('x')
            generator.force_new_dynamic_value('y')
            generator.force_new_dynamic_value('scale')
            discards = self.orientation
            
        (a,b,c) = (generator.x,generator.y,generator.scale)   
        return generator(xdensity=xdensity,ydensity=ydensity,bounds=bounds,x=self.x+self.jitter_magnitude*self.r(),y=self.y+self.jitter_magnitude*self.r(),orientation=self.inspect_value("orientation"),index=self.inspect_value("index"))


class SequenceSelector(PatternGenerator):
    """
    PatternGenerator that selects from a list of other PatternGenerators in a sequential order.
    """

    generators = param.List(default=[Constant()],precedence=0.97,
                               class_=PatternGenerator,bounds=(1,None),
        doc="List of patterns from which to select.")

    size  = param.Number(default=1.0,doc="Scaling factor applied to all sub-patterns.")


    def __init__(self,generators,**params):
        super(SequenceSelector,self).__init__(**params)
        self.generators = generators
        self.index = 0 

    def function(self,params):
        """Selects and returns one of the patterns in the list."""
        bounds = params['bounds']
        xdensity=params['xdensity']
        ydensity=params['ydensity']
        x=params['x']
        y=params['y']
        scale=params['scale']
        offset=params['offset']
        size=params['size']
        orientation=params['orientation']
        index=params['index']
        
        if self.index == len(self.generators):
           self.index = 0 
        
        pg = self.generators[self.index]
        self.index = self.index + 1
        
        
        
        image_array = pg(xdensity=xdensity,ydensity=ydensity,bounds=bounds,
                         x=x+size*(pg.x*cos(orientation)-pg.y*sin(orientation)),
                         y=y+size*(pg.x*sin(orientation)+pg.y*cos(orientation)),
                         orientation=pg.orientation+orientation,size=pg.size*size,
                         scale=pg.scale*scale,offset=pg.offset+offset)
                       
        return image_array
    
def measure_ot(lat_exc,lat_inh,e,t):
    import topo
    topo.sim["V1"].in_connections[2].strength=lat_exc
    topo.sim["V1"].in_connections[3].strength=lat_inh
    
    topo.sim["V1"].output_fn.output_fns[1].t = t
    topo.sim["V1"].output_fn.output_fns[1].e = e
    
    
    import topo.command.analysis
    import topo.command.pylabplots
    
    filename = "Exc=" + str(lat_exc) + "_Inh=" + str(lat_inh) + "_E=" + str(e) +  "_T="+ str(t) 
     
    topo.commands.analysis.measure_or_tuning_fullfield(display=True,num_phase=4,num_orientation=80,frequencies=[2.4],
                               curve_parameters=[{"contrast":1},{"contrast":5},{"contrast":10},{"contrast":50},{"contrast":90}])
    
    topo.commands.pylabplots.cyclic_tuning_curve(suffix="GC_with_LGNGC_HR",filename=filename,sheet=topo.sim["V1"],coords=[(0,0)],x_axis="orientation")
    
    

def plot_linearized_rfs(sheet_name="V1Simple", lgn_on_projection_name="LGNOnAfferent",lgn_off_projection_name="LGNOffAfferent"):
    
    (V1x,V1y) = shape(topo.sim[sheet_name])

    lgn_on = topo.sim[sheet_name].projections[lgn_on_projection_name]
    lgn_off = topo.sim[sheet_name].projections[lgn_off_projection_name]
    
    for x in xrange(0,V1x):
        for y in xrange(0,V1y):
            RF = numpy.zeros(shape(topo.sim["Retina"].activity))
            on_cfs = lgn_on.cfs[x][y]
            off_cfs = lgn_on.cfs[x][y]
            (lgnx,lgny) = shape(numpy.zeros(shape(cfs)))                 
            for lx in xrange(0,lgnx):
                    for ly in xrange(0,lgny):                            
                           RF +=  on_cfs.weights[lx,ly] * topo.sim["LGNOn"].projections["Afferent"].cfs[0,0].weights 
    
#class CascadeHomeostatic(OutputFnWithState):
#    """
#    """
#
#    a_init = param.Number(default=13,doc="Multiplicative parameter controlling the exponential.")
#    
#    b_init = param.Number(default=-4,doc="Additive parameter controlling the exponential.")
#    
#    b_eta = param.Number(default=0.02,doc="Learning rate for homeostatic plasticity.")
#    
#    a_eta = param.Number(default=0.002,doc="Learning rate for homeostatic plasticity.")
#    
#    mu = param.Number(default=0.01,doc="Target average firing rate.")
#    
#    b_smoothing = param.Number(default=0.997, doc="""
#        Weighting of previous activity vs. current activity when calculating the average.""")
#    
#    a_smoothing = param.Number(default=0.9997, doc="""
#        Weighting of previous activity vs. current activity when calculating the average.""")
#        
#    num_cascades = param.Number(default=9,doc="Target average firing rate.")
#    thresholds = [0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9]
#
#    step = param.Number(default=1, doc="""
#        How often to update the a and b parameters.
#    For instance, step=1 means to update it every time this OF is
#        called; step=2 means to update it every other time.""")
#    
#
#    def __init__(self,**params):
#        super(CascadeHomeostatic,self).__init__(**params)
#    self.first_call = True
#    self.n_step=0
#      
#
#    def __call__(self,x):
#        if self.first_call:
#            self.first_call = False
#            self.a = ones(x.shape, x.dtype.char) * self.a_init
#            self.b = ones(x.shape, x.dtype.char) * self.b_init
#            self.y_avg = zeros(x.shape, x.dtype.char) 
#        self.y_counts = []
#        self.targets = []
#        for i in xrange(self.num_cascades):
#            self.y_counts.append(zeros(x.shape, x.dtype.char))
#            self.targets.append(exp(-self.thresholds[i]/self.mu))
#        print self.targets
#    
#        # Apply sigmoid function to x, resulting in what Triesch calls y
#        x_orig = copy.copy(x)
#                   
#        x *= 0.0
#        x += 1.0 / (1.0 + exp(-(self.a*x_orig + self.b)))
#            
#    
#        self.n_step += 1
#        if self.n_step == self.step:
#            self.n_step = 0
#            if self.plastic:                
#                self.y_avg = (1.0-self.b_smoothing)*x + self.b_smoothing*self.y_avg #Calculate average for use in debugging only
#                self.b -= self.b_eta * (self.y_avg - self.mu)
#                    
#                for i in xrange(self.num_cascades):
#                     self.y_counts[i] = (1.0-self.a_smoothing)*((x >= self.thresholds[i])*1.0) + self.a_smoothing*self.y_counts[i]
#                     self.a -= self.a_eta *   ((self.y_counts[i] >= self.targets[i])*2.0-1.0)
#                        
#                self.y_count=self.y_counts[2] 

