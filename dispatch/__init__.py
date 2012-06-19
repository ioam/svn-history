import os, sys, copy, re, glob, json, pickle, fnmatch
import time, pipes, subprocess
import logging

import numpy as np
from itertools import chain, groupby
from collections import defaultdict

import param

# TaskCommands could be called CommandTemplates.
# TaskSpecifiers could be called ArgumentSpecifiers
# TaskLaunchers could be called BatchLauncher  [renamed to Launcher for now]
# task decorators could be called workflows (launch workflows?).  dispatch.

#================#
# TaskSpecifiers #
#================#

"""
TaskSpecifiers are intended to be clear, succinct and composable way of
specifying the large parameter sets. High-dimensional parameter sets are typical
of large-scale scientific models and can make working with such models
difficult. Using TaskSpecifiers, you can document how the parameters of your
model change across runs without having to handle any flat representations
explicitly.

TaskSpecifiers are designed to allow parameters to be varied on the commandline
for visualisation, analysis or parameter search and are based on the string
representations that invokes the target process at the commandline. Users can
specify parameter ranges, Cartesian products or dynamic parameter search
strategies (such as hillclimbing, bisection optimisation etc) independent of
executable invocation, computational platform and environment.

To help enforce a declarative style, public parameters are declared constant
after initialization and should not be mutated. Instead, TaskSpecifiers objects
need to be declared correctly when instantiated.

Internally, the core of a TaskSpecifier is a Python iterator which returns a
list of dictionaries on each call to next(). Each item in the dictionaries is
labelled value where a parameter name keys is associated to its corresponding
string representation. When used in conjunction with a TaskCommand, these
dictionaries allow commands to built in a flexible manner.
"""



class TaskSpecifier(param.Parameterized):
    """
    The base class for all TaskSpecifiers. On each iteration, a Taskspecifier
    can returns a list of dictionaries (parameter specifications). The keys of
    each specification are the parameter names while the string values specify
    the values of the parameter that can be later built into commandline
    strings.

    When dynamic=False, StopIteration should be raised after the first
    iteration. This is because no runtime data is necessary to determine the
    specifications so they should all be returned all in one go.

    For some search strategies (eg. hillclimbing), feedback is needed at runtime
    before the next sample of the parameter space is taken. In these cases,
    dynamic=True and the state of the TaskSpecifier is updated between
    iterations using data generated at runtime via the update() method.

    Even if the values in the specifications cannot be known till runtime
    (ie. dynamic=True), it can be extremely useful to know the *number* of
    specifications are expected on future iterations. Therefore, if a dynamic
    TaskSpecifier always follows a particular pattern of operation, the
    schedule() method should be implemented accordingly. This can allows
    placeholder jobs to be reserved (eg. on a compute cluster).

    Note that the update and schedule methods are only ever used in dynamic
    TaskSpecifiers and do not need to be implemented if dynamic=False.

    The varying_keys and constant_keys methods help make a distinction between
    the parameters we wish to manipulate between runs (informative) and constant
    settings (less informative).
    """
    __abstract=True

    dynamic = param.Boolean(default=False, constant=True, doc='''
            Flag to indicate whether the TaskSpecifier needs to have its state
            updated via the update() method between iterations (ie. between
            calls to the next method). If all the specifications cannot be known
            ahead of time (eg. parameter search), dynamic must be set to True.''')

    rationale = param.String(default='',  allow_None=True, doc='''
      Allows documentation metadata to be associated with each TaskSpecifier.
      This allows a justification to be given of why the given TaskSpecifier is
      to used and why the parameters chosen are suitable for the task at hand.
      Note that rationale is one of the few TaskSpecifier parameters not
      declared constant''')

    fp_precision = param.Integer(default=4,  constant=True, doc='''
         The floating point precision to use for floating point values.  Unlike
         other basic Python types, floats need care with their representation (on
         the commandline) as using repr() is not sufficient control.''')

    def __init__(self, rationale='', dynamic=False, **params):
        super(TaskSpecifier,self).__init__(dynamic=dynamic, **params)

        if rationale != '': rationale = "\n[ %s ]\n%s" % (repr(self), rationale)
        self.rationale += rationale

    def __iter__(self): return self

    def formatter(self, obj):
        " Helper function that helps format floating point values appropriately "
        if type(obj) == float: return ('%%0.%df' % self.fp_precision) % obj
        return repr(obj)

    def constant_keys(self):
        """
        Returns the list of parameter names whose values vary as the
        TaskSpecifer is iterated.  Note that constant_keys() + varying_keys()
        should cover the entire set of keys.
        """
        raise NotImplementedError

    def varying_keys(self):
        """
        Returns the list of parameters whose values are constant as the
        TaskSpecifer is iterated.  Whenever it is possible, keys should be
        sorted from slowest varying to fastest varying and sorted
        alphanumerically within groups varying at the same rate.
        """
        raise NotImplementedError

    def next(self):
        """
        Called to get a list of specifications: dictionaries with parameter name
        keys and string values.
        """
        raise StopIteration

    def update(self, data):
        """
        Called to update the state of the iterator when dynamic= True.
        Typically this methods is receiving metric values generated by the
        previous set of tasks in order to determine the next desired point in
        the parameter space. If the update fails or data is None, StopIteration
        should be raised.
        """
        raise NotImplementedError

    def schedule(self):
        """
        Specifies the expected number of specifications that will be returned on
        future iterations. This is simply a list of integers specifying the
        number of specifications that will be returned on each call to
        next. Only invoked if dynamic=True and returns None if scheduling is not
        possible.

        N.B: If dynamic=False, schedule := [len(specs) for specs in  static_task_specifier]
        """
        raise NotImplementedError

    def copy(self):
        """
        Convenience method to allow the TaskSpecifiers to be inspected without
        exhausting it.
        """
        return copy.deepcopy(self)

    def _collect_by_key(self,specs):
        """
        Returns a dictionary like object with the lists of values collapsed by
        their respective key. Useful to find varying vs constant keys and to
        find how fast keys vary.
        """
        # Collects key, value tuples as list of lists then flatten using chain
        allkeys = chain.from_iterable([[(k, run[k])  for k in run] for run in specs])
        collection = defaultdict(list)
        for (k,v) in allkeys: collection[k].append(v)
        return collection

    def show(self):
        """
        Convenience method to inspect the available values generated by the
        TaskSpecifier in human-readable format. When not dynamic, allows you to
        easily see how many specifications will be generated.

        When dynamic=True, as many specifications will be listed as possible
        before update is required.
        """

        copied = self.copy()
        enumerated = [el for el in enumerate(copied)]
        for (group_ind, specs) in enumerated:
            if len(enumerated) > 1: print("Group %d" % group_ind)
            ordering = self.constant_keys() + self.varying_keys() # Ordered nicely by varying_keys definition.
            spec_lines = [ ', '.join(['%s=%s' % (k, s[k]) for k in ordering]) for s in specs]
            print('\n'.join([ '%d: %s' % (i,l) for (i,l) in enumerate(spec_lines)]))

        if self.dynamic:
            print('No data available to show remaining output of dynamic TaskSpecifier %s' %
                  self.__class__.__name__)

    def __str__(self):
        """
        TaskSpecifiers are expected to have a succinct representation that is
        human-readable but correctly functions as a proper object representation
        (rationale may be omitted however).
        """
        return repr(self)

    def __add__(self, other):
        """
        Concatenates TaskSpecifiers appropriately based according to whether
        they are dynamic or not. See StaticConcatenate and DynamicConcatenate
        documentation.
        """
        assert not (self.dynamic and other.dynamic), 'Cannot concatenate two dynamic specifiers.'

        if self.dynamic or other.dynamic: return DynamicConcatenate(self,other)
        else:                             return StaticConcatenate(self,other)

    def __mul__(self, other):
        """
        Takes the Cartesian product of the two TaskSpecifiers. See
        StaticCartesianProduct and DynamicCartesianProduct documentation.
        """
        assert not (self.dynamic and other.dynamic), \
            'Cannot take Cartesian product two dynamic specifiers.'

        if self.dynamic or other.dynamic: return DynamicCartesianProduct(self, other)
        else:                             return StaticCartesianProduct(self, other)

    def _cartesian_product(self, first_specs, second_specs):
        """
        Takes the Cartesian product of the specifications. Result will contain N
        specifications where N = len(first_specs) * len(second_specs) and keys
        are merged.  Example: [{'a':1},{'b':2}] * [{'c':3},{'d':4}] =
        [{'a':1,'c':3},{'a':1,'d':4},{'b':2,'c':3},{'b':2,'d':4}]
        """
        return  [ dict(zip(
                          list(s1.keys()) + list(s2.keys()),
                          list(s1.values()) + list(s2.values())
                      ))
                 for s1 in first_specs for s2 in second_specs ]

