<H1>Frequently Asked Questions about Topographica</H1>

<P>Here we collect together some answers to <A HREF="#general">general
questions</A> about Topographica. If you have a problem that isn't
answered below, please feel free to ask us (either in one of our <A
HREF="../Forums/index.html">forums</A>, or by email). <!-- address?-->

<H3><A NAME='general'>General Questions</A></H3>
<OL>

<!----------------------------------------------------------------------------->
<LI><B>Q:</B> <i>How can I get access to the actual data shown in the
  various plots, etc.?</i>

<P><B>A:</B>
The main objects in the simulation can be accessed through the
<code>topo.sim</code> attribute.  For instance, if you have a sheet
named <code>'V1'</code>, it can be accessed as
<code>topo.sim['V1']</code>.  From there the projections, weights,
etc. for that unit can be obtained.  See the
<a href="../User_Manual/commandline.html">Command line</A> section of
the user manual for more information, including how to plot such data
manually.

<!----------------------------------------------------------------------------->
<LI><B>Q:</B> <i>After upgrading Topographica or editing some of its files,
  I get errors when loading a saved snapshot.</i>

<P><B>A:</B>
As of 0.9.5, Topographica saves the state by using Python's pickling
procedure, which saves <em>everything</em> in the current simulation.
The disadvantage of this approach is that changes in the
definition of any of the classes used (apart from changing parameter
values or strictly adding code) can cause the reloading to fail.
Whenever possible, we provide legacy snapshot support that maps from
the old definition into the new one, and so snapshots <em>should</em>
continue to be loadable.  However, if you have trouble with a
particular file, please file a bug report so that we can extend the
legacy support to be able to load it.  In the long run we plan to set
up an archival storage format, probably based on XML and/or HDF5, to
work around these issues.
  

<!--CEBALERT: this is out of date, isn't it? -->
  
<!----------------------------------------------------------------------------->
<LI><B>Q:</B> <i>When I try to save a snapshot of my network, I get
  this scary warning:</i> 

<pre>
Parameterized53371: Warning: ManagedRandomComposite (type <class 
'param.parameterized.ParameterizedMetaclass'>) has 
source in __main__; it will only be found on unpickling if the class is 
explicitly defined (e.g. by running the same script first) before 
unpickling.
</pre>

<P><B>A:</B> 
That doesn't necessarily indicate anything is wrong.  What it is
saying is that you have defined some variables and/or classes in your
.ty script file, rather than in a .py module in topo/.  Python knows

<!-- No warning is printed for variables: just functions and classes.
Do we need to add a warning for variables? (Maybe we could actually
pickle variables?)  Also, it's not just those functions and classes
defined in a .ty script file, but also those defined at the command
prompt. -->

how to restore the state of anything in an imported module, but it has

<!-- 'imported module' = module imported from topo -->

no idea how to find classes defined in regular scripts like those in
the examples directory (which we name ending in .ty to make the
difference obvious).  So you can either:

<P>1. Move any classes, functions, etc. that you need from your .ty file
into somewhere in a .py file that your script then imports.  That's
usually the best long-term solution, because then anyone can use your
classes.  If there are very specialized classes or functions in the
.ty file that are not useful for other people, you can consider
putting it into the contrib/ subdirectory, with a suitably unique
filename.  However, this approach may not be appropriate if you find
it easier to develop the functions in one file.

<P>or

<P>2. Before reloading a saved snapshot, just run your .ty file as you
did the first time.  That will define all the classes, functions,
etc., and then reloading the saved snapshot should work fine.
      
<P>The warning is just telling you that you need to do option 2; if you
want to suppress the warning entirely you can do option 1.
</LI>


<!----------------------------------------------------------------------------->
<LI><B>Q:</B> <i>Topographica seems to build fine, but when I run the
GUI or the tests, I get an "ImportError: No module named _tkagg".</i>

