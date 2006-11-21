<P>Older news:

<p><b>02 November 06:</b> Some users have reported problems when using
optimized code on systems with the most recent GCC 4.1.x C/C++
compilers.  We have added a patch to the included weave
inline-compilation package that should fix the problem, currently
available only on the most recent CVS version of Topographica.
Affected users may need to do a <A target="_top"                                                                  
href="../Downloads/cvs.html">CVS</A> update, then "make -C external
weave-uninstall ; make".  These changes will be included in the next
official release.

<p><b>23 July 06:</b> Version 0.9.1
<A target="_top" href="../Downloads/index.html">released</A>.
This is a bugfix release only, upgrading the included Tcl/Tk package
to correct a syntax error in its configure script, which had
been preventing compilation on platforms using bash 3.1 (such as
Ubuntu 6.06).  There is no benefit to updating if 0.9.0 already runs
on your platform.

<p><b>20 February 06:</b> Version 0.8.2 released, including numerous
bugfixes, 
circular receptive fields,
shared-weight projections,
<A TARGET="_top" href="../Tutorials/lissom_oo_or.html">tutorial with ON/OFF LGN model</A>,
<A TARGET="_top" href="../Tutorials/som_retinotopy.html">SOM retinotopy tutorial</A>,
Euclidean-distance-based response and learning functions,
density-independent SOM parameters,
<A TARGET="_top" href="../Downloads/cvs.html#osx">Mac OS X instructions</A>,
<A TARGET="_top" href="../Developer_Manual/index.html">developer manual</A>,
<A TARGET="_top" href="../User_Manual/index.html">partial user manual</A>,
much-improved 
<A target="_top" href="../images/060220_model_editor_screen_shot.png">model editor</A>,
<A TARGET="_top" href="../User_Manual/commandline.html#pylab">generic Matlab-style plotting</A>,
topographic grid plotting,
RGB plots,
user-controllable plot sorting,
plot color keys,
<!-- Normally distributed random PatternGenerator, -->
and progress reports during learning.  See the 
<A target="_top" href="../images/060220_topographica_screen_shot.png">Linux screenshot</A>.

<p><b>22 December 05:</b> Version 0.8.1 released, including numerous
bugfixes, more flexible plotting (including weight colorization),
user-controllable optimization, properties panels, more-useful
<A TARGET="_top" href="../Reference_Manual/index.html">reference manual</A>,
image input patterns, and a prototype graphical
model editor.  <!-- Plus SOMs with selectable Projections -->

<p><b>8 November 05:</b> New site launched with Topographica version
0.8.0, including a new
 <a target="_top" href="../Tutorials/lissom_or.html">LISSOM tutorial</a>.
(<a target="_top" href="../images/051107_topographica_screen_shot_white.png">Linux screenshot</a>).
