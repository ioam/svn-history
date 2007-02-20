<H1>SOM Retinotopic Map</H1>

<p>
This tutorial shows how to use the
<a href="http://topographica.org/">Topographica</a> simulator to explore a
simple retinotopic map simulation.  This particular example, taken
from Chapter 3 of the <A
href="http://computationalmaps.org">Computational Maps in the Visual
Cortex</A>, uses a Kohonen-type Self-Organizing Map (SOM).
Topographica also supports a wide range of other models, and is easily
extensible for models not yet supported.
</p>

<p>This tutorial assumes that you have already followed the
instructions for <a href="../Downloads/index.html">obtaining and
installing</a> Topographica.</p>


<h2>Self-organization</h2>

In this example, we will see how a simple model cortical network
develops a mapping of the dimensions of variance in the input space.

<ol> 
<p></p>

<li>First, copy the <code>som_retinotopy.ty</code> example file from
  wherever the Topographica distribution is installed, into
  your own directory.  For instance, if Topographica is installed in
  <code>/home/jbednar/public/topographica/</code> and you would like
  to work in <code>~/cnv</code> in UNIX, you would type:
<pre>
  $ cd ~/cnv/
  $ cp /home/jbednar/public/topographica/examples/som_retinotopy.ty .
</pre>

<P><li>To start the full simulation from the book using the
  Topographica GUI, you could run:
<pre>
  /home/jbednar/public/topographica/topographica -g som_retinotopy.ty
</pre>
  However, a much smaller network is faster to run, and gets similar
  results.  To use a retina density of 10 and a cortical density of
  10, instead run Topographica as:
<pre>
  /home/jbednar/public/topographica/topographica -g \
  -c default_retina_density=10 -c default_density=10 som_retinotopy.ty
</pre>
  (all on one line, with no backslash).  These changes can also be
  made in the .ty file itself, if you do not want to type them each
  time you run the program.
  
<p>
You should now see a window for the GUI:
<p class='center'>
<img src="images/topographica_console.png" alt="Console Window"
align="middle" width="370" height="239">
</p>
  
<p>
The font, window, and button style will differ on different platforms,
but similar controls should be provided.
</p>

</li>

<li>This simulation is a small, fully connected map, with one input
sheet and one cortical sheet. The architecture can be viewed in the
  <span class='w_title'>Model Editor</span> window (which can be
  selected from the <span class='t_item'>Simulation</span> menu), but
  is also shown below: 
<p class='center'>
<img src="images/som_network_diagram.png" alt="SOM network."
align="middle" WIDTH="261" HEIGHT="318" border=2>
</p>

<P>The large circle indicates that these two Sheets are fully connected.

<p></p>
</li>

<li>To see the initial state of this network, select <span
class='t_item'>Projection</span> from the <span
class='t_item'>Plots</span> menu to get the <span
class='w_title'>Projection</span> window.  This plot shows the initial
set of weights from a 10x10 subset of the V1 neurons:
<!-- (i.e., all neurons for this small network): -->

<p class='center'>
<img src="images/som_projection_000000.png" alt="Projection window at 0"
align="middle" WIDTH="420" HEIGHT="469">
</p>

<p> Each neuron is fully connected to the input units, and thus has a
24x24 array of weights (or 10x10 if you reduced the density as
suggested above).  Initially, the weights are uniformly random.
</p>

<p></p>
</li>

<li>We can visualize the mapping from the input space into the
cortical space by selecting <span class='t_item'>Center of Gravity</span> from
the <span class='t_item'>Plots</span> menu on the <span
class='w_title'>Topographica Console</span> to get several plots.
These plots show the results of computing the <i>center of gravity</i>
(a.k.a. <i>centroid</i> or <i>center of mass</i>) of the set of input
weights for each neuron.

<P>This data is presented in several forms, of which the easiest to
interpret at this stage is the <span class='w_title'>Topographic
mapping</span> window.  This plot shows the CoG for each V1 neuron,
plotted on the Retina:

<p class='center'>
<IMG WIDTH="420" HEIGHT="469" SRC="images/som_grid_000000.png" align="middle" alt="CoG bitmap plots">
</p>

<P>Each neuron is represented by a point, and a line segment is drawn
from each neuron to each of its four immediate neighbors so that
neighborhood relationships (if any) will be visible.  From this plot
is is clear that all of the neurons have a CoG near the center of the
retina, which is to be expected because the weights are fully
connected and evenly distributed (and thus all have an average (X,Y)
value near the center of the retina).

<P>The same data is shown in the <span class='w_title'>Center of
Gravity</span> plot window, although it is more difficult to interpret
at this stage:

<p class='center'>
<IMG WIDTH="513" HEIGHT="340" SRC="images/som_cog_000000.png"  align="middle" alt="CoG bitmap plots">
</p>

