<!-- $Id$ -->

<h1>Installing Topographica on Windows XP/2000</h1>

<p>(Installation procedure verified as of January 26th, 2006) We plan
   to offer an self-extracting installer to make the installation
   process go more smoothly under Windows, but these instructions
   should work in the meantime.
<p>If there is a problem with the
   automatic setup.bat installation, the below method will install
   Topographica. After Topographica is installed you can optionally
   install the optimized C functions by going to &quot;Step 3)
   Integrating Topographica and Weave&quot; below.
</p>

<h2>Manually Installing Topographica on Windows:</h2>

<p><b>Step 1)</b> Topographica is a Python 2.4.2 program and requires
   Python 2.4.2 to be installed. If an older version of Python is
   associated with Python Files then the included Python 2.4.2
   installer located in \external\ should be executed.
</p>

<p><b>Step 2)</b> After Python has been installed or detected, change
   the directory to .\external\win32\ and run the following commands:
</p>

<pre>
   start /wait setup.py configure % Verifies Python 2.4 installed.
   start /wait setup.py install </pre>

<p>If the 'setup.py install' does not finish correctly then you will
   need to do the steps <b>2a-c</b> manually, if it worked fine go to
   step <b>3</b>.
<p><b>Step 2a)</b> Install the following programs found in external\win32\<br>
</p>

<pre>
   Numeric-23.7.win32-py2.4.exe    Python Numeric package
   PIL-1.1.5b3.win32-py2.4.exe     Python Imaging Library
   matplotlib-0.81.win32-py2.4.exe PyLab Math and Plotting package
   ..\Pmw.tgz                      Python Mega Widgets  (Contains a Read-Me)
   fixedpoint-0.1.2_patched.tgz    FixedPoint number classes
</pre>

<p><b>Step 2b)</b> Copy the core Topographica files in \topo\* to the
   install location BASE_LOCATION\topo\
</p>

<p><b>Step 2c)</b> Topographica can now be executed by issuing the
   following command from a Shell window that is in the root location
   of the Topographica installation:
</p>

<pre> [Python Location]\python.exe topographica.py</pre>

<p>To execute an existing Topographica script add the filename to the
   end of the command:
</p>

<pre>     [Python Location]\python.exe topographica.py script.py
</pre>

<h2>Step 3) Integrating Topographica and Weave on Windows</h2>

<p>As of 1/2006, the Weave (part of SciPy) C compiler linkage is not
   installed by default for Python 2.4.2. Some optimized features of
   Topographica that require Weave will be disabled, and a warning
   message about using slower non-optimized functions will be
   displayed.  This affects many of the example network simulations in
   the /examples/ directory.  Installing Weave will auto-enable the
   optimized functions within Topographica.
</p>

<p><b>Downloading Weave and a C++ compiler:</b></p>

<p>Since Weave does not have a pre-compiled Windows version that works
   with Python 2.4.2, you need to compile and install it yourself.
   Topographica has been tested with Scipy-0.3.2, which can be
   downloaded from the SciPy website <a
   href="http://www.scipy.org">http://www.scipy.org</a> .  You will
   not need the entire SciPy source, only the SciPy_core files which
   has already been included in the /external/ directory of the 
   Topographica distribution.
</p>

<p>Weave also requires a C++ compiler for both compiling the weave
   package, and for executing the Python weave.inline() functions. The
   MSVC development suite or MinGW can be used. Topographica has been
   tested with MinGW, using the following package versions from <a
   href="http://www.mingw.org">http://www.mingw.org</a> :
</p>

<pre>
    mingw-runtime-3.9
    w32api-3.5
    binutils-2.15.91
    gcc-core-3.4.2
    gcc-g++-3.4.2
</pre>

<p><b>Compiling Weave:</b></p>

<p>Follow the directions on SciPy.org for compiling Weave: <a
   href="http://www.scipy.org/documentation/buildscipywin32.txt">http://www.scipy.org/documentation/buildscipywin32.txt</a></p>

<p>Commands to compile weave: (From the Weave documentation link above)</p>
<pre>
    python setup.py build --compiler=mingw32
    python setup.py --compiler=mingw32 install
</pre>

<p><b>Helpful tip:</b> You may find it necessary to adjust your
   Windows system variables to find the MinGW paths before other gcc
   compilers you may have installed, such as cygwin. If you do not
   want to make a system-wide
   change, it is possible to create a .BAT file like the one below
   that will update environment variables for a single cmd window. The
   adjusted paths are also required when Topographica runs, since the
   inline statements use the compiler.
</p>

<pre>
    REM Must change paths so MinGW is seen instead of Cygwin compilers.
    REM This file: C:\mingw\minpath.bat  Also put in topographica.{bat,cmd}
    @Echo Prepend the paths for MinGW
    set PATH=C:\mingw\bin;%PATH%
    set LIB=C:\mingw\lib;%LIB%
    set INCLUDE=C:\mingw\include;%INCLUDE%
</pre>

<p><b>Step 4)</b> Test that weave is working correctly:</p>

<pre>
    python
    >>> import weave
    >>> scipy.test()
</pre>

<p>By default, Topographica is configured to use a gcc compiler such
   as MinGW.  If you wish to use MS Visual C++ instead, then the
   compiler option in topo/base/inlinec.py must be changed from
   "compiler='gcc'" to "compiler='msvc'".
</p>


<p>If Weave is installed but your C compiler is not installed or
   configured properly then Topographica will abort with an error
   when you try to run it. If you are unable to fix the C compiler,
   but still want to run Topographica, you can set the
   <tt>import_weave</tt> variable in topo/misc/inlinec.py to False to
   disable the Weave auto-detection process.  Note, however, that most
   models will execute much more slowly in this case.
</p>

<p><b>Step 5) </b> examples/lissom_or.ty should now run with no errors
   or warnings.</p> 

<hr> 

<h2>If there is a problem:</h2>

<p>If you experience the error:</p>

<pre>
  File "C:\Python23\lib\string.py", line 220, in atoi 
    return _int(s, base)
TypeError: int() can't convert non-string with explicit base
</pre>

then you may be running an old version of Python.  Check your
Environment Variables in "My Computer -> Properties" to make sure you
don't have an old version of Python earlier in your path statement
that is running first.  
</p>

<hr>

<p>Once you have the Windows version working, please return to the <a
   href="index.html">Downloads</a> page for the usual information
   about running Topographica and updating it later.
</p>

