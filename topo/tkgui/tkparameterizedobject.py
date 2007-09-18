"""
Classes linking ParameterizedObjects and Parameters to Tkinter.

TkParameterizedObject allows graphical representation and manipulation
of any ParameterizedObject's Parameters, in a flexible way. Usually,
it is simply desired to display all the Parameters of a
ParameterizedObject; for this, use ParametersFrame, which extends
TkParameterizedObject. If more flexibility is required, though, it
is possible to use TkParameterizedObject itself.

A typical use of TkParameterizedObject might be in some subclass that
is also a Tkinter.Frame. The Frame serves as the container into which
the representations of the Parameters are placed - although any
suitable Tkinter widget can be used, and there is in fact no need to
sublass TkParameterizedObject. The following example shows this,
displaying the Parameters from two different ParameterizedObjects in a
window:


 ## Existing, non-GUI code
 from topo.base.parameterizedobject import ParameterizedObject
 from topo.base.parameterclasses import Number,StringParameter,BooleanParameter

 class Object1(ParameterizedObject):
     duration = Number(2.0,bounds=(0,None),doc='Duration of measurement')
     displacement = Number(0.0,bounds=(-1,1),doc='Displacement from point A')

 class Object2(ParameterizedObject):
     active_today = BooleanParameter(True,doc='Whether or not to count today')
     operator_name = StringParameter('Zhong Wen',doc='Operator today')

 o1 = Object1()
 o2 = Object2()


 ## Flexible GUI representation 
 import Tkinter
 from topo.tkgui.tkparameterizedobject import TkParameterizedObject

 app_window = Tkinter.Tk()

 t1 = TkParameterizedObject(app_window,extraPO=o1)
 t2 = TkParameterizedObject(app_window,extraPO=o2)

 t1.pack_param('duration')
 t1.pack_param('displacement')
 t2.pack_param('active_today')
 # (choose not to display o2's 'operator_name')


The resulting window exhibits some of the more important features of
TkParameterizedObject: each Parameter is represented by an appropriate
widget (e.g. slider for a Number); type and range checking is handled
already by using Parameters; doc strings are displayed automatically
as pop-up help for each Parameter; changes to the Parameters in the
GUI are instantly reflected in the objects themselves; Parameter
names are formatted nicely for display.

Additionally, it is possible to associate changes to variables with
function calls, display true Parameter variable names, and more (umm
like what) - see the detailed documentation.

Examples of TkParameterizedObject usage can be found in
parametersframe.ParametersFrame (as mentioned above) and
in plotgrouppanel.PlotGroupPanel (where it is used to
allow editing of PlotGroups).


$Id$
"""

# CB: this file has now gone beyond the maximum complexity limit


# CEBALERT: in the same way that parameterizedobject.py does not
# import much, this file should import as little as possible from
# outside basic gui files and topo/base so that it can be used
# independently of as much of topographica as possible.  Right now,
# the only real violation is 'import topo', and the place topo.guimain
# is used (just to pass a message to the messagebar). Instead, should
# pass in the console as an optional argument, and only use it if it's
# not None.  (Also applies to parametersframe.py.)



### CEB: currently working on this file (still have to attend to
# simple ALERTs).


import __main__, sys
import Tkinter, Pmw

from inspect import getdoc
from Tkinter import BooleanVar, StringVar, Frame, Checkbutton, \
     Entry, Button, OptionMenu
from Pmw import Balloon

import topo

from topo.base.parameterizedobject import ParameterizedObject,Parameter, \
     classlist,ParameterizedObjectMetaclass
from topo.base.parameterclasses import BooleanParameter,StringParameter, \
     Number,SelectorParameter,ClassSelectorParameter,ObjectSelectorParameter, \
     StringParameter

from topo.misc.utils import eval_atof

from tkguiwindow import TkPOTaggedSlider



def lookup_by_class(dict_,class_):
    """
    Look for class_ or its superclasses in the keys of dict_; on
    finding a match, return the value (return None if no match found).

    Searches from the most immediate class to the most distant
    (i.e. from class_ to the final superclass of class_).
    """
    v = None
    for c in classlist(class_)[::-1]:
        if c in dict_:
            v = dict_[c] 
            break
    return v


def find_key_from_value(dict_,val):
    """
    Return the key corresponding to val in the values() of dict_
    (i.e. dict_[key]=val), or None if val is not found.

    Note that if there are multiple instances of val in the
    values() of dict_, then any one of them could be
    returned.
    """
    key = None
    for name,object_ in dict_.items():
        if object_==val:
            key=name
    return key
            


# CEBALERT: implement buttons properly
##### Temporary: for easy buttons
#
# buttons are not naturally represented by parameters?
# they're like callableparameters, i guess, but if the
# thing they should call is a method of another object,
# that's a bit tricky
#
# Maybe we should have a parent class that implements the
# non-Parameter specific stuff, then one that bolts on the
# Parameter-specific stuff, and then instead of ButtonParameter we'd
# have TopoButton, or something like that...
#
# Anyway need to be able to do somrthing like call a button
# rather than having all the variously named methods associated
# with buttons.
#
class ButtonParameter(Parameter):

    __slots__ = []
    __doc__ = property((lambda self: self.doc))

    def __init__(self,default="[button]",**params):
        Parameter.__init__(self,default=default,**params)
