"""
Code used to support old snapshots, and update scripts.

$Id$
"""
__version__='$Revision: 8021 $'

import imp
import sys

# CB: If we were using pickle rather than cpickle, could subclass the
# unpickler to look for module Xs as module X if Xs can't be found,
# and probably simplify quite a lot of the legacy code installation.
#
# Maybe we could do that by trying to use cpickle initially, then
# falling back to pickle when we do a 'legacy load' of the snapshot.


# CB: Could probably simplify some things in here where I've
# accidentally used the more complex code like fake_a_class for simply
# linking one class to another after renaming the class (fake_a_class()
# is to create a class in a module where the class doesn't exist at
# all any more). But things are working at the moment...

# CEBALERT: should have ONE list for the update script and for this,
# rather than having (effectively) a list in each.

def preprocess_state(class_,state_mod_fn): 
    """
    Allow processing of state with state_mod_fn before
    class_.__setstate__(instance,state) is called.

    state_mod_fn must accept two arguments: instance and state.
    """
    old_setstate = class_.__setstate__
    def new_setstate(instance,state):
        # passing instance here allows us to avoid having to list
        # specific classes in SnapshotSupport, because we can
        # now test each instance.
        state_mod_fn(instance,state) 
        old_setstate(instance,state)
    class_.__setstate__ = new_setstate


def select_setstate(class_,selector,pre_super=False,post_super=True):
    """
    Select appropriate function to call as a replacement
    for class.__setstate__ at runtime.

    selector must return None if the class_'s original method is
    to be used; otherwise, it should return a function that takes
    an instance of the class and the state.

    pre_super and post_super determine if super(class_)'s
    __setstate__ should be invoked before or after (respectively)
    calling the function returned by selector. If selector returns
    None, super(class_)'s __setstate__ is never called.
    """
    if pre_super is True and post_super is True:
        raise ValueError("Cannot call super method before and after.")

    old_setstate = class_.__setstate__
    def new_setstate(instance,state):
        setstate = selector(state) or old_setstate

        if pre_super and setstate is not old_setstate:
            super(class_,instance).__setstate__

        setstate(instance,state)

        if post_super and setstate is not old_setstate:
            super(class_,instance).__setstate__(state)


    class_.__setstate__ = new_setstate


def fake_a_class(module,old_name,new_class,new_class_args=()):
    """
    Install a class named 'old_name' in 'module'; when created,
    the class actually returns an instance of 'new_class'.

    new_class_args allow any arguments to be supplied to new_class
    before other arguments are passed at creation time.
    """
    class_code = """
class %s(object):
    def __new__(cls,*args,**kw):
        all_args = new_class_args+args
        return new_class(*all_args,**kw)"""        
    exec class_code%old_name in locals()
    fake_old_class = eval(old_name,locals())

    setattr(module,old_name,fake_old_class)


def fake_a_package(old,new,add_what):

    import topo
    
    code = \
"""
from topo.%s import *
"""%new
    fake_a_module('%s'%old,topo,code,'topo')

    mod = __import__("topo.%s"%old)
    #mod = eval('topo.%s'%old)

    for x in add_what:
    
        code = \
"""
from topo.%s.%s import *
"""%(new,x)

        # gotta supply the path because mod is fake...
        fake_a_module(x,mod,code,'topo.%s'%old)

# CB: should use a factory to produce functions or should use
# decorations.  Would avoid code duplication and make it simpler to
# see what's happening

# CB: not fully tested (don't know if it's enough to support all user
# code).
def fake_a_module(name,parent=None,source_code=None,parent_path=None):
    """Create the module parent.name using source_code."""
    # CB: parent path is necessary (even though it should be available
    # from parent) when faking a package

    assert source_code is not None # hack til I reorder the args!

    # create the module
    module = imp.new_module(name)
    exec source_code in module.__dict__

    if parent is not None:
        # install the module
        if parent_path is None:
            parent_path = parent.__name__

        sys.modules[parent_path+'.'+name]=module
        setattr(parent,name,module)
    else:
        sys.modules[name]=module


