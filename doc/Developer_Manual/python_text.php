<H1>How to write code in Python</H1>

<P>If you are familiar with other programming languages, but not
Python, the best place to start is to run the Python tutorial on the
www.python.org web site.  On the first pass, don't try to memorize
anything, just try to get a feel for the overall syntax and workings
of Python.  Then try looking at the Topographica code.  After working
with Topographica a while, it is then a good idea to revisit the
Python tutorial and go over it in more detail, trying to figure
everything out and remember it now that the basic concepts are there.

<P>For those with experience with functional programming languages
like ML, Haskell, Scheme, or Lisp, you will be pleased to find
features such as map, apply, reduce, filter, zip, and list
comprehensions.  For those who aren't familiar with any of those, it
is very important to study the "Functional Programming Tools" and
"List Comprehensions" sections of the tutorial, because we often use
those features to write concise functions that may be hard to
understand at first glance.  Lisp programmers should probably check
out <A HREF="http://www.norvig.com/python-lisp.html">Python for Lisp
Programmers</A> for details of differences.

<P>For those with experience in Java or C++, a good (opinionated)
introduction is <A
HREF="http://dirtsimple.org/2004/12/python-is-not-java.html">Python is
not Java</A>, and the <A
HREF="http://www.ferg.org/projects/python_java_side-by-side.html">Python
and Java Side-by-side comparison</A> may also be useful.


<H1>Python coding conventions</H1>

<P>By default, the project uses the standard set of <A
HREF="http://www.python.org/peps/pep-0008.html">Python coding
conventions</A> written by Guido van Rossum, Python's author.

<P>These need not be followed to the letter; they simply help resolve
differences between Topographica authors if there are disagreements.

<P>One particular guideline of these that Jim does not always follow
is that he likes to use lines much longer than 80 characters, e.g. for
a string.  Other differences are listed elsewhere in this file, such
as in the REVISION INFO section.

<P>To keep things simple and consistent, we should try to use what
seems to be the most common Python names for the following concepts
(as opposed to those from C++ or Java):

<DL COMPACT>
<DT>method</DT><DD>     (not 'member function' or 'virtual function')
<DT>subclass</DT><DD>   (although 'derived class' is also ok)
<DT>superclass</DT><DD> (although 'base class' is also ok)
</DL>

<P>Typically, classes are named with InitialCapitalLetters, member
functions and attributes (variables and parameters) are lower_case,
and filenames are lowercasewithnounderscores.py.


<H1>User-level and simulator code</H1>

<P>By convention, we use a file extension of .py for the Python code
making up the simulator, in the <CODE>topo/</CODE> subdirectory.
Models and other user-level code such as scripts and examples should
use an extension of .ty, indicating that it is a file for use with
Topographica.  (Many of the .py files are general purpose, and could
be used with any Python program, but the .ty files typically require
all or most of Topographica.)

<P>All .ty files should use only the publically available classes and
functions in <CODE>topo/</CODE>, i.e. they should respect the
(as-yet-only-loosely-defined) Topographica API.

<P>Typically, files will be named with the lowercase version of the
main class which they contain.  E.g. sheet.py contains class Sheet and
some associated functions.  Most files should contain one main class,
though often subclasses are also included (in which case the file
should be named after the parent class).


<H1>Alerts</H1>

<P>As a convention, problematic areas of the code have been marked
with comments containing the text <CODE>ALERT</CODE> or
<CODE>HACKALERT</CODE>, usually prefixed with the initials of the
person who wrote the alert.  These comments help clarify how the code
should look when it is fully polished, and act as our to-do list.
They also help prevent poor programming style from being propagated to
other parts of the code before we have a chance to correct it.

<P>Anyone who sees a problem in the code but is unable for any reason
to fix the problem should add an alert for it.  The alert must
specifically describe what the problem is and how it could be
corrected (if known). If the problem is serious, especially if it may
affect any results seen by the users, it should be labeled a
HACKALERT.  Less serious issues, such as those primarily affecting
code readability, future maintainability, and generality, should be
labeled an ALERT.

<P>All Topographica developers are responsible for fixing alerts.  No
file in Topographica is owned by any single developer, and no
permission is needed from anyone to fix the problem.  Anyone who reads
an alert should, at the minimum, add a comment saying how the ALERT
could be fixed (if they have any idea), and ideally should fix the
problem.

<P>As soon as the problem is gone, the ALERT comment should be removed
entirely from the code.

<P>If any Topographica developer ever runs out of tasks, a good thing
to do is to search the Topographica directory for <CODE>ALERT</CODE>, and then
start fixing all those that seem fixable, starting with the easiest.


