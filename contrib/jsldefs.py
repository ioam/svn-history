"""
File containing definitions used by jude law.
"""
import topo
import matplotlib
import os, topo, __main__
import pylab
import numpy
from numpy import exp,zeros,ones,concatenate,median, abs,array,where, ravel
from pylab import save

from topo import param

from math import pi
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
from math import pi
from numpy.fft.fftpack import fft2
from numpy.fft.helper import fftshift
from numpy import abs
import numpy.oldnumeric as Numeric
from topo.misc.filepath import normalize_path
from topo.command.pylabplots import plot_tracked_attributes
from topo.base.cf import CFPOutputFn
from topo import param
from topo.base.functionfamily import TransferFn, IdentityTF
from topo.transferfn.basic import IdentityTF 
import string
import time
import re
from topo.misc import filepath

def coords(projection_name, sheet):
    proj = topo.sim[sheet].projections()[projection_name]
    x=[]
    y=[]
    rows,cols = proj.dest.shape
    for r in range(rows):
        for c in range(cols):
            x.append(proj._cfs[r][c].x)
            y.append(proj._cfs[r][c].y)
    data=zip(x,y)
    save(normalize_path("coords"+projection_name),data,fmt='%.6f', delimiter=',')
    return x,y
def run_lesi_batch(script_file,filename,chunk,sheet,value,endtime,rfs,snapshot,output_directory="Output",
                    **params):
    """

    """
    import sys # CEBALERT: why I have to import this again? (Also done elsewhere below.)
    
   
    from topo.misc.commandline import auto_import_commands
    auto_import_commands()
    
    command_used_to_start = string.join(sys.argv)
    
    starttime=time.time()
    startnote = "Batch run started at %s." % time.strftime("%a %d %b %Y %H:%M:%S +0000",
                                                           time.gmtime())
    print startnote

    # Ensure that saved state includes all parameter values
    from topo.command.basic import save_script_repr
    param.parameterized.script_repr_suppress_defaults=False

    # Make sure pylab plots are saved to disk

    # Construct simulation name
    scriptbase= re.sub('.ty$','',os.path.basename(script_file))
    prefix = ""
    prefix += time.strftime("%Y%m%d%H%M")
    prefix += "_" + scriptbase

    simname = prefix

    # Construct parameter-value portion of filename; should do more filtering
    for a in params.keys():
        val=params[a]
        
        # Special case to give reasonable filenames for lists
        valstr= ("_".join([str(i) for i in val]) if isinstance(val,list)
                 else str(params[a]))
        prefix += "," + a + "=" + valstr


    # Set provided parameter values in main namespace
    for a in params.keys():
        __main__.__dict__[a] = params[a]


    # Create output directories
    if not os.path.isdir(normalize_path(output_directory)):
        os.mkdir(normalize_path(output_directory))

    filepath.output_path = normalize_path(os.path.join(output_directory,prefix))
    
    if os.path.isdir(filepath.output_path):
	print "Batch run: Warning -- directory: " +  \
              filepath.output_path + \
              " already exists! Run aborted; rename directory or wait one minute before trying again."
        import sys
        sys.exit(-1)
    else:
	os.mkdir(filepath.output_path)
        print "Batch run output will be in " + filepath.output_path

    ##################################
    # capture stdout
    #
    import StringIO
    stdout = StringIO.StringIO()
    sys.stdout = stdout
    ##################################


    # Run script in main
    try:
        execfile(script_file,__main__.__dict__)

        topo.sim.name=simname

        # Run each segment, doing the analysis and saving the script state each time
        data_file = open(normalize_path(filename),'a')
        lesi_analysis_function(data_file, False, False)
        cont=selectivity_test(sheet, value)
        coords("LateralExcitatory", "V1Exc")
        #save_script_repr()
        while cont==True and topo.sim.time()<endtime:
            topo.sim.run(chunk)
            lesi_analysis_function(data_file, False, False)
            cont=selectivity_test(sheet, value)
            #save_script_repr()
            elapsedtime=time.time()-starttime
            param.Parameterized(name="run_batch").message(
                "Elapsed real time %02d:%02d." % (int(elapsedtime/60),int(elapsedtime%60)))

        if rfs==True:
            print "in rfsloop"
            if snapshot:
                print "in a"
                lesi_analysis_function(data_file, True, True)
            else:
                print "in b"
                lesi_analysis_function(data_file, False,True)

        if snapshot:
            lesi_analysis_function(data_file, True, False)

        data_file.close()

    except:
        import traceback
        traceback.print_exc(file=sys.stdout)
        sys.stderr.write("Warning -- Error detected: execution halted.\n")

    
    endnote = "Batch run completed at %s." % time.strftime("%a %d %b %Y %H:%M:%S +0000",
                                                           time.gmtime())

    ##################################
    # Write stdout to output file and restore original stdout
    stdout_file = open(normalize_path(simname+".out"),'w')
    stdout_file.write(command_used_to_start+"\n")
    stdout_file.write(startnote+"\n")
    stdout_file.write(stdout.getvalue())
    stdout_file.write(endnote+"\n")
    stdout.close()
    sys.stdout = sys.__stdout__
    ##################################

    # ALERT: Need to count number of errors and warnings and put that on stdout
    # and at the end of the .out file, so that they will be sure to be noticed.
    
    print endnote
    
