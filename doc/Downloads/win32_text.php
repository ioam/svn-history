<h1>Installing Topographica on Windows XP/2000</h1>

<p>(Installation procedure verified as of November 14, 2005)

We are currently in the process of streamlining the installation
process under Windows; the current method is much more difficult than
on other platforms.  In any case, there is a relatively easy method
that will usually work ("The fast way" below), and a more difficult
method that will work in more cases ("The slow way").  Both of these
methods will provide only a non-optimized version of Topographica,
which will be quite slow; for an optimized version see "Integrating
Topographica and Weave" below.

<h2>The fast way:</h2>

<ol>
<li> Unpack the topographica archive into a temporary directory.<br>
<li> Double click on setup.bat<br>
<li> Follow the various installation prompts for the packages 
     bundled with Topographica.<br>
</ol>

<P>
After installation you should now have an icon on your desktop that
opens the directory where Topographica is installed.  There will be a
new file association called ".ty" which are scripts that the
Topographica program will execute when you double-click on them.

<P>
You can now test the installation by double-clicking on the
topographica.bat file.  This should run the interactive Topographica
shell and give you a "Topographica>" prompt.


<h2>If there is a problem:</h2>

Known issues:

<hr>

<p>As of 11/2005, the Weave (part of SciPy) C compiler linkage is not
installed by default for Python 2.4.  Some features of Topographica 
that require Weave will cause ImportErrors if attempted on a Windows 
platform.  This includes many of the example network simulations in the
/examples/ directory.  There are directions in /examples/lissom_or.ty
for changing the code to not use the optimized Weave functions.

<p>See below for directions on how to integrate Weave with Topographica
on Windows.

<hr>

<p>If you experience the error:
<pre>
  File "C:\Python23\lib\string.py", line 220, in atoi 
    return _int(s, base)
TypeError: int() can't convert non-string with explicit base
</pre>

then you may be running an old version of Python.  Check your
Environment Variables in "My Computer -> Properties" to make sure you
don't have an old version of Python earlier in your path statement
that is running first.


<h2>Installing the slow way:</h2>

<p>To install the Topographica parts by hand, be sure Python 2.4 is
installed and do (a), (b), and (c) below.  See Note.


<p>
Topographica is a Python 2.4 program and requires Python 2.4 to be
installed.  The setup.bat script checks to see if the correct version
exists.  If an older version of Python is associated with
Python Files then an included Python 2.4 installer located in
\external\ will be executed.

<p>
After Python has been installed or detected, the directory is changed
to .\external\win32\ and following commands are run:

<pre>
   start /wait setup.py configure     % Verifies Python 2.4 installed.
   start /wait setup.py install
</pre>


<p>
The 'setup.py install' does the following:

<p>
a) Installs the following programs found in external\win32\<br>
<pre>
   Numeric-23.7.win32-py2.4.exe    Python Numeric package
   PIL-1.1.5b3.win32-py2.4.exe	   Python Imaging Library
   matplotlib-0.81.win32-py2.4.exe PyLab Math and Plotting package
   ..\Pmw.tgz                      Python Mega Widgets  (Contains a Read-Me)
   fixedpoint-0.1.2_patched.tgz    FixedPoint number classes
</pre>

<p>
b) Copy the core Topographica files in \topo\* to the install location
   BASE_LOCATION\topo\

c) Additional tasks in the script include (in no particular order):
<ol>
<li> Associate Topographica File extensions (.ty).
<li> Give .ty Files a pretty icon.
<li> Construct a Topographica run command that is named topographica.py.
     This can be run directly, or through topographica.bat:
<li> Create a topographica.bat wrapper for running Topographica.
<li> Create a Desktop CMD file to open the Install location of Topographica
</ol>   

<p>
Note: The "Additional Tasks" of part (c) listed above are only for
streamlining the Topographica user interface and are not needed
to run the system.  If there is a problem with the install
script and (c) does not complete then Topographica can still be
executed by issuing the following command from a Shell window
that is in the root location of the Topographica installation:

<pre>
   [Python Location]\python.exe topographica.py
</pre>

To execute an existing Topographica script add the filename to
the end of the command:

<pre>
   [Python Location]\python.exe topographica.py script.py
</pre>


<h2>Integrating Topographica and Weave on Windows</h2>

<p>
Topographica is under active development (12/2005) to make the Windows
version of Topographica easier to install and use.  For now, these
notes should be able to help you get Weave (www.scipy.org) built on
Windows and integrated with Topographica.


<p>Building Weave:

<p>
Since Weave does not have a pre-compiled Windows version that works
with Python 2.4, you need to compile and install it yourself into the
Python 2.4 site-packages directory.  You will not need the entire
SciPy source, only the SciPy_core files.  Topographica has been tested
with Scipy-0.3.2.

<p>
Weave requires a C++ compiler for both compiling the weave package,
and for executing the Python weave.inline() functions.  The MSVC
development suite or MinGW can be used.  Topographica has been tested
with MinGW, using the following package versions:
<pre>
    mingw-runtime-3.9
    w32api-3.5
    binutils-2.15.91
    gcc-core-3.4.2
    gcc-g++-3.4.2
</pre>

<p>You may find it necessary to adjust your Windows system variables to
find the MinGW paths before other gcc compilers, such as cygwin.  If
you do not want to make a system-wide change, it is possible to create
a .BAT file like the one below that will update environment variables
for a single cmd window.  NOTE: The adjusted paths are also required
when Topographica runs, since the inline statements use the compiler.

<pre>
    REM Must change paths so MinGW is seen instead of Cygwin compilers.
    REM C:\mingw\minpath.bat  Also put in topographica.{bat,cmd}
    @Echo Prepend the paths for MinGW
    set PATH=C:\mingw\bin;%PATH%
    set LIB=C:\mingw\lib;%LIB%
    set INCLUDE=C:\mingw\include;%INCLUDE%
</pre>

<p>From the Weave documentation, commands to compile weave:
<pre>
    python setup.py build --compiler=mingw32
    python setup.py --compiler=mingw32 install
</pre>

Commands to test weave:
<pre>
    python
    >>> import weave
    >>> scipy.test()
</pre>

<p>
Changes to the Topographica distribution:

<p>
Topographica has been designed to work with the gcc compiler.  If you
wish to use MS Visual C++ instead, then the compiler option in 
topo/base/inlinec.py must be changed from "compiler='gcc'" to "compiler='msvc'".

<p>
examples/lissom_or.ty should now run with no errors.

<br> <p> Once you have the Windows version working, please return to
the <a href="index.html">Downloads</a> page for the usual information
about running Topographica and updating it later.
