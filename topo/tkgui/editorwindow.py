"""
Toolbar and canvas for the model editor GUI.

Originally written by Alan Lindsay.
$Id$
"""
__version__='$Revision$'


# Alan Lindsay
# Binding Mouse Action

from Tkinter import *
from editortools import ArrowToolbar, ObjectToolbar, ConToolbar
from topo.base.simulator import get_active_sim

""" TopoGUICanvas extends the Tk Canvas class.
    There are 3 modes that determine the effect of mouse events in the Canvas
    A Canvas can accept new objects, move objects and make connections 
    between them. The intended use of this class is as the main
    canvas in a Topographica model-editing GUI. """

class GUICanvas(Canvas) :

    ############ Constructor ####################################

    def __init__(self, root = None, width = 600, height = 600) :
        # Superclass call
        Canvas.__init__(self, root, width = width, height = height, bg = "white", bd = 2, relief = SUNKEN)
	# give focus (mainly to listen for key presses)
	self.focus_set()
	self.curObj = None
	self.curCon = None
	self.focus = None
	# list holding references to all the objects in the canvas	
	self.objectList = []
	# create the menu widget used as a popup on objects and connections
	self.option_add("*Menu.tearOff", "0") 
	self.menu = Menu(self)
	# add proporty and delete entries in the menu.
	self.menu.insert_command(END, label = 'Properties', command = lambda: self.showProperties(self.focus))
	self.menu.insert_command(END, label = 'Delete', command = lambda: self.deleteXY(self.focus))
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
        # set the initial mode.
	self.mode = None
	self.simulator = self.getSim() # get the topo simulator
	print self.simulator

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
         }[self.mode](x,y)             # select function depending on mode.
    
    def leftClickDrag(self, event) :
        # what is to happen if the mouse is dragged while the left button
        # is pressed.
	x,y = self.canvasx(event.x), self.canvasy(event.y)
        {"ARROW" : self.updtMove,        # case Arrow mode
	 "MAKE" : self.none,		 # case Make mode
         "CONNECTION" : self.updtConnect # case Connection mode.
         }[self.mode](x,y)             # select function depending on mode
        
    def leftRelease(self, event) :
        # what is to happen when the left mouse button is released.
	x,y = self.canvasx(event.x), self.canvasy(event.y)
        {"ARROW" : self.endMove,         # case Arrow mode
	 "MAKE" : self.createObject,	 # case Make mode
         "CONNECTION" : self.endConnect  # case Connection mode.
         }[self.mode](x,y)             # select function depending on mode

    def leftDoubleClick(self, event) :
        # what is to happen if the left button is double clicked.
	# the same for all modes - show the properties for the clicked item
	focus = self.getXY(event.x, event.y) # gets object or connection at this point
	if (focus != None) :
		focus.setFocus(True) # give focus
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
	if (self.mode == "CONNECTION") :
		self.conbar.setFocus(False)
	elif (self.mode == "MAKE") :
		self.objbar.setFocus(False)
	else :
		self.arrbar.setFocus(False)
	if (char == 'c') :
        	self.mode = "CONNECTION"
		self.conbar.setFocus(True)
	elif (char == 'm') :
		self.mode = "MAKE"
		self.objbar.setFocus(True)
	elif (char == 'a') :
		self.mode = "ARROW"
		self.arrbar.setFocus(True)

    ########### Object moving methods #################################

    def initMove(self, x, y) :
	# determine if click was on an object and retain it.
	self.curObj = self.getObjectXY(x, y)
	if (self.curObj != None) : # if it was, give it the focus
		self.curObj.setFocus(True)

    def updtMove(self, x, y) :
	# if dragging an object, refresh it's position
	if (self.curObj != None) :
	    self.curObj.move(x, y)

    def endMove(self, x, y) :
        # if dropped an object, remove focus and refresh; dereference
	if (self.curObj != None) :
		self.curObj.setFocus(False)
		self.curObj.move(x, y)
	self.curObj = None

    ############ Connection methods ########################

    def initConnect(self, x, y) :
        # determine if click was on an object and retain
	curObj = self.getObjectXY(x, y)
	if (curObj == None) : # if not change to ARROW mode
		self.changeMode('a')
	else :  # if it is, create a GUIProjection and give it the focus
		self.curCon = self.conbar.newCover(curObj)
		self.curCon.setFocus(True)

    def updtConnect(self, x, y) :
        # update GUIConnection TO pos 
       	self.curCon.updtPos((x, y))
        
    def endConnect(self, x, y) :
	# determine if the connection has been dropped on an object
	obj = self.getObjectXY(x, y)
	if (obj != None) : # if it has - connect the objects and remove focus
		if (self.curCon != None) :
			self.conbar.createConnection(self.curCon, obj)
			self.curCon.setFocus(False)
	else : # if not remove the connection
		if (self.curCon != None) :
			self.curCon.remove()
	self.curCon = None

    ########### Object Methods ######################################

    def createObject(self, x, y) : # create a new object
	self.addObject(self.objbar.createObject(x, y))

    def addObject(self, obj) : # add a new object to the Canvas
	self.objectList = self.objectList + [obj]

    def removeObject(self, obj) : # remove an object from the canvas
	for i in range(len(self.objectList)) : # find object index in list
		if (obj == self.objectList[i]) : break
	else : return # object was not found
	del self.objectList[i] # delete object from list

    def getObjectXY(self, x, y) : # return object at given x, y (None if no object)
	for obj in self.objectList :
		if (obj.inBounds(x, y)) :
			return obj
	return None

    ########### Connection Methods #################################

    def getConXY(self, x, y) :
	for obj in self.objectList : # return connection at given x, y (None if no connection)
		for con in obj.fromCon :
			if (con.inBounds(x, y)) :
				return con
	return None

    ########### Properties Method ##################################

    def showProperties(self, focus) :
        # <auto> remove right click hang list
	print("Properties of ", focus)
	if (focus != None) :
		focus.setFocus(False)
	# create window with ParameterFrame(focus) included
        
    ########### Delete GUI Object Method ###########################

    def deleteXY(self, focus) :
	if (focus == None) : 
		pass
	else :
		focus.remove()

    ########### Hang List Methods ##################################

    def showHangList(self, event) :
        self.changeMode('a') # change to ARROW mode
	# gets object or connection at this point
	focus = self.getXY(self.canvasx(event.x), self.canvasy(event.y)) 
	if (focus != None) :
		focus.setFocus(True) # give it the focus
	self.focus = focus
	# create the popup menu at current mouse coord
	self.menu.tk_popup(event.x_root, event.y_root)
        
    ############## Util ############################################

    def setToolBars(self, arrbar, conbar, objbar) :
	# reference objects with methods allowing adding and removing objects 
	# and connections for the canvas
	self.arrbar = arrbar
	self.conbar = conbar
	self.objbar = objbar
	# initialise mode
	self.changeMode('a')

    # does nothing
    def none(self, x, y) : pass

    def getXY(self, x, y) :
    # returns the connection or object at this x, y position or None if there
    # is not one. Checks for a connection first and returns first found.
	focus = self.getConXY(x, y) # checks bounds of connections
	if (focus == None) :
		# checks bounds of objects
    		focus = self.getObjectXY(x, y)
	return focus # returns the first found

    def getSim(self) :
	sim = get_active_sim()
	if (sim == None) :
		from topo.base.simulator import Simulator, set_active_sim
		sim = Simulator()
		set_active_sim(sim)
	return sim


####################################################################

"""
This class constructs the main editor window. It uses a instance of GUICanvas as the main
editing canvas and inserts the three-option toolbar in a Frame along the left side of the
window. 
"""
class ModelEditor :
    def __init__(self):
	# editor window
	root = Tk()
	root.title("Model Editor") # set title bar
	
	# create a GUICanvas and place it in a frame
	canvFrame = Frame(root, bg = 'white')
	canvas = GUICanvas(canvFrame)

	# create the three toolbar items and place them into a frame
	frame = Frame(root, bg = 'light grey')
	arrbar = ArrowToolbar(canvas, frame) # movement arrow toolbar item
	objbar = ObjectToolbar(canvas, frame) # object creation toolbar item
	conbar = ConToolbar(canvas, frame) # connection toolbar item
	frame.pack(side = LEFT, fill = BOTH) # pack the toolbar on the left
	canvas.pack(fill = BOTH, expand = YES) # pack the canvas and allow it to be expanded
	canvFrame.pack(fill = BOTH, expand = YES) # pack the canvas frame into the window; expandable
	canvas.setToolBars(arrbar, conbar, objbar) # give the canvas a reference to the toolbars
	
	# start the main loop.
	mainloop()
