"""
Classes linking Parameters to Tkinter.

TkParameterized allows flexible graphical representation and
manipulation of a Parameterized's individual Parameters;
ParametersFrame extends TkParameterized, displaying all the
Parameters as a list.



TO BE UPDATED...

Note that TkParameterized extends TkParameterizedBase by
adding widget-drawing abilities; documentation for using these classes
begins at a more useful and simple level in TkParameterized, and
continues in more detail in TkParameterizedBase (an abstract
class).



A typical use of TkParameterized might be in some subclass that
is also a Tkinter.Frame (e.g. PlotGroupPanel). The Frame serves as the
container into which the representations of the Parameters are placed
- although any suitable Tkinter widget can be used, and there is in
fact no need to sublass TkParameterized. The following example
shows this, displaying the Parameters from two different
Parameterizeds in a window:


 ## Existing, non-GUI code
 from topo.base.parameterizedobject import Parameterized
 from topo.base.parameterclasses import Number,StringParameter,BooleanParameter

 class Object1(Parameterized):
     duration = Number(2.0,bounds=(0,None),doc='Duration of measurement')
     displacement = Number(0.0,bounds=(-1,1),doc='Displacement from point A')

 class Object2(Parameterized):
     active_today = BooleanParameter(True,doc='Whether or not to count today')
     operator_name = StringParameter('Zhong Wen',doc='Operator today')

 o1 = Object1()
 o2 = Object2()


 ## Flexible GUI representation 
 import Tkinter
 from topo.tkgui.tkparameterizedobject import TkParameterized

 app_window = Tkinter.Tk()

 t1 = TkParameterized(app_window,extraPO=o1)
 t2 = TkParameterized(app_window,extraPO=o2)

 t1.pack_param('duration')
 t1.pack_param('displacement')
 t2.pack_param('active_today')
 # (choose not to display o2's 'operator_name')


The resulting window exhibits some of the more important features of
TkParameterized: each Parameter is represented by an appropriate
widget (e.g. slider for a Number); type and range checking is handled
already by using Parameters; doc strings are displayed automatically
as pop-up help for each Parameter; changes to the Parameters in the
GUI are instantly reflected in the objects themselves; Parameter
names are formatted nicely for display.

Additionally, it is possible to associate changes to variables with
function calls, display true Parameter variable names, and more (umm
like what) - see the detailed documentation.

Existing examples of TkParameterized usage can be found in
parametersframe.ParametersFrameWithApply (as mentioned above) and
in plotgrouppanel.PlotGroupPanel (where it is used to
allow editing of PlotGroups).


$Id: tkparameterizedobject.py 8444 2008-04-27 05:29:14Z ceball $
"""

### CB: file currently being reorganized.
# This file is too long because the param/gui interface code has
# become too long, and needs cleaning up.



# CEBALERT: in the same way that parameterizedobject.py does not
# import much, this file should import as little as possible from
# outside basic gui files and topo/base so that it can be used
# independently of as much of topographica as possible.

# CEB: currently working on this file (still have to attend to
# simple ALERTs; documentation finished for TkParameterized
# but not for TkParameterizedBase)

# CB: it's quite likely that the way TkParameterizedBase is
# implemented could be simplified. Right now, it still contains
# leftovers of various attempts to get everything working. But
# it does seem to work!



# ERROR: (checking for number equality not correct because of precision,
# so they're listed as 'changed' when in fact they haven't been...at least
# by the user...check that we don't actually introduce a change here by
# displaying numbers!)



## import logging
## import string,time
## log_name= 'guilog_%s'%string.join([str(i) for i in list(time.gmtime())],"")

## logging.basicConfig(level=logging.DEBUG,
##                     format='%(asctime)s %(levelname)s %(message)s',
##                     filename='topo/tkgui/%s'%log_name,
##                     filemode='w')
## from os import popen
## version = popen('svnversion -n').read()
## logging.info("tkgui logging started for %s"%version)



import __main__, sys
import Tkinter
import copy

from inspect import getdoc
from Tkinter import BooleanVar, StringVar, Frame, Checkbutton, \
     Entry, TclError, E, W, Label
from Tile import Combobox

from ..parameterized import Parameterized,ParameterizedMetaclass,\
     classlist

from .. import Boolean,String,Number,Selector,ClassSelector,ObjectSelector,\
     Callable,Dynamic,Parameter

from widgets import FocusTakingButton as Button2, TaggedSlider, Balloon, Menu, \
     askyesno,TkguiWindow



# CEBALERT: copied from topo.misc.filepaths, to make it clear what we
# need. I guess we should consider how much of topo.misc.filepaths
# we might want in topo/params...
########################################
import os.path, sys
application_path = os.path.split(os.path.split(sys.executable)[0])[0]
output_path = application_path

def resolve_path(path,search_paths=[]):
    """
    Find the path to an existing file, searching in the specified
    search paths if the filename is not absolute, and converting a
    UNIX-style path to the current OS's format if necessary.

    To turn a supplied relative path into an absolute one, the path is
    appended to each path in (search_paths+the current working
    directory+the application's base path), in that order, until the
    file is found.

    (Similar to Python's os.path.abspath(), except more search paths
    than just os.getcwd() can be used, and the file must exist.)
    
    An IOError is raised if the file is not found anywhere.
    """
    path = os.path.normpath(path)

    if os.path.isabs(path): return path

    all_search_paths = search_paths + [os.getcwd()] + [application_path]

    paths_tried = []
    for prefix in set(all_search_paths): # does set() keep order?            
        try_path = os.path.join(os.path.normpath(prefix),path)
        if os.path.isfile(try_path): return try_path
        paths_tried.append(try_path)

    raise IOError('File "'+os.path.split(path)[1]+'" was not found in the following place(s): '+str(paths_tried)+'.')

########################################



def inverse(dict_):
    """
    Return the inverse of dictionary dict_.
    
    (I.e. return a dictionary with keys that are the values of dict_,
    and values that are the corresponding keys from dict_.)

    The values of dict_ must be unique.
    """
    idict = dict([(value,key) for key,value in dict_.iteritems()])
    if len(idict)!=len(dict_):
        raise ValueError("Dictionary has no inverse (values not unique).")
    return idict



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


def keys_sorted_by_value_unique(d, **sort_kwargs):
    """
    Return the keys of d, sorted by value.

    The values of d must be unique (see inverse)
    """
    values = d.values()
    values.sort(**sort_kwargs)
    i = inverse(d)
    return [i[val] for val in values]



def is_button(widget):
    return 'command' in widget.config() and not hasattr(widget,'toggle')



# Buttons are not naturally represented by parameters?
#
# Maybe we should have a parent class that implements the
# non-Parameter specific stuff, then one that bolts on the
# Parameter-specific stuff, and then instead of Button we'd
# have TopoButton, or something like that...
import ImageTk, Image, ImageOps

