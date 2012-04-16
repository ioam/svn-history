import numpy
import pickle
import topo 
import pylab

def save_stuff(name):
    f = open(name,'wb')
    
    
    times = numpy.arange(1.0,10.0,1.0)
    #times = numpy.arange(1.0,100.0,1.0)
    #times = numpy.arange(0.2,3.0,0.05)    
    ct = 0
    
    dict = []
    
    sheets=["V1Simple","V1Complex", "V1ComplexInh"]
    #sheets=["V1Simple","V1Complex"]
    
    for t in times:
        topo.sim.run(t-ct)    
        d = {}
        for s in sheets:
            d[s] = {}
            d[s]["Activity"] = topo.sim[s].activity.copy()
            d[s]["Proj"] = {}
            
            if s == "V1Simple" or s == "V1ComplexInh":
               d[s]["OFy_avg"] = topo.sim[s].output_fns[-1].y_avg.copy()
               d[s]["OFt"] = topo.sim[s].output_fns[-1].t.copy()
            
            for con in topo.sim[s].in_connections:
                d[s]["Proj"][con.name] = {}
                d[s]["Proj"][con.name]['Activity']= con.activity.copy()
                #d[s]["Proj"][con.name]['CFS'] = [[b.weights.copy() for b in c] for c in con.cfs]
        
        dict.append(d)
        ct = t
        
    pickle.dump(dict,f)
    f.close()
    
def compare_stuff():
    f1 = open('m1.typ','rb')
    dd1 = pickle.load(f1)
    f2 = open('m2.typ','rb')
    dd2 = pickle.load(f2)
    
    c = 0
    for (d1,d2) in zip(dd1,dd2):
        c = c + 1
        for s in d1.keys():
            if numpy.sum(numpy.abs(d1[s]['Activity'] - d2[s]['Activity'])) != 0: 
               print ('Activity of sheet ' + s + '  at time ' + str(c) + ' do not match')
               print numpy.sum(numpy.abs(d1[s]['Activity'] - d2[s]['Activity']))
               pylab.figure()
               pylab.subplot(1,2,1)
               pylab.imshow(d1[s]['Activity'])
               pylab.subplot(1,2,2)
               pylab.imshow(d2[s]['Activity'])
            
            
            if s == "V1Simple" or s == "V1ComplexInh":
                if numpy.sum(numpy.abs(d1[s]['OFy_avg'] - d2[s]['OFy_avg'])) != 0: 
                   print ('YAVG of sheet ' + s + '  at time ' + str(c) + ' do not match') 
                
                if s == "V1ComplexInh":
                    if numpy.sum(numpy.abs(d1[s]['OFt'] - 4*d2[s]['OFt'])) != 0: 
                       print ('T of sheet ' + s + '  at time ' + str(c) + ' do not match') 

                else:
                    if numpy.sum(numpy.abs(d1[s]['OFt'] - d2[s]['OFt'])) != 0: 
                       print ('T of sheet ' + s + '  at time ' + str(c) + ' do not match') 
                
            for con in d1[s]["Proj"]:
                if numpy.sum(numpy.abs(d1[s]["Proj"][con]['Activity'] - d2[s]["Proj"][con]['Activity'])) != 0: 
                   print ('Activity of projection ' + con + ' in sheet ' + s + ' at time ' + str(c) + ' do not match')    
                
                #flag = True
                #for w1,w2 in zip(d1[s]["Proj"][con]['CFS'],d2[s]["Proj"][con]['CFS']):
                #    for ww1,ww2 in zip(w1,w2):
                #        if numpy.sum(numpy.abs(ww1 - ww2)) != 0:
                #           flag = False
                
                #if not flag: print ('Weights of projection ' + con + ' in sheet ' + s + ' at time ' + str(c) + ' do not match')    
