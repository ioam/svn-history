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
As of 0.9.2, Topographica saves the state by using Python's pickling
procedure, which saves <em>everything</em> in the current simulation.
The disadvantage of this approach is that most changes in the
definition of any of the classes used (apart from changing parameter
values or strictly adding code) will cause the reloading to fail.
Until we have set up an archival storage format, probably based on XML,
snapshots should be considered temporary.  
  
<!----------------------------------------------------------------------------->
<LI><B>Q:</B> <i>When I try to save a snapshot of my network, I get
  this scary warning:</i> 

<pre>
ParameterizedObject53371: Warning: ManagedRandomComposite (type <class 
'topo.base.parameterizedobject.ParameterizedObjectMetaclass'>) has 
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
classes.  However, this approach is not always appropriate, if there
are very specialized classes or functions in the .ty file that are not
useful for other people.

<P>or

<P>2. Before reloading a saved snapshot, just run your .ty file as you
did the first time.  That will define all the classes, functions,
etc., and then reloading the saved snapshot should work fine.
      
<P>The warning is just telling you that you need to do option 2; if you
want to suppress the warning entirely you can do option 1.
</LI>


<!-- what about: "I think I've found a problem: what should I do now?" -->

  
</OL>