class SnapshotSupport(object):

    @staticmethod
    def install(svn=None):

        # CEBALERT: should add svn version test to see which hacks
        # actually need to be installed. I.e. organize these in
        # suitable way e.g. dictionary.
        # Haven't yet thought about whether or not it's actually possible
        # to get the version number before unpickling...

        def param_remove_hidden(instance,state):
            # Hidden attribute removed from Parameter in r7861
            if 'hidden' in state:
                if state['hidden'] is True:
                    state['precedence']=-1
                del state['hidden']

        def param_add_readonly(instance,state):
            # Hidden attribute added to Parameter in r7975
            if 'readonly' not in state:
                state['readonly']=False

        from .. import param
        preprocess_state(param.Parameter,param_remove_hidden)
        preprocess_state(param.Parameter,param_add_readonly)


        def class_selector_remove_suffixtolose(instance,state):
            # suffix_to_lose removed from ClassSelectorParameter in r8031
            if 'suffix_to_lose' in state:
                del state['suffix_to_lose']

        preprocess_state(param.ClassSelector,class_selector_remove_suffixtolose)



        def cf_rename_slice_array(instance,state):
            ## slice_array was renamed to input_sheet_slice in r7548
            if 'slice_array' in state:
                input_sheet_slice = state['slice_array']
                state['input_sheet_slice'] = input_sheet_slice
                del state['slice_array'] # probably doesn't work

        from topo.base.cf import ConnectionField
        preprocess_state(ConnectionField,cf_rename_slice_array)


        def sim_remove_time_type_attr(instance,state):
            # _time_type attribute added to simulation in r7581
            # and replaced by time_type param in r8215
            if '_time_type' in state:
                # CB: untested code (unless someone has such a snapshot;
                # if nobody has such a snapshot, can remove this code).
                state['_time_type_param_value']=state['_time_type']
                del state['_time_type']
            
        from topo.base.simulation import Simulation
        preprocess_state(Simulation,sim_remove_time_type_attr)


        def slice_setstate_selector(state):
            # Allow loading of pickles created before Pickle support was added to Slice.
            #
            # In snapshots created between 7547 (Slice becomes array) and 7762
            # (inclusive; Slice got pickle support in 7763), Slice instances
            # will be missing some information.
            #
            # CB: info could be recovered if required.
            if isinstance(state,dict):
                return None
            else:
                return ndarray.__setstate__

        from topo.base.sheetcoords import Slice                
        select_setstate(Slice,slice_setstate_selector,post_super=False)

        # CB: this is to work round change in SCS, but __setstate__ is never
        # called on that (method resolution order means __setstate__ comes
        # from EventProcessor instead)
        def sheet_set_shape(state):
            # since 7958, SCS has stored shape on creation
            def setstate(instance,state):
                if '_SheetCoordinateSystem__shape' not in state:
                    m = '_SheetCoordinateSystem__'
                    # all these are necessary for the calculation now,
                    # but would not otherwise be restored until later
                    setattr(instance,'bounds',state['bounds'])
                    setattr(instance,'lbrt',state['lbrt'])
                    setattr(instance,m+'xdensity',state[m+'xdensity'])
                    setattr(instance,m+'xstep',state[m+'xstep'])
                    setattr(instance,m+'ydensity',state[m+'ydensity'])
                    setattr(instance,m+'ystep',state[m+'ystep'])

                    shape = Slice(instance.bounds,instance).shape_on_sheet()
                    setattr(instance,m+'shape',shape)

            return setstate

        from topo.base.sheet import Sheet
        select_setstate(Sheet,sheet_set_shape) 


        ##########
        # r8001 Removed OutputFnParameter and CFPOutputFnParameter
        # r8014 Removed LearningFnParameter and ResponseFnParameter (+CFP equivalents)
        # r8028 Removed CoordinateMapperFnParameter
        # r8029 Removed PatternGeneratorParameter

        from topo.base.functionfamily import OutputFn,ResponseFn,LearningFn,\
             CoordinateMapperFn
        d = {"OutputFnParameter":OutputFn,
             "ResponseFnParameter":ResponseFn,
             "LearningFnParameter":LearningFn,
             "CoordinateMapperFnParameter":CoordinateMapperFn}        

        import topo.base.functionfamily
        for name,arg in d.items():
            fake_a_class(topo.base.functionfamily,name,
                         param.ClassSelector,(arg,))

        from topo.base.cf import CFPOutputFn,CFPResponseFn,CFPLearningFn
        d = {"CFPOutputFnParameter":CFPOutputFn,
             "CFPResponseFnParameter":CFPResponseFn,
             "CFPLearningFnParameter":CFPLearningFn}         

        import topo.base.cf
        for name,arg in d.items():
            fake_a_class(topo.base.cf,name,
                         param.ClassSelector,(arg,))

        import topo.base.patterngenerator
        from topo.base.patterngenerator import PatternGenerator
        fake_a_class(topo.base.patterngenerator,"PatternGeneratorParameter",
                     param.ClassSelector,(PatternGenerator,))
        ##########
            

        # for snapshots saved before r7901
        class SimSingleton(object):
            """Support for old snapshots."""
            def __setstate__(self,state):
                sim = state['actual_sim']
                param.Dynamic.time_fn = sim.time

        import topo.base.simulation
        topo.base.simulation.SimSingleton=SimSingleton


        # CEBALERT: we really need to start detecting the version so
        # hacks aren't unnecessary installed. Or at least provide an
        # option to request legacy support otherwise it's turned
        # off. Or something like that.

        # rXXXX
        # support topo.base.parameterized
        import topo.base
        code = \
