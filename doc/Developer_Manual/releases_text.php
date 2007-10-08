<H1>Making Releases</H1>

<P>The latest version of Topographica is always available by CVS, but
we also make more stable versions available periodically.  To make
such a release, the steps we generally follow are:

<ol>
<li><P>Ensure that no one besides yourself has any modified files checked
  out in CVS; if they do, make sure all of it gets checked in or
  does not need to be included in the release, and ensure that none
  of it will be checked in until the release is complete.
  
<li><P>Increment the RELEASE number and the RELEASE_TAG in ./Makefile,
  and do "make new-version".
   
<li><P>Update the documentation files, especially README.txt and
  doc/Downloads/index_text.php.  The rest should be read through,
  making sure that the auto-generated pages are working properly,
  and that those written by hand match the current version of the
  code.  In particular, doc/Reference_Manual/index_text.php needs
  to match the current version of the reference manual.

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
  
<li><P>Update Changelog.txt (using "make Changelog.txt",
  removing any overlap on the starting date, filling the new items in
  Emacs, and checking in the result), and summarize major changes in it
  for the release notes.

<li><P>Update the remaining work lists in
  Future_Work/index_text.php and Future_Work/current_text.php to
  reflect completed tasks and changes in priority.

<li><P>Check in any modified files into CVS.
   
<li><P>Save all open files from within any editor, and do a "make dist"
  to create a candidate distribution archive.  (To ensure that
  all files are saved in Emacs, you can do "M-x compile RET make
  dist".)
  
<li><P>Unpack the distribution archive and examine it:
    <ol>
    <li><P>Use "ls -lFRA" or "find ." to ensure that no stray files were
      included; if they were, edit "distclean:" in ./Makefile to
      delete them from the generated distribution.
   
    <li><P>Double-check the generated documentation to ensure that it is
      complete and was generated properly.
      
    <li><P>Compile the source on various platforms, ensure that there are 
      no errors.  Also perform a self-test on the various platforms
      ("make tests").
    </ol>
    
<li><P>If you find problems, go back to step 6 and start over.

<li><P>When the package is ready for release, copy binaries to
    SourceForge using their admin interface, and add a news release
    and screenshot.

<li><P>Build on Windows and make .exe versions, test them, and upload
    them to SourceForge.

<li><P>Tag the files in cvs as being the latest stable version using
    "make LATEST_STABLE", and update the public web site with this version 
    using "make sf-web-site".

<li><P>Notify the other developers that they may once again commit new
    code to the CVS repository.

<li>Send an announcement to topographica-announce at lists.sf.net.
</ol>