def run_param_batch(script_file,filename,chunk,sheet,value,endtime,output_directory="Output",
                    **params):
    """

    """
    import sys # CEBALERT: why I have to import this again? (Also done elsewhere below.)
    
   
    from topo.misc.commandline import auto_import_commands
    auto_import_commands()
    
    command_used_to_start = string.join(sys.argv)
    
    starttime=time.time()
    startnote = "Batch run started at %s." % time.strftime("%a %d %b %Y %H:%M:%S +0000",
                                                           time.gmtime())
    print startnote

    # Ensure that saved state includes all parameter values
    from topo.command.basic import save_script_repr
    param.parameterized.script_repr_suppress_defaults=False

    # Make sure pylab plots are saved to disk

    # Construct simulation name
    scriptbase= re.sub('.ty$','',os.path.basename(script_file))
    prefix = ""
    prefix += time.strftime("%Y%m%d%H%M")
    prefix += "_" + scriptbase

    simname = prefix

    # Construct parameter-value portion of filename; should do more filtering
    for a in params.keys():
        val=params[a]
        
        # Special case to give reasonable filenames for lists
        valstr= ("_".join([str(i) for i in val]) if isinstance(val,list)
                 else str(params[a]))
        prefix += "," + a + "=" + valstr


    # Set provided parameter values in main namespace
    for a in params.keys():
        __main__.__dict__[a] = params[a]


    # Create output directories
    if not os.path.isdir(normalize_path(output_directory)):
        os.mkdir(normalize_path(output_directory))

    filepath.output_path = normalize_path(os.path.join(output_directory,prefix))
    
    if os.path.isdir(filepath.output_path):
	print "Batch run: Warning -- directory: " +  \
              filepath.output_path + \
              " already exists! Run aborted; rename directory or wait one minute before trying again."
        import sys
        sys.exit(-1)
    else:
	os.mkdir(filepath.output_path)
        print "Batch run output will be in " + filepath.output_path

    ##################################
    # capture stdout
    #
    import StringIO
    stdout = StringIO.StringIO()
    sys.stdout = stdout
    ##################################


    # Run script in main
    try:
        execfile(script_file,__main__.__dict__)

        topo.sim.name=simname

        # Run each segment, doing the analysis and saving the script state each time
        data_file = open(normalize_path(filename),'a')
        param_analysis_function(data_file)
        cont=selectivity_test(sheet, value)
        coords("LateralExcitatory", "V1")
        #save_script_repr()
        while cont==True and topo.sim.time()<=endtime:
            topo.sim.run(chunk)
            param_analysis_function(data_file)
            cont=selectivity_test(sheet, value)
            #save_script_repr()
            elapsedtime=time.time()-starttime
            param.Parameterized(name="run_batch").message(
                "Elapsed real time %02d:%02d." % (int(elapsedtime/60),int(elapsedtime%60)))
        data_file.close()    
    except:
        import traceback
        traceback.print_exc(file=sys.stdout)
        sys.stderr.write("Warning -- Error detected: execution halted.\n")

    
    endnote = "Batch run completed at %s." % time.strftime("%a %d %b %Y %H:%M:%S +0000",
                                                           time.gmtime())

    ##################################
    # Write stdout to output file and restore original stdout
    stdout_file = open(normalize_path(simname+".out"),'w')
    stdout_file.write(command_used_to_start+"\n")
    stdout_file.write(startnote+"\n")
    stdout_file.write(stdout.getvalue())
    stdout_file.write(endnote+"\n")
    stdout.close()
    sys.stdout = sys.__stdout__
    ##################################

    # ALERT: Need to count number of errors and warnings and put that on stdout
    # and at the end of the .out file, so that they will be sure to be noticed.
    
    print endnote


    