<P><B>A:</B> As of 10/2007, if Topographica was built on a machine
without a functioning Xwindows DISPLAY, e.g. via a remote login using
ssh, the build process would complete but Matplotlib would have failed
silently because it could not find the current display to extract some
parameters.  As of 9/2008 (version 0.9.5), we can no longer reproduce
this problem, and thus it appears to have been fixed by Matplotlib's
maintainers.  However, if you do encounter something like this, you
can try rebuilding Topographica while logged in rather than remotely.
If that works, please let us know that we should continue to suggest
that people avoid building in a remote session.
  
<!----------------------------------------------------------------------------->
<LI><B>Q:</B> <i>What models or algorithms does Topographica support?</i>

<P><B>A:</B> 
Topographica is built in a highly modular fashion, and thus it can
support an effectively infinite number of algorithms with little or no
change to the underlying code.  For instance, there is no particular
Topographica component that implements the SOM algorithm -- instead, a
SOM network like examples/som_retinotopy.ty is simply built from:

<ol>
<li>An input pattern specified from a large library of possible 
  <?php classref('topo.base.patterngenerator','PatternGenerator')?>s
<li>A general-purpose
  <?php classref('topo.sheet.basic','GeneratorSheet')?> 
  for presenting input patterns
<li>A general-purpose weight projection class 
  <?php classref('topo.base.cf','CFProjection')?> 
<li>A general-purpose array of units
  <?php classref('topo.base.cf','CFSheet')?> 
<li>A specialized transfer function 
  (<?php classref('topo.transferfn.misc','KernelMax')?>) that picks a
  winning unit and activates the rest according to a user-specified
  kernel function.
</ol>

<P>This approach makes it simple to change specific aspects of a model
(e.g. the specific kernel function) without necessarly requiring any
new code, as long as the new function has already been written for any
previous model.  For this example, only the KernelMax function (about
50 lines of Python code) was added specifically for supporting SOM;
the other components are all used in a wide variety of other models.
<BR><BR>


<!----------------------------------------------------------------------------->
<LI><B>Q:</B> <i>I think I've found a problem with Topographica. What should
  I do now?</i>

<P><B>A:</B> 
Topographica is continuously changing to support active research, so
problems can occur. To be sure you have found a problem with
Topographica itself, and to help us fix it quickly, please follow our
guidelines for <a href="../Forums/problems.html">Reporting specific
problems with Topographica</a>.
  
<!----------------------------------------------------------------------------->


<!----------------------------------------------------------------------------->
<LI><B>Q:</B> <A NAME="easyinstall"></A><i>easy_install/pip failed while processing
dependencies. What can I do now?</i>

<P><B>A:</B> 

easy_install and pip can sometimes encounter problems while processing
dependencies. In such cases, installation will stop at the failed
dependency, so it is usually straightforward to identify and fix the
problem. Below we list some possibilities for solving easy_install/pip
problems:

<ul>

<li>pip dependency-processing problems can sometimes be solved by
installing the individual dependencies before running <code>pip
install topographica</code>:
<code>pip install numpy; pip install PIL</code> (then, optionally,
other recommended dependencies). Once these are installed, repeat the
<code>pip install topographica</code> command.</li>

<li>Binaries of Topographica's required dependencies (NumPy and PIL)
as well as recommended dependencies (MatPlotLib, gmpy) are available
for many platforms. Once installed, repeat the <code>easy_install
topographica</code> or <code>pip install topographica</code>
command.</li>

<li>If a binary is not available for your platform, you should check
the dependency's installation instructions for your platform. Usually,
you will need to make sure that you have typical code-building tools
(e.g. a C/C++ compiler). Your distribution will usually have such
tools available, e.g. the "build-essential" package on Ubuntu
or <A HREF="http://developer.apple.com/technologies/tools/xcode.html">Xcode</A>
on Mac. You will also need the Python headers, for which it might be
necessary to install your distribution's "python-dev" or
"python-devel" package.</li>

</ul>

<!----------------------------------------------------------------------------->

  
</OL>


