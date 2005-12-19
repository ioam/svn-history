"""
Objects that can be manipulated by the model editor GUI.

Originally written by Alan Lindsay.
$Id$
"""
__version__='$Revision$'

# JABALERT: Please try to eliminate import *
from Tkinter import *

class EditorObject :
    """
    Anything that can be added and manipulated in an EditorCanvas. Every EditorCanvas
    has a corresponding Topo object associated with it. An instance of this class can 
    have the focus.
    """
    FROM = 0
    TO = 1

    # constructor
    def __init__(self, name, canvas) :
	self.canvas = canvas # retains a reference to the canvas
	self.name = name # set the name of the sheet
	self.focus = False # this does not have the focus

    def draw(self) :
	# draw the object at the current x, y position
	pass

    def setFocus(self, focus) : # set focus
	self.focus = focus

    def move(self, x, y) :
	# update position of object and redraw
	pass

    def remove(self) :
	# remove this object from the canvas and deal with relevant 
	# Topographica objects.
	pass    

    def inBounds(self, x, y) : 
	# return true, if x,y lies within this gui object's boundary
	pass

####################################################################


class EditorNode(EditorObject) :
    """
    An EditorNode is used to cover any topographica node, presently this can only be a sheet.
    It is a sub class of EditorObject and supplies the methods required by any node to be used
    in a EditorCanvas. Extending classes will supply a draw method and other type specific 
    attributes. 
    """
    def __init__(self, canvas, pos, name, colour = ('slate blue', 'lavender')) :
	EditorObject.__init__(self, name, canvas)
	self.colours = colour # colours for drawing this node on the canvas
	self.fromCon = [] # connections from this node
	self.toCon = [] # connections to this node
	self.x = pos[0] # set the x and y coords of the centre of this node
	self.y = pos[1]
	self.loopCount = 0

    ############ Connection methods ########################

    def attatchCon(self, con, fromTo) : # add the connection to or from this node
	if (fromTo == self.FROM) :
		self.fromCon = self.fromCon + [con]
	else :
		self.toCon = self.toCon + [con]
	
    def removeCon(self, con, fromTo) : # remove a connection to or from this node
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

    ############ Util methods ##############################
    
    def getPos(self) :
	return (self.x, self.y) # return center point of node



class EditorSheet(EditorNode) :
    """
    Represents any topo sheet. It is a subclass of EditorNode and fills in the
    methods that are not defined. It is represented by a Paralellogram in its
    Canvas. The colours used for drawing can be set. Uses bounding box to
    determine if x, y coord is within its boundary.
    """
    def __init__(self, canvas, sheet, pos, name) :
	# super constructor call
	EditorNode.__init__(self, canvas, pos, name)
	self.sheet = sheet # the topo sheet that this object represents
	self.width = 50.0 # set the width and height parameters for this object
	self.height = 25.0
	self.initDraw(self.colours[1]) # create a new paralellogram

    ############ Draw methods ############################

    def setFocus(self, focus) :
	EditorNode.setFocus(self, focus) # call to super's set focus
	self.canvas.delete(self.id) # remove the current parallelogram
	self.canvas.delete(self.label) # remove label
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
		self.id = (self.canvas.create_polygon(x1, y2, (x1 + midx), y1, (x2 + midx), y1,
							x2, y2, fill = colour , outline = "black"))
		self.label = self.canvas.create_text(self.x - (60 + len(self.name)*3), self.y, text = self.name)
	
	except IndexError :
		print("Out of Canvas")

    def draw(self, x = 0, y = 0) :
	# move the parallelogram and label by the given x, y coords (default redraw)
	try :
		self.canvas.move(self.id, x, y)
		self.canvas.move(self.label, x, y)
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
	self.canvas.delete(self.id) # remove the sheet and label from the draw area
	self.canvas.delete(self.label)
	self.canvas.removeObject(self) # remove from canvas' object list

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

####################################################################

class EditorConnection(EditorObject) :

    """
    A connection formed between 2 EditorNodes on a EditorCanvas. A EditorConnection is used
    to cover any topographica connection (connection / projection), and extending 
    classes will supply a draw method and other type specific attributes.
    """
    def __init__(self, name, canvas, nodeFrom) :
	EditorObject.__init__(self, name, canvas)
	self.nodeFrom = nodeFrom # initial node selected
	self.nodeTo = None # updated when the user selects the second node - self.connect(..)
	# temporary point, for when the to connection node is undefined
	self.posTo = nodeFrom.getPos()
	


    ############ Draw methods ############################

    def setFocus(self, focus) : # give this connection the focus
     	self.focus = focus
	self.draw()

    ############ Update methods ############################ 
    
    def move(self) :
	# if one of the nodes connected by this connection move, then move by redrawing
	self.draw() 

    def updtPos(self, pos) : # update the temporary point
	self.posTo = pos
	self.draw()

    def connect(self, nodeTo, con) : # pass the node this connection is to
	#from topo.base.projection import Projection
	self.connection = con # store the topo connection this object represents
	if (self.name == "") :
		self.name = con.name
	if (self.nodeFrom == nodeTo) : # if lateral connection, update that obects counter
		self.drawIndex = nodeTo.getLoopCount()
		nodeTo.incrementLoopCount()
	self.nodeTo = nodeTo # store a reference to the node this is connected to
	self.nodeFrom.attatchCon(self, self.FROM) # tell the sheets that they are connected.
	self.nodeTo.attatchCon(self, self.TO)
	self.posTo = None


