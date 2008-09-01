<p><b>16 May 2008:</b> Updates since version 0.9.4
  (currently available only via <A
  HREF="../Downloads/cvs.html">SVN</A>, but to be included in the next
  release):
<center>
<table width="100%" cellpadding="5">
<tr>
<td width="50%">
<dl COMPACT>
<font size="-1">  
<dt>General improvements:</dt>
<dd>
  numerous bugfixes and performance improvements<br>
<!-- fixed a number of pychecker warnings.<BR> -->
<!-- moved current to-do items to the sf.net trackers<BR> -->
<!--  made start() method of EventProcessors be called just before the first
  execution of the simulator after the EP is added, e.g. to allow joint
  normalization across a Sheet's projections<BR> -->
  simulation can now be locked to real time<BR>
  added optional XML snapshot
  <A HREF="../Reference_Manual/topo.commands.basic-module.html#save_snapshot">saving</A> and
  <A HREF="../Reference_Manual/topo.commands.basic-module.html#load_snapshot">loading</A>
<!-- (do 'make -C external gnosis') --><BR>
  simpler and more complete support for dynamic parameters<BR>  
  updated to Python 2.5 and numpy 1.1.1.<BR>
  source code repository moved from CVS to Subversion (<A HREF="../Downloads/cvs.html">SVN</A>)<BR>
  simulation time is now a rational number<BR>
<!-- Simplified package importing API (promoting basic.py, etc.; not yet done) -->
</dd>
<dt>Command-line and batch:</dt>
<dd>
  command prompt uses <A
  HREF="http://ipython.scipy.org/">IPython</A> for better debugging, help<BR> 
  command-line options can be called explicitly, e.g.<BR>
  &nbsp;&nbsp;&nbsp;<A HREF="../Reference_Manual/topo.misc.commandline-module.html#gui">topo.misc.commandline.gui()</A> or<BR>
  &nbsp;&nbsp;&nbsp;<A HREF="../Reference_Manual/topo.misc.commandline-module.html#auto_import_commands">topo.misc.commandline.auto_import_commands()</A><BR>
  simulation name set automatically from .ty script name by default<BR>
<!--  added -p option to call Psyco JIT optimizer<BR> -->
</dd>
</font>
</dl>
</td>
<td width="50%">
<dl COMPACT>
<font size="-1">
<!--  
<dt>GUI:</dt>
<dd>
  cleaned up ParametersFrame and TaggedSlider behavior<BR>
</dd>
<dt>Plotting:</dt>
<dd>
</dd>
-->
<dt>Example scripts:</dt>
<dd>
  new example files for robotics interfacing<BR>
  &nbsp;&nbsp;&nbsp;(<A HREF="../Reference_Manual/topo.misc.playerrobot-module.html">misc/playerrobot.py</A>,
  <A HREF="../Reference_Manual/topo.misc.robotics-module.html">misc/robotics.py</A>)<br>
  new joint simulations, plots, and analysis for combined modelling of 
  position, orientation, ocular dominance, stereoscopic disparity,
  motion direction, speed, spatial frequency, and color
  (examples/lissom.ty).
  <BR>
</dd>
<dt>Component library:</dt>
<dd>
  added <A HREF="../Reference_Manual/topo.commands.analysis-module.html#decode_feature">decode_feature</A> for estimating perceived values,<br>
  &nbsp;&nbsp;&nbsp;e.g. for calculating aftereffects<BR>
  PatternGenerator for real-time camera inputs<BR>
  Pipeline OutputFns can now be constructed easily using +<BR>
<!-- &nbsp;&nbsp;&nbsp;('x=HalfRectify() ; y=Square() ; z=x+y' gives 'z==PipelineOF(output_fns=x,y)')<BR> -->
  new Output_Fn classes: 
  <?php classref('topo.outputfns.basic','PoissonSample')?>,<BR>
  &nbsp;&nbsp;&nbsp;<?php classref('topo.outputfns.homeostatic','ScalingOF')?> (for homeostatic plasticity),<BR>
  &nbsp;&nbsp;&nbsp;<?php classref('topo.outputfns.basic','AttributeTrackingOF')?> 
  (for analyzing or plotting values over time)<BR>
  allowed <?php classref('topo.sheets.lissom','LISSOM')?>
  normalization to be <A
  HREF="../Reference_Manual/topo.sheets.lissom.LISSOM-class.html#post_initialization_weights_output_fn">changed</A> after initialization<BR>
  new CompositeSheetMask, AndMask, and OrMask classes<BR>
  NumberGenerators can now be combined and modified using arithmetic expressions
