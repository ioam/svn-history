"""
Window and canvas for the model editor GUI.

Originally written by Alan Lindsay.
$Id$
"""
__version__='$Revision$'

from Tkinter import Canvas, Frame, Checkbutton, Button, Toplevel, Tk, Menu, Scrollbar, SUNKEN, YES, BOTH, LEFT, END, RIGHT, TOP, BOTTOM, X, Y
from tkFileDialog import asksaveasfilename
from random import Random, random

import topo
from topo.base.sheet import Sheet
from topo.base.projection import Projection

from editorobjects import EditorNode, EditorSheet, EditorProjection
from editortools import ArrowTool, NodeTool, ConnectionTool, ParametersTool

class EditorCanvas(Canvas):

    """ 
    EditorCanvas extends the Tk Canvas class.
    There are 3 modes that determine the effect of mouse events in the Canvas
    A Canvas can accept new objects, move objects and make connections 
    between them. The intended use of this class is as the main
    canvas in a Topographica model-editing GUI. 
    """

    def __init__(self, root = None, width = 600, height = 600):
        Canvas.__init__(self, root, width = width, height = height, bg = "white", bd = 2, relief = SUNKEN)
        self.panel = Frame(root)
        self.panel.pack(side = TOP, fill = X)
        # Top bar of the canvas, allowing changes in size, display and to force refresh.
        Button(self.panel,text="Refresh", command=self.refresh).pack(side=LEFT)
        Button(self.panel,text="Reduce", command=self.reduce_scale).pack(side=LEFT)
        Button(self.panel,text="Enlarge", command=self.enlarge_scale).pack(side=LEFT)        
        self.auto_refresh = False
        self.console = topo.guimain
        self.auto_refresh_checkbutton = Checkbutton(self.panel,text="Auto-refresh",
                                                    command=self.toggle_auto_refresh)
        self.auto_refresh_checkbutton.pack(side=LEFT)

        self.normalize_checkbutton = Checkbutton(self.panel, text="Normalize",
                                                    command=self.toggle_normalize)

        self.normalize_checkbutton.pack(side=LEFT)
        if EditorNode.normalize == True:
            self.normalize_checkbutton.select()

        # retain the current focus in the canvas
        self.scaling_factor = 1.0
        self.current_object = None
        self.current_connection = None
        self.focus = None
        # list holding references to all the objects in the canvas	
        self.object_list = []
        # set the initial mode.
        self.display_mode = 'video'
        self.mode = "ARROW"
        self.MAX_VIEWS = 5
        # get the topo simulation
        self.simulation = topo.sim

        # create the menu widget used as a popup on objects and connections
        self.option_add("*Menu.tearOff", "0") 
        self.item_menu = Menu(self)
        self.view = Menu(self.item_menu)
        # add property, toggle activity drawn on sheets, object draw ordering and delete entries to the menu.
        self.item_menu.insert_command(END, label = 'Properties', 
            command = lambda: self.show_properties(self.focus))
        self.item_menu.add_cascade(label = 'Change View', menu = self.view, underline = 0)
        self.item_menu.insert_command(END, label = 'Move Forward', 
            command = lambda: self.move_forward(self.focus))
        self.item_menu.insert_command(END, label = 'Move to Front', 
            command = lambda: self.move_to_front(self.focus))
        self.item_menu.insert_command(END, label = 'Move to Back', 
            command = lambda: self.move_to_back(self.focus))
        self.item_menu.insert_command(END, label = 'Delete', 
            command = lambda: self.delete_focus(self.focus))
        # the indexes of the menu items that are for objects only
        self.object_indices = [2,3,4]

        self.canvas_menu = Menu(self)
        self.sheet_options = Menu(self.canvas_menu)
        mode_options = Menu(self.canvas_menu)
        self.canvas_menu.add_command(label = 'Export as PostScript image', command = self.save_snapshot)
        self.canvas_menu.add_cascade(label = 'Select Mode', menu = mode_options)
        mode_options.add_command(label = 'Video', command = lambda: self.set_display_mode('video'))
        mode_options.add_command(label = 'Normal', command = lambda: self.set_display_mode('normal'))
        mode_options.add_command(label = 'Printing', command = lambda: 
            self.set_display_mode('printing'))
        self.canvas_menu.add_cascade(label = 'Sheet options', menu = self.sheet_options, underline = 0)
        self.sheet_options.add_command(label = 'Toggle Density Grid', command = 
            self.toggle_object_density)
        self.sheet_options.add_command(label = 'Toggle Activity', command = self.toggle_object_activity)

        # bind key_press events in canvas.
        self.bind('<KeyPress>', self.key_press)
        # bind the possible left button events to the canvas.
        self.bind('<Button-1>', self.left_click)
        self.bind('<B1-Motion>', self.left_click_drag)
        self.bind('<Double-1>', self.left_double_click)
        self.bind('<ButtonRelease-1>', self.left_release)
        # bind the possible right button events to the canvas.
        self.bind('<Button-3>', self.right_click)
        # because right-click opens menu, a release event can only be flagged by the menu.
        self.item_menu.bind('<ButtonRelease-3>', self.right_release)   

        # add scroll bar; horizontal and vertical
        self.config(scrollregion = (0, 0, 1200, 1200))
        vertical_scrollbar = Scrollbar(root)
        horizontal_scrollbar = Scrollbar(root, orient = 'horizontal')
        vertical_scrollbar.config(command = self.yview)
        horizontal_scrollbar.config(command = self.xview)
        self.config(yscrollcommand=vertical_scrollbar.set)
        self.config(xscrollcommand=horizontal_scrollbar.set)
        vertical_scrollbar.pack(side = RIGHT, fill = Y)
        horizontal_scrollbar.pack(side = BOTTOM, fill = X)
    
    def key_press(self, event):
        "What happens when a key is pressed."
        self.change_mode(event.char)


    #   Left mouse button event handlers
        
    def left_click(self, event):
        "What is to happen if the left button is pressed."
        
        x,y = self.canvasx(event.x), self.canvasy(event.y)
        {"ARROW" : self.init_move,	     # case Arrow mode
         "MAKE" : self.none,		     # case Make mode
         "CONNECTION" : self.init_connection # case Connection mode.
        }[self.mode](x,y)                    # select function depending on mode
    
    def left_click_drag(self, event):
        "What is to happen if the mouse is dragged while the left button is pressed."
        
        x,y = self.canvasx(event.x), self.canvasy(event.y)
        {"ARROW" : self.update_move,              # case Arrow mode
         "MAKE" : self.none,		       # case Make mode
         "CONNECTION" : self.update_connection # case Connection mode.
        }[self.mode](x,y)                      # select function depending on mode
        
    def left_release(self, event):
        "What is to happen when the left mouse button is released."
        
        x,y = self.canvasx(event.x), self.canvasy(event.y)
        {"ARROW" : self.end_move,            # case Arrow mode
         "MAKE" : self.create_object,	     # case Make mode
         "CONNECTION" : self.end_connection  # case Connection mode.
        }[self.mode](x,y)                    # select function depending on mode

    def left_double_click(self, event):
        """
        What is to happen if the left button is double clicked.
	The same for all modes - show the properties for the clicked item.
        Gets object or connection at this point and gives it the focus.
        """
        focus = self.get_xy(event.x, event.y) 
        if (focus != None):
            focus.set_focus(True)
        # show the object or connection's properties.
        self.show_properties(focus)         

    
    #   Right mouse button event handlers

    def right_click(self, event):
        "What is to happen if the right button is pressed."
        self.show_hang_list(event)

    def right_release(self, event):
        "What is to happen when the right mouse button is released (bound to the menu)."
        if (self.focus != None) : # remove focus.
            self.focus.set_focus(False)


    #   Mode Methods
    
    def change_mode(self, char):
        "Changes the mode of the canvas, i.e., what mouse events will do."
        
        if not char in ('c', 'm', 'a') : return
        # remove the focus from the previous toolbar item
        {"ARROW" : self.arrow_tool.set_focus,     # arrow toolbar item
         "MAKE" : self.object_tool.set_focus,	     # object toolbar item
         "CONNECTION" : self.connection_tool.set_focus # connection toolbar item
        }[self.mode](False)                  # select function depending on mode

        # determine the new mode and corresponding toolbar item.
        if (char == 'c'):
            mode = "CONNECTION"
            bar = self.connection_tool
        elif (char == 'm'):
            mode = "MAKE" 
            bar = self.object_tool
        elif (char == 'a'):
            mode = "ARROW"
            bar = self.arrow_tool
        # set the focus of the toolbar item of the new mode and retain the note the new mode.
        bar.set_focus(True)
        self.mode = mode


    #   Panel methods
    
    def refresh(self):
        for obj in self.object_list:
            obj.set_focus(True)
            obj.set_focus(False)
        for obj in self.object_list:
            connection_list = obj.from_connections[:]
            connection_list.reverse()
            for con in connection_list:
                con.move()

    def enlarge_scale(self):
        self.scaling_factor += 0.2
        self.refresh()
 
    def reduce_scale(self):
        if self.scaling_factor <= 0.4 : return
        self.scaling_factor -= 0.2
        self.refresh()

    def toggle_auto_refresh(self):
        self.auto_refresh = not self.auto_refresh
        if self.auto_refresh:
            self.console.auto_refresh_panels.append(self)
        else:
            self.console.auto_refresh_panels.remove(self)

    def toggle_normalize(self):
        EditorNode.normalize = not EditorNode.normalize
        self.refresh()



    #   Object moving methods
    #
    # If an object is left clicked in the canvas, these methods allow
    # it to be repositioned in the canvas.

    def init_move(self, x, y):
        "Determine if click was on an object."
        
        self.current_object = self.get_object_xy(x, y)
        if (self.current_object != None) : 
            # if it was, give it the focus
            self.current_object.set_focus(True)

    def update_move(self, x, y):
        "If dragging an object, refresh its position"
        
        if (self.current_object != None):
            self.current_object.move(x, y)

    def end_move(self, x, y):
        "If dropping an object, remove focus and refresh."
        
        if (self.current_object != None):
            self.current_object.set_focus(False)
            self.current_object.move(x, y)
        # redraw all the objects in the canavas and dereference
        self.redraw_objects()
        self.current_object = None

    #   Connection methods
    #
    # these methods allow a connection to be made between two objects in the canvas

    def init_connection(self, x, y):
        "Determine if click was on an object, and retain if so."
        
        current_object = self.get_object_xy(x, y)
        if (current_object == None) : # if not change to ARROW mode
            self.change_mode('a')
        else :  # if on an object, create a connection and give it the focus
            self.current_connection = self.connection_tool.new_cover(current_object)
            self.current_connection.set_focus(True)

    def update_connection(self, x, y):
        "Update connection's position."
       	self.current_connection.update_position((x, y))
        
    def end_connection(self, x, y):
        "Determine if the connection has been dropped on an object."
        
        obj = self.get_object_xy(x, y)
        if (obj != None) : # if an object, connect the objects and remove focus
            if (self.current_connection != None):
                connected = self.connection_tool.create_connection(self.current_connection, obj)
                if connected:
                    self.current_connection.set_focus(False)
        else : # if not an object, remove the connection
            connected=False
            if (self.current_connection != None):
                self.current_connection.remove()
        if connected:
            self.redraw_objects()
        # dereference
        self.current_connection = None

    def get_connection_xy(self, x, y):
        "Return connection at given x, y (None if no connection)."
        
        for obj in self.object_list:
            connection_list = obj.from_connections[:]
            connection_list.reverse()
            for con in connection_list:
                if (con.in_bounds(x, y)):
                    return con
        return None

    #   Object Methods

    def create_object(self, x, y) : 
        "Create a new object."
        self.add_object(self.object_tool.create_node(x, y))

    def add_object(self, obj) : 
        "Add a new object to the Canvas."
        
        self.object_list = [obj] + self.object_list

    def add_object_to_back(self, obj) : 
        "Add a new object to the Canvas at back of the list."
        
        self.object_list =  self.object_list + [obj]

    def remove_object(self, obj) : 
        "Remove an object from the canvas."
        
        for i in range(len(self.object_list)) : 
            if (obj == self.object_list[i]) : break
        else : return # object was not found
        del self.object_list[i]
        return i

    def toggle_object_density(self):
        if EditorNode.show_density:
            EditorNode.show_density = False
        else:
            EditorNode.show_density = True
        self.refresh() 

    def toggle_object_activity(self):
        if EditorNode.show_activity:
            EditorNode.show_activity = False
            view = 'normal'
        else:
            EditorNode.show_activity = True
            view = 'activity'
        for obj in self.object_list:
            obj.select_view(view)
        self.refresh()

    def get_object_xy(self, x, y) : 
        "Return object at given x, y (or None if no object)."
        
        # search through the bounds of each object in the canvas. 
        # returns the first (nearest to front) object, None if no object at x,y
        for obj in self.object_list:
            if (obj.in_bounds(x, y)):
                break
        else : return None
        return obj


    def show_properties(self, focus):
        "Show properties of an object or connection, and remove the focus."
        
        if (focus != None):
            focus.show_properties()
            focus.set_focus(False)
        
    def delete_focus(self, focus):
        "Tell a connection or object to delete itself."
        
        if (focus == None) : 
            pass
        else:
            focus.remove()
            self.redraw_objects()

    #   Object Order Methods
    #
    # These methods ensure the ordering in the canvas window is held
    # and allows manipulation of the order.

    def redraw_objects(self, index = None):
        """
        Redraw all the objects in the canvas.

        If non-None, the index specifies that only the objects below
        that index need drawing.
        """

        if (index == None or index < 0) : index = len(self.object_list)
        for i in range(index ,0, -1):
            self.object_list[i-1].draw()
    
    def move_to_front(self, obj):
        index = self.remove_object(obj)
        self.add_object(obj)
        self.redraw_objects(index)

    def move_forward(self, obj):
        for i in range(len(self.object_list)) : # find object index in list
            if (obj == self.object_list[i]) : break
        else : return # object was not found
        # swap this object for the one higher in the canvas and redraw
        a = self.object_list[(i-1) : (i+1)]
        a.reverse()
        self.object_list[(i-1):(i+1)] = a
        self.redraw_objects(i+1)

    def move_to_back(self, obj):
        self.remove_object(obj)
        self.add_object_to_back(obj)
        self.redraw_objects()

    #   Hang List Methods
    #
    # If there is an object or connection at the right clicked point,
    # a popup menu is displayed, allowing for modifications to the
    # particular obj/con.

    def show_hang_list(self, event):

        # change to ARROW mode and get x, y mouse coords
        self.change_mode('a')
        x, y = self.canvasx(event.x), self.canvasy(event.y)
        # get connection at this point
        focus = self.get_connection_xy(x, y)
        for i in range(self.MAX_VIEWS) : # max number of views
            self.view.delete(END)
        if (focus == None):
            # if no connection, checks bounds of objects
            focus = self.get_object_xy(x, y)
            # fill in menu items that are just for objects
            for i in self.object_indices:
                self.item_menu.entryconfig(i, foreground = 'Black', activeforeground = 'Black')
        else:
            # gray out menu items that are just for objects
            for i in self.object_indices:
                self.item_menu.entryconfig(i,foreground = 'Gray', activeforeground = 'Gray')
        if (focus != None):
            for (label, function) in focus.get_viewing_choices():
                self.view.add_command(label = label, command = function)
            # give the connection or object the focus
            focus.set_focus(True)
            self.focus = focus
            # create the popup menu at current mouse coord
            self.item_menu.tk_popup(event.x_root, event.y_root)
        else:
            self.canvas_menu.tk_popup(event.x_root, event.y_root)
        
    #   Utility methods

    def save_snapshot(self):
        POSTSCRIPT_FILETYPES = [('Encapsulated PostScript images','*.eps'),
                                ('PostScript images','*.ps'),('All files','*')]
        snapshot_name = asksaveasfilename(filetypes=POSTSCRIPT_FILETYPES)
        if snapshot_name:
            self.postscript(file=snapshot_name)

    def set_display_mode(self, mode):
        self.display_mode = mode
        for obj in self.object_list:
            obj.set_mode(mode)

    def set_tool_bars(self, arrow_tool, connection_tool, object_tool):
        # reference to the toolbar items, a tool is notified when the canvas is changed
        # to the mode corresponding to it.
        self.arrow_tool = arrow_tool
        # connection tool supplies 'connection' objects that can draw themselves in the canvas
        self.connection_tool = connection_tool
        # object tool supplies 'object' objects that can draw themselves in the canvas
        self.object_tool = object_tool
        # initialise mode
        self.change_mode('a')

    # does nothing
    def none(self, x, y) : pass

    def get_xy(self, x, y):
        "Returns the connection or object at this x, y position or None if there is not one."
        
        # check for a connection
        focus = self.get_connection_xy(x, y)
        if (focus == None):
            # if no connection, check bounds of objects
            focus = self.get_object_xy(x, y)
        return focus # return the first found or None





