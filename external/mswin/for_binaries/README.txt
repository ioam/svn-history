Making a Windows installation package
=====================================

(1) First you need to be using a copy that has been setup to
    work under CVS. This means you have run setup.bat in the
    Topographica root directory and can use Topographica.

(2) CEBHACKALERT: run 'make win' on unix to get the release
    version correct.

(3) Run 'prepare_for_binaries.bat'

(4) Delete the doc/ subdirectory and replace it with one where the 
    documentation has been compiled (I copy it over from a linux
    version, but you could complile the php files on Windows, good
    luck with that).

(5) Copy topographica.iss to wherever you want to create the .exe
    file, then delete the external directory (which includes this file
    so remember the next step!).

(6) I use 'Inno Setup 5', an open-source installation package creator.
    (See http://www.jrsoftware.org/isinfo.php)
    The script topographica.iss will create a .exe installation file;
    just choose 'compile' from the menu.