<!-- (e.g. abs(2*UniformRandom()-5) is now a NumberGenerator too).--><BR>
</dd>
</font>
</dl>
</td>
</tr>
</table>
</center>


<!--  To add:
Buildbots
Simplified example file syntax
Docking
Dynamic parameters now update once per simulation time
Added OutputFnDebugger
Clean up hierarchical.ty, cfsom.ty?
PyTables HDF5 interface?
added stop_updating and restore_updating functions to OutputFn and PipelineOF to allow functions with state to freeze their state during e.g. pattern_present
Use tk8.5 for anti-aliased fonts
New functions for analyzing V1 complex cells
Optimized Trace learning rule
New code allowing for divisive and multiplicative connections
New Naka-Rushton output function (used for gain control)
Instructions for checking out Git version of repository
Added topo/misc/legacy.py
Added Jitter class
Added an example of how to generate activity movies (examples/lissom_or_movie.ty)
Replaced FixedPoint with mxnumber (or gmpy?) for speed
Added mouse model (examples/lissom_oo_or_species.ty)
Added combined (joint) plots using contour and arrow overlays
Added new preference map types (Hue, Direction, Speed...)
Added contrib dir
-->


<p><b>26 October 07:</b> Version 0.9.4 
<A target="_top" href="../Downloads/index.html">released</A>, including:

<center>
<table width="100%" cellpadding="5">
<tr>
<td width="50%">
<dl COMPACT>
<font size="-1">  
<dt>General improvements:</dt>
<dd>
  numerous bugfixes<br>
  set up <A target="_top" href="http://buildbot.topographica.org">automatic daily builds</A><br>
</dd>
<dt>Example scripts:</dt>
<dd>
  new whisker barrel cortex simulation<br>
  &nbsp;&nbsp;(using transparent Matlab wrapper)<br>
  new elastic net ocular dominance simulation<br>
  new spiking example; still needs generalizing<br>
</dd>
<dt>Command-line and batch:</dt>
<dd>
  <!-- <A target="_top" href="../User_Manual/commandline.html#option-a">-a
  option to import commands automatically<br> -->
  <A target="_top" href="../User_Manual/batch.html">batch 
  mode</A> for running multiple similar simulations<br>
  <A target="_top" href="../User_Manual/commandline.html#saving-bitmaps">saving 
  bitmaps</A> from script/command-line (for batch runs)<br>
  script/command-line <A target="_top" href="../User_Manual/commandline.html#scripting-gui">control over GUI</A><br>
  <!-- grid_layout command to simplify model diagrams<br> -->
  <!-- options for controlling plot sizing<br> -->
  added auto-import option (-a and -g) to save typing<br>
</dd>
</font>
</dl>
</td>
<td width="50%">
<dl COMPACT>
<font size="-1">
<dt>GUI:</dt>
<dd>
  greatly simplified adding GUI code <!--<A target="_top" href="../Developer_Manual/gui.html#programming-tkgui">adding GUI code</A>--><br>
  <!--  added GUI tests<br> -->
  <!--  added optional pretty-printing for parameter names in GUI<br> -->
  added progress bars, scroll bars, window icons<br>
  new Step button on console
  <!-- changed -g to launch the GUI where it is specified, to allow more control<br> -->
  <!-- added categories for plots to simplify GUI<br> -->
</dd>
<dt>Plotting:</dt>
<dd>
  <A target="_top" href="../User_Manual/plotting.html#rfplots">reverse-correlation RF mapping</A><br>
  <A target="_top" href="../User_Manual/commandline.html#3d-plotting">3D 
  wireframe plotting</A> (in right-click menu)<br>
  gradient plots, histogram plots (in right-click menu)<br>
  <A target="_top" href="../User_Manual/plotting.html#measuring-preference-maps">simplified
  bitmap plotting</A> (removed template classes)<br>
  GUI plots can be saved as PNG or EPS (right-click menu)<br>
  automatic collection of plots for animations (see ./topographica examples/lissom_or_movie.ty)<br>