class ModelEditor:
    """
    This class constructs the main editor window. It uses a instance
    of GUICanvas as the main editing canvas and inserts the
    three-option toolbar in a Frame along the left side of the window.
    """

    def __init__(self):
        
        # create editor window and set title
        root = Tk()
        root.title("Model Editor")
        # create a GUICanvas and place it in a frame
        canvas_frame = Frame(root, bg = 'white')
        canvas = EditorCanvas(canvas_frame)

        # create the three toolbar items and place them into a frame
        frame = Frame(root, bg = 'light grey', bd = 2)
        parameters_tool = ParametersTool(frame)
        arrow_tool = ArrowTool(canvas, frame, parameters_tool) # movement arrow toolbar item
        object_tool = NodeTool(canvas, frame, parameters_tool) # object creation toolbar item
        connection_tool = ConnectionTool(canvas, frame, parameters_tool) # connection toolbar item
        parameters_tool.pack(side = TOP)
        frame.pack(side = LEFT, fill = Y) # pack the toolbar on the left
        canvas.pack(fill = BOTH, expand = YES) # pack the canvas and allow it to be expanded
        canvas_frame.pack(fill = BOTH, expand = YES) # pack the canvas frame into the window; expandable
        # give the canvas a reference to the toolbars
        canvas.set_tool_bars(arrow_tool, connection_tool, object_tool) 

        # give the canvas focus and import any objects and connections already in the simulation
        canvas.focus_set()
        self.canvas = canvas
        self.import_model()

    def import_model(self):
        
        # random generator, and values used for randomly positioning sheets
        random_generator = Random() 
        padding = 75; spread_extent = 500
        # get a list of all the sheets in the simulation
        sim = self.canvas.simulation
        node_dictionary = sim.objects(Sheet)
        node_list = node_dictionary.values()

        # create the editor covers for the nodes
        for node in node_list:
            # if the sheet has x,y coords, use them
            dictionary_entries = node.__dict__.keys()
            ### JABALERT: Should probably change these to layout_x and layout_y, 
            ### because they are about how the sheets are laid out in a visualization,
            ### even if that layout is just generated as an image and saved to disk
            ### rather than in a gui.
            if (('gui_x' in dictionary_entries) and ('gui_y' in dictionary_entries)):
                x, y = node.gui_x, node.gui_y
            # if not generate random coords
            else:
                x = padding + random_generator.random() * spread_extent 
                y = padding + random_generator.random() * spread_extent
            editor_node = EditorSheet(self.canvas, node, (x, y), node.name)
            self.canvas.add_object(editor_node)

        # create the editor covers for the connections
        
        for editor_node in self.canvas.object_list:
            node = editor_node.sheet
            for con in node.out_connections:
                # create cover for a projection
                editor_connection = EditorProjection("", self.canvas, editor_node)
                # find the EditorNode that the proj connects to
                for dest_editor_node in self.canvas.object_list:
                    if (dest_editor_node.sheet == con.dest):
                        dest = dest_editor_node
                        break
                else:
                    # JABALERT: Should eliminate all print statements.
                    print "Incomplete connection: ", con
                    break
                # connect the connection to the destination node
                editor_connection.connect(dest, con)
        self.canvas.redraw_objects()
