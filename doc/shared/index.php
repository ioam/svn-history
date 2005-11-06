<HTML><HEAD>
<META HTTP-EQUIV="content-type" CONTENT="text/html; charset=ISO-8859-1">
<LINK rel="stylesheet" type="text/css" media="screen" href="../shared/topo.css">
<TITLE>The Topographica Simulator</TITLE>
<META  NAME="keywords" CONTENT="Topographica, neural network simulator">
<META  NAME="description" CONTENT="Home page for the Topographica brain region simulator.">
</HEAD>
<?php

	include('../shared/config.php');

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
<b>News: (20 April 05)</b> Pre-release (development) version of Topographica 
 <a target="_top" href="#releases">available via CVS</a>.
(<a target="_top" href="http://www.cs.utexas.edu/users/nn/web-pubs/lissom/screenshots/050423_Topographica_linuxscreenshot.png">Linux screenshot</a>)
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
	include('text.php');

	# close table
	print '</td></tr></table>';

	# 6. trailer
	include('../shared/trailer.php');

?>

</BODY>
</HTML>
