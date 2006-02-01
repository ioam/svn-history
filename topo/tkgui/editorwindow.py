"""
Window and canvas for the model editor GUI.

Originally written by Alan Lindsay.
$Id$
"""
__version__='$Revision$'

from Tkinter import Canvas, Frame, Tk, Menu, Scrollbar, SUNKEN, YES, BOTH, LEFT, END, RIGHT, BOTTOM, X, Y
from editortools import ArrowTool, NodeTool, ConTool
from topo.base.simulator import get_active_sim, set_active_sim, Simulator
from topo.base.sheet import Sheet
from topo.base.projection import Projection
from editorobjects import EditorSheet, EditorProjection
from random import Random, random

class EditorCanvas(Canvas) :

    """ 
    EditorCanvas extends the Tk Canvas class.
    There are 3 modes that determine the effect of mouse events in the Canvas
    A Canvas can accept new objects, move objects and make connections 
    between them. The intended use of this class is as the main
    canvas in a Topographica model-editing GUI. 
    """

    ############ Constructor ####################################
    def __init__(self, root = None, width = 600, height = 600) :
        # Superclass call
        Canvas.__init__(self, root, width = width, height = height, bg = "white", bd = 2, relief = SUNKEN)
        # retain the current focus in the canvas
        self.curObj = None
        self.curCon = None
        self.focus = None
        # list holding references to all the objects in the canvas	
        self.objectList = []
        # set the initial mode.
        self.mode = "ARROW"
        # get the topo simulator
        self.simulator = self.getSim()
        print self.simulator

        # create the menu widget used as a popup on objects and connections
        self.option_add("*Menu.tearOff", "0") 
        self.menu = Menu(self)
        # add property, toggle activity drawn on sheets, object draw ordering and delete entries to the menu.
        self.menu.insert_command(END, label = 'Properties', command = lambda: self.showProperties(self.focus))
        self.menu.insert_command(END, label = 'Show Activity',command = lambda: self.showActivity(self.focus))
        self.menu.insert_command(END, label = 'Move Forward', command = lambda: self.moveForward(self.focus))
        self.menu.insert_command(END, label = 'Move to Front', command = lambda: self.moveToFront(self.focus))
        self.menu.insert_command(END, label = 'Move to Back', command = lambda: self.moveToBack(self.focus))
        self.menu.insert_command(END, label = 'Delete', command = lambda: self.deleteXY(self.focus))
        # the indexes of the menu items that are for objects only
        self.objInds = [1,2,3,4]

        # bind keyPress events in canvas.
        self.bind('<KeyPress>', self.keyPress)
        # bind the possible left button events to the canvas.
        self.bind('<Button-1>', self.leftClick)
        self.bind('<B1-Motion>', self.leftClickDrag)
        self.bind('<Double-1>', self.leftDoubleClick)
        self.bind('<ButtonRelease-1>', self.leftRelease)
        # bind the possible right button events to the canvas.
        self.bind('<Button-3>', self.rightClick)
        # because right-click opens menu, a release event can only be flagged by the menu.
        self.menu.bind('<ButtonRelease-3>', self.rightRelease)   

        # add scroll bar; horizontal and vertical
        self.config(scrollregion = (0, 0, 1200, 1200))
        sbar = Scrollbar(root)
        sbarx = Scrollbar(root, orient = 'horizontal')
        sbar.config(command = self.yview)
        sbarx.config(command = self.xview)
        self.config(yscrollcommand=sbar.set)
        self.config(xscrollcommand=sbarx.set)
        sbar.pack(side = RIGHT, fill = Y)
        sbarx.pack(side = BOTTOM, fill = X)
    
    ############ Keypress event handlers ############################

    def keyPress(self, event) :
        # what happens when a key is pressed.
        self.changeMode(event.char)

    ############ Left mouse button event handlers ###################
        
    def leftClick(self, event) :
        # what is to happen if the left button is pressed.
        x,y = self.canvasx(event.x), self.canvasy(event.y)
        {"ARROW" : self.initMove,	 # case Arrow mode
         "MAKE" : self.none,		 # case Make mode
         "CONNECTION" : self.initConnect # case Connection mode.
        }[self.mode](x,y)                # select function depending on mode
    
    def leftClickDrag(self, event) :
        # what is to happen if the mouse is dragged while the left button
        # is pressed.
        x,y = self.canvasx(event.x), self.canvasy(event.y)
        {"ARROW" : self.updtMove,        # case Arrow mode
         "MAKE" : self.none,		 # case Make mode
         "CONNECTION" : self.updtConnect # case Connection mode.
        }[self.mode](x,y)                # select function depending on mode
        
    def leftRelease(self, event) :
        # what is to happen when the left mouse button is released.
        x,y = self.canvasx(event.x), self.canvasy(event.y)
        {"ARROW" : self.endMove,         # case Arrow mode
         "MAKE" : self.createObject,	 # case Make mode
         "CONNECTION" : self.endConnect  # case Connection mode.
        }[self.mode](x,y)                # select function depending on mode

    def leftDoubleClick(self, event) :
        # what is to happen if the left button is double clicked.
	# the same for all modes - show the properties for the clicked item
        # gets object or connection at this point and give it the focus
        focus = self.getXY(event.x, event.y) 
        if (focus != None) :
            focus.setFocus(True)
        # show the object or connection's properties.
        self.showProperties(focus)         
    
    ############ Right mouse button event handlers #################

    def rightClick(self, event) :
        # what is to happen if the right button is pressed.
        self.showHangList(event)

    def rightRelease(self, event) :
        # what is to happen when the right mouse button is released (bound to the menu).
        if (self.focus != None) : # remove focus.
            self.focus.setFocus(False)

    ########### Mode Methods #######################################
    
    def changeMode(self, char) :
        # changes the mode of the canvas. This will change the effect of mouse events in 
        # the canvas.
        if not char in ('c', 'm', 'a') : return
        # remove the focus from the previous toolbar item
        {"ARROW" : self.arrbar.setFocus,     # arrow toolbar item
         "MAKE" : self.objbar.setFocus,	     # object toolbar item
         "CONNECTION" : self.conbar.setFocus # connection toolbar item
        }[self.mode](False)                  # select function depending on mode

        # determine the new mode and corresponding toolbar item.
        if (char == 'c') :
            mode = "CONNECTION"
            bar = self.conbar
        elif (char == 'm') :
            mode = "MAKE" 
            bar = self.objbar
        elif (char == 'a') :
            mode = "ARROW"
            bar = self.arrbar
        # set the focus of the toolbar item of the new mode and retain the note the new mode.
        bar.setFocus(True)
        self.mode = mode

    ########### Object moving methods #################################
    # if an object is left clicked in the canvas, these methods allow it to be repositioned in
    # the canvas.

    def initMove(self, x, y) :
        # determine if click was on an object.
        self.curObj = self.getObjectXY(x, y)
        if (self.curObj != None) : 
            # if it was, give it the focus
            self.curObj.setFocus(True)

    def updtMove(self, x, y) :
        # if dragging an object, refresh it's position
        if (self.curObj != None) :
            self.curObj.move(x, y)

    def endMove(self, x, y) :
        # if dropping an object, remove focus and refresh.
        if (self.curObj != None) :
            self.curObj.setFocus(False)
            self.curObj.move(x, y)
        # redraw all the objects in the canavas and dereference
        self.redrawObjects()
        self.curObj = None

    ############ Connection methods ########################
    # these methods allow a connection to be made between two objects in the canvas

    def initConnect(self, x, y) :
        # determine if click was on an object and retain
        curObj = self.getObjectXY(x, y)
        if (curObj == None) : # if not change to ARROW mode
            self.changeMode('a')
        else :  # if on an object, create a connection and give it the focus
            self.curCon = self.conbar.newCover(curObj)
            self.curCon.setFocus(True)

    def updtConnect(self, x, y) :
        # update connection's pos 
       	self.curCon.updtPos((x, y))
        
    def endConnect(self, x, y) :
        # determine if the connection has been dropped on an object
        obj = self.getObjectXY(x, y)
        if (obj != None) : # if an object, connect the objects and remove focus
            if (self.curCon != None) :
                self.conbar.createConnection(self.curCon, obj)
                self.curCon.setFocus(False)
        else : # if not an object, remove the connection
            if (self.curCon != None) :
                self.curCon.remove()
        # dereference
        self.curCon = None

    ########### Object Methods ######################################

    def createObject(self, x, y) : 
        # create a new object
        self.addObject(self.objbar.createNode(x, y))

    def addObject(self, obj) : 
        # add a new object to the Canvas
        self.objectList = [obj] + self.objectList

    def addObjectToBack(self, obj) : 
        # add a new object to the Canvas at back of the list
        self.objectList =  self.objectList + [obj]

    def removeObject(self, obj) : 
        # remove an object from the canvas
        # find object index in list
        for i in range(len(self.objectList)) : 
            if (obj == self.objectList[i]) : break
        else : return # object was not found
        # delete index from list
        del self.objectList[i]
        return i

    def showActivity(self, focus) : 
        # toggle whether the activity of an object is plotted
        focus.showActivity()

    def getObjectXY(self, x, y) : 
        # return object at given x, y (None if no object)
        # search through the bounds of each object in the canvas returns the first
        # (nearest to front) object, None if no object at x,y
        for obj in self.objectList :
            if (obj.inBounds(x, y)) :
                break
        else : return None
        return obj

    ########### Connection Methods #################################

    def getConXY(self, x, y) :
        # return connection at given x, y (None if no connection)
        for obj in self.objectList :
            conList = obj.fromCon[:]
            conList.reverse()
            for con in conList :
                if (con.inBounds(x, y)) :
                    return con
        return None

    ########### Properties Method ##################################

    def showProperties(self, focus) :
        # show properties of an object or connection and remove the focus
        if (focus != None) :
            focus.showProperties()
            focus.setFocus(False)
        
    ########### Delete GUI Object Method ###########################

    def deleteXY(self, focus) :
        # tell a connection or object to delete itself
        if (focus == None) : 
		pass
        else :
		focus.remove()

    ########### Object Order Methods ###############################
    # these methods ensure the ordering in the canvas window is held and 
    # allows manipulation of the order.    

    def redrawObjects(self, index = None) :
        # redraw all the objects in the canvas, index specifies that only
        # the objects below a certain index need drawn
        if (index == None or index < 0) : index = len(self.objectList)
        for i in range(index ,0, -1) :
            self.objectList[i-1].draw()
    
    def moveToFront(self, obj) :
        # remove the object from the canvas list
        index = self.removeObject(obj)
        # add it to the front and redraw the necessary objects
        self.addObject(obj)
        self.redrawObjects(index)

    def moveForward(self, obj) :
        for i in range(len(self.objectList)) : # find object index in list
            if (obj == self.objectList[i]) : break
        else : return # object was not found
        # swap this object for the one higher in the canvas and redraw
        a = self.objectList[(i-1) : (i+1)]
        a.reverse()
        self.objectList[(i-1):(i+1)] = a
        self.redrawObjects(i+1)

    def moveToBack(self, obj) :
        # remove the object from the canvas list
        self.removeObject(obj)
        # add it to the back and redraw all
        self.addObjectToBack(obj)
        self.redrawObjects()

    ########### Hang List Methods ##################################
    # if there is an object or connection at the right clicked point, a popup menu
    # is displayed, allowing for modificaitions to the particular obj/con

    def showHangList(self, event) :
        # change to ARROW mode and get x, y mouse coords
        self.changeMode('a')
        x, y = self.canvasx(event.x), self.canvasy(event.y)
        # get connection at this point
        focus = self.getConXY(x, y)
        if (focus == None) :
            # if no connection, checks bounds of objects
            focus = self.getObjectXY(x, y)
            # fill in menu items that are just for objects
            for i in self.objInds :
                self.menu.entryconfig(i, foreground = 'Black', activeforeground = 'Black')
        else :
            # gray out menu items that are just for objects
            for i in self.objInds :
                self.menu.entryconfig(i,foreground = 'Gray', activeforeground = 'Gray')
        if (focus != None) :
            # give the connection or object the focus
            focus.setFocus(True)
            self.focus = focus
            # create the popup menu at current mouse coord
            self.menu.tk_popup(event.x_root, event.y_root)
        
    ############## Util ############################################

    def setToolBars(self, arrbar, conbar, objbar) :
        # reference to the toolbar items, a tool is notified when the canvas is changed
        # to the mode corresponding to it.
        self.arrbar = arrbar
        # connection tool supplies 'connection' objects that can draw themselves in the canvas
        self.conbar = conbar
        # object tool supplies 'object' objects that can draw themselves in the canvas
        self.objbar = objbar
        # initialise mode
        self.changeMode('a')

    # does nothing
    def none(self, x, y) : pass

    def getXY(self, x, y) :
        # returns the connection or object at this x, y position or None if there
        # is not one.
        # check for a connection
        focus = self.getConXY(x, y)
        if (focus == None) :
            # if no connection, check bounds of objects
            focus = self.getObjectXY(x, y)
        return focus # return the first found or None

    def getSim(self) :
        # get the active Topographica simulator
        sim = get_active_sim()
        # if there is not one, create one and register it for other processes
        if (sim == None) :
            sim = Simulator()
            set_active_sim(sim)
        return sim



