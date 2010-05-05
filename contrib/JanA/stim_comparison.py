import scipy
from scipy import linalg
import pickle
from contrib.modelfit import *
import numpy
import contrib.dd
	
	
def CompareNaturalVSHartley():	
	f = open("modelfitDatabase1.dat",'rb')
	dd = pickle.load(f)
	node = dd.children[22]

	rfs  = node.children[4].data["ReversCorrelationRFs"][0:102]
	
	pred_act  = numpy.array(node.children[4].data["ReversCorrelationPredictedActivities"][:,0:102])
	pred_val_act  = numpy.array(node.children[4].data["ReversCorrelationPredictedValidationActivities"][:,0:102])
	
	pred_act_t  = numpy.array(node.children[4].data["ReversCorrelationPredictedActivities+TF"][:,0:102])
	pred_val_act_t  = numpy.array(node.children[4].data["ReversCorrelationPredictedValidationActivities+TF"][:,0:102])
	
	
	training_set = node.data["training_set"][:,0:102]
	validation_set = node.data["validation_set"][:,0:102]
	
	training_inputs = node.data["training_inputs"]
	validation_inputs = node.data["validation_inputs"]
	raw_validation_set = node.data["raw_validation_set"]
	
	f = file("/home/antolikjan/topographica/topographica/Mice/2010_04_22/Hartley/imcutout.dat", "r")
    	hartley_inputs = [line.split() for line in f]
    	f.close()
	(a,b) = numpy.shape(hartley_inputs)
	for i in xrange(0,a):
	    for j in xrange(0,b):
		hartley_inputs[i][j] = float(hartley_inputs[i][j])
	hartley_inputs = numpy.mat(hartley_inputs).T		
        hartley_inputs = numpy.array(hartley_inputs)

	f = file("/home/antolikjan/topographica/topographica/Mice/2010_04_22/Hartley/RFcut.dat", "r")
    	hartley_RFs = [line.split() for line in f]
    	f.close()
	(a,b) = numpy.shape(hartley_RFs)
	for i in xrange(0,a):
	    for j in xrange(0,b):
		hartley_RFs[i][j] = float(hartley_RFs[i][j])
	hartley_RFs = numpy.array(hartley_RFs)		

	f = file("/home/antolikjan/topographica/topographica/Mice/2010_04_22/Hartley/spiking_3-7.dat", "r")
    	hartley_set = [line.split() for line in f]
	f.close()
	(a,b) = numpy.shape(hartley_set)
	for i in xrange(0,a):
	    for j in xrange(0,b):
		hartley_set[i][j] = float(hartley_set[i][j])
	hartley_set = numpy.array(hartley_set)		
	
		
	print numpy.shape(hartley_inputs)
	print numpy.shape(hartley_RFs)
	print numpy.shape(validation_inputs)
	
	print numpy.min(validation_inputs)
	print numpy.max(validation_inputs)
	
	 
	
	hartley_pred_act = numpy.mat(hartley_inputs) * numpy.mat(hartley_RFs)
	  
	hartley_pred_val_act = numpy.mat((validation_inputs-128.0)/128.0) * numpy.mat(hartley_RFs)
	
	rf_mag = [numpy.sum(numpy.power(r,2)) for r in rfs]
	
	#discard ugly RFs          	
	pylab.figure()
	pylab.hist(rf_mag)

	
	to_delete = numpy.nonzero((numpy.array(rf_mag) < 0.000000)*1.0)[0]
	print to_delete
	rfs = numpy.delete(rfs,to_delete,axis=0)
	pred_act = numpy.delete(pred_act,to_delete,axis=1)
	pred_val_act = numpy.delete(pred_val_act,to_delete,axis=1)
	training_set = numpy.delete(training_set,to_delete,axis=1)
	validation_set = numpy.delete(validation_set,to_delete,axis=1)
	
	for i in xrange(0,len(raw_validation_set)):
	    raw_validation_set[i] = numpy.delete(raw_validation_set[i],to_delete,axis=1)
	
	
	
	#(sx,sy) = numpy.shape(rfs[0])
	#ofs = fit_sigmoids_to_of(numpy.mat(training_set),numpy.mat(pred_act))
	#pred_act_t = apply_sigmoid_output_function(numpy.mat(pred_act),ofs)
	#pred_val_act_t= apply_sigmoid_output_function(numpy.mat(pred_val_act),ofs)
	
	pylab.figure()
	m = numpy.max([numpy.abs(numpy.min(rfs)),numpy.abs(numpy.max(rfs))])	
	for k in xrange(0,len(rfs)):		
		pylab.subplot(15,15,k+1)
		w = numpy.array(rfs[k])
		pylab.show._needmain=False
		pylab.imshow(w,vmin=-m,vmax=m,interpolation='nearest',cmap=pylab.cm.RdBu)
		pylab.axis('off')
		pylab.colorbar()
	
	pylab.figure()
	m = numpy.max([numpy.abs(numpy.min(hartley_RFs)),numpy.abs(numpy.max(hartley_RFs))])	
	for k in xrange(0,len(rfs)):		
		pylab.subplot(15,15,k+1)
		w = numpy.array(hartley_RFs[:,k])
		pylab.show._needmain=False
		pylab.imshow(numpy.reshape(w,(41,41)),vmin=-m,vmax=m,interpolation='nearest',cmap=pylab.cm.RdBu)
		pylab.axis('off')
		pylab.colorbar()

	
	print 'NATURAL'
	
	(ranks,correct,pred) = performIdentification(validation_set,pred_val_act)
	print "Natural:", correct , "Mean rank:", numpy.mean(ranks) , "MSE", numpy.mean(numpy.power(validation_set - pred_val_act,2))
	
	(ranks,correct,pred) = performIdentification(validation_set,pred_val_act_t)
	print "Natural+TF:", correct , "Mean rank:", numpy.mean(ranks) , "MSE", numpy.mean(numpy.power(validation_set - pred_val_act_t,2))
		
	raw_validation_data_set=numpy.rollaxis(numpy.array(raw_validation_set),2)
	
	signal_power,noise_power,normalized_noise_power,training_prediction_power,validation_prediction_power = signal_power_test(raw_validation_data_set, numpy.array(training_set), numpy.array(validation_set), pred_act, pred_val_act)
	signal_power,noise_power,normalized_noise_power,training_prediction_power_t,validation_prediction_power_t = signal_power_test(raw_validation_data_set, numpy.array(training_set), numpy.array(validation_set), pred_act_t, pred_val_act_t)
	
	print "Prediction power on training set / validation set: ", numpy.mean(training_prediction_power) , " / " , numpy.mean(validation_prediction_power)
	print "Prediction power after TF on training set / validation set: ", numpy.mean(training_prediction_power_t) , " / " , numpy.mean(validation_prediction_power_t)


        print 'HARTLEY'
	 
	(ranks,correct,pred) = performIdentification(validation_set,hartley_pred_val_act)
	print "Natural:", correct , "Mean rank:", numpy.mean(ranks) , "MSE", numpy.mean(numpy.power(validation_set - hartley_pred_val_act,2))
	