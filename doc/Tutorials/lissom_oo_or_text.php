<H1>LISSOM Orientation Map</H1>

<!-- CEBALERT: the html in this file is a mix of standards (i.e., it's a mess). -->

<p>
This tutorial shows how to use the
<a href="http://topographica.org/">Topographica</a> software to explore a
simple orientation map simulation using test patterns and weight
plots.  This particular example uses a <a
href="http://nn.cs.utexas.edu/lookup?rflissom">LISSOM model</a>
cortex, although Topographica supports many other models and is easily
extensible for models not yet supported.
</p>

<p>This tutorial assumes that you have already followed the
instructions for <a href="../Downloads/index.html">obtaining and
installing</a> Topographica.  Also, you will need to generate a saved
orientation map network, which can be done by running
<blockquote><code class='to_type'>./topographica -c "targets=['lissom_oo_or_10000.typ']" examples/run.py</code></blockquote>

(on Unix or Mac systems; on Windows, the syntax is slightly different&mdash;see the note about
<A HREF="../Downloads/win32notes.html#unix-commands-on-win">translating Unix shell commands</A>).

<P>Depending on the speed of your machine, you may want to go get a
snack at this point; on a 3GHz 512MB machine this training process
currently takes about half an hour.<!--lodestar: 34m-->
</p>



<h2>Response of an orientation map</h2>

In this example, we will load a saved network and test its behavior by
presenting different visual input patterns.  We will assume that
Topographica is installed in <code>/home/jbednar/public/topographica/</code>.

<ol> 
<p></p>
<li>First, change to your topographica directory, e.g.:

<blockquote><code class='to_type'>cd /home/jbednar/public/topographica/</code></blockquote>
<p></p>
</li>

<li>Next, start the Topographica GUI:
<blockquote><code class='to_type'>
  ./topographica -g
  </code></blockquote>
<p></p>
  
<p class='center'>
<img src="images/topographica_console.png" alt="Console Window"
align="middle" width="426" height="149">
</p>
<p>
The window and button style will differ on different platforms, but
similar buttons should be provided.
</p>
<p></p>
</li>
<li> Next, load the saved network by selecting
selecting <span class='t_item'>Load snapshot</span> from the
<span class='t_item'>Simulation</span> menu and selecting
<code>lissom_oo_or_10000.typ</code> in the examples/ directory. This small orientation
map simulation should load in a few seconds, with a 54x54
retina, a 36x36 LGN (composed of one 36x36 OFF channel sheet, and one
36x36 ON channel sheet), and a 48x48 V1 with about two million 
synaptic weights. The architecture can be viewed in the <span
class='w_title'>Model Editor</span> window (which can be selected from
the <span class='t_item'>Simulation</span> menu), but is also shown
below:
<p class='center'>
<img src="images/lissom_network_diagram_oo.png" alt="LISSOM network"
align="middle" width="569" height="413">
</p>

<p></p>
</li>

<li> To see how this network responds to a simple visual image,
first open an select <a name="Activity-plot"><span
class='t_item'>Activity</span></a> window from
the <span class='t_item'>Plots</span> menu on the <span
class='w_title'>Topographica Console</span>, then 
select <span class='t_item'>Test pattern</span> from the <span
class='t_item'>Simulation</span> menu to get the 
<span class='w_title'>Test Pattern</span> window:

<p class='center'>
<img src="images/test_pattern_oo.png" alt="Test Pattern window"
align="middle" WIDTH="450" HEIGHT="758">
</p>

<p>
Then select a <span class='t_item'>Line</span> <span
class='t_item'>Pattern generator</span>, and hit <span
class='b_press'>Present</span> to present a horizontal line to the
network.  
</p>

<p></p>
</li>

<li>The <a name="Activity-plot"><span class='t_item'>Activity</span></a> 
window should then show the result:
<p class='center'>
<img src="images/activity_line_oo.png" alt="Response to a line" align="middle" width="676" height="372">
</p>

<P>This window shows the response for each neural area.  For now, please
make sure that <span class='t_item'>Strength only</span> is turned on;
it is usually off by default.

<P>As you move your mouse over the plots, information about the
location of the mouse cursor is displayed in the status bar at the
bottom of the window. For these plots, you can see the
<a href="../User_Manual/space.html#matrix-coords">matrix
coordinates</a> (labeled "Unit"),
<a href="../User_Manual/space.html#sheet-coords">sheet coordinates</a>
(labeled "Coord"), and the activity level of the unit currently under
the pointer.

</p><p>In the <span class='t_item'>Retina</span> plot, each
photoreceptor is represented as a pixel whose shade of gray codes the
response level, increasing from black to white.  This pattern is what
was specified in the <span class='w_title'>Test Pattern</span> window.
Similarly, locations in the LGN that have an OFF or ON cell response
to this pattern are shown in the <span class='t_item'>LGNOff</span> and
<span class='t_item'>LGNOn</span> plots.  
At this stage the response level in <span class='t_item'>V1</span> is
also coded in shades of gray, and the numeric values can be found
using the pointer.

<P>From these plots, you can see that the single line presented on the
retina is edge-detected in the LGN, with ON LGN cells responding to
areas brighter than their surround, and OFF LGN cells responding to
areas darker than their surround.  In V1, the response is patchy, as
explained below.
</p>

<p></p>
</li>

<li> To help understand the response patterns in V1, we can look at
the weights to V1 neurons.  These weights were learned previously, by
presenting 10000 pairs of oriented Gaussian patterns at random angles
and positions.  To plot a single neuron, select
<a name="ConnectionFields-plot"><span class='t_item'>Connection Fields</span></a> from the <span
class='t_item'>Plots</span> menu, then select <span
class='t_item'>V1</span> from the <span class='t_item'>Sheet</span>
drop-down list. This will plot the synaptic strengths of connections
to the neuron in the center of the cortex (by default):

<p class="center">
<img src="images/unit_weights_0_0_oo.png" alt="Weights of one
neuron" align="middle" WIDTH="676" HEIGHT="404">
</p>

<P>Again, please make sure for now that <span class='t_item'>Strength
only</span> is turned on; it is usually off by default.

<p> The plot shows the afferent weights to V1 (i.e., connections from
the ON and OFF channels of the LGN), followed by the lateral excitatory
and lateral inhibitory weights to that neuron from nearby neurons in
V1. The afferent weights represent the retinal pattern that would most
excite the neuron.  For the particular neuron shown above, the optimal
retinal stimulus would be a short, bright line oriented at about 180
degrees (horizontal) in the center of the retina.  </p><p></p></li>

<li>If all neurons had the same weight pattern, the response
would not be patchy -- it would just be a blurred version of the
input (for inputs matching the weight pattern), or blank (for other
inputs). To see what the other neurons look like, select 
<a name="Projection-plot"><span class='t_item'>Projection</span></a>
from the <span class='t_item'>Plots</span> menu, then select <span
class='t_item'>LGNOnAfferent</span> from the drop-down <span
class='t_item'>Projection</span> list:
  

<p class="center">
<img src="images/projection_oo.png" alt="Afferent weights of many
neurons" align="middle" WIDTH="669" HEIGHT="627">
</p>

This plot shows the afferent weights from the LGN ON sheet for every fifth neuron in each
direction.  You can see that most of the neurons are selective
for orientation (not just a circular spot), and each has a slightly
different preferred orientation.  This suggests an explanation for why
the response is patchy: neurons preferring orientations other than
the one present on the retina do not respond.  You can also look at
the <span class='t_item'>LateralInhibitory</span> weights instead of
<span class='t_item'>LGNOnAfferent</span>; those are patchy as well because the typical
activity patterns are patchy.

</p><p></p></li><li>To visualize all the neurons at once
in experimental animals, optical imaging experiments measure responses
to a variety of patterns and record the one most effective at stimulating each
neuron.  The results of a similar procedure can be viewed by selecting
<span class='t_item'>Plots</span> > <span class='t_item'>Preference Maps</span> >
<a name="OrientationPreference-plot"><span class='t_item'>Orientation Preference</span></a>:

<p class="center">
<img src="images/oo_or_map.png" alt="Orientation map" width="629" height="413">
</p><br>

<P>
The <span class='t_item'>Orientation Preference</span> plot
is the orientation map for V1 in this model.
Each neuron in the plot is color coded by its preferred orientation,
according to the key shown to the left of the plot.
(If viewing a monochrome printout, see web page for the colors).
</p>

<p> You can see that nearby neurons have similar orientation
preferences, as found in primate visual cortex. The <span
class='t_item'>Orientation Selectivity</span> plot shows the relative
selectivity of each neuron for orientation on an arbitrary scale; you
can see that in this simulation nearly all neurons became orientation
selective.  The <span class='t_item'>Orientation
Preference&Selectivity</span> plot shows the two other Orientation
plots combined -- each neuron is colored with its preferred
orientation, and the stronger the selectivity, the brighter the color.
In this case, because the neurons are strongly selective, the
Preference&Selectivity plot is nearly identical to the Preference plot.

</p><p>
</p></li>

<li>Now that we have looked at the orientation map, we can see more clearly
why activation patterns are patchy by coloring each neuron with its
orientation preference.  To do this, make sure that <span
class='t_item'>Strength only</span> is turned off in the 
<span class='w_title'>Activity</span> window:

<p class="center">
<img src="images/activity_line_oo_or.png" alt="Color-coded response to a line" width="676" height="372" ><br />
<img src="images/or_key_horiz_transparent.png" alt="Orientation key" height="23" width="288">
</p><br>

<p>Each V1 neuron is now color coded by its orientation, with brighter
colors indicating stronger activation.  Additionally, the status bar
beneath the plots now also shows the values of the separate channels
comprising the plot: OrientationPreference (color),
OrientationSelectivity (saturation), and Activity (brightness).

<P>
The color coding allows us to see that the neurons responding are
indeed those that prefer orientations similar to the input pattern,
and that the response is patchy because other nearby neurons do not
respond.  To be sure of that, try selecting a line with a different
orientation, and hit present again -- the colors should be different,
and should match the orientation chosen.
</p>
<p></p>
</li>

<li>If you now turn off <span class='t_item'>Strength only</span>
in the <span class='w_title'>Connection Fields</span>
window, you can see that the neuron whose weights we plotted is
located in a patch of neurons with similar orientation preferences: 

<p class="center">
<img src="images/unit_weights_0_0_oo_or.png" alt="Colorized weights of
one neuron" align="middle" width="676" height="404" ><br />
<img src="images/or_key_horiz_transparent.png" alt="Orientation key" height="23" width="288">
</p><br>

<P> Look at the <span class='t_item'>LateralExcitatory</span> weights,
which show that the neurons near this neuron are nearly all red (horizontal).
<!-- somewhere might want to say this one almost falls on a boundary--> 

<P>
Returning to the <span class='w_title'>Test pattern</span> window,
try presenting a vertical line
(<span_class='t_item'>orientation</span> of <code>pi/2</code>) and
then, in the <span class='w_title'>Activity</span> window, right click
on one of the cyan-colored patches of activity (for instance, around unit
41,24). This will bring up a menu:

<p class="center">
<img src="images/lissom_oo_or_activity_rightclick.png" alt="Right-click menu" align="middle" width="424" height="109" >
</p><br>

<!--CB: should probably be a list-->
<P>The menu offers operations on different parts of the plot:
the first submenu shows operations available on the single selected unit, and
the second shows operations available on the combined (visible) plot. The final
three submenus show operations available on each of the separate channels that
comprise the plot.

<P>Here we are interested to see the connection fields of the unit we selected,
so we choose <span class='t_item'>Connection Fields</span> from the 
<span class='t_item'>Single unit</span> submenu to get a new plot:

<p class="center">
<img src="images/unit_weights_41_24_oo_or.png" alt="Colorized weights of
one neuron" align="middle" width="676" height="404" ><br />
<img src="images/or_key_horiz_transparent.png" alt="Orientation key" height="23" width="288">
</p><br>

<P>This time we can see from the <span class='t_item'>LateralExcitatory</span> weights
that the neurons near this one are all colored cyan (i.e., are selective for vertical).
</li>

<li>
<P>
Right-click menus are available on most plots, and provide a convenient
method of further investigating and understanding the plots. For instance,
on the <span class='w_title'>Orientation Preference</span> window, the 
connection fields of units at any location can easily be visualized, 
allowing one to see the connection fields of units around different features of the map.
<!-- ...do we want to go further or is this tutorial already ready to split into
more optional sections? -->

<P>As another example, an interesting property of orientation maps
measured in animals is that their Fourier spectrums usually show a
ring shape, because the orientations repeat at a constant spatial
frequency in all directions. Selecting <br> <span class='t_item'>Hue
channel: OrientationPreference</span> > <span class='t_item'>Fourier
transform</span>
 from the right-click menu allows us to see the same is true of the map generated
by LISSOM:


<p class="center">
<img src="images/lissom_oo_or_orpref_ft.png" alt="FT of orientation preference map" align="middle" width="420" height="475" >
</p><br>

</li>

<P>Other right-click options allow you to look at the gradient of each
plot (showing where the values change most quickly across the
surface) or the histogram (showing the distribution of values in the
plot), plot it in a separate window or as a 3D wireframe, or to save
the images to disk.

<li> Now that you have a feel for the various plots, you can try
different input patterns, seeing how the cortex responds to each one.
Just select a <span class='t_item'>Pattern generator</span>, e.g.  <span class='t_item'>Gaussian</span>,
<span class='t_item'>Disk</span>, or <span
class='t_item'>SineGrating</span>, and then hit
<span class='b_press'>Present</span>.

<p> For each <span class='t_item'>Pattern generator</span>, you can change various parameters that
control its size, location, etc.:

</p><blockquote>
<dl compact="compact">
<dt><span class='t_item'>orientation</span>                          </dt><dd> controls the angle (try pi/4 or -pi/4)
</dd><dt><span class='t_item'>x</span> and <span class='t_item'>y</span>         </dt><dd> 
control the position on the retina (try 0 or 0.5)
</dd><dt><span class='t_item'>size</span></dt><dd>
controls the overall size of e.g. Gaussians and rings
</dd><dt><span class='t_item'>aspect_ratio</span> </dt><dd>
controls the ratio between width and height; will be scaled by the
  size in both directions
</dd><dt><span class='t_item'>smoothing</span>
</dt><dd> controls the amount of Gaussian falloff around the edges of patterns such as rings and lines
</dd><dt><span class='t_item'>scale</span>

</dt><dd> controls the brightness (try 1.0 for a sine grating).  Note
that this relatively simple model is very sensitive to the scale, and
scales higher than about 1.2 will result in a broad,
orientation-unselective response, while low scales will give no
response.  More complex models (and actual brains!)
are less sensitive to the scale or contrast.
</dd><dt><span class='t_item'>offset</span>                         </dt><dd> is added to every pixel
</dd><dt><span class='t_item'>frequency</span>
</dt><dd> controls frequency of a sine grating or Gabor 
</dd><dt><span class='t_item'>phase</span>                          </dt><dd> controls phase of a sine grating or Gabor 
</dd></dl>
</blockquote>
</p>

<p> 
To present photographs, select a <span class='t_item'>Pattern generator</span> of type
<span class='t_item'>Image</span>. (You can type the path to an image file of your
own (in e.g. PNG, JPG, TIFF, or PGM format) in the <span
class='t_item'>filename</span> box.) For most photographs you will 
need to change the <span class='t_item'>scale</span> to something like
2.0 to see a reasonable
response from this model V1, and you may want to enlarge the image
size to look at details.  A much larger (and slower) map would
be required to see interesting patterns in the response to most images,
but even with this network you may be able to see some
orientation-specific responses to large contours in the image:
</p>

<p class="center">
<img src="images/natural_image_oo_or.png" alt="Ellen Arthur" align="middle" width="676" height="372" ><br />
</p>

<P>Be aware when comparing the Retina and V1 plots for a photograph
that each processing stage eliminates some of the outer edges of the
image, so that V1 is only looking at the center of the image on the
LGN.  You can see the relative sizes by enabling
<span class='t_item'>Sheet coordinates</span>,
which will plot V1 at its true size relative to the LGN, and likewise
for the LGN with respect to the Retina.  (This option is normally
turned off because it makes the plots smaller, but it can be very
helpful for understanding how the sheets relate to each other.)
</p></li>

<li>The procedure above allows you to explore the relationship between
the input and the final response after the cortex has settled due to
the lateral connections.  If you want to understand the settling
process itself, you can also visualize how the activity propagates
from the retina to the LGN, from the LGN to V1, and then within V1.
To do this, first make sure that there is an <span
class='t_item'>Activity</span> window open, with Auto-refresh enabled.
Then go to the console window and hit "Step" repeatedly, you will see
the activity arrive first in the LGN, then in V1, and then gradually
change within V1.  The Step button moves to the next scheduled event
in the simulation, which are at even multiples of 0.05 for this
particular simulation.  You can also type in the specific duration
(e.g. 0.05) to move forward into the "Run for:" box, and hit "Go"
instead.

<P>As explained in the
<A HREF="../User_Manual/time.html">User Manual</A>,
this process is controlled by the network structure and the delays
between nodes.  For simplicity, let's consider time starting at zero.
The first scheduled event is that the Retina will be asked to draw an
input pattern at time 0.05 (the phase of the
<?php classref('topo.sheets.generatorsheet','GeneratorSheet') ?>).  Thus
the first visible activity occurs in the Retina, at 0.05.  The
Retina is connected to the LGN with a delay of 0.05, and so the LGN
responds at 0.10.  Again, the delay from the LGN to V1 is 0.05, so V1
is first activated at time 0.15.  V1 also has self-connections with a
delay of 0.05, and so V1 is then repeatedly activated every 0.05 timesteps.
Eventually, the number of V1 activations reaches a fixed limit for LISSOM
(usually about 10 timesteps), and no further events are generated or consumed
until the next input is generated at time 1.05.  Thus the default
stepsize of 1.0 lets the user see the results after each input pattern
has been presented and the cortex has come to a steady state, but
results can also be examined at a finer timescale.
</li>
</ol>



<h2>Learning (optional)</h2>

The previous examples all used a network trained previously, without
any plasticity enabled.  Many researchers are interested in the
processes of development and plasticity.  These processes can be
studied using the LISSOM model in Topographica as follows.

<p>
</p><ol>

<p></p><li>First, quit from any existing simulation, and start with a fresh copy:

<blockquote><code class='to_type'>
  ./topographica examples/lissom_oo_or.ty -g
  </code></blockquote>
<p></p>


<p></p></li><li>Next, open an <span class='w_title'>Activity</span> window 
and make sure that it has <span class='t_item'>Auto-refresh</span> enabled.  Unless your machine is 
very slow, also enable <span class='t_item'>Auto-refresh</span> in a
<span class='w_title'>Projection</span> window showing <span
class='t_item'>LGNOnAfferent</span>.  On a very fast machine you could
even <span class='t_item'>Auto-refresh</span> an <span class='w_title'>Orientation Preference</span> window
(probably practical only if you reduce the nominal_density of V1).

<p></p></li><li>Now click the mouse into the <span class='t_item'>Learning iterations</span> field
of the <span class='w_title'>Topographica Console</span> window, and hit Go a few
times, each time looking at
the random input(s) and the response to them in the
<span class='w_title'>Activity</span> window.  The effect on the network weights of
learning this input can be seen in the <span class='w_title'>Projection</span>
window.

<p></p></li><li>With each new input, you may be able to see small changes in the
weights of a few neurons in the <span
class='t_item'>LGNOnAfferent</span> array (by peering closely).  If
the changes are too subtle for your taste, you can make each input
have a obvious effect by speeding up learning to a highly implausible
level.  To do this, open the <span class='w_title'>Model Editor</span>
window, right click on the LGNOnAfferent projection, and change
Learning Rate from the default 0.48 to 200, and then do the same for
the LGNOffAfferent projection.  You can also do the same from the
terminal, or from the <span class='w_title'>Command Prompt</span>
window available from the <span class='t_item'>Simulation</span> menu:

<blockquote><code class='to_type'>
topo.sim['V1'].projections('LGNOnAfferent').learning_rate=200
topo.sim['V1'].projections('LGNOffAfferent').learning_rate=200
</code></blockquote>

Now each new pattern generated in a
training iteration will nearly wipe out any existing weights.

<p></p></li><li>For more control over the training inputs, open the 
<span class='w_title'>Test Pattern</span> window, select a
<span class='t_item'>Pattern generator</span>, e.g. <span class='t_item'>Disk</span>, and other
parameters as desired.  Then enable <span class='t_item'>Learning</span> in that
window, and hit <span class='b_press'>Present</span>.  You should again see how
this input changes the weights, and can experiment with different inputs.

<!--CEBHACKALERT: need to support dynamic params in the ME for this to be useful -->
<!--
<p><li>Once you have a particular input pattern designed, you can see
how that pattern would affect the cortex over many iterations.  To do
so, right click on the Retina and select a new pattern for the <span
class='t_item'>Input Generator</span> item, then right click on that
item and modify any of its parameters you like.  At present the Model
Editor does not support dynamic parameters (such as random positions
and orientations); to choose those you will need to edit the .ty
script file for the simulation.
-->

<p></p></li><li>After a few steps,
<!--
(or to do e.g. 20 steps in a row, change
<span class='t_item'>Learning iterations</span> to 20 and press return)
-->you can
plot (or refresh) an <span class='w_title'>Orientation
Preference</span> map to see what sort of
orientation map has developed.  (Press the 'Refresh' button next to
the <span class='t_item'>Update command</span> item if no plot is visible when
first opening the window.  Measuring a new map will usually take about 15
seconds to complete.)  If you've changed the learning rate to
a high value, or haven't presented many inputs, the map will not
resemble actual animal maps, but it should still have patches
selective for each orientation.
<p></p></li>


<!--
<li>If you are patient, you can even run a full, more realistic,
simulation with your favorite type of input. (**no you can't, or at
least not this way: UPDATE.)  To do this, quit and
start again and change the
<span class='t_item'>Pattern generator</span> as before, but make sure not to change
<code>alpha_input</code>.  Then you can change
<span class='t_item'>Learning iterations</span> to 10000 and ** <span class='b_press'>Train</span>), to see how
a full simulation would work with your new inputs.  If you hit the
<span class='b_press'>Activity</span> button ** while it's training, you'll see a window
pop up when it's done (which will be at least several minutes, for
recent machines, or even longer with older machines).  If you are less
patient, try doing 1000 iterations at a time instead before looking at
an Orientation Map</b></span>.<p></p></li>
-->

