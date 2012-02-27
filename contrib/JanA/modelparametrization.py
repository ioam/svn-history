import matplotlib.gridspec as gridspec
from topo.command.basic import wipe_out_activity, clear_event_queue
import topo 
import pylab

class ModelRecording(object):
      """
      
      sheets            - list of sheets of the model that need to be reset 
      retina            - retina name of the model
      reset_homeo       - HACKY
                          if reset_homeo != None it will reset homeostatic 
                          plasticity. reset_homeo tells the order of the homeo transfer function
                          in the list of .output_fns
      sheets_to_record  - sheets that we want to record
      sslice            - the slice of activity and projection activity that are to be recorded (None is all)
      """
          
      def __init__(self, sheets, retina,  sheets_to_record=None, sslice=None, reset_homeo=None):
          self.sheets = sheets
          self.retina = retina  
          self.reset_homeo = reset_homeo
          self.sslice = sslice
          self.sheets_to_record = sheets_to_record
                   
      def pre_test(self):
          self.plastic = {}
          for s in self.sheets:
              self.plastic[s] = topo.sim[s].plastic
              topo.sim[s].plastic = False
          
          wipe_out_activity()
          clear_event_queue()
          topo.sim.state_push()     
          
          # HACKY
          if self.reset_homeo != None:  
            for s in self.sheets:
                topo.sim[s].output_fns[self.reset_homeo].old_a*=0
          
      def post_test(self):
          topo.sim.state_pop()        
          
          for s in self.sheets:
              topo.sim[s].plastic = self.plastic[s]
      
      def present_stimulus_sequence(self,interval,stimuli):
          
            self.records = {}          
            ip = topo.sim[self.retina].input_generator  
            
            if stimuli!= None:
                for s in stimuli:
                    self.pre_test()
                    topo.sim['Retina'].set_input_generator(s)
                    topo.sim.run(interval)           
                    self.record()
                    self.post_test()
            else:
                    self.pre_test()
                    topo.sim.run(interval)           
                    self.record()
                    self.post_test()                
            
            topo.sim[self.retina].set_input_generator(ip)
    
      def record(self):
          if self.sheets_to_record == None:
              sh = self.sheets
          else:
              sh = self.sheets_to_record
          
          for s in sh:      
            if not self.records.has_key(s):
               self.records[s] = {}
            
            if not self.records[s].has_key('activity'):
                self.records[s]['activity'] = []
                
            if self.sslice == None: 
                self.records[s]["activity"].append(topo.sim[s].activity.copy())
            else:
                self.records[s]["activity"].append(topo.sim[s].activity[self.sslice[0],self.sslice[1]].copy())
            
            if not self.records[s].has_key('projections'):
               self.records[s]['projections'] = {} 
            
            for p in topo.sim[s].projections().keys():
                if not self.records[s]['projections'].has_key(p):
                    self.records[s]['projections'][p] = []
                if self.sslice == None: 
                    self.records[s]['projections'][p].append(topo.sim[s].projections()[p].activity.copy())
                else:
                    self.records[s]['projections'][p].append(topo.sim[s].projections()[p].activity[self.sslice[0],self.sslice[1]].copy())
      
      def plot_activity(self,gs,index):
          """
          Plots the activities in all layers to the stimulus number index in the list of stimuli that were presented
          """
          gs = gridspec.GridSpecFromSubplotSpec(1, len(self.records.keys()), subplot_spec=gs)  
          for i,s in enumerate(self.records.keys()):
              print i
              ax = pylab.subplot(gs[0,i])
              ax.imshow(self.records[s]['activity'][index],cmap='gray') 
            
                

class ModelParametrization(object):
    """
    This class can run iteratively all combinations of parameter_values corresponding 
    to parameters and for each such combination it executes the model_measurment_function
    
    parameters - the list of parameters that should be scanned
    parameter_values - list of lists. The outer list len is the same as len of parameters
                       each sublist contains values that should be explored for the given parameter
                
    model_measurement_function - the function that when called will perform the measurement of the model 
    plotting_function          - function that plots the results after each measurement.  
    directory                  - where to save results
    """
    def __init__(self,parameters,parameter_values,model_measurement_function,plotting_function,plotting_params,directory):
        self.parameters = parameters
        self.parameter_values = parameter_values
        self.plotting_function = plotting_function
        self.plotting_params = plotting_params
        self.model_measurement_function = model_measurement_function
        self.directory = directory
        self.init_vals = [eval(p) for p in self.parameters]
        
    
    def go(self,initial_run=False):
        if initial_run:
           topo.sim.run(1.0) 
            
        self.run_combinations(self.parameter_values)
        
        for p,iv in zip(self.parameters, self.init_vals):
            exec(p + '= iv')
    
    def set_params(self,values):
        for p,v in zip(self.parameters,values):
            exec(p + ' = v')
    
    @staticmethod
    def set_parameters(parameters,values):
        """
        Helper function, that makes it easy to set simulation with a particular combination of parameter values
        """
        for p,v in zip(parameters,values):
            exec(p + ' = v')
            
    def execute_model_measurement(self,params):
        self.set_params(params)
        self.model_measurement_function()
        
        self.fig = pylab.figure(facecolor='w')
        gs = gridspec.GridSpec(1, 1)
        gs.update(left=0.05, right=0.95, top=0.95, bottom=0.05)
        self.plotting_function(gs[0,0],**self.plotting_params)
        
        st = ""
        for p in params:
            st = st + ' ' +  str(p)
        
        pylab.savefig(self.directory + '/' +  st + '.png');
        
    
    def _run_combinations_rec(self, param, params, index):
        if(len(params) == index):
            self.execute_model_measurement(param)
            return
        a = params[index]
        for p in a:
            new_param = param + [p]
            self._run_combinations_rec(new_param, params, index + 1)

    def run_combinations(self, params):
        """
            this function runs function func with all combinations of params defined in the array params, eg.
            params = [[1,2,3],[1,2,3]...]
        """
        run_combinations_counter = 0
        self._run_combinations_rec([], params, 0)
            


# various plotting functions            
def explore_initial_activity(parameters,parameter_values,sheets,sheets_to_record,retina,reset_homeo,interval,directory):
    mr = ModelRecording(sheets, retina, sheets_to_record = sheets_to_record, reset_homeo = reset_homeo)
    f = lambda : mr.present_stimulus_sequence(interval,None)
    mp = ModelParametrization(parameters,parameter_values,f,mr.plot_activity,{'index' : 0},directory)
    mp.go(initial_run=True)
