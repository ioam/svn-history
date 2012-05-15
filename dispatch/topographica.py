import os, sys, re, pickle, imp, shutil, time
import topo 
import param
from dispatch import TaskCommand
from dispatch import TaskLauncher
from dispatch import review_and_launch


class topo_param_formatter(param.ParameterizedFunction):
   ''' This class is closely related to the param_formatter class in
       topo/command/__init__.py.  Like that default class, it formats parameters
       as a string for use in a directory name.  Unlike that default, it does
       not use the parameters repr directly but instead their commandline
       representation as returned by the TaskSpecifier.

   Unlike the default param_formatter, this version has several important
   advantages:
   - It allows for a custom separator and an optional trunctation
     length for values.  
   - It removes the need to import param.misc.OrderedDict in
     the command string to specify map.  
   - Parameters are sorted from slowest to fastest varying or 
     (optionally) alphanumerically.  
   - Does not support custom ordering but does still support abbreviations.
   - It formats a string for the parameters that vary by default (can be toggled)
   - Most importantly, it formats values *exactly* as they appear in a command.  For example, a value
     specified as 6.00 on the commandline remains this way and is never represented to higher
     precision or with floating point error.
   '''

   abbreviations = param.Dict(default={}, doc='''
       A dictionary of abbreviations to use of type {<key>:<abbrev>}. 
       If a specifier key has an entry in the dictionary, the abbreviation is used.
       Useful for shortening long parameter names in the directory structure.''')

   alphanumeric_sort = param.Boolean(default=False, doc='''
        Whether to sort the (possibly abbreviated) keys alphabetically or not. 
        By default, keys are ordered from slowest varying to fastest varying 
        provided this information is available from the TaskSpecifier.''')

   format_constant_keys = param.Boolean(default=False, doc=''' 
        Whether or not to format the parameters that are known to be constant across batches.''')

   truncation_limit = param.Number(default=None, allow_None=True, doc= ''' 
        If None, no truncation is performed, otherwise specifies the maximum
        length of any given specification value. ''')

   separator = param.String(default=',', doc=""" 
          The separator to use between <key>=<value> pairs.""")


   def __call__(self, constant_keys, varying_keys, spec):
      
      if self.format_constant_keys: ordering = constant_keys + varying_keys
      else:                         ordering = varying_keys

      if self.alphanumeric_sort: ordering = sorted(ordering)
      abbreved = [ (self.abbreviations.get(k,k), spec[k]) for k in ordering]
      return self.separator.join(['%s=%s' % (k, v[:self.truncation_limit]) for (k,v) in abbreved])
      

