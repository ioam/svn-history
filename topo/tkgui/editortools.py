"""
Tools for the model editor GUI toolbar.

Originally written by Alan Lindsay.
$Id$
"""
__version__='$Revision$'

from Tkinter import *
from editorobjects import GUISheet
import topo.sheets
from topo.sheets import *
from topo.base.utils import find_classes_in_package
from topo.base.sheet import Sheet
from editorobjects import GuiProjection
import topo.projections
from topo.projections import *
from topo.base.utils import find_classes_in_package
from topo.base.projection import Projection

### JABALERT: Should change these names to ArrowTool, etc.

class ArrowToolbar(Frame) :
    """
    ArrowToolbar is a selectable frame containing an arrow icon and a label. It is a
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
	self.icon = Canvas(self, bg = 'light grey', width = 35, height = 30, bd = 0)
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

class ObjectToolbar(Frame) :
     """
     SheetToolbar extends Frame. It is expected to be included in a topographica
     model development GUI and functions as a self populating Object toolbar.
     The available Sheet types are supplied to be selected from. The Toolbar supplies
     a suitable GUI cover for an object and creates the topo object(Sheet).
     """

     ############ Constructor ####################################

     def __init__(self, canvas,  parent = None) :
	# super constructor call.
	Frame.__init__(self, parent, bg = 'light grey', bd = 2, relief = GROOVE)
	self.canvas = canvas # hold canvas reference.
	# label sets canvas mode.
	self.titleLabel = Label(self, text="Object:", bg ='light grey')
	self.titleLabel.bind('<Button-1>', self.changeMode)
	self.titleLabel.pack()
	# gets list of all the available sheets.
	self.sheetList = self.getSheetList()
	sheetList = self.sheetList.keys()
	# create a dictionary with an entry for each sheet option. This will act as a count
	# giving a convenient way of forming default sheet names.
	self.cntDict = {}
	for name in sheetList :
		self.cntDict[name] = 0
	# sets up a reference to the string associated with the current menu selection.
	self.currentOp = StringVar()
	self.currentOp.set(sheetList[0])
	# populate the menu with the available sheet list.
	self.opMenu = apply(OptionMenu, (self, self.currentOp) + tuple(sheetList))
	self.opMenu.config(bg = 'light grey')
	self.opMenu.pack()
	self.opMenu.bind('<Button-1>', self.changeMode)
	# pack in toolbar at top and fill out in X direction; click changes canvas mode
	self.pack(side = TOP, fill = X)
	self.bind('<Button-1>', self.changeMode)

     ####### Focus Methods ####################################################
	
     def changeMode(self, event) :
	# changes the GUICanvas mode to 'MAKE'
	self.canvas.changeMode('m') 

     def setFocus(self, focus) :
	# change the background highlight to reflect whether this toolbar item is selected or not
	if (focus) :
		col = 'dark grey'
	else :
		col = 'light grey'
		
	self.config(bg = col)
	self.opMenu.config(bg = col)
	self.titleLabel.config(bg = col)

     ####### Object Methods ###################################################

     def createObject(self, x, y) :
	# get the current selection
	curOp = self.currentOp.get()
	# create the new topo object
	sheet = self.sheetList[curOp]()
	# get the count for this sheet type and increment the count
	count = self.cntDict[curOp]
	self.cntDict[curOp] += 1
	# create the cover for the sheet and return it.
	guiSheet = GUISheet(self.canvas, sheet, (x, y), (curOp + " " + str(count)))
	return guiSheet
	

     ####### Util Methods #####################################################
     def getSheetList(self ) :	
	# find all subclasses of Sheet defined in topo/sheets
	return find_classes_in_package(topo.sheets, Sheet)

###############################################################################

""" ConToolbar extends Frame. It is expected to be included in a topographica
    model development GUI and functions as a self populating Connection toolbar.
    The available Connection types are listed and the user can select one.
    When a connection is formed between two sheets a topo.projection of the
    specified type is instantiated and a reference to it is stored in it's GUI
    cover. Allows user to change the GUICanvas mode to 'CONNECTION' mode."""

# NOTE currently only searches for topo.projections (connections have not been implemented yet).

class ConToolbar(Frame) :

     ############ Constructor ####################################

     def __init__(self, canvas,  parent = None) :
	# super constructor call.
	Frame.__init__(self, parent, bg = 'light grey', bd = 2, relief = GROOVE)
	self.canvas = canvas # hold canvas reference.
	# gets list of all the available projections.
	self.projList = self.getProjList()
	projList = self.projList.keys() # gets the class names.
	# label sets canvas mode.
	self.titleLabel = Label(self, text = "Connect:", bg = 'light grey')
	self.titleLabel.pack()
	self.titleLabel.bind('<ButtonRelease-1>', self.changeMode)
	# sets up a reference to the string associated with the current menu selection.
	self.currentOp = StringVar()
	self.currentOp.set(projList[0])
	# populate the menu with the available projection list.
	self.opMenu = apply(OptionMenu, (self, self.currentOp) + tuple(projList))
	self.opMenu.config(bg = 'light grey')
	self.opMenu.pack()
	self.opMenu.bind('<Button-1>', self.changeMode) # menu sets canvas mode.
	self.width = 200
	self.height = 100
	# pack in toolbar at top and fill out in X direction; click changes canvas mode
	self.pack(side = TOP, fill = X)
	self.bind('<Button-1>', self.changeMode)

     ########## Canvas Topo Linking Methods #########################################

     def newCover(self, fromObj) :
	# create a GUIProjection and return it. If more than one representation for 
	# connections/projections the returned object will depend on current selection.
	return GuiProjection(self.canvas, fromObj)

     def createConnection(self, guiCon, obj) :
	# connects the gui connection. Will also form correct connection in the
	# topo simulator.
	sim = self.canvas.simulator
	obj1 = guiCon.objectFrom.sheet
	obj2 = obj.sheet
	conType = self.projList[self.currentOp.get()]
	name = guiCon.objectFrom.name + " TO " + obj.sheet.name
	sim.connect(obj1, obj2, connection_type = conType, connection_params={'name': name})
	con = None
	guiCon.connect(obj, con)

     ########## Focus Methods #######################################################
	
     def changeMode(self, event) :
	# changes the GUICanvas mode to 'CONNECTION'
	self.canvas.changeMode('c') 

     def setFocus(self, focus) :
	# change the background highlight to reflect whether this toolbar item is selected or not
	if (focus) :
		col = 'dark grey'
	else :
		col = 'light grey'
	
	self.config(bg = col)
	self.opMenu.config(bg = col)
	self.titleLabel.config(bg = col)

     ########### Util Methods ########################################################
     def getProjList(self ) :
	# find all subclasses of Projection defined in topo/projections
	return find_classes_in_package(topo.projections, Projection)