#####



def parameters(parameterized_object):
    """
    Return a dictionary {name:parameter} of the parameters of
    parameterized_object, where parameterized_object can be an
    instance of ParameterizedObject or ParameterizedObjectMetaclass.
    
    (To list the Parameters, ParameterizedObjectMetaclass has
    classparams(), whereas ParameterizedObject has params();  this
    function selects the appropriate one.)
    """
    if isinstance(parameterized_object,ParameterizedObjectMetaclass):
        return parameterized_object.classparams()
    elif isinstance(parameterized_object,ParameterizedObject):
        return parameterized_object.params()
    else:
        raise TypeError(`parameterized_object`+ \
            " is not a ParameterizedObject or ParameterizedObjectMetaclass.")


class TkParameterizedObjectBase(ParameterizedObject):
    """
    A ParameterizedObject that maintains Tkinter.Variable shadows
    (proxies) of its Parameters. The Tkinter Variable shadows are kept
    in sync with the Parameter values, and vice versa.

    Optionally performs the same for an *additional* shadowed
    ParameterizedObject (extraPO). The Parameters of the extra
    shadowed PO are available via this object (both via the usual
    'dot' attribute access and via dedicated parameter accessors
    declared in this class). 

    The Tkinter.Variable shadows for this ParameterizedObject and any
    extra shadowed one are available under their corresponding
    parameter names in the _tk_vars dictionary.

    (See note 1 for complications arising from name clashes.)
    

    Parameters being represented by TkParameterizedObjectBase also
    have a 'translators' dictionary, allowing mapping between string
    representations of the objects and the objects themselves (for use
    with e.g. a Tkinter.OptionMenu). More information about the
    translators is available from specific translator-related methods
    in this class.


    Notes
    =====
    
    (1) (a) There is an order of precedance for parameter lookup:
        this PO > shadowed PO.

        Therefore, if you create a Parameter for this PO
        with the same name as one of the shadowed PO's Parameters, only
        the Parameter on this PO will be shadowed.

        Example: 'name' is a common attribute. As a
        ParameterizedObject, this object has a 'name' Parameter. Any
        shadowed PO will also have a 'name' Parameter. By default,
        this object's name will be shadowed at the expense of the name
        of the extra shadowed PO.

        The precedence order can be reversed by setting the attribute
        'self_first' on this object to False.


        (b) Along the same lines, an additional complication can arise
        relating specifically to 'dot' attribute lookup.  For
        instance, a sublass of TkParameterizedObject might also
        inherit from Tkinter.Frame. Frame has many of its own
        attributes, including - for example - 'size'. If we shadow a
        ParameterizedObject that has a 'size' Parameter, the
        ParameterizedObject's size Parameter will not be available as
        .size because ('dot') attribute lookup begins on the local
        object and is not overridden by 'self_first'. Using the
        parameter accessors .get_parameter_object('size') or
        .get_parameter_value('size') (and the equivalent set versions)
        avoids this problem.
        


    (2) If a shadowed PO's Parameter value is modified elsewhere, the
        Tkinter Variable shadow is NOT updated until that Parameter value
        or shadow value is requested from this object. Thus requesting the
        value will always return an up-to-date result, but any GUI display
        of the Variable might display a stale value (until a GUI refresh
        takes place).
    """
    # CEBNOTE: Regarding note 1a above...it would be possible - with
    # some extra work - to shadow Parameters that are duplicated on
    # this PO and extraPO. Among other changes, things like the
    # _tk_vars dict would need different (e.g. name on this PO and
    # name on extraPO)

    # CEBNOTE: Regarding note 1b...might be less confusing if we stop
    # parameters of shadowed POs being available as attributes (and
    # use only the parameter access methods instead).

    # CEBNOTE: Regarding note 2 above...if the above becomes a
    # problem, we could have some autorefresh of the vars or a
    # callback of some kind in the parameterized object itself.

    # CEB: because of note 1, attributes of this class should have
    # names that are unlikely to clash (or they should be private);
    # this will make it easier for creators and users of subclasses to
    # avoid name clashes.


    # must exist *before* an instance is init'd
    # (for __getattribute__)
    _extraPO = None

    # CBENHANCEMENT: __repr__ will need some work (display params of
    # subobjects etc?).

    # overrides method from superclass
    def _setup_params(self,**params):
        """
        Parameters that are not in this object itself but are in the
        extraPO get set on extraPO.

        Then calls ParameterizedObject's _setup_params().
        """
        ### a parameter might be passed in for one of the extra_pos;
        ### if a key in the params dict is not a *parameter* of this
        ### PO, then try it on the extra_pos
        for n,p in params.items():
            if n not in self.params():
                self.set_parameter_value(n,p)
                del params[n]

        ParameterizedObject._setup_params(self,**params)

    # CEBALERT: rename extraPO...but to what?
    # Rename change_PO().
    def __init__(self,extraPO=None,self_first=True,**params):
        """


        Translation between displayed values and objects
        ------------------------------------------------

        A Parameter has a value, but that might need some processing
        to become a value suitable for display. For instance, the
        SheetMask() object <SheetMask SheetMask0001923> ...



        Important attributes
        --------------------

        * _extraPO
        

        * self_first
        Determines precedence order for Parameter lookup:
        if True, Parameters of this object take priority whenever
        there is a name clash; if False, Parameters of extraPO take
        priority.

        * param_to_tkvar
        Dictionary indicating Tkinter Variable to use for particular
        Parameter types.

        * param_has_modifyable_choices
        Some parameters are represented by widgets whose options
        can't be changed once created (e.g. OptionMenu), and some
        parameters have a fixed set of options (e.g. Boolean).
        
        * param_immediately_apply_change
        Some types of Parameter are represented with widgets where a
        complete change can be instantaneous (e.g. when dragging a
        slider for a number, the change at each instant should be
        applied). Others, such as Parameter, are represented with
        widgets that do not finish their changes instantaneously
        (e.g. entry into a text box is not be considered finished
        until Return is pressed).

        (Note that in the various dictionaries above, the entry for
        Parameter serves as a default, since keys are looked up by
        class, so any Parameter type not specifically listed will be
        covered by the Parameter entry.)
        

        * obj2str_fn & str2obj_fn

        * translator_creators


        * _tk_vars

        
        """
        assert extraPO is None \
               or isinstance(extraPO,ParameterizedObjectMetaclass) \
               or isinstance(extraPO,ParameterizedObject)

        self.self_first = self_first

        # (Note that, for instance, we don't include Number:DoubleVar.
        # This is because we use Number to control the type, so we
        # don't need restrictions from DoubleVar.)
        self.param_to_tkvar = {BooleanParameter:BooleanVar,
                                     Parameter:StringVar}

        self.param_has_modifyable_choices = {BooleanParameter:False,
                                             SelectorParameter:False,
                                             Parameter:True}

        # CEBALERT: really, this should be in TkParameterizedObject.
        # All changes should be instantaneous here, and
        # TkParameterizedObject (which has the concept of widgets)
        # should override the _update_param method to have some
        # Parameters not be updated immediately.
        self.param_immediately_apply_change = {BooleanParameter:True,
                                               SelectorParameter:True,
                                               Number:False,
                                               Parameter:False}

        self.obj2str_fn = {
            StringParameter: None,
            BooleanParameter: None,
            ButtonParameter: None,
            Number: None,
            SelectorParameter: self.__selector_obj2str,
            Parameter: self.__param_obj2str}

        self.str2obj_fn = {
            StringParameter: None,
            BooleanParameter: None, 
            ButtonParameter: None,
            SelectorParameter: None,
            Number: eval_atof,
            Parameter: lambda x: eval(x,__main__.__dict__)}

        # {Parameter type: create-translator fn}
        self.translator_creators = {
            ClassSelectorParameter: self.csp_thing,
            ObjectSelectorParameter: self.osp_thing,
            Parameter: self.p_thing}
        
        self.change_PO(extraPO)
        super(TkParameterizedObjectBase,self).__init__(**params)


    def change_PO(self,extraPO):
        """
        Shadow the Parameters of extraPO.
        """
        self._extraPO = extraPO
        self._tk_vars = {}
        self.translators = {}

        # always respect the precedence
        for PO in self._source_POs()[::-1]:
            self._init_tk_vars(PO)



    def _source_POs(self,parameterized_object=None):
        """
        Return a correctly ordered* list of ParameterizedObjects in
        which to find Parameters.

        (* ordered by precedence, as defined by self_first)

        Specifying parameterized_object results in the list
        containing only that parameterized_object.
        """
        if parameterized_object:
            sources = [parameterized_object]
        elif not self._extraPO:
            sources = [self]
        elif self.self_first:
            sources = [self,self._extraPO]
        else:
            sources = [self._extraPO,self]
        return sources


    def _init_tk_vars(self,PO):
        """
        Create Tkinter Variable shadows of all Parameters of PO.        
        """
        for name,param in parameters(PO).items():
            self._add_tk_var_entry(PO,name,param)


    def _add_tk_var_entry(self,PO,name,param):
        """
        Add _tk_vars[name] to represent param.
        
        The appropriate Variable is used for each Parameter type.

        Also adds tracing mechanism to keep the Variable and Parameter
        values in sync, and updates the translator dictionary to map
        string representations to the objects themselves.
        """
        self._update_translator(name,param)

        tk_var = lookup_by_class(self.param_to_tkvar,type(param))()
        self._tk_vars[name] = tk_var

        # overwrite Variable's set() with one that will handle
        # transformations to string
        tk_var._original_set = tk_var.set
        tk_var.set = lambda v,x=name: self._set_tk_val(x,v)

        tk_var.set(getattr(PO,name))
        tk_var._last_good_val=tk_var.get() # for reverting
        tk_var.trace_variable('w',lambda a,b,c,p_name=name: self._update_param(p_name))        
        # CB: Instead of a trace, could we override the Variable's
        # set() method i.e. trace it ourselves?  Or does too much
        # happen in tcl/tk for that to work?
        
        # Override the Variable's get() method to guarantee an
        # out-of-date value is never returned.  In cases where the
        # tkinter val is the most recently changed (i.e. when it's
        # edited in the gui, resulting in a trace_variable being
        # called), the _original_get() method is used.
        # CEBALERT: what about other users of the variable? Could they
        # be surprised by the result from get()?
        tk_var._original_get = tk_var.get
        tk_var.get = lambda x=name: self._get_tk_val(x)
        # CEB: document or remove (for TaggedSlider - allows
        # slider to get value when only a string is present)
        tk_var._true_val = lambda x=name: self.get_parameter_value(x)
        

    def _set_tk_val(self,param_name,val):
        """
        Set the tk variable to (the possibly transformed-to-string) val.
        """
        val = self.object2string_ifrequired(param_name,val)
        tk_var = self._tk_vars[param_name]
        tk_var._original_set(val) # trace not called because we're already in trace,
                                  # and tk disables trace activation during trace

    def _get_tk_val(self,param_name):
        """
        Return the (possibly transformed-to-string) value of the
        tk variable representing param_name.
        
        (Before returning the variable's value, ensures it's up to date.)
        """
        tk_val = self._tk_vars[param_name]._original_get() 
        po_val = self.get_parameter_value(param_name)

        po_stringrep = self.object2string_ifrequired(param_name,po_val)

        # CB: document
        # update translators, too, in case there's been external update
        param = self.get_parameter_object(param_name)
        self._update_translator(param_name,param)

        if not tk_val==po_stringrep:
            self._tk_vars[param_name].set(po_stringrep)
        return po_val         
            

    def value_changed(self,name):
        """
        Return True if the displayed value does not equal the object's
        value (and False otherwise).
        """
        displayed_value = self.string2object_ifrequired(name,self._tk_vars[name]._original_get())
        object_value = self.get_parameter_value(name) #getattr(self._extraPO,name)
        
        if displayed_value!=object_value:
            return True
        else:
            return False


    def _update_param(self,param_name,force=False):
        """
        Attempt to set the parameter represented by param_name to the
        value of its corresponding Tkinter Variable.

        If setting the parameter fails (e.g. an inappropriate value
        is set for that Parameter type), the Variable is reverted to
        its previous value.

        (Called by the Tkinter Variable's trace_variable() method.)
        """
        tk_var = self._tk_vars[param_name]

        # tk_var could be ahead of parameter (set in GUI), so use
        # _original_get()
        val = self.string2object_ifrequired(param_name,tk_var._original_get())

        # CB: simplify this
        try:
            sources = self._source_POs()
            
            for po in sources:

                if param_name in parameters(po):
                    parameter = parameters(po)[param_name]

                    ### can only edit constant parameters for class objects
                    if parameter.constant==True and not isinstance(po,ParameterizedObjectMetaclass):
                        return

                    ### only edit a non-immediate parameter type if force is True
                    if not force and not lookup_by_class(self.param_immediately_apply_change,
                                                         type(parameter)):
                        return


                    if self.value_changed(param_name):
                        gui_value_changed=True
                    else:
                        gui_value_changed=False


                    ### use set_in_bounds if it exists
                    # i.e. users of widgets get their values cropped
                    # (no warnings/errors, so e.g. a string in a
                    # tagged slider just goes to the default value)
                    # CEBALERT: set_in_bounds not valid for POMetaclass?
                    if hasattr(parameter,'set_in_bounds') and isinstance(po,ParameterizedObject): 
                        parameter.set_in_bounds(po,val)
                    else:
                        setattr(po,param_name,val)

                    ### call any function associated with GUI set()/modification.
                    # CEBALERT: now I've added on_modify, need to go through and rename
                    # on_change and decide whether each use should be for alteration of 
                    # value or just gui set. Or just have one. etc...
                    if hasattr(tk_var,'_on_change'): tk_var._on_change()

                    if hasattr(tk_var,'_on_modify'):
                        if gui_value_changed: tk_var._on_modify()

                    ### Update the translator, if necessary
                    if lookup_by_class(self.param_has_modifyable_choices,
                                       type(parameter)):
                        self._update_translator(param_name,parameter)

                    return

            assert False, "can't get here!"

            
        except: # everything
            tk_var.set(tk_var._last_good_val)
            raise # whatever the parameter-setting error was

        

    def get_parameter_object(self,name,parameterized_object=None,with_location=False):
        """
        Return the Parameter specified by the name from the sources of
        Parameters in this object (or the specified parameterized_object).
        """
        sources = self._source_POs(parameterized_object)
        
        for po in sources:
            params = parameters(po)
            if name in params:
                if not with_location:
                    return params[name] # a bit hidden
                else:
                    return params[name],po

        raise AttributeError(self.__attr_err_msg(name,sources))
    get_parameter = get_parameter_object # CEBALERT: remove
        
    

