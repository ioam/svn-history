<H3><A NAME="build-on-cygwin">Building Topographica on Cygwin</A></H3>

<P>Some kind of introduction.


Could host a "local directory" with the right packages, which
people could use to install a cygwin setup that would build
topographica without any extra work. Unless there's some
way to pass a list of packages into cygwin's setup.exe.

http://cygwin.com/faq/faq.setup.html#faq.setup.cli



<H4>Notes</H4>

** Notes From start of March 2007 **

(i.e. pre-March copy of Topographica, cygwin, etc)


Build of all default targets completed without errors with the
changes listed below. Only major change is for python. 
make tests gives no error, simulations appear to work
(with and without weave), and the plots seem ok (except for
matplotlib ones, which give a file not found error).

* To see the GUI, have to call mainloop. Otherwise nothing appears.

<a href="cygwin_packages">Cygwin packages</a> I used





TCL/Tk
==========

http://wiki.tcl.tk/11891

export CC="gcc -mno-cygwin"

cd win/
./configure --prefix=/home/chris/topographica/
make
make install

cd win/
./configure --prefix=/home/chris/topographica
make
make install


Python
==========

http://www.tishler.net/jason/software/python/python-2.4.README

(1) rebaseall to solve fork problem
cmd prompt:
/cygwin/bin/ash.exe
rebaseall

did that make everything really slow?
Same problem as...?
http://cygwin.com/ml/cygwin/2007-02/msg00404.html
(except I don't have virus checker)
http://lists-archives.org/cygwin/24041-slow-compile-issue-with-cygwin-make-since-v1-5-17.html
http://article.gmane.org/gmane.os.cygwin/84307/match=slow+compile+cygwin+make
http://thread.gmane.org/gmane.os.cygwin/84257/focus=84307

(2) Replace Python-2.4.4.tgz with cygwin's own python sources!

(3) 
cd python-2.4.3-1
./configure --prefix=/home/chris/topographica
make
make install

./configure --prefix=/home/chris/topographica LDFLAGS=-rpath,/home/chris/topographica/lib ; make; make instal

# make executables user writable to guarantee strip succeeds
find $InstallPrefix -name '*.exe' -o -name '*.dll' | xargs chmod u+w

# strip executables
find $InstallPrefix -name '*.exe' -o -name '*.dll' | xargs strip 


pil
==========

did it compile?


numpy
==========
current svn version works with no changes
 

pmw
==========

no problems


fixedpoint
==========

no problems


weave
==========

no problems



matplotlib
==========


chris@ghost ~/topographica/lib
$ ln -s libtk84.a libtk8.4.a

chris@ghost ~/topographica/lib
$ ln -s libtcl84.a libtcl8.4.a


gnosis
===========

no problems


pychecker
===========

no problems

common
===========

no problems


pylint
===========
no problems


epydoc
===========
no problems

docutils
===========
no problems




