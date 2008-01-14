"""
Classes for graphically manipulating all the Parameters of a ParameterizedObject.

ParametersFrame and ParametersFrameWithApply display the Parameters of
a supplied ParameterizedObject. Both allow these Parameters to be
edited; ParametersFrame applies changes immediately as they are made,
whereas ParametersFrameWithApply makes no changes until a confirmation
is given (by pressing the 'Apply' button).


ParametersFrame extends TkParameterizedObject; see TkParameterizedObject
for the underlying details of representing Parmeters in the GUI.


$Id$
"""
__version__='$Revision$'


# CEB: still working on this file


# KNOWN ISSUES
#
# - Defaults button doesn't work for SelectorParameters (need to insert
#   new (class default) object into the list).
#

import Tkinter, tkMessageBox

from Tkinter import Frame, E,W, Label, TclError
from inspect import getdoc

from topo.base.parameterizedobject import ParameterizedObject, \
                                          ParameterizedObjectMetaclass

from topo.misc.utils import keys_sorted_by_value

from widgets import Menu
from topowidgets import TkguiWindow
from tkparameterizedobject import TkParameterizedObject, ButtonParameter



# CB: color buttons to match? deactivate irrelevant buttons?

class ParametersFrame(TkParameterizedObject,Frame):
    """
    Displays and allows instantaneous editing of the Parameters
    of a supplied ParameterizedObject.

    Changes made to Parameter representations on the GUI are
    immediately applied to the underlying object.
    """
    Defaults = ButtonParameter(doc="""Return values to class defaults.""")

    Refresh = ButtonParameter(doc="Return values to those currently set on the object (or, if editing a class, to those currently set on the class).")  

    # CEBALERT: this is a Frame, so close isn't likely to make
    # sense. But fortunately the close button acts on master.
    # Just be sure not to use this button when you don't want
    # the master window to vanish (e.g. in the model editor).
    Close = ButtonParameter(doc="Close the window. (If applicable, asks if unsaved changes should be saved).")

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
        actually changes. (See TkParameterizedObject for more detail.)
        """
        Frame.__init__(self,master,borderwidth=1,relief='raised')
        TkParameterizedObject.__init__(self,master,
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
        assert isinstance(self._extraPO,ParameterizedObject)

        defaults = self._extraPO.defaults()

        for param_name,val in defaults.items():
            if not self.get_parameter_object(param_name).hidden:
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
            if not p.hidden:
                self.displayed_params[n]=p
                    
        self.pack_displayed_params(on_change=on_change,on_modify=on_modify)

        # hide Defaults button for classes
        if isinstance(parameterized_object,ParameterizedObjectMetaclass):
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
                help_text+="\n\nDefault: %s"%self._object2string(parameter_name,param_obj.default)
        

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


    def switch_dynamic(self,name):
        # here: need to switch widget etc
        self.repack_param(x)


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
        w = TkParameterizedObject._create_selector_widget(self,frame,name,widget_options)
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

        parameter_window = TkguiWindow()
        parameter_window.title(PO_to_edit.name+' parameters')

        ### CEBALERT: confusing? ###
        title=Tkinter.Label(parameter_window, text="("+param_name + " of " + self._extraPO.name + ")")
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
##         TkParameterizedObject._indicate_tkvar_status(self,param_name)

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
    ParameterizedObject.

    Changes made to Parameter representations in the GUI are not
    applied to the underlying object until Apply is pressed.
    """

    # CB: might be nice to make Apply button blue like the unapplied changes,
    # but can't currently set button color
    Apply = ButtonParameter(doc="""Set object's Parameters to displayed values.\n
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
        ### Delete all variable traces
        # (don't want to update parameters immediately)
        for v in self._tkvars.values():
            self.__delete_trace(v)
            v._checking_get = v.get
            v.get = v._original_get


    def has_unapplied_change(self):
        """Return True if any one of the packed parameters' displayed values is different from
        that on the object."""
        for name in self.displayed_params.keys():
            if self._tkvar_changed(name):
                return True
        return False


    
##     def _handle_gui_set(self,p_name,force=False):
##         TkParameterizedObject._handle_gui_set(self,p_name,force)

##         if hasattr(self,'representations') and 'Apply' in self.representations:
##             w=self.representations['Apply']['widget']
##             if self.has_unapplied_change():
##                 w['foreground']='blue'
##             else:
##                 w['foreground']='black'
            



    def _close_button(self):
        # CEBALERT: dialog box should include a cancel button
        if self.has_unapplied_change() \
               and tkMessageBox.askyesno("Close","Apply changes before closing?"):
            self.update_parameters()
        super(ParametersFrameWithApply,self)._close_button()


    def update_parameters(self):
        if isinstance(self._extraPO,ParameterizedObjectMetaclass):
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


    def __delete_trace(self,var): pass #var.trace_vdelete(*var.trace_vinfo()[0])


    def _defaults_button(self):
        """See Defaults parameter."""
        assert isinstance(self._extraPO,ParameterizedObject)

        defaults = self._extraPO.defaults()

        for param_name,val in defaults.items():
            if not self.get_parameter_object(param_name).hidden:
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
    if not (isinstance(parameterized_object,ParameterizedObject) or \
           isinstance(parameterized_object,ParameterizedObjectMetaclass)):
        raise ValueError("Can only edit parameters of a ParameterizedObject.")

    if not with_apply:
        pf_class = ParametersFrame
    else:
        pf_class = ParametersFrameWithApply

    return pf_class(Tkinter.Toplevel(),parameterized_object,**params)

    
