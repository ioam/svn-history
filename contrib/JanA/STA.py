from contrib.JanA.ofestimation import *
import contrib.dd
import contrib.JanA.dataimport
from contrib.JanA.regression import laplaceBias
from contrib.JanA.visualization import printCorrelationAnalysis
import scipy
import scipy.stats

animals = ['./LSCSM/LSCSM/2009_11_04_region3.dat','./LSCSM/LSCSM/2009_11_04_region5.dat','./LSCSM/LSCSM/2010_04_22.dat','./20091110_region4.dat']
animal_names = ['2009_11_04_region3','2009_11_04_region5','2010_04_22','20091110_region4']

animal_num = 2

animal = animals[animal_num]

res = contrib.dd.loadResults(animal)

dataset_node = res.children[0].children[0]

training_set = dataset_node.data["training_set"]
validation_set = dataset_node.data["validation_set"]
raw_validation_set = dataset_node.data["raw_validation_set"]
training_inputs= dataset_node.data["training_inputs"]
validation_inputs= dataset_node.data["validation_inputs"]

(num_pres,num_neurons) = numpy.shape(training_set)

testing_set = training_set[-0.1*num_pres:,:]
training_set = training_set[:-0.1*num_pres,:]

testing_inputs = training_inputs[-0.1*num_pres:,:]
training_inputs = training_inputs[:-0.1*num_pres,:]

kernel_size =  numpy.shape(numpy.mat(training_inputs))[1]


laplace = laplaceBias(int(numpy.sqrt(kernel_size)),int(numpy.sqrt(kernel_size)))
a = 0.0000000001

rpis = []
for i in xrange(0,40):
    print a
    a = a*2
    rpis.append(numpy.linalg.pinv(numpy.mat(training_inputs).T*numpy.mat(training_inputs) + a*laplace) * numpy.mat(training_inputs).T * numpy.mat(training_set))
    

best_rpis = numpy.mat(numpy.zeros((kernel_size,num_neurons)))
best_lambda = numpy.mat(numpy.zeros((1,num_neurons)))
import pylab
pylab.figure()

a = [1e-10,2e-10,1e-10,8e-10,1.6e-09,3.2e-09,6.4e-09,1.28e-08,2.56e-08,5.12e-08,1.024e-07,2.048e-07,4.096e-07,8.192e-07,1.6384e-06,3.2768e-06,6.5536e-06,1.31072e-05,2.62144e-05,5.24288e-05,0.0001048576,0.0002097152,0.0004194304,0.0008388608,0.0016777216,0.0033554432,0.0067108864,0.0134217728,0.0268435456,0.0536870912,0.1073741824,0.2147483648,0.4294967296,0.8589934592,1.7179869184,3.4359738368,6.8719476736,13.7438953472,27.4877906944,54.9755813888]


for i in xrange(0,num_neurons):
    corrs=[]
    for j in xrange(0,40):
	pa = numpy.mat(training_inputs * rpis[j][:,i])
        pta = numpy.mat(testing_inputs * rpis[j][:,i])
	corrs.append(scipy.stats.pearsonr(numpy.array(pta).flatten(),numpy.array(testing_set)[:,i].flatten())[0])
	
    if i < 10:
       pylab.plot(corrs)
    print numpy.shape(best_rpis[:,i])
    print numpy.shape(rpis[numpy.argmax(corrs)][:,i])
    best_rpis[:,i] = rpis[numpy.argmax(corrs)][:,i]
    best_lambda[0,i] = a[numpy.argmax(corrs)]


print best_lambda

rpa = numpy.mat(training_inputs * best_rpis)
rpva = numpy.mat(validation_inputs * best_rpis)
     
ofs = run_nonlinearity_detection(numpy.mat(training_set),numpy.mat(rpa),display=False)
rpi_pred_act_t = apply_output_function(numpy.mat(rpa),ofs)
rpi_pred_val_act_t = apply_output_function(numpy.mat(rpva),ofs)
printCorrelationAnalysis(training_set,validation_set,rpi_pred_act_t,rpi_pred_val_act_t)

numpy.savetxt(animal_names[animal_num]+'STA_20091011.txt',best_rpis)
