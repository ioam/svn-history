<H1>SOM Retinotopic Map</H1>

<p>
This tutorial shows how to use the
<a href="http://topographica.org/">Topographica</a> software to explore a
simple retinotopic map simulation.  This particular example uses a
Kohonen-type Self-Organizing Map (SOM), although Topographica supports
other models and is easily extensible for models not yet supported.
</p>

<p>This tutorial assumes that you have already followed the
instructions for <a href="../Downloads/index.html">obtaining and
installing</a> Topographica.</p>


<h2>Self-organization</h2>

In this example, we will see how a simple model cortical network
develops a mapping of the input space.

<ol> 
<p></p>

<li>First, copy the <code>som_retinotopy.ty</code> example file from
  wherever the Topographica distribution is installed into
  your own directory.  For instance, if Topographica is installed in
  <code>/home/jbednar/public/topographica/</code> and you would like
  to work in <code>~/cnv</code> in UNIX, you would type:
<pre>
  $ cd ~/cnv/
  $ cp /home/jbednar/public/topographica/examples/som_retinotopy.ty .
</pre>

<!--
<P><li>Next, you will usually want to edit the <code>som_retinotopy.ty</code> file to make it
  faster to run, by reducing the number of units simulated in the
  retina and V1.  On most machines, a GeneratorSheet.nominal_density of 10
  (used for the Retina) and a RetinotopicSOM.nominal_density of 10 (used for
  V1) should be reasonably fast to run.  The default Retina density of
  24 and V1 density of 40 are set to match the simulation presented in
  Chapter 3 of the CMVC book, but much smaller densities should also
  work well.
  
<pre>
  $ emacs som_retinotopy.ty
  $ diff som_retinotopy.ty~ som_retinotopy.ty
  66c66
  < RetinotopicSOM.nominal_density = locals().get('default_density',40.0)
  ---
  > RetinotopicSOM.nominal_density = locals().get('default_density',10.0)
  69,70c69,70
  < RetinotopicSOM.radius_0 = 13.2/40
  ---
  > RetinotopicSOM.radius_0 = 15.0/40.0

  $ diff som_retinotopy.ty~ som_retinotopy.ty
  65c65
  < GeneratorSheet.nominal_density = 24
  ---
  > GeneratorSheet.nominal_density = 10
  76c76
  < RetinotopicSOM.nominal_density = locals().get('default_density',40.0)
  ---
  > RetinotopicSOM.nominal_density = locals().get('default_density',10.0)
</pre>
-->

<P><li> Next, start the Topographica GUI, telling it to load the
SOM retinotopy simulation:
<pre>
  /home/jbednar/public/topographica/topographica -g som_retinotopy.ty
</pre>

<p></p>
You should see a new window for the GUI:
<p class='center'>
<img src="images/topographica_console.png" alt="Console Window"
align="middle" width="370" height="239">
</p>
<p>
The window and button style will differ on different platforms, but
similar buttons should be provided.
</p>

<p></p>
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
align="middle" WIDTH="615" HEIGHT="457">
</p>

<p>
Each neuron is fully connected to the input units, and thus has a
10x10 array of weights.  Initially, the weights are uniformly random.
</p>

<p></p>
</li>

<li>We can visualize the mapping from the input space into the
cortical space by selecting <span class='t_item'>Center of Gravity</span> from
the <span class='t_item'>Plots</span> menu on the <span
class='w_title'>Topographica Console</span> to get several plots.
These plots show the results of computing the <i>center of gravity</i>
(a.k.a. <i>centroid</i> or <i>center of mass</i>) of the set of input
weights for each neuron.  For instance, in
the <span class='w_title'>Center of Gravity</span>
plot window:

<p class='center'>
<IMG WIDTH="513" HEIGHT="326" SRC="images/som_cog_000000.png"  align="middle" alt="CoG bitmap plots">
</p>

the V1 X CoG plot shows the X location preferred by each neuron, where
black is the minimum (usually coordinate -0.5) and white is the
maximum (usually coordinate 0.5).  Because the initial weight values
are random and fully connected, the center of gravity is typicallly
around the center of the retina, and thus most pixels are a medium
gray in this plot.  The V1 Y CoG plot shows similar measurements for
the Y locations.

<P>The colorful plot labeled "V1 CoG" may be difficult to interpret at
this stage, and we will discuss it further below.  It shows a
false-color visualization of the CoG values, where the amount of red
in the plot is proportional to the X CoG, and the amount of green in
the plot is proportional to the Y CoG.  Where both X and Y are low,
the plot is black or very dark, and where both are high the plot is
yellow (because red and green light together appears yellow).  Most
pixels are a medium green or red at this stage in training.

<P>Easier to interpret at this stage is the <span
class='w_title'>Topographic mapping</span> window, helpfully labeled
"Figure 1".  This plot shows the CoG for each V1 neuron, plotted on
the Retina:

