Making a Windows installation package
=====================================

(1) First you need to be using a copy that has been setup to
    work under CVS. This means you have run setup.bat in the
    setup_cvs_copy/ directory.

(2) Do a 'make new-version' on unix to update the release numbers

(3) Run 'prepare_for_installer.bat'. Be sure you are ok with
    sacrificing your copy of Topographica this way! You probably
    want to copy your topographica directory and perform this 
    procedure on that copy! 
    (Note that the last output of this script will be 'The system
    cannot find the path specified'; this is because the last line 
    deletes the script itself.)

(4) Delete the doc/ subdirectory and replace it with one where the 
    documentation has been compiled (I copy it over from a linux
    version, but you could complile the php files on Windows, good
    luck with that).

(6) I use 'Inno Setup 5', an open-source installation package creator
    (see http://www.jrsoftware.org/isinfo.php).
    Open topographica.iss in the topographica directory, adjust the
    paths marked *** to match those on your system, then just choose
    'compile' from the 'build' menu. You should get a setup.exe file
    in the newly created Output directory.
