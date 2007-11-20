<?php
print '<table width="100%" cellpadding="5"><tr><td bgcolor="'.$banner_bg_color.'">'
?>
<blockquote>
<i>
<b>News:</b>

<p><b>20 November 07:</b> Updates since version 0.9.4:

<center>
<table width="100%" cellpadding="5">
<tr>
<td width="50%">
<dl COMPACT>
<font size="-1">  
<dt>General improvements:</dt>
<dd>
  numerous bugfixes<br>
  fixed a number of pychecker warnings.<BR>
  moved current to-do items to the sf.net trackers<BR>
  
  
<!--  made start() method of EventProcessors be called just before the first
  execution of the simulator after the EP is added, e.g. to allow joint
  normalization across a Sheet's projections<BR> -->
  simulation can now be locked to real time<BR>
  added optional XML snapshot saving and loading (do 'make -C external gnosis')<BR>
  
</dd>
<dt>Example scripts:</dt>
<dd>
  new example files for robotics interfacing (misc/playerrobot.py, misc/robotics.py)<BR>
</dd>
<dt>Command-line and batch:</dt>
<dd>
  added <A HREF="http://ipython.scipy.org">
  IPython</A> (do 'make -C external ipython') for better command prompt, debugging, help<BR>
  simplified commandline argument processing; now can do
  topo.commandline.gui() or topo.commandline.auto_import_commands()
  after Topographica has started.<BR>
  simulation name set automatically from .ty script name by default<BR>
  
</dd>
</font>
</dl>
</td>
<td width="50%">
<dl COMPACT>
<font size="-1">
<dt>GUI:</dt>
<dd>
  cleaned up ParametersFrame and TaggedSlider behavior<BR>
</dd>
<dt>Plotting:</dt>
<dd>
</dd>
<dt>Component library:</dt>
<dd>
  added code for estimating perceived values
  (<A HREF="../Reference_Manual/topo.commands.analysis-module.html#decode_feature">commands.analysis.decode_feature</A>),<br>
  &nbsp;&nbsp;e.g. for calculating aftereffects<BR>
  Image class now allows camera inputs<BR>
  <A HREF="../Reference_Manual/topo.outputfns.basic.PoissonSample-class.html">PoissonSample</A>
  OutputFn class<BR>
  Pipeline OutputFns can now be constructed easily using +<BR>
  &nbsp;&nbsp;('x=HalfRectify() ; y=Square() ; z=x+y' gives 'z==PipelineOF(output_fns=x,y)')<BR>
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