import __main__
import numpy
import pylab
import os.path
import scipy.stats
from math import pi, sqrt, exp, pow
from topo.plotting.plotfilesaver import * 
from topo.command.pylabplot import cyclic_tuning_curve, matrixplot
from topo.command.analysis import save_plotgroup
from matplotlib.ticker import MaxNLocator
from param import normalize_path
import pickle

import matplotlib.gridspec as gridspec

prefix = '/home/jan/DATA/LESI/CCLESIGifSMNew6NNBig=2/'
prefix_out = '/home/jan/DATA/LESI/CCLESIGifSMNew6NNBig=2/out2'


normalize_path.prefix = prefix_out

pylab.rc(('xtick.major','xtick.minor','ytick.major','ytick.minor'), pad=8)    

def release_fig(filename=None):
    fullname=filename+".png"
    pylab.savefig(normalize_path(fullname),dpi=100)


def disable_top_right_axis(ax):
    for loc, spine in ax.spines.iteritems():
            if loc in ['right','top']:
               spine.set_color('none') # don't draw spine
    for tick in ax.yaxis.get_major_ticks():
        tick.tick2On = False
    for tick in ax.xaxis.get_major_ticks():
        tick.tick2On = False

def disable_bottom_axis(ax):
    for loc, spine in ax.spines.iteritems():
            if loc in ['bottom']:
               spine.set_color('none') # don't draw spine
    for tick in ax.xaxis.get_major_ticks():
        tick.tick1On = False

def disable_left_axis(ax):
    for loc, spine in ax.spines.iteritems():
            if loc in ['left']:
               spine.set_color('none') # don't draw spine
    for tick in ax.yaxis.get_major_ticks():
        tick.tick1On = False

def remove_x_tick_labels():
    pylab.xticks([],[])  
 
def remove_y_tick_labels(): 
    pylab.yticks([],[])  



