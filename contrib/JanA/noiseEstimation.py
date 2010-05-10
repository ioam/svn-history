import numpy 
import pylab

def signal_power_test(raw_validation_data_set, training_set, validation_set, pred_act, pred_val_act):
	
        signal_power=[]
	noise_power=[]
	normalized_noise_power=[]
	
	for i in xrange(0,len(raw_validation_data_set)):
	    (sp,np,nnp) = signal_and_noise_power(raw_validation_data_set[i])
	    signal_power.append(sp)
	    noise_power.append(np)
	    normalized_noise_power.append(nnp)
	
	pylab.figure()
	pylab.subplot(131)
	pylab.title('distribution of estimated signal power in neurons')
	pylab.plot(noise_power,signal_power,'ro')
	pylab.ylabel('signal power')
	pylab.xlabel('noise power')
	
	#print numpy.shape(training_set)
	#print numpy.shape(signal_power)
	#print numpy.shape(pred_act)
	
	training_prediction_power=numpy.divide(numpy.var(training_set,axis=0) - numpy.var(pred_act - training_set,axis=0), signal_power)
	validation_prediction_power=numpy.divide(numpy.var(validation_set,axis=0) - numpy.var(pred_val_act - validation_set,axis=0), signal_power)
	pylab.subplot(132)
	pylab.title('distribution of estimated prediction power ')
	pylab.plot(normalized_noise_power,training_prediction_power,'ro',label='training')
	pylab.plot(normalized_noise_power,validation_prediction_power,'bo',label='validation')
	pylab.axis([20.0,100.0,-2.0,2.0])
	pylab.xlabel('normalized noise power')
	pylab.ylabel('prediction power')
	pylab.legend()

	pylab.subplot(133)
	pylab.title('relationship between test set prediction power \n and validation prediction power')
	pylab.plot(validation_prediction_power,training_prediction_power,'ro')
	pylab.axis([-2.0,2.0,0.0,2.0])
	pylab.xlabel('validation set prediction power')
	pylab.ylabel('test set prediction power')
	

	return (signal_power,noise_power,normalized_noise_power,training_prediction_power,validation_prediction_power)

def signal_and_noise_power(responses):
    (trials,n) = numpy.shape(responses)	
    sp =  (1 / (trials-1.0)) * (trials * numpy.var(numpy.mean(responses,axis=0)) - numpy.mean(numpy.var(responses,axis=1)))
    np =  numpy.mean(numpy.var(responses,axis=1)) - sp
    nnp =  (numpy.mean(numpy.var(responses,axis=1)) - sp) / numpy.mean(numpy.var(responses,axis=1)) * 100
    return (sp,np,nnp)

def estimateNoise(trials):
    (num_neurons,num_trials,num_resp) = numpy.shape(trials)	
	
    mean_responses = numpy.mean(trials,1)
    		
    for i in xrange(0,1):
	pylab.figure()
	pylab.hist(mean_responses[i,:])
	bins = numpy.arange(numpy.min(mean_responses[i,:]),numpy.max(mean_responses[i,:]) + (numpy.max(mean_responses[i,:])-numpy.min(mean_responses[i,:]))/5.0,( numpy.max(mean_responses[i,:])-numpy.min(mean_responses[i,:]))/5.0)
	print numpy.min(mean_responses[i,:])
	print numpy.max(mean_responses[i,:])
	print bins
	#membership = numpy.zeros(numpy.shape(mean_responses[i,:]))
	for j in xrange(0,5):
	    membership = ((mean_responses[i,:] >= bins[j]) &  (mean_responses[i,:] < bins[j+1]))
	    print membership	
	    raw_responses = trials[i,:,membership].flatten()

	    pylab.figure()
	    pylab.hist(raw_responses)	
		
	
	
	
	
	
	
	