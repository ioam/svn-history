#!/usr/bin/env python
# -*- coding: utf8 -*-
"""

retina.py
===================

The retina for 'benchmark one'. This should feed the "Hyper-Column" ( https://facets.kip.uni-heidelberg.de/private/wiki/index.php/V1_hypercolumn#Benchmark_one )
For this retina, it consists of 2 layers of neurons on a rectangular grid connected in a one to one fashion.
Here, we more use primate " 'Phasic' responses originate with morphologically larger ganglion cell types with fast optic nerve fiber conduction velocities (~4 m/s, Gouras, 1969). Microelectrodes staining of such cells shows that they are 'parasol' types (Dacey and Lee, 1994). ON types branch low in the inner plexiform layer (sublamina b), while OFF types branch high in the inner plexiform layer (sublamina a) following the classic branching pattern for ON and OFF center cells (Nelson et al, 1978; Dacey and Lee, 1994). Phasic cells are often referred to as the 'magnocellular' or 'M-cell' pathway because their fibers terminate in the magnocellular layer of the lateral geniculate nucleus of the thalamus. Near the fovea receptive fields of phasic cells are 2-3 times larger than those of tonic cells and may be 10 times larger in peripheral retina."

See :
Data for parameters http://webvision.med.utah.edu/GCPHYS1.HTM (TODO LUP: define different sets for different animals (cat, monkey, human))
Morphology : http://webvision.med.utah.edu/GC1.html
Topics on http://homepages.inf.ed.ac.uk/cgi/rbf/CVONLINE/phase3entries.pl?TAG59

LUP : the grid is rectangular, but should be hexagonal
TODO: justify or not SFA (since we are interested in synchrony effect, we should rather use a simpler model

$ Id $

"""
import datetime
try: 
    import pyNN.nest as pyNN
except:
    print "Warning -- could not import pyNN; continuing anyway..."

    
import os, tempfile
import numpy

def tmpfile2spikelist(filename,dt):
    """
    Returns a spike list from the tmp file saved by PyNN-NEST (=a line commented, then one line per event: absolute time in ms, GID)
    
    the spike list is represented as a list of events. Events are tuples (relative time
    since last event, neuron_id); neuron_id and time are integers

    """
    import os

    f = open(filename,'r')
    lines = f.readlines()
    f.close()

    spike_list = []
    spike_time_ = 0

    for i_line in range(1,len(lines)):
	[spike_time , neuron_id] = lines[i_line].split("\t", 1)
        spike_time = float(spike_time) / dt
	rel_spike_time = float(spike_time) - spike_time_
	spike_time_    = float(spike_time)
	spike_list.append((int(rel_spike_time),int(neuron_id)))
	
    return spike_list


def spikelist2spikematrix(DATA, N, N_time, dt):
    """
    Returns a matrix of the number of spikes during simulation.
    Is of the shape of N x N 
    The spike list is a list of tuples (rel time, neuron_id) where the location of each neuron_id is given by the NEURON_ID matrix, which is in a standardized way [[ (N*i+j)  ]] where i and j are line and column respectively.

    for instance for a 4x4 population

       [[ 0,  1,  2,  3],
       [ 4,  5,  6,  7],
       [ 8,  9, 10, 11],
       [12, 13, 14, 15]]

    """

    DATA=numpy.array([[int(k), int(v)] for k,v in DATA])
    spikematrix=numpy.zeros((N,N))
    if DATA.size > 0:
        neuron_id=DATA[:,1]
        for i_id in numpy.unique(neuron_id):
            column = numpy.mod(i_id,N)
            line = numpy.floor(i_id/N)
            where_i_id_fired = [int(index) for index in numpy.where(neuron_id==i_id)[0] ]
            spikematrix[line,column] = sum(where_i_id_fired )

    return spikematrix / N_time * dt