#########################################################################
##Sheet types only used lissom_oo_or_homeostatic_tracked.ty for reproducing published figures##
from topo.sheet.lissom import LISSOM
from topo.base.sheet import activity_type
import copy

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

    target_lr = param.Number(default=0.045, doc="""
        Target average activity for jointly scaled projections.

        Used for calculating a learning rate scaling factor.""")
    
    smoothing = param.Number(default=0.999, doc="""
        Influence of previous activity, relative to current, for computing the average.""")

    
   
    def __init__(self,**params):
        super(JointScaling_lronly,self).__init__(**params)
        self.x_avg=None
        self.lr_sf=None
        self.__current_state_stack=[]        

    def calculate_joint_sf(self, joint_total):
        """
        Calculate current scaling factors based on the target and previous average joint activities.

        Keeps track of the scaled average for debugging. Could be
        overridden by a subclass to calculate the factors differently.
        """
      
        if self.plastic:
            self.lr_sf *=0.0
            self.lr_sf += self.target_lr/self.x_avg
            self.x_avg = (1.0-self.smoothing)*joint_total + self.smoothing*self.x_avg
            


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

        if self.x_avg is None:
            self.x_avg=self.target_lr*ones(self.shape, activity_type)
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

    def state_push(self,**args):
        super(JointScaling_lronly,self).state_push(**args)
        self.__current_state_stack.append((copy.copy(self.x_avg),copy.copy(self.lr_sf)))
        
        

    def state_pop(self,**args):
        super(JointScaling_lronly,self).state_pop(**args)
        self.x_avg, self.lr_sf=self.__current_state_stack.pop()
       
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
    target = param.Number(default=0.045, doc="""
        Target average activity for jointly scaled projections.""")

    smoothing = param.Number(default=0.999, doc="""
        Influence of previous activity, relative to current, for computing the average.""")

         
    def __init__(self,**params):
        super(JointScaling_affonly,self).__init__(**params)
        self.x_avg=None
        self.sf=None
        self.scaled_x_avg=None
        self.__current_state_stack=[] 

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



    def state_push(self,**args):
        super(JointScaling_affonly,self).state_push(**args)
        self.__current_state_stack.append((copy.copy(self.x_avg),copy.copy(self.scaled_x_avg),
                                           copy.copy(self.sf)))
        
        

    def state_pop(self,**args):
        super(JointScaling_affonly,self).state_pop(**args)
        self.x_avg,self.scaled_x_avg, self.sf =self.__current_state_stack.pop()



#############################################################################
#Functions for analysis#####################################################

class StoreMedSelectivity(param.Parameterized):
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
        save(normalize_path("MedianSelectivity"+sheet),plot_data,fmt='%.6f', delimiter=',') #uncomment if you also want to save the raw data


class StoreStability(param.Parameterized):
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
        save(normalize_path(filename+sheet+str(topo.sim.time())),plot_data,fmt='%.6f', delimiter=',') # uncomment if you want to save the raw data

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

from topo.base.arrayutil import wrap
import numpy
from numpy.oldnumeric import sqrt

def map_gradient(sheet, data_file, time, cyclic=True,cyclic_range=1.0):
    """
    Compute and show the gradient plot of the supplied data.
    Translated from Octave code originally written by Yoonsuck Choe.
    
    If the data is specified to be cyclic, negative differences will
    be wrapped into the range specified (1.0 by default).
    """
    map=topo.sim[sheet].sheet_views['OrientationPreference'].view()[0]
    selectivity=topo.sim[sheet].sheet_views['OrientationSelectivity'].view()[0]
    avg_selectivity=median(selectivity.flat)
    r,c = topo.sim[sheet].shape
    dx = numpy.diff(map,1,axis=1)[0:r-1,0:c-1]
    dy = numpy.diff(map,1,axis=0)[0:r-1,0:c-1]
    
    if cyclic: # Wrap into the specified range
        # Convert negative differences to an equivalent positive value
        dx = wrap(0,cyclic_range,dx)
        dy = wrap(0,cyclic_range,dy)
        #
        # Make it increase as gradient reaches the halfway point,
        # and decrease from there
        dx = 0.5*cyclic_range-abs(dx-0.5*cyclic_range)
        dy = 0.5*cyclic_range-abs(dy-0.5*cyclic_range)

    
    mat_gradient=sqrt(dx*dx+dy*dy)
    tot_gradient=sum(mat_gradient.flat)
    param_data = (avg_selectivity, tot_gradient)
    data_file.write(str(time)+sheet+", "+str(avg_selectivity)+",  "+str(tot_gradient)+"\n")
    #save(normalize_path(str(time)),param_data,fmt='%.6f', delimiter=',')  

# Used by homeostatic analysis function
default_analysis_plotgroups=["Activity"]
Selectivity=StoreMedSelectivity()
Stability=StoreStability()

#Avg selectivity needs to be more than value for test to be False and simulation to be stopped
def selectivity_test(sheet, value):
    selectivity=topo.sim[sheet].sheet_views['OrientationSelectivity'].view()[0]
    avg_selectivity=median(selectivity.flat)
    if avg_selectivity<=value:
        return True
    else:
        return False

def save_map(sheet):
    map=topo.sim[sheet].sheet_views['OrientationPreference'].view()[0]
    save(normalize_path("Map"+str(topo.sim.time())),map,fmt='%.6f', delimiter=',')
        

from topo.command.pylabplots import PylabPlotCommand
class two_photon_plot(PylabPlotCommand):
    def __call__(self,sheet, projection, preference, size=(10,10), cell_size=100, **params):
        p=ParamOverrides(self,params)
        pylab.hsv()
        pylab.figure(figsize=size)
        x,y = coords(projection, sheet)
        map=topo.sim[sheet].sheet_views[preference].view()[0]
        data=ravel(map)
        pylab.scatter(x,y,s=cell_size,c=data,marker='o')
        pylab.savefig(normalize_path(preference+sheet+str(topo.sim.time())+".png"), dpi=100)
        p.title=preference
        self._generate_figure(p)
        

