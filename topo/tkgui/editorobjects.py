"""
Objects that can be manipulated by the model editor GUI.

Originally written by Alan Lindsay.
$Id$
"""
__version__='$Revision$'

# JABALERT: Please try to eliminate import *
from Tkinter import *
import Pmw
import math

from parametersframe import ParametersFrame

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

    def showProperties(self) :
	# show parameters frame for object
	paramWindow = Toplevel()
	Label(paramWindow, text = self.name).pack(side = TOP)
	self.paramFrame = ParametersFrame(paramWindow)
	self.buttonPanel = Frame(paramWindow)
	self.buttonPanel.pack(side = BOTTOM)
        #JABHACKALERT: We also need an OK button that applies and then closes the window
	updateButton = Button(self.buttonPanel, text = 'Update', command = self.updateParameters)
	updateButton.pack(side = LEFT)

    def updateParameters(self) :
	self.paramFrame.set_obj_params()

    def setFocus(self, focus) : # set focus
	self.focus = focus

    def move(self) :
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

    def attachCon(self, con, fromTo) :
	if (fromTo == self.FROM) :
		self.fromCon = self.fromCon + [con]
	else :
		self.toCon = self.toCon + [con]
	self.draw()
	
    def removeCon(self, con, fromTo) : # remove a connection to or from this node
	if (fromTo) :
		l = len(self.toCon)
		for i in range(l) :
			if (con == self.toCon[i]) : break
		else : return
		del self.toCon[i]
		node = con.nodeFrom
	else :
		l = len(self.fromCon)
		for i in range(l) :
			if (con == self.fromCon[i]) : break
		else : return
		del self.fromCon[i]
		node = con.nodeTo
	index = con.drawIndex
	# Decrease the indexes of the connections between the same nodes and with a higher index.
	for con in self.fromCon :
		if (node == con.nodeTo and con.drawIndex > index) :
			con.drawIndex -= 1
			if (not(con.nodeTo == con.nodeFrom)) :
				con.connectToCoord(self.width)
	self.draw()

    def getConCount(self, node) :
	count = 0
	for con in self.fromCon :
		if (con.nodeTo == node) :
			count += 1
	for con in self.toCon :
		if (con.nodeFrom == node) :
			count += 1
	return count

    ############ Util methods ##############################
    
    def getPos(self) :
	return (self.x, self.y) # return center point of node

    def showProperties(self) :
	EditorObject.showProperties(self)
	self.paramFrame.create_widgets(self.sheet)
	lateralButton = Button(self.buttonPanel, text = 'Lateral', command = self.showLatParams)
	lateralButton.pack(side = RIGHT)

    def showLatParams(self) :
	latList = []
	for con in self.fromCon :
		if (con.nodeTo == con.nodeFrom) :
			latList += [con]
	paramWindow = Toplevel()
	for con in latList :
		frame = Frame(paramWindow)
		frame.pack(side = LEFT)
		Label(frame, text = con.name).pack(side = TOP)
		con.paramFrame = ParametersFrame(frame)
		con.paramFrame.create_widgets(con.connection)
		buttonPanel = Frame(frame)
		buttonPanel.pack(side = BOTTOM)
		Button(buttonPanel, text = 'Update', 
				command = con.updateParameters).pack(side = LEFT)
		Button(buttonPanel, text = 'Delete',
				command = con.remove).pack(side = RIGHT)

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
	sheet.guiX, sheet.guiY = self.x, self.y # store the ed coords in the topo sheet
	self.width = 70.0 # set the width and height parameters for this object
	self.height = 35.0
	col = self.colours[1]
	self.initDraw(col) # create a new paralellogram
	self.currentCol = col
	self.gradient = 1

    ############ Draw methods ############################

    def setFocus(self, focus) :
	EditorNode.setFocus(self, focus) # call to super's set focus
	self.canvas.delete(self.id) # remove the current parallelogram
	self.canvas.delete(self.label) # remove label
	if (focus) : col = self.colours[0]
	else : 	       col = self.colours[1]
	self.initDraw(col) # create new one with correct colour
	"""
	Try something like this instead..
	if focus : 
		col = self.colours[0]
	else :
		col = self.colours[1]
	self.canvas.config(self.id, fill = col)"""
	self.currentCol = col
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
		if (not(con.nodeFrom == con.nodeTo)) :
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
	self.sheet.guiX, self.sheet.guiY = x, y # update topo sheet position
	self.draw(self.x - old[0], self.y - old[1])

    ############ Util methods ##############################

    def inBounds(self, posx, posy) : # returns true if point lies in a bounding box
	# if the coord is pressed within the parallelogram representation this 
	# returns true.
	# Get the paralellogram points and centers them around the given point
	x = self.x - posx; y = self.y - posy
	A = (x - (1.5 * self.width), y + self.height)
	B = (x - (0.5 * self.width), y - self.height)
	C = (x + (1.5 * self.width), y - self.height)
	D = (x + (0.5 * self.width), y + self.height)
	# calculate the line constants 	
	# As the gradient of the lines is 1 the calculation is simple.
	aAB = A[1] + A[0]
	aCD = C[1] + C[0]
	# The points are centered around the given coord, finding the intersects with line y = 0
	# and ensuring that the left line lies on the negative side of the point and the right line
	# lies on the positive side of the point determines that the point is within the parallelogram.
	if ((D[1] >= 0) and (B[1] <= 0) and (aAB <= 0) and (aCD >= 0)) :
		return True
	return False


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
     	EditorObject.setFocus(self, focus)
	self.draw()

    ############ Update methods ############################ 
    
    def move(self) :
	# if one of the nodes connected by this connection move, then move by redrawing	
	self.gradient = self.calcGradient()
	self.draw() 

    def updtPos(self, pos) : # update the temporary point
	self.posTo = pos
	self.draw()

    def connect(self, nodeTo, con) : # pass the node this connection is to
	#from topo.base.projection import Projection
	self.connection = con # store the topo connection this object represents
	if (self.name == "") :
		self.name = con.name
	self.drawIndex = self.nodeFrom.getConCount(nodeTo)
	if (not (self.nodeFrom == nodeTo)) :
		self.connectToCoord(self.nodeFrom.width - 10)
	self.nodeTo = nodeTo # store a reference to the node this is connected to
	self.nodeFrom.attachCon(self, self.FROM) # tell the sheets that they are connected.
	self.nodeTo.attachCon(self, self.TO)
	self.posTo = None
	self.gradient = self.calcGradient()

    ############ Util methods ##############################
    def showProperties(self) :
	EditorObject.showProperties(self)
	self.paramFrame.create_widgets(self.connection)

    def connectToCoord(self, width) :
	n = self.drawIndex
	sign = math.pow(-1, n)
	self.dev = sign * width + (-sign) * math.pow(0.5, math.ceil(0.5 * (n + 1))) * width


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
	self.dev = 0
	self.radius = 10
	self.gradient = (1,1)
	self.id = (None,None)
	self.label = None
	self.balloon = Pmw.Balloon(canvas)

    ############ Draw methods ############################
    def draw(self, receptiveFields = True) :
	# determine if connected to a second node, and find the correct posFrom
	for id in self.id : # remove the old connection
		self.canvas.delete(id)
	self.canvas.delete(self.label)
	posFrom = self.nodeFrom.getPos() # get the centre points of the two nodes
	if (self.nodeTo == None) :  # if not connected yet, use temporary point.
		posTo = self.posTo
		latCol = self.nodeFrom.currentCol
	else :
		posTo = self.nodeTo.getPos()
		latCol = self.nodeTo.currentCol

	# set the colour to be used depending on whether connection has the focus.
	if (self.focus) : col = 'slate blue'
	else : col = 'black'
	# midpoint of line
	mid = self.getMid(posFrom, posTo)
	if (posTo == posFrom) : # connection to and from the same node
		"""
		AL - OLD: Shows lateral connections as loops (here to see if still useful)
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
		"""
		n = 0.7 * self.drawIndex
		fact = (15 / (1 + n))  
		x1 = posTo[0] - (2 * fact)
		y1 = posTo[1] + fact
		x2 = posTo[0] + (2 * fact)
		y2 = posTo[1] - fact
		self.id = (self.canvas.create_oval(x1, y1, x2, y2, fill = latCol, 
						dash = (2,2), outline = 'black'), None)
		self.balloon.tagbind(self.canvas, self.id[0], self.name)

	else :  # connection between distinct nodes
		if (receptiveFields) : # if receptive fields are to be drawn
			x1, y1 = posTo
			x2, y2 = posFrom
			x1 += self.dev
			x2 += self.dev
			rad = self.radius
			self.id = (self.canvas.create_line(x1,y1,x2-rad,y2, fill = col),
				   self.canvas.create_line(x1,y1,x2+rad,y2, fill = col),
				   self.canvas.create_oval(x2-rad,y2-(0.5*rad),x2+rad,y2+(0.5*rad)))
		else :
			# create a line between the nodes - use 2 to make arrow in centre.
	    		self.id = (self.canvas.create_line(posFrom, mid , arrow = LAST, fill = col),
	    			  self.canvas.create_line(mid, posTo, fill = col))
		# draw name label
		dX = (10 + len(self.name)*3)
		dY = self.drawIndex * 20
		self.label = self.canvas.create_text(mid[0] - dX,
			     mid[1] - dY, text = self.name)
	
	
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

    def calcGradient(self) :
	posTo = (self.nodeTo.x, self.nodeTo.y)
	posFrom = (self.nodeFrom.x, self.nodeFrom.y)
	A = (posTo[0] + self.dev ,posTo[1])
	T = (posFrom[0] + self.dev ,posFrom[1])
	B = (T[0] - self.radius, T[1])
	C = (T[0] + self.radius, T[1])
	try :
		MBA = (A[1] - B[1]) / (A[0] - B[0])
		MCA = (A[1] - C[1]) / (A[0] - C[0])
	except ZeroDivisionError :
		return 99999 # AL - this should be a big number
	return (MBA, MCA)

    def inBounds(self, x, y, receptiveFields = True) : # returns true if point lies in a bounding box
	# returns true if x, y lie inside the triangular receptive field representing this projection
	if (receptiveFields) :
		if (self.nodeTo == None or self.nodeTo == self.nodeFrom) :
			return False
		# get the points of the triangular receptive field, centered around the x, y point given
		posTo = (self.nodeTo.x, self.nodeTo.y)
		posFrom = (self.nodeFrom.x, self.nodeFrom.y)
		A = (posTo[0] + self.dev - x, posTo[1] - y)
		T = (posFrom[0] + self.dev - x, posFrom[1] - y)
		B = (T[0] - self.radius, T[1])
		C = (T[0] + self.radius, T[1])
		# if the y coords lie outwith the boundaries, return false
		if (((A[1] < B[1]) and (B[1] < 0 or A[1] > 0)) or 
		    ((A[1] >= B[1]) and (B[1] > 0 or A[1] < 0))) :
			return False
		# calculate the constant for the lines of the triangle
		aBA = A[1] - (self.gradient[0] * A[0])
		aCA = A[1] - (self.gradient[1] * A[0])
		# The points are centered around the given coord, finding the intersects with line y = 0
		# and ensuring that the left line lies on the negative side of the point and the right line
		# lies on the positive side of the point determines that the point is within the triangle.
		if (((0 - aCA) / self.gradient[1] >= 0) and ((0 - aBA) / self.gradient[0] <= 0)) :
			return True
		return False	

	# If connections are represented as lines
	# currently uses an extent around the arrow head.
	posTo = self.nodeTo.getPos()
	posFrom = self.nodeFrom.getPos()
	if (self.nodeTo == self.nodeFrom) :
		dev = self.drawIndex * 15
		mid = (posTo[0], posTo[1] - (30 + dev))
	else :
		mid = self.getMid(posFrom, posTo)

	if ((x < mid[0] + 10) & (x > mid[0] - 10) & (y < mid[1] + 10) & (y > mid[1] - 10)) :
		return True
	return False
