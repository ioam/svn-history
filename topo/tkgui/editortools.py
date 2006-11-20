"""
Tools for the model editor GUI toolbar.

Originally written by Alan Lindsay.
$Id$
"""
__version__='$Revision$'

from Tkinter import Frame, Button, Label, Canvas, TOP, X, GROOVE, RAISED, BOTTOM, Toplevel
import Pmw
import tkFont

import topo.sheets
from topo.sheets import *
from topo.base.parameterizedobject import ParameterizedObject
from topo.base.parameterclasses import concrete_descendents
from topo.base.sheet import Sheet
import topo.projections
from topo.projections import *
from topo.base.projection import Projection

from editorobjects import EditorSheet, EditorProjection
from parametersframe import ParametersFrame

class ArrowTool(Frame):
    """
    ArrowTool is a selectable frame containing an arrow icon and a label. It is a
    toolbar item in a ModelEditor that allows the user to change the GUICanvas to 
    'ARROW' mode. 
    """

    def __init__(self, canvas,  parent = None, parambar = None):
        Frame.__init__(self, parent, bg = 'light grey', bd = 4, relief = RAISED)
        self.canvas = canvas # hold canvas reference
        self.parameter_tool = parambar # To display class properties and name
        # label sets canvas mode
        self.title_label = Label(self, text="Move:", bg ='light grey')
        self.title_label.bind('<Button-1>', self.change_mode)
        self.title_label.pack()
        self.doc = 'Use the arrow tool to select and\nmove objects in the canvas around'
        # arrow icon
        self.icon = Canvas(self, bg = 'light grey', width = 35, height = 30)
        self.icon.create_polygon(10,0, 10,22, 16,17, 22,29, 33,22, 25,13, 33,8, 
            fill = 'black', outline = 'white')
        self.icon.pack()
        self.icon.bind('<Button-1>', self.change_mode) # icon sets canvas mode
        # pack in toolbar at top and fill out in X direction; click changes canvas mode
        self.pack(side = TOP, fill = X)
        self.bind('<Button-1>', self.change_mode)
	
	
    def change_mode(self, event):
        self.canvas.change_mode('a') # (ARROW)

    def set_focus(self, focus):
        "Change the background highlight to reflect whether this toolbar item is selected."
        
        if (focus):
             col = 'dark grey'; relief = GROOVE
             if not(self.parameter_tool == None):
                 self.parameter_tool.set_focus('Arrow', None, self.doc)
        else:
            col = 'light grey'; relief = RAISED

        self.config(bg = col, relief = relief)
        self.title_label.config(bg = col)
        self.icon.config(bg = col)





class NodeTool(Frame):
    """
    NodeTool extends Frame. It is expected to be included in a topographica
    model development GUI and functions as a self populating Node tool.
    The available Sheet types are supplied to be selected from. This Tool supplies
    a suitable Editor cover for a node and creates the corresponding topo object.
    """

    def __init__(self, canvas,  parent = None, parambar = None):
        
        Frame.__init__(self, parent, bg = 'light grey', bd = 4, relief = RAISED)
        self.canvas = canvas # hold canvas reference.
        self.parameter_tool = parambar # To display class properties and name
        # bind clicks, pack in toolbar at top and fill out in X direction
        self.bind('<Button-1>', self.change_mode)
        self.pack(side = TOP, fill = X)
        # label sets canvas mode
        self.title_label = Label(self, text="Add sheet of type:", bg ='light grey')
        self.title_label.bind('<Button-1>', self.change_mode)
        self.title_label.pack()
        self.doc = 'Use the sheet tool to click a\nsheet object into the canvas.'
        # gets list of all the available sheets.
        self.sheet_list = concrete_descendents(Sheet)
        sheet_list = self.sheet_list.keys()
        # populate the menu with the available sheet list.
        self.option_menu = Pmw.ComboBox(self, selectioncommand = 
            self.set_option, scrolledlist_items = sheet_list)
        self.option_menu.pack()
        self.option_menu.bind('<Button-1>', self.change_mode)
        # select the initial selection
        self.option_menu.selectitem(sheet_list[0])
        self.current_option = sheet_list[0]


    #   Focus Methods
	
    def change_mode(self, option):
        self.canvas.change_mode('m') # ('MAKE')

    def set_focus(self, focus):
        "Change the background highlight to reflect whether this toolbar item is selected."
        
        if (focus):
            col = 'dark grey'; relief = GROOVE
            if not(self.parameter_tool == None):
                current_option = self.sheet_list[self.current_option]
                name = str(current_option).split('.')[-1][:-2]
                self.parameter_tool.set_focus(name, current_option, self.doc)
        else:
            col = 'light grey'; relief = RAISED
        self.config(bg = col, relief = relief)
        self.title_label.config(bg = col)
        self.option_menu.config(bg = col)


    #   Node Methods

    def create_node(self, x, y):
        if self.parameter_tool.focus:
            self.parameter_tool.update_parameters()
        # get the current selection and create the new topo object

        # CEBHACKALERT: because ParameterizedObject overwrites the name
        # unless it's passed in params when the object is created, I
        # pass the class name (set by ParametersFrame) here.
        # Same goes for projections.
        sheet_name=self.sheet_list[self.current_option].name
        if sheet_name is not None:
            sheet = self.sheet_list[self.current_option](name=sheet_name)
        else:
            sheet = self.sheet_list[self.current_option]()
            
        sim = self.canvas.simulation # get the current simulation
        sim[sheet.name] = sheet
        # create the cover for the sheet and return it.
        return EditorSheet(self.canvas, sheet, (x, y), sheet.name)


    #   Util Methods
    
    def set_option(self, option):
        self.current_option = option
        self.change_mode(None)




