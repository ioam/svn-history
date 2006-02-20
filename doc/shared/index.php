<HTML><HEAD>
<META HTTP-EQUIV="content-type" CONTENT="text/html; charset=ISO-8859-1">
<LINK rel="stylesheet" type="text/css" media="screen" href="../shared/topo.css">
<TITLE>The Topographica Simulator</TITLE>
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
	if ($fname == "/Home") {
		print '
<table width="100%" cellpadding="5"><tr><td bgcolor="'.$banner_bg_color.'">
<blockquote>
<blockquote>
<i>
<b>News:</b>

<p><b>14 February 06:</b> Version 0.8.2 released, including numerous
bugfixes, 
circular receptive fields,
shared-weight projections,
<A TARGET="_top" href="../Tutorials/lissom_oo_or.html">tutorial with ON/OFF LGN model</A>,
<A TARGET="_top" href="../Tutorials/som_retinotopy.html">SOM retinotopy tutorial</A>,
Euclidean-distance-based response and learning functions,
density-independent SOM parameters,
<A TARGET="_top" href="../Downloads/index.html#osx">Mac OS X instructions</A>,
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





<p><b>22 December 05:</b> Version 0.8.1 released, including numerous
bugfixes, more flexible plotting (including weight colorization),
user-controllable optimization, properties panels, more-useful
<A TARGET="_top" href="../Reference_Manual/index.html">reference manual</A>,
image input patterns, and a prototype graphical
model editor.  <!-- Plus SOMs with selectable Projections -->

<p><b>8 November 05:</b> New site launched with Topographica version
0.8.0, including a new
 <a target="_top" href="../Tutorials/lissom_or.html">LISSOM tutorial</a>.
(<a target="_top" href="../images/051107_topographica_screen_shot_white.png">Linux screenshot</a>).

</i>
</blockquote>
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