class StaticSpecs(TaskSpecifier):
    """
    Base class for many important static TaskSpecifiers (dynamic=False) but is
    useful in its own right. Can be constructed from launcher log files and used
    to manipulate output data using Tables.  Accepts the full static
    specifications directly as primary argument and provides all necessary
    mechanisms to collect varying and constant keys, implements next()
    appropriately and has useful support for len().  Note that specs (list of
    dictionaries) are expected to have string keys *and* values.
    """

    def __init__(self, specs, rationale='', fp_precision=4, **kwargs):
        self._specs = list(specs)
        self._exhausted = False
        super(StaticSpecs, self).__init__(dynamic=False,
                                          rationale=rationale,
                                          fp_precision=fp_precision, **kwargs)

    def next(self):
        if self._exhausted: raise StopIteration
        else: self._exhausted=True
        return self._specs

    def _unique(self, sequence, idfun=repr):
        """
        Note: repr() must be implemented properly on all objects. This is
        assumed by all Taskspecifiers objects anyway as values are always
        converted to string representation.
        """
        seen = {}
        return [seen.setdefault(idfun(e),e) for e in sequence
                if idfun(e) not in seen]

    def constant_keys(self):
        collection = self._collect_by_key(self._specs)
        return [k for k in collection if (len(self._unique(collection[k])) == 1)]

    def varying_keys(self):
        collection = self._collect_by_key(self._specs)
        constant_set = set(self.constant_keys())
        unordered_varying = set(collection.keys()).difference(constant_set)
        # Finding out how fast keys are varying
        grouplens = [(len([len(list(y)) for (_,y) in groupby(collection[k])]),k) for k in collection ]
        varying_counts = [ (n,k) for (n,k) in sorted(grouplens) if (k in unordered_varying)]
        # Grouping keys with common frequency alphanumerically (desired behaviour).
        ddict = defaultdict(list)
        for (n,k) in varying_counts: ddict[n].append(k)
        alphagroups = [sorted(ddict[k]) for k in sorted(ddict)]
        return [el for group in alphagroups for el in group]

    def __len__(self): return len(self._specs)

    def __repr__(self):
        return "StaticSpecs(%s)" % (self._specs)


class StaticConcatenate(StaticSpecs):
    """
    StaticConcatenate is the sequential composition of two Static
    Specifiers. The specifier (firstspec + secondspec) will return the
    specifications in firstspec followed by the specification in secondspec.
    """

    def __init__(self, first, second, rationale=''):

        self.first = first
        self.second = second

        rationales = [rationale, first.rationale, second.rationale]
        if rationale == '': rationales = rationales[1:]
        rationale = "\n\n".join([r for r in rationales if (r is not '')])

        super(StaticConcatenate, self).__init__(next(first.copy())
                                              + next(second.copy()),
                                                rationale=rationale)

    def __repr__(self):
        return "(%s + %s)" % (repr(self.first), repr(self.second))

class StaticCartesianProduct(StaticSpecs):
    """
    StaticCartesianProduct is the cartesian product of two Static
    Specifiers. The specifier (firstspec * secondspec) returns the Cartesian
    product of the specifications in firstspec and the specification in
    secondspec (ie. len(firstspec)*len(secondspec) combined specifications.
    """

    def __init__(self, first, second, rationale=''):

        self.first = first
        self.second = second

        rationales = [rationale, first.rationale, second.rationale]
        if rationale == '': rationales = rationales[1:]
        rationale = "\n\n".join([r for r in rationales if (r is not '')])

        specs = self._cartesian_product(next(first), next(second))
        overlap = set(self.first.varying_keys()) &  set(self.second.varying_keys())
        assert overlap == set(), 'Sets of keys cannot overlap between TaskSpecifiers in cartesian product.'

        super(StaticCartesianProduct, self).__init__(specs, rationale=rationale)

    def __repr__(self):   return '(%s * %s)' % (repr(self.first), repr(self.second))


