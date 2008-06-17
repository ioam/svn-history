"""
File containing definitions used by jude law.
"""

import matplotlib
import os, topo, __main__
import pylab
import numpy
from numpy import exp,zeros,ones,concatenate,median
from pylab import save
from topo.base.parameterizedobject import ParameterizedObject
from math import pi
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
from math import pi
from numpy.fft.fftpack import fft2
from numpy.fft.helper import fftshift
from numpy import abs
import numpy.oldnumeric as Numeric
from topo.misc.filepaths import normalize_path
from topo.commands.pylabplots import plot_tracked_attributes

#########################################################################
##Sheet types only used lissom_oo_or_homeostatic_tracked.ty for reproducing published figures##
from topo.sheets.lissom import LISSOM
from topo.base.parameterclasses import Number
from topo.base.sheet import activity_type

class JointScaling_lronly(LISSOM):
    """

    LISSOM sheet extended to allow auto-scaling of Afferent
    projection learning rate.
    
    An exponentially weighted average is used to calculate the average
    joint activity across all jointly-normalized afferent projections.
    This average is then used to calculate a scaling factor for the
    afferent learning rate.

    The target activity for learning rate scaling is set based on
    original values from the lissom_oo_or.ty simulation using two
    Gaussians per iteration as the input dataset.  """

    target_lr = Number(default=0.045, doc="""
        Target average activity for jointly scaled projections.

        Used for calculating a learning rate scaling factor.""")
    
    smoothing = Number(default=0.999, doc="""
        Influence of previous activity, relative to current, for computing the average.""")

    
   
    def __init__(self,**params):
        super(JointScaling_lronly,self).__init__(**params)
        self.lr_x_avg=None
        self.lr_sf=None
                

    def calculate_joint_sf(self, joint_total):
        """
        Calculate current scaling factors based on the target and previous average joint activities.

        Keeps track of the scaled average for debugging. Could be
        overridden by a subclass to calculate the factors differently.
        """
      
        if self.plastic:
            self.lr_sf *=0.0
            self.lr_sf += self.target_lr/self.lr_x_avg
            self.lr_x_avg = (1.0-self.smoothing)*joint_total + self.smoothing*self.lr_x_avg
            


    def do_joint_scaling(self):
        """
        Scale jointly normalized projections together.

        Assumes that the projections to be jointly scaled are those
        that are being jointly normalized.  Calculates the joint total
        of the grouped projections, and uses this to calculate the
        scaling factor.
        """
        joint_total = zeros(self.shape, activity_type)
        
        for key,projlist in self._grouped_in_projections('JointNormalize'):
            if key is not None:
                if key =='Afferent':
                    for proj in projlist:
                        joint_total += proj.activity
                    self.calculate_joint_sf(joint_total)
                    for proj in projlist:
                        if hasattr(proj.learning_fn,'learning_rate_scaling_factor'):
                            proj.learning_fn.update_scaling_factor(self.lr_sf)
                        else:
                            raise ValueError("Projections to be joint scaled must have a learning_fn that supports scaling e.g. CFPLF_PluginScaled")
                        
                else:
                    raise ValueError("Only Afferent scaling currently supported")                  


    def activate(self):
        """
        Compute appropriate scaling factors, apply them, and collect resulting activity.

        Scaling factors are first computed for each set of jointly
        normalized projections, and the resulting activity patterns
        are then scaled.  Then the activity is collected from each
        projection, combined to calculate the activity for this sheet,
        and the result is sent out.
        """
        self.activity *= 0.0

        if self.lr_x_avg is None:
            self.lr_x_avg=self.target_lr*ones(self.shape, activity_type)
        if self.lr_sf is None:
            self.lr_sf=ones(self.shape, activity_type)

        #Afferent projections are only activated once at the beginning of each iteration
        #therefore we only scale the projection activity and learning rate once.
        if self.activation_count == 0: 
            self.do_joint_scaling()   

        for proj in self.in_connections:
            self.activity += proj.activity
        
        if self.apply_output_fn:
            self.output_fn(self.activity)
           
          
        self.send_output(src_port='Activity',data=self.activity)

       