#    def get_like_the_gui(self,name):
#        return self._tk_vars[name].get()

##### these guarantee only to get/set parameters #####
    def get_parameter_value(self,name,parameterized_object=None):
        """
        Get the value of the parameter specified by name.
        """
        sources = self._source_POs(parameterized_object)

        for po in sources:
            params = parameters(po)
            if name in params: return getattr(po,name) # also hidden!

        raise AttributeError(self.__attr_err_msg(name,sources))

        
    def set_parameter_value(self,name,val,parameterized_object=None):
        """
        Set the value of the parameter specified by name to val.
        """
        sources = self._source_POs(parameterized_object)

        for po in sources:
            if name in parameters(po).keys(): 
                setattr(po,name,val)
                return # so hidden I forgot to write it until now

        raise AttributeError(self.__attr_err_msg(name,sources))
#######################################################        


###### these lookup attributes in order #####
# (i.e. you could get attribute of self rather than a parameter)
# (might remove these to save confusion: they are useful except when 
#  someone would be surprised to get an attribute of e.g. a Frame (like 'size') when
#  they were expecting to get one of their parameters. Also, means you can't set
#  an attribute a on self if a exists on one of the shadowed objects)

# (also they ignore self_first)

    def __attr_err_msg(self,attr_name,objects):
        if not hasattr(objects,'__len__'):objects=[objects]

        error_string = "'%s' not in %s"%(attr_name,str(objects.pop(0)))

        for o in objects:
            error_string+=" or %s"%str(o)
            
        return error_string
    

    def __getattribute__(self,name):
        """
        If the attribute is found on this object, return it. Otherwise,
        search the list of shadow POs and return from the first match.
        If no match, get attribute error.
        """
        try:
            return object.__getattribute__(self,name)
        except AttributeError:
            extraPO = object.__getattribute__(self,'_extraPO')

            if hasattr(extraPO,name):
                return getattr(extraPO,name) # HIDDEN!

            raise AttributeError(self.__attr_err_msg(name,[self,extraPO]))
                    

    def __setattr__(self,name,val):
        """
        If the attribute already exists on this object, set it. If the attribute
        is found on a shadow PO (searched in order), set it there. Otherwise, set the
        attribute on this object (i.e. add a new attribute).
        """
        try:
            object.__getattribute__(self,name)
            object.__setattr__(self,name,val)
            if name in self._tk_vars: self._tk_vars[name].set(val)
            return # a bit hidden

        except AttributeError:
            if hasattr(self._extraPO,name):
                setattr(self._extraPO,name,val)
                if name in self._tk_vars: self._tk_vars[name].set(val)
                return # also a bit hidden

        # name not found, so set on this object
        object.__setattr__(self,name,val)
            
