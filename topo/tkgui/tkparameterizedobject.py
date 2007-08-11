"""
TkParameterizedObject and associated classes, linking Parameters
and tkgui.

$Id$
"""

# CB: this file has now gone beyond the maximum complexity limit

### CEB: currently working on this file

import __main__

from inspect import getdoc
import Tkinter
from Tkinter import BooleanVar, StringVar, DoubleVar, IntVar,Frame, Tk, Checkbutton, Entry, Button,OptionMenu
import Pmw

import topo

from topo.base.parameterizedobject import ParameterizedObject,Parameter,classlist,ParameterizedObjectMetaclass
from topo.base.parameterclasses import BooleanParameter,StringParameter,Number,SelectorParameter,ClassSelectorParameter,ObjectSelectorParameter

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





# CB: ClassSelectorParam/ObjectSelectorParam work in progress; most
# of the current tests to distinguish them should go away.

# ClassSelectorParameter has its value set to an OBJECT but lists range of CLASSES
# ObjectSelectorParameter has its value set to an OBJECT, and lists range of OBJECTS



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
    
    (1) Attribute lookup follows a precedance order, object>shadowed POs (
    (with the shadowed POs being in order of their initial specification):

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

    _extraPO = None
    _tk_vars = {}
    translators = {}
    me_first = True  # for precedence 
    


    # CBENHANCEMENT: __repr__ will need some work (display params of subobjects etc?).

    
    def _parameters(self,parameterized_object):
        """
        ParameterizedObjectMetaclass has classparams(); ParameterizedObject has params().
        """
        if isinstance(parameterized_object,ParameterizedObjectMetaclass):
            return parameterized_object.classparams()
        elif isinstance(parameterized_object,ParameterizedObject):
            return parameterized_object.params()
        else:
            raise TypeError(`parameterized_object`+" is not a ParameterizedObject or ParameterizedObjectMetaclass.")



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
    def __init__(self,extraPO=None,me_first=True,**params):

        self.me_first = me_first
        self._extraPO = extraPO
        self._tk_vars = {}
        self.translators = {}
        
        super(TkParameterizedObjectBase,self).__init__(**params)

        for PO in self._source_POs()[::-1]:
            self._init_tk_vars(PO)


    def _init_tk_vars(self,PO):
        """
        Create Tkinter Variable shadows of all Parameters of PO.
        
        The appropriate Variable is used for each Parameter type.

        Also adds tracing mechanism to keep the Variable and Parameter values in sync.
        
        For a Parameter with the 'range' attribute, also updates the translator dictionary to
        map string representations to the objects themselves.
        """
        for name,param in self._parameters(PO).items():

            # shouldn't need second check but seems range could be None or something else not like a list?
            #if hasattr(param,'range') and hasattr(param.range,'__len__'): 
            self._update_translator(name,param)

            tk_var = parameters_to_tkvars.get(type(param),StringVar)()
            self._tk_vars[name] = tk_var

            # overwrite Variable's set() with one that will handle transformations to string
            tk_var._original_set = tk_var.set
            tk_var.set = lambda v,x=name: self.__set_tk_val(x,v)

            tk_var.set(getattr(PO,name))
            tk_var._last_good_val=tk_var.get() # for reverting
            tk_var.trace_variable('w',lambda a,b,c,p_name=name: self._update_param(p_name))        
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

        current_param_value = self.get_parameter_value(name)
        #t=self.translators[name]={}
        # store list of OBJECTS for ClassSelectorParameter's
        # range (although CSParam's range uses classes; matches parametersframe.ParametersFrame behavior)
        if isinstance(param,ClassSelectorParameter): #hasattr(param,'range'):
            t=self.translators[name]={}

            for n,o in param.range().items():

                # ** current value takes the place of inst'd class
                # or we lose the object
                if type(current_param_value)==o:
                    t[n] = current_param_value
                else:
                    t[n] = o()
                
        elif isinstance(param,ObjectSelectorParameter):
            t=self.translators[name]={}
            for n,o in param.range().items():
                t[n] = o
#        else:

#            t[repr(current_param_value)] = current_param_value
            



    def tra(self,v):

        try:
            k=eval(v,__main__.__dict__)
        except TypeError:
            k=v

        return k
        
    
    def string2object_ifrequired(self,param_name,val):
        """
        If val is in param_name's translator, then translate to the object.
        """
        new_val = val

        if param_name in self.translators:
            t = self.translators[param_name]
            if val in t:
                new_val = t[val]
        else:
            new_val = self.tra(val)
            
        #else:
        #    # ALWAYS evaluate, which means strings must be quoted in the GUI
        #    new_val = self.tra(val)



        return new_val
    converta = string2object_ifrequired  #CB: old method name - remove when unused


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
    atrevnoc = object2string_ifrequired  #CB: old method name - remove when unused
        
            

    def _update_param(self,param_name):
        """
        Attempt to set the parameter represented by param_name to the
        value of its corresponding Tkinter Variable.

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
            ### if it will always work.
            return 

        val = self.string2object_ifrequired(param_name,val)

        
        try:
            sources = self._source_POs()
            
            for po in sources:
                if param_name in self._parameters(po).keys():
                    parameter = self._parameters(po)[param_name]
                    ## use set_in_bounds if it exists: i.e. users of widgets get their
                    ## values cropped (no warnings/errors)
                    if hasattr(parameter,'set_in_bounds') and isinstance(po,ParameterizedObject):
                        #setattr(po,param_name,val)
                        #try:
                        parameter.set_in_bounds(po,val)
                        #except TypeError: # CEBHACKALERT: set_in_bounds not valid for POMetaclass
                        #    setattr(po,param_name,val)
                    else:
                        setattr(po,param_name,val)
                        
                    if hasattr(tk_var,'_on_change'): tk_var._on_change()
                    return # hidden


            assert False,"Error in use of _update_param: param must exist" # remove this
            
        except: # everything
            tk_var.set(tk_var._last_good_val)
            # CEBALERT: is above too fast for gui? variable changes correctly, but sometimes doesn't appear
            # on gui until next click? Needs more testing. Could try:
            #topo.guimain.after(250,lambda x=tk_var._last_good_val: tk_var.set(x))
            raise # whatever the parameter-setting error was


    def _source_POs(self,parameterized_object=None):
        """
        Return a correctly ordered list of ParameterizedObjects in which to find Parameters
        (unless one is specified, in which case it's the only item in the list).
        """
        if parameterized_object:
            sources = [parameterized_object]
        elif not self._extraPO:
            sources = [self]
        elif self.me_first:
            sources = [self,self._extraPO]
        else:
            sources = [self._extraPO,self]
        return sources
    

    def get_parameter(self,name,parameterized_object=None):
        """
        Return the Parameter specified by the name from the sources of
        Parameters in this object (or the specified parameterized_object).
        """
        sources = self._source_POs(parameterized_object)
        
        for po in sources:
            params = self._parameters(po)
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
        sources = self._source_POs(parameterized_object)

        for po in sources:
            params = self._parameters(po)
            if name in params: return getattr(po,name) # also hidden!

        raise AttributeError("none of %s have parameter %s"%(str(sources),name))

        
    def set_parameter_value(self,name,val,parameterized_object=None):
        """
        Set the value of the parameter specified by name to val.
        """
        sources = self._source_POs(parameterized_object)

        for po in sources:
            if name in self._parameters(po).keys(): 
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

# (also they ignore me_first)

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
            if hasattr(extraPO,name): return getattr(extraPO,name) 
            
            raise AttributeError("Neither %s nor %s has attribute %s"%(self,extraPO,name))
                    

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

# CEBHACKALERT: need to update this; not currently used in any code but testing
    def initialize_ranged_parameter(self,param_name,range_):
        p = self.get_parameter(param_name)

        if hasattr(range_,'__len__'):
            [p.Arange.append(x) for x in range_]
        else:
            p.Arange.append(range_)

        p.default = p.Arange[0]
        self._update_translator(param_name,p)



import _tkinter # (required to get tcl exception class)

class TkParameterizedObject(TkParameterizedObjectBase):
    """
    A TkParameterizedObjectBase that can draw widgets representing the
    Parameters of its ParameterizedObject(s).
    """

    pretty_parameters = BooleanParameter(default=True,doc=
                                         """Whether to format parameter names, or display
                                         the variable names instead.""")
    
    def __init__(self,master,extraPO=None,me_first=True,**params):
        self.master = master
        TkParameterizedObjectBase.__init__(self,extraPO=extraPO,me_first=me_first,**params)

        self.balloon = Pmw.Balloon(master)

        # map of Parameter classes to appropriate widget-creation method
        self.widget_creators = {
            BooleanParameter:self._create_boolean_widget,
            Number:self._create_number_widget,
            ButtonParameter:self._create_button_widget,
            StringParameter:self._create_string_widget,
            SelectorParameter:self._create_ranged_widget}
            #ClassSelectorParameter:self._create_ranged_widget}
        

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


    # CB: do some widgets need to have <return> bound to frame's refresh?


##     def repackparam(self,name):
##         self._widgets[name].destroy()
##         self.pack_param(name,parent=self._furames[name])
        

    # move elsewhere
    # Will create some general function for converting parameter names to
    # a 'pretty' representation. Need to merge more of tkpo with param frame
    def pretty_print(self,s):
        if not self.pretty_parameters:
            return s
        else:
            n = s.replace("_"," ")
            n = n.capitalize()
            return n



### Methods to create widgets ###
    def _create_button_widget(self,frame,name,widget_options,command):
        return Button(frame,text=self.pretty_print(name),command=command,**widget_options)

    # CEB: rename 'ranged' after sorting out that Parameter (it is supposed to be temporary)
    def _create_ranged_widget(self,frame,name,widget_options):
        param = self.get_parameter_object(name)
        self._update_translator(name,param)

        new_range = self.translators[name].keys()
        
        assert len(new_range)>0 # CB: remove

        tk_var = self._tk_vars[name]


        ############# 
        current_string = self.get_parameter_value(name)
        
        if isinstance(param,ObjectSelectorParameter):
            if current_string not in new_range: #param.range().values():
                current_string = new_range[0]
                
        if isinstance(param,ClassSelectorParameter):
            # need to break into the two possibilities of class & object
            if param.in_range(current_string):
                current_string = self.object2string_ifrequired(name,current_string)
            else:
                current_string = new_range[0]
            
        tk_var.set(current_string)
        #############

        w = OptionMenu(frame,tk_var,*new_range,**widget_options)

        help_text =getdoc(self.get_parameter_value(name))
        
        self.balloon.bind(w,help_text)
        
        return w 



    def _create_number_widget(self,frame,name,widget_options):
        widget = TaggedSlider(frame,variable=self._tk_vars[name],**widget_options)
        param = self.get_parameter_object(name)
        if param.bounds and param.bounds[0] and param.bounds[1]:
            # CEBALERT: TaggedSlider.set_bounds() needs BOTH bounds (neither can be None)
            widget.set_bounds(*param.bounds) # assumes set_bounds exists on the widget
        return widget

    def _create_boolean_widget(self,frame,name,widget_options):
        return Checkbutton(frame,variable=self._tk_vars[name],**widget_options)
        
    def _create_string_widget(self,frame,name,widget_options):
        w = Entry(frame,textvariable=self._tk_vars[name],**widget_options)

        # CEBHACKALERT: but need to be able to edit for a class!
        if self.get_parameter_object(name).constant:
            w['state']='readonly'
            w['fg']='gray45'
            
        return w
#################################


    # CEBALERT: on_change should be on_set (since it's called not only for changes)
    # CB: packing might need to be better (check eg label-widget space)
    def pack_param(self,name,parent=None,widget_options={},on_change=None,**pack_options):
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

        #if PO is None:
        param = self.get_parameter_object(name)
        #else:
        #    param = self._parameters(PO)[name]

        # default is label on the left
        label_side='left'; widget_side='right'

        # select the appropriate widget-creation method;
        # default is self._create_string_widget... 
        widget_creation_fn = self._create_string_widget
        # ...but overwrite that with a more specific one, if possible
        for c in classlist(type(param))[::-1]:
            if self.widget_creators.has_key(c):
                widget_creation_fn = self.widget_creators[c]
                break
            
        ### buttons are different from the other widgets: no label and no variable
        if widget_creation_fn==self._create_button_widget:
            assert on_change is not None, "Buttons need a command."
            label = None
            widget = widget_creation_fn(frame,name,widget_options,command=on_change)
        else:
            tk_var = self._tk_vars[name]
            if on_change is not None: tk_var._on_change=on_change
            widget = widget_creation_fn(frame,name,widget_options)

            # checkbuttons are 'widget label' rather than 'label widget'
            if widget.__class__ is Tkinter.Checkbutton:  # type(widget) doesn't seem to work
                widget_side='left'; label_side='right'

            label = Tkinter.Label(frame,text=self.pretty_print(name))
            label.pack(side=label_side)

        widget.pack(side=widget_side,expand='yes',fill='x')

        # CEBALERT: will just have one of these, and will be properly named.
        self._furames[name]=(frame,label); self._widgets[name]=widget

        # If there's a label, balloon's bound to it - otherwise, bound
        # to enclosing frame.
        # (E.g. when there's [label] [text_box], only want balloon for
        # label (because maybe more help will be present for what's in
        # the box) but when there's [button], want popup help over the
        # button.)
        self.balloon.bind(label or frame,getdoc(param))
        
        frame.pack(pack_options)
        return frame 



    # For convenience. Maybe should offer a way to access any attribute on master.
    # Probably too confusing - might remove this, too.
    def title(self,t):
        self.master.title(t)
        




# CB: ** just for testing at the moment **

##########################################################################################

from tkguiwindow import Menu,TkguiWindow

class ParametersFrame2(TkParameterizedObject,Frame):

    Apply = ButtonParameter()
    Defaults = ButtonParameter()
    Reset = ButtonParameter()
    Close = ButtonParameter()

    Refresh = ButtonParameter()

    def __init__(self,master,PO=None,**params):        
        Frame.__init__(self,master)
        self.master.title("Parameters of "+ (PO.name or str(PO)) ) # classes dont have names
        
        TkParameterizedObject.__init__(self,master,extraPO=PO,me_first=False,**params)

        ### Pack all of the non-hidden Parameters
        self.packed_params = {}
        for n,p in self._parameters(PO).items():
            if not p.hidden:
                self.pack_param(n)
                self.packed_params[n]=p
            
        ### Delete all variable traces
        # (don't want to update parameters immediately)
        for v in self._tk_vars.values():
            self.__delete_trace(v)
            v._checking_get = v.get
            v.get = v._original_get

        ### Right-click menu for widgets
        self.option_add("*Menu.tearOff", "0") 
        self.menu = Menu(self)
        self.menu.insert_command('end', label = 'Properties', command = lambda: 
            self.__edit_PO_in_currently_selected_widget())


        self.pack_param('Refresh',on_change=self._sync_tkvars2po)

        self.buttons_frame = Frame(self)
        self.buttons_frame.pack()
        
        self.pack_param('Apply',parent=self.buttons_frame,on_change=self.update_parameters,side='left')
        self.pack_param('Defaults',parent=self.buttons_frame,on_change=self.defaultsB,side='left')

        if isinstance(self._extraPO,ParameterizedObject):
            self.pack_param('Reset',parent=self.buttons_frame,on_change=self.resetB,side='left')
        
        self.pack_param('Close',parent=self.buttons_frame,on_change=self.closeB,side='left')


    def _sync_tkvars2po(self):
        for name in self.packed_params.keys():
            self._tk_vars[name]._checking_get()


    def defaultsB(self):
        if isinstance(self._extraPO,ParameterizedObjectMetaclass):
            print "what are these?"
        elif isinstance(self._extraPO,ParameterizedObject):
            self._extraPO.reset_params()
            self._sync_tkvars2po()
        

    def resetB(self):
        self._sync_tkvars2po()


    def closeB(self):
        # CEBALERT: warn if there are unapplied changes
        self.master.destroy()



    def __value_changed(self,name):
        if self.string2object_ifrequired(name,self._tk_vars[name]._original_get())!=getattr(self._extraPO,name):
            return True
        else:
            return False


    def __delete_trace(self,var):
        trace_mode = var.trace_vinfo()[0][0]
        trace_name = var.trace_vinfo()[0][1]
        var.trace_vdelete(trace_mode,trace_name)


    def update_parameters(self):
        if isinstance(self._extraPO,ParameterizedObjectMetaclass):
            for name in self.packed_params.keys():
                if self.__value_changed(name): self._update_param(name)
        else:    
            for name,param in self.packed_params.items():
                if not param.constant and self.__value_changed(name):
                    self._update_param(name)


    def _create_ranged_widget(self,frame,name,widget_options):
        w = TkParameterizedObject._create_ranged_widget(self,frame,name,widget_options)
        w.bind('<<right-click>>',lambda event: self.__right_click(event, w))
        return w


    def __right_click(self, event, widget):
        self.__currently_selected_widget = widget
        self.menu.tk_popup(event.x_root, event.y_root)


    # rename
    def __edit_PO_in_currently_selected_widget(self):
        """
        Open a new window containing a ParametersFrame for the 
        PO in __currently_selected_widget.
        """
        ### simplify this lookup-by-value!
        param_name = None
        for name,wid in self._widgets.items():
            if self.__currently_selected_widget is wid:
                param_name=name
                break

        PO_to_edit = self.get_parameter_value(param_name)

        parameter_window = TkguiWindow()
        parameter_window.title(PO_to_edit.name+' parameters')

        ### CB: could be confusing?
        title=Tkinter.Label(parameter_window, text="("+param_name + " of " + self._extraPO.name + ")")
        title.pack(side = "top")
        self.balloon.bind(title,getdoc(self.get_parameter_object(param_name,self._extraPO)))
        ###
        
        parameter_frame = type(self)(parameter_window,PO=PO_to_edit)

            
        

#./topographica -g examples/hierarchical.ty -c "from topo.tkgui.tkparameterizedobject import ParametersFrame2; import Tkinter; g = Gaussian(); p = ParametersFrame2(Tkinter.Toplevel(),PO=g); p.pack()"

#./topographica -g examples/hierarchical.ty -c "from topo.tkgui.tkparameterizedobject import ParametersFrame2; import Tkinter; g = Gaussian(); p = ParametersFrame2(Tkinter.Toplevel(),PO=g); p.pack(); p2 = ParametersFrame2(Tkinter.Toplevel(),PO=topo.sim['V1']); p2.pack(); p3 = ParametersFrame2(Tkinter.Toplevel(),PO=Gaussian); p3.pack(); p4 = ParametersFrame2(Tkinter.Toplevel(),PO=type(topo.sim['V1']))"
