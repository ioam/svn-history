Matlab and other files used by lissom_whisker_barrels.ty
Stuart P. Wilson, August 2007

_______________________________________________________________________________

sweep.m

This is the main function used by matlab to construct whisker input
patterns. 

For each of w^2 whiskers, gang^2 ganglion cells are defined as a ring
network each with a maximally effective angle (MEA) of whisker
deflection of the whisker. This is held in pref_ang_vect as a
Cartesian co-ordinate (x,y), where the first cell's MEA is 0 rad and
the rest are assigned anti-clockwise (plot pref_ang_vect x vs y to see
the ring).

sweep.m takes as an argument a stimulus surface (surface) which for
the thesis was a 3D pipe with a Gaussian fall-off. 

A deflection vector is constructed by sampling the height of this
surface in a regular w x w array (whiskers(:,:)) which starts at a
central region of zeros corresponding to the centre of the pipe and
moves outwards, proportional to speed and time, in direction t.  A dot
product (rectify = 1 for thesis sims, i.e. half-wave-rectified
dot-product) between the MEA of each ganglion cell, for each whisker
is returned in a matrix called rates (number of ganglion cells by
number of whiskers). If active_whisker is 0, the ring network for each
whisker is stimulated, else only specified whiskers are stimulated.

No manipulations to topography are made in sweep; it simply stores the
firing rates.

_______________________________________________________________________________

sweep_anticor.m, sweep_random.m, sweep_unccor.m

These functions are used in place of sweep.m for the experimental
training patterns reported in the thesis. 

These are all exactly the same as sweep but vary the correlations as
reported in the thesis, as their names suggest. In the anticorrelated
condition (..._antcor.m), the central whisker in the array (whisker 5
in a 3x3 array) is given a deflection vector which is offset from the
others by 180 degrees. In the random condition (..._random.m) the
whiskers defelection angles are all independently randomised, and in
the uncorrelated condition (..._uncor.m), only the central whisker is
randomised where all others are correlated as normal.  

It is important to note that these conditions affect only the *angle*
at which the various whiskers are deflected. However the length of the
deflection vector is still defined by moving over the stimulus surface
so the spatial correlations are unaffected by randomisations and
offsets.

At they stand, I don't think that these conditions are appropriate for
the lagged model as randomisations will occur on ecach time step.

_______________________________________________________________________________

pipe.m

This function creates the stimulus surface.

It returns a 2D array (surf_size^2) corresponding to a 3D surface
where the value held at each co-ordinate is the height, or efficacy
with which to affect a whisker deflection (range 0 to max. 1). A 1D
profile is defined which is rotated around the surface centre to
create a circular 'object'. 

Arguments for defining this profile are sigma_ON and sigma_OFF which
define the spread of two Gaussians that could define the 1D profile,
offset from one-another to fit the firing of the Rapidly Adapting
Ganglion cell ON and OFF popoulations from the thesis (OFF_MAX is the
peak of the RA OFF Gaussian). For simulations in the thesis however,
OFF_MAX is set to zero so there is actually only the one Gaussian
component to the pipe. This is difficult to explain in text, but try
changing the paramaters and using mesh(pipe(...)) to see the
surface. A 'hole' of zeros is 'cut' into the surface to be the centre
of the pipe, which is slightly larger than the size of the whisker
array (argument w).   



_______________________________________________________________________________

generate_barrelettes.m

This function remaps the firing rates onto the input sheet.

It determines at what co-ordinate on the input sheet the firing rates
for each ganglion cell are mapped to. The sheet is split into
barrelette regions, 1 for each whisker with the whiskerpad somatotopy
maintained, and the rates are mapped to a random location within each
region.  

Within-barrelette randomisation is given by shuf, which should be the
output of the function shuffle.m.  

_______________________________________________________________________________

shuffle.m

This function returns an array,r, of randomly permuted co-ordinates
(1:gang) for each whisker, for use in
generate_barrlettes.m. Randomisation of ganglion cell co-ordinates
should be used only once in a simulation.

So either shuffle.m is only called once, or it is always called with
the same random seed; the 'seed' argument... seed is 5489 for all sims
reported in the thesis although others were used for validation.   

_______________________________________________________________________________

test_deflections.m

This function is the same as sweep, but is used for testing the
deflection preference of each cortical unit in the model, with a
constant deflection vector of unit length 1 (i.e. no surface). It is
used by Topographica to cycle through each angular deflection (t) for
each whisker (active_whisker) on the array. 

This function is probably not neccessary... instead sweep could simply
be given a uniform input surface of ones. 

_______________________________________________________________________________

ganglion_labels.m

This function is used for colorizing the ganglion cells in
Topographica, i.e. by performing exactly the same remapping of
ganglion cell positions to that of generate_barrelettes.m, again using
the same instance of shuffle.m. Instead of returning firing rates
however, ganglion_labels.m returns an array which holds the MEA
(between 0 and 2*pi) for the ganglion cell at each co-ordinate on the
input sheet.


_______________________________________________________________________________

whiskerbot_frame.m, plus wbot_data_new.mat, and other .mat files 

The .mat files contain WhiskerBot data used to generate the thesis
plots, included primarily as examples.

whiskerbot_frame.m is rather a hacky way of plugging whiskerbot data
into the model. Data is stored in a .mat file from various whiskerbot
sims which I have conducted, as strain vectors in a series of
time-steps as whiskerbot navigates its environment. Strains are from
horizontal and vertical servos. The PatternGenerator class
WhiskerBotData() fetches the strains from the .mat file, and then calls
whiskerbot_frame.m which computes the ganglion unit firing rates with
whiskerbot strain data.  

To test the network on whiskerbot strains, jsut open up a test pattern
window in Topographica, and scroll to WhiskerBotData as the pattern
generator. whiskerBot_Data refers to one of the saved whiskerbot
simulations (i.e. 1 2 3 4 or 5), time_step refers to the whiskerBot
sim a a given time frame (0 to 50 (ms) in the thesis sims), and the
whiskerBot_gain parameter can be used to amplify the test_pattern;
this was useful in development for earlier whiskerBot sims where
deflections of the whiskers were poorly controlled. Gain = 1 or less
should be fine for the current data.





