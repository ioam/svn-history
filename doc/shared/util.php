<?php

############################################################################
#       find current folder name
############################################################################
function folder_name() {

  $fname = $_SERVER[PHP_SELF];
  $fname = preg_replace('|/../shared/index\.php|',"",$fname);
  $fname = preg_replace('|../|',"/",$fname);

  return $fname;
}

############################################################################
#       find current folder name, ready for displaying to the screen
############################################################################
function bare_folder_name() {

  $fname = $_SERVER[PHP_SELF];
  $fname = preg_replace('|/../shared/index\.php|',"",$fname);
  $fname = preg_replace('|../|',"",$fname);
  $fname = preg_replace('|_|'," ",$fname);

  return $fname;
}

############################################################################
#       banner
############################################################################
function banner($fname) {

  include('config.php');

  if ($fname == "/Home")  {
	
	# main page banner
	print '
<table width="100%" cellpadding="20"><tr><td bgcolor="'.$banner_bg_color.'">
<CENTER>
<IMG src="../images/'.$logofile.'" align="middle"
     width="497" height="138" border="0" alt="Topographica logo">
<!-- &nbsp;
<IMG src="../images/'.$logotext.'" align="middle"
     width="420" height="113" border="3" alt="Topographica"> -->
</CENTER>
</td></tr></table>
';

  } else {

	# subdirectory page banner
	$pwd = bare_folder_name();

	print '
<table width="100%" cellpadding="20"><tr><td bgcolor="'.$banner_bg_color.'">
<CENTER>
<table border=0 width="400" height="102" background="../images/topo-subbanner-bg.png"><tr><td><center>
<font size="+3" face="serif" font-style="italic"><i>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'.$pwd.'</i></font></center>
</td></tr></table>
</CENTER>
</td></tr></table>
';
  }

}

############################################################################
#        menu 
############################################################################
function menu_side($fname) {

	include('config.php');

	# menu name and link
	$menu_items = array("Home" => "../Home/index.html", 
		"Team Members" => "../Team_Members/index.html",
		"Tutorial" => "../Tutorial/index.html",
		"User Manual" => "../User_Manual/index.html",
		"Reference Manual" => "../Reference_Manual/index.html",
		"Downloads" => "http://sourceforge.net/project/showfiles.php?group_id=53602",
		"Lists, Forums" => "../Lists,_Forums/index.html",
		"Plans" => "../Plans/index.html",
		);

	# 1. black border (using table)
	print '<table border="0" width="140"><tr><td bgcolor="'.$frame_color.'" valign="top">';
	
	# 2. main menu table
	print '  <table border="0" width="100%" valign="top" cellspacing="3" cellpadding="8">';
		
	# 2.1 menu items
	foreach ($menu_items as $key => $link) {
		if ($link == "Home") {
			$link = "../index.html";
		}
		print '    <tr><td bgcolor="'.$button_color.'"><a href="'.$link.'" class="button"><font face="sans-serif"><b>'.$key.'</b></font></a></td></tr>';
	}
	print '  </table>';
	print '</table>';
}

?>