def param_analysis_function(data_file):
    """

    Analysis function specific to this simulation which can be used in
    batch mode to plots and/or store tracked attributes during
    development.

    """
    import topo
    import copy
    from topo.command.analysis import save_plotgroup, PatternPresenter, update_activity
    from topo.base.projection import ProjectionSheet
    from topo.sheet.generator import GeneratorSheet
    from topo.pattern.basic import Gaussian, SineGrating
    from topo.command.basic import pattern_present, wipe_out_activity
    from topo.base.simulation import EPConnectionEvent

    # Save all plotgroups listed in default_analysis_plotgroups
    for pg in default_analysis_plotgroups:
        save_plotgroup(pg)

    # Plot all projections for all measured_sheets
    measured_sheets = [s for s in topo.sim.objects(ProjectionSheet).values()
                       if hasattr(s,'measure_maps') and s.measure_maps]
    for s in measured_sheets:
        for p in s.projections().values():
            save_plotgroup("Projection",projection=p)


    #uncomment if want to ignore output function in selectivity measurement
    #present a pattern without plasticity to ensure that values are initialized at t=0
    pattern_present(inputs={"Retina":SineGrating()},duration=1.0,
                    plastic=False,apply_output_fn=True,overwrite_previous=False)  

    topo.sim["V1"].state_push()
    topo.sim["V1"].output_fn.state_push()
     

    if topo.sim["V1"].sf==None:
        pass
    else:
        topo.sim["V1"].sf *=0.0
        topo.sim["V1"].sf +=1.0
            
    topo.sim["V1"].output_fn.output_fns[1].a *=0.0
    topo.sim["V1"].output_fn.output_fns[1].b *=0.0
    topo.sim["V1"].output_fn.output_fns[1].a +=12.0
    topo.sim["V1"].output_fn.output_fns[1].b +=-5.0

    
    save_plotgroup("Orientation Preference")
    #save_plotgroup("Retinotopy")
    #Save raw retinotopy data for analysis
    #retinotopy=topo.sim["V1"].sheet_views['RetinotopyPreference'].view()[0]
    #save(normalize_path("retinotopy"+str(topo.sim.time())),retinotopy,fmt='%.6f', delimiter=',')
    #save_plotgroup("Bar X Preference")
    #save_plotgroup("Bar Y Preference") 
    #Xpref=topo.sim["V1"].sheet_views['XPreference'].view()[0]
    #save(normalize_path("Xpref"+str(topo.sim.time())),Xpref,fmt='%.6f', delimiter=',')
    #Ypref=topo.sim["V1"].sheet_views['YPreference'].view()[0]
    #save(normalize_path("Ypref"+str(topo.sim.time())),Ypref,fmt='%.6f', delimiter=',')
    #save_plotgroup("Retinotopy_XY")
    #RetXpref=topo.sim["V1"].sheet_views['RetxPreference'].view()[0]
    #save(normalize_path("RetXpref"+str(topo.sim.time())),Xpref,fmt='%.6f', delimiter=',')
    #RetYpref=topo.sim["V1"].sheet_views['RetyPreference'].view()[0]
    #save(normalize_path("RetYpref"+str(topo.sim.time())),Ypref,fmt='%.6f', delimiter=',')

    #Restore original values
    topo.sim["V1"].state_pop()
    topo.sim["V1"].output_fn.state_pop()

    map_gradient("V1", data_file, topo.sim.time())
    Selectivity("V1", "Selectivity", 0, topo.sim.time())
    Stability("V1", "Stability", 0, topo.sim.time())
    save_map("V1")

    #two_photon_plot("V1", "RetxPreference", "LateralExcitatory" size=(5,5), cell_size=10)
    #two_photon_plot("V1","RetyPreference","LateralExcitatory" size=(5,5), cell_size=10)
    #two_photon_plot("V1","OrientationPreference","LateralExcitatory" size=(5,5), cell_size=10)   
   

    plot_tracked_attributes(topo.sim["V1"].output_fn.output_fns[0], filename="Afferent", ylabel="Afferent", raw=True)
    plot_tracked_attributes(topo.sim["V1"].output_fn.output_fns[2], filename="V1", ylabel="V1", raw=True)
    

    plot_tracked_attributes(topo.sim["V1"].projections()["LGNOnAfferent"].output_fn.output_fns[1], filename="On_before", ylabel="On_before")
    plot_tracked_attributes(topo.sim["V1"].projections()["LGNOffAfferent"].output_fn.output_fns[1], filename="Off_before", ylabel="Off_before")


    plot_tracked_attributes(topo.sim["V1"].projections()["LateralExcitatory"].output_fn.output_fns[1], filename="LatExBefore", ylabel="LatExBefore")
    plot_tracked_attributes(topo.sim["V1"].projections()["LateralInhibitory"].output_fn.output_fns[1], filename="LatInBefore", ylabel="LatInBefore")

    #save_snapshot()
    #save_plotgroup("RF Projection")

