<H1>LISSOM Orientation Map</H1>

<!-- CEBALERT: Should fix indentation; make standards-compliant so it will -->
<!-- display properly on different browsers (I'll fix spacing at the -->
<!-- same time); sort blockquotes -->

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
orientation map network, which can be done by changing to the
<code>examples/</code> directory and running "make
lissom_oo_or_20000.typ".  Depending on the speed of your machine, you
may want to go out for coffee at this point; on a 3GHz 512MB machine
this training process currently takes a little over an hour.
</p>



<h2>Response of an orientation map</h2>

In this example, we will load a saved network and test its behavior by
presenting different visual input patterns.  We will assume that
Topographica is installed in /home/jbednar/public/topographica/.

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
align="middle" width="496" height="215">
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
<code>examples/lissom_oo_or_20000.typ</code>. This small orientation
map simulation should load in a few seconds, with a 54x54
retina, a 36x36 LGN (composed of one 36x36 OFF channel sheet, and one
36x36 ON channel sheet), and a 48x48 V1 with about two million 
synaptic weights. The architecture can be viewed in the <span
class='w_title'>Model Editor</span> window (which can be selected from
the <span class='t_item'>Simulation</span> menu), but is also shown
below:
<p class='center'>
<img src="images/lissom_network_diagram_oo.png" alt="LISSOM network"
align="middle" width="570" height="412">
</p>

<p></p>
</li>

<li> To see how this network responds to a simple visual image,
select <span class='t_item'>Test pattern</span> from the <span class='t_item'>Simulation</span> menu to get the
<span class='w_title'>Test Pattern</span> window, select a <span class='t_item'>Line</span> <span class='t_item'>Input type</span>, then hit <span class='b_press'>Present</span>:

<p class='center'>
<img src="images/test_pattern_oo.png" alt="Test Pattern window"
align="middle" WIDTH="324" HEIGHT="600">
</p>

<p>
This will present a horizontal line.  
</p>

<p></p>
</li>

<li>To see the result, select <span class='t_item'>Activity</span> from
the <span class='t_item'>Plots</span> menu on the <span class='w_title'>Topographica Console</span> to get:
<p class='center'>
<img src="images/activity_line_oo.png" alt="Response to a line" align="middle" width="424" height="256">
</p>

This window shows the response for each neural area.  

</p><p>In the <span class='t_item'>Retina</span> plot, each
photoreceptor is represented as a pixel whose shade of grey codes the
response level, increasing from black to white.  This pattern is what
was specified in the <span class='w_title'>Test Pattern</span> window.
Similarly, locations in the LGN that have an OFF or ON cell response
to this pattern are shown in the <span class='t_item'>LGNOff</span> and
<span class='t_item'>LGNOn</span> plots.  The Retina appears larger
than the LGN because the borders of the Retina have been
<A HREF="../User_Manual/space.html#edge-buffers"> extended on all
sides</A> so that no LGN has a ConnectionField cut off by the border.
At this stage the response level in <span class='t_item'>V1</span> is
also coded in shades of grey. Note that the V1 response is patchy, as
explained below.  The borders of the LGN were also extended so that no
neuron in V1 would have an afferent ConnectionField cut off by the LGN
border, though this may not be evident because the V1 plot is at a
different scale than the others.

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
presenting 20000 oriented Gaussian patterns at random angles
and positions.  To plot a single neuron, select 
<span class='t_item'>Connection Fields</span> from the <span
class='t_item'>Plots</span> menu, then select <span
class='t_item'>V1</span> from the <span class='t_item'>Sheet</span>
drop-down list. This will plot the synaptic strengths of connections
to the neuron in the center of the cortex (by default):



<p class="center">
<img src="images/unit_weights_0_0_oo.png" alt="Weights of one
neuron" align="middle" WIDTH="566" HEIGHT="266">
</p>

