<H1>Making Releases</H1>

<!--CEBALERT: seems we've never done a relese from svn...-->

<P>The latest version of Topographica is always available by SVN, but
we also make more stable versions available periodically.  To make
such a release, the steps we generally follow are:

<ol>
<li><P>Ensure that no one besides yourself has any modified files checked
  out in SVN; if they do, make sure all of it gets checked in or
  does not need to be included in the release, and ensure that none
  of it will be checked in until the release is complete.

<li><P>Increment the RELEASE number <!--and the RELEASE_TAG--> in ./Makefile,
  and do "make new-version".
   
<li><P>Update the documentation files, especially README.txt and
  doc/Downloads/index_text.php.  The rest should be read through,
  making sure that the auto-generated pages are working properly,
  and that those written by hand match the current version of the
  code.  In particular, doc/Reference_Manual/index_text.php needs
  to match the current version of the reference manual (don't forget
  to <code>make reference-manual</code>).

<li><P>Update the tutorials to match changes to the GUI, if necessary.
  A simple way to get updated versions of each image is to:

  <ol>
  <li>Change to the doc/Tutorials/images/ directory
  <li>Launch <code>xv</code> on all of the images (<code>xv * &</code>)
  <li>Select the image you want to update, using xv's right-click menu
  <li>Select Grab from xv's right-click menu
  <li>Select Save from xv's right-click menu
  </ol>

  <P>The advantage of this method is that you never need to type in
  filenames, make sure they match the .html or .php file, and so on.

  <P>Be sure to work through the tutorial once it is updated, to make
  sure all of the instructions still make sense for the new release.
  
<li><P>Update Changelog.txt (by making a copy of ChangeLog.txt, doing
  "make Changelog.txt", and pasting the new items at the top of the
  copy (so that any fixes to the old items are preserved).  Also
  summarize major changes in it for the release notes in News/.

<li><P>Update the remaining work lists in
  Future_Work/index_text.php and Future_Work/current_text.php to
  reflect completed tasks and changes in priority.

<li><P>Check any modified files into SVN.
   
<li><P>Save all open files from within any editor, and do a "make dist"
  to create a candidate distribution archive.  (To ensure that
  all files are saved in Emacs, you can do "M-x compile RET make
  dist".) Note that this step is best done on a local disk rather 
  than on a network drive. (Additionally, using a scratch copy of 
  Topographica on which you have run 'make -C external clean' will
  speed things up, but this is not necessary.)
  
<li><P>Unpack the distribution archive and examine it:
    <ol>
    <li><P>Use "ls -lFRA" or "find ." to ensure that no stray files were
      included; if they were, edit "distclean:" in ./Makefile to
      delete them from the generated distribution.
   
    <li><P>Double-check the generated documentation to ensure that it is
      complete and was generated properly.
      
<!--CEBALERT: need to make slow-tests' list of scripts only
include those present in release-->
    <li><P>Compile the source on various platforms, ensuring that there are 
      no errors.  Also perform a self-test on the various platforms
      ("make tests; make slow-tests"). 
    </ol>
    
<li><P>If you find problems, go back to step 6 and start over.

<li><P>When the package is ready for release, copy binaries to
    SourceForge using their admin interface, and add a news release
    and screenshots. As at 3/2009, the upload command would be something like
    <code>rsync -avP -e ssh topographica-0.9.5.tar.gz  ceball@frs.sourceforge.net:uploads/</code>

<!--
how i made the zip file:
zip -r topographica-0.9.6.zip topographica-0.9.6/*
-->

<li><P>Build on Windows and make .exe versions, test them, and upload
    them to SourceForge.

<li><P>Tag the files in SVN as being the latest stable version using
    "make LATEST_STABLE", copy the trunk to svn's releases/ directory
    using "make tag-release", and update the public web site with this version 
    using "make sf-web-site". Note that this last step should be run from
    the copy of Topographica you created for distribution so that no stray
    files from doc/ are uploaded. Also note that these three commands can
    be run together with "make svn-release".

<li><P>Notify the other developers that they may once again commit new
    code to the SVN repository.

<li>Send an announcement to topographica-announce at lists.sf.net.
</ol>