where the V1 X CoG plot shows the X location preferred by each neuron,
and the V1 Y CoG plot shows the preferred Y locations.  The monochrome
values are scaled so that the neuron with the smallest X preference is
colored black, and that with the largest is colored white, regardless
of the absolute preference values (due to Normalization being
enabled).  Thus the absolute values of the X preferences are not
visible in these plots.  (Without normalization, values below 0.0 are
cropped to black, so only normalized plots are useful for this
particular example.)

<P>The colorful plot labeled "V1 CoG" shows a false-color
visualization of the CoG values, where the amount of red in the plot
is proportional to the X CoG, and the amount of green in the plot is
proportional to the Y CoG.  Where both X and Y are low, the plot is
black or very dark, and where both are high the plot is yellow
(because red and green light together appears yellow).  This provides
a way to visualize how smoothly both X and Y are mapped, although at
this stage of training it is not particularly useful.

<P><li>The behavior of this randomly connected network can be visualized
by plotting the feedforward activation of each neuron, which
represents the SOM Euclidean-distance response function.  Select
<span class='t_item'>Activity</span> from
the <span class='t_item'>Plots</span> menu to get the following plot:

<p class='center'>
<IMG WIDTH="416" HEIGHT="340" SRC="images/som_activity_000000.png" align="middle" alt="Activity at 0">
</p>

<p>This window shows the response for each Sheet in the model, which
is zero at the start of the simulation (and thus both plots are
black).  Note that these responses are best thought of as Euclidean
proximity, not distance.  This formulation of the SOM response
function actually subtracts the distances from the max distance, to
ensure that the response will be larger for smaller Euclidean
distances (as one intuitively expects for a neural response).

<P><li>To run one input generation, presentation, activation, and
learning iteration, click in the <span class='t_item'>Run
for</span> field of the <span class='w_title'>Topographica
Console</span> window, make sure it says 1, and hit Go.  The
<span class='w_title'>Activity</span> window should then refresh to
show something like:

<p class='center'>
<IMG WIDTH="416" HEIGHT="340" SRC="images/som_activity_000001.png" align="middle" alt="Activity at 0">
</p>

<p>In the <span class='t_item'>Retina</span> plot, each photoreceptor
is represented as a pixel whose shade of grey codes the response
level, increasing from black to white.  The
<code>som_retinotopy.ty</code> file specified that the input be a
circular Gaussian at a location that is random in each iteration, and
in this particular example the location is near the border of the
retina.

<P>The V1 feedforward activity appears random because SOM uses a
Euclidean distance response function, and the distance from the input
vector to a random weight vector is random.  Note that you should
usually check the <span class='t_item'>Normalize</span> button for a
SOM network, because the Euclidean distance is expressed in arbitrary
units, although the plot often looks fine even without normalizing the
minimum value to black and the maximum to white.


<P><li> If you now hit <span class='t_item'>Refresh</span> in the
<span class='w_title'>Projection</span> window, you'll see that some
of the neurons have learned new weight patterns based on this input.

<p class='center'>
<img src="images/som_projection_000001.png" alt="Projection window at 1"
align="middle" WIDTH="420" HEIGHT="469">
</p>

(You should probably turn on the <span
class='t_item'>Auto-refresh</span> button so that this plot will stay
updated for the rest of this session.)  Some of the weights have now
changed due to learning.  In the SOM algorithm, the unit with the
maximum response (i.e., the minimum Euclidean distance between its
weight vector and the input pattern) is chosen, and the weights of
units within a circular area defined by a Gaussian-shaped
<i>neighborhood function</i> around this neuron are updated.

<P>This effect is visible in the <span
class='w_title'>Projection</span> plot -- a few neurons around the
winning unit at the top middle have changed their weights.
Continue pressing Go in the Console window to learn a few more
patterns, each time noticing that a new input pattern is generated and
the weights are updated.  After a few iterations it should be clear
that the input patterns are becoming represented in the weight
patterns, though not very cleanly yet:

<p class='center'>
<img src="images/som_projection_000005.png" alt="Projection window at 5"
align="middle" WIDTH="420" HEIGHT="469">
</p>

Also note that the activation patterns are becoming smoother, since
the weight vectors are now similar between neighboring neurons:

<p class='center'>
<IMG WIDTH="416" HEIGHT="340" SRC="images/som_activity_000005.png" align="middle" alt="Activity at 0">
</p>

<P><li>Continue training for a while and looking at the activation and
weight patterns.  Instead of 1, you can change the
<span
class='t_item'>Run for</span> field to any number to train
numerous iterations in a batch, e.g. 1000.  After 5000 iterations, 
updating the <span class='w_title'>Center of Gravity</span> should
result in something like:

<p class='center'>
<IMG WIDTH="513" HEIGHT="340" SRC="images/som_cog_005000.png"  align="middle" alt="CoG bitmap plots">
</p>

