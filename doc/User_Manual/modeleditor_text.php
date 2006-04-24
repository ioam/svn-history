<h1>Topographica Model Editor</h1>

Topographica allows you to view, manipulate or create a Topographica model. By combining pre-defined components and changing each component's parameters, you can produce useful models without any programming.

<h2>Opening the Model Editor</h2>
<p>The model editor can be accessed through the Topographica console. Select the Simulation menu in the console's top menu bar, and choose the model editor. A new window will appear with a toolbar on the left, a view bar at the top and a work area in the middle.

<h2>Viewing a Model</h2>
<p>In order to understand the behaviour of a model it is often useful to know how the model is connected. The model editor can help you with this visualisation.

<p>Import the model you wish to visualise and then open a model editor window (as described above). The model editor will automatically display the existing model.

<h3>Representations</h3>
<p>There are two main classes of component used to define a model; the sheet, and the projection. 

<p>Sheets are the main computational unit in Topographica and are represented by a parallelogram. The default view indicates the size and shape of the sheet. The editor also allows you to plot a density grid over the sheet. This grid indicates how closely packed the neurons are on a sheet. This can be achieved by right clicking in the main window and selecting Toggle Density Grid from the Sheet options menu. The other option, Toggle Activity, allows you to display the actual activity of the sheets. If you only want to view the activity of one sheet then right click on the particular sheet and select Activity from the Change View menu. The activity of each neuron of the sheet is plotted onto the parallelogram, so the density of the sheet will determine how detailed the image appears.

<p>Although the sheets are the main units they have no way of communicating, this means that stimulus would not be able to move through a network. Projections form a uni-directional connection between sheets, allowing activity to propagate through a model. The projections allow each neuron on one sheet to be connected to a certain area on the other sheet; this area is called the projection's receptive field. Although the default view simply plots an abstracted receptive field (each is drawn with a standard size), you can choose to use the actual size of the receptive field instead. To change the view, right click on the desired projection and select Field Radius from the Change View menu. The line option in this menu simply joins the sheets with a directed line.

<p>Not all projections are between distinct sheets. The editor represents connections that join a sheet to itself as a dotted ellipse around the centre of the sheet. Again these projections allow each neuron on a sheet to be stimulated by an area of the sheets previous activity. You can view the size of this area by right clicking on the desired connection and selecting Field Radius from the Change View menu. A looped line is used as the line representation of the projection.

<p>The name of each sheet and projection is displayed beside their representation in the canvas. To find out the name of a projection that links a sheet to itself, hover the mouse over the representation. If it is not obvious which name is linked with an item, right click on the representation and select Properties. The name is displayed at the top of the window. To view other properties of a component refer to section called The Parameters, which describes the properties window.

<p>In this image you can see the representations used in the model editor for sheets and connections. a) marks a connection that joins from sheet b) to sheet c). The representation for connections to and from the same sheet is marked d) and a density grid and activity plot can be viewed on e) and f) respectively: 
<center>
<IMG WIDTH="845" HEIGHT="683" SRC="images/editorrepresentations.png">
</center>

<h2>Creating a Model</h2>
<p>Creating a new model for Topographica can be achieved in two ways. If you have any programming experience, you might consider defining a model in Python script. Example scripts are distributed with Topographica in the Examples folder. The second way is to use the model editor to either create a brand new model, or manipulate an existing model. 
<p>To create a model for Topographica, you need to specify the computational units required and how they should be connected. Open a new model editor window as described in Opening the Model Editor. If a model is loaded, the editor work area will display the model as described in Viewing a Model. Now you are ready to specify your model. 

<h3>Toolbar</h3>
<p>On the left hand side of the editor is a toolbar that sets the mode of the editor's work area. There are three items; the arrow, for selecting and moving items in the window; an object pull down, allowing you to enter a new sheet into the window; a connection pull down, allowing you to make connections between sheets in the window:
<center>
<IMG WIDTH="507" HEIGHT="176" SRC="images/editortoolbaritems.png">
</center>

