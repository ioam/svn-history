<H1>Plotting and visualization</H1>

<P>Topographica includes a general-purpose system for managing and
plotting visualizations of Sheets and Projections.  New types of plots
can be added easily, without any GUI programming, allowing users to
visualize any quantities of interest.

<H2>Basic plots</H2>

<P>The basic plots useful for nearly any model are demonstrated in the
<A HREF="../Tutorials/lissom_oo_or.html">LISSOM tutorial</A>:

<dl>
<dt><A HREF="../Tutorials/lissom_oo_or.html#Activity-plot">Activity</A></dt>
<dd>Plots the activity level of each unit.
<dt><A HREF="../Tutorials/lissom_oo_or.html#ConnectionFields-plot">Connection Fields</A></dt>
<dd>Plots the strength of each weight in each ConnectionField of one unit.
<dt><A HREF="../Tutorials/lissom_oo_or.html#Projection-plot">Projection</A></dt>
<dd>Plots an array of ConnectionFields making up a Projection to one Sheet.
<dt>ProjectionActivity</dt>
<dd>Plots the contribution from each Projection to the activity of one Sheet.
</dl>  

<P>As an example, the most commonly used plot is Activity:

<center>
<img src="images/lissom_oo_or_10000_activity_mono_pointer.png" WIDTH="676" HEIGHT="366">
</center>

<P>This group of plots (a "PlotGroup") includes one plot per Sheet,
and this particular simulation has four Sheets.  Each plot is a bitmap
representation of the matrix that makes up that Sheet.  Moving the
mouse over each image will show the coordinates at that location, as
well as the value of the plot at that point.  Note that two sets of
coordinates are shown: integer
<A HREF="space.html#matrix-coords">matrix coordinates</A>, which show
the internal layout of units within the Sheet, starting at the upper
left, and floating-point <A HREF="space.html#sheet-coords">sheet
coordinates</A>, which show the Topographica density-independent
coordinates used when specifying parameters in scripts and the GUI
(with 0.0,0.0 usually at the center).  Right clicking at the location
shown (usually control-click on a 1-button Mac system) would allow the
user to open a ConnectionField plot for the indicated unit, as well as
run other analyses or visualizations of this unit or Sheet.

<P>By default, the Activity plot typically shows other information as well:

<center>
<img src="images/lissom_oo_or_10000_activity.png" WIDTH="676" HEIGHT="366">
</center>

<P>Here the color of each unit in V1 is determined by that unit's
orientation preference, so that one can see that different input
orientations result in different types of neurons activated.  The
"Activity" plot is actually specified as a combination of three
SheetViews on different <i>channels</i>:

<ul>
<li>Strength: Activity
<li>Hue: OrientationPreference
<li>Confidence: OrientationSelectivity
</ul>

<P>That is, the primary plot (the Strength channel) is Activity, but
it is colorized with the OrientationPreference (the Hue channel).  The
amount of colorization depends on the OrientationSelectivity (the
Confidence channel), which is appropriate because unselective neurons
then show up white.  The monochrome plot shown first above was
obtained by toggling the "Strength only" button, which disables Hue and
Confidence.

<P>For a plot with multiple channels, moving the mouse over the bitmap
will show the values in all of the available channels, and the
right-click menu will allow you to see what channels are available,
and to plot or analyze any of the channels independently.


<H2>Preference map plots</H2>

<P>The basic plots display data that is already available within
Topographica, to visualize the structure or behavior of the model
directly. Another important type of visualization is preference map
plots, which measure and show the input patterns to which a neural
unit responds most strongly.  That is, they are an indirect
measurement based on actively providing a stimulus and measuring the
response.  These maps are calculated using a
<a HREF="#measuring-preference-maps">general-purpose preference map
analysis package</a>, described below, and are primarily specified in
<A HREF="../Reference_Manual/topo.commands.analysis-module.html">
topo/commands/analysis.py</A>. The available plots include:

<dl>
<dt>Position Preference</dt>
<dd>Measure preference for the X and Y position of a Gaussian.
<dt>Center of Gravity</dt>
<dd>Measure the center of gravity of each ConnectionField in a Projection to one Sheet.
<dt><A HREF="../Tutorials/lissom_oo_or.html#OrientationPreference-plot">Orientation Preference</A></dt>
<dd>Measure preference for sine grating orientation.
<dt>Ocular Preference</dt>
<dd>Measure preference for sine gratings between two eyes.
<dt>Spatial Frequency Preference</dt>
<dd>Measure preference for sine grating frequency.
<dt>PhaseDisparity Preference</dt>
<dd>Measure preference for sine gratings differing in phase between two sheets.
</dl>


<H2>Tuning curve plots</H2>

<P>The above plots are all visualized as a two-dimensional array of
values.  Other common plots are visualized as a set of one-dimensional
curves, including:

<dl>
<dt>Orientation Tuning Fullfield</dt>
<dd>Plot orientation tuning curves for a specific unit, measured using full-field sine gratings. Although the data takes a long time to collect, once it is ready the plots are available immediately for any unit.
<dt>Orientation Tuning</dt>
<dd>Measure orientation tuning for a specific unit at different contrasts, using a pattern chosen to match the preferences of that unit.
<dt>Size Tuning</dt>
<dd>Measure the size preference for a specific unit.
<dt>Contrast Response</dt>
<dd>Measure the contrast response function for a specific unit.
</dl>

<P>Each of these plots shows the properties of one user-selectable
unit.  For instance, the Orientation Tuning Fullfield plot shows how
the response of that unit varies with orientation and contrast:

<center>
<img src="images/or_tuning.png" WIDTH="550" HEIGHT="447">
</center>

<P>Here each curve represents one value of contrast tested, and each
data point on the curve represents the response of this unit to an
input of the specified contrast and orientation, as a maximum over all
phases tested.

<P>The tuning curve plots are measured just as the preference map
plots are (and using the same code), but they are visualized in a
different way.


<H2>Changing existing plots</H2>

<P>The available plots are all specified in a general way that allows
users to change the details of how the data is visualized.  Each plot
has an associated template that specifies a command to run to generate
the data, and then how to visualize the results.

<P>The command used is shown in the plot window as "update command",
where users can add or change parameters or command names as needed.
For instance, if you want to reduce the number of sine grating phases
used when measuring orientation maps, say, from 18 to 8, you can
change the string in the Orientation Preference window from
<code>measure_or_pref()</code> to
<code>measure_or_pref(num_phase=8)</code>.  The next time the plot is
refreshed, the new value will be used instead.  To see what options
are available for each command, see
<A HREF="../Reference_Manual/topo.commands.analysis-module.html">
topo/commands/analysis.py</A>.

<P> If you often need to change the parameters for map or curve
measurement, then you can do that easily without modifying your copy
of Topographica by putting appropriate lines into the .ty script to
which they apply.  For instance, the default parameters used in most
preference map measurement commands present each pattern for only a
very short duration and turn off the response function, which works
well with the example files because it results in a linear response
(no threshold function and no lateral interactions) and thus makes the
results independent of the input scale and offset.  If this approach
is not valid for your own model, then you can change the duration for
which sine gratings are presented to 1.0, and turn on the response
function by default:

<pre>
  from topo.plotting.templates import plotgroup_templates
  plotgroup_templates["Orientation Preference"].command=
      "measure_or_pref(scale=0.75,offset=0.5,display=False,
       pattern_presenter=PatternPresenter(
           pattern_generator=SineGrating(),apply_output_fn=True,
           duration=1.0))"
</pre>

<P>

<P>Of course, the specific parameters here can be anything you want,
and you can do it for any plot group.

<P>Similarly, you can change the specific types of data used in each
plot. For instance, you can remove the default OrientationPreference
subplot from Activity plots using:
<pre>
  from topo.plotting.templates import plotgroup_templates
  plotgroup_templates["Orientation Preference"].plot_templates['Color']=None
  plotgroup_templates["Orientation Preference"].plot_templates['Confidence']=None
</pre>


<P>You can also put lines like these into
<a href="commandline.html#toporc">$HOME/.topographicarc</a>, if you find
that you always want different defaults than Topographica's, for all
scripts that you run.