class Button(Callable):
    """
    Parameter representing all Parameter classes that are GUI-specific.

    Can be associated with an image when used in a
    TkParameterized by specifying an image_path (i.e. location
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

    def __init__(self,default=None,image_path=None,size=None,
                 **params):
        Callable.__init__(self,default=default,**params)
        self.image_path = image_path
        self.size = size
        self._hack = []

# CB: would create the photoimage on construction and store it as an
# attribute, except that it gives "RuntimeError: Too early to create
# image". Must be happening before tk starts, or something. So
# instead, return image on demand. Also, because of PIL bug (see
# topoconsole.py "got to keep references to the images") we store
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
            



class TkParameterizedBase(Parameterized):
    """
    A Parameterized that maintains Tkinter.Variable shadows
    (proxies) of its Parameters. The Tkinter Variable shadows are kept
    in sync with the Parameter values, and vice versa.

    Optionally performs the same for an *additional* shadowed
    Parameterized (extraPO). The Parameters of the extra
    shadowed PO are available via this object (via both the usual
    'dot' attribute access and dedicated parameter accessors
    declared in this class). 

    The Tkinter.Variable shadows for this Parameterized and any
    extra shadowed one are available under their corresponding
    parameter names in the _tkvars dictionary.

    (See note 1 for complications arising from name clashes.)
    

    Parameters being represented by TkParameterizedBase also
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
        Parameterized, this object has a 'name' Parameter. Any
        shadowed PO will also have a 'name' Parameter. By default,
        this object's name will be shadowed at the expense of the name
        of the extra shadowed PO.

        The precedence order can be reversed by setting the attribute
        'self_first' on this object to False.


        (b) Along the same lines, an additional complication can arise
        relating specifically to 'dot' attribute lookup.  For
        instance, a sublass of TkParameterized might also
        inherit from Tkinter.Frame. Frame has many of its own
        attributes, including - for example - 'size'. If we shadow a
        Parameterized that has a 'size' Parameter, the
        Parameterized's size Parameter will not be available as
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
    # _tkvars dict would need different (e.g. name on this PO and
    # name on extraPO)

    # CEBNOTE: Regarding note 1b...might be less confusing if we stop
    # parameters of shadowed POs being available as attributes (and
    # use only the parameter access methods instead). But having them
    # available as attributes is really convenient.

    # CEBNOTE: Regarding note 2 above...if the above becomes a
    # problem, we could have some autorefresh of the vars or a
    # callback of some kind in the parameterized object itself.
    # (See note in TkParameterized.__init__.)

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
        
##         if isinstance(self._extraPO,Parameterized):
##             extraPOstring = self._extraPO.__class__.__name__+"(name=%s)"%self._extraPO.name
##         elif isinstance(self._extraPO,ParameterizedMetaclass):
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
        extraPO get set on extraPO. Then calls Parameterized's
        _setup_params().
        """
        ### a parameter might be passed in for one of the extra_pos;
        ### if a key in the params dict is not a *parameter* of this
        ### PO, then try it on the extra_pos
        for n,p in params.items():
            if n not in self.params():
                self.set_parameter_value(n,p)
                del params[n]

        Parameterized._setup_params(self,**params)

    # CEBALERT: rename extraPO...but to what?
    # Rename change_PO() and anything else related.
    def __init__(self,extraPO=None,self_first=True,live_update=True,guimain=None,**params):
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


        

        * obj2str_fn & str2obj_fn

        * translator_creators

        (Note that in the various dictionaries above, the entry for
        Parameter serves as a default, since keys are looked up by
        class, so any Parameter type not specifically listed will be
        covered by the Parameter entry.)



        * _tkvars

        
        """
        assert extraPO is None \
               or isinstance(extraPO,ParameterizedMetaclass) \
               or isinstance(extraPO,Parameterized)

        self.guimain = guimain
        # make self.first etc private

        self._live_update = live_update
        self.self_first = self_first

        ## Which Tkinter Variable to use for each Parameter type
        # (Note that, for instance, we don't include Number:DoubleVar.
        # This is because we use Number to control the type, so we
        # don't need restrictions from DoubleVar.)
        self.__param_to_tkvar = {Boolean:BooleanVar,
                                 Parameter:StringVar}

        # CEBALERT: Parameter is the base parameter class, but ... 
        # at least need a test that will fail when a new param type added
        # Rename
        self.trans={Parameter:Eval_ReprTranslator,
                    Dynamic:Eval_ReprTranslator,
                    ObjectSelector:String_ObjectTranslator,
                    ClassSelector:CSPTranslator,
                    Number:Eval_ReprTranslator,
                    Boolean:BoolTranslator,
                    String:DoNothingTranslator}
        
        self.change_PO(extraPO)
        super(TkParameterizedBase,self).__init__(**params)


    def change_PO(self,extraPO):
        """
        Shadow the Parameters of extraPO.
        """
        self._extraPO = extraPO
        self._tkvars = {}
        self.translators = {}

        # (reverse list to respect precedence)
        for PO in self._source_POs()[::-1]:
            self._init_tkvars(PO)


    def _init_tkvars(self,PO):
        """
        Create Tkinter Variable shadows of all Parameters of PO.        
        """
        for name,param in PO.params().items():
            self._create_tkvar(PO,name,param)
            

    # rename param to param_obj
    def _create_tkvar(self,PO,name,param):
        """
        Add _tkvars[name] to represent param.
        
        The appropriate Variable is used for each Parameter type.

        Also adds tracing mechanism to keep the Variable and Parameter
        values in sync, and updates the translator dictionary to map
        string representations to the objects themselves.
        """
        # CEBALERT: should probably delete any existing tkvar for name
        self._create_translator(name,param)

        tkvar = lookup_by_class(self.__param_to_tkvar,type(param))()
        self._tkvars[name] = tkvar

        # overwrite Variable's set() with one that will handle
        # transformations to string
        tkvar._original_set = tkvar.set
        tkvar.set = lambda v,x=name: self._tkvar_set(x,v)

        tkvar.set(self.get_parameter_value(name,PO))
        tkvar._last_good_val=tkvar.get() # for reverting
        tkvar.trace_variable('w',lambda a,b,c,p_name=name: self._handle_gui_set(p_name))
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
        tkvar._original_get = tkvar.get
        tkvar.get = lambda x=name: self._tkvar_get(x)


################################################################################
# 
################################################################################

    def _handle_gui_set(self,p_name):
        """
        * The callback to use for all GUI variable traces/binds *
        """
        if self._live_update: self._update_param_from_tkvar(p_name)


    def _tkvar_set(self,param_name,val):
        """
        Set the tk variable to (the possibly transformed-to-string) val.
        """
        self.debug("_tkvar_set(%s,%s)"%(param_name,val))
        val = self._object2string(param_name,val)
        tkvar = self._tkvars[param_name]
        tkvar._original_set(val) # trace not called because we're already in trace,
                                  # and tk disables trace activation during trace

    
    # CB: separate into update and get?
    def _tkvar_get(self,param_name):
        """
        Return the value of the tk variable representing param_name.
        
        (Before returning the variable's value, ensures it's up to date.)
        """
        tk_val = self._tkvars[param_name]._original_get() 
        po_val = self.get_parameter_value(param_name)

        po_stringrep = self._object2string(param_name,po_val)

        if not self.translators[param_name].last_string2object_failed and not tk_val==po_stringrep:
            self._tkvars[param_name]._original_set(po_stringrep)
        return tk_val         

        
    def _tkvar_changed(self,name):
        """
        Return True if the displayed value does not equal the object's
        value (and False otherwise).
        """
        self.debug("_tkvar_changed(%s)"%name)
        displayed_value = self._string2object(name,self._tkvars[name]._original_get())
        object_value = self.get_parameter_value(name) #getattr(self._extraPO,name)

        if displayed_value!=object_value:
            changed = True
        else:
            changed = False

        self.debug("..._v_c return %s"%changed)
        return changed


    # CEBALERT: now I've added on_modify, need to go through and rename
    # on_change and decide whether each use should be for alteration of 
    # value or just gui set. Probably can remove on_change.    
    def _update_param_from_tkvar(self,param_name):
        """
        Attempt to set the parameter represented by param_name to the
        value of its corresponding Tkinter Variable.

        If setting the parameter fails (e.g. an inappropriate value
        is set for that Parameter type), the Variable is reverted to
        its previous value.

        (Called by the Tkinter Variable's trace_variable() method.)
        """
        self.debug("TkPOb._update_param_from_tkvar(%s)"%param_name)
        
        parameter,sourcePO=self.get_parameter_object(param_name,with_location=True)

        ### can only edit constant parameters for class objects
        if parameter.constant==True and not isinstance(sourcePO,ParameterizedMetaclass):
            return  ### HIDDEN

        tkvar = self._tkvars[param_name]
        
        if self._tkvar_changed(param_name):

            # don't attempt to set if there was a string-to-object translation error
            if self.translators[param_name].last_string2object_failed:
                return   ### HIDDEN 

            # (use _original_get() because we don't want the tkvar to be reset to
            # the parameter's current value!)
            val = self._string2object(param_name,tkvar._original_get())

            try: 
                self.__set_parameter(param_name,val)
            except: # everything
                tkvar.set(tkvar._last_good_val)
                raise # whatever the parameter-setting error was

            self.debug("set %s to %s"%(param_name,val))
                
            if hasattr(tkvar,'_on_modify'): tkvar._on_modify()

        ### call any function associated with GUI set()
        if hasattr(tkvar,'_on_change'): tkvar._on_change()


