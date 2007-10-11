<H1>Running Topographica simulations in batch mode</H1>

<P>Topographica is designed so that full functionality is available
from the command line and batch mode, without any GUI required.  This
support is essential for running large numbers of similar simulations,
e.g. to compare parameter settings or other options, such as on
cluster computers.

<P>Topographica provides a simple mechanism for running in batch mode,
so that all results will be placed into a uniquely identifiable
directory that records the options used for the run.  Example:

<pre>
  ./topographica -c "from topo.misc.commandline import run_batch" \
    -c "run_batch('examples/tiny.ty')"
</pre>

<P>The result will be a directory with a name like
<code>200710112056_tiny</code> in the Output subdirectory, where the
name encodes the date of the run (in year/month/day/hour/minute
format) plus the name of the script file.  If you want to override any
of the options accepted by tiny.ty, you can do that when you call
run_batch:

<pre>
  ./topographica -c "from topo.misc.commandline import run_batch" \
    -c "run_batch('examples/tiny.ty',default_density=3)"
</pre>

<p>To help you keep the options straight, they will be encoded into
the directory name (as
<code>200710112056_tiny:default_density=3</code> in this case).

<p>run_batch also accepts a parameter <code>analysis_fn</code>, which
can be any callable Python object (e.g. the name of a function).  The
analysis_fn will be called periodically during the run, at times
specified by a parameter <code>analysis_times</code> (e.g.
<code>[100,500,1000,5000]</code>).  The simulation will complete after
the last analysis time.

<p>The default analysis_fn creates a few plots each time and saves the
current script_repr() of the simulation to record the parameter
settings from that time.  In practice you will want to supply your own
function, defined either in your .ty file or in a separate script or
module executed before you call run_batch.  In this case you can start
from the default_analysis_function in topo/misc/commandline.py as an
example.  Your analysis_fn should avoid using any GUI functions (i.e.,
should not import anything from topo.tkgui), and it should save all of
its results into files.  For more information about commands that can
go into the analysis_fn, see the <A HREF="commandline.html">command
line/script language</A> section.

<p>When preparing results for publication, it is highly recommended
that you do them in batch mode, so that you have a permanent record of
all of the commands and options used to generate your results, and so
that they will be stored in a uniquely identifiable directory that you
can access reliably later.