<h3>The Work Area</h3>
<p>The main part of the editor is the work area (canvas), this displays a representation of the model that Topographica is currently using. If you haven't opened a model, this area will be empty. The first thing you may want to do is add a sheet to the model. Click on the sheet pull down menu and a list of all the types of sheet available to you will appear. This list is formed from the pre-defined library of Topographica, covered later. Select the type of sheet that you want to be part of your model, for example, you may wish to provide some stimulus to the model by using a GeneratorSheet, in this case you would select GeneratorSheet from the menu. Notice that the focus of the toolbar will have shifted to the object item, click in the canvas and a sheet of the type you selected will be added to the model. You can repeat this process until you have all the sheets you require for your model.
<p>To allow stimulus to flow through your model, you need to connect the sheets together. Click on the connection pull down and a list of all the existing types of projections will be presented. This list collects the pre-defined projections available to Topographica and is described later. Select the type of projection you want, for example, for a standard connection with a receptive field select a CFProjection. The canvas is now in connection mode, this means it will expect you to drag the mouse from one sheet to another (to the same sheet for feedback connections). To do this click and hold the mouse over the sheet you want the connection to be form. Then, while holding the mouse button down, move the mouse to the sheet you want to be connected to. Release the mouse button:
<center>
<IMG WIDTH="649" HEIGHT="378" SRC="images/editorconnectiondrag.png">
</center>
<p>In most cases this will form a connection between the two sheets and you will see the clear representation for the connection as shown above. If you have selected a sheet, but decide you don't want a connection, release the mouse in an area without any other components. To connect a sheet to itself, simply select the sheet and release the mouse while it is still over the same sheet.

<h3>The Predefined Components</h3>
<p>Topographica supplies a library of components, composed of both basic and specific sheets and projections. To understand what a particular component does you should consult the Library section of the reference manual. The section is divided into several different parts, so you can view all the possible sheets or projections available to you and use their descriptions to understand how you can use them in your model.
<p>The model editor's lists populate themselves from this library, so all the components described in the manual will be available for you to use in the editor. The editor places no restrictions on how you connect these components together, however projections may not always be able to connect obscurely shaped sheets.

<h3>Extending the Library</h3>
<p>The Topographica team are regularly making additions to the library and these additions are automatically available in the model editor. If you decide to extend any of the components, simply save the files in the same folder as the others of that type and your extension will automatically be available for use in the model editor.

<h2>The Parameters</h2>
<p>All of the components that you can use to define a Topographica model have parameters. Parameters are attributes that allow you to control the behaviour of your components. To view the parameters that a component has, right click on the component's representation in the work area. This will bring up a window with the component's name at the top and several entries underneath. You will notice that these entries vary in style, for a description of the various types of parameter and valid changes you can make to the parameters refer to Controlling simulation parameters in the User Guide. Some examples of entry methods are, sliders for real numbers or pull down menus for class selectors(described later) and enumerations. In these cases you can simply move the slider or select a different option from the menu to change the parameter's value:
<center>
<IMG WIDTH="353" HEIGHT="443" SRC="images/editorproperties.png">
</center>
<p>When you have made the necessary changes, click Ok to accept the changes and close the window, or Update just to make the changes. If you decide not to make the changes then click the close box in the top right hand corner.
<p>If you are looking at a sheet's parameters you will notice another menu under these buttons. This allows you to open the properties frame of any of the connections joined to that sheet. Simply select a connection from the list and it's frame will open underneath.

<h3>Constants</h3>
<p>The Parameters section of the User Guide also details that a parameter can be declared as a constant. This means you cannot change it once the component has been made. To ensure consistency, the model editor must create the components as soon as you make them in the editor, so these values must already be set. The editor allows you to set a sheet's constant values; density, the number of neurons per unit length or width and the bounds, defining the bounding box that defines the shape and size of a sheet. 
<p>When the canvas is in object mode(i.e. select the object item in the toolbar), there is a parameter frame embedded into the toolbar underneath the toolbar items. To set the density of future sheets of the selected type, enter the density as an integer into the box next to density. The default density is 10, you are free to set this to any number, however remember the more units the more computation time is required. Similarly, to change the bounding box of future sheets you must define two points; the bottom left and top right of the bounding box. To do this enter the 4 decimals, each separated by a space, for example, x1 y1 x2 y2. The default is -0.5 -0.5 0.5 0.5, a unit square centred around 0, you are free to decide the shape and size, however not all shapes can be joined together and again note that the size will greatly effect how long a simulation will take.

<h3>Class Selector</h3>
<p>As introduced earlier, there is a parameter type called a class selector. This is used when the field of a component is one of a selection of classes. You can choose the appropriate class by selecting it from the menu, however some of these classes have parameters of their own. The editor allows you to change these parameters. Select the option from the menu and then right click within the menu's box. A pop-up menu will allow you to open up that option's parameter frame.