def homeostatic_analysis_function():
    """

    Analysis function specific to this simulation which can be used in
    batch mode to plots and/or store tracked attributes during
    development.

    """
    import topo
    import copy
    from topo.command.analysis import save_plotgroup, PatternPresenter, update_activity
    from topo.base.projection import ProjectionSheet
    from topo.sheet.generator import GeneratorSheet
    from topo.pattern.basic import Gaussian, SineGrating
    from topo.command.basic import pattern_present, wipe_out_activity
    from topo.base.simulation import EPConnectionEvent

    # Save all plotgroups listed in default_analysis_plotgroups
    for pg in default_analysis_plotgroups:
        save_plotgroup(pg)

    # Plot all projections for all measured_sheets
    measured_sheets = [s for s in topo.sim.objects(ProjectionSheet).values()
                       if hasattr(s,'measure_maps') and s.measure_maps]
    for s in measured_sheets:
        for p in s.projections().values():
            save_plotgroup("Projection",projection=p)

    #present a pattern without plasticity to ensure that values are initialized at t=0
    pattern_present(inputs={"Retina":SineGrating()},duration=1.0,
                    plastic=False,apply_output_fn=True,overwrite_previous=False)        

   

    #topo.sim["V1"].state_push()
    #topo.sim["V1"].output_fn.state_push()
     

    #if __main__.__dict__['scaling'] == True:
    #    if topo.sim["V1"].sf==None:
    #        pass
    #    else:
    #        topo.sim["V1"].sf *=0.0
    #        topo.sim["V1"].sf +=1.0
            
    #if __main__.__dict__['tracking'] == True:
    #    topo.sim["V1"].output_fn.output_fns[1].a *=0.0
    ##   topo.sim["V1"].output_fn.output_fns[1].b *=0.0
    #    topo.sim["V1"].output_fn.output_fns[1].a +=12.0
    #    topo.sim["V1"].output_fn.output_fns[1].b +=-5.0

    #else:
    #    topo.sim["V1"].output_fn.a *=0.0
    #    topo.sim["V1"].output_fn.b *=0.0
    #    topo.sim["V1"].output_fn.a +=12.0
    #    topo.sim["V1"].output_fn.b +=-5.0
        

    #if __main__.__dict__['changestrength']==True:
    #    topo.sim["LGNOn"].projections()["Afferent"].strength=2.33
    #    topo.sim["LGNOff"].projections()["Afferent"].strength=2.33
            

    save_plotgroup("Orientation Preference")

    

    #Restore original values
    #topo.sim["V1"].state_pop()
    #topo.sim["V1"].output_fn.state_pop()

    #if __main__.__dict__['changestrength']==True:
    #    topo.sim["LGNOn"].projections()["Afferent"].strength=__main__.__dict__['new_strength']
    #    topo.sim["LGNOff"].projections()["Afferent"].strength=__main__.__dict__['new_strength']

    
    
     
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
                plot_tracked_attributes(topo.sim["V1"].output_fn.output_fns[0], filename="Afferent", ylabel="Afferent", raw=True)
                plot_tracked_attributes(topo.sim["V1"].output_fn.output_fns[2], filename="V1", ylabel="V1", raw=True)
            else:
                if __main__.__dict__['lr_scaling']==True:
                    plot_tracked_attributes(topo.sim["V1"].output_fn.output_fns[0], filename="Afferent", ylabel="Afferent")
                    plot_tracked_attributes(topo.sim["V1"].output_fn.output_fns[2], filename="V1", ylabel="V1")
                    
                else:
                    plot_tracked_attributes(topo.sim["V1"].output_fn.output_fns[1], filename="Afferent", ylabel="Afferent")
          
        else:
            if __main__.__dict__['scaling'] == True:
                plot_tracked_attributes(topo.sim["V1"].output_fn.output_fns[0], filename="Afferent", ylabel="Afferent", raw=True)
                plot_tracked_attributes(topo.sim["V1"].output_fn.output_fns[3], filename="V1", ylabel="V1", raw=True)
            else:
                plot_tracked_attributes(topo.sim["V1"].output_fn.output_fns[2], filename="V1", ylabel="V1", raw=True)
                
            

        plot_tracked_attributes(topo.sim["V1"].projections()["LateralExcitatory"].output_fn.output_fns[1], filename="LatExBefore", ylabel="LatExBefore")
        plot_tracked_attributes(topo.sim["V1"].projections()["LateralInhibitory"].output_fn.output_fns[1], filename="LatInBefore", ylabel="LatInBefore")

        
SelectivityExc=StoreMedSelectivity()
StabilityExc=StoreStability()
SelectivityInh=StoreMedSelectivity()
StabilityInh=StoreStability()

