<H1>Publishing Topographica results</H1>

<P>While many people will want to use Topographica for demonstrations,
class tutorials, small projects, etc., many projects are expected to
lead to a publication eventually.  There is still substantial work to
be done to make Topographica output more useful for publications
(volunteers welcome!); many of the visualizations, etc. are currently
most appropriate on screen rather than in a printout.  This section
describes how to produce publication-quality results from the current
simulator.  If you follow these guidelines, you should end up with
smaller file sizes, faster document generation, and better quality.

<P>Before discussing Topographica-specific tips, we first provide
background on image formats and image plotting in general.  These
considerations apply to any image displayed on screen or in a paper.


<H2>Image types: photos, bitmaps, and vector graphics</H2>

<P>Before working with any graphical software, it is crucial to
understand the three basic types of computer graphics images, which
determine the file formats and programs that are appropriate for a
particular task.  The three types and the recommended formats are:


<P>
<TABLE>
<TR>
<TH><b>Type</b></TH>
<TH><b>Description</b></TH>
<TH><b>Examples</b></TH>
<TH><b>Still formats</b></TH>
<TH><b>Animated formats</b></TH>

<TR><TD><B>Photographic bitmaps</B></TD>
<TD>smooth, continuously-varying bitmapped images, with lots of colors</TD>
<TD>photographs, photorealistic renderings, scans</TD>
<TD>JPEG</TD>
<TD>MPEG</TD>

<TR><TD><B>Indexed-color bitmaps</B></TD>

<TD>sharp-edged bitmapped images with only a few colors</TD> 
<TD>screenshots, 80's-style video games, icons</TD>
<TD>PNG, GIF (if colors<256), TIFF, BMP</TD>
<TD>GIF89a, MNG</TD>

<TR><TD><B>Vector/structured graphics</B></TD>
<TD>sharp-edged diagrams/text that is resolution-independent,
   i.e. not bitmapped and intended to display well on both the
   screen and on a printer.</TD>
<TD>text, diagrams, charts, graphs</TD>
<TD>SVG, PDF, EPS, PostScript, FIG</TD>
<TD>Flash</TD>
</TABLE>

<P>Each of these three categories needs to be treated very
differently, and if you use an image from one category with a format
or program suitable for another, the result will have much lower
quality and a much larger file size than it would with the correct
format.  For instance, if you are drawing a box-and-arrow diagram to
be used in a printed document and save it in type GIF, the result will
have ugly "jaggies" and will look quite unprofessional.  The same
simple drawing saved in type JPEG will have little "halos" and
"ringing" around all of the sharp borders if you look closely, and
solid color areas will have "speckles" and will not look uniform,
especially in a printout. Plus the file size will be very large in
JPEG and GIF for any reasonable quality printed version.  So for such
a drawing, a vector drawing program is the only acceptable choice.  On
the other hand, vector drawing programs do not generally offer any
benefits for photographs, for which JPEG is a great choice.  But JPEG
is a very bad choice for screenshots, as it will introduce the
above-mentioned artifacts, and PNG works well for those.

<P>Overuse of JPEG is probably the most common mistake; see the
<a href="http://www.faqs.org/faqs/jpeg-faq/part1/section-3.html">JPEG
FAQ</a> for more information about when <strong>not</strong> to use
it.  Note that the most important time to consider the format is when
you first create the file.  Once a file is in JPEG format, it will
have artifacts forever, even if later converted to a non-lossy format.
And once a file is in GIF format, it will have limited color
resolution, even if later converted to JPEG or PNG.  Using PNG by
default works well, switching to JPEG for photo-like images and PDF or
SVG for diagrams when appropriate.


<H2>Printed versus displayed graphics (white versus black backgrounds)</H2>

<P>Display screens like CRTs create images by combining different
colors of light, starting from a black background and adding more red,
green, and/or blue light until the image becomes white.  (LCD displays
are similar, though the light that they use is often initially white
and then filtered into these three colors.)  This process is called
<A HREF="http://en.wikipedia.org/wiki/Additive_color"> additive color
mixing</A>.  The result is that bright colors and bright white are
both very visible against a black background on a CRT; they are both
very different from the default state of the screen.

<P>Diagrams on printed paper use
<A HREF="http://en.wikipedia.org/wiki/Subtractive_color"> subtractive
color mixing</A> -- the paper initially reflects white light (all
colors of light), and then ink put on it removes more and more of
certain colors of light until none remain, at which case black is
perceived.  In this case very bright colors (with lots of color ink)
and black both show up well against white.  But each color is
difficult to distinguish from black, because both bright colors and
black have large amounts of ink, and so bright colors on a black
background is a poor choice for subtractive color.

