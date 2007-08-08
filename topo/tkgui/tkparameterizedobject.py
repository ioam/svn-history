"""

$Id$
"""

# CB: this file has now gone beyond the maximum complexity limit


from inspect import getdoc
import Tkinter
from Tkinter import BooleanVar, StringVar, DoubleVar, IntVar,Frame, Tk, Checkbutton, Entry, Button,OptionMenu
import Pmw

import topo

from topo.plotting.plotgroup import RangedParameter


from topo.base.parameterizedobject import ParameterizedObject,Parameter
from topo.base.parameterclasses import BooleanParameter,StringParameter,Number

from translatorwidgets import TaggedSlider


##### Temporary: for easy buttons
#
# buttons are not naturally represented by parameters?
# they're like callableparameters, i guess, but if the
# thing they should call is a method of another object,
# that's a bit tricky

# Maybe we should have a parent class that implements the
# non-Parameter specific stuff, then one that bolts on the
# Parameter-specific stuff, and then instead of ButtonParameter we'd
# have TopoButton, or something like that...

class ButtonParameter(Parameter):

    __slots__ = []
    __doc__ = property((lambda self: self.doc))

    def __init__(self,default="[button]",**params):
        Parameter.__init__(self,default=default,**params)
#####


# (Duplicates PropertiesFrame/ParamtersFrame)
parameters_to_tkvars = {
    BooleanParameter:BooleanVar,
    StringParameter:StringVar,
    Number:DoubleVar
    }
parameters_to_tkwidgets = {
    BooleanParameter:Checkbutton,
    Number:TaggedSlider,
    StringParameter:Entry,
    ButtonParameter:Button,
    RangedParameter:OptionMenu
    }

## CEBHACKALERT: by using tkinter's optionmenu rather than pmw's, i think
## i lost the history.