def lesi_analysis_function(data_file, snapshot, rfs):
    """

    Analysis function specific to this simulation which can be used in
    batch mode to plots and/or store tracked attributes during
    development.

    """
    import topo
    import copy
    from topo.command.analysis import save_plotgroup,update_activity #ultragrid!!!
    from topo.analysis.featureresponses import PatternPresenter
    from topo.base.projection import ProjectionSheet
    from topo.sheet.generator import GeneratorSheet
    from topo.pattern.basic import Gaussian, SineGrating
    from topo.command.basic import pattern_present, wipe_out_activity, save_snapshot
    from topo.base.simulation import EPConnectionEvent


    # Build a list of all sheets worth measuring
    f = lambda x: hasattr(x,'measure_maps') and x.measure_maps
    measured_sheets = filter(f,topo.sim.objects(ProjectionSheet).values())
    input_sheets = topo.sim.objects(GeneratorSheet).values()
    
    # Set potentially reasonable defaults; not necessarily useful
    topo.command.analysis.coordinate=(0.0,0.0)
    if input_sheets:    topo.command.analysis.input_sheet_name=input_sheets[0].name
    if measured_sheets: topo.command.analysis.sheet_name=measured_sheets[0].name

    # Save all plotgroups listed in default_analysis_plotgroups
    for pg in default_analysis_plotgroups:
        save_plotgroup(pg)

    # Plot all projections for all measured_sheets
    for s in measured_sheets:
        for p in s.projections().values():
            save_plotgroup("Projection",projection=p)

    #present a pattern without plasticity to ensure that values are initialized at t=0
    pattern_present(inputs={"Retina":SineGrating()},duration=1.0,
                    plastic=False,apply_output_fn=True,overwrite_previous=False)        

    #topo.sim["V1Exc"].state_push()
    #topo.sim["V1Exc"].output_fn.state_push()
     

    #topo.sim["V1Exc"].sf *=0.0
    #topo.sim["V1Exc"].sf +=1.0
            
    #topo.sim["V1Exc"].output_fn.output_fns[1].a *=0.0
    #topo.sim["V1Exc"].output_fn.output_fns[1].b *=0.0
    #topo.sim["V1Exc"].output_fn.output_fns[1].a +=12.0
    #topo.sim["V1Exc"].output_fn.output_fns[1].b +=-5.0

    save_plotgroup("Orientation Preference")

    map_gradient("V1Exc", data_file, topo.sim.time())
    SelectivityExc("V1Exc", "SelectivityExc", 0, topo.sim.time())
    StabilityExc("V1Exc", "StabilityExc", 0, topo.sim.time())
    save_map("V1Exc")

    map_gradient("V1Inh", data_file, topo.sim.time())
    SelectivityInh("V1Inh", "SelectivityInh", 0, topo.sim.time())
    StabilityInh("V1Inh", "StabilityInh", 0, topo.sim.time())
    save_map("V1Inh")

    topo.command.analysis.sheet_name="V1Exc"
    
    plot_tracked_attributes(topo.sim["V1Exc"].output_fn.output_fns[0], 0, 
                            topo.sim.time(),filename="V1Exc", ylabel="V1Exc", raw=True)
    plot_tracked_attributes(topo.sim["V1Exc"].output_fn.output_fns[2], 0, 
                            topo.sim.time(),filename="V1Exc_of", ylabel="V1Exc_of", raw=True)

    if __main__.__dict__['homeo_inh'] == True:
        plot_tracked_attributes(topo.sim["V1Inh"].output_fn.output_fns[1], 0, 
                                topo.sim.time(), filename="V1Inh", ylabel="V1Inh", raw=True)
    else:
        plot_tracked_attributes(topo.sim["V1Inh"].output_fn.output_fns[2], 0, 
                                topo.sim.time(), filename="V1Inh", ylabel="V1Inh", raw=True)

    plot_tracked_attributes(topo.sim["V1Exc"].projections()["LGNOnAfferent"].output_fn.output_fns[1], 0,
                            topo.sim.time(), filename="LGNOnAfferent", ylabel="LGNOnAfferent", raw=True)
    plot_tracked_attributes(topo.sim["V1Exc"].projections()["LGNOffAfferent"].output_fn.output_fns[1], 0,
                            topo.sim.time(), filename="LGNOffAfferent", ylabel="LGNOffAfferent", raw=True)

    plot_tracked_attributes(topo.sim["V1Exc"].projections()["LateralExcitatory_local"].output_fn.output_fns[1], 0,
                            topo.sim.time(), filename="LateralExcitatory_local", ylabel="LateralExcitatory_local", raw=True)
    plot_tracked_attributes(topo.sim["V1Exc"].projections()["LateralExcitatory"].output_fn.output_fns[1], 0,
                            topo.sim.time(), filename="LateralExcitatory", ylabel="LateralExcitatory", raw=True)
    plot_tracked_attributes(topo.sim["V1Exc"].projections()["V1Inh_to_V1Exc"].output_fn.output_fns[1], 0,
                            topo.sim.time(), filename="V1Inh_to_V1Exc", ylabel="V1Inh_to_V1Exc", raw=True)

    plot_tracked_attributes(topo.sim["V1Inh"].projections()["V1Inh_to_V1Inh"].output_fn.output_fns[1], 0,
                            topo.sim.time(), filename="V1Inh_to_V1Inh", ylabel="V1Inh_to_V1Inh", raw=True)
    plot_tracked_attributes(topo.sim["V1Inh"].projections()["V1Exc_to_V1Inh_local"].output_fn.output_fns[1], 0,
                            topo.sim.time(), filename="V1Exc_to_V1Inh_local", ylabel="V1Exc_to_V1Inh_local", raw=True)
    plot_tracked_attributes(topo.sim["V1Inh"].projections()["V1Exc_to_V1Inh"].output_fn.output_fns[1], 0,
                            topo.sim.time(), filename="V1Exc_to_V1Inh", ylabel="V1Exc_to_V1Inh", raw=True)
    if snapshot:
        save_snapshot()
        
    topo.command.analysis.input_sheet=topo.sim["Retina"]
    if rfs:
        print "measuring rfs"
        topo.plotting.plotgroup.RFProjectionPlotGroup.input_sheet=topo.sim["Retina"]
        topo.plotting.plotgroup.RFProjectionPlotGroup.sheet=topo.sim["V1Exc"]
        #Retina_pix=topo.sim["Retina"].shape[0]
        #V1Exc_pix=topo.sim["V1Exc"].shape[0]
        
        save_plotgroup("RF Projection", input_sheet=topo.sim["Retina"], sheet=topo.sim["V1Exc"])
        #ultragrid_zoom_3(0,0,0,Retina_pix,0,Retina_pix,V1Exc_pix,9999999999,normalize_path("RFS_Exc"+str(topo.sim.time())))
        
        #topo.plotting.plotgroup.RFProjectionPlotGroup.input_sheet=topo.sim["Retina"]
        #topo.plotting.plotgroup.RFProjectionPlotGroup.sheet=topo.sim["V1Inh"]
        #Retina_pix=topo.sim["Retina"].shape[0]
        #V1Inh_pix=topo.sim["V1Inh"].shape[0]
        
        #save_plotgroup("RF Projection", input_sheet=topo.sim["Retina"], sheet=topo.sim["V1Inh"])
        #ultragrid_zoom_3(0,0,0,Retina_pix,0,Retina_pix,V1Inh_pix,9999999999,normalize_path("RFS_Inh"+str(topo.sim.time())))

    #Restore original values
    topo.sim["V1Exc"].state_pop()
    topo.sim["V1Exc"].output_fn.state_pop()

    if snapshot:
        save_snapshot()
    