def retina_default():
    """
    (Over-)Writes default parameters for the retina into the HDF file located at url.

    Sets up parameters and the whole structure of the dictionary / HDF file in url.

    This part of the benchmark contains all relevant parameters and stores them to a dictionary for clarity &future compatibility with XML exports.

    LUP TODO: this should also come from  a XML file? see Andrew's wrapper

    """
    params = {} # a dictionary containing all parameters
    # === Define parameters ========================================================
    # LUP: get running file name and include script in HDF5?
    N=100
    params = {'description' : 'default retina',
        'N': N, # integer;  total number of Ganglion Cells LUP: how do we include types and units in parameters? (or by default it is a float in ISO standards)
        'N_ret': 2.0, # float;  diameter of Ganglion Cell's RF
        'K_ret': 4.0, # float; ratio of center vs. surround in DOG
        'dt'         : 0.1,# discretization step in simulations (ms)
        'simtime'    : 40000*0.1,      # float; (ms)
        'syn_delay'  : 1.0,         # float; (ms)
        'noise_std' : 2.0,       # (nA??) standard deviation of the internal noise
        'snr' : 2.0,
        'weight'     : 1.0,       #
        'threads' : 2, 'kernelseeds' : [43210987, 394780234],      # array with one element per thread
        #'threads' : 1, 'kernelseeds' : 43210987,       # array with one element per thread
        # seed for random generator used when building connections
        'connectseed' : 12345789,  # seed for random generator(s) used during simulation
        'now' : datetime.datetime.now().isoformat() # the date in ISO 8601 format to avoid overriding old simulations
    }

    # retinal neurons parameters
    params['parameters_gc'] = {'Theta':-57.0, 'Vreset': -70.0,'Vinit': -63.0, 'TauR': 0.5, 'gL':28.95,
    'C':289.5, 'V_reversal_E': 0.0, 'V_reversal_I': -75.0, 'TauSyn_E':1.5,
    'TauSyn_I': 10.0, 'V_reversal_sfa': -70.0, 'q_sfa': 0., #14.48,
    'Tau_sfa':110.0, 'V_reversal_relref': -70.0, 'q_relref': 3214.0,
    'Tau_relref': 1.97,'python':True}
    params['u'] = params['parameters_gc']['Vinit'] + numpy.random.rand(N,N)* (params['parameters_gc']['Theta'] - params['parameters_gc']['Vreset'])

    return params

def retina_fiber():

    """
    Parameters for the retina to get just one fiber

    """
    params = retina_default()
    params.update({'description' : 'fiber retina','N': 1})
    #N = params['N']
    #params.update({'amplitude' : numpy.ones((N, N))})
    return params

def retina_debug():

    """
    Debug parameters for the retina

    """
    params = retina_default()
    params.update({'description' : 'debug retina','N': 8})
    return params


