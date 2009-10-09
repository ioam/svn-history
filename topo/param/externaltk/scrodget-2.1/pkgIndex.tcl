# Tcl package index file, version 1.0
# This file is generated by the "pkg_mkIndex" command
# and sourced either when an application starts up or
# by a "package unknown" script.  It invokes the
# "package ifneeded" command to set up package-related
# information so that packages will be loaded automatically
# in response to "package require" commands.  When this
# script is sourced, the variable $dir must contain the
# full path name of this file's directory.

set _version 2.1


 # Note that version 2.1 is just scrodget.tcl - ver 2.0.2
 #  plus
 # this pkIndex.tcl performing some namespace manipulation
 #  in order to enable tile support.
 

package ifneeded scrodget $_version "
        [list source [file join $dir scrodget.tcl]]
         # redefine version
        package forget scrodget
        package provide scrodget $_version
"


package ifneeded ttk::scrodget $_version  "
    package require tile
    namespace eval ttk {
        namespace eval scrodget {
            namespace import ::ttk::scrollbar
        }
         # force re-sourcing scrodget in ::ttk namespace
        package forget scrodget
        [list source [file join $dir scrodget.tcl]]
        package forget  scrodget
        package provide scrodget $_version

        namespace export scrodget
        package provide ttk::scrodget $_version
    }
"

