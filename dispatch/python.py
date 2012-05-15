
# https://github.com/ponty/entrypoint2
# http://coderazzi.net/python/optmatch/index.htm
# https://github.com/seomoz/shovel

import param
import os, sys, json
from dispatch import TaskCommand

class SimplePyScriptCommand(TaskCommand):
   """ A very simple way to invoke a Python script and pass it some
   arguments. The order in which the arguments are passed in can
   optionally be specified. Note that the tid is always passed in
   first.

   0,       1,      2,     3...
   Script, tid, root_dir, 
   Also: tid_arg_first, root_path_second
   """

   script_path = param.String(default='', constant=True, doc='''
       The path to the Python script to be run. ''')

   argorder = param.List(default=[], constant=True, doc='''
       If None, assumes the ordering of the arguments is assumed to be
       irrelevant. Otherwise, the arguments are supplied to the script
       in the specified order.''')

   def __init__(self, script_path, argorder=[]):
      script_path = os.path.abspath(script_path)
      super(SimplePyScriptCommand, self).__init__(script_path=script_path, 
                                                 argorder=argorder)

   def __call__(self, spec, tid=None, info={}): 
      prefix = ['python', self.script_path, 
                str(tid), param.normalize_path(info['root_directory'])]

      if self.argorder == []:  return prefix + spec.values()
      else:                    return prefix + [spec[k] for k in self.argorder]


   def queue(self,tid, info):
      spec_path = os.path.join(param.normalize_path(), info['root_directory'], 'specifications')
      spec_file_path = os.path.join(spec_path, 'spec-%s' % tid)
      return ['python', '-m', 'dispatch.python', 'specify', self.script_path, spec_file_path]

   def specify(self, spec, tid, info):
      spec_path = os.path.join(param.normalize_path(), info['root_directory'], 'specifications')
      if not os.path.isdir(spec_path): os.makedirs(spec_path)
      spec_file_path = os.path.join(spec_path, 'spec-%s' % tid)
      prefix = [str(tid), param.normalize_path(info['root_directory'])]

      if self.argorder == []:  specstr = ' '.join(prefix+spec.values())
      else:                    specstr = ' '.join(prefix + [spec[k] for k in self.argorder])

      with open(spec_file_path,'w') as specfile: specfile.write(specstr)


if __name__ == '__main__':
   if sys.argv[1] == 'specify':
      script = sys.argv[2]
      spec = sys.argv[3]
      with open(spec,'r') as specfile:
         new_args = specfile.read().split()
      sys.argv=[script]+new_args
      execfile(script)


# From Jim:
#executable= "../topographica"
#command_skeleton= ["%{executable}","%{static_args}","%{task_spec}","%{command_files}"]
#static_args = str([x.str() for x in arglist],kvseparator)
#task_spec_str = str([x.str() for x in task_spec.keys()],kvseparator)
#command format(command_skeleton,{"static_args":static_args,"task_spec":task_spec_str,...)
