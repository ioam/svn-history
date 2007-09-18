"""
Classes for manipulating all the Parameters of a ParameterizedObject.

LiveParametersFrame and ParametersFrame display the Parameters of a
supplied ParameterizedObject. Both allow these Parameters to be
edited; LiveParametersFrame applies changes immediately as they are
made, whereas ParametersFrame makes no changes until a confirmation is
given (by pressing the 'Apply' button, for instance).


$Id$
"""
__version__='$Revision$'


# CEBNOTE: now we can consider having something that indicates if a
# value has changed, and greying out irrelevant buttons (e.g. Apply
# when there are no differences). Just depends on having a refresh
# occur at the right time.

# CEBNOTE: e.g. type SheetMask(), get new one every time click Apply.
# Could stop by overwriting user-typed stuff with actual value, but
# then we'd lose things like pi hanging around in the
# display. Alternatively could add SheetMask() to translator
# dictionary, so no new object would get created for that text for the
# lifetime of the window, but could be risky - what if someone expects
# a new one each time?

# CEBALERT: need to catch window close event so it uses the same exit handling
# as the close button

# CEBALERT: apply/reset etc button positions need to be fixed.

# CEBERRORALERT: semantics of all the buttons needs to be checked.
# In particular, defaults button has surprising behavior.

import Tkinter, tkMessageBox

from Tkinter import Frame, E,W, Label
from inspect import getdoc

from topo.base.parameterizedobject import ParameterizedObject, \
                                          ParameterizedObjectMetaclass

from topo.misc.utils import keys_sorted_by_value

from tkguiwindow import Menu,TkguiWindow
from tkparameterizedobject import TkParameterizedObject, ButtonParameter, \
                                  parameters



