Topographica is a general-purpose neural simulator focusing on
topographic maps.  This version of the simulator is still under active
development; an updated version may be available from
topographica.org.  Subsequent versions are not guaranteed to be able
to load files saved from this version, and scripts developed using
this version are likely to need modification when subsequent versions
are released.

The Topographica software code and documentation are copyright
2005-2007 James A. Bednar, Christopher Ball, Christopher Palmer,
Yoonsuck Choe, Julien Ciroux, Judah B. De Paula, Judith Law, Alan
Lindsay, Louise Mathews, Jefferson Provost, Veldri Kurniawan, Tikesh
Ramtohul, Lewis Ng, Ruaidhri Primrose, Foivos Demertzis, Roger Zhao,
and Yiu Fai Sit.

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License version 2 as
published by the Free Software Foundation. This program is distributed
in the hope that it will be useful, but without any warranty; without
even the implied warranty of merchantability or fitness for a
particular purpose.  See the GNU General Public License for more
details, in the file COPYING.txt.

Before you start, make sure that you have a copy of Topographica in a
directory where you have at least 500MB of disk space available.


BUILDING DOCUMENTATION

To read more about Topographica before trying to build it, you can
build the documentation separately from compiling Topographica itself.
If PHP4, m4, and fig2dev are installed on your system (as in most
Linux distributions), just change to the topographica directory and
type "make doc reference-manual", then load doc/index.html
into your web browser.  If there are any problems generating the local
copy, you can instead use the web-based documentation at
www.topographica.org.  (The doc/ directory is just a copy of the
www.topographica.org site, although the web site will not necessarily
match this particular copy of Topographica.)


BUILDING TOPOGRAPHICA

The topographica CVS directory includes the files necessary to build
Topographica from source code on most platforms.  All non-standard
external libraries are included and for most platforms are built from
source.  This approach makes the initial compilation time longer and
the simulator directory larger, but it minimizes the changes necessary
for specific platforms and operating system versions.

For specific instructions on building Topographica on each platform,
see doc/Downloads/index.html.  There may also be additional
platform-specific information in doc/Downloads/<platform>.html.  If
you haven't compiled the documentation, for each <file>.html you can
simply read the corresponding source file <file>_text.php in a text
editor. 


USING TOPOGRAPHICA

See doc/Tutorials/index.html for examples of getting started with
Topographica, and doc/index.html for all of the documentation.  You
can also get online help from the Topographica command line using
help(), or from the shell command line using "./bin/pydoc some-text".