################################################



# CEBALERT: can't use this after pack_param() unless Tkinter.OptionMenu
# supports changing the list of items after widget creation - might
# need to use Pmw's OptionMenu (which does support that).

# CEBHACKALERT: need to update this; not currently used in any code except testing
    def initialize_ranged_parameter(self,param_name,range_):
        p = self.get_parameter(param_name)

        if hasattr(range_,'__len__'):
            [p.Arange.append(x) for x in range_]
        else:
            p.Arange.append(range_)

        p.default = p.Arange[0]
        self._update_translator(param_name,p)



########## METHODS TO CREATE TRANSLATOR DICTIONARY ENTRIES ############


    def _update_translator(self,name,param=None):
        """
        Map names of objects (for display) to the actual objects.
        """
        if not param: param = self.get_parameter_object(name)
        fn = lookup_by_class(self.translator_creators,type(param))       
        if fn: fn(name,param)



    # CEBNOTE: shouldn't have to distinguish SelectorParameters, but
    # since we want to instantiate the choices for
    # ClassSelectorParameter, we have to.
    def csp_thing(self,name,param):
        """
        Create a translator dictionary entry for the named ClassSelectorParameter.

        Creates mappings between class names (from range()) and
        instances of those classes.
        """
        current_param_value = self.get_parameter_value(name)
        
        translator = self.translators[name]={}
        # store list of OBJECTS (not classes) for ClassSelectorParameter's range
        # (Although CSParam's range uses classes; allows parameters set on the
        # options to persist - matches parametersframe.ParametersFrame.)
        for class_name,class_ in param.range().items():
            translator[class_name] = class_()

        # we want the current_param_value to be in this dictionary, so we replace
        # the entry that has the same class
        for class_name,object_ in translator.items():
            if type(current_param_value)==type(object_):
                translator[class_name] = current_param_value
                break


    def osp_thing(self,name,param):
        """
        Create a translator dictionary entry for the named ObjectSelectorParameter

        Creates mappings between names of objects (from range()) and
        the objects themselves.
        """
        current_param_value = self.get_parameter_value(name)
        
        translator = self.translators[name]={}
        for object_name,object_ in param.range().items():
            translator[object_name] = object_


    def p_thing(self,name,param):
        """
        Create a translator dictionary entry for the named Parameter.

        Creates a mapping between repr(current_value) and current_value.            
        """
        current_param_value = self.get_parameter_value(name)
        self.translators[name]= {repr(current_param_value): current_param_value}