"""
from topo.param.parameterized import *
"""
        fake_a_module('parameterized',topo.base,code)
        
        # rXXXX
        # support topo.base.parameterizedobject
        code = \
"""
from topo.param.parameterized import *
ParameterizedObject=Parameterized
"""
        fake_a_module('parameterizedobject',topo.base,code)


        # rXXXX
        # support topo.base.parameterclasses
        code = \
"""
from topo.param import *

from topo.param import Boolean as BooleanParameter
from topo.param import String as StringParameter
from topo.param import Callable as CallableParameter
from topo.param import Composite as CompositeParameter
from topo.param import Selector as SelectorParameter
from topo.param import ObjectSelector as ObjectSelectorParameter
from topo.param import ClassSelector as ClassSelectorParameter
from topo.param import List as ListParameter
from topo.param import Dict as DictParameter
"""
        fake_a_module('parameterclasses',topo.base,code)


        # DynamicNumber was removed in rXXXX
        class DynamicNumber(object):
            """
            Provide support for existing code that uses DynamicNumber:
            see __new__().
            """
            warnedA = False  # suppress warnings for the moment.
            warnedB = False

            def __new__(cls,default=None,**params):
                """
                If bounds or softbounds or any params are supplied, assume
                we're dealing with DynamicNumber declared as a parameter
                of a ParameterizedObject class.  In this case, return a
                new *Number* parameter instead.

                Otherwise, assume we're dealing with DynamicNumber
                supplied as the value of a Number Parameter. In this case,
                return a DynamicNumber (but one which is not a Parameter,
                just a simple wrapper).

                * Of course, this is not 100% reliable: if someone defines
                * a class with a DynamicNumber but doesn't pass any doc or
                * bounds or whatever. But in such cases, they'll get the
                * ParameterizedObject warning about being unable to set a
                * class attribute.

                Most of the code is to generate warning messages.

                """
                if len(params)>0:
                    ####################
                    m = "\n------------------------------------------------------------\nPlease update your code - instead of using the 'DynamicNumber' Parameter in the code for your class, please use the 'Number' Parameter; the Number Parameter now supports dynamic values automatically.\n\nE.g. change\n\nclass X(Parameterized):\n    y=DynamicNumber(NumberGenerator())\n\nto\n\n\nclass X(Parameterized):\n    y=Number(NumberGenerator())\n------------------------------------------------------------\n"
                    if not cls.warnedA:
                        param.Parameterized().warning(m)
                        cls.warnedA=True
                    ####################

                    n = Number(default,**params)
                    return n
                else:
                    ####################
                    m = "\n------------------------------------------------------------\nPlease update your code - instead of using DynamicNumber to contain a number generator, pass the number generator straight to the Number parameter:\n\nE.g. in code using the class below...\n\nclass X(Parameterized):\n    y=Number(0.0)\n\n\nchange\n\nx = X(y=DynamicNumber(NumberGenerator()))\n\nto\n\nx = X(y=NumberGenerator())\n------------------------------------------------------------\n"
                    if not cls.warnedB:
                        param.Parameterized().warning(m)
                        cls.warnedB=True
                    ####################
                    return object.__new__(cls,default)


            def __init__(self,default=0.0,bounds=None,softbounds=None,**params):
                self.val = default
            def __call__(self):
                return self.val()





            

        import topo.base.parameterclasses
        topo.base.parameterclasses.DynamicNumber = DynamicNumber
        import topo.param
        topo.param.DynamicNumber = DynamicNumber

        from topo.base.cf import CFProjection
        from numpy import array
        def cfproj_add_cfs(instance,state):
            # cfs attribute added in r8227
            if 'cfs' not in state:
                cflist = state['_cfs']
                state['cfs'] = array(cflist)
        preprocess_state(CFProjection,cfproj_add_cfs)


        # rXXXX renaming of component libraries
    
        # i don't understand why I can't get the following idea to work:
        # e.g. simply have sys.modules['topo.outputfns']=topo.outputfn (and for basic etc)
        # it doesn't work: importing topo.outputfns just gives topo

        # should read the list basic/optimized/etc from somewhere
        fake_a_package('outputfns','outputfn',['basic','optimized','projfn'])
        fake_a_package('responsefns','responsefn',['basic','optimized','projfn'])
        fake_a_package('learningfns','learningfn',['basic','optimized','projfn'])
        fake_a_package('coordmapperfns','coordmapper',['basic'])
        # note there's no legacy support for people using CFSOM. We could
        # add that if necessary.
        fake_a_package('sheets','sheet',['composer','generator',
                                         'lissom','optimized','saccade','slissom'])
        fake_a_package('eps','ep',['basic'])
        fake_a_package('patterns','pattern',['basic','image','random','rds','teststimuli']) # missed audio
        fake_a_package('commands','command',['basic','analysis','pylabplots'])

        fake_a_package('projections','projection',['basic','optimized'])
        # the isn't-in-__all__ shimmy
        import sys
        sys.modules['topo.projections.basic'].CFPOF_SharedWeight = topo.projection.basic.CFPOF_SharedWeight
        sys.modules['topo.projections.basic'].SharedWeightCF = topo.projection.basic.SharedWeightCF


        # rXXXX renamed generatorsheet
        code = \