</dd>
<dt>Component library:</dt>
<dd>
  new
  <A HREF="../Reference_Manual/topo.coordmapperfns-module.html">
  coordmapperfns</A> (Grid, Pipeline, Polar/Cartesian)<br>
  <!-- OutputFnDebugger for keeping track of statistics<br> -->
</dd>
</font>
</dl>
</td>
</tr>
</table>
</center>

Screenshots: 
<A target="_top" href="../images/071018_plotting1_ubuntu.png">plotting 1</A>, 
<A target="_top" href="../images/071018_plotting2_ubuntu.png">plotting 2</A>, 
<A target="_top" href="../images/071018_modeleditor_ubuntu.png">model editor</A>.
<br><br>

<p><b>23 April 07:</b> Version 0.9.3 
<A target="_top" href="../Downloads/index.html">released</A>, including:

<center>
<table width="100%" cellpadding="5">
<tr>
<td width="50%">
<dl COMPACT>
<font size="-1">  
<dt>General improvements:</dt>
<dd>
  numerous bugfixes<br>
  significant optimizations (~5 times faster)<br>
  <!-- (about 5 times faster than 0.9.2 for most scripts, with more improvements to come)<br>  -->
  compressed snapshots (1/3 as large)<br>
  <!-- more comprehensive test suite checking both speed and functionality<br> -->
  much-improved reference manual<br>
  <!-- arrays based on Numpy rather than Numeric<br> -->
</dd>
<dt>Component library:</dt>
<dd>
  adding noise to any calculation<br>
  lesioning units and non-rectangular sheet shapes (see PatternCombine)<br>
  basic auditory pattern generation<br>
<!--  greatly simplified convolutions<br>--> <!-- SharedWeightCFProjection -->
  greatly simplified SOM support<br> <!-- now can be mixed and matched with any other components<br> -->
  more dynamic parameters (such as ExponentialDecay)<br> 
  flexible mapping of ConnectionField centers between sheets<br>
</dd>
<dt>Example scripts:</dt>
<dd>
  examples that more closely match published simulations<br>
  new simulations for face processing and for
  self-organization from natural images<br>
</dd>
</font>
</dl>
</td>
<td width="50%">
<dl COMPACT>
<font size="-1">
<dt>GUI:</dt>
<dd>
  Better OS X and Windows support<br>
  progress reporting for map measurement<br>
  dynamic display of coordinates in plots<br>
  stop button to interrupt training safely<br>
  ability to plot and analyze during training<br>
  right-click menu for analysis of bitmap plots<br>
  saving current simulation as an editable .ty script<br>
</dd>
<dt>Command-line and batch:</dt>
<dd>
<!--  more-informative command prompt<br> -->
  site-specific commands in ~/.topographicarc<br>
  simple functions for doing optimization<br>
<!--  saving of plot data with snapshots<br> -->
</dd>
<dt>Plotting:</dt>
<dd>
  spatial frequency map plots<br>
  tuning curve plots<br>
  FFT transforms (in right-click menu)<br>
</dd>
</font>
</dl>
</td>
</tr>
</table>
</center>

Screenshots: 
<A target="_top" href="../images/topographica-0.9.3_ubuntu.png">Plotting</A>, 
<A target="_top" href="../images/topographica-0.9.3_modeleditor_ubuntu.png">Model editor</A>.
<br><br>


<p><b>29 November 06:</b> There will be a short talk on Topographica
at the <A target="_top" href="http://us.pycon.org/TX2007/">PyCon 2007</A>
convention, February 23-25, 2007.
<br><br>

<p><b>22 November 06:</b> Version 0.9.2
<A target="_top" href="../Downloads/index.html">released</A>, including
numerous bugfixes (e.g. to support GCC 4.1.x compilers),
much more complete user manual,
more useful reference manual,
more sample models,
flexible joint normalization across Projections,
arbitrary control of mapping CF centers (see CoordinateMapperFn),
Composite and Selector patterns to allow flexible combinations of input patterns,
homeostatic learning and output functions,
sigmoid and generalized logistic output functions,
and a new disparity map example (including a
random dot stereogram input pattern).
<!-- Choice class to select randomly from a list of choices -->
<br><br>