class LiveParametersFrame(TkParameterizedObject,Frame):
    """
    Displays and allows instantaneous editing of the Parameters
    of a supplied ParameterizedObject.
    """
    Defaults = ButtonParameter(doc=
        """Return object's Parameters to class defaults.""")

    # CEBALERT: this is a Frame, so close isn't likely to make
    # sense. But fortunately the close button acts on master.
    # Just be sure not to use this button when you don't want
    # the master window to vanish (e.g. in the model editor).
    Close = ButtonParameter(doc="Close the parent window.")

    def __init__(self,master,parameterized_object=None,on_change=None,
                 on_modify=None,**params):
        """
        Create a LiveParametersFrame with the specifed master, and
        representing the Parameters of parameterized_object.

        on_change is an optional function to call whenever any of the
        GUI variables representing Parameter values is set() by the
        GUI. Since a variable's value is not necessarily changed by
        such a set(), on_modify is another optional function to call
        only when a GUI variable's value changes.
        (See TkParameterizedObject for more detail.)
        """
        Frame.__init__(self,master)
        TkParameterizedObject.__init__(self,master,
                                       extraPO=parameterized_object,
                                       self_first=False,**params)

        self.on_change= on_change
        self.on_modify = on_modify

        ## Frame for the Parameters
        self._params_frame = Frame(self)
        self._params_frame.pack(side='top',expand='yes',fill='both')

        if parameterized_object:
            self.set_PO(parameterized_object,on_change=on_change,
                        on_modify=on_modify)

        ## Frame for the Buttons
        self._buttons_frame = Frame(self)
        self._buttons_frame.pack(side='bottom',expand='yes',fill='x')
        
        self.pack_param('Defaults',parent=self._buttons_frame,
                        on_change=self.defaultsB,side='left')
        Frame(self._buttons_frame,width=20).pack(side='left') # spacer
        self.pack_param('Close',parent=self._buttons_frame,
                        on_change=self.closeB,side='right')

        ### Right-click menu for widgets
        self.option_add("*Menu.tearOff", "0") 
        self.menu = Menu(self)
        self.menu.insert_command('end',label='Properties',
            command=lambda:self.__edit_PO_in_currently_selected_widget())

        # CEBALERT: just because callers assume this pack()s itself.
        # Really it should be left to callers i.e. this should be removed.
        self.pack(expand='yes',fill='both') 


    
    


    # CEBALERT: all thses on_change=None mean someone could lose their initial setting which
    # will suprise them: claenup
    def set_PO(self,parameterized_object,on_change=None,on_modify=None):

        self.change_PO(parameterized_object)

        try:
            self.master.title("Parameters of "+ (parameterized_object.name or str(parameterized_object)) ) # classes dont have names
        except AttributeError:
            pass # can only set window title on a window (model editor puts frame in another frame)

        ### Pack all of the non-hidden Parameters
        self.displayed_params = {}
        for n,p in parameters(parameterized_object).items():
            if not p.hidden:
                self.displayed_params[n]=p
            
        ### Delete all variable traces
        # (don't want to update parameters immediately)
        #for v in self._tk_vars.values():
        #    self.__delete_trace(v)
        #    v._checking_get = v.get
        #    v.get = v._original_get
        
        self.pack_displayed_params(on_change=on_change,on_modify=on_modify)
        
    create_widgets = set_PO

    # CEBALERT: name doesn't make sense! change displayed_params to something else e.g. params_to_display
    def pack_displayed_params(self,on_change=None,on_modify=None):


        # basically original ParametersFrame.__new_widgets


        # wipe old labels and widgets from screen
        if hasattr(self,'currently_displaying'):
            for rep in self.currently_displaying.values():
                try:
                    rep['label'].destroy()
                except AttributeError:
                    # e.g. buttons have None for label
                    pass
                rep['widget'].destroy()
                

        # sort Parameters by reverse precedence
        parameter_precedences = {}
        for name,parameter in self.displayed_params.items():
            parameter_precedences[name]=parameter.precedence
        sorted_parameter_names = keys_sorted_by_value(parameter_precedences)
            
        # create the labels & widgets
        for name in self.displayed_params:
            widget,label = self.create_widget(name,self._params_frame,on_change=on_change or self.on_change,
                                              on_modify=on_modify or self.on_modify)
            self.representations[name]={'widget':widget,'label':label}

        
        
        # add widgets & labels to screen in a grid
        rows = range(len(sorted_parameter_names))
        for row,parameter_name in zip(rows,sorted_parameter_names): 
            widget = self.representations[parameter_name]['widget']

            label = self.representations[parameter_name]['label']

            help_text = getdoc(self.get_parameter_object(parameter_name))

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

        self.currently_displaying = dict([(param_name,self.representations[param_name])
                                        for param_name in self.displayed_params])



    # CEBERRORALERT: shouldn't set straight onto the object: wait for Apply.
    def defaultsB(self):
        if isinstance(self._extraPO,ParameterizedObjectMetaclass):
            raise NotImplementedError, "Unfinished"

        self._extraPO.reset_params()

        # CEBERRORALERT: need a (/to call a) refresh method.
        #self._sync_tkvars2po()
        


        
    def closeB(self):
        ## CEBALERT: dialog box should include a cancel button
        #if self.has_unapplied_change() and tkMessageBox.askyesno("Close","Apply changes before closing?"):
        #    self.update_parameters()
        Frame.destroy(self) # hmm
        self.master.destroy()
            

    def _create_string_widget(self,frame,name,widget_options):
        w = TkParameterizedObject._create_string_widget(self,frame,name,widget_options)
        # for right-click editing of anything!...
        #w.bind('<<right-click>>',lambda event: self.__right_click(event, w))
        return w
        
    def _create_selector_widget(self,frame,name,widget_options):
        w = TkParameterizedObject._create_selector_widget(self,frame,name,widget_options)
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
        for name,representation in self.representations.items():
            if self.__currently_selected_widget is representation['widget']:
                param_name=name
                break

        PO_to_edit = self.string2object_ifrequired(param_name,self._tk_vars[param_name].get()) #get_parameter_value(param_name)

        parameter_window = TkguiWindow()
        parameter_window.title(PO_to_edit.name+' parameters')

        ### CB: could be confusing?
        title=Tkinter.Label(parameter_window, text="("+param_name + " of " + self._extraPO.name + ")")
        title.pack(side = "top")
        self.balloon.bind(title,getdoc(self.get_parameter_object(param_name,self._extraPO)))
        ###
        
        parameter_frame = type(self)(parameter_window,parameterized_object=PO_to_edit)

        parameter_frame.pack()


    # CEBALERT: clean this up.
    def unpack_param(self,param_name):
        raise NotImplementedError
    # because it's unfinished (need to remove from list of displayed params)
    # super(ParametersFrame,self).unpack_param(param_name)
    # also need to do hide,unhide - probably




