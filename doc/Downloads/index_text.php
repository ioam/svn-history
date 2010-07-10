<H2><A NAME="installing-topographica">Installing Topographica</A></H2>

<P>Topographica is based on a suite of commonly used tools for
scientific software development, including Python, NumPy, and
PIL. This page describes how to install Topographica and a suitable
scientific Python environment.

<P>If you already have a Python environment that you wish to use for
Topographica, or if your platform is not listed below, instead follow
our instructions for <A HREF="existingpython.html">installing Topographica
into an existing Python environment</A>.

<P>Developers, as well as users who wish to access the most recent
changes or edit the version-controlled source code, should instead
follow the <A HREF="../Developer_Manual/installation.html">developers'
installation guide</A>.

<!-- CEBALERT: put this somewhere
<P>Before starting, note that if you want to run large simulations
(requiring more than about 3 GB of memory), you should install
Topographica on a 64-bit platform.
-->

<!-- CEBALERT: will need to update filenames and links. Note that
SF.net allows you to have files to present to users based on their
OS. -->
<H3><A NAME="win">Windows</A></H3>

<P>Install the <A HREF="http://www.pythonxy.com/">Python(x,y)</A>
or <A HREF="http://www.enthought.com/products/getepd.php">EPD</A>
scientific Python environment, then run the
self-installing <a href="https://sourceforge.net/projects/topographica/files/">exe</a>
for Windows. Once complete, proceed to the
<A HREF="#postinstall">After Installation</A> section below.

<H3><A NAME="mac">Mac</H3>

<!-- CEBALERT: discuss people for whom EPD is free? provide link to
30-day trial?! -->

<P>Install
the <A HREF="http://www.enthought.com/products/getepd.php">EPD</A>
scientific Python environment, then run the
Topographica <a href="http://sourceforge.net/projects/topographica/files/">app</a>
for Mac. Once complete, proceed to the
<A HREF="#postinstall">After Installation</A> section below.

<H3><A NAME="lin">Linux</A></H3>

<P>We provide packages for Debian-based systems (e.g. Ubuntu), and
RPM-based systems (e.g. Fedora Core). Installing one of these packages
with your package manager will install both the necessary Python
environment and Topographica itself. Users of linux systems that
cannot make use of either of these packaging systems should instead
follow our instructions for <A HREF="existingpython.html">installing
Topographica into an existing Python environment</A>.

<P><em><A NAME="deb">deb</A></em>: Download the
appropriate <A HREF="http://sourceforge.net/projects/topographica/files/">deb</A>
file and then install it with a command like
<code>sudo dpkg -i topographica.deb</code>; alternatively,
<A HREF="https://launchpad.net/~topographica-developers/+archive/topographica">add the Topographica PPA</A> to your software sources and
then run
<code>sudo apt-get install topographica</code>, which will allow
Topographica and its dependencies to be updated automatically for
future releases.

<P><em><A NAME="rpm">rpm</A></em>: Download the
<A HREF="http://sourceforge.net/projects/topographica/files/">rpm</A>
file and then issue a command such as <code>sudo rpm -i
topographica.rpm</code> to install it.

<P>Once the package has been installed, you can proceed to
the <A HREF="#postinstall">After Installation</A> section below.

<H3><A NAME="postinstall">After installation</A></H3>

<P>Linux and Mac users can run <code>topographica -g</code> from a
terminal to start Topographica. Windows users can double click on the
Topographica icon on the desktop.

<P>Running Topographica interactively is described in detail in
the <A HREF="../User_Manual/scripts.html">User Manual</A>. If you want
to get straight into working with a full network, a good way to begin
is by working through
the <A HREF="../Tutorials/som_retinotopy.html">SOM</A>
or <A HREF="../Tutorials/lissom_oo_or.html">LISSOM</A> tutorials.

<P> Have fun with Topographica, and be sure to subscribe to
the <A HREF="https://lists.sourceforge.net/lists/listinfo/topographica-announce">topographica-announce</A>
mailing list to hear about future updates!
