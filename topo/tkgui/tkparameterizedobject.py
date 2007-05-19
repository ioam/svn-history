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
    the Tkinter Variable shadow is NOT updated. Requesting t.p will correctly
    return 7, but the Tkinter Variable is still set to the old value.  
    """
    # if the above becomes a problem, we could have some autorefresh of the vars
    # or a callback of some kind in the parameterized object itself.
    
    _tk_vars = None
    _parameterized_object = None

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
            self._tk_vars[name]=parameters_to_tkvars.get(type(param),StringVar)()
            self._tk_vars[name].set(getattr(self._parameterized_object,name))
            self._tk_vars[name]._last_good_val=self._tk_vars[name].get() # for reverting
            self._tk_vars[name].trace_variable('w',lambda a,b,c,p_name=name: self.__update_param(p_name))        

        # Instead of a trace, could we override the Variable's set() method i.e. trace it ourselves?
        # Or does too much happen in tcl/tk for that to work?
        # Additionally, maybe we should override the Variable's get() method so that it first updates
        # the var to match the parameter?

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
        val = tk_var.get()
        
        try:
            setattr(self._parameterized_object,param_name,val)
        except:
            #tk_var.set(tk_var._last_good_val)
            # hack: above is too fast for gui? variable changes correctly, but doesn't appear
            # on gui until next click
            topo.guimain.after(250,lambda x=tk_var._last_good_val: tk_var.set(x))
            raise


    def __getattribute__(self,name):
        """
        Return self.name if that attribute exists, otherwise return
        self._parameterized_object.name.

        If neither self.name nore self._parameterized_object.name
        exists, an AttributeError is raised for the
        parameterized_object.
        """
        try:
            return object.__getattribute__(self,name)
        except AttributeError:
            parameterized_object = object.__getattribute__(self,'_parameterized_object')
            return getattr(parameterized_object,name)

    def __setattr__(self,name,value):
        try:
            object.__getattribute__(self, name) 
            object.__setattr__(self, name, value)
        except AttributeError:
            object.__setattr__(self._parameterized_object, name, value)
            # why 'if name'? better have it, no?
            if name in self._tk_vars: self._tk_vars[name].set(value)
                    

import _tkinter # (required to catch tcl exception)
# Needs renaming. Could be a Frame, too. 
class WidgetDrawingTkPO(TkPO):
    """
    A TkPO that can create widgets on a specified Tkinter Widget (master).
    """
    def __init__(self,po,tkmaster):
        super(WidgetDrawingTkPO,self).__init__(po)
        assert tkmaster is not None # need tkmaster for widget creation
        self.tkmaster = tkmaster
        self.balloon = Pmw.Balloon(tkmaster)

    def pack_param(self,name,widget_options={},**pack_options):
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
        param = self.params()[name]
        widget_type = parameters_to_tkwidgets.get(type(param),Entry)
        tk_var = self._tk_vars[name]

        try:
            w = widget_type(self.tkmaster,variable=tk_var,**widget_options)
        except _tkinter.TclError:
            try:
                w = widget_type(self.tkmaster,textvariable=tk_var,**widget_options)
            except _tkinter.TclError:
                raise # meaning the widget doesn't support variable or textvariable
        
        self.balloon.bind(w,getdoc(self.params()[name]))

        w.pack(pack_options)
        return w 



### demo
class SomeFrame(WidgetDrawingTkPO,Frame):

    def __init__(self,po,master,**config):
        WidgetDrawingTkPO.__init__(self,po,tkmaster=master)
        Frame.__init__(self,master,**config)
        
        for name in po.params().keys():
            Tkinter.Label(master,text=name).pack()
            self.pack_param(name)


#from topo.patterns.basic import Gaussian        
#g = Gaussian()
#f = SomeFrame(g,Tkinter.Toplevel())


# ** direct changes to g are not reflected in f's tkinter shadows **