class SurroundModulationPlotting():

    low_contrast=20
    high_contrast=100
    
    def __init__(self):
        import pylab
        
        
        f = open(prefix+'data_dict.pickle','rb')
        (self.OR,self.OS,self.MR,self.data_dict) = pickle.load(f)
        f.close()
        
        self.recalculate_orientation_contrast_supression()
        self.recalculate_size_tuning_measures()
        
        for coords in self.data_dict.keys():
            xindex,yindex = coords
            self.plot_size_tunning(xindex,yindex)
            self.plot_orientation_contrast_tuning(xindex,yindex)
        
        self.plot_histograms_of_measures()
        print('1')
        self.plot_average_size_tuning_curve()
        print('2')
        self.plot_average_oct()
        print('3')
        
        self.Figure6()
        print('4')
        self.Figure8()
        print('5')
        #lhi = compute_local_homogeneity_index(self.OR*pi,1.5)    
        #f = open(prefix+'lhi1.5.pickle','wb')            
        #pickle.dump(lhi,f)
        #f.close()
                
        f = open(prefix+'lhi2.0.pickle','rb')            
        self.lhi = pickle.load(f)
        
        raster_plots_lc,raster_plots_hc = self.plot_map_feature_to_surround_modulation_feature_correlations(self.lhi,"Local Homogeneity Index")
        self.correlations_figure(raster_plots_lc)
        #self.plot_map_feature_to_surround_modulation_feature_correlations(self.OS,"OrientationSelectivity")
        print len(self.data_dict)
        
    def recalculate_orientation_contrast_supression(self):
        for (xindex,yindex) in self.data_dict.keys():
            measurment = self.data_dict[(xindex,yindex)]["OCT"]
            
            for curve_label in measurment.keys():
                if curve_label != 'ORTC':
                    curve =  measurment[curve_label]["data"]
                    
                    orr = measurment["ORTC"]["info"]["pref_or"]
                    orr_ort = orr + (numpy.pi/2.0)        
                    
                    pref_or_resp=curve[orr].view()[0][xindex][yindex]
                    cont_or_resp=curve[orr_ort].view()[0][xindex][yindex]
            
                    if pref_or_resp != 0 and cont_or_resp != 0:
                        measurment[curve_label]["measures"]["or_suppression"]=(pref_or_resp-cont_or_resp)/numpy.max([cont_or_resp,pref_or_resp])
                    else: 
                        measurment[curve_label]["measures"]["or_suppression"]=0.0
   
    
    
    def recalculate_size_tuning_measures(self):
        for (xindex,yindex) in self.data_dict.keys():
            curve_data = self.data_dict[(xindex,yindex)]["ST"]
            
            hc_curve_name = "Contrast = " + str(self.high_contrast) + "%";
            lc_curve_name = "Contrast = " + str(self.low_contrast) + "%";
            for curve_label in [hc_curve_name,lc_curve_name]:
                curve = curve_data[curve_label]["data"]
                x_values = sorted(curve.keys())
                y_values = [curve[key].view()[0][xindex, yindex] for key in x_values]

                #compute critical indexes in the size tuning curves
                curve_data[curve_label]["measures"]["peak_near_facilitation_index"] = numpy.argmax(y_values)
                curve_data[curve_label]["measures"]["peak_near_facilitation"] = x_values[curve_data[curve_label]["measures"]["peak_near_facilitation_index"]]


                curve_data[curve_label]["measures"]["peak_supression_index"] = curve_data[curve_label]["measures"]["peak_near_facilitation_index"] + numpy.argmin(y_values[curve_data[curve_label]["measures"]["peak_near_facilitation_index"] + 1:]) + 1
                curve_data[curve_label]["measures"]["peak_supression"] = x_values[curve_data[curve_label]["measures"]["peak_supression_index"]]
                curve_data[curve_label]["measures"]["suppresion_index"] = (y_values[curve_data[curve_label]["measures"]["peak_near_facilitation_index"]] - y_values[-1]) /  y_values[curve_data[curve_label]["measures"]["peak_near_facilitation_index"]]

                curve_data[curve_label]["measures"]["peak_far_facilitation_index"] = curve_data[curve_label]["measures"]["peak_supression_index"] + numpy.argmax(y_values[curve_data[curve_label]["measures"]["peak_supression_index"] + 1:]) + 1
                curve_data[curve_label]["measures"]["peak_far_facilitation"] = x_values[curve_data[curve_label]["measures"]["peak_far_facilitation_index"]]
                curve_data[curve_label]["measures"]["counter_suppresion_index"] = (y_values[curve_data[curve_label]["measures"]["peak_far_facilitation_index"]] - y_values[curve_data[curve_label]["measures"]["peak_supression_index"]])/ y_values[curve_data[curve_label]["measures"]["peak_near_facilitation_index"]]
                
                
   
    def plot_size_tunning(self, xindex, yindex,independent=True):

        if independent:
           fig = pylab.figure()
        
        colors=['red','blue','green','purple','orange','black','yellow']
        
        measurment = self.data_dict[(xindex,yindex)]["ST"]
        
        i = 0
        m = 0
        for curve_label in measurment.keys():
            curve =  measurment[curve_label]["data"]
            x_values = sorted(curve.keys())
            y_values = [curve[key].view()[0][xindex, yindex] for key in x_values]
            
            pylab.plot(x_values, y_values, lw=3, color=colors[i],label=curve_label)
            
            m = max(m,max(y_values))
                
            pylab.annotate('', xy=(measurment[curve_label]["measures"]["peak_near_facilitation"], y_values[measurment[curve_label]["measures"]["peak_near_facilitation_index"]]), xycoords='data',
            xytext=(-1, 20), textcoords='offset points', arrowprops=dict(facecolor='green', shrink=0.05))
    
    
            if measurment[curve_label]["measures"].has_key("peak_supression"):
                pylab.annotate('', xy=(measurment[curve_label]["measures"]["peak_supression"], y_values[measurment[curve_label]["measures"]["peak_supression_index"]]), xycoords='data',
                           xytext=(-1, 20), textcoords='offset points', arrowprops=dict(facecolor='red', shrink=0.05))
            
            if measurment[curve_label]["measures"].has_key("peak_far_facilitation"):
                pylab.annotate('', xy=(measurment[curve_label]["measures"]["peak_far_facilitation"], y_values[measurment[curve_label]["measures"]["peak_far_facilitation_index"]]), xycoords='data',
                           xytext=(-1, 20), textcoords='offset points', arrowprops=dict(facecolor='blue', shrink=0.05))
            i+=1
        
        
        disable_top_right_axis(pylab.gca())
        ax = pylab.gca()
        pylab.setp(pylab.getp(pylab.gca(), 'xticklabels'), fontsize=20)
        pylab.setp(pylab.getp(pylab.gca(), 'yticklabels'), fontsize=20)
        ax.set_xlim(0,2)  
        ax.set_xticks([0,1,2])
        m = numpy.ceil(m)
        ax.set_yticks([0,m/2,m])
        ax.set_ylim(0,m)
        if independent:
            release_fig("STC[" + str(xindex) + "," + str(yindex) + "]")
    
    
    def calculate_octc_selectivity(self,angles,responses):
        c = 0
        n = 0
        for a,r in zip(angles,responses):
            c = c + r * complex(numpy.cos(a),numpy.sin(a))    
            n = n + numpy.abs(r)
        return numpy.abs(c)/n
        
    
    def plot_orientation_contrast_tuning(self, xindex, yindex,independent=True):
            if independent:
               fig = pylab.figure()
        
            colors=['red','blue','green','purple','orange','black','yellow']
            
            orientation = self.data_dict[(xindex,yindex)]["OCT"]["ORTC"]["info"]["pref_or"]
            
            measurment = self.data_dict[(xindex,yindex)]["OCT"]
            i = 0
            m = 0
            
            for curve_label in measurment.keys():
                if curve_label != 'Contrastsurround = 100%':
                    curve =  measurment[curve_label]["data"]
                    
                    x_values = sorted(curve.keys())
                    y_values = []
                    for k in x_values:
                        y_values.append(curve[k].view()[0][xindex, yindex])

                    if curve_label != 'ORTC':
                        
                        z = []
                        ks = sorted(measurment["ORTC"]["data"].keys())
                        for k in ks:                        
                            z.append(measurment["ORTC"]["data"][k].view()[0][xindex, yindex])
                        
                        ssi = self.calculate_octc_selectivity(2*x_values,y_values-numpy.max(z))
                        self.data_dict[(xindex,yindex)]["OCT"][curve_label]["measures"]["SSI"]=ssi
                        self.data_dict[(xindex,yindex)]["OCT"]['Contrastsurround = 100%']["measures"]["SSI"]=ssi
                        
                    
                    
                    x_values=numpy.array(x_values)-orientation

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


                    inds = numpy.argsort(x_values)
                    y_values = numpy.take(y_values, inds)
                    x_values = sorted(x_values)

                    #numpy.append(y_values,y_values[0])
                    #numpy.append(x_values,x_values[0]+numpy.pi)
                    
                    if x_values[0] == -numpy.pi/2:
                        y_values = numpy.append(y_values,[y_values[0]])
                        x_values = numpy.append(x_values,[numpy.pi/2])
                    else:
                        y_values = numpy.append([y_values[-1]],y_values)
                        x_values = numpy.append([-numpy.pi/2],x_values)

                    
                    m = max(m,max(y_values))
                    
                    pylab.plot(x_values, y_values, lw=3, color=colors[i],label=curve_label)
                    i+=1
            
            disable_top_right_axis(pylab.gca())
            ax = pylab.gca()
            pylab.title(str(ssi))
            pylab.setp(pylab.getp(pylab.gca(), 'xticklabels'), fontsize=20)
            pylab.setp(pylab.getp(pylab.gca(), 'yticklabels'), fontsize=20)
            ax.set_xlim(-numpy.pi/2-0.2,numpy.pi/2.0+0.2)  
            ax.set_xticks([-numpy.pi/2,0,numpy.pi/2.0])
            ax.set_xticklabels(['-pi/2','0','pi/2'])
            
            # get ceil at first decimal point
            m = numpy.ceil(m)
            ax.set_yticks([0.1,m/2,m])
            ax.set_ylim(0.1,m)

            if independent:
                release_fig("OCTC[" + str(xindex) + "," + str(yindex) + "]")
            

    def plot_average_size_tuning_curve(self,independent=True):
        
        if independent:
            fig = pylab.figure()
                
        average_curves={}        
        sem_curves={}        
        curves={}        
        
        
        
        for k in self.data_dict.keys():
            # find maximum for the curves
            m = []
            for curve_label in self.data_dict[k]["ST"].keys():
                    xindex, yindex = k
                    curve =  self.data_dict[k]["ST"][curve_label]["data"]
                    x_values = sorted(curve.keys())
                    m.append(numpy.max([curve[key].view()[0][xindex, yindex] for key in x_values]))
            
            m = numpy.max(m)
            
            for curve_label in self.data_dict[k]["ST"].keys():
                    xindex, yindex = k
                    curve =  self.data_dict[k]["ST"][curve_label]["data"]
                    x_values = sorted(curve.keys())
                    y_values = [curve[key].view()[0][xindex, yindex] for key in x_values]
                    
                    # normalize curve
                    y_values = y_values / m
      
                    if curves.has_key(curve_label):
                      curves[curve_label].append(numpy.array(y_values))
                    else:
                      curves[curve_label]=[numpy.array(y_values)]
            
        
        
        
        for curve_label in curves:
            average_curves[curve_label]=numpy.mean(numpy.array(curves[curve_label]),axis=0)
            sem_curves[curve_label]=scipy.stats.sem(numpy.array(curves[curve_label]),axis=0)
        
        
        colors=['red','blue']
        i=0
        for curve_label in average_curves:
            pylab.plot(x_values, average_curves[curve_label]*100, lw=3, color=colors[i]) 
            pylab.errorbar(x_values, average_curves[curve_label]*100, lw=1, ecolor=colors[i], yerr=sem_curves[curve_label]*100, fmt=None) 
            pylab.xticks([0,numpy.max(x_values)/2,numpy.max(x_values)])
            pylab.yticks([0,50,100])
            pylab.gca().set_yticklabels(['0%','50%','100%'])
            pylab.xlim(-0.1,numpy.max(x_values)+0.1)
            pylab.ylim(0,100)
            i=i+1

        disable_top_right_axis(pylab.gca())

        pylab.setp(pylab.getp(pylab.gca(), 'xticklabels'), fontsize=20)
        pylab.setp(pylab.getp(pylab.gca(), 'yticklabels'), fontsize=20)  
 
        if independent:
            release_fig("AverageSTC")
   
    def plot_average_oct(self,independent=True):
        if independent:
            fig = pylab.figure()
        
        average_curves={}        
        sem_curves={}        
        curves={}        
        for k in self.data_dict.keys():
          xindex, yindex = k          
          curve =  self.data_dict[k]["OCT"]["ORTC"]["data"]
          x_values = sorted(curve.keys())
          m = numpy.max([curve[l].view()[0][xindex, yindex] for l in x_values])
            
          for curve_label in self.data_dict[k]["OCT"].keys():
              if curve_label != 'Contrastsurround = 100%':                
                  orientation = self.data_dict[(xindex,yindex)]["OCT"]["ORTC"]["info"]["pref_or"]
                  curve =  self.data_dict[k]["OCT"][curve_label]["data"]
                  x_values = sorted(curve.keys())
                  y_values = [curve[l].view()[0][xindex, yindex] for l in x_values]
                  x_values=numpy.array(x_values)-orientation
                  
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


                  inds = numpy.argsort(x_values)
                  y_values = numpy.take(y_values, inds)
                  x_values = sorted(x_values)
                  
                  if x_values[0] == -numpy.pi/2:
                    y_values = numpy.append(y_values,[y_values[0]])
                    x_values = numpy.append(x_values,[numpy.pi/2])
                  else:
                    y_values = numpy.append([y_values[-1]],y_values)
                    x_values = numpy.append([-numpy.pi/2],x_values)
                  
                  # normalize curve
                  y_values = y_values / m
                    
                  if curves.has_key(curve_label):
                      curves[curve_label].append(numpy.array(y_values))
                  else:
                      curves[curve_label]=[numpy.array(y_values)]
        
        for curve_label in curves:
            average_curves[curve_label]=numpy.mean(numpy.array(curves[curve_label]),axis=0)
            sem_curves[curve_label]=scipy.stats.sem(numpy.array(curves[curve_label]),axis=0)


        colors=['red','blue','green','purple','orange','black','yellow']
        i=0
        
        for curve_label in average_curves.keys():
            pylab.plot(x_values, average_curves[curve_label]*100, lw=3, color=colors[i]) 
            ax = pylab.gca()
            ax.errorbar(x_values, average_curves[curve_label]*100, lw=1, ecolor=colors[i], yerr=sem_curves[curve_label]*100, fmt=None) 
            ax.set_xlim(-numpy.pi/2-0.2,numpy.pi/2.0+0.2)  
            ax.set_xticks([-numpy.pi/2,0,numpy.pi/2.0])
            ax.set_xticklabels(['-pi/2','0','pi/2'])
            ax.set_yticks([0,50,100])
            ax.set_yticklabels(['0%','50%','100%'])
            ax.set_ylim(0,110)
            
            
            i=i+1
        
        disable_top_right_axis(pylab.gca())
        pylab.setp(pylab.getp(pylab.gca(), 'xticklabels'), fontsize=20)
        pylab.setp(pylab.getp(pylab.gca(), 'yticklabels'), fontsize=20)
        if independent:
            release_fig("AverageOCTC") 

    def plot_histograms_of_measures(self):
        histograms_lc = {} 
        histograms_hc = {}
        for (xcoord,ycoord) in self.data_dict.keys():
            for curve_type in self.data_dict[(xcoord,ycoord)].keys():
                if curve_type == "ST":
                   curve_label = "Contrast"
                else:
                   curve_label = "Contrastsurround"
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
                    #pylab.title(str(numpy.mean(histograms_lc[key])) + "+/-" + str(numpy.std(histograms_lc[key])/ (len(histograms_lc[key])*len(histograms_lc[key]))) + "MeanHC: " + str(numpy.mean(histograms_hc[key])) + "+/-" + str(numpy.std(histograms_hc[key])/ (len(histograms_hc[key])*len(histograms_hc[key]))) , fontsize=12)
                    
                    f = fig.add_subplot(111)
                    mmax = numpy.max([numpy.max(histograms_lc[key]),numpy.max(histograms_hc[key])])
                    mmin = numpy.min([numpy.min(histograms_lc[key]),numpy.min(histograms_hc[key])])
                    bins = numpy.arange(mmin-0.01,mmax+0.01,(mmax+0.01-(mmin-0.01))/10.0)
                    
                    if key == 'ST_contrast_dependent_shift':
                        f.hist(histograms_hc[key],bins=bins,normed=False)
                    else:
                        histograms_lc[key]
                        histograms_hc[key]
                        f.hist((histograms_lc[key],histograms_hc[key]),bins=bins,color=['white','black'],normed=True,label=['Low contrast','High contrast'])
                        f.legend(loc = "upper left")
                        
                    
                    ax = pylab.gca()
                    disable_left_axis(ax)
                    disable_top_right_axis(ax)
                    pylab.setp(pylab.getp(pylab.gca(), 'xticklabels'), fontsize=20)
                    ax.xaxis.set_major_locator(MaxNLocator(4))
                    remove_y_tick_labels()
                    #f.axvline(x=numpy.mean(histograms_lc[key]),linewidth=4, color='r')
                    
                    release_fig("Histogram<" + key + ">")
                    print key + "LC mean :" + str(numpy.mean(histograms_lc[key]))
                    print key + "HC mean :" + str(numpy.mean(histograms_hc[key]))
                else:
                    print "Histogram ", key , " empty!"

    def Figure6(self):
        self.fig = pylab.figure(facecolor='w',figsize=(14, 12),dpi=800)
        gs = gridspec.GridSpec(44, 36)
        gs.update(left=0.05, right=0.95, top=0.95, bottom=0.05,wspace=0.2,hspace=0.2)
        
        picked_stcs = [(53,51), (55,51) , (49,51) , (47,55) , (47,61) , (53,59) ]
        #picked_stcs = [(51,57),(51,57),(51,57),(51,57),(51,57),(51,57)]
        
        
        ax = pylab.subplot(gs[1:19,9:27])
        self.plot_average_size_tuning_curve(independent=False)
        pylab.ylabel('Normalized response', fontsize=20)
        
        ax = pylab.subplot(gs[22:32,1:11])
        self.plot_size_tunning(picked_stcs[0][0], picked_stcs[0][1],independent=False)
        remove_x_tick_labels()
        pylab.ylabel('Response', fontsize=20)
        ax = pylab.subplot(gs[22:32,13:23])
        self.plot_size_tunning(picked_stcs[1][0], picked_stcs[1][1],independent=False)
        disable_left_axis(pylab.gca())
        remove_x_tick_labels()
        remove_y_tick_labels()
        ax = pylab.subplot(gs[22:32,25:35])
        self.plot_size_tunning(picked_stcs[2][0], picked_stcs[2][1],independent=False)
        disable_left_axis(pylab.gca())
        remove_x_tick_labels()
        remove_y_tick_labels()
        
        ax = pylab.subplot(gs[34:44,1:11])
        self.plot_size_tunning(picked_stcs[3][0], picked_stcs[3][1],independent=False)
        pylab.ylabel('Response', fontsize=20)
        ax = pylab.subplot(gs[34:44,13:23])
        self.plot_size_tunning(picked_stcs[4][0], picked_stcs[4][1],independent=False)
        disable_left_axis(pylab.gca())
        remove_y_tick_labels()
        ax = pylab.subplot(gs[34:44,25:35])
        self.plot_size_tunning(picked_stcs[5][0], picked_stcs[5][1],independent=False)
        disable_left_axis(pylab.gca())
        remove_y_tick_labels()
        
        release_fig("Figure6") 

    def Figure8(self):
        self.fig = pylab.figure(facecolor='w',figsize=(14, 12),dpi=800)
        gs = gridspec.GridSpec(44, 36)
        gs.update(left=0.05, right=0.95, top=0.95, bottom=0.05,wspace=0.2,hspace=0.2)
        
        picked_stcs = [(53,47),(53,49),(55,47),(51,63),(49,53),(47,63)]
        #picked_stcs = [(54,45), (54,63) , (66,57) , (54,57) , (57,45) , (60,57)]
        
        ax = pylab.subplot(gs[1:19,9:27])
        self.plot_average_oct(independent=False)
        pylab.ylabel('Normalized response', fontsize=20)
        
        ax = pylab.subplot(gs[22:32,1:11])
        self.plot_orientation_contrast_tuning(picked_stcs[0][0], picked_stcs[0][1],independent=False)
        remove_x_tick_labels()
        pylab.ylabel('Response', fontsize=20)
        ax = pylab.subplot(gs[22:32,13:23])
        self.plot_orientation_contrast_tuning(picked_stcs[1][0], picked_stcs[1][1],independent=False)
        disable_left_axis(pylab.gca())
        remove_x_tick_labels()
        remove_y_tick_labels()
        ax = pylab.subplot(gs[22:32,25:35])
        self.plot_orientation_contrast_tuning(picked_stcs[2][0], picked_stcs[2][1],independent=False)
        disable_left_axis(pylab.gca())
        remove_x_tick_labels()
        remove_y_tick_labels()
        
        ax = pylab.subplot(gs[34:44,1:11])
        self.plot_orientation_contrast_tuning(picked_stcs[3][0], picked_stcs[3][1],independent=False)
        pylab.ylabel('Response', fontsize=20)
        ax = pylab.subplot(gs[34:44,13:23])
        self.plot_orientation_contrast_tuning(picked_stcs[4][0], picked_stcs[4][1],independent=False)
        disable_left_axis(pylab.gca())
        remove_y_tick_labels()
        ax = pylab.subplot(gs[34:44,25:35])
        self.plot_orientation_contrast_tuning(picked_stcs[5][0], picked_stcs[5][1],independent=False)
        disable_left_axis(pylab.gca())
        remove_y_tick_labels()
        release_fig("Figure8") 
    
    def correlations_figure(self,raster_plots):
        
        self.fig = pylab.figure(facecolor='w',figsize=(15, 18),dpi=800)
        gs = gridspec.GridSpec(3,2)
        gs.update(left=0.07, right=0.95, top=0.95, bottom=0.05,wspace=0.2,hspace=0.2)
        
        ax = pylab.subplot(gs[0,0])
        m,b = numpy.polyfit(raster_plots["or_suppression"][1],raster_plots["or_suppression"][0],1)
        correlation,pval = scipy.stats.pearsonr(raster_plots["or_suppression"][1],raster_plots["or_suppression"][0])
        pylab.scatter(raster_plots["or_suppression"][1],raster_plots["or_suppression"][0],s=18, facecolor = 'r',lw = 0)
        pylab.plot(raster_plots["or_suppression"][1],m*numpy.array(raster_plots["or_suppression"][1])+b,'-k',linewidth=2)
        disable_top_right_axis(ax)
        pylab.ylabel('Orientation-contrast suppression', fontsize=20)
        
        ax = pylab.subplot(gs[0,1])
        m,b = numpy.polyfit(raster_plots["SSI"][1],raster_plots["SSI"][0],1)
        correlation,pval = scipy.stats.pearsonr(raster_plots["SSI"][1],raster_plots["SSI"][0])
        pylab.scatter(raster_plots["SSI"][1],raster_plots["SSI"][0],s=18, facecolor = 'r',lw = 0)
        pylab.plot(raster_plots["SSI"][1],m*numpy.array(raster_plots["SSI"][1])+b,'-k',linewidth=2)
        disable_top_right_axis(ax)
        pylab.ylabel('Surround selectivity index', fontsize=20)
        
        print raster_plots.keys()
        
        ax = pylab.subplot(gs[1,0])
        m,b = numpy.polyfit(raster_plots["suppresion_index"][1],raster_plots["suppresion_index"][0],1)
        correlation,pval = scipy.stats.pearsonr(raster_plots["suppresion_index"][1],raster_plots["suppresion_index"][0])
        pylab.scatter(raster_plots["suppresion_index"][1],raster_plots["suppresion_index"][0],s=18, facecolor = 'r',lw = 0)
        pylab.plot(raster_plots["suppresion_index"][1],m*numpy.array(raster_plots["suppresion_index"][1])+b,'-k',linewidth=2)
        disable_top_right_axis(ax)
        pylab.ylabel('Suppression index', fontsize=20)

        ax = pylab.subplot(gs[1,1])
        m,b = numpy.polyfit(raster_plots["counter_suppresion_index"][1],raster_plots["counter_suppresion_index"][0],1)
        correlation,pval = scipy.stats.pearsonr(raster_plots["counter_suppresion_index"][1],raster_plots["counter_suppresion_index"][0])
        pylab.scatter(raster_plots["counter_suppresion_index"][1],raster_plots["counter_suppresion_index"][0],s=18, facecolor = 'r',lw = 0)
        pylab.plot(raster_plots["counter_suppresion_index"][1],m*numpy.array(raster_plots["counter_suppresion_index"][1])+b,'-k',linewidth=2)
        disable_top_right_axis(ax)
        pylab.ylabel('Counter suppression index', fontsize=20)
        
        
        ax = pylab.subplot(gs[2,0])
        pylab.scatter(self.lhi.ravel(),self.MR.ravel()*2,s=3, facecolor = 'r',lw = 0)
        xx,z = running_average(self.lhi.ravel(),self.MR.ravel()*2)
        pylab.plot(xx,z,'k',lw=3.0)
        disable_top_right_axis(ax)
        pylab.xlabel('Local homogeneity index', fontsize=20)
        pylab.ylabel('Modulation ratio', fontsize=20)
        
        
        ax = pylab.subplot(gs[2,1])
        pylab.scatter(self.lhi.ravel(),self.OS.ravel(),s=3, facecolor = 'r',lw = 0)
        xx,z = running_average(self.lhi.ravel(),self.OS.ravel())
        pylab.plot(xx,z,'k',lw=3.0)           
        disable_top_right_axis(ax)
        pylab.xlabel('Local homogeneity index', fontsize=20)
        pylab.ylabel('Orientation selectivity', fontsize=20)

        print scipy.stats.pearsonr(self.lhi.ravel(),self.OS.ravel())        
        print scipy.stats.pearsonr(self.lhi.ravel(),self.MR.ravel()*2)
        
        release_fig("CorrelationFigure") 


    def plot_map_feature_to_surround_modulation_feature_correlations(self,map_feature,map_feature_name):
            
            from numpy import polyfit
            
            raster_plots_lc={}
            raster_plots_hc={}
            for (xcoord,ycoord) in self.data_dict.keys():
                for curve_type in self.data_dict[(xcoord,ycoord)].keys():
                    if curve_type == "ST":
                       curve_label = "Contrast"
                    else:
                       curve_label = "Contrastsurround" 
                    
                    
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
                        #correlation = numpy.corrcoef(raster_plots_hc[key][0],raster_plots_hc[key][1])[0,1]
                        import scipy.stats
                        correlation = scipy.stats.pearsonr(raster_plots_hc[key][0],raster_plots_hc[key][1])[0]
                        pval= scipy.stats.pearsonr(raster_plots_hc[key][0],raster_plots_hc[key][1])[1] 
                    except FloatingPointError:
                          correlation = 0
                    m,b = numpy.polyfit(raster_plots_hc[key][0],raster_plots_hc[key][1],1)
                    f.plot(raster_plots_hc[key][0],raster_plots_hc[key][1],'ro')
                    f.plot(raster_plots_hc[key][0],m*numpy.array(raster_plots_hc[key][0])+b,'-k',linewidth=2)
                    release_fig("RasterHC<" + map_feature_name + ","+ key +  " Corr:"+ str(correlation) + '|'+ str(pval) + ">")
                    
            
            for key in raster_plots_lc.keys():
                    fig = pylab.figure()
                    f = fig.add_subplot(111)
                    f.set_xlabel(str(key))
                    f.set_ylabel(map_feature_name)
                    m,b = numpy.polyfit(raster_plots_lc[key][0],raster_plots_lc[key][1],1)
                    try:
                        #correlation = numpy.corrcoef(raster_plots_lc[key][0],raster_plots_lc[key][1])[0,1]
                        import scipy.stats
                        correlation = scipy.stats.pearsonr(raster_plots_lc[key][0],raster_plots_lc[key][1])[0]
                        pval= scipy.stats.pearsonr(raster_plots_lc[key][0],raster_plots_lc[key][1])[1] 
                    except FloatingPointError:
                          correlation = 0
                    f.plot(raster_plots_lc[key][0],raster_plots_lc[key][1],'ro')
                    f.plot(raster_plots_lc[key][0],m*numpy.array(raster_plots_lc[key][0])+b,'-k',linewidth=2)
                    release_fig("RasterLC<" + map_feature_name + ","+ key + " Corr:"+ str(correlation)+ '|'+ str(pval) + ">")
        
            return (raster_plots_lc,raster_plots_hc)

