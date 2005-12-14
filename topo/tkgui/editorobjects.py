"""
Objects that can be manipulated by the model editor GUI.

Originally written by Alan Lindsay.
$Id$
"""
__version__='$Revision$'

# JABALERT: Please try to eliminate import *
from Tkinter import *
import Pmw # ALALERT: Is this necessary?

# ALALERT: Should add a base class that unifies GuiObject and
# GuiConnection into one class, probably renaming the existing
# GuiObject to GuiNode and then using GuiObject for the base class.
# Might also want to rename the Gui portion to be more specific,
# i.e., to convey that it's an object in the model editor.


"""
An object to be created and manipulated in a GUICanvas. A GuiObject is used to cover
any topographica sheet, and extending classes will supply a draw method and other
type specific attributes. An instance of this class can have the focus.

"""

class GuiObject :

    FROM = 0
    TO = 1	

    def __init__(self, canvas, pos, name, colour = ('slate blue', 'lavender')) :
	self.drawArea = canvas # retains a reference to the canvas
	self.colours = colour # colours for drawing this object in the canvas
	self.name = name # set the name of the sheet
	self.fromCon = [] # connections from this object
	self.toCon = [] # connections to this object
	self.x = pos[0] # set the x and y coords of the centre of this object
	self.y = pos[1]
	self.loopCount = 0
	self.focus = False # has the focus - false

    ############ Draw methods ############################

    def draw(self) :
	# draw the object at the current x, y position
	pass

    def setFocus(self, focus) : # set focus
	self.focus = focus

    ############ Connection methods ########################

    def attatchCon(self, con, fromTo) : # add the connection to or from this object
	if (fromTo == self.FROM) :
		self.fromCon = self.fromCon + [con]
	else :
		self.toCon = self.toCon + [con]
	
    def removeCon(self, con, fromTo) : # remove a connection to or from this object
	if (fromTo) :
		l = len(self.toCon)
		for i in range(l) :
			if (con == self.toCon[i]) : break
		else : return
		del self.toCon[i]
	else :
		l = len(self.fromCon)
		for i in range(l) :
			if (con == self.fromCon[i]) : break
		else : return
		del self.fromCon[i]

    def getLoopCount(self) :
	return self.loopCount

    def incrementLoopCount(self) :
	self.loopCount += 1

    ############ Update methods ############################ 

    def remove(self) :
	# remove this object from the canvas and remove any connections and deal
	# with relevant Topographica objects.
	pass

    def move(self, x, y) :
	# update position of object and redraw
	pass

    ############ Util methods ##############################

    def inBounds(self, x, y) : 
	# return true, if x,y lies within this gui object's boundary
	pass
    
    def getPos(self) :
	return (self.x, self.y) # return center point of object






####################################################################

"""
Represents any topo sheet. It is a subclass of GuiObject and fills in the
methods that are not defined. It is represented by a Paralellogram in its
Canvas. The colours used for drawing can be set. Uses bounding box to
determine if x,y coord is within its boundary.

"""

class GUISheet(GuiObject) :

    def __init__(self, canvas, sheet, pos, name) :
	# super constructor call
	GuiObject.__init__(self, canvas, pos, name)
	self.sheet = sheet # the topo sheet that this object represents
	self.width = 50.0 # set the width and height parameters for this object
	self.height = 25.0
	self.initDraw(self.colours[1]) # create a new paralellogram

    ############ Draw methods ############################

    def setFocus(self, focus) :
	GuiObject.setFocus(self, focus) # call to super's set focus
	self.drawArea.delete(self.id) # remove the current parallelogram
	self.drawArea.delete(self.label) # remove label
	if (focus) : col = self.colours[0]
	else : 	       col = self.colours[1]
	self.initDraw(col) # create new one with correct colour
	# redraw the connections
	for con in self.toCon : 
		con.move()
	for con in self.fromCon :
		con.move()

    def initDraw(self, colour) :
	# get the parallelogram points
	x1 = self.x - (1.5 * self.width)
	y1 = self.y - self.height
	x2 = self.x + (0.5 * self.width)
	y2 = self.y + self.height
	midx = 0.5 * (x2 - x1) # mid x coord
	try :
		self.id = (self.drawArea.create_polygon(x1, y2, (x1 + midx), y1, (x2 + midx), y1,
							x2, y2, fill = colour , outline = "black"))
		self.label = self.drawArea.create_text(self.x - (60 + len(self.name)*3), self.y, text = self.name)
	
	except IndexError :
		print("Out of Canvas")

    def draw(self, x = 0, y = 0) :
	# move the parallelogram and label by the given x, y coords (default redraw)
	try :
		self.drawArea.move(self.id, x, y)
		self.drawArea.move(self.label, x, y)
	except IndexError :
		print("Out of Canvas")
		
	# redraw the connections
	for con in self.toCon : 
		con.move()
	for con in self.fromCon :
		con.move()

    ############ Update methods ############################ 

    def remove(self) :
	l = len(self.fromCon) # remove all the connections from and to this sheet
	for index in range(l) :
		self.fromCon[0].remove()
	l = len(self.toCon)
	for index in range(l) :
		self.toCon[0].remove()
	self.drawArea.delete(self.id) # remove the sheet and label from the draw area
	self.drawArea.delete(self.label)
	self.drawArea.removeObject(self) # remove from canvas' object list

    def move(self, x, y) :
	# the connections position is updated
	old = self.x, self.y
	self.x = x
	self.y = y
	self.draw(self.x - old[0], self.y - old[1])

    ############ Util methods ##############################

    def inBounds(self, x, y) : # returns true if point lies in a bounding box
	# current box is a rectangular compromise between the largest and smallest extent of the 
	# parallelogram
	if ((y > (self.y - self.height)) & (y < (self.y + self.height)) & 
	(x > (self.x - self.width)) & (x < (self.x + self.width))) :
		return 1
	return 0


