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
from topo.projection.basic import CFProjection, SharedWeightCFProjection
from topo.base.boundingregion import BoundingBox 
from topo.misc.numbergenerator import UniformRandom, BoundedNumber, ExponentialDecay
from topo.pattern.basic import Gaussian, Selector, Null
from topo.transferfn.basic import DivisiveNormalizeL1, HomeostaticMaxEnt, TransferFnWithState, Sigmoid, PiecewiseLinear
from topo.base.arrayutil import clip_lower
from topo.sheet.lissom import LISSOM
from topo.sheet.optimized import NeighborhoodMask_Opt, LISSOM_Opt
from topo.plotting.plotfilesaver import * 
from topo.command.pylabplots import cyclic_tuning_curve, matrixplot
from topo.command.analysis import save_plotgroup
from topo.misc.filepath import normalize_path, application_path
from topo.command.pylabplots import plot_tracked_attributes
from topo.base.functionfamily import CoordinateMapperFn
from topo.plotting.bitmap import MontageBitmap
from topo.base.patterngenerator import PatternGenerator, Constant 
from topo.transferfn.basic import  Sigmoid

class surround_analysis():

    peak_near_facilitation_hist = []
    peak_supression_hist  = []   
    peak_far_facilitation_hist  = []
    sheet_name = ""
    data_dict = {}
    
    low_contrast=30
    high_contrast=60
    
    def __init__(self,sheet_name="V1Complex"):
        from topo.analysis.featureresponses import MeasureResponseCommand, FeatureMaps, FeatureCurveCommand, UnitCurveCommand, SinusoidalMeasureResponseCommand
        import pylab
        self.sheet_name=sheet_name
        self.sheet=topo.sim[sheet_name]
        # Center mask to matrixidx center
        self.center_r,self.center_c = self.sheet.sheet2matrixidx(0,0)
        self.center_x,self.center_y = self.sheet.matrixidx2sheet(self.center_r,self.center_c)
        FeatureCurveCommand.curve_parameters=[{"contrast":self.low_contrast},{"contrast":self.high_contrast}]
        FeatureCurveCommand.display=True
        FeatureCurveCommand.sheet=topo.sim[sheet_name]
        SinusoidalMeasureResponseCommand.num_phase=8
        SinusoidalMeasureResponseCommand.frequencies=[2.6]
        SinusoidalMeasureResponseCommand.scale=1.0
        MeasureResponseCommand.scale=1.0
        FeatureCurveCommand.num_orientation=8


    def analyse(self,steps=1,ns=10,step_size=1):
        save_plotgroup("Orientation Preference and Complexity")
        #save_plotgroup("Position Preference")
        for x in xrange(0,steps*2+1):
            for y in xrange(0,steps*2+1):
                xindex = self.center_r+(x-steps)*step_size
                yindex = self.center_c+(y-steps)*step_size
                xcoor,ycoor = self.sheet.matrixidx2sheet(xindex,yindex)
                topo.command.pylabplots.measure_size_response.instance(sheet=self.sheet,num_sizes=ns,max_size=3.0,coords=[(xcoor,ycoor)])(coords=[(xcoor,ycoor)])        
                
                self.data_dict[(xindex,yindex)] = {}
                self.data_dict[(xindex,yindex)]["ST"] = self.calculate_RF_sizes(xindex, yindex)
                self.plot_size_tunning(xindex,yindex)
                
                self.data_dict[(xindex,yindex)]["OCT"] = self.perform_orientation_contrast_analysis(self.data_dict[(xindex,yindex)]["ST"],xcoor,ycoor,xindex,yindex)
                self.plot_orientation_contrast_tuning(xindex,yindex)
                self.plot_orientation_contrast_tuning_abs(xindex,yindex)
                
                
        
        self.plot_histograms_of_measures()
        lhi = compute_local_homogeneity_index(self.sheet.sheet_views['OrientationPreference'].view()[0]*pi,0.5)                
        self.plot_map_feature_to_surround_modulation_feature_correlations(lhi,"Local Homogeneity Index")
        self.plot_map_feature_to_surround_modulation_feature_correlations(self.sheet.sheet_views['OrientationSelectivity'].view()[0],"OrientationSelectivity")
        self.plot_map_feature_to_surround_modulation_feature_correlations(self.sheet.sheet_views['OrientationPreference'].view()[0]*numpy.pi,"OrientationPreference")

        f = open(normalize_path("dict.dat"),'wb')
        import pickle
        pickle.dump(self.data_dict,f)
        

    def perform_orientation_contrast_analysis(self,data,xcoor,ycoor,xindex,yindex):
        curve_data={}
        hc_curve = data["Contrast = " + str(self.high_contrast) + "%" ]
        lc_curve = data["Contrast = " + str(self.low_contrast) + "%" ]
        
        print "BBB",lc_curve["measures"]["peak_near_facilitation"],self.high_contrast
        topo.command.pylabplots.measure_or_tuning(size=lc_curve["measures"]["peak_near_facilitation"],curve_parameters=[{"contrast":self.high_contrast}],display=True,coords=[(xcoor,ycoor)])
        topo.command.pylabplots.cyclic_tuning_curve.instance(x_axis="orientation",coords=[(xcoor,ycoor)])
        topo.command.pylabplots.measure_orientation_contrast(sizecenter=lc_curve["measures"]["peak_near_facilitation"],
                                                             sizesurround=4.0,
                                                             size=0.0,
                                                             display=True,
                                                             contrastcenter=self.high_contrast,
                                                             thickness=4.0-lc_curve["measures"]["peak_near_facilitation"]-0.1,
                                                             num_phase=8,
                                                             curve_parameters=[{"contrastsurround":self.low_contrast},{"contrastsurround":self.high_contrast}],coords=[(xcoor,ycoor)])
        
        for curve_label in sorted(self.sheet.curve_dict['orientationsurround'].keys()):
            print curve_label
            curve_data[curve_label]={}
            curve_data[curve_label]["data"]=self.sheet.curve_dict['orientationsurround'][curve_label]
            curve_data[curve_label]["measures"]={}
            orr=numpy.pi*self.sheet.sheet_views["OrientationPreference"].view()[0][xindex][yindex]
            pref_or_resp=self.sheet.curve_dict['orientationsurround'][curve_label][orr].view()[0][xindex][yindex]
            print self.sheet.curve_dict['orientationsurround'][curve_label].keys() , "\nAAA" , str(orr+(numpy.pi/2.0))
            
            cont_or_resp=self.sheet.curve_dict['orientationsurround'][curve_label][orr+(numpy.pi/2.0)].view()[0][xindex][yindex]
            
            if pref_or_resp != 0:
                curve_data[curve_label]["measures"]["or_suppression"]=(pref_or_resp-cont_or_resp)/pref_or_resp
            else: 
                curve_data[curve_label]["measures"]["or_suppression"]=-10
        
        hc_curve_name = "Contrast = " + str(self.high_contrast) + "%";
        hc_curve_name_orc = "Contrastsurround = " + str(self.high_contrast) + "%";
        lc_curve_name_orc = "Contrastsurround = " + str(self.low_contrast) + "%";
        
        
        orr=numpy.pi*self.sheet.sheet_views["OrientationPreference"].view()[0][xindex][yindex]
        hc_pref_or_resp=self.sheet.curve_dict['orientationsurround'][hc_curve_name_orc][orr].view()[0][xindex][yindex]
        hc_cont_or_resp=self.sheet.curve_dict['orientationsurround'][hc_curve_name_orc][orr+numpy.pi/2.0].view()[0][xindex][yindex]
        lc_pref_or_resp=self.sheet.curve_dict['orientationsurround'][lc_curve_name_orc][orr].view()[0][xindex][yindex]
        lc_cont_or_resp=self.sheet.curve_dict['orientationsurround'][lc_curve_name_orc][orr+numpy.pi/2.0].view()[0][xindex][yindex]
    
        ar = []
        for o in self.sheet.curve_dict['orientation'][hc_curve_name].keys():
            ar.append(self.sheet.curve_dict['orientation'][hc_curve_name][o].view()[0][xindex][yindex])
            
        peak_or_response = max(ar)

        curve_data["ORTC"]={}
        curve_data["ORTC"]["data"]=self.sheet.curve_dict['orientation'][hc_curve_name]
        curve_data["ORTC"]["measures"]={}
        curve_data["ORTC"]["measures"]["colinear_hc_suppresion_index"] = (peak_or_response - hc_pref_or_resp) / peak_or_response 
        curve_data["ORTC"]["measures"]["colinear_lc_suppresion_index"] = (peak_or_response - lc_pref_or_resp) / peak_or_response
        curve_data["ORTC"]["measures"]["orcontrast_hc_suppresion_index"] = (peak_or_response - hc_cont_or_resp) / peak_or_response 
        curve_data["ORTC"]["measures"]["orcontrast_lc_suppresion_index"] = (peak_or_response - lc_cont_or_resp) / peak_or_response
        
        return curve_data 


    def calculate_RF_sizes(self,xindex, yindex):
        curve_data = {}
        hc_curve_name = "Contrast = " + str(self.high_contrast) + "%";
        lc_curve_name = "Contrast = " + str(self.low_contrast) + "%";
        for curve_label in [hc_curve_name,lc_curve_name]:
            curve = self.sheet.curve_dict['size'][curve_label]
            curve_data[curve_label] = {}
            curve_data[curve_label]["data"] = curve  
            
            x_values = sorted(curve.keys())
            y_values = [curve[key].view()[0][xindex, yindex] for key in x_values]

            #compute critical indexes in the size tuning curves
            curve_data[curve_label]["measures"]={}
            curve_data[curve_label]["measures"]["peak_near_facilitation_index"] = numpy.argmax(y_values)
            curve_data[curve_label]["measures"]["peak_near_facilitation"] = x_values[curve_data[curve_label]["measures"]["peak_near_facilitation_index"]]

            if(curve_data[curve_label]["measures"]["peak_near_facilitation"] < (len(y_values) - 1)):
                curve_data[curve_label]["measures"]["peak_supression_index"] = curve_data[curve_label]["measures"]["peak_near_facilitation_index"] + numpy.argmin(y_values[curve_data[curve_label]["measures"]["peak_near_facilitation_index"] + 1:]) + 1
                curve_data[curve_label]["measures"]["peak_supression"] = x_values[curve_data[curve_label]["measures"]["peak_supression_index"]]
                curve_data[curve_label]["measures"]["suppresion_index"] = (y_values[curve_data[curve_label]["measures"]["peak_near_facilitation_index"]] - y_values[curve_data[curve_label]["measures"]["peak_supression_index"]])/ y_values[curve_data[curve_label]["measures"]["peak_near_facilitation_index"]]  
                
            if(curve_data[curve_label]["measures"].has_key("peak_supression_index") and (curve_data[curve_label]["measures"]["peak_supression_index"] < (len(y_values) - 1))):
                curve_data[curve_label]["measures"]["peak_far_facilitation_index"] = curve_data[curve_label]["measures"]["peak_supression_index"] + numpy.argmax(y_values[curve_data[curve_label]["measures"]["peak_supression_index"] + 1:]) + 1
                curve_data[curve_label]["measures"]["peak_far_facilitation"] = x_values[curve_data[curve_label]["measures"]["peak_far_facilitation_index"]]
                curve_data[curve_label]["measures"]["counter_suppresion_index"] = (y_values[curve_data[curve_label]["measures"]["peak_far_facilitation_index"]] - y_values[curve_data[curve_label]["measures"]["peak_supression_index"]])/ y_values[curve_data[curve_label]["measures"]["peak_near_facilitation_index"]]
                
                
        curve_data[hc_curve_name]["measures"]["contrast_dependent_shift"]=curve_data[lc_curve_name]["measures"]["peak_near_facilitation"]/curve_data[hc_curve_name]["measures"]["peak_near_facilitation"]                 
        curve_data[lc_curve_name]["measures"]["contrast_dependent_shift"]=curve_data[lc_curve_name]["measures"]["peak_near_facilitation"]/curve_data[hc_curve_name]["measures"]["peak_near_facilitation"]
        return curve_data   
       

    def plot_size_tunning(self, xindex, yindex):
        fig = pylab.figure()
        f = fig.add_subplot(111, autoscale_on=False, xlim=(-0.1, 2.2), ylim=(-0.1, 0.7))
        pylab.title(self.sheet_name, fontsize=12)
        colors=['red','blue','green','purple','orange','black','yellow']
        
        measurment = self.data_dict[(xindex,yindex)]["ST"]
        i = 0
        for curve_label in measurment.keys():
            curve =  measurment[curve_label]["data"]
            x_values = sorted(curve.keys())
            y_values = [curve[key].view()[0][xindex, yindex] for key in x_values]
            
            f.plot(x_values, y_values, lw=3, color=colors[i])
            
                
            f.annotate('', xy=(measurment[curve_label]["measures"]["peak_near_facilitation"], y_values[measurment[curve_label]["measures"]["peak_near_facilitation_index"]]), xycoords='data',
            xytext=(-1, 20), textcoords='offset points', arrowprops=dict(facecolor='green', shrink=0.05))
    
    
            if measurment[curve_label]["measures"].has_key("peak_supression"):
                f.annotate('', xy=(measurment[curve_label]["measures"]["peak_supression"], y_values[measurment[curve_label]["measures"]["peak_supression_index"]]), xycoords='data',
                           xytext=(-1, 20), textcoords='offset points', arrowprops=dict(facecolor='red', shrink=0.05))
            
            if measurment[curve_label]["measures"].has_key("peak_far_facilitation"):
                f.annotate('', xy=(measurment[curve_label]["measures"]["peak_far_facilitation"], y_values[measurment[curve_label]["measures"]["peak_far_facilitation_index"]]), xycoords='data',
                           xytext=(-1, 20), textcoords='offset points', arrowprops=dict(facecolor='blue', shrink=0.05))
            i+=1
            
        release_fig("STC[" + str(xindex) + "," + str(yindex) + "]")


    def plot_orientation_contrast_tuning_abs(self, xindex, yindex):
        fig = pylab.figure()
        f = fig.add_subplot(111, autoscale_on=True)
        pylab.title(self.sheet_name, fontsize=12)
        colors=['red','blue','green','purple','orange','black','yellow']
        
        orientation = numpy.pi*self.sheet.sheet_views["OrientationPreference"].view()[0][xindex][yindex]
        print orientation
        measurment = self.data_dict[(xindex,yindex)]["OCT"]
        i = 0
        for curve_label in measurment.keys():
            curve =  measurment[curve_label]["data"]
            
            
            # center the values around the orientation that the neuron preffers 
            x_values = sorted(curve.keys())
            print x_values
            y_values = [curve[key].view()[0][xindex, yindex] for key in x_values]
            ### wrap the data around    
            #y_values.append(curve[key].view()[0][xindex, yindex])
            #x_values.append(x_values[0]+numpy.pi)

            f.plot(x_values, y_values, lw=3, color=colors[i])
            f.axvline(x=orientation,linewidth=4, color='r')
            i+=1
        
        release_fig("AbsOCTC[" + str(xindex) + "," + str(yindex) + "]")

    def plot_orientation_contrast_tuning(self, xindex, yindex):
        fig = pylab.figure()
        f = fig.add_subplot(111, autoscale_on=True)
        pylab.title(self.sheet_name, fontsize=12)
        colors=['red','blue','green','purple','orange','black','yellow']
        
        orientation = numpy.pi*self.sheet.sheet_views["OrientationPreference"].view()[0][xindex][yindex]
        
        measurment = self.data_dict[(xindex,yindex)]["OCT"]
        i = 0
        hc_curve_name_orc = "Contrastsurround = " + str(self.high_contrast) + "%";
        
        for curve_label in measurment.keys():
            
            print "AAA:",curve_label
            curve =  measurment[curve_label]["data"]
            x_values = sorted(curve.keys())
            y_values = []
            for k in x_values:
                y_values.append(curve[k].view()[0][xindex, yindex])
                
            
            
            x_values=x_values-orientation

            for j in xrange(0,len(x_values)):
                if x_values[j] > numpy.pi/2.0:
                   x_values[j] -= numpy.pi 
                if x_values[j] < -numpy.pi/2.0:
                   x_values[j] += numpy.pi

            for j in xrange(0,len(x_values)):
                if x_values[j] > numpy.pi/2.0:
                   x_values[j] -= numpy.pi 
                if x_values[j] < -numpy.pi/2.0:
                   x_values[j] += numpy.pi


            y_values = sorted(y_values, key=lambda x: x_values[numpy.argmax(y_values == x)])
            x_values = sorted(x_values) 
            y_values.append(y_values[0])
            x_values.append(x_values[0]+numpy.pi)
            
            f.plot(x_values, y_values, lw=3, color=colors[i])
            i+=1
        
        release_fig("OCTC[" + str(xindex) + "," + str(yindex) + "]")
        
        fig = pylab.figure()
        f = fig.add_subplot(111, autoscale_on=True)

        curve =  measurment["ORTC"]["data"]
        x_values= sorted(curve.keys())
        y_values=[curve[key].view()[0][xindex,yindex] for key in x_values]

        f.plot(x_values, y_values, lw=3)
        release_fig("OTC[" + str(xindex) + "," + str(yindex) + "]")

        

    def plot_map_feature_to_surround_modulation_feature_correlations(self,map_feature,map_feature_name):
        
        from numpy import polyfit
        
        raster_plots_lc={}
        raster_plots_hc={}
        for (xcoord,ycoord) in self.data_dict.keys():
            for curve_type in self.data_dict[(xcoord,ycoord)].keys():
                print curve_type
                if curve_type == "ST":
                   curve_label = "Contrast"
                else:
                   curve_label = "Contrastsurround" 
                
                print self.data_dict[(xcoord,ycoord)][curve_type].keys()
                
                if self.data_dict[(xcoord,ycoord)][curve_type].has_key(curve_label + " = " + str(self.low_contrast) + "%"):
                    for measure_name in self.data_dict[(xcoord,ycoord)][curve_type][curve_label + " = " + str(self.high_contrast) + "%"]["measures"].keys():
                        if not raster_plots_hc.has_key(measure_name):
                            raster_plots_hc[measure_name]=[[],[]]    
                        raster_plots_hc[measure_name][0].append(self.data_dict[(xcoord,ycoord)][curve_type][curve_label + " = " + str(self.high_contrast) + "%"]["measures"][measure_name])
                        raster_plots_hc[measure_name][1].append(map_feature[xcoord,ycoord])        
                
                if self.data_dict[(xcoord,ycoord)][curve_type].has_key(curve_label + " = " + str(self.low_contrast) + "%"):
                    for measure_name in self.data_dict[(xcoord,ycoord)][curve_type][curve_label + " = " + str(self.low_contrast) + "%"]["measures"].keys():
                        if not raster_plots_lc.has_key(measure_name):
                            raster_plots_lc[measure_name]=[[],[]]    
                        raster_plots_lc[measure_name][0].append(self.data_dict[(xcoord,ycoord)][curve_type][curve_label + " = "  + str(self.low_contrast) + "%"]["measures"][measure_name])
                        raster_plots_lc[measure_name][1].append(map_feature[xcoord,ycoord])        

        for key in raster_plots_hc.keys():
                fig = pylab.figure()
                f = fig.add_subplot(111)
                f.set_xlabel(str(key))
                f.set_ylabel(map_feature_name)
                try:
                    correlation = numpy.corrcoef(raster_plots_hc[key][0],raster_plots_hc[key][1])[0,1]
                except FloatingPointError:
                      correlation = 0
                m,b = numpy.polyfit(raster_plots_hc[key][0],raster_plots_hc[key][1],1)
                f.plot(raster_plots_hc[key][0],raster_plots_hc[key][1],'ro')
                f.plot(raster_plots_hc[key][0],m*numpy.array(raster_plots_hc[key][0])+b,'-k',linewidth=2)
                release_fig("RasterHC<" + map_feature_name + ","+ key +  " Corr:"+ str(correlation) + ">")
                

        for key in raster_plots_lc.keys():
                fig = pylab.figure()
                f = fig.add_subplot(111)
                f.set_xlabel(str(key))
                f.set_ylabel(map_feature_name)
                m,b = numpy.polyfit(raster_plots_lc[key][0],raster_plots_lc[key][1],1)
                try:
                    correlation = numpy.corrcoef(raster_plots_lc[key][0],raster_plots_lc[key][1])[0,1]
                except FloatingPointError:
                      correlation = 0
                f.plot(raster_plots_lc[key][0],raster_plots_lc[key][1],'ro')
                f.plot(raster_plots_lc[key][0],m*numpy.array(raster_plots_lc[key][0])+b,'-k',linewidth=2)
                release_fig("RasterLC<" + map_feature_name + ","+ key + " Corr:"+ str(correlation) + ">")

            
    def plot_histograms_of_measures(self):
        histograms_lc = {} 
        histograms_hc = {}
        for (xcoord,ycoord) in self.data_dict.keys():
            for curve_type in self.data_dict[(xcoord,ycoord)].keys():
                print curve_type
                if curve_type == "ST":
                   curve_label = "Contrast"
                else:
                   curve_label = "Contrastsurround"
                print self.data_dict[(xcoord,ycoord)][curve_type].keys()   
                for measure_name in self.data_dict[(xcoord,ycoord)][curve_type][curve_label + " = " + str(self.high_contrast) + "%"]["measures"].keys():
                    if not histograms_hc.has_key(curve_type + "_" + measure_name):
                        histograms_hc[curve_type + "_" + measure_name]=[]
                    histograms_hc[curve_type + "_" + measure_name].append(self.data_dict[(xcoord,ycoord)][curve_type][curve_label + " = " + str(self.high_contrast) + "%"]["measures"][measure_name])

                for measure_name in self.data_dict[(xcoord,ycoord)][curve_type][curve_label + " = " + str(self.low_contrast) + "%"]["measures"].keys():
                    if not histograms_lc.has_key(curve_type + "_" + measure_name):
                        histograms_lc[curve_type + "_" + measure_name]=[]
                    histograms_lc[curve_type + "_" + measure_name].append(self.data_dict[(xcoord,ycoord)][curve_type][curve_label + " = " + str(self.low_contrast) + "%"]["measures"][measure_name])
                
        for key in histograms_lc.keys():
                if ((len(histograms_lc[key]) != 0) and (len(histograms_hc[key]) != 0)):
                    fig = pylab.figure()
                    pylab.title(self.sheet_name+ " " + "MeanLC: " + str(numpy.mean(histograms_lc[key])) + "+/-" + str(numpy.std(histograms_lc[key])/ (len(histograms_lc[key])*len(histograms_lc[key]))) + "MeanHC: " + str(numpy.mean(histograms_hc[key])) + "+/-" + str(numpy.std(histograms_hc[key])/ (len(histograms_hc[key])*len(histograms_hc[key]))) , fontsize=12)
                    
                    f = fig.add_subplot(111)
                    f.set_xlabel(str(key))
                    f.set_ylabel('#Cells')
                    mmax = numpy.max(numpy.max(histograms_lc[key]),numpy.max(histograms_hc[key]))
                    mmin = numpy.min(numpy.min(histograms_lc[key]),numpy.min(histograms_hc[key]))
                    bins = numpy.arange(mmin,mmax+0.01,(mmax-mmin)/10.0)
                    f.hist(histograms_hc[key],bins=bins,normed=False,facecolor='green')
                    #f.axvline(x=numpy.mean(histograms_lc[key]),linewidth=4, color='r')
                    release_fig("Histogram<" + key + ">")
                    print key + "LC mean :" + str(numpy.mean(histograms_lc[key]))
                    print key + "HC mean :" + str(numpy.mean(histograms_hc[key]))
                else:
                    print "Histogram ", key , " empty!"

