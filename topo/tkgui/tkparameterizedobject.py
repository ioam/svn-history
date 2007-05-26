"""

$Id$
"""

# CB: testing out Parameter-Tkinter Variable coupling


from inspect import getdoc
import Tkinter
from Tkinter import BooleanVar, StringVar, DoubleVar, IntVar,Frame, Tk, Checkbutton, Entry, Button
import Pmw

from topo.base.parameterizedobject import ParameterizedObject,Parameter
from topo.base.parameterclasses import BooleanParameter,StringParameter,Number

from translatorwidgets import TaggedSlider



# buttons are not naturally represented by parameters?
# they're like callableparameters, i guess, but if the
# thing they should call is a method of another object,
# that's a bit tricky
class ButtonParameter(Parameter):

    __slots__ = []
    __doc__ = property((lambda self: self.doc))

    def __init__(self,default="[button]",**params):
        """Initialize a string parameter."""
        Parameter.__init__(self,default=default,**params)
        



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
    ButtonParameter:Button
    }


### CB: most of the documenation needs to be updated! Please ignore
### it for the moment.

class TkParameterizedObjectBase(ParameterizedObject):
    """
    A ParameterizedObject that maintains Tkinter.Variable shadows
    (proxies) of its Parameters.

    Optionally performs the same for any number of additional
    shadowed ParameterizedObjects.


    
    The Parameters are available as
    attributes of this object; the Tkinter.Variable shadows are
    available under their corresponding parameter name in the _tk_vars
    dictionary.


    So, for a ParameterizedObject po with a Parameter p, t=TkParameterizedObjectBase(po) allows
    access to po.p via t.p, i.e. setting t.p sets po.p, and getting
    t.p returns po.p.

    t stores a Tkinter Variable representing p as t._tk_vars[p];
    setting t.p not only sets po.p, but also the Variable representing
    p. Conversely, setting the Tkinter Variable t._tk_vars[p] also
    sets po.p. In this way, a Parameter is kept in sync with a Tkinter
    Variable.


    ** Important Note **
    If the parameterized_object itself is modified elsewhere (e.g. po.p=7),
    the Tkinter Variable shadow is NOT updated until the shadow's value is
    requested. Thus requesting t.p will correctly return 7, but any GUI
    display of the Variable will display the old value until a refresh takes
    place.
    """
    # if the above becomes a problem, we could have some autorefresh of the vars
    # or a callback of some kind in the parameterized object itself.

    _extra_pos = []
    #_tk_vars = {}
    

    # __repr__ will need some work (display params of subobjects etc?)


    def __init__(self,extra_pos=[],**params):
        super(TkParameterizedObjectBase,self).__init__(**params)
        self._extra_pos = extra_pos
        self._tk_vars = {}
        self.__setup_tk_vars()

    
    def __setup_tk_vars(self):
        """
        Create Tkinter Variables corresponding to
        parameterized_object's Parameters, and store them in the
        _tk_vars dictionary under the corresponding parameter name.

        The Tkinter Variable defaults to StringVar if no corresponding
        Variable for the Parameter type is found in
        parameters_to_vars.
        
        Each Tkinter Variable is traced so that when its value changes
        the corresponding parameter is set on parameterized_object.
        """
        # * lookup order: self then extra_pos in order, so set in reverse *
        for PO in self._extra_pos[::-1]+[self]:
            for name,param in PO.params().items():
                tk_var = parameters_to_tkvars.get(type(param),StringVar)()
                self._tk_vars[name] = tk_var
                tk_var.set(getattr(PO,name))
                tk_var._last_good_val=tk_var.get() # for reverting
                tk_var.trace_variable('w',lambda a,b,c,p_name=name: self.__update_param(p_name))        
                # Instead of a trace, could we override the Variable's set() method i.e. trace it ourselves?
                # Or does too much happen in tcl/tk for that to work?
                
                # Override the Variable's get() method to guarantee an out-of-date value is never returned.
                # In cases where the tkinter val is the most recently changed (i.e. when it's edited in the
                # gui, resulting in a trace_variable being called), use the _original_get() method.
                tk_var._original_get = tk_var.get
                tk_var.get = lambda x=name: self.__get_tk_val(x)


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
    

    def __update_param(self,param_name):
        """
        Attempt to set the parameterized_object's param_name to the
        value of its correspinding Tkinter Variable.

        If setting the parameter fails (e.g. an inappropriate value
        is set for that Parameter type), the Variable is reverted to
        its previous value.

        (Called by the Tkinter Variable's trace_variable() method.)
        """
        tk_var = self._tk_vars[param_name]
        val = tk_var._original_get() # tk_var ahead of parameter

        try:
            sources = [self]+self._extra_pos
            
            for po in sources:
                if param_name in po.params().keys():
                    setattr(po,param_name,val)
                    if hasattr(tk_var,'_on_change'): tk_var._on_change()
                    return # hidden

            assert False,"Error in use of __update_param: param must exist" # remove this
            
        except: # everything
            #tk_var.set(tk_var._last_good_val)
            # hack: above is too fast for gui? variable changes correctly, but doesn't appear
            # on gui until next click
            topo.guimain.after(250,lambda x=tk_var._last_good_val: tk_var.set(x))
            raise

    def __sources(self,parameterized_object=None):
        
        if parameterized_object is None:
            sources = [self]+self._extra_pos
        else:
            sources = [parameterized_object] 
        return sources
    

    def get_parameter_object(self,name,parameterized_object=None):

        sources = self.__sources(parameterized_object)
        
        for po in sources:
            params = po.params()
            if name in params: return params[name] # a bit hidden

        raise AttributeError("none of %s have parameter %s"%(str(sources),name))
            