<p><li> If you are <em>really</em> patient, you can change the number
of units to something closer to real primate cortex, by quitting,
editing the Python code file <code>examples/lissom_oo_or.ty</code> to
change the <code>nominal_density</code> of V1 from 48 to 142,
and doing:
<blockquote><code class='to_type'>
  ./topographica examples/lissom_oo_or.ty -g
  </code></blockquote>
<p></p>
  
You'll need about a gigabyte of memory and a lot of time, but you can then step
through the simulation as above.  The final result after 10000
iterations (requiring about half a day on a 3GHz machine) should be a much
smoother map and neurons that are more orientation selective.  Even
so, the overall organization and function should be similar.
</li></ol>


<h2>Exploring further</h2>

<p> Topographica comes with additional examples, and more are
currently being added.  In particular, the above examples work
in nearly the same way with the simpler <code>lissom_or.ty</code>
model.  Any valid Python code can
be used to control and extend Topographica; documentation for Python and existing Topographica commands
can be accessed from the <span class='t_item'>Help</span> menu of the
<span class='w_title'>Topographica Console</span> window.
<p>
 Please contact 
<A HREF="mailto:&#106&#98&#101&#100&#110&#97&#114&#64&#105&#110&#102&#46&#101&#100&#46&#97&#99&#46&#117&#107?subject=Comments%20on%20Topographica%20tutorial">&#106&#98&#101&#100&#110&#97&#114&#64&#105&#110&#102&#46&#101&#100&#46&#97&#99&#46&#117&#107</a>
if you have questions or suggestions about the software or this
tutorial.
</p>
