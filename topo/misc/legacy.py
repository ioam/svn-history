"""
Code used to support old snapshots, and update scripts.

$Id$
"""
__version__='$Revision: 8021 $'




### various functions to support loading of old snapshots

def preprocess_state(class_,state_mod_fn): 
    """
    Allow processing of state with state_mod_fn before
    class_.__setstate__(instance,state) is called.
    """
    old_setstate = class_.__setstate__
    def new_setstate(instance,state):
        state_mod_fn(state) 
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



class SnapshotSupport(object):

    @staticmethod
    def install(svn=None):

        # CEBALERT: should add svn version test to see which hacks
        # actually need to be installed. I.e. organize these in
        # suitable way e.g. dictionary.
        # Haven't yet thought about whether or not it's actually possible
        # to get the version number before unpickling...

        def param_remove_hidden(state):
            # Hidden attribute removed from Parameter in r7861
            if 'hidden' in state:
                if state['hidden'] is True:
                    state['precedence']=-1
                del state['hidden']

        def param_add_readonly(state):
            # Hidden attribute added to Parameter in r7975
            if 'readonly' not in state:
                state['readonly']=False

        from ..param import Parameter
        preprocess_state(Parameter,param_remove_hidden)
        preprocess_state(Parameter,param_add_readonly)


        def class_selector_remove_suffixtolose(state):
            # suffix_to_lose removed from ClassSelectorParameter in r8031
            if 'suffix_to_lose' in state:
                del state['suffix_to_lose']

        from topo.base.parameterclasses import ClassSelectorParameter
        preprocess_state(ClassSelectorParameter,class_selector_remove_suffixtolose)



        def cf_rename_slice_array(state):
            ## slice_array was renamed to input_sheet_slice in r7548
            if 'slice_array' in state:
                input_sheet_slice = state['slice_array']
                state['input_sheet_slice'] = input_sheet_slice
                del state['slice_array'] # probably doesn't work

        from topo.base.cf import ConnectionField
        preprocess_state(ConnectionField,cf_rename_slice_array)


        def sim_remove_time_type_attr(state):
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
        from topo.base.parameterclasses import ClassSelectorParameter

        from topo.base.functionfamilies import OutputFn,ResponseFn,LearningFn,\
             CoordinateMapperFn
        d = {"OutputFnParameter":OutputFn,
             "ResponseFnParameter":ResponseFn,
             "LearningFnParameter":LearningFn,
             "CoordinateMapperFnParameter":CoordinateMapperFn}        

        import topo.base.functionfamilies
        for name,arg in d.items():
            fake_a_class(topo.base.functionfamilies,name,
                         ClassSelectorParameter,(arg,))

        from topo.base.cf import CFPOutputFn,CFPResponseFn,CFPLearningFn
        d = {"CFPOutputFnParameter":CFPOutputFn,
             "CFPResponseFnParameter":CFPResponseFn,
             "CFPLearningFnParameter":CFPLearningFn}         

        import topo.base.cf
        for name,arg in d.items():
            fake_a_class(topo.base.cf,name,
                         ClassSelectorParameter,(arg,))

        import topo.base.patterngenerator
        from topo.base.patterngenerator import PatternGenerator
        fake_a_class(topo.base.patterngenerator,"PatternGeneratorParameter",
                     ClassSelectorParameter,(PatternGenerator,))
        ##########
            

        # for snapshots saved before r7901
        class SimSingleton(object):
            """Support for old snapshots."""
            def __setstate__(self,state):
                sim = state['actual_sim']
                from topo.base.parameterclasses import Dynamic
                Dynamic.time_fn = sim.time

        import topo.base.simulation
        topo.base.simulation.SimSingleton=SimSingleton


        # DynamicNumber was removed in rXXXX
        # CEBALERT: missing support 
        class DynamicNumber(object):
            # placeholder: use code from topo.base.parameterclasses.DynamicNumber
            # (e.g. revision 7604)
            def __new__(cls,*args,**kw):
                raise NotImplementedError("""
                Please email ceball at users.sf.net, requesting an
                update to the legacy snapshot support. If possible,
                please make your snapshot available for testing.""")

        import topo.base.parameterclasses
        topo.base.parameterclasses.DynamicNumber = DynamicNumber


        from topo.base.cf import CFProjection
        from numpy import array
        def cfproj_add_cfs(state):
            # cfs attribute added in r8227
            if 'cfs' not in state:
                cflist = state['_cfs']
                state['cfs'] = array(cflist)
        preprocess_state(CFProjection,cfproj_add_cfs)

        