The X and Y CoG plots are now smooth, but not yet the axis-aligned gradients
(e.g. left to right) that an optimal topographic mapping would
have. Similarly, the topographic grid plot:

<p class='center'>
<IMG WIDTH="420" HEIGHT="469" SRC="images/som_grid_005000.png" align="middle" alt="Grid at 100">
</p>

shows that the network is now responding to different regions of the
input space, but that most regions of the input space are not covered
properly.  Additional training up to 10000 iterations leads to a flat, square
map:

<p class='center'>
<IMG WIDTH="420" HEIGHT="469" SRC="images/som_grid_010000.png" align="middle" alt="Grid at 10000">
</p>

although the weight patterns are still quite broad and not very
selective for typical input patterns:

<P class='center'>
<img src="images/som_projection_010000.png" alt="Projection window at 10000"
align="middle" WIDTH="420" HEIGHT="469">
</p>


and by 40000 the map has good coverage of the available portion of the
input space:

<p class='center'>
<IMG WIDTH="420" HEIGHT="469" SRC="images/som_grid_040000.png" align="middle" alt="Grid at 40000">
</p>

<LI>The final projection window at 40000 now shows that each neuron
has developed weights concentrated in a small part of the input space,
matching a prototypical input at one location:

<p class='center'>
<img src="images/som_projection_040000.png" alt="Projection window at 40000"
align="middle" WIDTH="420" HEIGHT="469">
</p>

For this particular example, the topographic mapping for the x and y
dimensions happen to be in the same orientation as the retina.  For
example, responses to patterns in the upper left of the retina lead to
responses in the upper left of the cortex.  There is no reason this
should be the case in general, and the map can be flipped or rotated
by 90 degrees along any axis with equivalent results.

<P><LI>Now, re-run the basic simulation by quitting and restarting
Topographica.  This time, change one of the parameter values, either
by editing the <code>som_retinotopy.ty</code> file before starting, or
by providing it on the command line (for those parameters that check
<code>locals()</code> for their defaults), or 
by typing the command at the Topographica terminal prompt.  For
instance, to see the starting value of the neighborhood radius (from
which all future values are calculated according to exponential
decay), type:

<pre>
  topo.sim['V1'].radius_0
</pre>


You should see an initial value of something like 0.9975 displayed in
your terminal window. Then change this value as you see fit, e.g. to
0.1:

<pre>
  topo.sim['V1'].radius_0=0.1
</pre>

and go through learning again.  (You can also make this change in the
Model Editor, or by passing "-c radius_0=0.1" on the command line.) 
With such a small learning radius, global ordering is unlikely to
happen, and one can expect the topographic grid not to flatten out
(despite local order in patches).
<br>
<br>

<P>Similarly, consider changing the learning rate from
<code>V1.alpha_0=0.42</code> to e.g. 1.0
(e.g. by passing "-c alpha_0=1.0" on the command line).  The retina
and V1 densities cannot be changed after the simulation has started; to
change those provide their values on the command line as above (or
edit the <code>som_retinotopy.ty</code> file)
and start Topographica again.

<P>You can also try changing the input_seed ("-c input_seed=XX"), to
get a different stream of inputs, or weight_seed ("-c
weight_seed=XX"), to get a different set of initial weights.
<!-- 
With some of these values, you may encounter cases where the SOM
fails to converge even though it seems to be working properly
otherwise.  For instance, some seed values result in topological
defects like a 'kink':

  (add picture)

<P>This condition represents a local optimum from which the network
has difficulty escaping, where there is local order over most of the
map except for a discontinuity. -->

<P>This condition represents a local optimum from which the network
<P>Finally, you could change the input pattern to get a different type
of map.  E.g. if an oriented pattern is used, with random
orientations, neurons will become selective for orientation and not
just position.  See the <code>examples/obermayer_pnas90.ty</code> file
for more details. <!--, though that simulation is quite
processor-intensive compared to this one. --> In general, the map
should form a representation of the dimensions over which the input
varies, with each neuron representing one location in this space, and
the properties of nearby neurons typically varying smoothly in all
dimensions.

</ol>

<h2>Exploring further</h2>

<p> Topographica comes with
additional examples, and more are currently being added. Any valid Python code can
be used to control and extend Topographica; documentation for Python and existing Topographica commands
can be accessed from the <span class='t_item'>Help</span> menu of the
<span class='w_title'>Topographica Console</span> window.
<p>
 Please contact 
<A HREF="mailto:&#106&#98&#101&#100&#110&#97&#114&#64&#105&#110&#102&#46&#101&#100&#46&#97&#99&#46&#117&#107?subject=Comments%20on%20Topographica%20tutorial">&#106&#98&#101&#100&#110&#97&#114&#64&#105&#110&#102&#46&#101&#100&#46&#97&#99&#46&#117&#107</a>
if you have questions or suggestions about the software or this
tutorial.
</p>