class Spec(StaticSpecs):
    """
    Allows easy instantiation of a single specification using keywords.  Useful
    for instantiating constant settings before a cartesian product.
    """

    def __init__(self, rationale='', fp_precision=4, **kwargs):
        assert kwargs != {}, "Empty specification not allowed."
        specs = [kwargs]
        super(Spec,self).__init__(specs, rationale=rationale,
                                  fp_precision=fp_precision)
        self._specs = [dict([ (k, self.formatter(kwargs[k])) for k in kwargs])]

    def __repr__(self):
        spec = self._specs[0]
        return "Spec(%s)"  % ', '.join(['%s=%s' % (k, spec[k]) for k in spec])


def identityfn(x): return x

class LinearSpecs(StaticSpecs):
    """
    LinearSpecs generates a range of specifications with linearly interpolated
    numeric values to a certain floating-point precision.
    """

    spec_key = param.String(default='default',doc='''
         The key name that is to be linearly varied over a numeric range.''')

    value =  param.Number(default=None, allow_None=True, constant=True, doc='''
         The starting numeric value of the linear interpolation.''')

    end_value = param.Number(default=None, allow_None=True, constant=True, doc='''
         The ending numeric value of the linear interpolation (inclusive).
         If not specified, a LinearSpec ''')

    steps = param.Integer(default=1, constant=True, doc='''
         The number of steps to use in the interpolation. Default is 1.''')

    mapfn = param.Callable(default=identityfn, constant=True)

    def __init__(self, spec_key, value, end_value=None,
                 steps=2, fp_precision=4, mapfn=identityfn, rationale=''):

        formatter = '%%0.%df' % fp_precision
        if end_value is not None:
            values = np.linspace(value, end_value, steps, endpoint=True)
            self._specs = [{spec_key:(formatter % mapfn(val))} for val in values ]
        else:    self._specs = [{spec_key:(formatter % mapfn(value))}]

        self._exhausted = False
        self._pparams = ['end_value', 'steps', 'fp_precision', 'mapfn']

        super(TaskSpecifier, self).__init__(spec_key=spec_key, value=value,
                                            end_value=end_value, steps=steps,
                                            fp_precision=fp_precision, rationale=rationale,
                                            dynamic=False, mapfn=mapfn)

    def __repr__(self):
        modified = dict(self.get_param_values(onlychanged=True))
        pstr = ', '.join(['%s=%s' % (k,self.formatter(modified[k])) for k in self._pparams if k in modified])
        return "%s('%s', %s, %s)" % (self.__class__.__name__, self.spec_key, self.value, pstr)

class ListSpecs(StaticSpecs):
    """
    A TaskSpecifier that takes its values from a given list.
    """

    spec_key = param.String(default='default',doc='''
         The key name that take its values from the given list.''')

    def __init__(self, spec_key, value_list, fp_precision=4, rationale=''):

        self._specs = []
        self._exhausted = False
        super(TaskSpecifier, self).__init__(spec_key=spec_key, rationale=rationale,
                                            fp_precision=fp_precision, dynamic=False)
        self._specs = [ {spec_key:self.formatter(val)} for val in value_list]
        self.value_list = [self.formatter(val) for val in value_list]

    def __repr__(self):
        return "%s(%s,%s)" % (self.__class__.__name__, self.spec_key, self.value_list) #value_list

#========================#
# Dynamic TaskSpecifiers #
#========================#

class DynamicConcatenate(TaskSpecifier):
    def __init__(self, first, second, rationale=''):
        self.first = first
        self.second = second
        rationales = [rationale, first.rationale, second.rationale]
        if rationale == '': rationales = rationales[1:]
        rationale = "\n\n".join([r for r in rationales if (r is not '')])

        super(Concatenate, self).__init__(dynamic=True, rationale=rationale)

        self._exhausted = False
        self._first_sent = False
        self._first_cached = None
        self._second_cached = None
        if not first.dynamic: self._first_cached = next(first.copy())
        if not second.dynamic: self._second_cached = next(second.copy())

    def schedule(self):
        if self._first_cached is None:
            first_schedule = self.first.schedule()
            if first_schedule is None: return None
            return first_schedule + [len(self._second_cached)]
        else:
            second_schedule = self.second.schedule()
            if second_schedule is None: return None
            return [len(self._second_cached)]+ second_schedule

    def constant_keys(self):
        return list(set(self.first.constant_keys()) | set(self.second.constant_keys()))

    def varying_keys(self):
        return list(set(self.first.varying_keys()) | set(self.second.varying_keys()))

    def update(self, data):
        if (self.first.dynamic and not self._exhausted): self.first.update(data)
        elif (self.second.dynamic and self._first_sent): self.second.update(data)

    def next(self):
        if self._first_cached is None:
            try:  return next(self.first)
            except StopIteration:
                self._exhausted = True
                return self._second_cached
        else:
            if not self._first_sent:
                self._first_sent = True
                return self._first_cached
            else:
                return  next(self.second)

    def __repr__(self):
        return "(%s + %s)" % (repr(self.first), repr(self.second))