<H2><a name="measuring-preference-maps">Adding a new plot</a></H2>

<P>The types of plots included with Topographica are only examples,
and it is quite straightforward to add a new type of preference map
plot.  As a reference, here is an implementation of Orientation
Preference plots:
  
<font size=-1><pre>
1. pgt= new_pgt(name='Orientation Preference',category="Preference Maps",
                doc='Measure preference for sine grating orientation.',
2.              command='measure_or_pref()')
3. pgt.add_plot('Orientation Preference',[('Hue','OrientationPreference')])
4. pgt.add_plot('Orientation Preference&Selectivity',[('Hue','OrientationPreference'),
                                                      ('Confidence','OrientationSelectivity')])
5. pgt.add_plot('Orientation Selectivity',[('Strength','OrientationSelectivity')])
6. pgt.add_static_image('Color Key','topo/commands/or_key_white_vert_small.png')
   
   
7. def measure_or_pref(num_phase=18,num_orientation=4,frequencies=[2.4],
                       scale=0.3,offset=0.0,display=False,weighted_average=True,
8.                     pattern_presenter=PatternPresenter(pattern_generator=SineGrating(),
                           apply_output_fn=False,duration=0.175)):
       step_phase=2*pi/num_phase
       step_orientation=pi/num_orientation
   
9.     feature_values = [Feature(name="frequency",values=frequencies),
                         Feature(name="orientation",range=(0.0,pi),step=step_orientation,cyclic=True),
                         Feature(name="phase",range=(0.0,2*pi),step=step_phase,cyclic=True)]
   
10.    param_dict = {"scale":scale,"offset":offset}
11.    x=FeatureMaps(feature_values)
       x.collect_feature_responses(pattern_presenter,param_dict,display,weighted_average)
</pre></font>

<P>What the first part of this code (the PlotGroupTemplate) does is:

<ol>
<li>Declare that the Orientation Preference plot group should go on the
  Preference Maps menu, with the indicated help string
<li>Declare that before trying to plot this data, generate it by
  calling the command "measure_or_pref", which is defined next.
<li>To this plot group, add up to one plot per Sheet named
  "Orientation Preference", plotting any SheetView named
  OrientationPreference in color (as the Hue channel).
<li>Add up to one more plot per Sheet, this time plotting the
  Orientation in the Hue channel and the Orientation Selectivity in
  the Confidence channel (so that unselective neurons show up white).
<li>Add up to one more plot per Sheet, this time plotting the
  the Orientation Selectivity by itself in grayscale (as a Strength).
<li>Add a color key as a static image appended to every plot.
</ol>

<P>The rest of the code specifies actual procedure for measuring the
appropriate data:

<ol start=7>
<li>Declare the parameters accepted by measure_or_pref()
<li>Define the default object that will generate input patterns, in
  this case sine gratings (but any other PatternGenerator can also be used).
<li>Specify the ranges of parameter values to be tested -- each of
  these defines one possible map (FrequencyPreference,
  OrientationPreference, and PhasePreference, in this case).  The
  contents of each map will be an estimate of the value of this
  parameter that will most strongly activate the corresponding unit.
<li>Add a few more parameter values that will not be varied (and thus
  will not generate preference maps).
<li>Present all combinations of feature values and collate the responses.
</ol>

<P>The preference for any input pattern can be measured using nearly
identical code, just selecting a different PatternGenerator and
specifying a different list of features to vary.  For each feature,
you will need to know the range and number of steps you want to test,
plus whether it is cyclic (i.e. wraps back around to zero eventually,
and is thus best visualized as a Hue).

<P>The data for plotting can also be calculated in any other way
(ignoring FeatureMaps and PatternPresenter altogether), as long as it
results in a SheetView added to the appropriate sheet_view_dict and
specified in the template.  For instance, the
<A HREF="../Reference_Manual/topo.commands.analysis-module.html#measure_cog">
measure_cog</A> command used in Center of Gravity plots simply looks
at each ConnectionField individually, computes its center of gravity,
and builds a SheetView out of that (rather than presenting any input
patterns).