def species_analysis_function():
    """

    Analysis function specific to this simulation which can be used in
    batch mode to plots and/or store tracked attributes during
    development.

    """

    import topo
    import copy
    from topo.command.analysis import save_plotgroup, PatternPresenter, update_activity
    from topo.base.projection import ProjectionSheet
    from topo.sheet.generator import GeneratorSheet
    from topo.pattern.basic import Gaussian, SineGrating
    from topo.command.basic import pattern_present, wipe_out_activity, save_snapshot
    from topo.base.simulation import EPConnectionEvent

    #Save all plotgroups listed in default_analysis_plotgroups
    for pg in default_analysis_plotgroups:
        save_plotgroup(pg)

    #Plot all projections for all measured_sheets
    measured_sheets = [s for s in topo.sim.objects(ProjectionSheet).values()
                       if hasattr(s,'measure_maps') and s.measure_maps]
    for s in measured_sheets:
        for p in s.projections().values():
            save_plotgroup("Projection",projection=p)
            
    #present a pattern without plasticity to ensure that values are initialized at t=0
    pattern_present(inputs={"Retina":SineGrating()},duration=1.0,
                    plastic=False,apply_output_fn=True,overwrite_previous=False)        

   

    topo.sim["V1"].state_push()
    topo.sim["V1"].output_fn.state_push()
     
    topo.sim["V1"].projections()["LGNOnAfferent"].strength=1.0
    topo.sim["V1"].projections()["LGNOffAfferent"].strength=1.0
    topo.sim["V1"].output_fn.output_fns[0].a *=0.0
    topo.sim["V1"].output_fn.output_fns[0].b *=0.0
    topo.sim["V1"].output_fn.output_fns[0].a +=12.0
    topo.sim["V1"].output_fn.output_fns[0].b +=-5.0
    
    save_plotgroup("Orientation Preference")

    save_plotgroup("Retinotopy")

    #Save raw retinotopy data for analysis
    retinotopy=topo.sim["V1"].sheet_views['RetinotopyPreference'].view()[0]
    save(normalize_path("retinotopy"+str(topo.sim.time())),retinotopy, fmt='%.6f', delimiter=',')

    #Restore original values
    topo.sim["V1"].state_pop()
    topo.sim["V1"].output_fn.state_pop()

    topo.sim["V1"].projections()["LGNOnAfferent"].strength=__main__.__dict__['aff_strength']
    topo.sim["V1"].projections()["LGNOffAfferent"].strength=__main__.__dict__['aff_strength']

    Selectivity("V1", "Selectivity", 0, topo.sim.time())
    Stability("V1", "Stability", 0, topo.sim.time())
   
    plot_tracked_attributes(topo.sim["V1"].output_fn.output_fns[1], filename="V1", ylabel="V1", raw=True)
    

    #plot_tracked_attributes(topo.sim["V1"].projections()["LGNOnAfferent"].output_fn.output_fns[1], filename="On_before", ylabel="On_before")
    #plot_tracked_attributes(topo.sim["V1"].projections()["LGNOffAfferent"].output_fn.output_fns[1], filename="Off_before", ylabel="Off_before")


    plot_tracked_attributes(topo.sim["V1"].projections()["LateralExcitatory"].output_fn.output_fns[1], filename="LatExBefore", ylabel="LatExBefore")
    plot_tracked_attributes(topo.sim["V1"].projections()["LateralInhibitory"].output_fn.output_fns[1], filename="LatInBefore", ylabel="LatInBefore")

    #save_snapshot()