################################################################################
# 
################################################################################



    def _source_POs(self):
        """
        Return a list of Parameterizeds in which to find
        Parameters.
        
        The list is ordered by precedence, as defined by self_first.
        """
        if not self._extraPO:
            sources = [self]
        elif self.self_first:
            sources = [self,self._extraPO]
        else:
            sources = [self._extraPO,self]
        return sources




    def get_source_po(self,name):
        """
        Return the Parameterized which contains the parameter 'name'.
        """
        sources = self._source_POs()
        
        for po in sources:
            if name in po.params():
                return po

        raise AttributeError(self.__attr_err_msg(name,sources))

        
    # CB: change with_location to with_source
    def get_parameter_object(self,name,parameterized_object=None,with_location=False):
        """
        Return the Parameter *object* (not value) specified by name,
        from the source_POs in this object (or the
        specified parameterized_object).

        If with_location=True, returns also the source parameterizedobject.
        """
        source = parameterized_object or self.get_source_po(name)
        parameter_object = source.params()[name]

        if not with_location:
            return parameter_object
        else:
            return parameter_object,source



######################################################################
# Attribute lookup

##### these guarantee only to get/set parameters #####
    def get_parameter_value(self,name,parameterized_object=None):
        """
        Return the value of the parameter specified by name.

        If a parameterized_object is specified, looks for the parameter there.
        Otherwise, looks in the source_POs of this object.
        """
        source = parameterized_object or self.get_source_po(name)
        return source.get_value_generator(name) 

        
    def set_parameter_value(self,name,val,parameterized_object=None):
        """
        Set the value of the parameter specified by name to val.

        Updates the corresponding tkvar.
        """
        source = parameterized_object or self.get_source_po(name)
        object.__setattr__(source,name,val)

        # update the tkvar
        if name in self._tkvars:
            self._tkvars[name]._original_set(self._object2string(name,val))


######################################################

########## these lookup attributes in order ##########
# (i.e. you could get attribute of self rather than a parameter)
# (might remove these to save confusion: they are useful except when 
#  someone would be surprised to get an attribute of e.g. a Frame (like 'size') when
#  they were expecting to get one of their parameters. Also, means you can't set
#  an attribute a on self if a exists on one of the shadowed objects)
# (also they (have to) ignore self_first)
    
    def __getattribute__(self,name):
        """
        If the attribute is found on this object, return it. Otherwise,
        return the attribute from the extraPO, if it exists.
        If there is no match, raise an attribute error.
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
        is found on the extraPO, set it there. Otherwise, set the
        attribute on this object (i.e. add a new attribute).
        """
        # use dir() not hasattr() because hasattr uses __getattribute__
        if name in dir(self):
            
            if name in self.params():
                self.set_parameter_value(name,val,self)
            else:
                object.__setattr__(self,name,val)
                
        elif name in dir(self._extraPO):

            if name in self._extraPO.params():
                self.set_parameter_value(name,val,self._extraPO)
            else:
                object.__setattr__(self._extraPO,name,val)

        else:

            # name not found, so set on this object
            object.__setattr__(self,name,val)   
#######################################################


######################################################################



    

######################################################################
# Translation between GUI (strings) and true values

    def _create_translator(self,name,param):
        self.debug("_create_translator(%s,%s)"%(name,param))
        
        translator_type = lookup_by_class(self.trans,type(param))

        # Dynamic parameters only *might* contain a 
        # dynamic value; if such a parameter really is dynamic, we
        # overwrite any more specific class found above
        # (e.g. a Number with a dynamic value will have a numeric
        # translator from above, so we replace that)
        if param_is_dynamically_generated(param,self.get_source_po(name)) or name in self.allow_dynamic:
            translator_type = self.trans[Dynamic]
            
        self.translators[name]=translator_type(param,initial_value=self.get_parameter_value(name))

        self.translators[name].guimain = self.guimain


    # CEB: doc replace & generalize,  or change
    def _object2string(self,param_name,obj,replace=True):
        """
        If val is one of the objects in param_name's translator,
        translate to the string.
        """
        self.debug("object2string(%s,%s)"%(param_name,obj))
        translator = self.translators[param_name]

        if replace is False:
            translator=copy.deepcopy(translator)
            
        
        return translator.object2string(obj)              


    def _string2object(self,param_name,string):
        """
        Change the given string for the named parameter into an object.
        
        If there is a translator for param_name, translate the string
        to the object; otherwise, call convert_string2obj on the
        string.
        """
        self.debug("string2object(%s,%s)"%(param_name,string))
        translator = self.translators[param_name]
        o = translator.string2object(string)
        self.debug("...s2o return %s, type %s"%(o,type(o)))
        return o

######################################################################

    def __attr_err_msg(self,attr_name,objects):
        """
        Helper method: return the 'attr_name is not in objects' message.
        """
        if not hasattr(objects,'__len__'):objects=[objects]

        error_string = "'%s' not in %s"%(attr_name,str(objects.pop(0)))

        for o in objects:
            error_string+=" or %s"%str(o)
            
        return error_string


    def __set_parameter(self,param_name,val):
        """
        Helper method:
        """
        # use set_in_bounds if it exists
        # i.e. users of widgets get their values cropped
        # (no warnings/errors, so e.g. a string in a
        # tagged slider just goes to the default value)
        # CEBALERT: set_in_bounds not valid for POMetaclass?
        parameter,sourcePO=self.get_parameter_object(param_name,with_location=True)
        if hasattr(parameter,'set_in_bounds') and isinstance(sourcePO,Parameterized): 
            parameter.set_in_bounds(sourcePO,val)
        else:
            setattr(sourcePO,param_name,val)
                        