#######################################################################


###METHODS TO CONVERT BETWEEN OBJECTS AND STRING REPRESENTATIONS FOR PARAMETERS###

    def __selector_obj2str(self,param_name,val):
        """
        For a SelectorParameter param_name,         object->str

        For ClassSelectorParameters, 
        
        Defaults to no translation (i.e. if val does not appear in the translator
        dictionary, then val itself is returned).
        """
        param = self.get_parameter_object(param_name)
        assert isinstance(param,SelectorParameter) # CB: eventually remove this
        
        translator = self.translators[param_name]

        ## ClassSelectorParameter
        if isinstance(param,ClassSelectorParameter):
            new_val = val 
            ## CEBALERT: code should be simplified.
            for name,object_ in translator.items():
                if object_==val:
                    new_val = name
                    break
                elif type(object_)==type(val):  # for CSParam, assume that matching class
                    new_val = name              # means we already have a better object from
                                                # whoever called this!
                    translator[name]=val # update translator
                    break
        else:
            new_val = find_key_from_value(translator,val) or val

        return new_val


    def __param_obj2str(self,param_name,obj):
        return repr(obj)
        # CB: should I be doing this instead:
        #if isinstance(obj,str):
        #    return obj
        #else:
        #    return repr(obj)


    def object2string_ifrequired(self,param_name,obj):
        """
        If val is one of the objects in param_name's translator,
        translate to the string.
        """
        param=self.get_parameter_object(param_name)
        obj2string_fn = lookup_by_class(self.obj2str_fn,type(param))

        if obj2string_fn:
            string = obj2string_fn(param_name,obj)
        else:
            string = obj

        return string       
                    


    def string2object_ifrequired(self,param_name,string):
        """
        Change the given string for the named parameter into an object.
        
        If there is a translator for param_name, translate the string
        to the object; otherwise, call convert_string2obj on the
        string.
        """
        param=self.get_parameter_object(param_name)

        ## CB: clean up/exclude CSP/remove [testtkpo failure]
        ######
        # update the  translator incase objectchanged externally
        fn = lookup_by_class(self.translator_creators,type(param))
            
        if fn: fn(param_name,param)
        ######

                
        try:
            ## We have a dictionary entry so just translate
            obj=self.translators[param_name][string]
        except KeyError:
            ## No dictionary entry: might need conversion
            obj = self.convert_string2obj(param_name,string)
            # CEBERRORALERT: silent problem here...
            # e.g. for V1's mask, typing:
            #  SheetMask()
            # gives a warning on the console if SheetMask isn't imported, but
            # because SheetMask is just a Parameter, it does get set to the string
            # "SheetMask()". Were it a Parameter only accepting SheetMasks, then
            # an error would be correctly raised by the Parameter itself.

        
        return obj
    

    # clean up test for guimain (see note at top of file)
    def convert_string2obj(self,param_name,string):
        param=self.get_parameter_object(param_name)
        string2obj_fn = lookup_by_class(self.str2obj_fn,type(param))

        if string2obj_fn:
            
            try:
                obj = string2obj_fn(string)
                #topo.guimain.status_message("OK: %s -> %s"%(string,obj))
                if hasattr(topo,'guimain'):
                    topo.guimain.status_message("OK")
                # CEBALERT: setting colors like this is a hack: need some
                # general method. Also this conflicts with tile.
                if hasattr(self,'representations') and param_name in self.representations:
                    self.representations[param_name]['widget'].config(background="white")
            except Exception, inst:
                m = param_name+": "+str(sys.exc_info()[0])[11::]+" ("+str(inst)+")"
                if hasattr(topo,'guimain'):
                    topo.guimain.status_message(m)
                obj = string

                if hasattr(self,'representations') and param_name in self.representations:
                    self.representations[param_name]['widget'].config(background="red")
            return obj
        else:
            obj=string

        return obj
            
