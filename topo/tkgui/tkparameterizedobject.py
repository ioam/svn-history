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





class TkPO(object):
    """
    A PO but with additional Tkinter Variables available representing the Parameters.

    When a Parameter is __set__() (as an attribute,
    e.g. this_obj.param_name=val), sets the parameter value (which is
    stored in THIS object), AND set()s the corresponding Tkinter variable.
    (e.g. this_obj._tk_vars[param_name].set(val)).
    """

    #__slots__ = ['_tk_vars','po']
    _tk_vars = None
    po = None

    def __init__(self,po,**params):
        """
        tkmaster is the tk widget onto which widgets will be placed.
        """
        self.po = po
        self._tk_vars = {} # tk variables corresponding to this tkpo's parameters
        super(TkPO,self).__init__(**params)
        self.__setup_tk_vars()


    def __setup_tk_vars(self):
        """
        Create Tk Variables corresponding to the Parameter types, and store them in the
        _tk_vars dictionary under the corresponding parameter name.

        The tkinter Variable defaults to StringVar if no corresponding variable for the
        Parameter type is found in parameters_to_vars.
        
        A tk var is traced so that if its value changes the parameter value can
        be set on this object. If setting the parameter value fails (e.g. inappropriate
        value), the tk var is reverted.
        """
        for name,param in self.po.params().items():
            self._tk_vars[name]=parameters_to_tkvars.get(type(param),StringVar)()
            self._tk_vars[name].set(getattr(self.po,name))
            self._tk_vars[name]._last_good_val=self._tk_vars[name].get() # for reverting
            self._tk_vars[name].trace_variable('w',lambda a,b,c,p_name=name: self.update_param(p_name))     
  
    def update_param(self,param_name):
        """
        Attempt to set param_name to the value of its correspinding tk_var.
        """
        tk_var = self._tk_vars[param_name]
        val = tk_var.get()
        
        try:
            setattr(self.po,param_name,val)
        except:
            #tk_var.set(tk_var._last_good_val)
            # hack: above is too fast for gui? variable changes correctly, but doesn't appear
            # on gui until next click
            topo.guimain.after(250,lambda x=tk_var._last_good_val: tk_var.set(x))
            raise


    def __getattribute__(self,name):
        """
        If the SimSingleton object has the attribute, return it; if the
        actual_sim has the attribute, return it; otherwise, an AttributeError
        relating to Simulation will be raised (as usual).
        """
        try:
            return object.__getattribute__(self,name)
        except AttributeError:
            po = object.__getattribute__(self,'po')
            return getattr(po,name)

    def __setattr__(self,name,value):
        """
        If this object has the attribute name, set it to value.
        Otherwise, set self.actual_sim.name=value.

        (Unless an attribute is inserted directly into this object's
        __dict__, the only attribute it has is 'actual_sim'. So, this
        method really sets attributes on actual_sim.)
        """
        # read like:
        #  if hasattr(self,name):
        #      setattr(self,name,value)
        #  else:
        #      setattr(self.actual_sim,name,value)
        try:
            object.__getattribute__(self, name) 
            object.__setattr__(self, name, value)
        except AttributeError:
            object.__setattr__(self.po, name, value)
            # why 'if name'? better have it, no?
            if name in self._tk_vars: self._tk_vars[name].set(value)
                    


class WidgetDrawingTkPO(TkPO):

    def __init__(self,po,tkmaster,**params):
        super(WidgetDrawingTkPO,self).__init__(po,**params)
        # for widget creation
        assert tkmaster is not None
        self.tkmaster = tkmaster
        self.balloon = Pmw.Balloon(tkmaster)

    def create_widget(self,param_name,**kw):
        """
        Return a widget of the requested type, with ...
        """
        param = self.params()[param_name]
        widget_type = parameters_to_tkwidgets.get(type(param),Entry)
        tk_var = self._tk_vars[param_name]

        ### CB: obviously I'm just joking
        import _tkinter
        try:
            w = widget_type(self.tkmaster,variable=tk_var,**kw)
        except _tkinter.TclError:
            try:
                w = widget_type(self.tkmaster,textvariable=tk_var,**kw)
            except _tkinter.TclError:
                try:
                    w = widget_type(self.tkmaster,tagvariable=tk_var,**kw)
                except _tkinter.TclError:
                    raise _tkinter.TclError("no variable, textvariable, tagvariable")
        ### end of joke
        
        self.balloon.bind(w,getdoc(self.params()[param_name]))

        # could pack the widget, could pass in pack options, etc
        return w


class SomeFrame(WidgetDrawingTkPO,Frame):

    def __init__(self,po,master,**params):
        WidgetDrawingTkPO.__init__(self,po,tkmaster=master,**params)
        Frame.__init__(self,master)
        
        for name in po.params().keys():
            self.create_widget(param_name=name).pack()



from topo.patterns.basic import Gaussian        
g = Gaussian()
f = SomeFrame(g,Tkinter.Toplevel())