<P>The practical effect is that diagrams and plots displayed onscreen
should have white or colored lines or patches against a black
background, while those printed on paper should have black or colored
lines or patches against a white background.  Only in those cases will
colors and fine lines be clear and visible.

<P>Unfortunately, Topographica so far has only partial support for
black-on-white diagrams suitable for printing; in other cases support
is planned but not yet implemented.  In the worst case, it is possible
to swap the Saturation and Value channels of plots using
<A HREF="http://www.gimp.org">the Gimp</A>, but in others programming
support will be necessary.



<H2>Topographica plots</H2>

<P>These sections describe how to generate publication figures from each
of the various Topographica plotting or display windows.


<H4>Model architecture</H4>

<P>The Model Editor window of Topographica is helpful for generating
architecture diagrams for modeling papers.  Just arrange the Sheets as
clearly as possible, make sure everything is named appropriately, and
then export this diagram to a file for use in your paper by
right-clicking and selecting <code>Export PostScript image</code>.
You will probably want to select <code>Printing</code> mode also, to
plot each sheet in white instead of black.

<P>Of course, it is possible to grab a screenshot of the Model Editor
window as well, but this is not recommended because the result will
have jagged lines, jagged text, and will usually be a much larger file
than necessary.  Once you have an Encapsulated PostScript image, you
can convert it to PDF for use in a document using
<code>epstopdf</code> (free) or Adobe Acrobat Distiller (expensive).


<H4>Projection plots</H4>

<P>There is not currently any support for saving these directly to disk.
Instead, they can be selected by taking a screenshot using your
favorite such utility.  

<P>First, be sure to make the CFs be as small as possible on screen;
there is no need to store many bytes of data for each weight value
(unless you want very thin outlines around the weights).  Also, be
sure that each pixel represents one unit, by turning on <code>Integer
Scaling</code>.  That way each unit will be plotted as either 1x1,
2x2, 3x3, etc., rather than some being 1x2, some 2x3, etc., as needed
to reach a certain fixed overall plot size.  Be sure to hit
<code>Reduce</code> as many times as you can, to get down to 1 pixel
per unit, and turn off Sheet Coordinates.  It does not matter that the
plot will be too small on screen at that point; it will be fine in
the final document if it is scaled appropriately.


<H4>Map plots</H4>

<P>Again, these plots must currently be saved using a screenshot
utility. 

<P>For preference maps (or any plot that includes images from only a
single Sheet), you should turn on <code>Integer Scaling</code> and
turn off <code>Sheet Coordinates</code>.  (Sheet coordinates are not
necessary or useful when all plots are of the same region, because the
relative sizes are then guaranteed to be accurate in all cases.)  If
you are only grabbing the image and not the label, then you should
make the plots as small as possible.  Otherwise, just pick a size that
looks nice with the label.


<H4>Activity and ConnectionField plots</H4>

<P>Again, these plots must currently be saved using a screenshot
utility. 

<P>For <code>Activity</code> plots and any other plot that includes
multiple Sheets, be sure to leave <code>Sheet Coordinates</code> on
and <code>Integer Scaling</code> off.  This way, the relative sizes of
the sheets will be preserved, at the expense of individual units being
slightly different sizes and the overall image size being larger.  The
reader is likely to be confused if the relative sizes are not correct
whenever there are multiple sheets in the same plot.


<H2>Citations</H2>

<P><A NAME="citing">If</A> you use this software in work leading to an
academic publication, please cite the following paper so that readers
will know how to replicate your results and build upon them.  (Plus,
it is only polite to cite work done by others that you rely on!)

<BLOCKQUOTE>
James&nbsp;A. Bednar, Yoonsuck Choe, Judah De Paula, Risto
  Miikkulainen, Jefferson Provost, and Tal Tversky.
<A HREF="http://nn.cs.utexas.edu/keyword?bednar:neurocomputing04-sw">Modeling
  cortical maps with Topographica</A>.
<CITE>Neurocomputing</CITE>, pages 1129-1135, 2004.
</BLOCKQUOTE>

or in BibTeX format:

<pre>
@Article{bednar:neurocomputing04-sw,
  author       = "James A. Bednar and Yoonsuck Choe and Judah {De Paula}
                  and Risto Miikkulainen and Jefferson Provost and Tal
                  Tversky",
  title	       = "Modeling Cortical Maps with {Topographica}",
  journal      = "Neurocomputing",
  year	       = 2004,
  pages        = "1129--1135",
  url	       = "http://nn.cs.utexas.edu/keyword?bednar:neurocomputing04-sw",
}
</pre>
