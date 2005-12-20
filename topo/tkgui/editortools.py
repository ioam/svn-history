"""
Tools for the model editor GUI toolbar.

Originally written by Alan Lindsay.
$Id$
"""
__version__='$Revision$'

from Tkinter import *
import Pmw
from editorobjects import EditorSheet, EditorProjection
import topo.sheets
from topo.sheets import *
from topo.base.utils import find_classes_in_package
from topo.base.sheet import Sheet
import topo.projections
from topo.projections import *
from topo.base.utils import find_classes_in_package
from topo.base.projection import Projection

class ArrowTool(Frame) :
    """
    ArrowTool is a selectable frame containing an arrow icon and a label. It is a
    toolbar item in a ModelEditor that allows the user to change the GUICanvas to 
    'ARROW' mode. 
    """
    ############ Constructor ####################################

    def __init__(self, canvas,  parent = None) :
	# super constructor call
	Frame.__init__(self, parent, bg = 'light grey', bd = 2, relief = GROOVE)
	self.canvas = canvas # hold canvas reference
	# label sets canvas mode
	self.titleLabel = Label(self, text="Move:", bg ='light grey')
	self.titleLabel.bind('<Button-1>', self.changeMode)
	self.titleLabel.pack()
	# arrow icon
	self.icon = Canvas(self, bg = 'light grey', width = 35, height = 30)
	self.icon.create_polygon(10,0, 10,22, 16,17, 22,29, 33,22, 25,13, 33,8, 
						fill = 'black', outline = 'white')
	self.icon.pack()
	self.icon.bind('<Button-1>', self.changeMode) # icon sets canvas mode
	# pack in toolbar at top and fill out in X direction; click changes canvas mode
	self.pack(side = TOP, fill = X)
	self.bind('<Button-1>', self.changeMode)
	
    ####### Focus Methods ####################################################
	
    def changeMode(self, event) :
	# change the canvas mode to 'ARROW'.
	self.canvas.changeMode('a')

    def setFocus(self, focus) :
	# change the background highlight to reflect whether this toolbar item is selected or not
	if (focus) :
		col = 'dark grey'
	else :
		col = 'light grey'
		
	self.config(bg = col)
	self.titleLabel.config(bg = col)
	self.icon.config(bg = col)

###############################################################################

class NodeTool(Frame) :
     """
     NodeTool extends Frame. It is expected to be included in a topographica
     model development GUI and functions as a self populating Node tool.
     The available Sheet types are supplied to be selected from. This Tool supplies
     a suitable Editor cover for a node and creates the corresponding topo object.
     """
     ############ Constructor ####################################

     def __init__(self, canvas,  parent = None) :
	# super constructor call.
	Frame.__init__(self, parent, bg = 'light grey', bd = 2, relief = GROOVE)
	self.canvas = canvas # hold canvas reference.
	# pack in toolbar at top and fill out in X direction
	self.pack(side = TOP, fill = X)
	# gets list of all the available sheets.
	self.sheetList = self.getSheetList()
	sheetList = self.sheetList.keys()
	# populate the menu with the available sheet list.
	self.opMenu = Pmw.ComboBox(self, label_text = 'Sheet :', labelpos = 'nw',
				   selectioncommand = self.setOption, scrolledlist_items = sheetList)
	self.opMenu.pack()
	self.opMenu.bind('<Button-1>', self.changeMode)
	# select the initial selection
	self.opMenu.selectitem(sheetList[0])
	self.currentOp = sheetList[0]

     ####### Focus Methods ####################################################
	
     def changeMode(self, option) :
	# changes the EditorCanvas mode to 'MAKE'
	self.canvas.changeMode('m')

     def setFocus(self, focus) :
	# change the background highlight to reflect whether this toolbar item is selected or not
	if (focus) :
		col = 'dark grey'
	else :
		col = 'light grey'
	self.config(bg = col)
	self.opMenu.config(bg = col)

     ####### Node Methods ###################################################

     def createNode(self, x, y) :
	# get the current selection and create the new topo object
	sheet = self.sheetList[self.currentOp]()
	sim = self.canvas.simulator # get the current simulator
	sim.add(sheet)
	# create the cover for the sheet and return it.
	return EditorSheet(self.canvas, sheet, (x, y), sheet.name)

     ####### Util Methods #####################################################
     def getSheetList(self) :	
	# find all subclasses of Sheet defined in topo/sheets
	return find_classes_in_package(topo.sheets, Sheet)

     def setOption(self, option) :
	self.currentOp = option
	self.changeMode(None)

###############################################################################

# NOTE currently only searches for topo.projections (connections have not been implemented yet).

class ConTool(Frame) :
     """ 
     ConTool extends Frame. It is expected to be included in a topographica
     model development GUI and functions as a self populating Connection toolbar.
     The available Connection types are listed and the user can select one.
     When a connection is formed between two nodes a topo.projection of the
     specified type is instantiated and a reference to it is stored in it's Editor
     cover. Allows user to change the EditorCanvas mode to 'CONNECTION' mode.
     """
     ############ Constructor ####################################

     def __init__(self, canvas, parent = None) :
	# super constructor call.
	Frame.__init__(self, parent, bg = 'light grey', bd = 2, relief = GROOVE)
	self.canvas = canvas # hold canvas reference.
	# pack in toolbar at top and fill out in X direction
	self.pack(side = TOP, fill = X)
	# gets list of all the available projections.
	self.projList = self.getProjList()
	projList = self.projList.keys() # gets the class names.
	# populate the menu with the available projection list.
	self.opMenu = Pmw.ComboBox(self, label_text = 'Projections :', labelpos = 'nw',
				   selectioncommand = self.setOption, scrolledlist_items = projList)
	self.opMenu.bind('<Button-1>', self.changeMode)
	self.opMenu.pack()
	# select the initial selection
	self.opMenu.selectitem(projList[0])
	self.currentOp = projList[0]

     ########## Canvas Topo Linking Methods #########################################

     def newCover(self, fromObj) :
	# create a EditorProjection and return it. If more than one representation for 
	# connections/projections the returned object will depend on current selection.
	return EditorProjection("", self.canvas, fromObj)

     def createConnection(self, edCon, node) :
	# connects the ed connection. Will also form correct connection in the
	# topo simulator.
	sim = self.canvas.simulator
	node1 = edCon.nodeFrom.sheet
	node2 = node.sheet
	conType = self.projList[self.currentOp]
	con = sim.connect(node1, node2, connection_type = conType)
	edCon.connect(node, con)
     
     def setOption(self, option) :
	self.currentOp = option
	self.changeMode(None)

     ########## Focus Methods #######################################################
     def changeMode(self, option) :
	# changes the EditorCanvas mode to 'CONNECTION'
	self.canvas.changeMode('c') 

     def setFocus(self, focus) :
	# change the background highlight to reflect whether this toolbar item is selected or not
	if (focus) :
		col = 'dark grey'
	else :
		col = 'light grey'
	
	self.config(bg = col)
	self.opMenu.config(bg = col)

     ########### Util Methods ########################################################
     def getProjList(self ) :
	# find all subclasses of Projection defined in topo/projections
	return find_classes_in_package(topo.projections, Projection)