"""
A connection formed between 2 GuiObjects on a GUICanvas. A GuiConnection is used
to cover any topographica connection (connection / projection), and extending 
classes will supply a draw method and other type specific attributes. An instance 
of this class can have the focus.

"""

class GuiConnection :
	
    def __init__(self, canvas, objectFrom) :
	self.objectFrom = objectFrom # initial object selected
	self.canvas = canvas # reference to the canvas
	self.objectTo = None # updated when the user selecs the second object - self.connect(..)
	# temporary point, for when the to connection object is undefined
	self.posTo = objectFrom.getPos()
	self.focus = False # this does not have the focus


    ############ Draw methods ############################

    def setFocus(self, focus) : # give this connection the focus
     	self.focus = focus
	self.draw()

    def draw(self) :
	# draw this connection in canvas
	pass

    ############ Update methods ############################ 
    
    def move(self) :
	# if one of the objects connected by this connection move, then move by redrawing
	self.draw() 

    def updtPos(self, pos) : # update the temporary point
	self.posTo = pos
	self.draw()

    def remove(self) :
	# remove this connection from the objects it is connected to and from canvas
	pass

    def connect(self, objectTo, con) : # pass the object this connection is to
	self.connection = con # store the topo connection this Object represents
	if (self.objectFrom == objectTo) : # if lateral connection, update that obects counter
		self.drawIndex = objectTo.getLoopCount()
		objectTo.incrementLoopCount()
	self.objectTo = objectTo # store a reference to the object this is connected to
	self.objectFrom.attatchCon(self, GuiObject.FROM) # tell the sheets that they are connected.
	self.objectTo.attatchCon(self, GuiObject.TO)
	self.posTo = None

    ############ Util methods ##############################

    def inBounds(self, x, y) :
	# return true, if x,y lies within this connection's boundary
	pass



####################################################################

"""
Represents any topo projection. It is a subclass of GuiConnection and fills 
in the methods that are not defined. It is represented by a either a line with
an arrow head in the middle, or a circle if representing a lateral projection.
Uses bounding box to determine if x,y coord is within a boundary around the 
arrow head.

"""

class GuiProjection(GuiConnection) :
	
	def __init__(self, canvas, objectFrom) :
		GuiConnection.__init__(self, canvas, objectFrom)
		# if more than one connection between objects, 
		# this will reflect how to draw this connection
		self.drawIndex = 0 
		self.id = (None,None)

    ############ Draw methods ############################
	def draw(self) :
		# determine if connected to a second sheet, and find the correct posFrom
		for id in self.id : # remove the old connection
			self.canvas.delete(id)

		posFrom = self.objectFrom.getPos() # get the centre points of the two objects
	  	if (self.objectTo == None) :  # if not connected yet, use temporary point.
			posTo = self.posTo
		else :
			posTo = self.objectTo.getPos()

		# set the colour to be used depending on whether connection has the focus.
		if (self.focus) : col = 'slate blue'
		else : col = 'black'

	  	if (posTo == posFrom) : # connection to and from the same sheet
			 # change the size of circle depending how many lateral connections there are.
			dev = self.drawIndex * 10 
	    		x1 = posTo[0] - (20 + dev)
	    		y2 = posTo[1]
	    		x2 = x1 + 40 + (2 * dev)
	    		y1 = y2 - (30 + dev) 
	    		midX = self.getMid((x1,0),(x2,0))[0]
			# create oval and an arrow head.
			self.id = (self.canvas.create_oval(x1, y1, x2, y2, outline = col), 
	        		self.canvas.create_line(midX, y1, midX+1, y1, arrow = FIRST, fill = col))
	  	else : # connection between distinct objects
	    		mid = self.getMid(posFrom, posTo)
			# create a  line between the objects - use 2 to make arrow in centre.
	    		self.id = (self.canvas.create_line(posFrom, mid , arrow = LAST, fill = col),
	    			self.canvas.create_line(mid, posTo, fill = col))
	
    ############ Update methods ############################ 
	def remove(self) :
		for id in self.id : # remove the representation from the canvas
			self.canvas.delete(id)
		if (self.objectTo != None) : # if a connection had been made then remove it from the 'to' object
			self.objectTo.removeCon(self, GuiObject.TO)
		self.objectFrom.removeCon(self, GuiObject.FROM) # and remove from 'from' object


     ############ Util methods ##############################

	def getMid(self, pos1, pos2) : # returns the middle of two points
		return (pos1[0] + (pos2[0] - pos1[0])*0.5, pos1[1] + (pos2[1] - pos1[1])*0.5)
	
	def inBounds(self, x, y) : # returns true if point lies in a bounding box
		# currently uses an extent around the arrow head.
		posTo = self.objectTo.getPos()
		posFrom = self.objectFrom.getPos()
		if (self.objectTo == self.objectFrom) :
			dev = self.drawIndex * 10
			mid = (posTo[0], posTo[1] - (30 + dev))
		else :
			mid = self.getMid(posFrom, posTo)

		if ((x < mid[0] + 10) & (x > mid[0] - 10) & (y < mid[1] + 10) & (y > mid[1] - 10)) :
			return 1
		return 0