class TkParameterized(TkParameterizedBase):
    """
    Provide widgets for Parameters of itself and up to one additional
    Parameterized.

    A subclass that defines a Parameter p can display it appropriately
    for manipulation by the user simply by calling
    pack_param('p'). The GUI display and the actual Parameter value
    are automatically synchronized (though see technical notes in
    TkParameterizedBase's documentation for more details).

    In general, pack_param() adds a Tkinter.Frame containing a label
    and a widget: 

    ---------------------                     The Parameter's
    |                   |                     'representation'
    | [label]  [widget] |<----frame
    |                   |
    ---------------------

    In the same way, an instance of this class can be used to display
    the Parameters of an existing Parameterized. By passing in
    extraPO=x, where x is an existing Parameterized, a Parameter
    q of x can be displayed in the GUI by calling pack_param('q').

    For representation in the GUI, Parameter values might need to be
    converted between their real values and strings used for display
    (e.g. for a ClassSelectorParameter, the options are really class
    objects, but the user must be presented with a list of strings to
    choose from). Such translation is handled and documented in the
    TkParameterizedBase; the default behaviors can be overridden
    if required.

    (Note that this class simply adds widget drawing to
    TkParameterizedBase. More detail about the shadowing of
    Parameters is available in the documentation for
    TkParameterizedBase.)
    """

    # CEBNOTE: as for TkParameterizedBase, avoid declaring
    # Parameters here (to avoid name clashes with any additional
    # Parameters this might eventually be representing).

    pretty_parameters = Boolean(default=True,precedence=-1,
        doc="""Whether to format parameter names, or display the
        variable names instead.

        Example use:
          TkParameterized.pretty_parameters=False
    
        (This causes all Parameters throughout the GUI to be displayed
        with variable names.)
        """)


    def __init__(self,master,extraPO=None,self_first=True,guimain=None,**params):
        """
        Initialize this object with the arguments and attributes
        described below:
        
        extraPO: optional Parameterized for which to shadow
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

        self.allow_dynamic = []
        self.param_immediately_apply_change = {Boolean:True,
                                               Selector:True,
                                               Number:False,
                                               Parameter:False}

        TkParameterizedBase.__init__(self,extraPO=extraPO,
                                           self_first=self_first,
                                           **params)

        self.balloon = Balloon(master)

        self.widget_creators = {
            Boolean:self._create_boolean_widget,
            Dynamic:self._create_string_widget,
            Number:self._create_number_widget,
            Button:self._create_button_widget,
            String:self._create_string_widget,
            Selector:self._create_selector_widget}
        
        self.representations = {}  
        
        # CEBNOTE: a refresh-the-widgets-on-focus-in method could make the gui
        # in sync with the actual object (so changes outside the gui could
        # show up when a frame takes focus). Or there could be timer process.


        self.popup_menu = Menu(master, tearoff=0)
        self.test_var = BooleanVar()
        self.popup_menu.add("checkbutton",indexname="dynamic",label="Enter dynamic value?",
                            state="disabled",command=self._switch_dynamic,
                            variable=self.test_var)


    def _param_right_click(self,event,param_name):
        
        param,po = self.get_parameter_object(param_name,with_location=True)
        currently_dynamic = param_is_dynamically_generated(param,po)
        
        if hasattr(param,'_value_is_dynamic') and not currently_dynamic:
            self._right_click_param = param_name
            state = "normal"
        else:
            self._right_click_param = None
            state = "disabled"

        self.popup_menu.entryconfig("dynamic",state=state)

        self.test_var.set(currently_dynamic or param_name in self.allow_dynamic) 
        self.popup_menu.tk_popup(event.x_root,
                                 event.y_root)



################################################################################
# 
################################################################################
 
    def _update_param_from_tkvar(self,param_name,force=False):
        """
        Prevents the superclass's _update_param_from_tkvar() method from being
        called unless:
        
        * param_name is a Parameter type that has changes immediately
          applied (see doc for param_immediately_apply_change
          dictionary);

        * force is True.

        (I.e. to update a parameter for which
        param_immediately_apply_change[type(parameter)]==False, call
        this method with force=True. E.g. when <Return> is pressed in
        a text box, this method is called with force=True.)
        """
        self.debug("TkPO._update_param_from_tkvar(%s)"%param_name)
        
        param_obj = self.get_parameter_object(param_name)
        
        if not lookup_by_class(self.param_immediately_apply_change,
                               type(param_obj)) and not force:
            return
        else:
            super(TkParameterized,self)._update_param_from_tkvar(param_name)


            
    def _tkvar_set(self,param_name,val):
        """
        Calls superclass's version, but adds help text for the
        currently selected item of SelectorParameters.
        """
        super(TkParameterized,self)._tkvar_set(param_name,val)

        if isinstance(self.get_parameter_object(param_name),Selector):
            try:
                w = self.representations[param_name]['widget']
                help_text =  getdoc(self._string2object(
                    param_name,
                    self._tkvars[param_name]._original_get()))


                ######################################################
                # CEBALERT: for projectionpanel, which currently has
                # to destroy a widget (because Tkinter.OptionMenu's
                # list of choices cannot easily be replaced). See ALERT
                # 'How do you change list [...]' in projectionpanel.py.
                try:
                    self.balloon.bind(w,help_text)
                except TclError:
                    pass
                ######################################################

            except (AttributeError,KeyError):
                # could be called before self.representations exists,
                # or before param in _tkvars dict
                pass




    ### Use in callbacks

    def _handle_gui_set(self,p_name,force=False):
        """Override the superclass's method to X and allow status indications."""
        #logging.info("%s._handle_gui_set(%s,force=%s)"%(self,p_name,force))
        if self._live_update:
            self._update_param_from_tkvar(p_name,force)

        self._indicate_tkvar_status(p_name)



    ### Simulate GUI actions

    def gui_set_param(self,param_name,val):
        """Simulate setting the parameter in the GUI."""
        self._tkvar_set(param_name,val)  # ERROR: presumably calls trace stuff twice
        self._handle_gui_set(param_name,force=True)

    def gui_get_param(self,param_name):
        """Simulate getting the parameter in the GUI."""
        return self._tkvars[param_name].get()



################################################################################
# End 
################################################################################





################################################################################
#
################################################################################

    # some refactoring required: should be a base method that's to do
    # with adding a representation for a parameter. then this stuff
    # would go in it.
    def _post_add_param(self,param_name):
        l = self.representations[param_name]['label']
        if l is not None:
            l.bind('<<right-click>>',lambda event: \
                   self._param_right_click(event,param_name))


    # CEBALERT: rename on_change and on_modify
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


        * parent is an existing widget that is to be the parent
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
        set elsewhere (e.g. Button's size can be overridden here
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
                          "label":label,"pack_options":pack_options,
                          "on_change":on_change,"on_modify":on_modify,
                          "widget_options":widget_options}                       
        self.representations[name] = representation

        # If there's a label, balloon's bound to it - otherwise, bound
        # to enclosing frame.
        # (E.g. when there's [label] [text_box], only want balloon for
        # label (because maybe more help will be present for what's in
        # the box) but when there's [button], want popup help over the
        # button.)
        param_obj = self.get_parameter_object(name)
        help_text = getdoc(param_obj)

        if param_obj.default is not None:
            # some params appear to have no docs!!!
            if help_text is not None:
                help_text+="\n\nDefault: %s"%self._object2string(name,param_obj.default,replace=False)
        
        self.balloon.bind(label or frame,help_text)
        
        frame.pack(pack_options)

        self._indicate_tkvar_status(name)

        self._post_add_param(name)
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


    def repack_param(self,name):

        f = self.representations[name]['frame']
        w = self.representations[name]['widget']
        l = self.representations[name]['label']
        o = self.representations[name]['pack_options']
        on_change = self.representations[name]['on_change']
        on_modify = self.representations[name]['on_modify']
        
        w.destroy(); l.destroy()        

        param_obj,PO = self.get_parameter_object(name,with_location=True)
        self._create_tkvar(PO,name,param_obj)
        
        self.pack_param(name,f,on_change=on_change,on_modify=on_modify,**o)


    def _switch_dynamic(self,name=None,dynamic=False):

        param_name = name or self._right_click_param
        param,po = self.get_parameter_object(param_name,with_location=True)
        if not hasattr(param,'_value_is_dynamic'):
            return
        
        if param_name in self.allow_dynamic:
            self.allow_dynamic.remove(param_name)
        else:
            self.allow_dynamic.append(param_name)

        self.repack_param(param_name)





################################################################################
#
################################################################################