# JABHACKALERT: Currently only searches for topo.projections (connections have not been implemented yet).
class ConnectionTool(Frame):
    """ 
    ConnectionTool extends Frame. It is expected to be included in a topographica
    model development GUI and functions as a self populating Connection toolbar.
    The available Connection types are listed and the user can select one.
    When a connection is formed between two nodes a topo.projection of the
    specified type is instantiated and a reference to it is stored in it's Editor
    cover. Allows user to change the EditorCanvas mode to 'CONNECTION' mode.
    """

    def __init__(self, canvas, parent = None, parambar = None):
        # super constructor call.
        Frame.__init__(self, parent, bg = 'light grey', bd = 4, relief = RAISED)
        self.canvas = canvas # hold canvas reference.
        self.parameter_tool = parambar # To display class properties and name
        # bind clicks, pack in toolbar at top and fill out in X direction
        self.bind('<Button-1>', self.change_mode)
        self.pack(side = TOP, fill = X)
        # label sets canvas mode
        self.title_label = Label(self, text="Add projection of type:", bg ='light grey')
        self.title_label.bind('<Button-1>', self.change_mode)
        self.title_label.pack()
        self.doc = 'Use the connection tool to\ndrag connections between objects'
        # gets list of all the available projections.
        self.proj_list = concrete_descendents(Projection)
        proj_list = self.proj_list.keys() # gets the class names.
        # populate the menu with the available projection list.
        self.option_menu = Pmw.ComboBox(self, selectioncommand = 
            self.set_option, scrolledlist_items = proj_list)
        self.option_menu.bind('<Button-1>', self.change_mode)
        self.option_menu.pack()
        # select the initial selection
        self.option_menu.selectitem(proj_list[0])
        self.current_option = proj_list[0]


    #   Canvas Topo Linking Methods

    def new_cover(self, from_node):
        """
        Create an EditorProjection and return it.

        If there is more than one representation for connections/
        projections, the returned object will depend on the current
        selection.
        """
        return EditorProjection("", self.canvas, from_node)

    def create_connection(self, editor_connection, node):
        "Connects the editor connection and the topo simulation connection."

        if self.parameter_tool.focus:
            self.parameter_tool.update_parameters()
        sim = self.canvas.simulation
        from_node = editor_connection.from_node.sheet
        to_node = node.sheet
        con_type = self.proj_list[self.current_option]
        con_name = con_type.name
        # CEBHACKALERT: see alert about sheet name

        # CEBHACKALERT: should probably catch a specific error?
        try:
            if con_name is not None:
                con = sim.connect(from_node.name,to_node.name,connection_type=con_type,name=con_name)
            else:
                con = sim.connect(from_node.name,to_node.name,connection_type=con_type)
        except Exception, e:
            ParameterizedObject().warning("Unable to connect these sheets with the given "+ self.current_option + " (" + str(e) +").")
            editor_connection.remove()
            return False
        
        editor_connection.connect(node, con)
        return True

    def set_option(self, option):
        self.current_option = option
        self.change_mode(None)


    #   Focus Methods
    
    def change_mode(self, option):
        self.canvas.change_mode('c') # ('CONNECTION')

    def set_focus(self, focus):
        "Change the background highlight to reflect whether this toolbar item is selected."
        
        if (focus):
            col = 'dark grey'; relief = GROOVE
            if not(self.parameter_tool == None):
                current_option = self.proj_list[self.current_option]
                name = str(current_option).split('.')[-1][:-2]
                self.parameter_tool.set_focus(name, current_option, self.doc)
        else:
            col = 'light grey'; relief = RAISED
        self.config(bg = col, relief = relief)
        self.title_label.config(bg = col)
        self.option_menu.config(bg = col)




class ParametersTool(Frame):

    def __init__(self, parent = None):
        Frame.__init__(self, parent)
        self.focus = None
        # label
        self.title_label = Label(self)
        self.title_label.pack(side = TOP)
        self.doc_label = Label(self, font = ("Times", 12))
        self.doc_label.pack(side = TOP)

        # CEBHACKALERT: the problem is, a tiny little window
        # with nothing in it opens when the model editor is
        # started. If it's shut, there'll be an error if someone
        # tries to add a new object.
        parameter_window = Toplevel() #self
        parameter_window.title('New object parameters')
        #Label(parameter_window, text = "Edit class p").pack(side = TOP)
        self.parameter_frame = ParametersFrame(parameter_window)
        self.parameter_window=parameter_window

    def update_parameters(self):
        self.parameter_frame.set_parameters()

    def set_focus(self, name, focus_class, doc = ''):
        self.focus = name
            
        self.title_label.config(text = name)
        self.doc_label.config(text = doc)

        if focus_class:
            self.parameter_frame.create_widgets(focus_class)

            
            