def run_retina(params):#,url,branch):
    """
    params are the parameters to use
    url,branch the url and branch where we store data

    """
    tmpdir = tempfile.mkdtemp()
    # === Build the network ========================================================
    print "Setting up simulation"
    pyNN.Timer.start() # start timer on construction
    pyNN.setup(timestep=params['dt'],max_delay=params['syn_delay'])
    pyNN.pynest.setDict([0],{'threads' : params['threads']})
    pyNN.setRNGseeds(params['kernelseeds'])

    N = params['N']
    #dc_generator
    phr_ON  = pyNN.Population((N,N),'dc_generator')
    phr_OFF  = pyNN.Population((N,N),'dc_generator')
    noise_ON = pyNN.Population((N,N),'noise_generator',{'mean':0.,'std':params['noise_std']})  # TODO LUP : justify this noise model
    noise_OFF = pyNN.Population((N,N),'noise_generator',{'mean':0.,'std':params['noise_std']})

    phr_ON.set({ 'start' : params['simtime']/4, 'stop' : params['simtime']/4*3})
    phr_ON.tset('amplitude', params['amplitude'] *  params['snr'])
    phr_OFF.set({ 'start' : params['simtime']/4, 'stop' : params['simtime']/4*3})
    phr_OFF.tset('amplitude', - params['amplitude']  * params['snr'])

    # target ON and OFF populations (what about tridimensional Population?)
    out_ON = pyNN.Population((N,N) ,'iaf_sfa_neuron',params['parameters_gc']) # IF_curr_alpha)#
    out_OFF = pyNN.Population((N,N) ,'iaf_sfa_neuron',params['parameters_gc']) # IF_curr_alpha)#

    #  Connecting the network
    retina_proj_ON = pyNN.Projection(phr_ON, out_ON, 'oneToOne')
    retina_proj_ON.setWeights(params['weight']) #*ones((N,N)) )
    retina_proj_OFF = pyNN.Projection(phr_OFF, out_OFF, 'oneToOne')
    retina_proj_OFF.setWeights(params['weight']) #*ones((N,N)) )

    noise_proj_ON = pyNN.Projection(noise_ON, out_ON, 'oneToOne')
    noise_proj_ON.setWeights(params['weight']) #*ones((N,N)) )
    noise_proj_OFF = pyNN.Projection(noise_OFF, out_OFF, 'oneToOne') # implication of ON and OFF having the same noise input?
    noise_proj_OFF.setWeights(params['weight']) #*ones((N,N)) )

    out_ON_filename=os.path.join(tmpdir,'out_on.gdf')
    out_OFF_filename=os.path.join(tmpdir,'out_off.gdf')
    out_ON.record()
    out_OFF.record()

    # reads out time used for building
    buildCPUTime= pyNN.Timer.elapsedTime()

    # === Run simulation ===========================================================
    print "Running simulation"

    pyNN.Timer.start() # start timer on construction
    pyNN.run(params['simtime'])
    simCPUTime = pyNN.Timer.elapsedTime()

    # TODO LUP use something like "for pop in [phr, out]" ?
    out_ON.printSpikes(out_ON_filename)
    out_OFF.printSpikes(out_OFF_filename)

    # TODO LUP  get out_ON_DATA on a 2D grid independantly of out_ON.cell.astype(int)
    out_ON_DATA = tmpfile2spikelist(out_ON_filename,params['dt'])
    out_OFF_DATA = tmpfile2spikelist(out_OFF_filename,params['dt'])

    print "\nRetina Network Simulation:"
    print(params['description'])
    print "Number of Neurons  : ", N**2
    print "Output rate  (ON) : ", out_ON.meanSpikeCount(), "spikes/neuron in ", params['simtime'], "ms"
    print "Output rate (OFF)   : ", out_OFF.meanSpikeCount(), "spikes/neuron in ",params['simtime'], "ms"
    print "Build time         : ", buildCPUTime, "s"
    print "Simulation time    : ", simCPUTime, "s"

    return out_ON_DATA,out_OFF_DATA

if __name__ == '__main__':

    #retina_default(url)
    params=retina_debug()
    params.update({'amplitude' : .10*numpy.ones((params['N'],params['N']))})
    out_ON_DATA, out_OFF_DATA=run_retina(params)
    import pylab
    out_ON_DATA=numpy.array(out_ON_DATA)
    spike_time=numpy.cumsum(out_ON_DATA[:,0]) * params['dt']
    neuron_id=out_ON_DATA[:,1]
    pylab.plot(spike_time,neuron_id,'.r')
    pylab.axis([0, params['simtime'], 0, params['N']**2 -1])
    out_OFF_DATA=numpy.array(out_OFF_DATA)
    spike_time=numpy.cumsum(out_OFF_DATA[:,0]) * params['dt']
    neuron_id=out_OFF_DATA[:,1]
    pylab.plot(spike_time,neuron_id,'.b')
    pylab.axis('tight')
    print spikelist2spikematrix(out_ON_DATA, params['N'], params['simtime']/params['dt'], params['dt'])
