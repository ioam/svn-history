This is a pre-release version of the Topographica cortical map
simulator; please do not trust this version of the code unless you
have verified it yourself.  An updated version may be available from
topographica.org.

Copyright 2005 James A. Bednar, Yoonsuck Choe, Judah B.
De Paula, Jefferson Provost, and Joseph Reisinger.

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License version 2 as
published by the Free Software Foundation. This program is distributed
in the hope that it will be useful, but without any warranty; without
even the implied warranty of merchantability or fitness for a
particular purpose.  See the GNU General Public License for more
details, in the file COPYING.txt.


OBTAINING THE CVS VERSION OF TOPOGRAPHICA

The Topographica simulator source files are maintained using the CVS
version control system, hosted by SourceForge.net.  See
http://sourceforge.net/docman/display_doc.php?docid=14033&group_id=1
for more details on CVS at SourceForge.

Note that at any point the CVS files are likely to be somewhat out of
sync with each other and with the documentation.  In particular, the
latest revisions may not have been tested on all architectures or at
all.  However, we do try to minimize the time that the CVS version of
the simulator is broken while changes are being made.

There are two ways to get your own local copy of the CVS files,
depending on whether or not you are an official Topographica
developer.  Non-developers can check out a read-only version of the
repository, while developers can get read/write access so that they
can make changes that become a permanent part of the project
repository.  

To get started, first change to a directory to which you have write
access with sufficient space available, i.e., at least several hundred
megabytes as of 4/2005.

Then to get read-only access, log in to the CVS server using the UNIX
command:

  cvs -d :pserver:anonymous@cvs.sf.net:/cvsroot/topographica login

When a password is requested, just press return.  Then change to
wherever you want the files to be stored, and use the command:

  cvs -d :pserver:anonymous@cvs.sf.net:/cvsroot/topographica checkout topographica

The result will be a directory named "topographica" within your
current directory.

For read/write access, no login step is needed, and the checkout
command is:

  cvs -d ':ext:uname@cvs.sourceforge.net:/cvsroot/topographica' checkout topographica

where uname should be replaced with your SourceForge.net username.
You will be asked for your SourceForge.net password.

The download process make take quite a while over a slow link, due to
the sizes of the files involved, but should only take a few minutes on
a broadband connection.


BUILDING THE CVS VERSION OF TOPOGRAPHICA

The topographica directory you have now checked out includes the files
necessary to build Topographica on most platforms.  To make the build
process simpler on a variety of platforms, source code versions of the
libraries needed are included, and are created as part of the build
process.  This approach makes the initial compilation time longer and
the simulator directory larger, but it minimizes the changes necessary
for specific platforms and operating system versions.


Linux: 

To build Topographica under Linux, just type "make" from within the
topographica/ directory.  Once it seems to be doing something is a
good time to go out for dinner or a movie; the build process will take
quite some time (e.g. about twenty minutes on a 3GHz Pentium IV
machine).  If all goes well, a script named "topographica" will be
created in the topographica/ directory; you can use this to start
Topographica as described below.

UNIX:

Topographica is developed under Linux, but should work on other
versions of UNIX as well, as long as they have standard GNU tools like
make and GCC installed.  Just follow the Linux instructions, replacing
"make" with "gmake" if that's the name of GNU make on your system.

Windows:

See WIN32_INSTALL.txt.

Mac:

Topographica builds only under Mac OS X or later.  Topographica
developers have only limited access to OS X machines, and so at any
time there are likely to be some issues with the OS X version,
although we do try to minimize them.  

If you have an X server installed, you can just build Topographica as
described for Linux.  It is also possible to build Topographica using
a native (Aqua) version of Python, which looks a bit nicer, but we
have not yet documented how to do that.


RUNNING TOPOGRAPHICA

Topographica is still under very active development, and until a full
public release, is not suitable for serious use unless you are
coordinating such usage with the developers.  However, it already
includes some useful code, such as a GUI version of a SOM-based
orientation map network.  To start this code, go to your topographica/
directory, and type e.g.:

  ./topographica -g examples/gui_example.py

You should see a window appear that has similar options available as
the one in the LISSOM tutorial at:

  http://homepages.inf.ed.ac.uk/jbednar/pytutorial.html

The tutorial was written for our more polished but less flexible
simulator LISSOM, also available from http://topographica.org, but you
can follow many of the instructions in that tutorial.  As of 4/2005,
the main differences are that all plots are grayscale, there is no
orientation or ocular dominance map measurement available, the model
does not have lateral connections or LGN cells, and no trained map is
provided.


DOCUMENTATION AND FURTHER STUDY

For practical use, please wait for the full public release of
Topographica. Because of the fast pace of current development, there
is very little documentation available, but the documentation for each
file can be accessed by loading topographica/docs/index.html into your
web browser.