class TopoRunBatchCommand(TaskCommand):
   """ TopoRunBatchCommand is designed to to format task specifications into
       Topographica run_batch tasks in a way that should be flexible enough to
       be used generally. Note that Topographica is invoked with the -a flag so
       all of topo.command is imported.

       Though some of the parameters required appear to duplicate those in
       run_batch, they are necessary to ensure some basic consistency in the use
       of run_batch between tasks. This TaskCommand class constrains -all- the
       options for run_batch with the exception of 'times' which is free to vary
       as part of the task specification. This is allowed as you may wish to
       change the times at which the analysis function is invoked across
       batches.

       This command is queuable with both the queue and specify methods
       implemented. As necessary, specifications are generated in the
       'specifications' subdirectory of the root directory.
       """

   analysis = param.ObjectSelector(default='default', objects=['default', 'TopoRunBatchAnalysis', 'custom'],
                                   constant=True, doc="""
              The type of analysis to use with run_batch. The options are
              'default' which runs the default run_batch analysis function,
              'TopoRunBatchAnalysis' which use the more sophisticated picklable
              analysis function and custom which requires the analysis callable
              to be created in the run_batch namespace via the custom_prelude.""")

   custom_prelude = param.List(default=[], constant=True, doc="""
          Lines of code to be executed prior run_batch invocation to introduce
          any desired classes/object into the namespace. This must be used to
          create the 'analysis' callable if a custom analysis option is selected.""")

   name_time_format = param.String(default='%Y%m%d%H%M', doc=""" 
         The timestamp format for directories created by run_batch in python
         datetime format.""")

   max_name_length= param.Number(default=200, doc="Equivalent to the run_batch parameter of same name.")
   
   snapshot = param.Boolean(default=True, doc="Equivalent to the run_batch parameter of same name.")

   vc_info = param.Boolean(default=True, doc="Equivalent to the run_batch parameter of same name.")
   
   save_global_params = param.Boolean(default=True, doc="Equivalent to the run_batch parameter of same name.")

   param_formatter = param.Callable(topo_param_formatter.instance(),doc="""
        If None, defaults to normal run_batch formatting.""")

   def __init__(self, tyfile, analysis='default', custom_prelude=[]):

      if (analysis == 'custom') and (custom_prelude==[]):
         raise Exception, 'Please specify custom_prelude to use custom analysis!'

      super(TopoRunBatchCommand, self).__init__(analysis=analysis,
                                                custom_prelude=custom_prelude)

      self.tyfile = os.path.abspath(tyfile)
      assert os.path.exists(self.tyfile), "Tyfile doesn't exist! Cannot proceed."

      self._prelude = []
      if self.analysis=='TopoRunBatchAnalysis':
         self._prelude = ['from dispatch.topographica import TopoRunBatchAnalysis']
      if self.analysis=='default':
         self._prelude = ["analysis = default_analysis_function"] 
               
      self._prelude = self.custom_prelude + self._prelude
      
   def queue(self,tid, info):
      ''' Uses load_kwargs helper function in topo.command.misc to get the
      run_batch settings from the specifications directory. '''
      spec_path = os.path.join(info['root_directory'], 'specifications') 
      spec_file_path = os.path.join(spec_path, 't%s.spec' % tid) 
      run_batch_cmd = "run_batch('%s',**load_kwargs('%s',globals(),locals()))" % (self.tyfile,spec_file_path)

      prelude = self._prelude[:]
      if self.analysis=='TopoRunBatchAnalysis':
         prelude += ["analysis=TopoRunBatchAnalysis.load(%s)" % repr(info['root_directory'])]
         prelude += ["analysis.current_tid = %s" % tid]

      return  [self.executable, '-a', '-c', ';'.join(prelude+[run_batch_cmd])]

   def specify(self, spec, tid, info):
      ''' Writes the specification as a Python dictionary to file (to the
      specifications subdirectory of root directory) as required by the
      load_kwargs helper method in topo.misc.command.'''

      spec_path = os.path.join(info['root_directory'], 'specifications')
      spec_file_path = os.path.join(spec_path, 't%d.spec' % tid)
      if not os.path.exists(spec_path): os.mkdir(spec_path)
   
      spec_file = open(spec_file_path,'w')
      kwarg_opts = self._run_batch_kwargs(spec, tid, info)
      allopts = dict(spec,**kwarg_opts) # Override run_batch keys if (mistakenly) provided.
      
      keywords = ',\n'.join(['%s=%s' % (k, allopts[k]) for k in 
                             sorted(kwarg_opts.keys()) + sorted(spec.keys())])
      spec_file.write('dict(\n%s\n)' % keywords); spec_file.close()

   def _run_batch_kwargs(self, spec, tid, info):
      ''' Defines the keywords accepted by run_batch and so specifies run_batch behaviour. '''
      options = {'name_time_format':   repr(self.name_time_format),
                 'max_name_length':    self.max_name_length, 
                 'snapshot':           self.snapshot,
                 'vc_info':            self.vc_info, 
                 'save_global_params': self.save_global_params}

      if info['batch_tag']=='': dirname_prefix = info['batch_name']
      else:                     dirname_prefix = info['batch_name'] + ('[%s]' % info['batch_tag'])

      # Settings using information from launcher
      derived_options = {'output_directory':repr(info['root_directory']),
                         'dirname_prefix':  repr(dirname_prefix),
                         'tag':             repr('t%s_' % tid)}   

      # Use fixed timestamp argument to run_batch if available.
      if info['timestamp'] is not None: derived_options['timestamp'] = info['timestamp']
      derived_options['analysis_fn'] = 'analysis'

      # Use the specified param_formatter (if desired) to create lambda in run_batch
      if self.param_formatter is not None:
         dir_format = self.param_formatter(info['constant_keys'], info['varying_keys'], spec)
         derived_options['dirname_params_filter'] =  'lambda p: %s' % repr(dir_format)

      return dict(options.items() + derived_options.items()) 

   def __call__(self, spec, tid=None, info={}): 
      """ Returns a Popen argument list to invoke Topographica and execute
      run_batch with all options appropriately set (in alphabetical
      order). Keywords that are not run_batch options are also in alphabetical
      order at the end of the keyword list"""

      kwarg_opts= self._run_batch_kwargs(spec, tid, info)      
      allopts = dict(spec,**kwarg_opts) # Override spec values if mistakenly included.

      prelude = self._prelude[:]
      if self.analysis=='TopoRunBatchAnalysis':
         prelude += ["analysis=TopoRunBatchAnalysis.load(%s)" % repr(info['root_directory'])]
         prelude += ["analysis.current_tid = %s" % tid]

      keywords = ', '.join(['%s=%s' % (k,allopts[k]) for k in sorted(kwarg_opts.keys())+sorted(spec.keys())])
      run_batch_list = prelude + ["run_batch(%s,%s)" % (repr(self.tyfile), keywords)]
      return  [self.executable, '-a', '-c',  '; '.join(run_batch_list)]



