<HTML><HEAD>
<META HTTP-EQUIV="content-type" CONTENT="text/html; charset=ISO-8859-1">
<LINK rel="stylesheet" type="text/css" media="screen" href="../shared/topo.css">
<TITLE>The Topographica Neural Map Simulator</TITLE>
</HEAD>
<?php

	include('../shared/config.php');

	# Hack: expects name of textfile to be passed in through the
	# arbitrary php.ini option 'sendmail_from'.
	$textfile = ini_get('sendmail_from');
        global $textfile;

        global $body_bg_color;
	print '<BODY bgcolor="'.$body_bg_color.'">';

	# 1. load the utility routines
        require_once('../shared/util.php');

	# 2. get current folder name
        $fname = folder_name();

	# 3. generate the banner

	print "<blockquote>\n";

	banner($fname);

	# 4. news box (need to replace with something clean)
	if ($fname == "/Home" && $textfile == "index_text.php") {
		print '
<table width="100%" cellpadding="5"><tr><td bgcolor="'.$banner_bg_color.'">
<blockquote>
<i>
<b>News:</b>



<p><b>8 Oct 2007:</b> Version 0.9.4 nearly ready for 
<A target="_top" href="../Downloads/index.html">release</A>, including:

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
<dt>Component library:</dt>
<dd>
  new
  <A HREF="../Reference_Manual/topo.coordmapperfns-module.html">
  coordmapperfns</A> (Grid, Pipeline, Polar/Cartesian)<br>
  <!-- OutputFnDebugger for keeping track of statistics<br> -->
</dd>
<dt>Example scripts:</dt>
<dd>
  new whisker barrel cortex simulation (lissom_whisker_barrels.ty)<br>
  (also works as example of calling Matlab code transparently via mlabwrap)<br>
  new elastic net ocular dominance simulation<br>
  new spiking example; still needs generalizing<br>
</dd>
</font>
</dl>
</td>
<td width="50%">
<dl COMPACT>
<font size="-1">
<dt>GUI:</dt>
<dd>
  greatly simplified adding GUI code<br>
  <!--  added GUI tests<br> -->
  <!--  added optional pretty-printing for parameter names in GUI<br> -->
  added progress bars, scroll bars, window icons<br>
  new Step button on console
  <!-- changed -g to launch the GUI where it is specified, to allow more control<br> -->
  <!-- added categories for plots to simplify GUI<br> -->
</dd>
<dt>Command-line and batch:</dt>
<dd>
  <A target="_top" href="../User_Manual/commandline.html#saving-bitmaps">saving 
  bitmaps</A> from script/command-line (for batch runs)<br>
  script/command-line <A target="_top" href="../User_Manual/commandline.html#scripting-gui">control over GUI</A><br>
  <!-- grid_layout command to simplify model diagrams<br> -->
</dd>
<dt>Plotting:</dt>
<dd>
  reverse-correlation RF mapping<br>
  <A target="_top" href="../User_Manual/commandline.html#3d-plotting">3D 
  wireframe plotting</A> (in right-click menu)<br>
  gradient plots, histogram plots (in right-click menu)<br>
  <A target="_top" href="../User_Manual/plotting.html#measuring-preference-maps">simplified
  bitmap plotting</A> (removed template classes)<br>
</dd>
</font>
</dl>
</td>
</tr>
</table>
</center>

<P>Screenshots: 
<A target="_top" href="../images/topographica-0.9.3_ubuntu.png">Plotting</A>, 
<A target="_top" href="../images/topographica-0.9.3_modeleditor_ubuntu.png">Model editor</A>.

<p><A target="_top" href="../Home/oldnews.html"><i>Older news</i></A>
</i>


</blockquote>
</td></tr></table>';
	}

	# 5. main text
	print '<table border="0" cellpadding="10" width="100%"><tr><td valign="top" bgcolor="'.$menu_bg_color.'" width="145">';

	# 5.2 menu column (right)
	menu_side($fname);

	# separator
	print '</td><td valign="top" bgcolor="'.$banner_bg_color.'">';
	
	# 5.1 main text column (left)
	include('..'.$fname.'/'.$textfile);

	# close table
	print '</td></tr></table>';

	# 6. trailer
	include('../shared/trailer.php');

?>

</BODY>
</HTML>