#######################################################################    



##         Example 2: consider the class:
##             class SomeFrame(TkParameterizedObjectBase,Tkinter.Frame)

##         Additionally, creators of subclasses of TkParameterizedObjectBase
##         must consider if any attributes of their new class will block
##         attributes or Parameters of TkParameterizedObjectBase or any
##         shadowed PO.

##         Tkinter.Frame has a number of attributes, some of which have
##         generic names ('size', for instance). If SomeFrame
##         shadows a ParameterizedObject that has a 'size' Parameter,
##         SomeFrame()
        


import _tkinter # (required to get tcl exception class)

class TkParameterizedObject(TkParameterizedObjectBase):
    """
    A TkParameterizedObjectBase that can draw widgets representing the
    Parameters of its ParameterizedObject(s).


    TkParameterizedObject.pretty_parameter
    """

    pretty_parameters = BooleanParameter(default=True,doc=
                                         """Whether to format parameter names, or display
                                         the variable names instead.

                                         Example use:
                                         TkParameterizedObject.pretty_parameters=False

                                         Have all Parameters displayed with variable names
                                         (set on the class).""")

    # CEBALERT: rename 'representations'
    def _set_tk_val(self,param_name,val):
        """
        Calls superclass's version, adding help text for the currently selected item
        of SelectorParameters.
        """
        super(TkParameterizedObject,self)._set_tk_val(param_name,val)

        if isinstance(self.get_parameter_object(param_name),SelectorParameter):
            try:
                w = self.representations[param_name]['widget']
                help_text =  getdoc(self.string2object_ifrequired(param_name,
                                                                  self._tk_vars[param_name]._original_get()))


                ######################################################
                # CEBALERT: for projectionpanel, which currently has
                # to destroy a widget (because Tkinter.OptionMenu's
                # list of choices cannot easily be replaced). See ALERT
                # 'How do you change list [...]' in projectionpanel.py.
                try:
                    self.balloon.bind(w,help_text)
                except _tkinter.TclError:
                    pass
                ######################################################

            except (AttributeError,KeyError):  # could be called before self.representations exists,
                                               # or before param in _tk_vars dict
                pass


    def __init__(self,master,extraPO=None,self_first=True,**params):
        self.master = master

        TkParameterizedObjectBase.__init__(self,extraPO=extraPO,self_first=self_first,**params)

        self.balloon = Balloon(master)

        # map of Parameter classes to appropriate widget-creation method
        self.widget_creators = {
            BooleanParameter:self._create_boolean_widget,
            Number:self._create_number_widget,
            ButtonParameter:self._create_button_widget,
            StringParameter:self._create_string_widget,
            SelectorParameter:self._create_selector_widget}
        
        self.representations = {}  # to store (frame,widget,label) for each param
        
        # (a refresh-the-widgets-on-focus-in method could make the gui
        # in sync with the actual object?)

        

    def pretty_print(self,s):
        """
        Convert a Parameter name s to a string suitable for display,
        if pretty_parameters is True.
        """
        if not self.pretty_parameters:
            return s
        else:
            n = s.replace("_"," ")
            n = n.capitalize()
            return n