"""
from topo.sheet.generator import *
"""
        
        fake_a_module('generatorsheet',topo.sheets,code,'topo.sheets')


        # rXXXX renamed functionfamilies
        code = \
"""
from topo.base.functionfamily import *
"""
        fake_a_module('functionfamilies',topo.base,code)

        # CB: maybe a simple link from sys.modules would work for these?
        # (didn't try - see earlier ALERT)

        # rXXXX renamed topo.x.projfns
        from topo import outputfn,responsefn,learningfn
        for x in ['outputfn','responsefn','learningfn']:
            code = \
"""
from topo.%s.projfn import *
"""%x
            # fake topo.x.projfns and topo.xs.projfns since both have existed...
            fake_a_module('projfns',eval('topo.%ss'%x),code,'topo.%ss'%x)
            fake_a_module('projfns',eval('topo.%s'%x),code,'topo.%s'%x)

        # rXXXX renamed topo.misc.numbergenerators
        import topo.misc.numbergenerator
        code = \
"""
from topo.misc.numbergenerator import *
"""
        fake_a_module('numbergenerators',topo.misc,code)

        # rXXXX renamed topo.misc.patternfns
        import topo.misc.patternfn
        code = \
"""
from topo.misc.patternfn import *
"""
        fake_a_module('patternfns',topo.misc,code)
        

        # rXXXX renamed topo.misc.utils
        import topo.misc.util
        code = \