def compute_local_homogeneity_index(or_map,sigma):
    (xsize,ysize) = or_map.shape 
    
    lhi = numpy.zeros(or_map.shape) 
    
    for sx in xrange(0,xsize):
        for sy in xrange(0,ysize):
            lhi_current=[0,0]
            for tx in xrange(0,xsize):
                for ty in xrange(0,ysize):
                    lhi_current[0]+=numpy.exp(-((sx-tx)*(sx-tx)+(sy-ty)*(sy-ty))/(2*sigma*sigma))*numpy.cos(2*or_map[tx,ty]*numpy.pi)
                    lhi_current[1]+=numpy.exp(-((sx-tx)*(sx-tx)+(sy-ty)*(sy-ty))/(2*sigma*sigma))*numpy.sin(2*or_map[tx,ty]*numpy.pi)
           # print sx,sy
           # print lhi.shape
           # print lhi_current        
            lhi[sx,sy]= numpy.sqrt(lhi_current[0]*lhi_current[0] + lhi_current[1]*lhi_current[1])
                    
    return lhi       

def release_fig(filename=None):
    import pylab        
    pylab.show._needmain=False
    if filename is not None:
       fullname=filename+str(topo.sim.time())+".png"
       pylab.savefig(normalize_path(fullname))
    else:
       pylab.show()
       
       
       