class TkParameterizedObjectBase(ParameterizedObject):
    """
    A ParameterizedObject that maintains Tkinter.Variable shadows
    (proxies) of its Parameters. The Tkinter Variable shadows are kept
    in sync with the Parameter values, and vice versa.

    Optionally performs the same for any number of additional
    shadowed ParameterizedObjects.


    The Parameters of the shadowed POs are available as attributes of
    this object (though see note 1); the Tkinter.Variable shadows are
    available under their corresponding parameter names in the
    _tk_vars dictionary.


    Any Parameter being represented that has a 'range' attribute will
    also have a 'translators' dictionary, allowing mapping between
    string representations of the objects and the objects themselves
    (for use with e.g. a Tkinter.OptionMenu).


    Notes
    =====
    
    (1) Attribute lookup follows a precedance order, object>shadowed POs (in order
    of their initial specification):

    E.g.
    POa = ParameterizedObject(x=2,y=2)         # where x, y, z are Parameters
    POb = ParameterizedObject(x=3,y=3,z=3)     #
    TkPOt = TkParameterizedObjectBase(extra_pos=[a,b])

    TkPOt.x = 1   # 'x' is just an attribute (not a Parameter)

    TkPOt.x==1 (i.e. tTkPO.__dict__['x'])
    TkPOt.y==2 ('y' not in tTkPO.__dict__ and precedence of POa is higher than POb)
    TkPOt.z==3 ('z' not in tTkPO.__dict__ and not a Parameter of POa)


    To avoid confusion with attributes defined on the local object,
    get_ and set_parameter_value() can be used to access parameter values only:
    TkPOt.get_parameter_value('x')==2  # POa.x is parameter with highest precedence 


    
    (2) If a shadowed PO's Parameter value is modified elsewhere, the
    Tkinter Variable shadow is NOT updated until that Parameter value
    or shadow value is requested from this object. Thus requesting the
    value will always return an up-to-date result, but any GUI display
    of the Variable might display a stale value (until a GUI refresh
    takes place).
    """
    # if the above becomes a problem, we could have some autorefresh of the vars
    # or a callback of some kind in the parameterized object itself.

    _extra_pos = []
    _tk_vars = {}
    translators = {}
    

    # __repr__ will need some work (display params of subobjects etc?)


    # Overrides method from superclass.
    def _setup_params(self,**params):
        """
        Parameters that are not in this object itself but are in one of the
        extra_pos get set on that extra_po.

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


    # CEBALERT: a list's too confusing, and there's currently no need for more
    # than one extra po. Change to just one extra PO?
    def __init__(self,extra_pos=[],**params):

        self._extra_pos = extra_pos
        self._tk_vars = {}
        self.translators = {}
        
        super(TkParameterizedObjectBase,self).__init__(**params)

        for PO in extra_pos[::-1]+[self]:
            self._init_tk_vars(PO)
        

    def _init_tk_vars(self,PO):
        """
        Create Tkinter Variable shadows of all Parameters of PO.
        
        The appropriate Variable is used for each Parameter type.

        Also adds tracing mechanism to keep the Variable and Parameter values in sync.
        
        For a Parameter with the 'range' attribute, also updates the translator dictionary to
        map string representations to the objects themselves.
        """
        for name,param in PO.params().items():

            # shouldn't need second check but seems range could be None or something else not like a list?
            if hasattr(param,'range') and hasattr(param.range,'__len__'): 
                self._update_translator(name,param)

            tk_var = parameters_to_tkvars.get(type(param),StringVar)()
            self._tk_vars[name] = tk_var

            # overwrite Variable's set() with one that will handle transformations to string
            tk_var._original_set = tk_var.set
            tk_var.set = lambda v,x=name: self.__set_tk_val(x,v)

            tk_var.set(getattr(PO,name))
            tk_var._last_good_val=tk_var.get() # for reverting
            tk_var.trace_variable('w',lambda a,b,c,p_name=name: self.__update_param(p_name))        
            # Instead of a trace, could we override the Variable's set() method i.e. trace it ourselves?
            # Or does too much happen in tcl/tk for that to work?

            # Override the Variable's get() method to guarantee an out-of-date value is never returned.
            # In cases where the tkinter val is the most recently changed (i.e. when it's edited in the
            # gui, resulting in a trace_variable being called), the _original_get() method is used.
            tk_var._original_get = tk_var.get
            tk_var.get = lambda x=name: self.__get_tk_val(x)



    def __set_tk_val(self,param_name,val):
        """
        Set the tk variable to (the possibly transformed-to-string) val.
        """
        val = self.object2string_ifrequired(param_name,val)
        tk_var = self._tk_vars[param_name]
        tk_var._original_set(val)


    def __get_tk_val(self,param_name):
        """
        Before returning a tk variable's value, ensure it's up to date. 
        """
        tk_var = self._tk_vars[param_name]
        tk_val = tk_var._original_get()
        po_val = self.get_parameter_value(param_name)

        if not tk_val==po_val:
            # tk var needs to be updated
            tk_var.set(po_val)
        return po_val #tk_var.get()



    ### CB: can't use this because widgets will be left behind with old variables!
##     def add_extra_po(self,PO):
##         # CB ** insert at start since last PO in will write over other same-named tkvars,
##         # so indicate that in search order. 
##         self._extra_pos.insert(0,PO)
##         self._init_tk_vars(PO)



    def _update_translator(self,name,param):
        """
        Map names of objects in param.range to the actual objects.
        """
        t=self.translators[name]={}

        for a in param.range:
            # use name attribute if it's valid, otherwise use str()
            # (this is the place to call any special name formatting)
            if hasattr(a,'name') and isinstance(a.name,str) and len(a.name)>0: 
                t[a.name] = a
            else:
                t[str(a)]=a

        
    
    def string2object_ifrequired(self,param_name,val):
        """
        If val is in param_name's translator, then translate to the object.
        """
        new_val = val
        
        if param_name in self.translators:
            t = self.translators[param_name]
            if val in t:
                new_val = t[val]

        return new_val
    converta = string2object_ifrequired


    def object2string_ifrequired(self,param_name,val):
        """
        If val is one of the objects in param_name's translator,
        translate to the string.
        """
        new_val = val

        if param_name in self.translators:
            t = self.translators[param_name]

            for k,v in t.items():
                if v==val:
                    new_val = k
        return new_val
    atrevnoc = object2string_ifrequired
        
            

    def __update_param(self,param_name):
        """
        Attempt to set the parameter represented by param_name to the
        value of its correspinding Tkinter Variable.

        If setting the parameter fails (e.g. an inappropriate value
        is set for that Parameter type), the Variable is reverted to
        its previous value.

        (Called by the Tkinter Variable's trace_variable() method.)
        """
        tk_var = self._tk_vars[param_name]

        try:
            val = tk_var._original_get() # tk_var ahead of parameter
        except ValueError: # means user not finished typing
            ### CEBALERT: this needs more testing since I'm not sure
            ### if it will always work!
            return 

        val = self.string2object_ifrequired(param_name,val)
        
        try:
            sources = [self]+self._extra_pos
            
            for po in sources:
                if param_name in po.params().keys():
                    parameter = po.params()[param_name]
                    ## use set_in_bounds if it exists: i.e. users of widgets get their
                    ## values cropped (no warnings/errors)
                    if hasattr(parameter,'set_in_bounds'):
                        parameter.set_in_bounds(po,val)
                    else:
                        setattr(po,param_name,val)
                        
                    if hasattr(tk_var,'_on_change'): tk_var._on_change()
                    return # hidden


            assert False,"Error in use of __update_param: param must exist" # remove this
            
        except: # everything
            tk_var.set(tk_var._last_good_val)
            # CEBALERT: is above too fast for gui? variable changes correctly, but sometimes doesn't appear
            # on gui until next click. Needs more testing. Could try:
            #topo.guimain.after(250,lambda x=tk_var._last_good_val: tk_var.set(x))
            raise # whatever the parameter-setting error was


    def __sources(self,parameterized_object=None):
        """
        Return a correctly ordered list of ParameterizedObjects in which to find Parameters
        (unless one is specified, in which case it's the only item in the list).
        """
        if parameterized_object is None:
            sources = [self]+self._extra_pos
        else:
            sources = [parameterized_object] 
        return sources
    

    def get_parameter(self,name,parameterized_object=None):
        """
        Return the Parameter specified by the name from the sources of
        Parameters in this object (or the specified parameterized_object).
        """
        sources = self.__sources(parameterized_object)
        
        for po in sources:
            params = po.params()
            if name in params: return params[name] # a bit hidden

        raise AttributeError("none of %s have parameter %s"%(str(sources),name))
    get_parameter_object = get_parameter
    

#    def get_like_the_gui(self,name):
#        return self._tk_vars[name].get()

##### these guarantee only to get/set parameters #####
    def get_parameter_value(self,name,parameterized_object=None):
        """
        Get the value of the parameter specified by name.
        """
        sources = self.__sources(parameterized_object)

        for po in sources:
            params = po.params()
            if name in params: return getattr(po,name) # also hidden!

        raise AttributeError("none of %s have parameter %s"%(str(sources),name))

        
    def set_parameter_value(self,name,val,parameterized_object=None):
        """
        Set the value of the parameter specified by name to val.
        """
        sources = self.__sources(parameterized_object)

        for po in sources:
            if name in po.params().keys(): 
                setattr(po,name,val)
                return # so hidden I forgot to write it until now

        raise AttributeError("none of %s have parameter %s"%(str(sources),name))
#######################################################        


###### these lookup attributes in order #####
# (i.e. you could get attribute of self rather than a parameter)
# (might remove these to save confusion: they are useful except when 
#  someone would be surprised to get an attribute of e.g. a Frame (like 'size') when
#  they were expecting to get one of their parameters. Also, means you can't set
#  an attribute a on self if a exists on one of the shadowed objects)

    def __getattribute__(self,name):
        """
        If the attribute is found on this object, return it. Otherwise,
        search the list of shadow POs and return from the first match.
        If no match, get attribute error.
        """
        try:
            return object.__getattribute__(self,name)
        except AttributeError:
            extra_pos = object.__getattribute__(self,'_extra_pos')
            for po in extra_pos:
                if hasattr(po,name): return getattr(po,name) 

            raise AttributeError("none of %s, %s has attribute %s"%(self,str(extra_pos),name))

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
            for po in self._extra_pos:
                if hasattr(po,name):
                    setattr(po,name,val)
                    if name in self._tk_vars: self._tk_vars[name].set(val)
                    return # also a bit hidden

        # name not found, so set on this object
        object.__setattr__(self,name,val)
################################################



# CAN'T USE THIS AFTER PACK unless Tkinter.OptionMenu supports changing the list
# of items after widget creation - might need to use Pmw's OptionMenu.
    def initialize_ranged_parameter(self,param_name,range_):
        p = self.get_parameter(param_name)

        if hasattr(range_,'__len__'):
            [p.range.append(x) for x in range_]
        else:
            p.range.append(range_)

        p.default = p.range[0]
        self._update_translator(param_name,p)



### CEB: working here - not complete.
        

import _tkinter # (required to get tcl exception class)


class TkParameterizedObject(TkParameterizedObjectBase):
    """
    A TkParameterizedObjectBase and Tkinter Frame that can draw
    widgets representing the Parameters of the supplied
    ParameterizedObjects.
    """

    pretty_parameters = BooleanParameter(default=True,doc="Whether to format parameter names, or use the variable names instead.")
    
    def __init__(self,master,extra_pos=[],**params):
        """

        """
        assert master is not None # (could probably remove this but i didn't want to think about it)
        self.master = master
        TkParameterizedObjectBase.__init__(self,extra_pos=extra_pos,**params)
        self.balloon = Pmw.Balloon(master)


        ####################################################
        ## CEBALERT: just keep one and will name properly
        ## & probably provide access methods
        # allows subclasses to 
        # access all plotgroup's widgets in an easy way.
        self._widgets = {}
        self._furames = {}
        ####################################################
        
        # (a refresh-the-widgets-on-focus-in method would make the gui
        # in sync with the actual object)


    # CB: some widgets need to have <return> bound to frame's refresh!
    # Also think about taggedsliders.

##     def repackparam(self,name):
##         self._widgets[name].destroy()
##         self.pack_param(name,parent=self._furames[name])
        

    # move elsewhere
    # Will create some general function for converting parameter names to
    # a 'pretty' representation. Need to merge more of tkpo with param frame
    def pretty_print(self,s):
        """
        """
        if not self.pretty_parameters:
            return s
        else:
            n = s.replace("_"," ")
            n = n.capitalize()
            return n


    # CB: document!
    # also note on_change is called during pack_param
    # on_change should be on_set (since it's called not only for changes)
    def pack_param(self,name,parent=None,widget_options={},on_change=None,**pack_options):
        """
        Create a widget for Parameter name, configured according to
        widget_options, and pack()ed according to the pack_options.

        Balloon help is automatically set from the Parameter's doc.

        The widget and label (if appropriate) are enlosed in a Frame.
        
        Returns the widget in case further processing of it is required.
        
        Examples:
        self.pack_param(name)
        self.pack_param(name,side='left')
        self.pack_param(name,{'width':50},side='top',expand='yes',fill='y')
        """
        frame = Frame(parent or self.master)
        param = self.get_parameter_object(name)
        
        widget_type = parameters_to_tkwidgets.get(type(param),Entry)

        # checkbuttons are 'wdiget label'; everything else is 'label widget'
        if widget_type is Tkinter.Checkbutton:
            widget_side='left'; label_side='right'
        else:
            widget_side='right';label_side='left'
            
        ### buttons are different from the other widgets: different labeling,
        ### and no need for a variable
        if widget_type==Tkinter.Button:
            assert on_change is not None, "Buttons need a command."
            widget = widget_type(frame,text=self.pretty_print(name),command=on_change,**widget_options)
            label = None
        else:

            tk_var = self._tk_vars[name]

            if on_change is not None: tk_var._on_change=on_change

            ### CEBALERT: clean up this widget type selection

            if widget_type==Tkinter.OptionMenu:

                self._update_translator(name,param)

                new_range = [self.object2string_ifrequired(name,i) for i in param.range]

                assert len(new_range)>0

                #if tk_var.get() not in new_range:  
                tk_var.set(new_range[0])
                
                widget = widget_type(frame,tk_var,*new_range,**widget_options)
                
                
            else:
            ### Tkinter widgets use either variable or textvariable
                try:
                    widget = widget_type(frame,variable=tk_var,**widget_options)
                except _tkinter.TclError:
                    try:
                        widget = widget_type(frame,textvariable=tk_var,**widget_options)
                    except _tkinter.TclError:
                        raise # meaning the widget doesn't support variable or textvariable
            ###

            # i'll probably pack in a better way at some point
            # (including packing of w below)
            # (e.g. checbutton should be closer to label)
            label = Tkinter.Label(frame,text=self.pretty_print(name))
            label.pack(side=label_side)


        ### CB: clean up
        if param.hidden:
            return frame

        widget.pack(side=widget_side,expand='yes',fill='x')

        # CEBALERT: move this; doesn't always need to be done
        try:
            widget.set_bounds(*param.bounds)
            widget.refresh()
        except: # could be TypeError (param has None for bounds) or AttributeError (no set_bounds)
                # (when moved to correct location, won't need AttributeError check)
            pass

        self._widgets[name]=widget

        self._furames[name]=(frame,label)

        # f's probably better than w
        self.balloon.bind(frame,getdoc(param))

        frame.pack(pack_options)
        return frame 



    # For convenience. Maybe should offer a way to access any attribute on master.
    # Probably too confusing - might remove this, too.
    def title(self,t):
        self.master.title(t)
        