"""
from topo.misc.util import *
"""
        fake_a_module('utils',topo.misc,code)
        

        # rXXXX renamed topo.misc.traces
        import topo.misc.trace
        code = \
"""
from topo.misc.trace import *
"""
        fake_a_module('traces',topo.misc,code)

        # rXXXX duplicate SineGratingDisk removed
        import topo.pattern.basic
        import topo.pattern.teststimuli
        topo.pattern.basic.SineGratingDisk = topo.pattern.teststimuli.SineGratingDisk

        # rXXXX homeostatic of moved into basic
        code = \
"""
from topo.outputfn import HomeostaticMaxEnt # and what else?
"""
        fake_a_module('homeostatic',topo.outputfns,code,'topo.outputfns')

        # rXXXX renamed CFProjection.weights_shape to CFProjection.cf_shape
        param.parameterized._param_name_changes['topo.base.cf.CFProjection']={'weights_shape':'cf_shape'}

        # rXXXX CF's bounds made into read-only attribute (since the value
        # actually comes from the slice).
        # (Problem exposed when Parameterized's __setstate__ changed to
        # set all state attributes, rather than just those in __dict__?)        
        def cf_bounds_property(instance,state):
            try:
                del state['bounds']
            except KeyError:
                pass

        from topo.base.cf import ConnectionField
        preprocess_state(ConnectionField,cf_bounds_property)

        ## If gmpy.mpq not available, use fixedpoint.FixedPoint. 
        ## 
        ## Note that this won't replace gmpy.mpq in the snapshot
        ## itself, because Simulation.time_type will remain gmpy.mpq.
        ## This has the advantage of not affecting the snapshot
        ## itself, but has the disadvantage of showing mpq as the
        ## time_type when it's actually FixedPoint on this run. We
        ## could easily replace time_type, too. I'm not sure which is
        ## better.
        ##
        ## (only implements creation of mpq)
        ##
        ## CEBALERT: not sure what precision should be used for
        ## FixedPoint to replace rational. Should we set the precision
        ## really high?
        code = \
"""
import fixedpoint
class mpq(object):
    def __new__(self,*args,**kw):
        return fixedpoint.FixedPoint(args[0],precision=4)
"""
        # only replace gmpy if necessary
        try:
            import gmpy
        except ImportError:
            param.Parameterized().warning("gmpy.mpq not available: using fixedpoint.FixedPoint as a replacement.")
            fake_a_module('gmpy',source_code=code)

        # allow_None added in r9380
        from topo import param
        def param_add_allow_None(instance,state):
            if 'allow_None' not in state and hasattr(instance.__class__,'allow_None'):
                print instance
                # have to add to state or else slot won't exist on instance, but will
                # exist on class (consequence of using __slots__)
                state['allow_None']=False

        preprocess_state(param.Parameter,param_add_allow_None)



# CEBALERT: rename SnapshotSupport and integrate LegacySupport so that
# the difference is clear.

def LegacySupport():
    """
    Support for running old scripts. Use in conjunction with
    SnapshotSupport.install() to avoid duplication.
    """
    # rXXXX renamed CFProjection.weights_shape to CFProjection.cf_shape 
    import topo.base.cf
    cfp = topo.base.cf.CFProjection
    type.__setattr__(cfp,'weights_shape',cfp.__dict__['cf_shape'])


        

def install_legacy_support():
    SnapshotSupport.install()
    LegacySupport()