<p><b>02 November 06:</b> Some users have reported problems when using
optimized code on systems with the most recent GCC 4.1.x C/C++
compilers.  We have added a patch to the included weave
inline-compilation package that should fix the problem, currently
available only on the most recent CVS version of Topographica.
Affected users may need to do a <A target="_top"
href="../Downloads/cvs.html">CVS</A> update, then "make -C external
weave-uninstall ; make".  These changes will be included in the next
official release.
<br><br>

<p><b>23 July 06:</b> Version 0.9.1
<A target="_top" href="../Downloads/index.html">released</A>.
This is a bugfix release only, upgrading the included Tcl/Tk package
to correct a syntax error in its configure script, which had
been preventing compilation on platforms using bash 3.1 (such as
Ubuntu 6.06).  There is no benefit to updating if 0.9.0 already runs
on your platform.
<br><br>

<p><b>07 June 06:</b> Version 0.9.0
<A target="_top" href="../Downloads/index.html">released</A>, including 
numerous bugfixes, 
context-sensitive (balloon) help for nearly every parameter and control,
full Windows support (<A target="_top" href="../images/060607_topographica_win_screenshot.png">screenshot</A>),
full Mac OS X support,
downloadable installation files,
significant performance increases (7X faster on the main example scripts, with more
speedups to come),
faster startup,
better memory management,
simpler programming interface,
improved state saving (e.g. no longer requiring the original script),
independently controllable random number streams,
plot window histories,
more library components (e.g. Oja rule, CPCA, covariance),
<!-- plotting in Sheet coordinates, -->
<!-- better plot size handling, -->
<!-- command history buffer, -->
prototype spiking neuron support, and
much-improved <A target="_top" href="../User_Manual/modeleditor.html">model editor</A>.

<p><b>15 May 06:</b> New book <A target="_top"
HREF="http://computationalmaps.org"><i>Computational Maps in the
Visual Cortex</i></A> available, including background on modeling
computational maps, a review of visual cortex models, and <A
target="_top" HREF="http://computationalmaps.org/docs/chapter5.pdf">an
extended set of examples of the types of models supported by
Topographica</a>.
<br><br>

<p><b>20 February 06:</b> Version 0.8.2 released, including numerous
bugfixes, 
circular receptive fields,
shared-weight projections,
<A TARGET="_top" href="../Tutorials/lissom_oo_or.html">tutorial with ON/OFF LGN model</A>,
<A TARGET="_top" href="../Tutorials/som_retinotopy.html">SOM retinotopy tutorial</A>,
Euclidean-distance-based response and learning functions,
density-independent SOM parameters,
<A TARGET="_top" href="../Downloads/cvs.html#osx">Mac OS X instructions</A>,
<A TARGET="_top" href="../Developer_Manual/index.html">developer manual</A>,
<A TARGET="_top" href="../User_Manual/index.html">partial user manual</A>,
much-improved 
<A target="_top" href="../images/060220_model_editor_screen_shot.png">model editor</A>,
<A TARGET="_top" href="../User_Manual/commandline.html#pylab">generic Matlab-style plotting</A>,
topographic grid plotting,
RGB plots,
user-controllable plot sorting,
plot color keys,
<!-- Normally distributed random PatternGenerator, -->
and progress reports during learning.  See the 
<A target="_top" href="../images/060220_topographica_screen_shot.png">Linux screenshot</A>.
<br><br>

<p><b>22 December 05:</b> Version 0.8.1 released, including numerous
bugfixes, more flexible plotting (including weight colorization),
user-controllable optimization, properties panels, more-useful
<A TARGET="_top" href="../Reference_Manual/index.html">reference manual</A>,
image input patterns, and a prototype graphical
model editor.  <!-- Plus SOMs with selectable Projections -->
<br><br>

<p><b>8 November 05:</b> New site launched with Topographica version
0.8.0, including a new
 <a target="_top" href="../Tutorials/lissom_or.html">LISSOM tutorial</a>.
(<a target="_top" href="../images/051107_topographica_screen_shot_white.png">Linux screenshot</a>).
