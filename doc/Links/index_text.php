<P>

<P>The development of Topographica was supported in part by the
U.S.
<A TARGET="_top" HREF="http://www.nimh.nih.gov">
National Institutes of Mental Health</A> under
<A TARGET="_top" HREF="http://www.nimh.nih.gov/neuroinformatics">
Human Brain Project</A>
grant 1R01-MH66991, and by the U.S.
<A TARGET="_top" HREF="http://www.nsf.gov">
National Science Foundation</A> under
grant IIS-9811478.  

<P>Educational applications of Topographica are supported in part by
the University of Edinburgh <A TARGET="_top"
HREF="http://anc.ed.ac.uk/neuroinformatics">Doctoral Training Centre
in Neuroinformatics</A>, with funding from the <A TARGET="_top"
HREF="http://www.epsrc.ac.uk/">Engineering and Physical Sciences
Research Council</A> and the <A TARGET="_top"
HREF="http://www.mrc.ac.uk/">Medical Research council</A> through the
<A TARGET="_top"
HREF="http://www.epsrc.ac.uk/ResearchFunding/Programmes/LifeSciencesInterface/">
Life Sciences Interface</A>.  For sample assignments see the 
<A  TARGET="_TOP"
href="http://www.inf.ed.ac.uk/teaching/courses/cnv/">web page</A>
for the course
<A  TARGET="_TOP" href="http://www.inf.ed.ac.uk/teaching/courses/cnv/">Computational
Neuroscience of Vision (CNV)</A> offered by the
<A TARGET="_TOP" HREF="http://www.inf.ed.ac.uk">School of
Informatics</A> of the 
<A TARGET="_TOP" HREF="http://www.ed.ac.uk">University of Edinburgh</A>.

<P>If you use this software in work leading to an academic
publication, please cite this reference:

<pre>
@Article{bednar:neurocomputing04-sw,
  author       = "James A. Bednar and Yoonsuck Choe and Judah {De Paula}
                  and Risto Miikkulainen and Jefferson Provost and Tal
                  Tversky",
  title	       = "Modeling Cortical Maps with {Topographica}",
  journal      = "Neurocomputing",
  year	       = 2004,
  pages        = "1129--1135",
  url	       = "<A TARGET="_top" HREF="http://nn.cs.utexas.edu/keyword?bednar:neurocomputing04-sw">http://nn.cs.utexas.edu/keyword?bednar:neurocomputing04-sw</A>",
}
</pre>

<P>
<A TARGET="_TOP" HREF="http://www.computationalmaps.org">
      <IMG SRC="../images/cmvc-cover-icon.jpg" ALT="Computational Maps in the Visual Cortex (2005) Miikkulainen, Bednar, Choe, and Sirosh" WIDTH="162" HEIGHT="251" BORDER="0" ALIGN="RIGHT"></a>
Many of the ideas in Topographica were developed in conjunction with our
new book:
<P><blockquote>
<A NAME="miikkulainen:book05">Risto</A>
  Miikkulainen, James&nbsp;A. Bednar, Yoonsuck Choe, and Joseph Sirosh.
<A TARGET="_top" HREF="http://computationalmaps.org"><CITE>Computational Maps in the Visual
  Cortex</CITE></A>.
Springer, Berlin, 2005.
</blockquote>
<P>The book has background on cortical maps in general, descriptions of
the various levels of modeling, and a detailed presentation of the
scaling equations that underlie Sheet coordinates 
(which are also described in
<A TARGET="_top" HREF="http://nn.cs.utexas.edu/keyword?bednar:neuroinformatics04">Bednar et al.
<CITE>Neuroinformatics</CITE>, 2:275-302, 2004</A>).

<P>Other useful simulators:

<dl>
  <dt><A target="_top" HREF="http://kacy.neuro.duke.edu/">Neuron</A> and
      <A TARGET="_top" HREF="http://www.genesis-sim.org/GENESIS">GENESIS</A></dt>
  <dd>Detailed low-level modeling of neurons and small networks.  It is possible
   to use these simulators for topographic maps, but the computational
   requirements are usually extremely high, and typical users simulate
   much smaller networks.  Note that there are now (3/2007) Python
   bindings for Neuron, so it should be practical to wrap a Neuron
   simulation into a Topographica Sheet for analysis.<BR><BR>
  <dt><A TARGET="_top" HREF="http://askja.bu.edu/catacomb">Catacomb</A></dt>
  <dd>Highly graphical Java-based simulator covering numerous levels,
    from ion channels to behavioral experiments.  Can be used for some
    of the same types of models supported by Topographica, but does
    not have an explicit focus on topographically organized areas.<BR><BR>
  <dt><A TARGET="_top" HREF="http://www.nest-initiative.org">NEST</A></dt>
  <dd>NEST (formerly called BLISS) is a general-purpose simulator for
    large networks of neurons, but without an explicit focus on
    topography.  NEST is based on a custom stack-based scripting
    language (like RPN calculators or PostScript) that is not nearly
    as friendly as Python, and requires much more of the simulation
    code to be written in C.  On the other hand, NEST does provide
    many useful, high-performance primitives, has good parallel
    computer support, and can be particularly useful for models that
    do not fit Topographica's abstractions closely.  NEST now has a
    Python interface, which can be used to wrap a spiking NEST
    simulation as a Topographica sheet.
    <BR><BR>
  <dt><A TARGET="_top" HREF="http://ilab.usc.edu/toolkit/documentation.shtml">iNVT</A></dt>
  <dd>iLab Neuromorphic Vision Toolkit is a high-performance
    computer-vision oriented C++ toolkit from Koch and Itti with support
    for saliency maps for modeling attention.  It has a strong focus
    on topographically organized regions, but at a high level of
    abstraction, and without specific support for learning and
    development.  It also requires more time-consuming and less
    flexible development in C++.<BR><BR>
  <dt><A TARGET="_top" HREF="http://www.cs.cmu.edu/~dr/Lens">LENS</A></dt>
  <dd>Simple, basic artificial neural-network simulator (primarily
    abstract backpropagation networks, but also has support for
    Kohonen SOM models of topographic maps).<BR><BR>
</dl>