class DynamicCartesianProduct(TaskSpecifier):

    def __init__(self, first, second, rationale=''):

        self.first = first
        self.second = second

        rationales = [rationale, first.rationale, second.rationale]
        if rationale == '': rationales = rationales[1:]
        rationale = "\n\n".join([r for r in rationales if (r is not '')])

        overlap = set(self.first.varying_keys()) &  set(self.second.varying_keys())
        assert overlap == set(), 'Sets of keys cannot overlap between TaskSpecifiers in cartesian product.'

        super(CartesianProduct, self).__init__(dynamic=True, rationale=rationale)

        self._first_cached = None
        self._second_cached = None
        if not first.dynamic: self._first_cached = next(first.copy())
        if not second.dynamic: self._second_cached = next(second.copy())

    def constant_keys(self):
        return list(set(self.first.constant_keys()) | set(self.second.constant_keys()))

    def varying_keys(self):
        return list(set(self.first.varying_keys()) | set(self.second.varying_keys()))

    def update(self, data):
        if self.first.dynamic:  self.first.update(data)
        if self.second.dynamic: self.second.update(data)

    def schedule(self):
        if self._first_cached is None:
            first_schedule = self.first.schedule()
            if first_schedule is None: return None
            return [len(self._second_cached)*i for i in first_schedule]
        else:
            second_schedule = self.second.schedule()
            if second_schedule is None: return None
            return [len(self._first_cached)*i for i in second_schedule]

    def next(self):
        if self._first_cached is None:
            first_spec = next(self.first)
            return self._cartesian_product(first_spec, self._second_cached)
        else:
            second_spec = next(self.second)
            return self._cartesian_product(self._first_cached, second_spec)

    def __repr__(self):   return '(%s * %s)' % (repr(self.first), repr(self.second))


#==============#
# TaskCommands #
#==============#

class TaskCommand(param.Parameterized):
    """
    A TaskCommand is a way of converting the general key-value dictionary format
    of a single task specification to a particular command that needs
    execution. TaskCommands are objects that when called return a command to be
    executed at the commandline as a list of strings (Popen format).

    TaskCommands should avoid all platform specific logic (this is the job of
    the Launcher) but there are some important cases where the specification
    needs to be read from file in order for a task to be queued before the
    specification has been generated. To achieve this two extra methods (other
    than __call__) should be implemented where possible:

    __call__(self, spec, tid=None, info={}):

    The method that must be implemented in all TaskCommands. The tid argument is
    the task id and info is a dictionary of run-time information provided by the
    launcher. Info consists of the following information : root_directory,
    timestamp, varying_keys, constant_keys, batch_name, batch_tag and
    batch_description.

    specify(spec, tid, info):

    Takes a specification for the task and writes it to a file in the
    'specifications' subdirectory of the root directory. The specification file
    names should include the tid to ensure uniqueness.

    queue(self,tid, info):

    The command (Popen args format) that retrieves the run-time information from
    the specification file of the given tid in the 'specifications' subdirectory
    of the root directory.
    """

    __abstract = True

    allowed_list = param.List(default=[],  doc='''
        An explicit list of specification keys that the TaskCommand is expected
        to accept. This allows some degree of error checking before tasks are
        launched (if set). Note that one alternate safeguard is to instruct your
        command to exit if invalid parameters are provided if such an option is
        available.  For example, Topographica can be told to promote warnings to
        exceptions. This way warnings about unrecognised parameters are not
        ignored resulting in invalid simulations results.''')

    executable = param.String(default='python', constant=True, doc='''
        The executable that is to be run by this TaskCommand. Unless the
        executable is a standard command that can be expected on the system
        path, this should be an absolute path to the executable. By default this
        invokes python or the python environment used to invoke the TaskCommand
        (eg. the topographica script).  Note: This can be overridden by the user
        but really should be set by the TaskCommand object with a sensible
        default behaviour.''')

    def __init__(self, executable=None, **kwargs):
        if executable is None:
            executable = sys.executable
        super(TaskCommand,self).__init__(executable=executable, **kwargs)

    def __call__(self, spec, tid=None, info={}):
        """
        Formats a single specification - a dictionary with string keys and
        string values.  The info dictionary includes the root_directory,
        batch_name, batch_tag, batch_description, timestamp, varying_keys,
        constant_keys.
        """
        raise NotImplementedError

    def show(self, task_specifier, file_handle = sys.stdout , queue_cmd_only=False):
        info = {'root_directory':     '<root_directory>',
                'batch_name':         '<batch_name>',
                'batch_tag':          '<batch_tag>',
                'batch_description':  '<batch_description>',
                'timestamp':          tuple(time.localtime()),
                'varying_keys':       task_specifier.varying_keys(),
                'constant_keys':      task_specifier.constant_keys()}

        if queue_cmd_only and not hasattr(self, 'queue'):
            print("Cannot show queue: TaskCommand not queueable")
            return
        elif queue_cmd_only:
            full_string = 'Queue command: '+ ' '.join([pipes.quote(el) for el in self.queue('<tid>',info)])
        else:
            copied = task_specifier.copy()
            full_string = ''
            enumerated = [el for el in enumerate(copied)]
            for (group_ind, specs) in enumerated:
                if len(enumerated) > 1: full_string += "\nGroup %d" % group_ind
                quoted_cmds = [[pipes.quote(el) for el in self(s,'<tid>',info)] for s in specs]
                cmd_lines = [ '%d: %s\n' % (i, ' '.join(qcmds)) for (i,qcmds) in enumerate(quoted_cmds)]
                full_string += ''.join(cmd_lines)

        file_handle.write(full_string)
        file_handle.flush()

#===========#
# Launchers #
#===========#