class TopoRunBatchAnalysis(param.Parameterized):
   """ This analysis class is a generalization of the normal analysis functions
   use in Topographica's run_batch command. It allows you to factor out and
   document steps in your analysis, offers a standard mechanism to collate data
   returned from map functions across multiple simulations and allows you to
   define a metric function for use with dynamic TaskSpecifiers
   (eg. Hillclimbing). Here are the types of operation you can define:

   Map functions
   -------------
   Functions called for their side-effects. Eg. saving plotgroups, orientation
   maps etc.
   
   Map-reduce operations 
   ---------------------
   Allows you to collect and process dataacross simulations. The map
   component generates the data per simulation while the reduce function
   collapse this data (eg. plotting a variable acrosssimulations).

   Metric function 
   ---------------
   Provides the TaskSpecifier feedback (eg. for automated parameter
   search). There can only be one metric function.

   It works by restoring the analysis object from a pickle file *within* the
   run_batch context, dynamically importing the user-defined functions from the
   launch script and then executing them as specified.  Dynamic import is
   necessary as pickles do not store code and the referenced user-functions need
   to exist before execution. To create the initial pickle file, you need to
   call the save() method once all map, map-reduce and metric functions are
   defined. Note that this class is a callable (no arguments) as it is designed
   to interface with run_batch like a normal analysis function.
   """

   current_tid = param.Integer(default=None, allow_None=True, doc='''
         The task identifier for the current task. This needs to be set in the
         run_batch context in order to ensure the correct naming convention for
         pickles generated by the map functions (for later reduction).''')

   @classmethod
   def load(cls, root_directory):
      ''' Classmethod used to load the analysis callable in a Topographica run_batch context.
          Loads the analysisfn.pickle file from the specified root directory.'''
      path = os.path.join(root_directory, 'analysisfn.pickle')
      with open(path,'rb') as p:  return pickle.load(p) 

   @classmethod
   def reduce_batch(cls, root_directory):
      ''' Classmethod used to load the analysis object then apply all reductions.
          Loads the analysisfn.pickle file from the specified root directory.'''
      path = os.path.join(root_directory, 'analysisfn.pickle')
      with open(path,'rb') as p:  
         analysis_obj = pickle.load(p)
         return analysis_obj.reduce

   def __init__(self):
      self.source_path = None; self.root_directory = None
      self.maps = []; self.map_reduces = []; self.metric = None

   def save(self):
      ''' The method to save the initial pickle file once the map, reduce and
      metric functions are defined. Must be called before launch and saves
      the object as analysisfn.pickle file from the specified root
      directory.'''
      if None in [self.source_path, self.root_directory]: 
         print "Please set the source_path and the root_directory before saving"
      if not os.path.isdir(self.root_directory): os.makedirs(self.root_directory) 
      path = os.path.join(self.root_directory, 'analysisfn.pickle') 
      with open(path,'wb') as p: pickle.dump(self, p)

   def set_metric(self, metric_fn, description):
      ''' Used to supply a metric function (eg. for hillclimbing) along with
      appropriate description.'''
      self.metric = { 'metric_fn':metric_fn.__name__, 'description':description}

   def add_map_fn(self, map_fn, description):
      ''' Used to supply an additional map function (called for its side-effects
      only) along with appropriate description.'''
      self.maps.append({'map_fn':map_fn.__name__, 'description':description})

   def add_map_reduce_fn(self, map_fn, reduce_fn, description):
      ''' Used to specify a map-reduce operation whereby the map_fn returns data
      from a given simulation which the reduce_fn collates across all
      simulations once the batch is complete. An appropriate description also
      needs to be supplied.'''
      self.map_reduces.append({'map_fn':map_fn.__name__, 
                               'reduce_fn':reduce_fn.__name__, 
                               'description':description})

   def pickle_data(self, subdir, fname, data): 
      ''' Helper method to pickle the given data to a file of the given name in
          the given subdirectory on the appropriate path'''
      pickle_dir = os.path.join(self.root_directory, subdir)
      if not os.path.isdir(pickle_dir): os.makedirs(pickle_dir)
      with open(os.path.join(self.root_directory, subdir, fname),'wb') as p: pickle.dump(data, p)

   def __call__(self):
      ''' The call that occurs in run_batch. Calls all the defined map
          functions, pickles the data returned from the map component of
          map-reductions and computes and pickles the metric. The pickled data
          is a tuple that includes the topographica simulation time at which the
          data was generated as run_batch typically applies the analysis
          functions at multiple simulation times.

          The pickles for map-reductions are stored in the root_directory under
          a subdirectory of the supplied map function name. The metric pickles
          are stored in the metrics folder of the root directory as required by
          all TaskLaunchers.'''

      if self.source_path is None:
         print "Source path was not set! Running default analysis function instead."
         topo.command.default_analysis_function(); return

      if (self.maps == []) and (self.map_reduces ==[]): default_analysis_function(); return

      module = imp.load_source('', self.source_path)
      topo_time = topo.sim.time()

      mapfns = [getattr(module, mapdict['map_fn']) for mapdict in self.maps]
      for mapfn in mapfns: mapfn() # Applying map functions in order

      rmapfns = [getattr(module, map_reduce['map_fn']) for map_reduce in self.map_reduces]
      for (rmapfn, info) in zip(rmapfns,self.map_reduces):
         fname = '%s@time=%s[%d]' % (info['map_fn'], str(topo_time), self.current_tid)
         self.pickle_data(info['map_fn'], fname, (topo_time, rmapfn())) # Pickle maps of map-reduces

      if self.metric is not None:  
         fname = 'metric-%d-time=%s' % (self.current_tid, str(topo_time))
         metricfn = getattr(module, metric['metric_fn'])
         self.pickle_data('metrics', fname, (self.current_tid, topo_time, metricfn())) # Pickle metric

   def reduce(self, spec_log, root_directory):
      ''' Method to apply all defined map-reduces. For each map function,
      locates all the pickles in the corresponding subfolder and matches the
      stored data to the tid in the filename. The data and Topographica
      simulation times are extracted and passed the the appropriate reduce
      function.'''
      reduces = [map_red['reduce_fn'] for map_red in self.map_reduces]
      reduce_maps = [map_red['map_fn'] for map_red in self.map_reduces]

      if self.source_path:  module = imp.load_source('', self.source_path)
      else:                 return

      reduce_fns = [getattr(module, rname) for rname in reduces]
      # Mapping is a dictionary of form {<map_name>:<reduce_function>}
      reduce_mapping = dict([(map_name, rfn) for (map_name, rfn) in zip(reduce_maps, reduce_fns)])
      
      for map_name in reduce_mapping:
         candidate_files = os.listdir(os.path.join(root_directory, map_name))
         tid_pattern = map_name + '.*\[(?P<tid>\d+)\]'
         regexp_matches = [(cf, re.match(tid_pattern,cf)) for cf in candidate_files]
         tid_matches = [(cf, int(m.groupdict()['tid'])) for (cf,m) in regexp_matches if (m is not None)]
         matches, tids = zip(*tid_matches)

         pickle_paths = [os.path.join(root_directory, map_name, f) for f in matches]
         unpickled = [pickle.load(open(p,'rb')) for p in pickle_paths]
         topo_times, map_data = zip(*unpickled)
         annotated = [ (data, t, dict(spec_log)[tid]) for (data, t, tid)  in zip(map_data, topo_times, tids)]
         reduce_mapping[map_name](annotated, root_directory)
         
   def __str__(self):
      ''' The printed representation of the analysis object. '''
      strList = []
      for fn_info in self.maps:
         strList += ["Map function '%(map_fn)s': %(description)s" % fn_info]
      for fn_info in self.map_reduces:
         strList += ["Map/Reduce function '%(map_fn)s': %(description)s" % fn_info]
      if strList == []: strList = ['Default TopoRunBatchAnalysis']
      if self.metric is not None: strList += ['Metric function %(metric_fn)s' % self.metric]
      return "\n".join(strList)

