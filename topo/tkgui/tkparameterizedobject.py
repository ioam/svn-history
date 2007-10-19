"""
Classes linking ParameterizedObjects and Parameters to Tkinter.

TkParameterizedObject allows graphical representation and manipulation
of any ParameterizedObject's Parameters, in a flexible way. Usually,
it is simply desired to display all the Parameters of a
ParameterizedObject; for this, use parametersframe.ParametersFrameWithApply,
which extends TkParameterizedObject. If more flexibility is required,
though, use TkParameterizedObject itself.

TkParameterizedObject adds widget-drawing abilities to TkParameterizedObjectBase.
Documentation begins in TkParameterizedObject (since it's not expected that
TkParameterizedObjectBase will be used directly), but continues in more
detail in TkParameterizedObjectBase. 




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
parametersframe.ParametersFrameWithApply (as mentioned above) and
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
     CallableParameter

from topo.misc.utils import eval_atof, inverse
from topo.misc.filepaths import Filename, resolve_path

from topowidgets import TkPOTaggedSlider
    

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


def keys_sorted_by_value(d, **sort_kwargs):
    """
    Return the keys of d, sorted by value.

    The values of d must be unique (see inverse)
    """
    values = d.values()
    values.sort(**sort_kwargs)
    i = inverse(d)
    return [i[val] for val in values]


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



# Buttons are not naturally represented by parameters?
#
# Maybe we should have a parent class that implements the
# non-Parameter specific stuff, then one that bolts on the
# Parameter-specific stuff, and then instead of ButtonParameter we'd
# have TopoButton, or something like that...
import ImageTk, Image, ImageOps


class ButtonParameter(CallableParameter):
    """
    Parameter representing all Parameter classes that are GUI-specific.

    Can be associated with an image when used in a
    TkParameterizedObject by specifying an image_path (i.e. location
    of an image suitable for PIL, e.g. a PNG, TIFF, or JPEG image) and
    optionally a size (width,height) tuple.


    Note that the button size can also be set when there is no image,
    but instead of being presumed to be in pixels, it is instead
    presumed to be in text units (a Tkinter feature: see
    e.g. http://effbot.org/tkinterbook/button.htm). Therefore, to
    place two identically sized buttons next to each other, with one
    displaying text and the other an image, you first have to convert
    one of the sizes to the other's units.
    """
    # CEBALERT: we should probably solve the above for users,
    # but what a pain!
    __slots__ = ['image_path','size','_hack']
    __doc__ = property((lambda self: self.doc))

    def __init__(self,default=None,image_path=None,size=None,
                 **params):
        CallableParameter.__init__(self,default=default,**params)
        self.image_path = image_path
        self.size = size
        self._hack = []

# CB: would create the photoimage on construction and store it as an
# attribute, except that it gives "RuntimeError: Too early to create
# image". Must be happening before tk starts, or something. So
# instead, return image on demand. Also, because of PIL bug (see
# topoconsole.py "got to keep references to the images") we also store
# a reference to the image each time.
    def get_image(self):
        """
        Return an ImageTk.PhotoImage of the image at image_path
        (or None if image_path is None or an Image cannot be created).
        """
        image = None
        if self.image_path:
            image=ImageTk.PhotoImage(ImageOps.fit(
                Image.open(resolve_path(self.image_path)),self.size or (32,32)))
            self._hack.append(image)

        return image
            



class TkParameterizedObjectBase(ParameterizedObject):
    """
    A ParameterizedObject that maintains Tkinter.Variable shadows
    (proxies) of its Parameters. The Tkinter Variable shadows are kept
    in sync with the Parameter values, and vice versa.

    Optionally performs the same for an *additional* shadowed
    ParameterizedObject (extraPO). The Parameters of the extra
    shadowed PO are available via this object (via coth the usual
    'dot' attribute access and dedicated parameter accessors
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

    # CEBNOTE: avoid (as far as possible) defining Parameters for this
    # object because they might clash with Parameters of objects it
    # eventually represents.


    # CEBNOTE: Regarding note 1a above...it would be possible - with
    # some extra work - to shadow Parameters that are duplicated on
    # this PO and extraPO. Among other changes, things like the
    # _tk_vars dict would need different (e.g. name on this PO and
    # name on extraPO)

    # CEBNOTE: Regarding note 1b...might be less confusing if we stop
    # parameters of shadowed POs being available as attributes (and
    # use only the parameter access methods instead). But having them
    # available as attributes is really convenient.

    # CEBNOTE: Regarding note 2 above...if the above becomes a
    # problem, we could have some autorefresh of the vars or a
    # callback of some kind in the parameterized object itself.
    # (See note in TkParameterizedObject.__init__.)

    # CEB: because of note 1, attributes of this class should have
    # names that are unlikely to clash (or they should be private);
    # this will make it easier for creators and users of subclasses to
    # avoid name clashes.

    # must exist *before* an instance is init'd
    # (for __getattribute__)
    _extraPO = None


    # CEBALERT: fix the more useful repr method
    def __repr__(self): return object.__repr__(self)    
##     def __repr__(self):
##         # Method adds the name of the _extraPO, plus avoids recursion problem (see note).
        
##         if isinstance(self._extraPO,ParameterizedObject):
##             extraPOstring = self._extraPO.__class__.__name__+"(name=%s)"%self._extraPO.name
##         elif isinstance(self._extraPO,ParameterizedObjectMetaclass):
##             extraPOstring = self._extraPO.__name__
##         elif self._extraPO is None:
##             extraPOstring = "None"
##         else:
##             raise TypeError

##         # this is just like in the superclass, except that for a button parameter
##         # calling repr(val) won't work if val is a method of this object (leads
##         # to a recursion error).
##         settings = []
##         for name,val in self.get_param_values():
##             if isinstance(self.get_parameter_object,ButtonParameter):
##                 r = object.__repr__(val)
##             else:
##                 r = repr(val)
##             settings.append("%s=%s"%(name,r))
            
##         return self.__class__.__name__ + "(_extraPO=%s, "%extraPOstring + ", ".join(settings) + ")"


    def _setup_params(self,**params):
        """
        Parameters that are not in this object itself but are in the
        extraPO get set on extraPO. Then calls ParameterizedObject's
        _setup_params().
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
    # Rename change_PO() and anything else related.
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


        * param_has_modifyable_choices
        Some parameters are represented by widgets whose options
        can't be changed once created (e.g. OptionMenu), and some
        parameters have a fixed set of options (e.g. Boolean).
        
        

        * obj2str_fn & str2obj_fn

        * translator_creators

        (Note that in the various dictionaries above, the entry for
        Parameter serves as a default, since keys are looked up by
        class, so any Parameter type not specifically listed will be
        covered by the Parameter entry.)



        * _tk_vars

        
        """
        assert extraPO is None \
               or isinstance(extraPO,ParameterizedObjectMetaclass) \
               or isinstance(extraPO,ParameterizedObject)

        self.self_first = self_first

        ## Which Tkinter Variable to use for each Parameter type
        # (Note that, for instance, we don't include Number:DoubleVar.
        # This is because we use Number to control the type, so we
        # don't need restrictions from DoubleVar.)
        self.__param_to_tkvar = {BooleanParameter:BooleanVar,
                                 Parameter:StringVar}

        self.param_has_modifyable_choices = {BooleanParameter:False,
                                             SelectorParameter:False,
                                             Parameter:True}

        # need to document somewhere that a new parameterclass that
        # only has a string as its value should get None,None
        self.obj2str_fn = {
            StringParameter: None,
            Filename: None,
            BooleanParameter: None,
            Number: None,
            SelectorParameter: self.__selector_obj2str,
            Parameter: self.__param_obj2str}

        self.str2obj_fn = {
            ButtonParameter: None,
            StringParameter: None,
            Filename: None,
            BooleanParameter: None, 
            SelectorParameter: None,
            Number: eval_atof,
            Parameter: lambda x: eval(x,__main__.__dict__)}

        # {Parameter type: create-translator fn}
        self.translator_creators = {
            ClassSelectorParameter: self.csp_thing,
            ObjectSelectorParameter: self.osp_thing,
            ButtonParameter: None,
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



    def _source_POs(self):
        """
        Return a correctly ordered* list of ParameterizedObjects in
        which to find Parameters.

        (* ordered by precedence, as defined by self_first)
        """
        if not self._extraPO:
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

        tk_var = lookup_by_class(self.__param_to_tkvar,type(param))()
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

    
    # CEBALERT: should probably separate into update and get
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
            self._tk_vars[param_name]._original_set(po_stringrep)
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


    def _update_param(self,param_name):
        """
        Attempt to set the parameter represented by param_name to the
        value of its corresponding Tkinter Variable.

        If setting the parameter fails (e.g. an inappropriate value
        is set for that Parameter type), the Variable is reverted to
        its previous value.

        (Called by the Tkinter Variable's trace_variable() method.)
        """
        parameter,sourcePO=self.get_parameter_object(param_name,with_location=True)

        ### can only edit constant parameters for class objects
        if parameter.constant==True and not isinstance(sourcePO,ParameterizedObjectMetaclass):
            return

        tk_var = self._tk_vars[param_name]

        ### before we set the parameter, record if the value has actually changed
        # CB: skip setting if it hasn't changed!
        if self.value_changed(param_name):

            # tk_var could be ahead of parameter (set in GUI), so use
            # _original_get()
            val = self.string2object_ifrequired(param_name,tk_var._original_get())
                        
            ### try to set the parameter to the gui value
            try:
                # use set_in_bounds if it exists
                # i.e. users of widgets get their values cropped
                # (no warnings/errors, so e.g. a string in a
                # tagged slider just goes to the default value)
                # CEBALERT: set_in_bounds not valid for POMetaclass?
                if hasattr(parameter,'set_in_bounds') and isinstance(sourcePO,ParameterizedObject): 
                    parameter.set_in_bounds(sourcePO,val)
                else:
                    setattr(sourcePO,param_name,val)
            except: # everything
                tk_var.set(tk_var._last_good_val)
                raise # whatever the parameter-setting error was


            if hasattr(tk_var,'_on_modify'): tk_var._on_modify()

            ### Update the translator, if necessary
            if lookup_by_class(self.param_has_modifyable_choices,
                               type(parameter)):
                self._update_translator(param_name,parameter)


        ### call any function associated with GUI set()
        # CEBALERT: now I've added on_modify, need to go through and rename
        # on_change and decide whether each use should be for alteration of 
        # value or just gui set. Probably can remove on_change.
        if hasattr(tk_var,'_on_change'): tk_var._on_change()


    def get_source_po(self,name):
        
        sources = self._source_POs()
        
        for po in sources:
            params = parameters(po)
            if name in params:
                return po

        raise AttributeError(self.__attr_err_msg(name,sources))

        
    # CB: change with_location to with_source
    def get_parameter_object(self,name,parameterized_object=None,with_location=False):
        """
        Return the Parameter *object* (not value) specified by name,
        from the sources of Parameters in this object (or the
        specified parameterized_object).

        If with_location=True, returns also the source parameterizedobject.
        """
        source = parameterized_object or self.get_source_po(name)
        parameter_object = parameters(source)[name]

        if not with_location:
            return parameter_object
        else:
            return parameter_object,source
    get_parameter = get_parameter_object # CEBALERT: remove
        


##### these guarantee only to get/set parameters #####
    def get_parameter_value(self,name,parameterized_object=None):
        """
        Get the value of the parameter specified by name.
        """
        source = parameterized_object or self.get_source_po(name)
        return getattr(source,name) 

        
    def set_parameter_value(self,name,val,parameterized_object=None):
        """
        Set the value of the parameter specified by name to val.
        """
        source = parameterized_object or self.get_source_po(name)
        setattr(source,name,val)

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
            # update tkvar
            if name in self._tk_vars:
                self._tk_vars[name]._original_set(self.object2string_ifrequired(name,val))
            return # a bit hidden

        except AttributeError:
            if hasattr(self._extraPO,name):
                setattr(self._extraPO,name,val)
                # update tkvar
                if name in self._tk_vars:
                    self._tk_vars[name]._original_set(self.object2string_ifrequired(name,val))
                return # also a bit hidden

        # name not found, so set on this object
        object.__setattr__(self,name,val)
            
################################################

        

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

        Creates mappings between class names (from get_range()) and
        instances of those classes.
        """
        current_param_value = self.get_parameter_value(name)
        
        translator = self.translators[name]={}
        # store list of OBJECTS (not classes) for ClassSelectorParameter's range
        # (Although CSParam's range uses classes; allows parameters set on the
        # options to persist - matches parametersframe.ParametersFrameWithApply.)
        # (But note, with f as a TkParameterizedObject with CSP x,
        #  g=Gaussian()
        #  f.x=Gaussian()
        #  id(f.x)!=id(g.x)
        # Not sure what behavior's best.)
        for class_name,class_ in param.get_range().items():
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

        Creates mappings between names of objects (from get_range()) and
        the objects themselves.
        """
        current_param_value = self.get_parameter_value(name)
        
        translator = self.translators[name]={}
        for object_name,object_ in param.get_range().items():
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
            new_val = inverse(translator).get(val) or val

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

        ## CB: clean up
        ######
        # update the  translator incase objectchanged externally
        if not isinstance(param,ClassSelectorParameter):
            fn = lookup_by_class(self.translator_creators,type(param))
            if fn: fn(param_name,param)
        ######
                
        try:
            ## We have a dictionary entry so just translate
            obj=self.translators[param_name][string]
        except KeyError:
            ## No dictionary entry: might need conversion
            obj = self.convert_string2obj(param_name,string)
        
        return obj


    # clean up test for guimain (see note at top of file)
    def convert_string2obj(self,param_name,string):
        param=self.get_parameter_object(param_name)
        string2obj_fn = lookup_by_class(self.str2obj_fn,type(param))

        if string2obj_fn:
            
            try:
                # should take param_name as well as string
                obj = string2obj_fn(string)
                #topo.guimain.status_message("OK: %s -> %s"%(string,obj))
                if hasattr(topo,'guimain'):
                    topo.guimain.status_message("OK")
                # CEBALERT: setting colors like this is a hack: need some
                # general method. Also this conflicts with tile.
                if hasattr(self,'representations') and param_name in self.representations:
                    self.representations[param_name]['widget'].config(background=topo.entry_background)
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
    Provide widgets for Parameters of itself and up to one additional
    ParameterizedObject.

    A subclass that defines a Parameter p can display it appropriately
    for manipulation by the user simply by calling
    pack_param('p'). The GUI display and the actual Parameter value
    are automatically synchronized (though see technical notes for
    TkParameterizedObjectBase for more details).

    In general, pack_param() adds a Tkinter.Frame containing a label
    and a widget: 

    ---------------------                     The Parameter's
    |                   |                     'representation'
    | [label]  [widget] |<----frame
    |                   |
    ---------------------

    In the same way, an instance of this class can be used to display
    the Parameters of an existing ParameterizedObject. By passing in
    extraPO=x, where x is an existing ParameterizedObject, a Parameter
    q of x can be displayed in the GUI by calling pack_param('q').

    For representation in the GUI, Parameter values might need to be
    converted between their real values and strings used for display
    (e.g. for a ClassSelectorParameter, the options are really class
    objects, but the user must be presented with a list of strings to
    choose from). Such translation is handled and documented in the
    superclass; the default behaviors can be overridden if required.

    
    (This class simply adds widget drawing to
    TkParameterizedObjectBase. More detail about the shadowing of
    Parameters is available in the documentation for
    TkParameterizedObjectBase.)
    """

    # CEBNOTE: as for TkParameterizedObjectBase, avoid declaring
    # Parameters here (to avoid name clashes with any additional
    # Parameters this might eventually be representing).

    pretty_parameters = BooleanParameter(default=True, hidden=True,
        doc="""Whether to format parameter names, or display the
        variable names instead.

        Example use:
          TkParameterizedObject.pretty_parameters=False
    
        (This causes all Parameters throughout the GUI to be displayed
        with variable names.)
        """)


    def __init__(self,master,extraPO=None,self_first=True,**params):
        """
        Initialize this object with the arguments and attributes
        described below:
        
        extraPO: optional ParameterizedObject for which to shadow
        Parameters (in addition to Parameters of this object; see
        superclass)

        self_first: if True, Parameters on this object take precedence
        over any ones with the same names in the extraPO (i.e. what
        to do if there are name clashes; see superclass)


        Important attributes
        ====================
        
        * param_immediately_apply_change

        Some types of Parameter are represented with widgets where
        a complete change can be instantaneous (e.g.  when
        selecting from an option list, the selection should be
        applied straightaway). Others are represented with widgets
        that do not finish their changes instantaneously
        (e.g. entry into a text box is not considered finished
        until Return is pressed).

        * widget_creators

        A dictionary of methods to create a widget for each Parameter
        type. For special widget options (specific to each particular
        parameter), see the corresponding method's docstring.

        * representations

        After pack_param() is called, a Parameter's representation
        consists of the tuple (frame,widget,label,pack_options) - the
        enclosing frame, the value-containing widget, the label
        holding the Parameter's name, and any options supplied for
        pack(). These can all be accessed through the representations
        dictionary, under the Parameter's name.
        """
        self.master = master
        self.param_immediately_apply_change = {BooleanParameter:True,
                                               SelectorParameter:True,
                                               Number:False,
                                               Parameter:False}

        TkParameterizedObjectBase.__init__(self,extraPO=extraPO,
                                           self_first=self_first,**params)

        self.balloon = Balloon(master)

        self.widget_creators = {
            BooleanParameter:self._create_boolean_widget,
            Number:self._create_number_widget,
            ButtonParameter:self._create_button_widget,
            StringParameter:self._create_string_widget,
            SelectorParameter:self._create_selector_widget}
        
        self.representations = {}  
        
        # CEBNOTE: a refresh-the-widgets-on-focus-in method could make the gui
        # in sync with the actual object (so changes outside the gui could
        # show up when a frame takes focus). Or there could be timer process.


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


    def pack_param(self,name,parent=None,widget_options={},
                   on_change=None,on_modify=None,**pack_options):
        """
        Create a widget for the Parameter name, configured according
        to widget_options, and pack()ed according to the pack_options.

        Pop-up help is automatically set from the Parameter's doc.

        The widget and label (if appropriate) are enlosed in a Frame
        so they can be manipulated as a single unit (see the class
        docstring). The representation
        (frame,widget,label,pack_options) is returned (as well as
        being stored in the representations dictionary).


        * parent is the existing widget that is to be the parent
        (master) of the widget created for this paramter. If no parent
        is specified, defaults to the originally supplied master
        (i.e. that set during __init__).

        * on_change is an optional function to call whenever the
        Parameter's corresponding Tkinter Variable's trace_variable
        indicates that it has been set (this does not necessarily mean
        that the widget's value has changed). When the widget is created,
        the on_change method will be called (because the creation of the
        widget triggers a set in Tkinter).

        * on_modify is an optional function to call whenever the
        corresponding Tkinter Variable is actually changed.
        

        widget_options specified here override anything that might have been
        set elsewhere (e.g. ButtonParameter's size can be overridden here
        if required).


        
        Examples of use:
        pack_param(name)
        pack_param(name,side='left')
        pack_param(name,parent=frame3,on_change=some_func)
        pack_param(name,widget_options={'width':50},side='top',expand='yes',fill='y')
        """
        frame = Frame(parent or self.master)

        widget,label = self._create_widget(name,frame,widget_options,on_change,on_modify)

        # checkbuttons are 'widget label' rather than 'label widget'
        if widget.__class__ is Tkinter.Checkbutton:  # type(widget) doesn't seem to work
            widget_side='left'; label_side='right'
        else:
            label_side='left'; widget_side='right'
            
        if label: label.pack(side=label_side) # label can be None (e.g. for Button)
        widget.pack(side=widget_side,expand='yes',fill='x')

        representation = {"frame":frame,"widget":widget,
                          "label":label,"pack_options":pack_options}
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


    def hide_param(self,name):
        """Hide the representation of Parameter 'name'."""
        if name in self.representations:
            self.representations[name]['frame'].pack_forget()
        # CEBNOTE: forgetting label and widget rather than frame would
        # just hide while still occupying space (i.e. the empty frame
        # stays in place, and so widgets could later be inserted at
        # exact same place)
        #self.representations[name]['label'].pack_forget()
        #self.representations[name]['widget'].pack_forget()
        # unhide_param would need modifying too
        

    def unhide_param(self,name,new_pack_options={}):
        """
        Un-hide the representation of Parameter 'name'.

        Any new pack options supplied overwrite the originally
        supplied ones, but the parent of the widget remains the same.
        """
        # CEBNOTE: new_pack_options not really tested. Are they useful anyway?
        if name in self.representations:
            pack_options = self.representations[name]['pack_options']
            pack_options.update(new_pack_options)
            self.representations[name]['frame'].pack(pack_options)


    def unpack_param(self,name):
        """
        Destroy the representation of Parameter 'name'.

        (unpack and then pack a param if you want to put it in a different
        frame; otherwise simply use hide and unhide)
        """
        f = self.representations[name]['frame']
        w = self.representations[name]['widget']
        l = self.representations[name]['label']

        del self.representations[name]

        for x in [f,w,l]:
            x.destroy()


    def _create_widget(self,name,master,widget_options={},on_change=None,on_modify=None):
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

        return widget,label

    
    def _create_button_widget(self,frame,name,widget_options):
        try:
            command = self._tk_vars[name]._on_change
        except AttributeError:
            raise TypeError("No command given for '%s' button."%name)

        del self._tk_vars[name]._on_change # because we use Button's command instead

        # Calling the parameter (e.g. self.Apply()) is like pressing the button:
        self.__dict__["_%s_param_value"%name]=command
        # like setattr(self,name,command) but without tracing etc

        # (...CEBNOTE: and so you can't edit a tkparameterizedobject
        # w/buttons with another tkparameterizedobject because the
        # button parameters all skip translation etc. Instead should
        # handle their translation. But we're not offering a GUI
        # builder so it doesn't matter.)

        button = Button(frame,command=command)

        button_param = self.get_parameter_object(name)

        image = button_param.get_image()
        if image:
            button['image']=image
            button['relief']='flat'
        else:
            button['text']=self.pretty_print(name)

        # and set size from ButtonParameter
        size = button_param.size
        if size:
            button['width']=size[0]
            button['height']=size[1]

        button.config(**widget_options) # widget_options override things from parameter
        return button


    def _create_selector_widget(self,frame,name,widget_options):
        """

        If widget_options includes 'sort_fn_args', these are passed to
        the sort() method of the list of *objects* available for the
        parameter, and the names are displayed sorted in that order.
        If 'sort_fn_args' is not present, the default is to sort the
        list of names using its sort() method.
        """
        param = self.get_parameter_object(name)
        self._update_translator(name,param)

        ## sort the range for display
        # CEBALERT: extend OptionMenu so that it
        # (a) supports changing its option list (subject of a previous ALERT)
        # (b) supports sorting of its option list
        new_range = self.translators[name].keys()
        if 'sort_fn_args' not in widget_options:
            # no sort specified: defaults to sort()
            new_range.sort()
        else:
            sort_fn_args = widget_options['sort_fn_args']
            del widget_options['sort_fn_args']
            if sort_fn_args is not None:
                new_range = keys_sorted_by_value(self.translators[name],**sort_fn_args)

        assert len(new_range)>0 # CB: remove    

        tk_var = self._tk_vars[name]
        
        # set to the item with highest precedence
        # (i.e. don't respect current value; why was I doing that before?)
        tk_var.set(new_range[0])

        w = OptionMenu(frame,tk_var,*new_range,**widget_options)
        help_text = getdoc(self.string2object_ifrequired(name,tk_var._original_get()))
        self.balloon.bind(w,help_text)
        return w
    

    def _create_number_widget(self,frame,name,widget_options):
        w = TkPOTaggedSlider(frame,variable=self._tk_vars[name],**widget_options)
        param = self.get_parameter_object(name)

        lower_bound,upper_bound = param.get_soft_bounds()
        if upper_bound is not None and lower_bound is not None:
            # TaggedSlider needs BOTH bounds (neither can be None)
            w.set_bounds(lower_bound,upper_bound) 
        param = self.get_parameter_object(name)
        if not lookup_by_class(self.param_immediately_apply_change,type(param)):
            w.bind('<<TagReturn>>', lambda e=None,x=name: self._update_param(x,force=True))
            w.bind('<<TagFocusOut>>', lambda e=None,x=name: self._update_param(x,force=True))
            w.bind('<<SliderSet>>', lambda e=None,x=name: self._update_param(x,force=True))
            
        return w


    def _create_boolean_widget(self,frame,name,widget_options):
        return Checkbutton(frame,variable=self._tk_vars[name],**widget_options)

        
    def _create_string_widget(self,frame,name,widget_options):
        widget = Entry(frame,textvariable=self._tk_vars[name],**widget_options)

        param = self.get_parameter_object(name)
        if not lookup_by_class(self.param_immediately_apply_change,type(param)):
            widget.bind('<Return>', lambda e=None,x=name: self._update_param(x,force=True))
            widget.bind('<FocusOut>', lambda e=None,x=name: self._update_param(x,force=True))

        return widget



    def _update_param(self,param_name,force=False):
        """
        Prevents the superclass's _update_param() method from being
        called unless:
        
        - param_name is a Parameter type that has changes immediately
        applied (see doc for param_immediately_apply_change
        dictionary);

        - force is True.

        (I.e. to update a parameter for which
        param_immediately_apply_change[type(parameter)]==False, call
        this method with force=True. E.g. when <Return> is pressed
        in a text box, this method is called with force=True.)        
        """
        param_obj = self.get_parameter_object(param_name)
        
        if not lookup_by_class(self.param_immediately_apply_change,
                               type(param_obj)) and not force:
            return
        else:
            super(TkParameterizedObject,self)._update_param(param_name)


    def _set_tk_val(self,param_name,val):
        """
        Calls superclass's version, but adds help text for the
        currently selected item of SelectorParameters.
        """
        super(TkParameterizedObject,self)._set_tk_val(param_name,val)

        if isinstance(self.get_parameter_object(param_name),SelectorParameter):
            try:
                w = self.representations[param_name]['widget']
                help_text =  getdoc(self.string2object_ifrequired(
                    param_name,
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

            except (AttributeError,KeyError):
                # could be called before self.representations exists,
                # or before param in _tk_vars dict
                pass




        
    



    # For convenience. Maybe should offer a way to access any attribute on master.
    # Probably too confusing - might remove this, too.
    def title(self,t):
        self.master.title(t)
        