class Launcher(param.Parameterized):
    """
    A Launcher takes a name, a TaskSpecifier and TaskCommand in the constructor
    and launches the corresponding tasks appropriately when invoked.

    This default Launcher uses subprocess to launch the tasks. It is intended to
    illustrate the basic design and should be used as a base class for more
    complex Launchers.
    """

    task_specifier = param.ClassSelector(TaskSpecifier, constant=True, doc='''
              The task specifier used to generate the varying parameters for the tasks.''')

    task_command = param.ClassSelector(TaskCommand, constant=True, doc='''
              The task command used to generate the commands for the tasks.''')

    tag = param.String(default='', doc='''
               A very short, identifiable human-readable string that
               meaningfully describes the batch to be executed. Should not
               include spaces as it may be used in filenames.''')

    description = param.String(default='', doc='''
              A short description of the purpose of the current set of tasks.''')

    max_concurrency = param.Integer(default=2, allow_None=True, doc='''
             Concurrency limit to impose on specifier. As the current class uses
             subprocess locally, two concurrent processes is the limit. Set to
             None for no limit (eg. for clusters)''')

    exit_callable = param.Callable(default=None, doc='''
             A callable that will be invoked when the Launcher has completed all
             tasks. For example, this can be used to collect and analyse data
             generated across tasks (eg. reduce across maps in a
             RunBatchAnalysis), inform the user of completion (eg. send an
             e-mail) among other possibilities.''')

    timestamp = param.NumericTuple(default= (0, 0, 0, 0, 0, 0, 0, 0, 0), doc="""
            Optional override of timestamp (default timestamp set on dispatch
            call) in Python struct_time 9-tuple format.  Useful when you need to
            have a known root_directory path (see root_directory documentation)
            before launch. For example, you should store state related to
            analysis (eg. pickles) in the same location as everything else.""")

    timestamp_format = param.String(default='%Y-%m-%d_%H%M', allow_None=True, doc="""
             The timestamp format for directories created by run_batch in python
             datetime format. If None is used, timestamp is omitted from root
             directory.""")

    metric_loader = param.Callable(default=pickle.load, doc='''
             The function that will load the metric files generated by the
             task. By default uses pickle.load but json.load is also valid
             option. The callable must take a file object argument and return a
             python object. A third interchange format that might be considered
             is cvs but it is up to the user to implement the corresponding
             loader.''')

    @classmethod
    def commandline(cls, argsv):
        """
        Class method to allow Launchers to be controlled from the commandline.
        If commandline is processed, should return True - note that decorator
        will exit immediately after (prevents the calling decorator from
        relaunching)
        """
        return False


    def __init__(self, batch_name, task_specifier, task_command, **kwargs):

        super(Launcher,self).__init__(task_specifier=task_specifier,
                                          task_command = task_command,
                                          **kwargs)

        self.batch_name = batch_name
        self._spec_log = []
        self.timestamp = tuple(time.localtime())

    def root_directory_name(self, timestamp):
        " A helper method that gives the root direcory name given a timestamp "
        if self.timestamp_format is not None:
            return time.strftime(self.timestamp_format, timestamp) + '-' + self.batch_name
        else:
            return self.batch_name


    def append_log(self, specs):
        """
        The log contains the tids and corresponding specifications used during
        launch with the specifications in json format.
        """

        self._spec_log += specs
        with open(os.path.join(self.root_directory,
                               ("%s.log" % self.batch_name)), 'a') as log:
            lines = ['%d %s' % (tid, json.dumps(spec)) for (tid, spec) in specs]
            log.write('\n'.join(lines))

    def record_info(self):
        """
        All Tasklaunchers should call this method to write the info file at the
        end of the launch.  The info file saves the full timestamp and launcher
        description. The file is written to the root_directory.
        """

        with open(os.path.join(self.root_directory,
            ('%s.info' % self.batch_name)), 'w') as info:
            startstr = time.strftime("Start Date: %d-%m-%Y Start Time: %H:%M (%Ss)",
                                     self.timestamp)
            endstr = time.strftime("Completed: %d-%m-%Y Start Time: %H:%M (%Ss)",
                                   time.localtime())
            lines = [startstr, endstr, 'Batch name: %s' % self.batch_name,
                     'Description: %s' % self.description]
            info.write('\n'.join(lines))

    def _setup_launch(self):
        """
        Method to be used by all launchers that prepares the rootdirectory and
        generate basic launch information for task specifiers to use. Prepends
        some basic information to the description, registers a timestamp and
        return a dictionary of useful information constant across all tasks.
        """

        root_name = self.root_directory_name(self.timestamp)
        self.root_directory = param.normalize_path(root_name)

        if not os.path.isdir(self.root_directory): os.makedirs(self.root_directory)
        metrics_dir = os.path.join(self.root_directory, 'metrics')
        if not os.path.isdir(metrics_dir) and self.task_specifier.dynamic:
            os.makedirs(metrics_dir)

        formatstr = "Batch '%s' of tasks specified by %s and %s launched by %s with tag '%s':\n"
        classnames= [el.__class__.__name__ for el in
                [self.task_specifier, self.task_command, self]]
        self.description = (formatstr % tuple([self.batch_name] + \
                classnames + [self.tag]))+self.description

        return {'root_directory':    self.root_directory,
                'timestamp':         self.timestamp,
                'varying_keys':      self.task_specifier.varying_keys(),
                'constant_keys':     self.task_specifier.constant_keys(),
                'batch_name':        self.batch_name,
                'batch_tag':         self.tag,
                'batch_description': self.description }

    def _setup_streams_path(self):
        streams_path = os.path.join(param.normalize_path(),
                               self.root_directory, "streams")

        try: os.makedirs(streams_path)
        except: pass

        # Waiting till these directories exist (otherwise potential qstat error)
        while not os.path.isdir(streams_path): pass

        return streams_path

    def extract_metrics(self, tids, launchinfo):
        """
        Method to extract the metrics generated by the tasks required to update
        the TaskSpecifier (if dynamic). Uses the metric loaded to extract the
        metrics of specified tids in the metrics subdirectory of the root
        directory. Convention is that metric files should always be prefixed
        with metric-<tid>- in this directory. Note the trailing '-' and if there
        are multiple files with same tid prefix, they will all be returned.
        """

        metrics_dir = os.path.join(self.root_directory, 'metrics')
        listing = os.listdir(metrics_dir)
        try:
            matches = [l for l in listing for tid in tids
                    if fnmatch.fnmatch(l, 'metric-%d-*' % tid)]
            pfiles = [open(os.path.join(metrics_dir, match),'rb') for match in matches]
            return [self.metric_loader(pfile) for pfile in pfiles]
        except:
            logging.error("Cannot load required metric files. Cannot continue.")
            return None # StopIteration should be raised by the TaskSpecifier.

    def limit_concurrency(self, elements):
        """
        Helper function that breaks list of elements into chunks (sublists) of
        size self.max_concurrency.
        """

        if self.max_concurrency is None: return [elements]

        return [elements[i:i+self.max_concurrency] for i in
               range(0, len(elements), self.max_concurrency)]

    def dispatch(self):
        """
        The method that starts Launcher execution. Typically called by a task
        decorator.  This could be called directly by the users but the risk is
        that if __name__=='__main__' is omitted, the launcher may rerun on any
        import of the script effectively creating a fork-bomb.
        """
        launchinfo = self._setup_launch()
        streams_path = self._setup_streams_path()

        last_tid = 0
        last_tids = []
        for gid, groupspecs in enumerate(self.task_specifier):
            tids = list(range(last_tid, last_tid+len(groupspecs)))
            last_tid += len(groupspecs)
            allcommands = [self.task_command(spec, tid, launchinfo) for (spec,tid) in zip(groupspecs,tids)]

            self.append_log(list(zip(tids,groupspecs)))
            batches = self.limit_concurrency(list(zip(allcommands,tids)))
            for bid, batch in enumerate(batches):
                processes = []
                stdout_handles = []
                stderr_handles = []
                for (cmd,tid) in batch:
                    stdout_handle = open(os.path.join(streams_path, "%s.o.%d" % (self.batch_name, tid)), "wb")
                    stderr_handle = open(os.path.join(streams_path, "%s.e.%d" % (self.batch_name, tid)), "wb")
                    processes.append(subprocess.Popen(cmd, stdout=stdout_handle, stderr=stderr_handle))
                    stdout_handles.append(stdout_handle)
                    stderr_handles.append(stderr_handle)

                logging.info("Batch of %d (%d:%d/%d) subprocesses started..." % \
                            (len(processes), gid, bid, len(batches)-1))

                [p.wait() for p in processes]

                [stdout_handle.close() for stdout_handle in stdout_handles]
                [stderr_handle.close() for stderr_handle in stderr_handles]

            last_tids = tids[:]

            if self.task_specifier.dynamic:
                self.task_specifier.update(self.extract_metrics(last_tids, launchinfo))

        self.record_info()
        if self.exit_callable is not None: self.exit_callable(self._spec_log, self.root_directory)

