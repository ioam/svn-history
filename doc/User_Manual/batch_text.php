<H1>Running Topographica simulations in batch mode</H1>

<P>Topographica is designed so that full functionality is available
from the command line and batch mode, without any GUI required.  This
support is essential for running large numbers of similar simulations,
e.g. to compare parameter settings or other options, usually using
clusters or networks of workstations.

<P>To make this process simpler, Topographica provides a command
topo.commands.basic.run_batch, which puts all results into a uniquely
identifiable directory that records the options used for the run.
Example:

<pre>
  ./topographica -a -c "run_batch('examples/tiny.ty')"
</pre>

<P>Here the <A href="commandline.html#option-a">"-a" option</a> is
used so that run_batch can be called without importing it explicitly,
and also so that all commands will be available to the various
plotting and analysis routines called by run_batch (as described
below). The result will be a directory with a name like
<code>200710112056_tiny</code> in the Output subdirectory, where the
name encodes the date of the run (in year/month/day/hour/minute
format) plus the name of the script file.  If you want to override any
of the options accepted by tiny.ty, you can do that when you call
run_batch:

<pre>
  ./topographica -a -c "run_batch('examples/tiny.ty',default_density=3)"
</pre>

<p>To help you keep the options straight, they will be encoded into
the directory name (as
<code>200710112056_tiny,default_density=3</code> in this case).

<p>run_batch also accepts a parameter <code>analysis_fn</code>, which
can be any callable Python object (e.g. the name of a function).  The
analysis_fn will be called periodically during the run, at times
specified by a parameter <code>times</code> (e.g.
<code>[0.5,2.8,100,500,1000,5000]</code>).  The simulation will
complete after the last analysis time.

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

<P>As you might expect, you can provide any other options before or
after the run_batch call, as usual.  These will be processed before or
after the batch run, respectively:

<pre>
  ./topographica -a -c "save_script_repr()" -c default_density=3\
  -c "run_batch('examples/tiny.ty')" \
  -c "save_snapshot()"
</pre>

Note that the output directory is not created or changed until the
run_batch command is executed, so the output from the
save_script_repr() command will go into the default output directory.
Also note that when a parameter is set before run_batch (as
default_density is in this example), it will not be encoded into the
directory filename, because run_batch will not be aware that it has
changed.  Similarly, any errors in the commands provided before or
after run_batch will not show up in the .out file stored in the
simulation directory, because that is closed when run_batch completes.
Thus it's usually best to use run_batch's options rather than
separate commands as shown here.