################################################################################
# WIDGET CREATION
################################################################################

    def _create_widget(self,name,master,widget_options={},on_change=None,on_modify=None):
        """
        Return widget,label for parameter 'name', each having the master supplied

        The appropriate widget creation method is found from the
        widget_creators dictionary; see individual widget creation
        methods for details to each type of widget.
        """
        # select the appropriate widget-creation method;
        # default is self._create_string_widget... 
        widget_creation_fn = self._create_string_widget

        param_obj,source_po = self.get_parameter_object(name,with_location=True)

        if not (param_is_dynamically_generated(param_obj,source_po) or name in self.allow_dynamic):
            # ...but overwrite that with a more specific one, if possible
            for c in classlist(type(param_obj))[::-1]:
                if self.widget_creators.has_key(c):
                    widget_creation_fn = self.widget_creators[c]
                    break
        elif name not in self.allow_dynamic:
            self.allow_dynamic.append(name)
                    
            
        if on_change is not None:
            self._tkvars[name]._on_change=on_change

        if on_modify is not None:
            self._tkvars[name]._on_modify=on_modify

        widget=widget_creation_fn(master,name,widget_options)

        # Is widget a button (but not a checkbutton)? If so, no label wanted.
        # CEBALERT 'notNonelabel': change to have a label with no text
        if is_button(widget): 
            label = None
        else:
            label = Tkinter.Label(master,text=self.__pretty_print(name))

        # disable widgets for constant params
        if param_obj.constant and isinstance(source_po,Parameterized):
            # (need to be able to set on class, hence check it's PO not POMetaclass
            widget.config(state='disabled')

        return widget,label

        
    def _create_button_widget(self,frame,name,widget_options):
        """
        Return a FocusTakingButton to represent Parameter 'name'.

        Buttons require a command, which should have been specified as the
        'on_change' function passed to pack_param().

        After creating a button for a Parameter param, self.param() also
        executes the button's command.

        If the Button was declared with an image, the button will
        have that image (and no text); otherwise, the button will display
        the (possibly pretty_print()ed) name of the Parameter.        
        """
        try:
            command = self._tkvars[name]._on_change
        except AttributeError:
            raise TypeError("No command given for '%s' button."%name)

        del self._tkvars[name]._on_change # because we use Button's command instead

        # Calling the parameter (e.g. self.Apply()) is like pressing the button:
        self.__dict__["_%s_param_value"%name]=command
        # like setattr(self,name,command) but without tracing etc

        # (...CEBNOTE: and so you can't edit a tkparameterizedobject
        # w/buttons with another tkparameterizedobject because the
        # button parameters all skip translation etc. Instead should
        # handle their translation. But we're not offering a GUI
        # builder so it doesn't matter.)

        button = Button2(frame,command=command)

        button_param = self.get_parameter_object(name)

        image = button_param.get_image()
        if image:
            button['image']=image
            #button['relief']='flat'
        else:
            button['text']=self.__pretty_print(name)
            

        # and set size from Button
        size = button_param.size
        #if size:
        #    button['width']=size[0]
        #    button['height']=size[1]

        button.config(**widget_options) # widget_options override things from parameter
        return button

    def update_selector(self,name):

        if name in self.representations:
            widget_options = self.representations[name]["widget_options"]

            new_range,widget_options = self._X(name,widget_options)

            w = self.representations[name]['widget']
            # hACK: tuple to work around strange list parsing tkinter/tcl
            w.configure(values=tuple(new_range)) # what a mess
            #w.configure(state='readonly') # CEBALERT: why necessary?
            # does it get changed somewhere else by mistake? e.g. does
            # plotgrouppanel switch disabled to normal and normal to
            # disabled without checking that normal isn't readonly?


    def _X(self,name,widget_options):

        self.translators[name].update()
        
        new_range = self.translators[name].cache.keys()

        if 'sort_fn_args' not in widget_options:
            # no sort specified: defaults to sort()
            new_range.sort()
        else:
            sort_fn_args = widget_options['sort_fn_args']
            del widget_options['sort_fn_args']
            if sort_fn_args is not None:
                new_range = keys_sorted_by_value_unique(self.translators[name].cache,**sort_fn_args)

        assert len(new_range)>0 # CB: remove    

        tkvar = self._tkvars[name]
        

        if 'new_default' in widget_options:
            if widget_options['new_default']:
                current_value = new_range[0]
            del widget_options['new_default']
        else:
            current_value = self._object2string(name,self.get_parameter_value(name))
            if current_value not in new_range:
                current_value = new_range[0] # whatever was there is out of date now

        tkvar.set(current_value)

        return new_range,widget_options
        

    def _create_selector_widget(self,frame,name,widget_options):
        """
        Return a Tkinter.OptionMenu to represent Parameter 'name'.

        In addition to Tkinter.OptionMenu's usual options, the
        following additional ones may be included in widget_options:

        * sort_fn_args: if widget_options includes 'sort_fn_args',
          these are passed to the sort() method of the list of
          *objects* available for the parameter, and the names are
          displayed sorted in that order.  If 'sort_fn_args' is not
          present, the default is to sort the list of names using its
          sort() method.

        * new_default: if widget_options includes 'new_default':True,
          the currently selected value for the widget will be set
          to the first item in the (possibly sorted as above) range.
          Otherwise, the currently selected value will be left as the
          current value.
        """
        #param = self.get_parameter_object(name)
        #self._update_translator(name,param)

        ## sort the range for display
        # CEBALERT: extend OptionMenu so that it
        # (a) supports changing its option list (subject of a previous ALERT)
        # (b) supports sorting of its option list
        # (c) supports selecting a new default

        new_range,widget_options = self._X(name,widget_options)

        tkvar = self._tkvars[name]

        # Combobox looks bad with standard theme on my ubuntu
        # (and 'changed' marker - blue text - not visible).
        w = Combobox(frame,textvariable=tkvar,
                     values=new_range,state='readonly',
                     **widget_options)

        # CEBALERT: somehow Combobox sets textvariable without calling
        # its set() method! So how can I possibly track that the
        # variable's been set? So (hack) track the ComboBox event
        # itself. Shouldn't be necessary, should be checked as tk
        # versions are upgraded...
        def f(event,name=name):
            v = self._tkvars[name].get()
            self._tkvar_set(name,v)
        w.bind("<<ComboboxSelected>>",f)

        # CEBALERT: hack to 
        w._readonly_=True
        

        help_text = getdoc(self._string2object(name,tkvar._original_get()))
        self.balloon.bind(w,help_text)
        return w
    

    def _create_number_widget(self,frame,name,widget_options):
        """
        Return a TaggedSlider to represent parameter 'name'.

        The slider's bounds are set to those of the Parameter.
        """
        w = TaggedSlider(frame,variable=self._tkvars[name],**widget_options)
        param = self.get_parameter_object(name)

        lower_bound,upper_bound = param.get_soft_bounds()
        if upper_bound is not None and lower_bound is not None:
            # TaggedSlider needs BOTH bounds (neither can be None)
            w.set_bounds(lower_bound,upper_bound) 

        # have to do the lookup because subclass might override default
        if not lookup_by_class(self.param_immediately_apply_change,type(param)):
            w.bind('<<TagReturn>>', lambda e=None,x=name: self._handle_gui_set(x,force=True))
            w.bind('<<TagFocusOut>>', lambda e=None,x=name: self._handle_gui_set(x,force=True))
            w.bind('<<SliderSet>>', lambda e=None,x=name: self._handle_gui_set(x,force=True))
            
        return w


    def _create_boolean_widget(self,frame,name,widget_options):
        """Return a Tkinter.Checkbutton to represent parameter 'name'."""
        return Checkbutton(frame,variable=self._tkvars[name],**widget_options)

        
    def _create_string_widget(self,frame,name,widget_options):
        """Return a Tkinter.Entry to represent parameter 'name'."""
        widget = Entry(frame,textvariable=self._tkvars[name],**widget_options)
        param = self.get_parameter_object(name)
        if not lookup_by_class(self.param_immediately_apply_change,type(param)):
            widget.bind('<Return>', lambda e=None,x=name: self._handle_gui_set(x,force=True))
            widget.bind('<FocusOut>', lambda e=None,x=name: self._handle_gui_set(x,force=True))
        return widget