### Methods to create widgets ###

    def create_widget(self,name,master,widget_options={},on_change=None,on_modify=None):
        # select the appropriate widget-creation method;
        # default is self._create_string_widget... 
        widget_creation_fn = self._create_string_widget
        # ...but overwrite that with a more specific one, if possible
        for c in classlist(type(self.get_parameter_object(name)))[::-1]:
            if self.widget_creators.has_key(c):
                widget_creation_fn = self.widget_creators[c]
                break
            
        if on_change is not None:
            self._tk_vars[name]._on_change=on_change

        if on_modify is not None:
            self._tk_vars[name]._on_modify=on_modify

        widget=widget_creation_fn(master,name,widget_options)

        # CEBALERT: change to have a label with no text
        if widget.__class__ is Tkinter.Button:
            label = None
        else:
            label = Tkinter.Label(master,text=self.pretty_print(name))

        # disable widgets for constant params
        param,location = self.get_parameter_object(name,with_location=True)
        if param.constant and isinstance(location,ParameterizedObject):
            # (need to be able to set on class, hence location)
            widget.config(state='disabled')

        # will be ok until we need something other than return, then
        # will have to go to one of the specific methods
        
        return widget,label

    
    def _create_button_widget(self,frame,name,widget_options):
        # buttons just need a command, not tracing of a variable
        try:
            command = self._tk_vars[name]._on_change
            del self._tk_vars[name]._on_change
        except AttributeError:
            raise TypeError("No command given for '%s' button."%name)

        return Button(frame,text=self.pretty_print(name),
                      command=command,**widget_options)


    def _create_selector_widget(self,frame,name,widget_options):
        param = self.get_parameter_object(name)
        self._update_translator(name,param)
        
        new_range = self.translators[name].keys()        
        assert len(new_range)>0 # CB: remove
        tk_var = self._tk_vars[name]

        current_value = self.object2string_ifrequired(name,self.get_parameter_value(name))
        if current_value not in new_range:current_value = new_range[0] #whatever was there is out of date now

        tk_var.set(current_value)

        w = OptionMenu(frame,tk_var,*new_range,**widget_options)
        help_text = getdoc(self.string2object_ifrequired(name,self._tk_vars[name]._original_get()))
        self.balloon.bind(w,help_text)
        return w
    

    def _create_number_widget(self,frame,name,widget_options):
        widget = TkPOTaggedSlider(frame,variable=self._tk_vars[name],**widget_options)
        param = self.get_parameter_object(name)

        lower_bound,upper_bound = param.get_soft_bounds()
        if upper_bound is not None and lower_bound is not None:
            # CEBALERT: TaggedSlider.set_bounds() needs BOTH bounds (neither can be None)
            widget.set_bounds(lower_bound,upper_bound) # assumes set_bounds exists on the widget

        param = self.get_parameter_object(name)
        if not lookup_by_class(self.param_immediately_apply_change,type(param)):
            #widget.update_command = lambda e=None,x=name:self.junk(x)
            
            widget.bind('<<TagReturn>>', lambda e=None,x=name: self.junk(x))
            widget.bind('<<TagFocusOut>>', lambda e=None,x=name: self.junk(x))
            widget.bind('<<SliderSet>>', lambda e=None,x=name: self.junk(x))
            
            #widget.bind('<<TaggedSliderSet>>', lambda e=None,x=name: self.junk(x))
            # also bind focus out


        return widget


    def _create_boolean_widget(self,frame,name,widget_options):
        return Checkbutton(frame,variable=self._tk_vars[name],**widget_options)

        
    def _create_string_widget(self,frame,name,widget_options):
        widget = Entry(frame,textvariable=self._tk_vars[name],**widget_options)

        param = self.get_parameter_object(name)
        if not lookup_by_class(self.param_immediately_apply_change,type(param)):
            widget.bind('<Return>', lambda e=None,x=name: self.junk(x))            
            # also bind focus out

        return widget