# CB: names still seem strange...ParametersFrame inherits from
# LiveParametersFrame?
class ParametersFrame(LiveParametersFrame):

    

    Apply = ButtonParameter(doc="""Set object's Parameters to displayed values.
                                   When editing a class, sets the class defaults
                                   (i.e. acts on the class object).""")
    

    # (CEBNOTE: used to be called Reset)
    Refresh = ButtonParameter(doc="Return values to those currently set on the object")  

    def __init__(self,master,parameterized_object=None,on_change=None,on_modify=None,**params):        
        super(ParametersFrame,self).__init__(master,parameterized_object,on_change,on_modify,**params)

        for p in self.param_immediately_apply_change: self.param_immediately_apply_change[p]=True
            
        
        self.pack_param('Apply',parent=self._buttons_frame,on_change=self.apply_button,side='left')
        self.pack_param('Refresh',parent=self._buttons_frame,on_change=self._sync_tkvars2po,side='right')


    def _create_string_widget(self,frame,name,widget_options):
        w= super(ParametersFrame,self)._create_string_widget(frame,name,widget_options)
        w.unbind('<Return>')
        return w

    def set_PO(self,parameterized_object,on_change=None,on_modify=None):
        self.change_PO(parameterized_object)

        try:
            self.master.title("Parameters of "+ (parameterized_object.name or str(parameterized_object)) ) # classes dont have names
        except AttributeError:
            pass # can only set window title on a window (model editor puts frame in another frame)

        ### Pack all of the non-hidden Parameters
        self.displayed_params = {}
        for n,p in parameters(parameterized_object).items():
            if not p.hidden:
                self.displayed_params[n]=p
            
        ### Delete all variable traces
        # (don't want to update parameters immediately)
        for v in self._tk_vars.values():
            self.__delete_trace(v)
            v._checking_get = v.get
            v.get = v._original_get
        
        self.pack_displayed_params(on_change=on_change,on_modify=on_modify)
    create_widgets = set_PO



    def _sync_tkvars2po(self):
        for name in self.displayed_params.keys():
            self._tk_vars[name]._checking_get()

    def defaultsB(self):
        super(ParametersFrame,self).defaultsB()
        self._sync_tkvars2po()

    def has_unapplied_change(self):
        """Return True if any one of the packed parameters' displayed values is different from
        that on the object."""
        for name in self.displayed_params.keys():
            if self.__value_changed(name):
                return True
        return False

    def closeB(self):
        # CEBALERT: dialog box should include a cancel button
        if self.has_unapplied_change() and tkMessageBox.askyesno("Close","Apply changes before closing?"):
            self.update_parameters()
        super(ParametersFrame,self).closeB()


    __value_changed = TkParameterizedObject.value_changed


    def __delete_trace(self,var):
        var.trace_vdelete(*var.trace_vinfo()[0])

    def update_parameters(self):
        if isinstance(self._extraPO,ParameterizedObjectMetaclass):
            for name in self.displayed_params.keys():
                if self.__value_changed(name):
                    self._update_param(name)
        else:
            for name,param in self.displayed_params.items():
                if not param.constant and self.__value_changed(name):
                    self._update_param(name)

    def apply_button(self):
        self.update_parameters()
        self._sync_tkvars2po()
        

    set_parameters=update_parameters



# CEBALERT: should be in something like tkgui.commands.
# (Designed for use at the commandline.)
def edit_parameters(parameterized_object,live=False,**params):
    """
    Edit the Parameters of parameterized_object.

    Specify live=True for a LiveParametersFrame (immediately
    updates the object - no need to press the Apply button).

    Extra params are passed to the ParametersFrame constructor.
    """
    if not (isinstance(parameterized_object,ParameterizedObject) or \
           isinstance(parameterized_object,ParameterizedObjectMetaclass)):
        raise ValueError("Can only edit parameters of a ParameterizedObject.")

    if live:
        pf_class = LiveParametersFrame
    else:
        pf_class = ParametersFrame

    return pf_class(Tkinter.Toplevel(),parameterized_object,**params)

    
