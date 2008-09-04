<H1>Frequently Asked Questions about Topographica</H1>

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
  
  
<!----------------------------------------------------------------------------->
<LI><B>Q:</B> <i>When I try to save a snapshot of my network, I get
  this scary warning:</i> 

<pre>
Parameterized53371: Warning: ManagedRandomComposite (type <class 
'topo.param.parameterized.ParameterizedMetaclass'>) has 
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
  (<?php classref('topo.outputfn.basic','KernelMax')?>) that picks a
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


  
</OL>