class JointScaling_affonly(LISSOM):
    """
    LISSOM sheet extended to allow joint auto-scaling of Afferent input projections.
    
    An exponentially weighted average is used to calculate the average
    joint activity across all jointly-normalized afferent projections.
    This average is then used to calculate a scaling factor for the
    current afferent activity.

    The target average activity for the afferent projections depends
    on the statistics of the input; if units are activated more often
    (e.g. the number of Gaussian patterns on the retina during each
    iteration is increased) the target average activity should be
    larger in order to maintain a constant average response to similar
    inputs in V1. 
    """
    target = Number(default=0.045, doc="""
        Target average activity for jointly scaled projections.""")

    smoothing = Number(default=0.999, doc="""
        Influence of previous activity, relative to current, for computing the average.""")

         
    def __init__(self,**params):
        super(JointScaling_affonly,self).__init__(**params)
        self.x_avg=None
        self.sf=None
        self.scaled_x_avg=None


    def calculate_joint_sf(self, joint_total):
        """
        Calculate current scaling factors based on the target and previous average joint activities.

        Keeps track of the scaled average for debugging. Could be
        overridden by a subclass to calculate the factors differently.
        """
      
        if self.plastic:
            self.sf *=0.0
            self.sf += self.target/self.x_avg
            self.x_avg = (1.0-self.smoothing)*joint_total + self.smoothing*self.x_avg
            self.scaled_x_avg = (1.0-self.smoothing)*joint_total*self.sf + self.smoothing*self.scaled_x_avg


    def do_joint_scaling(self):
        """
        Scale jointly normalized projections together.

        Assumes that the projections to be jointly scaled are those
        that are being jointly normalized.  Calculates the joint total
        of the grouped projections, and uses this to calculate the
        scaling factor.
        """
        joint_total = zeros(self.shape, activity_type)
        
        for key,projlist in self._grouped_in_projections('JointNormalize'):
            if key is not None:
                if key =='Afferent':
                    for proj in projlist:
                        joint_total += proj.activity
                    self.calculate_joint_sf(joint_total)
                    for proj in projlist:
                        proj.activity *= self.sf
                                         
                else:
                    raise ValueError("Only Afferent scaling currently supported")                  


    def activate(self):
        """
        Compute appropriate scaling factors, apply them, and collect resulting activity.

        Scaling factors are first computed for each set of jointly
        normalized projections, and the resulting activity patterns
        are then scaled.  Then the activity is collected from each
        projection, combined to calculate the activity for this sheet,
        and the result is sent out.
        """
        self.activity *= 0.0

        if self.x_avg is None:
            self.x_avg=self.target*ones(self.shape, activity_type)
        if self.scaled_x_avg is None:
            self.scaled_x_avg=self.target*ones(self.shape, activity_type) 
        if self.sf is None:
            self.sf=ones(self.shape, activity_type)

        #Afferent projections are only activated once at the beginning of each iteration
        #therefore we only scale the projection activity and learning rate once.
        if self.activation_count == 0: 
            self.do_joint_scaling()   

        for proj in self.in_connections:
            self.activity += proj.activity
        
        if self.apply_output_fn:
            self.output_fn(self.activity)
           
          
        self.send_output(src_port='Activity',data=self.activity)

#############################################################################
#Functions for analysis#####################################################

class StoreMedSelectivity(ParameterizedObject):
    """
    Plots and/or stores the average (median) selectivity across the map.
    """

    from numpy import median
    def __init__(self):
        self.select=[]

    def __call__(self, sheet, filename, init_time, final_time, **params):
        
        selectivity=topo.sim[sheet].sheet_views['OrientationSelectivity'].view()[0]
        avg=median(selectivity.flat)
        self.select.append((topo.sim.time(),avg))

        pylab.figure(figsize=(6,4))
        pylab.grid(True)
        pylab.ylabel("Average Selectivity")
        pylab.xlabel('Iteration Number')
       
        plot_y=[y for (x,y) in self.select]
        plot_x=[x for (x,y) in self.select]
        pylab.plot(plot_x, plot_y)
        plot_data= zip(plot_x, plot_y)
        #print plot_data
        (ymin,ymax)=params.get('ybounds',(None,None))
        pylab.axis(xmin=init_time,xmax=final_time, ymin=ymin, ymax=ymax)
        # The size * the dpi gives the final image size
        #   a 4"x4" image * 80 dpi ==> 320x320 pixel image
        pylab.savefig(normalize_path("MedianSelectivity"+sheet+".png"), dpi=100)
        #save(normalize_path("MedianSelectivity"+sheet),plot_data,fmt='%.6f', delimiter=',') #uncomment if you also want to save the raw data


class StoreStability(ParameterizedObject):
    """

    Plots and/or stores the orientation similarity index across the map
    during development (as defined in Chapman et. al, J. Neurosci
    16(20):6443, 1996).  Each previous stored timepoint is compared
    with the current timepoint.

    """

    
    def __init__(self):
        self.pref_dict={}

    def __call__(self, sheet, filename, init_time, final_time, **params):

        self.pref_dict[topo.sim.time()]=topo.sim[sheet].sheet_views['OrientationPreference'].view()[0]
       

        ##Comparisons
        times = sorted(self.pref_dict.keys())
        values=[]

        for time in times:
            difference = abs(self.pref_dict[topo.sim.time()]-self.pref_dict[time])
            rows,cols = difference.shape
            for r in range(rows):
                for c in range(cols):
                    if difference[r,c] >= 0.5:
                        difference[r,c] = 1-difference[r,c]

            difference *= 2.0
            avg_diff=sum(difference.flat)/len(difference.flat)
            value = 1-avg_diff
            values.append(value)
            
            
        plot_data= zip(times,values)
        #save(normalize_path(filename+str(topo.sim.time())),plot_data,fmt='%.6f', delimiter=',') # uncomment if you want to save the raw data

        pylab.figure(figsize=(6,4))
        pylab.grid(True)
        pylab.ylabel("Average Stability")
        pylab.xlabel('Iteration Number')
       
        pylab.plot(times,values)
        (ymin,ymax)=params.get('ybounds',(None,None))
        pylab.axis(xmin=init_time,xmax=final_time, ymin=ymin, ymax=ymax)
        # The size * the dpi gives the final image size
        #   a 4"x4" image * 80 dpi ==> 320x320 pixel image
        pylab.savefig(normalize_path("AverageStability"+sheet+str(topo.sim.time())+".png"), dpi=100)


