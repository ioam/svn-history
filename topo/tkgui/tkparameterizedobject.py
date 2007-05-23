"""

$Id$
"""

# CB: testing out Parameter-Tkinter Variable coupling


from inspect import getdoc
import Tkinter
from Tkinter import BooleanVar, StringVar, DoubleVar, IntVar,Frame, Tk, Checkbutton, Entry
import Pmw

from topo.base.parameterizedobject import ParameterizedObject,Parameter
from topo.base.parameterclasses import BooleanParameter,StringParameter,Number

from translatorwidgets import TaggedSlider





# (Duplicates PropertiesFrame/ParamtersFrame)
parameters_to_tkvars = {
    BooleanParameter:BooleanVar,
    StringParameter:StringVar,
    Number:DoubleVar
    }
parameters_to_tkwidgets = {
    BooleanParameter:Checkbutton,
    Number:TaggedSlider,
    StringParameter:Entry
    }



# CB: documentation hasn't been updated regarding parameter access.

# CB: need to rename - not sure what to choose.
class TkPO(object):
    """
    Stores a ParameterizedObject and creates Tkinter.Variable shadows
    (proxies) of its Parameters.

    The Parameters of the parameterized_object are available as
    attributes of this object; the Tkinter.Variable shadows are
    available under their corresponding parameter name in the _tk_vars
    dictionary.


    So, for a ParameterizedObject po with a Parameter p, t=TkPO(po) allows
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

    def __init__(self,parameterized_object):
        super(TkPO,self).__init__()
        self._parameterized_object = parameterized_object
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
        for name,param in self._parameterized_object.params().items():
            tk_var = parameters_to_tkvars.get(type(param),StringVar)()
            self._tk_vars[name] = tk_var
            tk_var.set(getattr(self._parameterized_object,name))
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
        po_val = getattr(self._parameterized_object,param_name)
        
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
            setattr(self._parameterized_object,param_name,val)
        except: # everything
            #tk_var.set(tk_var._last_good_val)
            # hack: above is too fast for gui? variable changes correctly, but doesn't appear
            # on gui until next click
            topo.guimain.after(250,lambda x=tk_var._last_good_val: tk_var.set(x))
            raise

        if hasattr(tk_var,'_on_change'): tk_var._on_change()

    # Could define attribute resolution order so that attributes from
    # this object (which could also be e.g. a Frame) are returned
    # first, then parameters from the parameterized_object (so
    # parameters could be accessed as attributes of this object).

    # (if we're going to have these, should update the gui display too)
    def get_param(self,name):
        return getattr(self._parameterized_object,name)

    def set_param(self,name,value):
        # have to go through this method for tk_var to be updated, but
        # we probably won't be using this at all.
        setattr(self._parameterized_object,name,value)
        # why 'if name'? better have it, no?
        if name in self._tk_vars: self._tk_vars[name].set(value)



import _tkinter # (required to get tcl exception class)

# CB: needs renaming
class WidgetDrawingTkPO(TkPO,Frame):
    """
    A TkPO and Tkinter Frame that can draw widgets representing the Parameters of the supplied po.
    """
    def __init__(self,po,master,**config):
        """
        (Frame.__init__ gets the config.)
        """
        assert master is not None # (could probably remove this but i didn't want to think about it)
        TkPO.__init__(self,po)
        Frame.__init__(self,master,**config)
        self.balloon = Pmw.Balloon(self)

        # a refresh-the-widgets-on-focus-in method would make the gui in sync with the actual object


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
        f = Frame(parent or self)
        
        param = self._parameterized_object.params()[name]
        widget_type = parameters_to_tkwidgets.get(type(param),Entry)
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

        # f's probably better than w
        self.balloon.bind(f,getdoc(param))

        f.pack(pack_options)
        return f 



## ### some demo
## class SomeFrame(WidgetDrawingTkPO):

##     def __init__(self,po,master,**config):
##         WidgetDrawingTkPO.__init__(self,po,master)
    
##         for name in po.params().keys():
##             Tkinter.Label(self,text=name).pack()
##             self.pack_param(name)


## from topo.patterns.basic import Gaussian        
## g = Gaussian()
## f = SomeFrame(g,Tkinter.Toplevel())
## f.pack()


### plotgroup template demo

## from topo.plotting.templates import plotgroup_templates
## class ExamplePlotGroupPanel(WidgetDrawingTkPO):
##     def __init__(self,pgt_name,master):
##         pgt = plotgroup_templates[pgt_name]
##         WidgetDrawingTkPO.__init__(self,pgt,master)

##         for name in pgt.params().keys():
##             self.pack_param(name)



## e = ExamplePlotGroupPanel("Activity",Tkinter.Toplevel())
## e.pack()