def rfs_analysis_function(sheet="V1", sheets_to_measure=["V1"]):
    """

    Analysis function specific to this simulation which can be used in
    batch mode to plots and/or store tracked attributes during
    development.

    """
    
    import topo
    import copy
    from topo.command.analysis import save_plotgroup, PatternPresenter, update_activity, ultragrid_zoom_3
    from topo.base.projection import ProjectionSheet
    from topo.sheet.generator import GeneratorSheet
    from topo.pattern.basic import Gaussian, SineGrating
    from topo.command.basic import pattern_present, wipe_out_activity, save_snapshot
    from topo.base.simulation import EPConnectionEvent

    #topo.plotting.plotgroup.plotgroups["RF Projection"].pre_plot_hooks="measure_rfs(scale=10.0,display=False,use_full=True,l=-1.0,b=-1.0,r=1.0,t=1.0)"
    #present a pattern without plasticity to ensure that values are initialized at t=0
    pattern_present(inputs={"Retina":SineGrating()},duration=1.0,
                    plastic=False,apply_output_fn=True,overwrite_previous=False)
    
    Retina_pix=topo.sim["Retina"].shape[0]

    V1_pix=topo.sim[sheet].shape[0]
    topo.sim[sheet].state_push()
    topo.sim[sheet].output_fn.state_push()
    
    topo.sim[sheet].projections()["LGNOnAfferent"].strength=1.0
    topo.sim[sheet].projections()["LGNOffAfferent"].strength=1.0
    topo.sim[sheet].output_fn.output_fns[0].a *=0.0
    topo.sim[sheet].output_fn.output_fns[0].b *=0.0
    topo.sim[sheet].output_fn.output_fns[0].a +=12.0
    topo.sim[sheet].output_fn.output_fns[0].b +=-5.0

    for each in sheets_to_measure:
        save_plotgroup("RF Projection", input_sheet=topo.sim["Retina"], sheet=topo.sim[each])
        ultragrid_zoom_3(0,0,0,Retina_pix,0,Retina_pix,V1_pix,9999999999,normalize_path("RFS"+each+str(topo.sim.time())))

    #Restore original values
    topo.sim[sheet].state_pop()
    topo.sim[sheet].output_fn.state_pop()
       
def plot_out_connections(cfprojection_name, units):
    """
    """
    from topo.command.pylabplots import matrixplot

    from topo.base.cf import MaskedCFIter
    proj=topo.sim["V1"].projections()[cfprojection_name]

    iterator=MaskedCFIter(proj)
    
    row, col = proj.src.shape
    
    
    lgn_cf={}
    for x in range(row):
        lgn_cf[x]={}
        for y in range(col):
            lgn_cf[x][y]={}
            lgn_cf[x][y]=zeros(proj.dest.shape) #for every cell in LGN there is an array the size of V1
            
    for x in range(row): #for every cell in lgn
        for y in range(col):
            for cf,v1x,v1y in iterator(): # for every cf in V1
                #if (mask[v1x][v1y] != 0):
                r1,r2,c1,c2= cf.input_sheet_slice # cells of lgn in that cf
                rx=range(r1, r2)
                ry=range(c1, c2)
                if x in rx: # if the lgn cell is in that cf
                    if y in ry:
                        indx = rx.index(x) #make note of the index of that cell in the cf
                        indy = ry.index(y)
                        
                        lgn_cf[x][y][v1x][v1y] += cf.weights[indx][indy] # fill in the array of v1 at that position with the weight of the cell
                            

    for unit in units: 
        matrixplot(lgn_cf[unit[0]][unit[1]])