<p class='center'>
<IMG WIDTH="420" HEIGHT="474" SRC="images/som_grid_000000.png" align="middle" alt="CoG bitmap plots">
</p>

All of the neurons have a CoG near the center of the retina, which is
to be expected because the weights are fully connected and evenly
distributed on average.  

<P><li>The behavior of this randomly connected network can be visualized
by plotting the feedforward activation of each neuron, which
represents the SOM Euclidean-distance response function.  Select
<span class='t_item'>Activity</span> from
the <span class='t_item'>Plots</span> menu to get the following plot:

<p class='center'>
<IMG WIDTH="408" HEIGHT="326" SRC="images/som_activity_000000.png" align="middle" alt="Activity at 0">
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
show:

<p class='center'>
<IMG WIDTH="408" HEIGHT="326" SRC="images/som_activity_000001.png" align="middle" alt="Activity at 0">
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
align="middle" WIDTH="615" HEIGHT="457">
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
<img src="images/som_projection_000006.png" alt="Projection window at 1"
align="middle" WIDTH="615" HEIGHT="457">
</p>

Also note that the activation patterns are becoming smoother, since
the weight vectors are now similar between neighboring neurons:

<p class='center'>
<IMG WIDTH="408" HEIGHT="326" SRC="images/som_activity_000006.png" align="middle" alt="Activity at 0">
</p>

<P><li>Continue training for a while and looking at the activation and
weight patterns.  Instead of 1, you can change the
<span
class='t_item'>Run for</span> field to any number to train
several iterations in a batch, e.g. 10.  After 100 iterations, 
updating the <span class='w_title'>Center of Gravity</span> should
result in something like:

<p class='center'>
<IMG WIDTH="513" HEIGHT="326" SRC="images/som_cog_000100.png"  align="middle" alt="CoG bitmap plots">
</p>

The X and Y CoG plots are now smooth, but not yet the axis-aligned gradients
(e.g. left to right) that an optimal topographic mapping would
have. Similarly, the topographic grid plot:

<p class='center'>
<IMG WIDTH="420" HEIGHT="474" SRC="images/som_grid_000100.png" align="middle" alt="Grid at 100">
</p>

shows that the network is now responding to different regions of the
input space, but that most regions of the input space are not covered
properly.  Additional training up to 10000 iterations leads to a flat, square
map:

<p class='center'>
<IMG WIDTH="420" HEIGHT="474" SRC="images/som_grid_010000.png" align="middle" alt="Grid at 10000">
</p>

and by 40000 the map has good coverage of the available portion of the
input space:

<p class='center'>
<IMG WIDTH="420" HEIGHT="474" SRC="images/som_grid_040000.png" align="middle" alt="Grid at 40000">
</p>

<LI>The final projection window at 40000 now shows that each neuron
has developed weights concentrated in a small part of the input space,
matching a prototypical input at one location:

<p class='center'>
<img src="images/som_projection_040000.png" alt="Projection window at 40000"
align="middle" WIDTH="615" HEIGHT="457">
</p>

For this particular example, the topographic mapping for the x
dimension happens to be in the same orientation as the retina, and for
the y dimension happens to be opposite.
For example, responses to patterns in the
upper left of the retina lead to responses in the bottom left of the
cortex.  There is no reason this should be the case in general, and
the map can be flipped or rotated by 90 degrees along any axis with
equivalent results.

<P><LI>Now, re-run the basic simulation by quitting and restarting
Topographica.  This time, change one of the parameter values, either
by editing the <code>som_retinotopy.ty</code> file before starting, or
by typing the command at the Topographica terminal prompt.  For
instance, to see the starting value of the neighborhood radius (from
which all future values are calculated according to exponential
decay), type:

<pre>
  topo.sim['V1'].radius_0
</pre>


You should see an initial value of something like 0.3325 displayed in
your terminal window. Then change this value as you see fit, e.g. to
0.1:

<pre>
  topo.sim['V1'].radius_0=0.1
</pre>

and go through learning again.  (You can also make this change in the Model Editor.) 
With such a small learning radius,
global ordering is unlikely to happen, and one can expect the
topographic grid not to flatten out (despite local order in patches).
<br>
<br>

<P>Similarly, consider changing the learning rate from
<code>V1.alpha_0=0.42</code> to e.g. 1.0.  V1.density and
Retina.density cannot be changed after the simulation has started; to
change those edit the <code>som_retinotopy.ty</code> file as described
in the initial steps above and start Topographica again.

<P>You can also try changing the random.seed() value in the .ty file,
to get a different stream of inputs, or RandomArray.seed(), to get a
different set of initial weights.

<P>Finally, you could change the input pattern to get a different type
of map.  E.g. if an oriented pattern is used, with random
orientations, neurons will become selective for orientation and not
just position.  See the <code>examples/obermayer_pnas90.ty</code> file
for more details. <!--, though that simulation is quite processor-intensive
compared to this one. -->

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