# Used by homeostatic analysis function
default_analysis_plotgroups=["Activity", "Orientation Preference"]
Selectivity=StoreMedSelectivity()
Stability=StoreStability()

def homeostatic_analysis_function():
    """

    Analysis function specific to this simulation which can be used in
    batch mode to plots and/or store tracked attributes during
    development.

    """
    #JLALERT Have not yet included saving and restoring state and changing
    #output function and scaling parameters during map measurement, therefore
    #selectivity plots will not reflect true selectivity.

    import topo
    import copy
    from topo.commands.analysis import save_plotgroup, PatternPresenter, update_activity
    from topo.base.projection import ProjectionSheet
    from topo.sheets.generatorsheet import GeneratorSheet
    from topo.patterns.basic import Gaussian
    from topo.commands.basic import pattern_present, wipe_out_activity
    from topo.base.simulation import EPConnectionEvent


    # Build a list of all sheets worth measuring
    f = lambda x: hasattr(x,'measure_maps') and x.measure_maps
    measured_sheets = filter(f,topo.sim.objects(ProjectionSheet).values())
    input_sheets = topo.sim.objects(GeneratorSheet).values()
    
    # Set potentially reasonable defaults; not necessarily useful
    topo.commands.analysis.coordinate=(0.0,0.0)
    if input_sheets:    topo.commands.analysis.input_sheet_name=input_sheets[0].name
    if measured_sheets: topo.commands.analysis.sheet_name=measured_sheets[0].name

    # Save all plotgroups listed in default_analysis_plotgroups
    for pg in default_analysis_plotgroups:
        save_plotgroup(pg)

    # Plot all projections for all measured_sheets
    for s in measured_sheets:
        for p in s.projections().values():
            save_plotgroup("Projection",projection=p)

    Selectivity("V1", "Selectivity", 0, topo.sim.time())
    Stability("V1", "Stability", 0, topo.sim.time())
    #Uncomment to present and record the response to a single gaussian
    #topo.sim.run(1)
    #pattern_present(inputs={"Retina":Gaussian(aspect_ratio=4.66667, size=0.088388, x=0.0, y=0.0, scale=1.0,orientation=0.0 )},
    #                duration=1.0, plastic=False,apply_output_fn=True,overwrite_previous=False)
    #update_activity()
    #save_plotgroup("Activity")

    if __main__.__dict__['tracking'] == True:
        if __main__.__dict__['triesch'] == True: 
            if __main__.__dict__['scaling'] == True:
                plot_tracked_attributes(topo.sim["V1"].output_fn.output_fns[0], 0, 
                                        topo.sim.time(), filename="Afferent", ylabel="Afferent", raw=True)
                plot_tracked_attributes(topo.sim["V1"].output_fn.output_fns[2], 0, 
                                        topo.sim.time(), filename="V1", ylabel="V1", raw=True)
            else:
                if __main__.__dict__['lr_scaling']==True:
                    plot_tracked_attributes(topo.sim["V1"].output_fn.output_fns[0], 0, 
                                            topo.sim.time(), filename="Afferent", ylabel="Afferent", raw=False)
                    plot_tracked_attributes(topo.sim["V1"].output_fn.output_fns[2], 0, 
                                            topo.sim.time(), filename="V1", ylabel="V1", raw=False)
                    
                else:
                    plot_tracked_attributes(topo.sim["V1"].output_fn.output_fns[1], 0, 
                                            topo.sim.time(), filename="Afferent", ylabel="Afferent", raw=False)
          
        else:
            if __main__.__dict__['scaling'] == True:
                plot_tracked_attributes(topo.sim["V1"].output_fn.output_fns[0], 0, 
                                        topo.sim.time(), filename="Afferent", ylabel="Afferent", raw=True)
                plot_tracked_attributes(topo.sim["V1"].output_fn.output_fns[3], 0, 
                                        topo.sim.time(), filename="V1", ylabel="V1", raw=True)
            else:
                plot_tracked_attributes(topo.sim["V1"].output_fn.output_fns[2], 0, 
                                        topo.sim.time(), filename="V1", ylabel="V1", raw=True)
                
            

        plot_tracked_attributes(topo.sim["V1"].projections()["LateralExcitatory"].output_fn.output_fns[1], 0,
                                topo.sim.time(), filename="LatExBefore", ylabel="LatExBefore")
        plot_tracked_attributes(topo.sim["V1"].projections()["LateralInhibitory"].output_fn.output_fns[1], 0,
                                topo.sim.time(), filename="LatInBefore", ylabel="LatInBefore")