################################################################################
# End WIDGET CREATION
################################################################################



    # CB: the colors etc for indication are only temporary
    def _indicate_tkvar_status(self,param_name,status=None):
        """
        Set the parameter's label to:
         - blue if the GUI value differs from that set on the object
         - red if the text doesn't translate to a correct value
         - black if the GUI and object have the same value
        """
        if self.translators[param_name].last_string2object_failed:
            status = 'error'

        self._set_widget_status(param_name,status)


    # this scheme is incompatible with tile
    # (tile having the right idea about how to do this kind of thing!)
    def _set_widget_status(self,param_name,status):

        if hasattr(self,'representations') and param_name in self.representations:

            widget = self.representations[param_name]['widget']

            states = {'error':'red','changed':'blue',None:'black'}

            try:
                if is_button(widget):
                    return
                else:
                    widget.config(foreground=states[status])
            except TclError:  #CEBALERT uh-oh
                pass

                            



    def __pretty_print(self,s):
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







######################################################################
######################################################################

class Translator(object):
    """
    Abstract class that

    Translators handle translation between objects and their
    string representations in the GUI.

        last_string2object_failed is a flag that can be set to indicate that
        the last string-to-object translation failed.
        (TkParameterized checks this attribute for indicating errors to
        the user.)

    """
    last_string2object_failed = False

    def __init__(self,param,initial_value=None):
        self.param = param
    
    def string2object(self,string_):
        raise NotImplementedError

    def object2string(self,object_):
        raise NotImplementedError

    def _pass_out_msg(self,msg):
        if self.guimain:
            self.guimain.status_message(msg)


class DoNothingTranslator(Translator):
    """
    Performs no translation. For use with Parameter types such as
    Boolean and String, where the representation
    of the object in the GUI is the object itself.
    """
    def string2object(self,string_):
        return string_

    def object2string(self,object_):
        return object_

# seems to be necessary after switching to tk 8.5
# need to check it's really necessary
class BoolTranslator(DoNothingTranslator):
    def string2object(self,string_):
        return bool(string_)


# Error messages: need to change how they're reported



class Eval_ReprTranslator(Translator):
    """
    Translates a string to an object by eval()ing the string in
    __main__.__dict__ (i.e. as if the string were typed at the
    commandline), and translates an object to a string by
    repr(object).
    """
    
    last_object = None
    last_string = None

    def __init__(self,param,initial_value=None):
        super(Eval_ReprTranslator,self).__init__(param,initial_value)
        self.last_string = self.object2string(initial_value)
        self.last_object = initial_value        

    # the whole last_string deal is required because of execing in main
    def string2object(self,string_):
        if string_!=self.last_string:
            try:
                self.last_object = eval(string_,__main__.__dict__)
                self.last_string = string_
                self._pass_out_msg("OK")
            except Exception,inst:
                m = str(sys.exc_info()[0])[11::]+" ("+str(inst)+")"
                self._pass_out_msg(m)
                self.last_string2object_failed=True
                return string_ # HIDDEN

        self.last_string2object_failed=False
        return self.last_object

        
    def object2string(self,object_):
        if object_==self.last_object:
            return self.last_string
        else:
            string_ = repr(object_)
            self.last_object = object_
            self.last_string = string_
            return string_


        

class String_ObjectTranslator(Translator):

    cache = {}
    
    def __init__(self,param,initial_value=None):
        super(String_ObjectTranslator,self).__init__(param,initial_value)
        self.cache = {}
        self.update()
        
    def string2object(self,string_):
        return self.cache.get(string_) or string_
        
    def object2string(self,object_):
        return inverse(self.cache).get(object_) or object_

    def update(self):
        self.cache = self.param.get_range()
        
        

class CSPTranslator(String_ObjectTranslator):
        
    def string2object(self,string_):
        obj = self.cache.get(string_) or string_

        ## instantiate if it's just a class
        if isinstance(obj,type) and isinstance(string_,str):
            obj = obj()
            self.cache[string_]=obj

        return obj
        
    def object2string(self,object_):
        ## replace class if we already have object
        for name,obj in self.cache.items():
            if type(object_)==obj or type(object_)==type(obj):
                self.cache[name]=object_
        ##

        return inverse(self.cache).get(object_) or object_
    
    def update(self):
        self.cache = self.param.get_range()



def param_is_dynamically_generated(param,po):

    if not hasattr(param,'_value_is_dynamic'):
        return False

    if isinstance(po,Parameterized):
        return param._value_is_dynamic(po)
    elif isinstance(po,ParameterizedMetaclass):
        return param._value_is_dynamic(None)
    else:
        raise ValueError("po must be a Parameterized or ParameterizedMetaclass.")



















## """
## Classes for graphically manipulating all the Parameters of a Parameterized.

## ParametersFrame and ParametersFrameWithApply display the Parameters of
## a supplied Parameterized. Both allow these Parameters to be
## edited; ParametersFrame applies changes immediately as they are made,
## whereas ParametersFrameWithApply makes no changes until a confirmation
## is given (by pressing the 'Apply' button).


## ParametersFrame extends TkParameterized; see TkParameterized
## for the underlying details of representing Parmeters in the GUI.


## $Id: tkparameterizedobject.py 8444 2008-04-27 05:29:14Z ceball $
## """
## __version__='$Revision: 8444 $'


# CEB: still working on this file


# KNOWN ISSUES
#
# - Defaults button doesn't work for Selectors (need to insert
#   new (class default) object into the list).
#

# (check Defaults btn with dynamic params)




def keys_sorted_by_value(d):
    """
    Return the keys of dictionary d sorted by value.
    """
    # By Daniel Schult, 2004/01/23
    # http://aspn.activestate.com/ASPN/Python/Cookbook/Recipe/52306
    items=d.items()
    backitems=[ [v[1],v[0]] for v in items]
    backitems.sort()
    return [ backitems[i][1] for i in range(0,len(backitems))]



# CB: color buttons to match? deactivate irrelevant buttons?