<p> The plot shows the afferent weights to V1 (i.e., connections from
the ON and OFF channels of the LGN, followed by the lateral excitatory
and lateral inhibitory weights to that neuron from nearby neurons in
V1. The afferent weights represent the retinal pattern that would most
excite the neuron.  For this particular neuron, the optimal retinal
stimulus would be a short, bright line oriented at about 40 degrees (2
o'clock) in the center of the retina, although this neuron is not
particularly orientation selective.  </p><p></p></li>

<li>If all neurons had the same weight pattern, the response
would not be patchy -- it would just be a blurred version of the
input (for inputs matching the weight pattern), or blank (for other
inputs). To see what the other neurons look like, select <span
class='t_item'>Projection</span> from the <span
class='t_item'>Plots</span> menu, then select <span
class='t_item'>LGNOnAfferent</span> from the drop-down <span
class='t_item'>Projection</span> list:
  

<p class="center">
<img src="images/projection_oo.png" alt="Afferent weights of many
neurons" align="middle" WIDTH="639" HEIGHT="449">
</p>

This plot shows the afferent weights from the LGN ON sheet for every fifth neuron in each
direction.  You can see that most of the other neurons are selective
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
neuron.  A similar procedure can be performed in the model by selecting
<span class='t_item'>Orientation Preference</span> from the <span
class='t_item'>Plots</span> menu.  This will usually take about 30
seconds to complete; it is normal for the Topographica windows not to
refresh during this time.  Once it completes, you should see:

<p class="center">
<img src="images/oo_or_map.png" alt="Orientation map" width="617" height="292">
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

<li>Now that we have the orientation map, we can see more clearly
why activation patterns are patchy by pressing <span class='b_press'>Present</span>
on the <span class='w_title'>Test pattern</span> window and then looking
at the refreshed image in the <span class='w_title'>Activity</span> window:

<p class="center">
<img src="images/activity_line_oo_or.png" alt="Color-coded response to a line" width="424" height="256" ><br />
<img src="images/or_key_horiz_transparent.png" alt="Orientation key" height="23" width="288">
</p><br>


(Alternatively, if you want to keep the old plot for comparison, you
can make sure that <span class='t_item'>Auto-refresh</span> is not enabled in it, then
generate a new plot by selecting <span class='t_item'>Activity</span> in the
<span class='t_item'>Plots</span> menu of the <span class='w_title'>Topographica Console</span> window.  This technique also applies to all of the other window types as well.)
</p>
<p> The V1 activity plots are colorized now that the orientation map
has been measured.  Each V1 neuron is now color coded by its
orientation, with brighter colors indicating stronger activation.  We
can now see that the neurons responding are indeed those that prefer
orientations similar to the input pattern, and that the response is
patchy because other nearby neurons do not respond.  To be sure of
that, try rotating the image by adjusting the orientation, then present 
it again -- the colors should be different, and match the orientation chosen.
</p>
<p></p>
</li>

<li> If you now <span class='b_press'>Refresh</span> the
<span class='w_title'>Connection Fields</span>
window, you can see that the neuron whose weights we plotted is
located in between two different patches of neurons responding to
different orientations: 


<p class="center">
<img src="images/unit_weights_0_0_oo_or.png" alt="Colorized weights of
one neuron" align="middle" width="566" height="266" ><br />
<img src="images/or_key_horiz_transparent.png" alt="Orientation key" height="23" width="288">
</p>
<p>
Look at the <span class='t_item'>LateralExcitatory</span> weights, which show that
the neurons around the location to the right of the retina's center
are primarily green, while those to the left are primarily red.  Thus
this particular neuron happens to be located on a fracture between two
orientations, which is why its orientation selectivity is low.
Neurons just to the left or right can be selected by changing the
(X,Y) coordinates; these should have higher selectivity.
</p>
<p></p></li>


<li> Now that you have a feel for the various plots, you can try
different input patterns, seeing how the cortex responds to each one.
Just select an <span class='t_item'>Input type</span>, e.g.  <span class='t_item'>Gaussian</span>,
<span class='t_item'>Disk</span>, or <span
class='t_item'>SineGrating</span>, and then hit
<span class='b_press'>Present</span>.

<p> For each <span class='t_item'>Input type</span>, you can change various parameters that
control its size, location, etc.:

</p><blockquote>
<dl compact="compact">
<dt><span class='t_item'>orientation</span>                          </dt><dd> controls the angle (try PI/4 or -PI/4)
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

</dt><dd> controls the brightness (try 0.5 for a sine grating).  Note
that this relatively simple model is very sensitive to the scale, and
scales higher than about 0.5 will result in a broad,
orientation-unselective response.  More complex models (and actual brains!)
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
0.6 to see a reasonable
response from this model V1.  A much larger (and slower) map would
be required to see detailed patterns in the response to most images,
but even with this network you may be able to see some
orientation-specific responses to large contours in the image:
</p>

<p class="center">
<img src="images/natural_image_oo_or.png" alt="Ellen Arthur" align="middle" width="424" height="256" ><br />
</p>

<P>Be aware when comparing the Retina and V1 plots for a photograph
that each processing stage eliminates some of the outer edges of the
image, so that V1 is only looking at the center of the image on the
LGN.
</p></li>

<li>The procedure above allows you to explore the relationship between
the input and the final response after the cortex has settled due to
the lateral connections.  If you want to understand the settling
process itself, you can also visualize how the activity propagates
from the retina to the LGN, from the LGN to V1, and then within V1.
To do this, go to the console window and change the "Run for" value
from 1.0 to 0.05.  Also make sure that there is an <span
class='t_item'>Activity</span> window open, with Auto-refresh enabled.
Now if you hit "Go" repeatedly, you will see the activity arrive first
in the LGN, then in V1, and then gradually change within V1.

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
until the next input is generated at time 1.05.  
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
  ./topographica -g examples/lissom_oo_or.ty
  </code></blockquote>
<p></p>


<p></p></li><li>Next, open an <span class='w_title'>Activity</span> window 
and make sure that it has <span class='t_item'>Auto-refresh</span> enabled.  Unless your machine is 
very slow, also enable <span class='t_item'>Auto-refresh</span> in a
<span class='w_title'>Projection</span> window showing <span
class='t_item'>LGNOnAfferent</span>.  On a very fast machine you could
even <span class='t_item'>Auto-refresh</span> an <span class='w_title'>Orientation Preference</span> window
(not really practical at present).

<p></p></li><li>Now click the mouse into the <span class='t_item'>Learning iterations</span> field
of the <span class='w_title'>Topographica Console</span> window, and press return a few
times, each time looking at
the random input(s) and the response to them in the
<span class='w_title'>Activity</span> window.  The effect on the network weights of
learning this input can be seen in the <span class='w_title'>Projection</span>
window.

<p></p></li><li>With each new input, you should be able to see small changes in the
weights of a few neurons in the <span
class='t_item'>LGNOnAfferent</span> array (by peering closely).  If the changes are too subtle for your taste,
you can make each input have a obvious effect by speeding up learning
to a highly implausible level.  To do this, type: 

<blockquote><code class='to_type'>
V1.projections()['LGNOnAfferent'].learning_rate
</code></blockquote>

in the <span class='t_item'>Command</span> box or at the Topographica
terminal prompt. The current learning rate will be
displayed in your terminal window. Next, type:

<blockquote><code class='to_type'>
V1.projections()['LGNOnAfferent'].learning_rate=200
V1.projections()['LGNOffAfferent'].learning_rate=200
</code></blockquote>

Now each new pattern generated in a
training iteration will nearly wipe out any existing weights.
(It may also be possible to view and change the learning_rate in the
<span class='w_title'>Model Editor</span> window, although that
feature is currently under development.)

<p></p></li><li>For more control over the training inputs, open the
<span class='w_title'>Test Pattern</span> window, select an
<span class='t_item'>Input type</span>, e.g. <span class='t_item'>Disk</span>, and other
parameters as desired.  Then enable <span class='t_item'>Network learning</span> in that
window, and hit <span class='b_press'>Present</span>.  You should again see how
this input changes the weights, and can experiment with different inputs.


<!--CEBHACKALERT: use for learning button not complete -->
<!--
<p><li>Once you have a particular input pattern designed, you can see
how that pattern would affect the cortex over many iterations.  To do
so, press the <span class='b_press'>Use for Training</span> button.  Now when you
train for more iterations you'll see the new pattern and its effect on
the weights.  (Note that the position and orientation of the new
training pattern will always be (**FIXED!) for this simulation, and that
training with (**UPDATE:) a photograph works only for photos named image.pgm.)</li></p>


<p></p></li><li>After a few steps (or to do e.g. 20 steps in a row, change
<span class='t_item'>Learning iterations</span> to 20 and press return), you can
plot (or refresh) an <span class='w_title'>Orientation
Preference</span> map to see what sort of
orientation map has developed.  If you've changed the learning rate to
a high value, or haven't presented many inputs, the map will not
resemble actual animal maps, but it should still have patches
selective for each orientation. 
<p></p></li>

<li>If you are patient, you can even run a full, more realistic,
simulation with your favorite type of input. (**no you can't, or at
least not this way: UPDATE.)  To do this, quit and
start again and change the
<span class='t_item'>Input type</span> as before, but make sure not to change
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
change the <code>nominal_density</code> of V1 from 48 to 150,
and doing:
<blockquote><code class='to_type'>
  ./topographica -g examples/lissom_oo_or.ty
  </code></blockquote>
<p></p>
  
You'll need a lot of memory and a lot of time, but you can then step
through the simulation as above.  The final result after 20000
iterations (requiring several hours, if not days) should be a much
smoother map and neurons that are more orientation selective.  Even
so, the overall organization and function should be similar.
</li></ol>


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
