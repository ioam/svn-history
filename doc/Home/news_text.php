<?php
print '<table width="100%" cellpadding="5"><tr><td bgcolor="'.$banner_bg_color.'">'
?>
<blockquote>
<i>
<b>News:</b>

<p><b>28 January 2008:</b> Updates since version 0.9.4
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
  simpler and more complete support for dynamic parameter values<BR>  
  updated to Python 2.5<BR>
  source code repository moved from CVS to Subversion (<A HREF="../Downloads/cvs.html">SVN</A>)<BR>
<!-- Simplified package importing API (promoting basic.py, etc.; not yet done) -->
</dd>
<dt>Command-line and batch:</dt>
<dd>
  command prompt now based on <A
  HREF="http://ipython.scipy.org/">IPython</A> for better command prompt, debugging, help<BR> 
  simplified commandline argument processing; now can do
  <A HREF="../Reference_Manual/topo.misc.commandline-module.html#gui">topo.misc.commandline.gui()</A><br>
  &nbsp;&nbsp;&nbsp;or
  <A HREF="../Reference_Manual/topo.misc.commandline-module.html#auto_import_commands">topo.misc.commandline.auto_import_commands()</A>
  after Topographica has started.<BR>
  simulation name set automatically from .ty script name by default<BR>
  
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
  new example files for robotics interfacing
  (<A HREF="../Reference_Manual/topo.misc.playerrobot-module.html">misc/playerrobot.py</A>,
  <A HREF="../Reference_Manual/topo.misc.robotics-module.html">misc/robotics.py</A>)<br>
</dd>
<dt>Component library:</dt>
<dd>
  added code for estimating perceived values
  (<A HREF="../Reference_Manual/topo.commands.analysis-module.html#decode_feature">commands.analysis.decode_feature</A>),<br>
  &nbsp;&nbsp;&nbsp;e.g. for calculating aftereffects<BR>
  PatternGenerator for real-time camera inputs<BR>
  Pipeline OutputFns can now be constructed easily using +<BR>
<!-- &nbsp;&nbsp;&nbsp;('x=HalfRectify() ; y=Square() ; z=x+y' gives 'z==PipelineOF(output_fns=x,y)')<BR> -->
  new Output_Fn classes: 
  <?php classref('topo.outputfns.basic','PoissonSample')?>,
  <?php classref('topo.outputfns.homeostatic','ScalingOF')?> (for homeostatic plasticity),<BR>
  &nbsp;&nbsp;&nbsp;<?php classref('topo.outputfns.basic','AttributeTrackingOF')?> 
  (for analyzing or plotting values over time)<BR>
  added post_initialization_weights_output_fn to
  <?php classref('topo.sheets.lissom','LISSOM')?>,  to allow
  normalization to<BR>
  &nbsp;&nbsp;&nbsp;be turned off or changed after initialization<BR>
  new CompositeSheetMask, AndMask, and OrMask classes<BR>
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

<p><A target="_top" href="../Home/oldnews.html"><i>Older news</i></A>
</i>

</blockquote>
</td></tr></table>