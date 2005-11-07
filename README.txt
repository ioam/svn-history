This version of the Topographica cortical map simulator is still under
active development.  An updated version may be available from
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

Before you start, make sure that you have a copy of Topographica in
your home directory or some other directory in which you can write
files, and that you have at least 500MB available.


BUILDING DOCUMENTATION

To read more about Topographica before trying to build it, you can
build the documentation (apart from the Reference Manual) separately
from compiling Topographica itself.  If PHP4 is installed on your
system (as in most Linux distributions), just change to the
topographica directory and type "make doc", then load doc/index.html
into your web browser.  If there are any problems generating the local
copy, you can instead use the web-based documentation at
www.topographica.org.


BUILDING TOPOGRAPHICA

The topographica CVS directory includes the files necessary to build
Topographica from source code on most platforms.  All non-standard
external libraries are included and for most platforms are built from
source.  This approach makes the initial compilation time longer and
the simulator directory larger, but it minimizes the changes necessary
for specific platforms and operating system versions.

Linux: 

To build Topographica under Linux, just type "make" from within the
topographica/ directory.  The build process will take a while to
complete (e.g. about 5-10 minutes on a 1.5GHz Pentium IV
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


USING TOPOGRAPHICA

See doc/Tutorial/index.html for examples of getting started with
Topographica, and doc/index.html for all of the documentation.  You
can also get online help from the Topographica command line using
help(), or from the shell command line using "./bin/pydoc some-text".