#################################


    def hide_param(self,name):
        """Hide the representation of Parameter 'name'."""
        self.representations[name]['frame'].pack_forget()
        # CEBNOTE: forgetting label and widget would just hide while
        # still occupying space (i.e. the empty frame stays in place)
        #self.representations[name]['label'].pack_forget()
        #self.representations[name]['widget'].pack_forget()
        # unhide_param would need modifying too
        


    def unhide_param(self,name,new_pack_options={}):
        """
        Un-hide the previously hidden representation of Parameter 'name'.

        Any new pack options supplied overwrite the originally
        supplied ones, but the parent of the widget remains the same.
        """
        # CEBNOTE: new_pack_options not really tested - maybe remove them.
        pack_options = self.representations[name]['pack_options']
        pack_options.update(new_pack_options)
        self.representations[name]['frame'].pack(pack_options)


    def unpack_param(self,name):
        """
        Destroy the representation of Parameter 'name'.

        (unpack and then pack a param if you want to put it in a different
        frame; otherwise use hide and unhide)
        """
        f = self.representations[name]['frame']
        w = self.representations[name]['widget']
        l = self.representations[name]['label']
        o = self.representations[name]['pack_options']

        del self.representations[name]

        for x in [f,w,l]:
            x.destroy()


    def junk(self,param_name):
        self._update_param(param_name,force=True)
        
    
    # CEBALERT: on_change should be on_set (since it's called not only for changes)
    # CB: packing might need to be better (check eg label-widget space)
    def pack_param(self,name,parent=None,widget_options={},on_change=None,on_modify=None,**pack_options):
        """
        Create a widget for the Parameter name, configured according
        to widget_options, and pack()ed according to the pack_options.

        If no parent is specified, defaults to the originally supplied
        master (i.e. that set during __init__).

        on_change is an optional function to call whenever the Parameter's
        corresponding Tkinter Variable's trace_variable indicates that it
        has been set.

        Balloon help is automatically set from the Parameter's doc.

        The widget and label (if appropriate) are enlosed in a Frame
        so they can be manipulated as a single unit.
        
        Returns the widget in case further processing of it is
        required.

        Note that the on_change function (if supplied) will be called
        on creation of the widget.
        
        Examples:
        self.pack_param(name)
        self.pack_param(name,side='left')
        self.pack_param(name,{'width':50},side='top',expand='yes',fill='y')
        """
        frame = Frame(parent or self.master)

        widget,label = self.create_widget(name,frame,widget_options,on_change,on_modify)

        # checkbuttons are 'widget label' rather than 'label widget'
        if widget.__class__ is Tkinter.Checkbutton:  # type(widget) doesn't seem to work
            widget_side='left'; label_side='right'
        else:
            label_side='left'; widget_side='right'
            
        if label: label.pack(side=label_side)
        widget.pack(side=widget_side,expand='yes',fill='x')

        representation = {"frame":frame,"widget":widget,"label":label,"pack_options":pack_options}
        self.representations[name] = representation
                               

        # If there's a label, balloon's bound to it - otherwise, bound
        # to enclosing frame.
        # (E.g. when there's [label] [text_box], only want balloon for
        # label (because maybe more help will be present for what's in
        # the box) but when there's [button], want popup help over the
        # button.)
        self.balloon.bind(label or frame,getdoc(self.get_parameter_object(name)))
        
        frame.pack(pack_options)
        return representation



    # For convenience. Maybe should offer a way to access any attribute on master.
    # Probably too confusing - might remove this, too.
    def title(self,t):
        self.master.title(t)
        