class QLauncher(Launcher):
    """
    Launcher that operates the Sun Grid Engine using default arguments suitable
    for runnign on the Edinburgh Eddie cluster. Allows automatic parameter
    search strategies such as hillclimbing to be used where parameters used
    depend on previously generated results without blocking waiting on results.

    One of the main features of this class is that it is non-blocking - it alway
    exits shortly after invoking qsub. This means that the script is not left
    running, waiting for long periods of time on the cluster. This is
    particularly important for long simulation where you wish to run some code
    at the end of the simulation (eg. plotting your results) or when waiting for
    results from runs (eg. waiting for results from 100 seeds to update your
    hillclimbing algorithm).

    To achieve this, QLauncher qsubs a command back to the launching user script
    which instructs Qlauncher to continue with 'collate_and_launch'
    step. Collating refers to either collecting output from a subset of runs to
    update the TaskSpecifier or to the final collation of all the results at the
    end of all runs. Each task depends on the previous collate step completing
    and in turn each collate step depends on the necessary tasks steps reaching
    completion.

    By convention the standard output and error streams go to the corresponding
    folders in the 'streams' subfolder of the root directory - any -o or -e qsub
    options will be overridden. The job name (the -N flag) is specified
    automatically and any user value will be ignored.
    """

    qsub_switches = param.List(default=['-V', '-cwd'], doc = """
          Specifies the qsub switches (flags without arguments) as a list of
          strings. By default the -V switch is used to exports all environment
          variables in the host environment to the batch job.""")

    qsub_flag_options = param.Dict(default={'-b':'y'}, doc="""
          Specifies qsub flags and their corresponding options as a
          dictionary. Valid values may be strings or lists of string.  If a
          plain Python dictionary is used, the keys are alphanumerically sorted,
          otherwise the dictionary is assumed to be an OrderedDict (Python 2.7+,
          Python3 or param.external.OrderedDict) and the key ordering will be
          preserved.

          By default the -b (binary) flag is set to 'y' to allow binaries to be
          directly invoked. Note that the '-' is added to the key if missing (to
          make into a valid flag) so you can specify using keywords in the dict
          constructor: ie. using qsub_flag_options=dict(key1=value1,
          key2=value2, ....)
        """)

    @classmethod
    def commandline(cls, args):
        """
        Continues the execution of the launcher if argument 'collate_and_launch'
        is last argument on the commandline. In this case, the root directory is
        expected to be the preceeding argument. This information allows the
        launcher.pickle file to be unpickled to resume launch.
        """
        if args[-1] != 'collate_and_launch': return False
        root_path = param.normalize_path(args[-2])
        pickle_path = os.path.join(root_path, 'launcher.pickle')
        launcher = pickle.load(open(pickle_path,'rb'))
        launcher.collate_and_launch()
        return True

    def __init__(self, batch_name, task_specifier, task_command, **kwargs):
        super(QLauncher, self).__init__(batch_name, task_specifier,
                task_command, **kwargs)

        self._launchinfo = None
        self.schedule = None
        self.last_tids = []
        self._spec_log = []
        self.last_tid = 0
        self.last_scheduled_tid = 0
        self.collate_count = 0

        self.max_concurrency = None # Inherited

        # The necessary conditions for reserving jobs before specification known.
        self.is_dynamic_qsub = all([self.task_specifier.dynamic,
                                    hasattr(self.task_specifier, 'schedule'),
                                    hasattr(self.task_command,   'queue'),
                                    hasattr(self.task_command,   'specify')])

    def qsub_args(self, override_options, cmd_args):
        """
        Method to generate Popen style argument list for qsub using the
        qsub_switches and qsub_flag_options parameters. Switches are returned
        first, sorted alphanumerically.  The qsub_flag_options follow in keys()
        ordered if not a vanilla Python dictionary (ie. a Python 2.7+ or
        param.external OrderedDict). Otherwise the keys are sorted
        alphanumerically. Note that override_options is a list of key-value
        pairs.
        """

        opt_dict = type(self.qsub_flag_options)()
        opt_dict.update(self.qsub_flag_options)
        opt_dict.update(override_options)

        if type(self.qsub_flag_options) == dict:   # Alphanumeric sort if vanilla Python dictionary
            ordered_options = [(k, opt_dict[k]) for k in sorted(opt_dict)]
        else:
            ordered_options =  list(opt_dict.items())

        unpacked_groups = [[(k,v) for v in val] if type(val)==tuple else [(k,val)]
                           for (k,val) in ordered_options]
        unpacked_kvs = [el for group in unpacked_groups for el in group]

        # Adds '-' if missing (eg, keywords in dict constructor) and flattens lists.
        ordered_pairs = [(k,v) if (k[0]=='-') else ('-%s' % (k), v)
                         for (k,v) in unpacked_kvs]
        ordered_options = [[k]+([v] if type(v) == str else v) for (k,v) in ordered_pairs]
        flattened_options = [el for kvs in ordered_options for el in kvs]

        return (['qsub'] + sorted(self.qsub_switches)
                + flattened_options + [pipes.quote(c) for c in cmd_args])

    def dispatch(self):
        """
        Main entry point for the launcher. Collects the static information about
        the launch and sets up the stdout and stderr stream output
        directories. Generates the first call to collate_and_launch().
        """
        self._launchinfo = self._setup_launch()
        self.job_timestamp = time.strftime('%H%M%S')

        streams_path = self._setup_streams_path()

        self.qsub_flag_options['-o'] = streams_path
        self.qsub_flag_options['-e'] = streams_path

        self.collate_and_launch()

    def collate_and_launch(self):
        """
        Method that collates the previous jobs and launches the next block of
        concurrent jobs. The launch type can be either static or dynamic
        (ie. using schedule, queue and specify with dynamic TaskSpecifiers).
        This method is invoked on initial dispatch and then subsequently via the
        commandline to collate the previously run jobs and launching the next
        block of jobs.
        """

        try:   specs = next(self.task_specifier)
        except StopIteration:
            self.qdel_batch()
            if self.exit_callable is not None:
                self.exit_callable(self._spec_log, self.root_directory)
            self.record_info()
            return

        tid_specs = [(self.last_tid + i, spec) for (i,spec) in enumerate(specs)]
        self.last_tid += len(specs)
        self.append_log(tid_specs)

        # Updating the TaskSpecifier
        if self.task_specifier.dynamic:
            self.task_specifier.update(self.extract_metrics(self.last_tids, self._launchinfo))
        self.last_tids = [tid for (tid,_) in tid_specs]

        output_dir = self.qsub_flag_options['-o']
        error_dir = self.qsub_flag_options['-e']
        if self.is_dynamic_qsub: self.dynamic_qsub(output_dir, error_dir, tid_specs)
        else:            self.static_qsub(output_dir, error_dir, tid_specs)

        # Pickle launcher before exit if necessary.
        if (self.task_specifier.dynamic) or (self.exit_callable is not None):
            root_path = param.normalize_path(self.root_directory)
            pickle_path = os.path.join(root_path, 'launcher.pickle')
            pickle.dump(self, open(pickle_path,'wb'))

    def qsub_collate_and_launch(self, output_dir, error_dir, job_names):
        """
        The method that qsubs a call to the user launch script with the
        necessary commandline arguments for collating and launching the next
        block of jobs.
        """

        job_name = "%s_%s_collate_%d" % (self.batch_name, self.job_timestamp,
                self.collate_count)

        overrides = [("-e",error_dir), ('-N',job_name), ("-o",output_dir),
                     ('-hold_jid',','.join(job_names))]

        cmd_args = [self.task_command.executable, self.script_path,
                    self.root_directory, 'collate_and_launch']
        popen_args = self.qsub_args(overrides, cmd_args)

        p = subprocess.Popen(popen_args, stdout=subprocess.PIPE)
        (stdout, stderr) = p.communicate()

        self.collate_count += 1
        logging.debug(stdout)
        logging.info("Invoked qsub for next batch.")
        return job_name

    def static_qsub(self, output_dir, error_dir, tid_specs):
        """
        This method handles static TaskSpecifiers and cases where the dynamic
        TaskSpecifiers cannot be queued ahead of specification.
        """
        processes = []
        job_names = []

        for (tid, spec) in tid_specs:
            job_name = "%s_%s_job_%d" % (self.batch_name, self.job_timestamp, tid)
            job_names.append(job_name)
            cmd_args = self.task_command(spec, tid, self._launchinfo)
            popen_args = self.qsub_args([("-e",error_dir), ('-N',job_name), ("-o",output_dir)],
                                        cmd_args)
            p = subprocess.Popen(popen_args, stdout=subprocess.PIPE)
            (stdout, stderr) = p.communicate()
            logging.debug(stdout)
            processes.append(p)

        logging.info("Invoked qsub for %d commands" % len(processes))
        if self.exit_callable is not None:
            self.qsub_collate_and_launch(output_dir, error_dir, job_names)

    def dynamic_qsub(self, output_dir, error_dir, tid_specs):
        """
        This method handles dynamic TaskSpecifiers where the dynamic
        TaskSpecifiers can be queued ahead of specification.
        """

        # Write out the specification files in anticipation of execution
        [self.task_command.specify(spec,tid, self._launchinfo) for (tid, spec) in tid_specs]

        # If schedule is empty (or on first initialization)...
        if (self.schedule == []) or (self.schedule is None):
            self.schedule = self.task_specifier.schedule()
            assert len(tid_specs)== self.schedule[0], "Number of specs don't match schedule!"

            # Generating the scheduled tasks (ie the queue commands)
            collate_name = None
            for batch_size in self.schedule:
                schedule_tids = [tid + self.last_scheduled_tid for tid in range(batch_size) ]
                schedule_tasks = [(tid, self.task_command.queue(tid, self._launchinfo)) for
                                      tid in schedule_tids]

                # Queueing with the scheduled tasks with appropriate job id dependencies
                hold_jid_cmd = []
                group_names = []

                for (tid, schedule_task) in schedule_tasks:
                    job_name = "%s_%s_job_%d" % (self.batch_name, self.job_timestamp, tid)
                    overrides = [("-e",error_dir), ('-N',job_name), ("-o",output_dir)]
                    if collate_name is not None: overrides += [('-hold_jid', collate_name)]
                    popen_args = self.qsub_args(overrides, schedule_task)
                    p = subprocess.Popen(popen_args, stdout=subprocess.PIPE)
                    (stdout, stderr) = p.communicate()
                    group_names.append(job_name)

                collate_name = self.qsub_collate_and_launch(output_dir, error_dir, group_names)
                self.last_scheduled_tid += batch_size

            # Popping the currently specified tasks off the schedule
            self.schedule = self.schedule[1:]

    def qdel_batch(self):
        """
        Runs qdel command to remove all remaining queued jobs using the
        <batch_name>* pattern . Necessary when StopIteration is raised with
        scheduled jobs left on the queue.
        """
        p = subprocess.Popen(['qdel', '%s_%s*' % (self.batch_name, self.job_timestamp)],
                             stdout=subprocess.PIPE)
        (stdout, stderr) = p.communicate()