####################################################################

class ModelEditor :
    """
    This class constructs the main editor window. It uses a instance of GUICanvas as the main
    editing canvas and inserts the three-option toolbar in a Frame along the left side of the
    window. 
    """

    def __init__(self):
        # create editor window and set title
        root = Tk()
        root.title("Model Editor")
        # create a GUICanvas and place it in a frame
        canvFrame = Frame(root, bg = 'white')
        canvas = EditorCanvas(canvFrame)

        # create the three toolbar items and place them into a frame
        frame = Frame(root, bg = 'light grey')
        arrbar = ArrowTool(canvas, frame) # movement arrow toolbar item
        objbar = NodeTool(canvas, frame) # object creation toolbar item
        conbar = ConTool(canvas, frame) # connection toolbar item
        frame.pack(side = LEFT, fill = BOTH) # pack the toolbar on the left
        canvas.pack(fill = BOTH, expand = YES) # pack the canvas and allow it to be expanded
        canvFrame.pack(fill = BOTH, expand = YES) # pack the canvas frame into the window; expandable
        canvas.setToolBars(arrbar, conbar, objbar) # give the canvas a reference to the toolbars

        # give the canvas focus and import any objects and connections already in the simulator
        canvas.focus_set()
        self.canvas = canvas
        self.importModel()

    def importModel(self) :
        # random generator, and values used for randomly positioning sheets
        randGen = Random() 
        minDis = 75; maxScale = 500
        # get a list of all the sheets in the simulator
        sim = self.canvas.simulator
        nodeDict = sim.objects(Sheet)
        nodeList = nodeDict.values()

        # create the editor covers for the nodes
        for node in nodeList :
            # if the sheet has x,y coords, use them
            dictEnts = node.__dict__.keys()
            if (('guiX' in dictEnts) and ('guiY' in dictEnts)) :
                x, y = node.guiX, node.guiY
            # if not generate random coords
            else :
                x = minDis + randGen.random() * maxScale 
                y = minDis + randGen.random() * maxScale
            guiNode = EditorSheet(self.canvas, node, (x, y), node.name)
            self.canvas.addObject(guiNode)

        # create the editor covers for the connections
        for guiNode in self.canvas.objectList :
            node = guiNode.sheet
            for conList in node.out_connections.values() :
                for con in conList :
                    # create cover for a projection
                    guiCon = EditorProjection("", self.canvas, guiNode)
                    # find the EditorNode that the proj connects to
                    for guiNDest in self.canvas.objectList :
                        if (guiNDest.sheet == con.dest) :
                            dest = guiNDest
                            break
                    else :
                        print "Incomplete connection : ", con
                        break
                    # connect the connection to the destination node
                    guiCon.connect(dest, con)
        self.canvas.redrawObjects()