class ParametersFrame(TkParameterized,Frame):
    """
    Displays and allows instantaneous editing of the Parameters
    of a supplied Parameterized.

    Changes made to Parameter representations on the GUI are
    immediately applied to the underlying object.
    """
    Defaults = Button(doc="""Return values to class defaults.""")

    Refresh = Button(doc="Return values to those currently set on the object (or, if editing a class, to those currently set on the class).")  

    # CEBALERT: this is a Frame, so close isn't likely to make
    # sense. But fortunately the close button acts on master.
    # Just be sure not to use this button when you don't want
    # the master window to vanish (e.g. in the model editor).
    Close = Button(doc="Close the window. (If applicable, asks if unsaved changes should be saved).")

    display_threshold = Number(default=0,precedence=-10,doc="Parameters with precedence below this value are not displayed.")

    def __init__(self,master,parameterized_object=None,on_change=None,
                 on_modify=None,**params):
        """
        Create a ParametersFrame with the specifed master, and
        representing the Parameters of parameterized_object.

        on_change is an optional function to call whenever any of the
        GUI variables representing Parameter values is set() by the
        GUI (i.e. by the user). Since a variable's value is not
        necessarily changed by such a set(), on_modify is another
        optional function to call only when a GUI variable's value
        actually changes. (See TkParameterized for more detail.)
        """
        Frame.__init__(self,master,borderwidth=1,relief='raised')
        TkParameterized.__init__(self,master,
                                       extraPO=parameterized_object,
                                       self_first=False,**params)

        self.on_change = on_change
        self.on_modify = on_modify

        ## Frame for the Parameters
        self._params_frame = Frame(self)
        self._params_frame.pack(side='top',expand='yes',fill='both')

        if parameterized_object:
            self.set_PO(parameterized_object,on_change=on_change,
                        on_modify=on_modify)

        self.__create_button_panel()

        ### Right-click menu for widgets
        self.option_add("*Menu.tearOff", "0") 
        self.menu = Menu(self)
        self.menu.insert_command('end',label='Properties',
            command=lambda:self.__edit_PO_in_currently_selected_widget())

        # CEBALERT: just because callers assume this pack()s itself.
        # Really it should be left to callers i.e. this should be removed.
        self.pack(expand='yes',fill='both') 


    def hidden_param(self,name):
        """Return True if a parameter's precedence is below the display threshold."""
        # CB: interpret None as 0; remove if we set a default precedence (though that would
        # break param_inheritance for precedence, I think)
        precedence = self.get_parameter_object(name).precedence or 0 
        return precedence<self.display_threshold
        

    def __create_button_panel(self):
        """
        Add the buttons in their own panel (frame).
        """
        ## Buttons
        #
        # Our button order (when all buttons present):
        # [Defaults] [Refresh] [Apply] [Close]
        # 
        # Our button - Windows
        # Close(yes) - OK
        # Close(no ) - Cancel
        # [X]        - Cancel
        # Apply      - Apply
        # Defaults   - 
        # Refresh    - Reset
        #
        # I think Windows users will head for the window's [X]
        # when they want to close and cancel their changes,
        # because they won't know if [Close] saves their changes
        # or not (until they press it, and find that it asks).
        #
        #
        # Some links that discuss and address what order to use for buttons:
        #
        # http://java.sun.com/products/jlf/ed2/book/HIG.Dialogs2.html
        # http://developer.kde.org/documentation/books/kde-2.0-development/ch08lev1sec6.html
        # http://developer.kde.org/documentation/standards/kde/style/dialogs/index.html
        # http://doc.trolltech.com/qq/qq19-buttons.html

        
        # Catch click on the [X]: like clicking [Close]
        # CEBALERT: but what if this frame isn't in its own window!
        try:
            self.master.protocol("WM_DELETE_WINDOW",self._close_button)
        except AttributeError:
            pass

        buttons_frame = Frame(self,borderwidth=1,relief='sunken')
        buttons_frame.pack(side="bottom",expand="no")
        
        self._buttons_frame_left = Frame(buttons_frame)
        self._buttons_frame_left.pack(side='left',expand='yes',fill='x')

        self._buttons_frame_right = Frame(buttons_frame)
        self._buttons_frame_right.pack(side='right',expand='yes',fill='x')

        self.pack_param('Defaults',parent=self._buttons_frame_left,
                        on_change=self._defaults_button,side='left')
        self.pack_param('Refresh',parent=self._buttons_frame_left,
                        on_change=self._refresh_button,side='left')
        self.pack_param('Close',parent=self._buttons_frame_right,
                        on_change=self._close_button,side='right')


    def _refresh_button(self):
        """See Refresh parameter."""
        for name in self.displayed_params.keys():
            self._tkvars[name].get()


    def _defaults_button(self):
        """See Defaults parameter."""
        assert isinstance(self._extraPO,Parameterized)

        defaults = self._extraPO.defaults()

        for param_name,val in defaults.items():
            if not self.hidden_param(param_name):
                self.gui_set_param(param_name,val)#_tkvars[param_name].set(val)

        if self.on_modify: self.on_modify()
        if self.on_change: self.on_change()
        self.update_idletasks()
        
        
    def _close_button(self):
        """See Close parameter."""
        Frame.destroy(self) # hmm
        self.master.destroy()



    # CEBALERT: all these 'on_change=None's mean someone could lose
    # their initial setting: cleanup
    def set_PO(self,parameterized_object,on_change=None,on_modify=None):
        """

        """

        self.change_PO(parameterized_object)

        title = "Parameters of "+ (parameterized_object.name or str(parameterized_object)) # (name for class is None)

        try:
            self.master.title(title)
        except AttributeError:
            # can only set window title on a window (model editor puts frame in another frame)
            pass

        # CB: need a method for this!
        self.__dict__['_name_param_value'] = title
        
        
        ### Pack all of the non-hidden Parameters
        self.displayed_params = {}
        for n,p in parameterized_object.params().items():
            if not self.hidden_param(n):
                self.displayed_params[n]=p
                    
        self.pack_displayed_params(on_change=on_change,on_modify=on_modify)

        # hide Defaults button for classes
        if isinstance(parameterized_object,ParameterizedMetaclass):
            self.hide_param('Defaults')
        else:
            self.unhide_param('Defaults')    


    def _wipe_currently_displaying(self):
        """Wipe old labels and widgets from screen."""
        if hasattr(self,'currently_displaying'):
            for rep in self.currently_displaying.values():
                try:
                    rep['label'].destroy()
                except AttributeError:
                    # e.g. buttons have None for label ('notNonelabel')
                    pass
                rep['widget'].destroy()
        

##     def pack_param(self):
##         raise TypeError("ParametersFrame arranges all parameters together in a grid.")


    def __grid_param(self,parameter_name,row):
        widget = self.representations[parameter_name]['widget']
        label = self.representations[parameter_name]['label']

        # CB: (I know about the code duplication here & in tkpo)
        param_obj = self.get_parameter_object(parameter_name)
        help_text = getdoc(param_obj)

        if param_obj.default is not None:
            # some params appear to have no docs!!!
            if help_text is not None:
                help_text+="\n\nDefault: %s"%self._object2string(parameter_name,param_obj.default,replace=False)
        

        label.grid(row=row,column=0,
                   padx=2,pady=2,sticky=E)

        self.balloon.bind(label, help_text)

        # We want widgets to stretch to both sides...
        posn=E+W
        # ...except Checkbuttons, which should be left-aligned.
        if widget.__class__==Tkinter.Checkbutton:
            posn=W

        widget.grid(row=row,
                    column=1,
                    padx=2,
                    pady=2,
                    sticky=posn)

        self.representations[parameter_name]['row']=row

        self._post_add_param(parameter_name)




    def __make_representation(self,name,on_change=None,on_modify=None):
        widget,label = self._create_widget(name,self._params_frame,
                                           on_change=on_change or self.on_change,
                                           on_modify=on_modify or self.on_modify)

        label.bind("<Double-Button-1>",lambda event=None,x=name: self.switch_dynamic(x))
        self.representations[name]={'widget':widget,'label':label}
        self._indicate_tkvar_status(name)

        

    # CEBALERT: name doesn't make sense! change displayed_params to
    # something else e.g. params_to_display
    def pack_displayed_params(self,on_change=None,on_modify=None):

        self._wipe_currently_displaying()

        ### sort Parameters by reverse precedence
        parameter_precedences = {}
        for name,parameter in self.displayed_params.items():
            parameter_precedences[name]=parameter.precedence
        sorted_parameter_names = keys_sorted_by_value(parameter_precedences)
            
        ### create the labels & widgets
        for name in self.displayed_params:
            self.__make_representation(name,on_change,on_modify)
            
        ### add widgets & labels to screen in a grid
        rows = range(len(sorted_parameter_names))
        for row,parameter_name in zip(rows,sorted_parameter_names): 
            self.__grid_param(parameter_name,row)

        self.currently_displaying = dict([(param_name,self.representations[param_name])
                                          for param_name in self.displayed_params])
            
        
    def _create_selector_widget(self,frame,name,widget_options):
        """As for the superclass, but binds <<right-click>> event for opening menu."""
        w = TkParameterized._create_selector_widget(self,frame,name,widget_options)
        w.bind('<<right-click>>',lambda event: self.__right_click(event, w))
        return w


    def __right_click(self, event, widget):
        """
        Popup the right-click menu.
        """
        self.__currently_selected_widget = widget
        self.menu.tk_popup(event.x_root, event.y_root)


    # CEBALERT: rename
    def __edit_PO_in_currently_selected_widget(self):
        """
        Open a new window containing a ParametersFrame (actually, a
        type(self)) for the PO in __currently_selected_widget.
        """
        # CEBALERT: simplify this lookup by value
        param_name = None
        for name,representation in self.representations.items():
            if self.__currently_selected_widget is representation['widget']:
                param_name=name
                break

        # CEBALERT: should have used get_parameter_value(param_name)?
        PO_to_edit = self._string2object(param_name,self._tkvars[param_name].get()) 

        parameter_window = TkguiWindow(self)
        parameter_window.title(PO_to_edit.name+' parameters')

        ### CEBALERT: confusing? ###
        title=Tkinter.Label(parameter_window, text="("+param_name + " of " + (self._extraPO.name or 'class '+self._extraPO.__name__) + ")")
        title.pack(side = "top")
        self.balloon.bind(title,getdoc(self.get_parameter_object(param_name,self._extraPO)))
        ############################
        
        parameter_frame = type(self)(parameter_window,parameterized_object=PO_to_edit)
        parameter_frame.pack()