##### these guarantee only to get/set parameters #####
    def get_parameter_value(self,name,parameterized_object=None):

        sources = self.__sources(parameterized_object)

        for po in sources:
            params = po.params()
            if name in params: return getattr(po,name) # also hidden!

        raise AttributeError("none of %s have parameter %s"%(str(sources),name))
        
    def set_parameter_value(self,name,val,parameterized_object=None):

        sources = self.__sources(parameterized_object)

        for po in sources:
            if name in po.params().keys(): 
                setattr(po,name,val)

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




import _tkinter # (required to get tcl exception class)

# CB: needs renaming
class TkParameterizedObject(TkParameterizedObjectBase):
    """
    A TkParameterizedObjectBase and Tkinter Frame that can draw widgets representing the Parameters of the supplied po.
    """
    def __init__(self,master,extra_pos=[],**params):
        """
        (Frame.__init__ gets the config.)
        """
        assert master is not None # (could probably remove this but i didn't want to think about it)
        self.master = master
        TkParameterizedObjectBase.__init__(self,extra_pos=extra_pos,**params)
        self.balloon = Pmw.Balloon(master)

        # just going to keep the dict
        self._widgets = []
        self._widgets2 = {}

        # a refresh-the-widgets-on-focus-in method would make the gui in sync with the actual object


    # should remove this now it's not a frame
    # (It sucks having to type 'master' all the time for stuff like a window title.
    # Maybe it's not just title, in which case use __getattribute__ to try method
    # on master.)
    def title(self,t):
        self.master.title(t)
        

    # CEBALERT: rename & doc parent * on_change
    def pack_param(self,name,parent=None,widget_options={},on_change=None,**pack_options):
        """
        Create a widget for Parameter name, configured according to
        widget_options, and pack()ed according to the pack_options.

        Balloon help is automatically set from the Parameter's doc.

        Returns the widget in case further processing of it is required.
        
        Examples:
        self.pack_param(name)
        self.pack_param(name,side='left')
        self.pack_param(name,{'width':50},side='top',expand='yes',fill='y')
        """
        f = Frame(parent or self.master)
        param = self.get_parameter_object(name) 
        
        widget_type = parameters_to_tkwidgets.get(type(param),Entry)

        # better not look expect a var for each param anywhere 
        ### buttons are different from the other widgets: different labeling,
        ### and no need for a variable
        # not isinstance because tkinter classes are oldstyle
        if widget_type==Tkinter.Button:
            assert on_change is not None, "Buttons need a command."
            w = widget_type(f,text=name,command=on_change,**widget_options)
        else:

            tk_var = self._tk_vars[name]

            # CB: called on_change, but it's on_set
            if on_change is not None: tk_var._on_change=on_change
    
        ### Tkinter widgets use either variable or textvariable
            try:
                w = widget_type(f,variable=tk_var,**widget_options)
            except _tkinter.TclError:
                try:
                    w = widget_type(f,textvariable=tk_var,**widget_options)
                except _tkinter.TclError:
                    raise # meaning the widget doesn't support variable or textvariable
        ###

            # CBALERT: should format label nicely (e.g. underscore to space)
            # some widgets: label widget    (e.g. entry)
            # others:       widget label    (e.g. checkbutton)
            # i'll probably pack in a better way at some point
            Tkinter.Label(f,text=name).pack(side="left")


        w.pack(side="right")

        # CEBALERT: possibly temporary. Needs attention: allows subclasses to
        # access all plotgroup's widgets in an easy way.
        self._widgets.append(w)
        self._widgets2[name]=w

        # f's probably better than w
        self.balloon.bind(f,getdoc(param))

        f.pack(pack_options)
        return f 










## ### A setup for basic testing...

## class OverlapPO(ParameterizedObject):
##     x = Parameter(0.0)
##     size = Parameter(1.0)
##     notoverlap = Parameter(0.4)


## class SomeFrame(TkParameterizedObject,Frame):

##     k = BooleanParameter(default=True)

##     def __init__(self,master,extra_pos=[],**params):
##         TkParameterizedObject.__init__(self,master,extra_pos=extra_pos,**params)
##         Frame.__init__(self,master)

##         self.pack_param('k',on_change=self.some_function)

##     def some_function(self):
##         print "called some_function"


## def another_function():
##     print "called another_function"


## from topo.patterns.basic import Gaussian        
## from topo.outputfns.basic import PiecewiseLinear

## g = Gaussian()
## p = PiecewiseLinear()
## o = OverlapPO()

## f = SomeFrame(Tkinter.Toplevel(),extra_pos=[g,p,o])
## f.pack()

## f.pack_param('x') # from the Gaussian
## f.pack_param('size',on_change=another_function) # from the Gaussian
## f.pack_param('upper_bound')
## f.pack_param('notoverlap')