def running_average(x,y):
    s = 0.1
    z = []
    xx = []
    for i in numpy.arange(0.01,1.0,0.1):
        w = []
        for (j,h) in zip(x,y):
           if abs(j-i) < 0.05:
              w.append(h)  
        z.append(numpy.mean(w))
        xx.append(i)
    return xx,z
    
def compute_local_homogeneity_index(or_map,sigma):
    (xsize,ysize) = or_map.shape 
    
    lhi = numpy.zeros(or_map.shape) 
    
    for sx in xrange(0,xsize):
        for sy in xrange(0,ysize):
            lhi_current=[0,0]
            for tx in xrange(0,xsize):
                for ty in xrange(0,ysize):
                    lhi_current[0]+=numpy.exp(-((sx-tx)*(sx-tx)+(sy-ty)*(sy-ty))/(2*sigma*sigma))*numpy.cos(2*or_map[tx,ty])
                    lhi_current[1]+=numpy.exp(-((sx-tx)*(sx-tx)+(sy-ty)*(sy-ty))/(2*sigma*sigma))*numpy.sin(2*or_map[tx,ty])
            lhi[sx,sy]= numpy.sqrt(lhi_current[0]*lhi_current[0] + lhi_current[1]*lhi_current[1])/(2*numpy.pi*sigma*sigma)
            
    return lhi