##     def unpack_param(self,param_name):
##         if param_name in self.currently_displaying:
##             raise NotImplementedError("yet")
##         super(ParametersFrame,self).unpack_param(param_name)
        
##     def hide_param(self,param_name):
##         if param_name in self.currently_displaying:
##             raise NotImplementedError("yet")
##         super(ParametersFrame,self).hide_param(param_name)

##     def unhide_param(self,param_name):
##         if param_name in self.currently_displaying:
##             raise NotImplementedError("yet")
##         super(ParametersFrame,self).unhide_param(param_name)    


    # ERROR need to sort out all this stuff in the tkpo/pf hierarchy
    
    def repack_param(self,param_name):

        self._refresh_value(param_name)
        
        r = self.representations[param_name]
        widget,label,row = r['widget'],r['label'],r['row']

        widget.destroy()
        label.destroy()

        param = self.get_parameter_object(param_name)
        
        self._create_translator(param_name,param)
        self.__make_representation(param_name)
        self.__grid_param(param_name,row)

        

    

##     def _indicate_tkvar_status(self,param_name):
##         """
##         Calls the superclass's method, then additionally indicates if a parameter
##         differs from the class default (by giving label green background).
##         """
##         TkParameterized._indicate_tkvar_status(self,param_name)

##         b = 'white'
        
##         param,sourcePO = self.get_parameter_object(param_name,with_location=True)

##         if sourcePO is not self and self.get_parameter_value(param_name) is not self.get_parameter_object(param_name).default:
##             b = "green"


##         if hasattr(self,'representations') and param_name in self.representations:
##             try:
##                 label = self.representations[param_name]['label']
##                 if label is None:  # HACK about the label being none
##                     return
##                 label['background']=b
##             except TclError:
##                 pass



    def _refresh_value(self,param_name):
        pass






class ParametersFrameWithApply(ParametersFrame):
    """
    Displays and allows editing of the Parameters of a supplied
    Parameterized.

    Changes made to Parameter representations in the GUI are not
    applied to the underlying object until Apply is pressed.
    """

    # CB: might be nice to make Apply button blue like the unapplied changes,
    # but can't currently set button color
    Apply = Button(doc="""Set object's Parameters to displayed values.\n
                                   When editing a class, sets the class defaults
                                   (i.e. acts on the class object).""")
    
    def __init__(self,master,parameterized_object=None,on_change=None,on_modify=None,**params):        
        super(ParametersFrameWithApply,self).__init__(master,parameterized_object,
                                                      on_change,on_modify,**params)
        self._live_update = False

        ### CEBALERT: describe why this apply is different from Apply
        for p in self.param_immediately_apply_change:
            self.param_immediately_apply_change[p]=True
            
        
        self.pack_param('Apply',parent=self._buttons_frame_right,
                        on_change=self._apply_button,side='left')

        # this check for displayed_params, like elsewhere it exists, is to get round the
        # fact that parametersframes can be opened without any associated object. Need
        # to clean this up. (displayed_params should probably start as an empty dict.)
        if hasattr(self,'displayed_params'):
            assert self.has_unapplied_change() is False, "ParametersFrame altered a value. If possible, please email ceball at users.sf.net describing what you were doing when you received this error."
            # should use existing code
            self.representations['Apply']['widget']['state']='disabled'


    def _create_string_widget(self,frame,name,widget_options):
        # CEBALERT: why do I unbind those events?
        w= super(ParametersFrameWithApply,self)._create_string_widget(frame,name,widget_options)
        w.unbind('<Return>')
        w.unbind('<FocusOut>')
        return w


    def set_PO(self,parameterized_object,on_change=None,on_modify=None):

        super(ParametersFrameWithApply,self).set_PO(parameterized_object,
                                                    on_change=on_change,
                                                    on_modify=on_modify)

        # (don't want to update parameters immediately)
        for v in self._tkvars.values():
            v._checking_get = v.get
            v.get = v._original_get


    def has_unapplied_change(self):
        """Return True if any one of the packed parameters' displayed values is different from
        that on the object."""
        for name in self.displayed_params.keys():
            if self._tkvar_changed(name):
                return True
        return False



    def _indicate_tkvar_status(self,param_name,status=None):

        if self._tkvar_changed(param_name):
            status = 'changed'

        super(ParametersFrameWithApply,self)._indicate_tkvar_status(param_name,status)
        
    
    def _handle_gui_set(self,p_name,force=False):
        TkParameterized._handle_gui_set(self,p_name,force)

        if hasattr(self,'representations') and 'Apply' in self.representations:
            w=self.representations['Apply']['widget']
            if self.has_unapplied_change():
                state='normal'
            else:
                state='disable'

            w.config(state=state)
            



    def _close_button(self):
        # CEBALERT: dialog box should include a cancel button
        if self.has_unapplied_change() \
               and askyesno("Close","Apply changes before closing?"):
            self.update_parameters()
        super(ParametersFrameWithApply,self)._close_button()


    def update_parameters(self):
        if isinstance(self._extraPO,ParameterizedMetaclass):
            for name in self.displayed_params.keys():
                #if self._tkvar_changed(name):
                self._update_param_from_tkvar(name)
        else:
            for name,param in self.displayed_params.items():
                if not param.constant:  #and self._tkvar_changed(name):
                    self._update_param_from_tkvar(name)


    def _apply_button(self):
        self.update_parameters()
        self._refresh_button(overwrite_error=False)

    def _refresh_value(self,param_name):
        po_val = self.get_parameter_value(param_name)
        po_stringrep = self._object2string(param_name,po_val)
        self._tkvars[param_name]._original_set(po_stringrep)

        
    def _refresh_button(self,overwrite_error=True):
        for name in self.displayed_params.keys():
            if self.translators[name].last_string2object_failed and not overwrite_error:
                pass
            else:
                self._refresh_value(name)
                #print self._tkvars[name]._checking_get()
                # CEBALERT: taggedsliders need to have tag_set() called to update slider
                w = self.representations[name]['widget']
                if hasattr(w,'tag_set'):w.tag_set()



    def _defaults_button(self):
        """See Defaults parameter."""
        assert isinstance(self._extraPO,Parameterized)

        defaults = self._extraPO.defaults()

        for param_name,val in defaults.items():
            if not self.hidden_param(param_name):
                self._tkvars[param_name].set(val)

        if self.on_modify: self.on_modify()
        if self.on_change: self.on_change()
        self.update_idletasks()



# CB: can override tracefn so that Apply/Refresh buttons are enabled/disabled as appropriate




def edit_parameters(parameterized_object,with_apply=True,**params):
    """
    Edit the Parameters of parameterized_object.

    Specify with_apply=False for a ParametersFrame (which immediately
    updates the object - no need to press the Apply button).

    Extra params are passed to the ParametersFrame constructor.
    """
    if not (isinstance(parameterized_object,Parameterized) or \
           isinstance(parameterized_object,ParameterizedMetaclass)):
        raise ValueError("Can only edit parameters of a Parameterized.")

    if not with_apply:
        pf_class = ParametersFrame
    else:
        pf_class = ParametersFrameWithApply

    return pf_class(Tkinter.Toplevel(),parameterized_object,**params)

    