#===================#
# Launch Decorators #
#===================#

class review_and_launch:
    """
    The basic example of the sort of decorator that -must- be used to start
    Launcher execution for the following reasons:

    1) The definition script may include objects/class that need to be imported
    (eg. for accessing analysis functions) to execute the tasks. By default this
    would execute the whole script and therefore re-run the Launcher which would
    cause a fork-bomb! This decorator only executes the Tasklauncher that is
    returned by the wrapped function if __name__=='__main__'

    2) Code in the script after Launcher execution has been invoked is *not*
    guaranteed to execute after all tasks are complete (eg. due to forking,
    subprocess, qsub etc). This decorator solves this issue, making sure
    execution is the last thing that happens. The exit_callable parameter is the
    proper way of executing code after the Launcher exits.
    """

    def __init__(self, launcher_class, output_directory=None, review=True, check_main=True):
        self.review = review
        self.launcher_class = launcher_class
        self.output_directory = output_directory
        self.check_main = check_main
        # The launcher classmethod 'commandline' is called before function invocation.
        if not isinstance(launcher_class,type) \
                or not issubclass(launcher_class, Launcher):
            raise Exception("Use decorator as follows: review_and_launch(<launcher_class>, review=True)")

    def section(self, text, car='=', carvert='|'):
        length=len(text)+4
        return '%s\n%s %s %s\n%s' % (car*length, carvert, text,
                                     carvert, car*length)

    def input_options(self, options, prompt='Select option', default=None):
        check_options = [x.lower() for x in options]

        while True:
            response = raw_input('%s [%s]: ' % (prompt, ', '.join(options))).lower()
            if response in check_options:
                return response
            elif response == '' and default is not None:
                return default.lower()

    def review_task_specification(self, task_specifier):
        print(self.section('TaskSpecifier'))
        print("Type: %s (dynamic=%s)" % (task_specifier.__class__.__name__,
            task_specifier.dynamic))
        print("Varying Keys: %s" % task_specifier.varying_keys())
        print("Constant Keys: %s" % task_specifier.constant_keys())
        print("Definition: %s" % task_specifier)

        if task_specifier.rationale != '':
            print("\nRationale:\n%s\n" % task_specifier.rationale)

        response = self.input_options(['Y', 'n','quit'],
                '\nShow available taskspecifier entries?', default='y')

        if response == 'quit': return False
        if response == 'y':  task_specifier.show()
        print
        return True

    def review_task_command(self, task_command, task_specifier, task_launcher):
        print(self.section('TaskCommand'))
        print("Type: %s" % task_command.__class__.__name__)
        if task_command.allowed_list != []:
            print("Allowed List: %s" % task_command.allowed_list)
        if isinstance(task_launcher, QLauncher):
            task_command.show(task_specifier.copy(),
                    queue_cmd_only=task_launcher.is_dynamic_qsub)

        if task_command.allowed_list != []:
            allowed_list = set(task_command.allowed_list)
            all_keys = set(task_specifier.varying_keys()+task_specifier.constant_keys())
            if not (all_keys <= allowed_list):
                clashes = all_keys - allowed_list
                raise Exception("Keys %s not in the allowed list of the TaskCommand!" % list(clashes))

        response = self.input_options(['Y', 'n','quit','savefile'],
                '\nShow available taskcommand entries?', default='y')
        if response == 'quit': return False
        if response == 'y':
            task_command.show(task_specifier.copy())
        if response == 'savefile':
            fname = input('Filename: ').replace(' ','_')
            with open(fname,'w') as f:
                task_command.show(task_specifier.copy(),file_handle=f)
        print
        return True

    def review_task_launcher(self, task_launcher,task_command):
        print(self.section('Launcher'))
        print("Type: %s" % task_launcher.__class__.__name__)
        print("Batch Name: %s" % task_launcher.batch_name)
        print("Command executable: %s" % task_command.executable)
        root_directory = task_launcher.root_directory_name(task_launcher.timestamp)
        print("Root directory: %s" % param.normalize_path(root_directory))
        print("Maximum concurrency: %s" % task_launcher.max_concurrency)

        if task_launcher.description == '': description = '<No description>'
        else:                               description = task_launcher.description
        print("Description: %s" % description)

        if task_launcher.tag == '':         tag = '<No tag>'
        else:                               tag = task_launcher.tag
        print("Tag: %s" % tag)
        print

    def __call__(self, f):
        if not self.check_main or f.__module__ == '__main__':
            commandline_used = self.launcher_class.commandline(sys.argv)
        if commandline_used: return None

        if self.output_directory is not None:
            param.normalize_path.prefix = self.output_directory
        task_launcher = f()

        # Finding and setting the script path (needed for Launcher that use the commandline)
        script_path = os.path.join(os.getcwd(), sys.argv[-1])
        if not os.path.exists(script_path):
            print "Cannot extract script path: %s" % script_path; sys.exit()

        task_launcher.script_path = script_path

        if not isinstance(task_launcher, Launcher):
            raise Exception("Function must return a Tasklauncher not '%s'" % str(task_launcher))

        if self.review:
            task_specifier = task_launcher.task_specifier
            task_command = task_launcher.task_command

            self.review_task_launcher(task_launcher, task_command)

            if self.review_task_specification(task_specifier) and \
              self.review_task_command(task_command, task_specifier, task_launcher) and \
              (self.input_options(['y','N'], 'Execute?', default='n') == 'y'):
                print("== Dispatching '%s' ==" % task_launcher.batch_name)
                task_launcher.dispatch()
            else: print("Aborting dispatch...")
        else:
            task_launcher.dispatch()

        return None