####################
# Launch Decorator #
####################

class topo_batch_analysis(review_and_launch):
   ''' Decorator designed to codify the correct workflow for using Topographica
    with run_batch. It coordinates the settings of the task launcher and the
    analysis object ensuring that a TopoRunBatchAnalysis is being used correctly
    with a TopoRunBatchCommand object. 

    In order to ensure the pickled TopoRunBatchAnalysis object is in the
    appropriate root directory, this decorator takes the current timestamp to
    determine the root directory before launch.
    '''

   def review_analysis(self, task_launcher, task_command, batch_analysis):
      
      if not isinstance(task_command,TopoRunBatchCommand):
         print "Command object must be a TopoRunBatchCommand. Cannot continue."
         
      print "\n" + self.section('Batch Analysis')
      print "Source path: %s" % self.script_path
      print "Analysis Info:\n%s\n" %  batch_analysis

   def setup_analysis(self, task_launcher, batch_analysis):
      ''' Takes the current timestamp, uses it to determine the root directory,
      configures the analysis object appropriately, saved it and finally sets
      up the launcher's exit callable. '''
      timestamp = tuple(time.localtime())
      root_directory = param.normalize_path(task_launcher.root_directory_name(timestamp))
      batch_analysis.root_directory = root_directory
      batch_analysis.source_path = self.script_path
      batch_analysis.save()
      task_launcher.exit_callable = TopoRunBatchAnalysis.reduce_batch(root_directory)
        
   def __call__(self,f):

      if f.__module__ == '__main__':

         commandline_used = self.launcher_class.commandline(sys.argv)
         if commandline_used: sys.exit()
         
         # Must be set in __main__ only and not on import of user-define analysis functions.
         param.normalize_path.prefix = self.output_directory          
          
         return_value = f() 
         try:  (task_launcher, batch_analysis) = return_value
         except: 
            print "Function must return a tuple (TaskLauncher, batch_analysis)"; return

         if not isinstance(task_launcher, TaskLauncher): 
            print "First element of returned tuple is not a Tasklauncher."; return

         if not isinstance(batch_analysis, TopoRunBatchAnalysis): 
            print "Second element of returned tuple if not a TopoRunBatchAnalysis object"; return

         if not isinstance(task_launcher.task_command, TopoRunBatchCommand):
            print "TaskCommand specified in the launcher is not a TopoRunBatchCommand object."; return

         if not (task_launcher.task_command.analysis =='TopoRunBatchAnalysis'):
            print "TaskCommand must be using the 'TopoRunBatchAnalysis' analysis type"; return

          # Finding and setting the script path (needed for TaskLauncher that use the commandline)
         self.script_path = os.path.join(os.getcwd(), sys.argv[-1])
         if not os.path.exists(self.script_path):
            print "Cannot extract script path: %s" % self.script_path; sys.exit()

         task_launcher.script_path = self.script_path

         if self.review:
            task_specifier = task_launcher.task_specifier
            task_command = task_launcher.task_command

            try: self.review_analysis(task_launcher, task_command, batch_analysis)
            except AssertionError: return

            self.review_task_launcher(task_launcher,task_command)
            self.review_task_specification(task_specifier)
            self.review_task_command(task_command,task_specifier, task_launcher)
                        
            response = self.input_options(['y','n'], 'Execute?')
            if response == 'y':  
               self.setup_analysis(task_launcher, batch_analysis)
               task_launcher.dispatch()
         else: 
            self.setup_analysis(task_launcher, batch_analysis)
            task_launcher.dispatch()
            return f