class EditorProjection(EditorConnection) :

    """
    Represents any topo projection. It is a subclass of EditorConnection and fills 
    in the methods that are not defined. It is represented by a either a line with
    an arrow head in the middle, or a circle if representing a lateral projection.
    Uses bounding box to determine if x,y coord is within a boundary around the 
    arrow head.
    """	
    def __init__(self, name, canvas, nodeFrom) :
	EditorConnection.__init__(self, name, canvas, nodeFrom)
	# if more than one connection between nodes, 
	# this will reflect how to draw this connection
	self.drawIndex = 0 
	self.id = (None,None)
	self.label = None

    ############ Draw methods ############################
    def draw(self, receptiveFields = True) :
	# determine if connected to a second node, and find the correct posFrom
	for id in self.id : # remove the old connection
		self.canvas.delete(id)
	self.canvas.delete(self.label)
	posFrom = self.nodeFrom.getPos() # get the centre points of the two nodes
	if (self.nodeTo == None) :  # if not connected yet, use temporary point.
		posTo = self.posTo
	else :
		posTo = self.nodeTo.getPos()

	# set the colour to be used depending on whether connection has the focus.
	if (self.focus) : col = 'slate blue'
	else : col = 'black'
	# midpoint of line
	mid = self.getMid(posFrom, posTo)
	if (posTo == posFrom) : # connection to and from the same node
		# change the size of circle depending how many lateral connections there are.
		dev = self.drawIndex * 15 
	    	x1 = posTo[0] - (20 + dev)
	    	y2 = posTo[1]
	    	x2 = x1 + 40 + (2 * dev)
	    	y1 = y2 - (30 + dev) 
	    	midX = self.getMid((x1,0),(x2,0))[0]
		# create oval and an arrow head.
		self.id = (self.canvas.create_oval(x1, y1, x2, y2, outline = col), 
	        self.canvas.create_line(midX, y1, midX+1, y1, arrow = FIRST, fill = col))
		# draw name label beside arrow head
		self.label = self.canvas.create_text(mid[0] - 
			     (20 + len(self.name)*3), mid[1] - (30 + dev) , text = self.name)
	else :  # connection between distinct nodes
		if (receptiveFields) : # if receptive fields are to be drawn
			x1, y1 = posTo
			x2, y2 = posFrom
			self.id = (self.canvas.create_line(x1,y1,x2-10,y2, fill = col),
				   self.canvas.create_line(x1,y1,x2+10,y2, fill = col),
				   self.canvas.create_oval(x2-10,y2-5,x2+10,y2+5))
		else :
			# create a line between the nodes - use 2 to make arrow in centre.
	    		self.id = (self.canvas.create_line(posFrom, mid , arrow = LAST, fill = col),
	    			  self.canvas.create_line(mid, posTo, fill = col))
		# draw name label beside arrow head
		self.label = self.canvas.create_text(mid[0] - 
			     (10 + len(self.name)*3), mid[1], text = self.name)
	
    ############ Update methods ############################ 
    def remove(self) :
	for id in self.id : # remove the representation from the canvas
		self.canvas.delete(id)
	self.canvas.delete(self.label)
	if (self.nodeTo != None) : # if a connection had been made then remove it from the 'to' node
		self.nodeTo.removeCon(self, self.TO)
	self.nodeFrom.removeCon(self, self.FROM) # and remove from 'from' node


    ############ Util methods ##############################
    def getMid(self, pos1, pos2) : # returns the middle of two points
	return (pos1[0] + (pos2[0] - pos1[0])*0.5, pos1[1] + (pos2[1] - pos1[1])*0.5)
	
    def inBounds(self, x, y) : # returns true if point lies in a bounding box
	# currently uses an extent around the arrow head.
	posTo = self.nodeTo.getPos()
	posFrom = self.nodeFrom.getPos()
	if (self.nodeTo == self.nodeFrom) :
		dev = self.drawIndex * 15
		mid = (posTo[0], posTo[1] - (30 + dev))
	else :
		mid = self.getMid(posFrom, posTo)

	if ((x < mid[0] + 10) & (x > mid[0] - 10) & (y < mid[1] + 10) & (y > mid[1] - 10)) :
		return 1
	return 0
