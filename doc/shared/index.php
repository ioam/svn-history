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

<p><b>23 April 2007:</b> Version 0.9.3 to be
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

<P>Binaries will be available soon; in the meantime, this release 
is available via <A HREF="../Downloads/cvs.html">cvs</a>.
  
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
